#!/usr/bin/env python3
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Server is working!'

if __name__ == '__main__':
    print("Starting test server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=False)