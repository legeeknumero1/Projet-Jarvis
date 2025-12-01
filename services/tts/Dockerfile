FROM python:3.11-slim

WORKDIR /app

# Install basic dependencies
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Create a dummy server script
RUN echo 'from http.server import HTTPServer, BaseHTTPRequestHandler\n\
    class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):\n\
    def do_GET(self):\n\
    self.send_response(200)\n\
    self.end_headers()\n\
    self.wfile.write(b"TTS Service Ready")\n\
    httpd = HTTPServer(("0.0.0.0", 8002), SimpleHTTPRequestHandler)\n\
    print("Starting TTS dummy server on 8002...")\n\
    httpd.serve_forever()' > server.py

CMD ["python3", "-u", "server.py"]
