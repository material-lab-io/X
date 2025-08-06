#!/usr/bin/env python3
"""
Fixed Flask Preview Server for Twitter/X Content Generator
"""

from flask import Flask, render_template_string, jsonify, request
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import logging
import base64
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Simplified HTML template
SIMPLE_PREVIEW_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tweet Thread Preview</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            background-color: #f7f9fa;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 20px;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        h1 {
            color: #1da1f2;
            margin: 0;
            font-size: 24px;
        }
        .status {
            margin-top: 10px;
            color: #657786;
        }
        .controls {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin: 20px 0;
        }
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 20px;
            font-size: 14px;
            cursor: pointer;
            background: #1da1f2;
            color: white;
        }
        button:hover {
            background: #1a91da;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .thread {
            background: white;
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .tweet {
            padding: 15px;
            border-bottom: 1px solid #e1e8ed;
            position: relative;
        }
        .tweet:last-child {
            border-bottom: none;
        }
        .tweet-number {
            position: absolute;
            left: -10px;
            top: 15px;
            background: #1da1f2;
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
        }
        .tweet-content {
            margin-left: 20px;
            white-space: pre-wrap;
        }
        .diagram-placeholder {
            background: #f0f0f0;
            padding: 20px;
            margin: 10px 0;
            border-radius: 8px;
            text-align: center;
            color: #666;
        }
        .error {
            background: #fee;
            color: #c00;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
        }
        .loading {
            text-align: center;
            padding: 40px;
            color: #657786;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐦 Tweet Thread Preview</h1>
            <div class="status">Phase 1-4 Pipeline Integration</div>
        </div>
        
        <div class="controls">
            <button onclick="loadSampleThread()">📄 Load Sample</button>
            <button onclick="runPipeline()">🔄 Run Pipeline</button>
            <button disabled>🚀 Post to Twitter</button>
        </div>
        
        <div id="content">
            <div class="loading">Click "Load Sample" to see a preview</div>
        </div>
    </div>
    
    <script>
        function loadSampleThread() {
            const content = document.getElementById('content');
            content.innerHTML = '<div class="loading">Loading sample thread...</div>';
            
            fetch('/api/sample')
                .then(response => response.json())
                .then(data => {
                    displayThread(data);
                })
                .catch(error => {
                    content.innerHTML = '<div class="error">Error loading sample: ' + error + '</div>';
                });
        }
        
        function runPipeline() {
            const content = document.getElementById('content');
            content.innerHTML = '<div class="loading">Running pipeline...</div>';
            
            fetch('/api/run', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        content.innerHTML = '<div class="error">Error: ' + data.error + '</div>';
                    } else {
                        displayThread(data);
                    }
                })
                .catch(error => {
                    content.innerHTML = '<div class="error">Error running pipeline: ' + error + '</div>';
                });
        }
        
        function displayThread(data) {
            const content = document.getElementById('content');
            let html = '<div class="thread">';
            html += '<h3>' + (data.topic || 'Thread') + '</h3>';
            
            const tweets = data.tweets || data.generatedTweets || [];
            tweets.forEach((tweet, index) => {
                const tweetText = typeof tweet === 'string' ? tweet : tweet.text;
                html += '<div class="tweet">';
                html += '<div class="tweet-number">' + (index + 1) + '</div>';
                html += '<div class="tweet-content">' + escapeHtml(tweetText) + '</div>';
                
                // Check for diagram placeholder
                if (tweetText.includes('[') && tweetText.includes('Diagram')) {
                    html += '<div class="diagram-placeholder">📊 Diagram would appear here</div>';
                }
                
                html += '</div>';
            });
            
            html += '</div>';
            content.innerHTML = html;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    """Redirect to preview"""
    return '<script>window.location.href = "/preview";</script>'

@app.route('/preview')
def preview():
    """Main preview page"""
    try:
        return render_template_string(SIMPLE_PREVIEW_TEMPLATE)
    except Exception as e:
        logger.error(f"Error rendering preview: {str(e)}")
        return f"<h1>Error</h1><p>{str(e)}</p>", 500

@app.route('/api/sample')
def api_sample():
    """Return sample thread data"""
    try:
        sample_data = {
            "topic": "Docker Best Practices",
            "generatedTweets": [
                "🐳 Let's talk about Docker best practices that will save you hours of debugging!",
                "1️⃣ Always use specific image tags, never 'latest'. Your future self will thank you when builds are reproducible.",
                "2️⃣ Multi-stage builds are your friend. Keep your images small and secure:\n\n📊 [Build Process Diagram]",
                "3️⃣ Use .dockerignore! It's like .gitignore but for Docker. Exclude node_modules, .git, and other unnecessary files.",
                "4️⃣ One process per container. This makes scaling, debugging, and monitoring much easier.",
                "What's your favorite Docker optimization tip? Share below! 👇"
            ]
        }
        return jsonify(sample_data)
    except Exception as e:
        logger.error(f"Error in api_sample: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/run', methods=['POST'])
def api_run():
    """Run the pipeline (simplified version)"""
    try:
        # Try to load generated_threads_final.json
        thread_file = Path("generated_threads_final.json")
        if thread_file.exists():
            with open(thread_file, 'r') as f:
                threads = json.load(f)
                # Return first thread
                if isinstance(threads, list) and len(threads) > 0:
                    return jsonify(threads[0])
                elif isinstance(threads, dict):
                    return jsonify(threads)
        
        # Fallback to sample
        return api_sample()
        
    except Exception as e:
        logger.error(f"Error in api_run: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    # Kill any existing processes on our ports
    import subprocess
    for port in [5002, 5003, 5004]:
        try:
            subprocess.run(f"lsof -ti:{port} | xargs kill -9", shell=True, capture_output=True)
        except:
            pass
    
    # Find available port
    import socket
    port = 5002
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    
    if result == 0:  # Port is in use
        for p in [5003, 5004, 5005, 8080]:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', p))
            sock.close()
            if result != 0:
                port = p
                break
    
    print(f"\n🚀 Starting Fixed Preview Server")
    print(f"📍 URL: http://localhost:{port}/preview")
    print(f"✅ Health check: http://localhost:{port}/health")
    print(f"\nPress Ctrl+C to stop\n")
    
    # Run with minimal debug output
    app.run(host='0.0.0.0', port=port, debug=False)