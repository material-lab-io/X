#!/usr/bin/env python3
"""Minimal preview server to test Flask functionality"""

from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Preview Server is Running!</h1><p>Go to <a href="/preview">/preview</a></p>'

@app.route('/preview')
def preview():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Tweet Preview - Test</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, sans-serif;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                text-align: center;
            }
            h1 { color: #1da1f2; }
            .status { 
                display: inline-block;
                padding: 10px 20px;
                background: #e8f5fd;
                color: #1da1f2;
                border-radius: 20px;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🐦 Tweet Preview Server</h1>
            <p>The preview server is working!</p>
            <div class="status">✅ Server Running on Port ''' + str(port) + '''</div>
            <p style="margin-top: 30px;">
                <a href="/api/test">Test API Endpoint</a>
            </p>
        </div>
    </body>
    </html>
    '''

@app.route('/api/test')
def api_test():
    return jsonify({
        'status': 'ok',
        'message': 'Preview server API is working',
        'port': port
    })

if __name__ == '__main__':
    # Find available port
    import socket
    for port in [5002, 5003, 5004, 5005, 8080, 8081]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            if result != 0:  # Port is free
                break
        except:
            pass
    
    print(f"\n🚀 Starting Minimal Preview Server")
    print(f"📍 URL: http://localhost:{port}/preview")
    print(f"🔍 Test: http://localhost:{port}/api/test\n")
    
    app.run(host='127.0.0.1', port=port, debug=False)