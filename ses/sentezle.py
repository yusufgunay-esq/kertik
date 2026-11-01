import os
import math
import struct
import wave
import random

SAMPLE_RATE = 48000

def write_wav(filename, samples):
    max_val = max(abs(s) for s in samples) if samples else 1.0
    norm_factor = 0.92 / max_val if max_val > 0.92 else 1.0
    
    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(SAMPLE_RATE)
        
        frames = bytearray()
        for s in samples:
            val = max(-1.0, min(1.0, s * norm_factor))
            int_val = int(val * 32767.0)
            frames.extend(struct.pack('<h', int_val))
        f.writeframes(frames)
    print(f"Olusturuldu: {filename} ({len(samples)/SAMPLE_RATE:.3f} saniye)")

def apply_lowpass(samples, cutoff_freq=220.0, q=0.707):
    omega = 2.0 * math.pi * cutoff_freq / SAMPLE_RATE
    sn = math.sin(omega)
    cs = math.cos(omega)
    alpha = sn / (2.0 * q)
    
    b0 = (1.0 - cs) / 2.0
    b1 = 1.0 - cs
    b2 = (1.0 - cs) / 2.0
    a0 = 1.0 + alpha
    a1 = -2.0 * cs
    a2 = 1.0 - alpha
    
    b0_n = b0 / a0
    b1_n = b1 / a0
    b2_n = b2 / a0
    a1_n = a1 / a0
    a2_n = a2 / a0
    
    out = [0.0] * len(samples)
    x1 = x2 = y1 = y2 = 0.0
    for i in range(len(samples)):
        x0 = samples[i]
        y0 = b0_n * x0 + b1_n * x1 + b2_n * x2 - a1_n * y1 - a2_n * y2
        x2 = x1; x1 = x0
        y2 = y1; y1 = y0
        out[i] = y0
    return out

def apply_steep_lowpass(samples, cutoff=220.0):
    return apply_lowpass(apply_lowpass(samples, cutoff, 0.707), cutoff, 0.707)

def apply_bandpass(samples, center_freq=380.0, q=2.0):
    omega = 2.0 * math.pi * center_freq / SAMPLE_RATE
    sn = math.sin(omega)
    cs = math.cos(omega)
    alpha = sn / (2.0 * q)
    
    b0 = sn / 2.0
    b1 = 0.0
    b2 = -sn / 2.0
    a0 = 1.0 + alpha
    a1 = -2.0 * cs
    a2 = 1.0 - alpha
    
    b0_n = b0 / a0; b1_n = b1 / a0; b2_n = b2 / a0
    a1_n = a1 / a0; a2_n = a2 / a0
    
    out = [0.0] * len(samples)
    x1 = x2 = y1 = y2 = 0.0
    for i in range(len(samples)):
        x0 = samples[i]
        y0 = b0_n * x0 + b1_n * x1 + b2_n * x2 - a1_n * y1 - a2_n * y2
        x2 = x1; x1 = x0; y2 = y1; y1 = y0
        out[i] = y0
    return out

# 1. SEANS BAŞLATMA - ADAY A (ÖNERİLEN): KURU CEVİZ AĞACINA İLK KERTİK
# (Transient Lif Çatlaması 0-8ms + Tok Gövde 118 Hz + Ahşap Rezonansı 186 Hz - 90ms)
def generate_baslat_ceviz_kertik():
    dur = 0.095
    num_samples = int(SAMPLE_RATE * dur)
    raw = [0.0] * num_samples
    
    # Lif çatlama tohumu
    b_noise = 0.0
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        
        # 1. Mikro Lif Transient (0-10ms)
        w = random.uniform(-1.0, 1.0)
        b_noise = 0.75 * b_noise + 0.25 * w
        grain_trans = b_noise * math.exp(-t * 450.0) * 0.45
        
        # 2. Gövde Modal Rezonansları (Ahşap Kütük)
        # Mode 1 (Temel tok frekans: 118 Hz)
        attack1 = 1.0 - math.exp(-t * 600.0)
        mode1 = math.sin(2.0 * math.pi * 118.0 * t) * math.exp(-t / 0.028) * attack1 * 1.25
        
        # Mode 2 (Ahşap lif gerilimi: 186 Hz)
        attack2 = 1.0 - math.exp(-t * 500.0)
        mode2 = math.sin(2.0 * math.pi * 186.0 * t) * math.exp(-t / 0.019) * attack2 * 0.35
        
        # Mode 3 (Hafif ahşap tınısı: 265 Hz)
        mode3 = math.sin(2.0 * math.pi * 265.0 * t) * math.exp(-t / 0.012) * attack1 * 0.15
        
        raw[i] = grain_trans + mode1 + mode2 + mode3
        
    filtered = apply_steep_lowpass(raw, cutoff=320.0)
    for i in range(num_samples):
        filtered[i] = math.tanh(filtered[i] * 1.55)
    return filtered

# 1. SEANS BAŞLATMA - ADAY B: NEHİR TAŞININ AHŞAP KAİDEYE OTURMASI
# (Derin Mineral Kütle 78 Hz + Tok Taban - 110ms)
def generate_baslat_tas_kaide():
    dur = 0.110
    num_samples = int(SAMPLE_RATE * dur)
    raw = [0.0] * num_samples
    
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        attack = 1.0 - math.exp(-t * 400.0)
        # 78 Hz derin taban
        f_drop = 78.0 + 35.0 * math.exp(-t * 45.0)
        sub_body = math.sin(2.0 * math.pi * f_drop * t) * math.exp(-t / 0.045) * attack * 1.35
        wood_base = math.sin(2.0 * math.pi * 135.0 * t) * math.exp(-t / 0.025) * attack * 0.30
        raw[i] = sub_body + wood_base
        
    filtered = apply_steep_lowpass(raw, cutoff=240.0)
    for i in range(num_samples):
        filtered[i] = math.tanh(filtered[i] * 1.45)
    return filtered

# 1. SEANS BAŞLATMA - ADAY C: MEKANİK ZEN TETİKLEYİCİSİ (LEICA DEKLANŞÖR/MANDAL)
# (Çift Mikro Temas: 145 Hz ön temas + 18ms sonra 102 Hz ana kilit - 90ms)
def generate_baslat_zen_mandal():
    dur = 0.095
    num_samples = int(SAMPLE_RATE * dur)
    raw = [0.0] * num_samples
    
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        # Ön temas (t=0)
        a1 = 1.0 - math.exp(-t * 500.0)
        s1 = math.sin(2.0 * math.pi * 145.0 * t) * math.exp(-t / 0.016) * a1 * 0.65
        
        # Ana kilit mandalı (t=18ms)
        s2 = 0.0
        if t >= 0.018:
            t2 = t - 0.018
            a2 = 1.0 - math.exp(-t2 * 450.0)
            s2 = math.sin(2.0 * math.pi * 102.0 * t2) * math.exp(-t2 / 0.032) * a2 * 1.20
            
        raw[i] = s1 + s2
        
    filtered = apply_steep_lowpass(raw, cutoff=300.0)
    for i in range(num_samples):
        filtered[i] = math.tanh(filtered[i] * 1.50)
    return filtered

# 7. KUM BAHÇESİ RÜZGARI (YouTube 'Whoosh' Efekti Değil; Kuru Kumun Sessiz Nefesi - 350ms)
def generate_maddi_7_ruzgar(guc=1):
    dur = 0.42 if guc > 1 else 0.32
    num_samples = int(SAMPLE_RATE * dur)
    raw = [0.0] * num_samples
    b0 = 0.0
    b1 = 0.0
    
    tepe = dur * 0.38
    for i in range(num_samples):
        t = i / SAMPLE_RATE
        white = random.uniform(-1.0, 1.0)
        
        # Kahverengi / pembe mikro kum liyakatı
        b0 = 0.94 * b0 + 0.06 * white
        b1 = 0.86 * b1 + 0.14 * white
        grain = (b0 * 0.7 + b1 * 0.3)
        
        # Sub-bass hava dalgalanması (40-60 Hz)
        air_wave = math.sin(2 * math.pi * 50.0 * t) * 0.15
        
        # Pürüzsüz yumuşak nefes zarfı (smooth breath envelope)
        if t < tepe:
            env = math.sin((t / tepe) * (math.pi / 2.0))
        else:
            env = math.exp(-(t - tepe) / (dur * 0.28))
            
        raw[i] = (grain + air_wave) * env * (0.55 if guc > 1 else 0.40)
        
    filtered = apply_steep_lowpass(raw, cutoff=180.0 if guc <= 1 else 220.0)
    for i in range(num_samples):
        filtered[i] = math.tanh(filtered[i] * 1.8)
    return filtered

if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Başlatma Sesi Adayları
    write_wav(os.path.join(out_dir, "maddi_1_baslat_ceviz_kertik.wav"), generate_baslat_ceviz_kertik())
    write_wav(os.path.join(out_dir, "maddi_1_baslat_tas_kaide.wav"), generate_baslat_tas_kaide())
    write_wav(os.path.join(out_dir, "maddi_1_baslat_zen_mandal.wav"), generate_baslat_zen_mandal())
    
    # Varsayılan başlat sesi olarak Ceviz Kertik atanıyor
    write_wav(os.path.join(out_dir, "maddi_1_baslat_ahsap_kertik.wav"), generate_baslat_ceviz_kertik())
    
    # 7. Kum Rüzgarı
    write_wav(os.path.join(out_dir, "maddi_7_kum_ruzgari_nefes.wav"), generate_maddi_7_ruzgar(guc=1))
    write_wav(os.path.join(out_dir, "maddi_7_kum_ruzgari_firtina.wav"), generate_maddi_7_ruzgar(guc=2))
    print("Tum seans baslatma akustik adaylari ve ses dosyaları basariyla uretildi!")

