#!/usr/bin/env python3
"""
Kertik APK yeniden derleyici.
Mevcut bir APK şablonunu alır, assets/www/index.html'i değiştirir,
v1 (jarsigner) + v2 (bu dosya) imzalarını atar.

Kullanım:
  python3 apkbuild.py sablon.apk yeni_index.html cikti.apk anahtar.p12 parola
"""
import sys, os, io, struct, zipfile, subprocess, shutil, hashlib

ALIGN = 4
CHUNK = 1 << 20
MAGIC = b"APK Sig Block 42"
V2_ID = 0x7109871a
SIG_ALG = 0x0103                       # RSASSA-PKCS1-v1_5 + SHA2-256


# ---------- 1. içeriği değiştir, META-INF'i at ----------
def rebuild(src, html_path, dst):
    zin = zipfile.ZipFile(src)
    new_html = io.open(html_path, "rb").read()
    with zipfile.ZipFile(dst, "w") as zout:
        for i in zin.infolist():
            if i.filename.startswith("META-INF/"):
                continue
            data = new_html if i.filename == "assets/www/index.html" else zin.read(i.filename)
            zi = zipfile.ZipInfo(i.filename, date_time=i.date_time)
            zi.compress_type = i.compress_type
            zi.external_attr = i.external_attr
            zi.create_system = i.create_system
            zout.writestr(zi, data)
    zin.close()


# ---------- 2. v1 imza ----------
def sign_v1(apk, p12, pw):
    subprocess.run(["jarsigner", "-keystore", p12, "-storetype", "PKCS12",
                    "-storepass", pw, "-keypass", pw,
                    "-sigalg", "SHA256withRSA", "-digestalg", "SHA-256",
                    apk, "kertik"], check=True, capture_output=True)


# ---------- 3. hizalama (STORED girdiler 4 bayta) ----------
def align(src, dst):
    zin = zipfile.ZipFile(src)
    out = io.open(dst, "wb")
    central = []
    for i in zin.infolist():
        raw = zin.read(i.filename)
        name = i.filename.encode()
        if i.compress_type == zipfile.ZIP_DEFLATED:
            import zlib
            co = zlib.compressobj(9, zlib.DEFLATED, -15)
            body = co.compress(raw) + co.flush()
        else:
            body = raw
        crc = zipfile.crc32(raw) & 0xFFFFFFFF
        extra = b""
        if i.compress_type == zipfile.ZIP_STORED:
            head = out.tell() + 30 + len(name)
            pad = (ALIGN - head % ALIGN) % ALIGN
            if pad:
                # 0xd935 = Android hizalama alanı; 4 bayttan kısaysa düz dolgu
                extra = struct.pack("<HH", 0xd935, pad - 4) + b"\0" * (pad - 4) if pad >= 4 else b"\0" * pad
                if pad < 4:
                    pad2 = pad + ALIGN
                    extra = struct.pack("<HH", 0xd935, pad2 - 4) + b"\0" * (pad2 - 4)
        off = out.tell()
        out.write(struct.pack("<IHHHHHIIIHH", 0x04034b50, 20, 0, i.compress_type,
                              0, 0, crc, len(body), len(raw), len(name), len(extra)))
        out.write(name); out.write(extra); out.write(body)
        central.append((i, name, crc, len(body), len(raw), off, extra))
    cd_off = out.tell()
    for (i, name, crc, csize, usize, off, extra) in central:
        out.write(struct.pack("<IHHHHHHIIIHHHHHII", 0x02014b50, 20, 20, 0, i.compress_type,
                              0, 0, crc, csize, usize, len(name), len(extra), 0, 0, 0,
                              i.external_attr, off))
        out.write(name); out.write(extra)
    cd_size = out.tell() - cd_off
    out.write(struct.pack("<IHHHHIIH", 0x06054b50, 0, 0, len(central), len(central),
                          cd_size, cd_off, 0))
    out.close(); zin.close()
    return cd_off, cd_size


# ---------- 4. v2 imza ----------
def chunked_digest(parts):
    chunks = []
    for p in parts:
        for o in range(0, len(p), CHUNK):
            chunks.append(p[o:o + CHUNK])
    top = hashlib.sha256()
    top.update(b"\x5a" + struct.pack("<I", len(chunks)))
    for c in chunks:
        h = hashlib.sha256()
        h.update(b"\xa5" + struct.pack("<I", len(c)) + c)
        top.update(h.digest())
    return top.digest()


def lp(b):                       # uint32 uzunluk önekli
    return struct.pack("<I", len(b)) + b


def sign_v2(path, p12, pw):
    from cryptography.hazmat.primitives.serialization import pkcs12, Encoding
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import hashes, serialization

    key, cert, _ = pkcs12.load_key_and_certificates(io.open(p12, "rb").read(), pw.encode())
    cert_der = cert.public_bytes(Encoding.DER)
    pub_der = key.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)

    data = bytearray(io.open(path, "rb").read())
    eocd_off = data.rfind(b"PK\x05\x06")
    cd_off = struct.unpack("<I", data[eocd_off + 16:eocd_off + 20])[0]
    cd_size = struct.unpack("<I", data[eocd_off + 12:eocd_off + 16])[0]

    contents = bytes(data[:cd_off])
    cd = bytes(data[cd_off:cd_off + cd_size])
    eocd = bytearray(data[eocd_off:])

    # Spec: EOCD digest'i, "merkezi dizin offseti" alanı İMZA BLOĞUNUN offseti
    # olarak alınmış hâliyle hesaplanır — bu da bloktan önceki cd_off'un aynısı.
    # Dosyaya yazılan EOCD ise blok kadar kaymış offseti taşır.
    digest = chunked_digest([contents, cd, bytes(eocd)])
    digests = lp(lp(struct.pack("<I", SIG_ALG) + lp(digest)))
    certs = lp(lp(cert_der))
    attrs = lp(b"")
    signed_data = digests + certs + attrs
    sig = key.sign(signed_data, padding.PKCS1v15(), hashes.SHA256())
    signatures = lp(lp(struct.pack("<I", SIG_ALG) + lp(sig)))
    signer = lp(signed_data) + signatures + lp(pub_der)
    signers = lp(lp(signer))
    pair = struct.pack("<Q", 4 + len(signers)) + struct.pack("<I", V2_ID) + signers
    block_len = len(pair) + 8 + 16
    block = struct.pack("<Q", block_len) + pair + struct.pack("<Q", block_len) + MAGIC

    e = bytearray(eocd)
    struct.pack_into("<I", e, 16, cd_off + len(block))

    out = contents + block + cd + bytes(e)
    io.open(path, "wb").write(out)


if __name__ == "__main__":
    src, html, dst, p12, pw = sys.argv[1:6]
    tmp = dst + ".tmp"
    rebuild(src, html, tmp)
    sign_v1(tmp, p12, pw)
    align(tmp, dst)
    os.remove(tmp)
    sign_v2(dst, p12, pw)
    print("yazıldı:", dst, os.path.getsize(dst), "bayt")
