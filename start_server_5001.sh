#!/bin/bash
# Start server on port 5001 as backup

echo "🚀 Starting Twitter/X Content Generator on port 5001"
echo "=================================================="
echo ""
echo "📌 SSH Port Forwarding Instructions:"
echo ""
echo "From your Windows WSL terminal, run:"
echo "  ssh -L 5001:localhost:5001 kushagra@your-server"
echo ""
echo "Then access in browser: http://localhost:5001"
echo ""

# Kill any existing process on 5001
pkill -f "python.*5001" 2>/dev/null || true
lsof -ti:5001 | xargs kill -9 2>/dev/null || true

# Activate virtual environment
source venv/bin/activate

# Create a modified web interface for port 5001
cat > temp_web_interface_5001.py << 'EOF'
#!/usr/bin/env python3
from flask import Flask, render_template_string, request, jsonify
import json
import os
from datetime import datetime
from pathlib import Path

app = Flask(__name__)

# Try to import the generator
try:
    from tweet_generator import TweetGenerator
    generator = TweetGenerator()
except Exception as e:
    print(f"Warning: Could not import TweetGenerator: {e}")
    # Fallback to simple generator
    try:
        from simple_tweet_generator import SimpleTweetGenerator
        generator = SimpleTweetGenerator()
    except:
        generator = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Tweet Generator - Port 5001</title>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 { color: #1DA1F2; }
        textarea, input {
            width: 100%;
            padding: 10px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        button {
            background: #1DA1F2;
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
        }
        button:hover { background: #1a8cd8; }
        .tweet {
            background: #f8f9fa;
            padding: 15px;
            margin: 10px 0;
            border-radius: 10px;
            border: 1px solid #e1e8ed;
        }
        .status { 
            margin: 20px 0;
            padding: 15px;
            border-radius: 5px;
            background: #e3f2fd;
        }
        .error {
            background: #ffebee;
            color: #c62828;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Twitter/X Content Generator</h1>
        <p>Running on port 5001</p>
        
        <form id="generateForm">
            <textarea id="topic" name="topic" rows="3" placeholder="Enter your topic (e.g., 'Building Docker containers efficiently')"></textarea>
            <button type="submit">Generate Tweet</button>
        </form>
        
        <div id="status"></div>
        <div id="results"></div>
    </div>
    
    <script>
        document.getElementById('generateForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const topic = document.getElementById('topic').value;
            const statusDiv = document.getElementById('status');
            const resultsDiv = document.getElementById('results');
            
            if (!topic.trim()) {
                statusDiv.innerHTML = '<div class="status error">Please enter a topic</div>';
                return;
            }
            
            statusDiv.innerHTML = '<div class="status">🔄 Generating content...</div>';
            resultsDiv.innerHTML = '';
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ topic: topic })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    statusDiv.innerHTML = '<div class="status">✅ Generated successfully!</div>';
                    resultsDiv.innerHTML = data.tweets.map((tweet, i) => 
                        `<div class="tweet"><strong>Tweet ${i+1}:</strong><br>${tweet}</div>`
                    ).join('');
                } else {
                    statusDiv.innerHTML = `<div class="status error">❌ Error: ${data.error}</div>`;
                }
            } catch (error) {
                statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        topic = data.get('topic', '')
        
        if not topic:
            return jsonify({'success': False, 'error': 'No topic provided'})
        
        if generator:
            # Try to generate content
            try:
                result = generator.generate_tweet(topic)
                if isinstance(result, str):
                    tweets = [result]
                elif isinstance(result, list):
                    tweets = result
                else:
                    tweets = [str(result)]
            except Exception as e:
                # Fallback to simple response
                tweets = [f"🔍 Exploring {topic}:\n\nThis is a test response. The full generator will provide AI-generated content about {topic}."]
        else:
            # No generator available, return test response
            tweets = [f"📝 Topic: {topic}\n\nServer is running but generator not configured. Please check API keys in config.json"]
        
        return jsonify({
            'success': True,
            'tweets': tweets,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("Server starting on http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)
EOF

# Start the server
python temp_web_interface_5001.py