#!/usr/bin/env python3
"""Simple preview server without complex dependencies"""

from flask import Flask, jsonify
import json
from pathlib import Path

app = Flask(__name__)

PREVIEW_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Tweet Preview</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        h1 { color: #1da1f2; }
        .tweet {
            padding: 15px;
            margin: 10px 0;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 3px solid #1da1f2;
        }
        .tweet-num {
            font-weight: bold;
            color: #1da1f2;
        }
        button {
            background: #1da1f2;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 20px;
            cursor: pointer;
            margin: 5px;
        }
        .status { 
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐦 Tweet Thread Preview</h1>
        <p>Simple preview without dependencies</p>
        
        <div>
            <button onclick="loadThreads()">Load Threads</button>
            <button onclick="loadSample()">Load Sample</button>
        </div>
        
        <div id="status"></div>
        <div id="content"></div>
    </div>
    
    <script>
        function loadThreads() {
            setStatus('Loading threads...', '');
            fetch('/api/threads')
                .then(r => r.json())
                .then(data => {
                    if (data.error) {
                        setStatus(data.error, 'error');
                    } else {
                        displayThreads(data.threads);
                        setStatus('Loaded ' + data.count + ' thread(s)', 'success');
                    }
                })
                .catch(err => setStatus('Error: ' + err, 'error'));
        }
        
        function loadSample() {
            const sample = {
                topic: "Sample Docker Thread",
                tweets: [
                    "🐳 Let's explore Docker best practices!",
                    "Always use specific tags, not 'latest'",
                    "Multi-stage builds keep images small",
                    "One process per container is the way"
                ]
            };
            displayThreads([sample]);
            setStatus('Loaded sample thread', 'success');
        }
        
        function displayThreads(threads) {
            const content = document.getElementById('content');
            content.innerHTML = '';
            
            threads.forEach(thread => {
                const div = document.createElement('div');
                div.innerHTML = '<h3>' + thread.topic + '</h3>';
                
                const tweets = thread.tweets || thread.generatedTweets || [];
                tweets.forEach((tweet, i) => {
                    const tweetText = typeof tweet === 'string' ? tweet : tweet.text;
                    div.innerHTML += '<div class="tweet"><span class="tweet-num">' + 
                        (i+1) + '.</span> ' + escapeHtml(tweetText) + '</div>';
                });
                
                content.appendChild(div);
            });
        }
        
        function setStatus(msg, type) {
            const status = document.getElementById('status');
            status.textContent = msg;
            status.className = 'status ' + type;
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
@app.route('/preview')
def preview():
    return PREVIEW_HTML

@app.route('/api/threads')
def get_threads():
    try:
        # Try to load generated_threads_final.json
        thread_file = Path("generated_threads_final.json")
        if thread_file.exists():
            with open(thread_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return jsonify({"threads": data, "count": len(data)})
                else:
                    return jsonify({"threads": [data], "count": 1})
        else:
            return jsonify({"error": "No generated_threads_final.json found"})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    port = 8080
    print(f"\n🚀 Simple Preview Server")
    print(f"📍 URL: http://localhost:{port}/preview")
    print(f"✨ No complex dependencies\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)