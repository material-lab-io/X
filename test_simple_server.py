#!/usr/bin/env python3
"""
Simple test server to verify basic connectivity
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <html>
    <head><title>Test Server Working!</title></head>
    <body>
        <h1>✅ Server is running successfully!</h1>
        <p>If you can see this, port forwarding is working correctly.</p>
        <p>The Twitter/X Content Generator is ready to be started.</p>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("Starting test server on http://localhost:5000")
    print("Press Ctrl+C to stop")
    app.run(host='0.0.0.0', port=5000, debug=False)