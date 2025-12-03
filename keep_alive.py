# keep_alive.py - Fake HTTP server for Render.com
from flask import Flask
from threading import Thread
import logging

# Disable Flask logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask('')

@app.route('/')
def home():
    return """
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

@app.route('/health')
def health():
    return "OK", 200

def run():
    """Start HTTP server on port 8080"""
    app.run(host='0.0.0.0', port=8080, debug=False)

def keep_alive():
    """Start keep-alive server in background thread"""
    t = Thread(target=run, daemon=True)
    t.start()
    print("🌐 Fake HTTP server started on port 8080")