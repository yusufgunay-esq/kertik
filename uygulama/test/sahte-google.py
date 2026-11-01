import http.server, socketserver, json, urllib.parse, io, re, threading, sys, os

STORE = {"files": {}, "next": 1, "polls": 0, "log": []}
HTML = io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "www", "index.html"), encoding="utf-8").read()

class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def send(self, code, body, ctype="application/json"):
        b = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers(); self.wfile.write(b)
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.end_headers()
    def body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(n).decode("utf-8", "replace")

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        if u.path in ("/", "/index.html"):
            return self.send(200, HTML, "text/html; charset=utf-8")
        if u.path == "/drive/v3/files":
            STORE["log"].append("list")
            fs = [{"id": k} for k in STORE["files"]]
            return self.send(200, json.dumps({"files": fs}))
        m = re.match(r"^/drive/v3/files/([^/]+)$", u.path)
        if m:
            fid = m.group(1)
            if fid not in STORE["files"]: return self.send(404, "{}")
            STORE["log"].append("read")
            return self.send(200, STORE["files"][fid])
        return self.send(404, "{}")

    def do_POST(self):
        u = urllib.parse.urlparse(self.path)
        b = self.body()
        if u.path == "/device/code":
            STORE["polls"] = 0
            return self.send(200, json.dumps({
                "device_code": "DC-1", "user_code": "WXYZ-1234",
                "verification_url": "https://www.google.com/device",
                "expires_in": 1800, "interval": 1}))
        if u.path == "/token":
            p = dict(urllib.parse.parse_qsl(b))
            if p.get("grant_type") == "refresh_token":
                if p.get("refresh_token") != "RT-1": return self.send(400, json.dumps({"error": "invalid_grant"}))
                return self.send(200, json.dumps({"access_token": "AT-1", "expires_in": 3600}))
            STORE["polls"] += 1
            if STORE["polls"] < 2:
                return self.send(428, json.dumps({"error": "authorization_pending"}))
            return self.send(200, json.dumps({"access_token": "AT-1", "refresh_token": "RT-1", "expires_in": 3600}))
        if u.path == "/upload/drive/v3/files":
            fid = "f%d" % STORE["next"]; STORE["next"] += 1
            parts = b.split("\r\n\r\n")
            STORE["files"][fid] = parts[-1].rsplit("\r\n--", 1)[0]
            STORE["log"].append("create")
            return self.send(200, json.dumps({"id": fid}))
        return self.send(404, "{}")

    def do_PATCH(self):
        u = urllib.parse.urlparse(self.path)
        b = self.body()
        m = re.match(r"^/upload/drive/v3/files/([^/]+)$", u.path)
        if m:
            fid = m.group(1)
            if fid not in STORE["files"]: return self.send(404, "{}")
            STORE["files"][fid] = b; STORE["log"].append("update")
            return self.send(200, json.dumps({"id": fid}))
        return self.send(404, "{}")

class S(socketserver.ThreadingTCPServer): allow_reuse_address = True
with S(("127.0.0.1", 8899), H) as srv:
    srv.serve_forever()
