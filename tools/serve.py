import http.server, os, sys
ROOT="/home/claude/xmas-mystery.github.io"
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(s,*a,**k): super().__init__(*a,directory=ROOT,**k)
    def send_error(s,code,msg=None,explain=None):
        if code==404:
            b=open(ROOT+"/404.html","rb").read(); s.send_response(404)
            s.send_header("Content-Type","text/html; charset=utf-8"); s.end_headers(); s.wfile.write(b)
        else: super().send_error(code,msg,explain)
    def log_message(s,*a): pass
http.server.ThreadingHTTPServer(("127.0.0.1",8765),H).serve_forever()
