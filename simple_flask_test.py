#!/usr/bin/env python3
import sys
print("Python path:", sys.executable)
print("Python version:", sys.version)

try:
    from flask import Flask
    print("✓ Flask imported successfully")
except ImportError as e:
    print("✗ Flask import failed:", e)
    sys.exit(1)

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <html>
    <head><title>Flask Test</title></head>
    <body>
        <h1>Flask is working!</h1>
        <p>Python: ''' + sys.version + '''</p>
        <p><a href="/test">Test endpoint</a></p>
    </body>
    </html>
    '''

@app.route('/test')
def test():
    return {'status': 'ok', 'message': 'Flask server is running'}

if __name__ == '__main__':
    print("\nStarting Flask test server...")
    print("If successful, access at: http://localhost:8888/")
    print("Press Ctrl+C to stop\n")
    
    try:
        app.run(host='127.0.0.1', port=8888, debug=False)
    except Exception as e:
        print(f"ERROR: Failed to start server: {e}")
        import traceback
        traceback.print_exc()