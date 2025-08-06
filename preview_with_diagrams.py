#!/usr/bin/env python3
"""Preview server with diagram integration"""

from flask import Flask, jsonify, send_file
import json
from pathlib import Path
import base64
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PREVIEW_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Tweet Preview with Diagrams</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
            line-height: 1.5;
        }
        .container {
            background: white;
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        h1 { 
            color: #1da1f2; 
            font-size: 24px;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #657786;
            margin-bottom: 20px;
        }
        .controls {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            margin-bottom: 20px;
        }
        button {
            background: #1da1f2;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
        }
        button:hover {
            background: #1a91da;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .thread {
            margin-top: 20px;
            border-top: 1px solid #e1e8ed;
            padding-top: 20px;
        }
        .thread-header {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 15px;
            color: #14171a;
        }
        .tweet {
            position: relative;
            padding: 15px 15px 15px 45px;
            margin: 10px 0;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 3px solid #1da1f2;
            min-height: 60px;
        }
        .tweet-num {
            position: absolute;
            left: 10px;
            top: 15px;
            width: 25px;
            height: 25px;
            background: #1da1f2;
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 12px;
            font-weight: bold;
        }
        .tweet-content {
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .tweet-meta {
            font-size: 13px;
            color: #657786;
            margin-top: 8px;
        }
        .diagram {
            margin: 15px 0;
            border-radius: 8px;
            overflow: hidden;
            border: 1px solid #e1e8ed;
            background: #f7f9fa;
        }
        .diagram img {
            width: 100%;
            height: auto;
            display: block;
        }
        .diagram-label {
            padding: 8px 12px;
            background: #e8f5fd;
            color: #1da1f2;
            font-size: 12px;
            font-weight: 500;
        }
        .status { 
            padding: 10px 15px;
            margin: 10px 0;
            border-radius: 8px;
            font-size: 14px;
        }
        .success { 
            background: #d1ecf1; 
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        .error { 
            background: #f8d7da; 
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .info {
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }
        .logs {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            font-family: monospace;
            font-size: 12px;
            max-height: 200px;
            overflow-y: auto;
        }
        .log-entry {
            margin: 2px 0;
        }
        .log-info { color: #0066cc; }
        .log-success { color: #008800; }
        .log-error { color: #cc0000; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐦 Tweet Thread Preview</h1>
        <p class="subtitle">Phase 1-4 Pipeline with Diagram Integration</p>
        
        <div class="controls">
            <button onclick="loadThreads()">📄 Load Threads</button>
            <button onclick="runPipeline()">🔄 Run Pipeline</button>
            <button onclick="showDiagrams()">🖼️ Show Diagrams</button>
            <button disabled>🚀 Post to Twitter</button>
        </div>
        
        <div id="status"></div>
        <div id="content"></div>
        <div id="logs" class="logs" style="display:none"></div>
    </div>
    
    <script>
        let currentThreads = [];
        let logs = [];
        
        function addLog(message, type = 'info') {
            const time = new Date().toLocaleTimeString();
            logs.push({time, message, type});
            updateLogs();
        }
        
        function updateLogs() {
            const logsDiv = document.getElementById('logs');
            if (logs.length > 0) {
                logsDiv.style.display = 'block';
                logsDiv.innerHTML = logs.map(log => 
                    `<div class="log-entry log-${log.type}">[${log.time}] ${log.message}</div>`
                ).join('');
                logsDiv.scrollTop = logsDiv.scrollHeight;
            }
        }
        
        function loadThreads() {
            setStatus('Loading threads...', 'info');
            addLog('Fetching threads from server', 'info');
            
            fetch('/api/threads')
                .then(r => r.json())
                .then(data => {
                    if (data.error) {
                        setStatus(data.error, 'error');
                        addLog('Error: ' + data.error, 'error');
                    } else {
                        currentThreads = data.threads;
                        displayThreads(data.threads);
                        setStatus(`Loaded ${data.count} thread(s)`, 'success');
                        addLog(`Successfully loaded ${data.count} thread(s)`, 'success');
                    }
                })
                .catch(err => {
                    setStatus('Error: ' + err, 'error');
                    addLog('Failed to load threads: ' + err, 'error');
                });
        }
        
        function runPipeline() {
            setStatus('Running pipeline...', 'info');
            logs = [];
            addLog('Starting Phase 1-4 pipeline', 'info');
            
            fetch('/api/pipeline/run', {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    if (data.error) {
                        setStatus('Pipeline error: ' + data.error, 'error');
                        addLog('Pipeline failed: ' + data.error, 'error');
                    } else {
                        currentThreads = data.threads;
                        displayThreads(data.threads);
                        setStatus('Pipeline completed successfully', 'success');
                        addLog('Pipeline completed', 'success');
                        
                        // Add pipeline logs
                        if (data.logs) {
                            data.logs.forEach(log => addLog(log.message, log.level));
                        }
                    }
                })
                .catch(err => {
                    setStatus('Pipeline error: ' + err, 'error');
                    addLog('Pipeline failed: ' + err, 'error');
                });
        }
        
        function showDiagrams() {
            setStatus('Checking available diagrams...', 'info');
            
            fetch('/api/diagrams')
                .then(r => r.json())
                .then(data => {
                    if (data.diagrams && data.diagrams.length > 0) {
                        setStatus(`Found ${data.diagrams.length} diagram(s)`, 'success');
                        displayDiagramList(data.diagrams);
                    } else {
                        setStatus('No diagrams found', 'error');
                    }
                })
                .catch(err => setStatus('Error: ' + err, 'error'));
        }
        
        function displayThreads(threads) {
            const content = document.getElementById('content');
            content.innerHTML = '';
            
            threads.forEach((thread, idx) => {
                const threadDiv = document.createElement('div');
                threadDiv.className = 'thread';
                
                threadDiv.innerHTML = `<div class="thread-header">${thread.topic || 'Thread ' + (idx + 1)}</div>`;
                
                const tweets = thread.tweets || thread.generatedTweets || [];
                tweets.forEach((tweet, i) => {
                    const tweetData = typeof tweet === 'string' ? {text: tweet} : tweet;
                    const tweetHtml = `
                        <div class="tweet">
                            <div class="tweet-num">${i + 1}</div>
                            <div class="tweet-content">${escapeHtml(tweetData.text)}</div>
                            ${tweetData.image_path ? `
                                <div class="diagram">
                                    <div class="diagram-label">📊 ${tweetData.image_name || 'Diagram'}</div>
                                    ${tweetData.image_data ? 
                                        `<img src="data:image/png;base64,${tweetData.image_data}" alt="Diagram">` :
                                        `<div style="padding:20px;text-align:center;color:#666;">
                                            Diagram: ${tweetData.image_path}
                                        </div>`
                                    }
                                </div>
                            ` : ''}
                            <div class="tweet-meta">
                                ${tweetData.text.length} characters
                                ${tweetData.image_path ? ' • 📸 Has media' : ''}
                            </div>
                        </div>
                    `;
                    threadDiv.innerHTML += tweetHtml;
                });
                
                content.appendChild(threadDiv);
            });
        }
        
        function displayDiagramList(diagrams) {
            const content = document.getElementById('content');
            content.innerHTML = '<h3>Available Diagrams</h3>';
            
            diagrams.forEach(diagram => {
                content.innerHTML += `
                    <div class="tweet">
                        <strong>${diagram.name}</strong><br>
                        Path: ${diagram.path}<br>
                        Size: ${diagram.size}
                    </div>
                `;
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
        
        // Load threads on page load
        window.onload = () => loadThreads();
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
            # Return sample data
            sample = [{
                "topic": "Docker Best Practices (Sample)",
                "generatedTweets": [
                    "🐳 Let's explore Docker best practices that will save you hours!",
                    "1️⃣ Always use specific tags, never 'latest'",
                    "2️⃣ Multi-stage builds keep images small:\n\n📊 [Diagram Placeholder]",
                    "3️⃣ One process per container for better scaling",
                    "What's your favorite Docker tip? 👇"
                ]
            }]
            return jsonify({"threads": sample, "count": 1})
    except Exception as e:
        logger.error(f"Error loading threads: {e}")
        return jsonify({"error": str(e)})

@app.route('/api/pipeline/run', methods=['POST'])
def run_pipeline():
    """Simplified pipeline that just binds diagrams to existing threads"""
    try:
        logs = []
        
        # Load threads
        thread_file = Path("generated_threads_final.json")
        if not thread_file.exists():
            return jsonify({"error": "No threads found to process"})
        
        with open(thread_file, 'r') as f:
            threads = json.load(f)
            if not isinstance(threads, list):
                threads = [threads]
        
        logs.append({"level": "info", "message": f"Loaded {len(threads)} threads"})
        
        # Check for diagrams
        diagram_dirs = [
            Path("/home/kushagra/X/optimized"),
            Path("automated_diagrams/png"),
            Path("diagrams/png")
        ]
        
        available_diagrams = []
        for dir_path in diagram_dirs:
            if dir_path.exists():
                png_files = list(dir_path.glob("*.png"))
                available_diagrams.extend(png_files)
                if png_files:
                    logs.append({"level": "info", "message": f"Found {len(png_files)} diagrams in {dir_path}"})
        
        logs.append({"level": "info", "message": f"Total diagrams available: {len(available_diagrams)}"})
        
        # Simple diagram matching for demo
        processed_threads = []
        for thread in threads:
            # For demo, just add a diagram to tweet 3 if it mentions diagram
            tweets = thread.get('generatedTweets', thread.get('tweets', []))
            processed_tweets = []
            
            for i, tweet in enumerate(tweets):
                tweet_obj = {"text": tweet if isinstance(tweet, str) else tweet.get('text', tweet)}
                
                # Check if this tweet mentions a diagram
                if any(word in tweet_obj['text'].lower() for word in ['diagram', 'chart', 'visual', '📊', '📈']):
                    if available_diagrams:
                        # Pick first available diagram for demo
                        diagram_path = available_diagrams[0]
                        tweet_obj['image_path'] = str(diagram_path)
                        tweet_obj['image_name'] = diagram_path.name
                        
                        # Try to load and encode the image
                        try:
                            with open(diagram_path, 'rb') as img:
                                tweet_obj['image_data'] = base64.b64encode(img.read()).decode('utf-8')
                            logs.append({"level": "success", "message": f"Attached {diagram_path.name} to tweet {i+1}"})
                        except Exception as e:
                            logs.append({"level": "error", "message": f"Failed to load image: {e}"})
                
                processed_tweets.append(tweet_obj)
            
            processed_thread = {
                "topic": thread.get('topic', 'Thread'),
                "tweets": processed_tweets
            }
            processed_threads.append(processed_thread)
        
        logs.append({"level": "success", "message": "Pipeline completed successfully"})
        
        return jsonify({
            "threads": processed_threads,
            "logs": logs
        })
        
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        return jsonify({"error": str(e)})

@app.route('/api/diagrams')
def get_diagrams():
    """List available diagrams"""
    try:
        diagram_dirs = [
            Path("/home/kushagra/X/optimized"),
            Path("automated_diagrams/png"),
            Path("diagrams/png")
        ]
        
        all_diagrams = []
        for dir_path in diagram_dirs:
            if dir_path.exists():
                for png_file in dir_path.glob("*.png"):
                    all_diagrams.append({
                        "name": png_file.name,
                        "path": str(png_file),
                        "size": f"{png_file.stat().st_size / 1024:.1f} KB"
                    })
        
        return jsonify({"diagrams": all_diagrams})
        
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    port = 8081
    print(f"\n🚀 Preview Server with Diagram Integration")
    print(f"📍 URL: http://localhost:{port}/preview")
    print(f"📊 Includes basic diagram support\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)