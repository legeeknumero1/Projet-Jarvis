from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"TTS Service Ready")

if __name__ == "__main__":
    print("Starting TTS dummy server on 8002...")
    httpd = HTTPServer(("0.0.0.0", 8002), SimpleHTTPRequestHandler)
    httpd.serve_forever()
