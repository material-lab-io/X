#!/usr/bin/env python3
import sys
print(f"Python version: {sys.version}")

try:
    from flask import Flask
    print("Flask imported successfully")
    
    app = Flask(__name__)
    print("Flask app created")
    
    @app.route('/')
    def home():
        return 'Hello World'
    
    print("Route defined")
    
    # Try to start server
    print("Starting server on port 5000...")
    app.run(host='127.0.0.1', port=5000, debug=False)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()