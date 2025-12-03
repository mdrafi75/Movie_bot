# keep_alive.py - Simple HTTP server without Flask
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
import time

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'OK')
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = """
            <html>
                <body style="background: #0f0f23; color: #00ff00; font-family: monospace; padding: 20px;">
                    <h1>🎬 Movie Bot is Running!</h1>
                    <p>✅ Telegram Bot: Active</p>
                    <p>🤖 Status: Online</p>
                    <p>📡 Service: Render.com Web Service</p>
                    <p>🔧 Health: <a href="/health" style="color: #00ff00;">/health</a></p>
                </body>
            </html>
            """
            self.wfile.write(html.encode())

    def log_message(self, format, *args):
        # Disable access logs
        pass

def run_server():
    """Start HTTP server on port 8080"""
    server = HTTPServer(('0.0.0.0', 8080), SimpleHandler)
    print("🌐 HTTP server started on port 8080")
    server.serve_forever()

def keep_alive():
    """Start HTTP server in background thread"""
    t = Thread(target=run_server, daemon=True)
    t.start()
    print("✅ Keep-alive server started")