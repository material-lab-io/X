#!/usr/bin/env python3
"""Simple test server to verify connectivity"""

from flask import Flask, jsonify, request
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
    <head>
        <title>Twitter/X Content Generator - Working!</title>
        <style>
            body { font-family: Arial; padding: 40px; background: #f0f0f0; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
            h1 { color: #1da1f2; }
            .status { color: green; font-weight: bold; }
            input, textarea { width: 100%; padding: 10px; margin: 10px 0; }
            button { background: #1da1f2; color: white; padding: 10px 20px; border: none; cursor: pointer; }
            button:hover { background: #1a8cd8; }
            #result { margin-top: 20px; padding: 20px; background: #f8f8f8; border-radius: 5px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Twitter/X Content Generator</h1>
            <p class="status">✅ Server is running successfully!</p>
            <p>Connection established at: """ + str(datetime.now()) + """</p>
            
            <h2>Generate Content</h2>
            <form id="genForm">
                <label>Topic:</label>
                <input type="text" id="topic" placeholder="e.g., Docker architecture" required>
                
                <label>Type:</label>
                <select id="type">
                    <option value="single">Single Tweet</option>
                    <option value="thread">Thread</option>
                </select>
                
                <button type="submit">Generate</button>
            </form>
            
            <div id="result"></div>
        </div>
        
        <script>
        document.getElementById('genForm').onsubmit = async (e) => {
            e.preventDefault();
            const topic = document.getElementById('topic').value;
            const type = document.getElementById('type').value;
            
            document.getElementById('result').innerHTML = 'Generating...';
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({topic, type})
                });
                const data = await response.json();
                
                if (data.success) {
                    let html = '<h3>Generated Content:</h3>';
                    if (type === 'single') {
                        html += '<p>' + data.content + '</p>';
                    } else {
                        data.tweets.forEach((tweet, i) => {
                            html += '<p><strong>Tweet ' + (i+1) + ':</strong><br>' + tweet + '</p>';
                        });
                    }
                    document.getElementById('result').innerHTML = html;
                } else {
                    document.getElementById('result').innerHTML = 'Error: ' + data.error;
                }
            } catch (err) {
                document.getElementById('result').innerHTML = 'Error: ' + err.message;
            }
        };
        </script>
    </body>
    </html>
    """

@app.route('/test')
def test():
    return jsonify({
        'status': 'working',
        'message': 'Server is running correctly!',
        'timestamp': str(datetime.now())
    })

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    topic = data.get('topic', 'Docker')
    content_type = data.get('type', 'single')
    
    if content_type == 'single':
        # Simple single tweet
        content = f"🚀 Let's talk about {topic}! Here's a key insight that often gets overlooked: understanding the fundamentals makes everything else click. What's your experience with {topic}? #tech #coding"
        return jsonify({
            'success': True,
            'content': content,
            'character_count': len(content)
        })
    else:
        # Simple thread
        tweets = [
            f"🧵 Deep dive into {topic}! Here's what I've learned after months of exploration:",
            f"First key insight: {topic} isn't just about the technology - it's about solving real problems efficiently.",
            f"The biggest misconception? That {topic} is overly complex. Once you understand the core concepts, it becomes intuitive.",
            f"My advice for learning {topic}: Start small, build something real, and iterate. Theory only takes you so far.",
            f"What questions do you have about {topic}? Drop them below! 👇"
        ]
        return jsonify({
            'success': True,
            'tweets': tweets,
            'total_tweets': len(tweets)
        })

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Simple Test Server Starting...")
    print("="*50)
    print("\nServer will run on: http://localhost:5000")
    print("\nIMPORTANT: Make sure you have SSH port forwarding!")
    print("In a NEW terminal, run:")
    print("  ssh -L 5000:localhost:5000 kushagra@100.114.8.73")
    print("\nThen access: http://localhost:5000")
    print("="*50 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)