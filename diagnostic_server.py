#!/usr/bin/env python3
"""
Diagnostic Server - Helps debug connection issues
"""

from flask import Flask, Response, request
import json
from pathlib import Path
import socket
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Log every request
@app.before_request
def log_request():
    logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")

def fix_unicode(text):
    """Fix double-escaped Unicode"""
    text = text.replace('\\\\u', '\\u')
    try:
        # Try to decode Unicode escapes
        import codecs
        return codecs.decode(text, 'unicode-escape')
    except:
        return text

@app.route('/')
def home():
    logger.info("Home route accessed")
    return Response("""
    <html>
    <head><title>Server Working</title></head>
    <body>
        <h1>✅ Server is Working!</h1>
        <p>Flask server is running properly.</p>
        <p><a href="/preview">View Tweet Preview</a></p>
        <hr>
        <p>Server Info:</p>
        <ul>
            <li>Host: 0.0.0.0</li>
            <li>Port: 5000</li>
        </ul>
    </body>
    </html>
    """, mimetype='text/html')

@app.route('/preview')
def preview():
    logger.info("Preview route accessed")
    
    try:
        # Simple inline response
        json_path = Path('generated_threads_final.json')
        
        if not json_path.exists():
            return Response("<h1>No data file found</h1>", mimetype='text/html')
        
        # Read file
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Build simple HTML
        html = '<html><head><title>Preview</title><meta charset="UTF-8"></head><body style="font-family: Arial; max-width: 800px; margin: 0 auto; padding: 20px;">'
        html += '<h1 style="color: #1da1f2;">Tweet Preview</h1>'
        
        if data and len(data) > 0:
            tweets = data[0].get('generatedTweets', [])
            for i, tweet in enumerate(tweets, 1):
                fixed_tweet = fix_unicode(tweet)
                html += f'<div style="background: #f0f0f0; padding: 15px; margin: 10px 0; border-radius: 10px;">'
                html += f'<strong>Tweet {i}:</strong><br>'
                html += f'<pre style="white-space: pre-wrap;">{fixed_tweet}</pre>'
                html += f'<small>{len(fixed_tweet)} chars</small>'
                html += '</div>'
        
        html += '</body></html>'
        
        return Response(html, mimetype='text/html')
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return Response(f"<h1>Error</h1><pre>{str(e)}</pre>", mimetype='text/html')

@app.route('/test')
def test():
    return Response("OK", mimetype='text/plain')

if __name__ == '__main__':
    # Get actual IP address
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    print("\n" + "="*60)
    print("🔍 DIAGNOSTIC SERVER")
    print("="*60)
    print(f"\nAccess URLs:")
    print(f"  Local:    http://127.0.0.1:5000/")
    print(f"  Network:  http://{local_ip}:5000/")
    print(f"  All IPs:  http://0.0.0.0:5000/")
    print(f"\nTest endpoints:")
    print(f"  /        - Home page")
    print(f"  /test    - Simple test")
    print(f"  /preview - Tweet preview")
    print("\n" + "="*60 + "\n")
    
    # Run on all interfaces
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)