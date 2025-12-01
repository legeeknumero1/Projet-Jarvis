from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"STT Service Ready")

if __name__ == "__main__":
    print("Starting STT dummy server on 8003...")
    httpd = HTTPServer(("0.0.0.0", 8003), SimpleHTTPRequestHandler)
    httpd.serve_forever()
