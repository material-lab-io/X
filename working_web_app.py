#!/usr/bin/env python3
"""
Working web interface for Twitter/X content generator
"""

from flask import Flask, request, jsonify, render_template_string
import json
import os
from datetime import datetime
import logging

# Disable Flask logs
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

# Import generators
try:
    from simple_tweet_generator import SimpleTweetGenerator
    from unified_tweet_generator import UnifiedTweetGenerator
    
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
        gemini_key = config.get('api_keys', {}).get('gemini')
    
    simple_gen = SimpleTweetGenerator()
    unified_gen = UnifiedTweetGenerator(gemini_key) if gemini_key else None
except Exception as e:
    print(f"Generator import error: {e}")
    simple_gen = None
    unified_gen = None

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Twitter/X Content Generator</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        
        .container {
            background: white;
            border-radius: 12px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        h1 {
            color: #1DA1F2;
            margin-bottom: 30px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #14171A;
        }
        
        input, select, textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #E1E8ED;
            border-radius: 8px;
            font-size: 16px;
        }
        
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #1DA1F2;
        }
        
        button {
            background: #1DA1F2;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 24px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
        }
        
        button:hover {
            background: #1a8cd8;
        }
        
        button:disabled {
            background: #AAB8C2;
            cursor: not-allowed;
        }
        
        .output {
            margin-top: 30px;
            display: none;
        }
        
        .tweet {
            background: #F5F8FA;
            border: 1px solid #E1E8ED;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
        }
        
        .tweet-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            font-size: 14px;
            color: #657786;
        }
        
        .tweet-content {
            font-size: 16px;
            line-height: 1.5;
            white-space: pre-wrap;
            margin-bottom: 15px;
        }
        
        .tweet-actions {
            display: flex;
            gap: 10px;
        }
        
        .action-btn {
            padding: 8px 16px;
            border: 1px solid #E1E8ED;
            background: white;
            border-radius: 20px;
            cursor: pointer;
            font-size: 14px;
        }
        
        .action-btn:hover {
            background: #F5F8FA;
            border-color: #1DA1F2;
        }
        
        .loading {
            display: none;
            text-align: center;
            margin: 20px 0;
        }
        
        .spinner {
            border: 3px solid #E1E8ED;
            border-top: 3px solid #1DA1F2;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .error {
            background: #FFEBEE;
            color: #C62828;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }
        
        .success {
            background: #E8F5E9;
            color: #2E7D32;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐦 Twitter/X Content Generator</h1>
        
        <form id="generatorForm">
            <div class="form-group">
                <label for="topic">Topic *</label>
                <input type="text" id="topic" name="topic" placeholder="e.g., Docker optimization, AI agents" required>
            </div>
            
            <div class="form-group">
                <label for="type">Content Type</label>
                <select id="type" name="type">
                    <option value="single">Single Tweet</option>
                    <option value="thread">Thread (5-7 tweets)</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="category">Category</label>
                <select id="category" name="category">
                    <option value="">Auto-detect</option>
                    <option value="ai_agents">AI Agent Testing</option>
                    <option value="docker">Docker</option>
                    <option value="video_models">Video Models</option>
                    <option value="llms">LLMs</option>
                    <option value="devtools">DevTools</option>
                    <option value="coding">Agentic Coding</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="generator">Generator</label>
                <select id="generator" name="generator">
                    <option value="simple">Simple (No API needed)</option>
                    {% if has_gemini %}
                    <option value="unified">Unified (Gemini-powered)</option>
                    {% endif %}
                </select>
            </div>
            
            <div class="form-group">
                <label for="context">Additional Context (Optional)</label>
                <textarea id="context" name="context" rows="3" placeholder="Any specific details or context..."></textarea>
            </div>
            
            <button type="submit" id="generateBtn">Generate Content</button>
        </form>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Generating your content...</p>
        </div>
        
        <div id="output" class="output"></div>
    </div>

    <script>
        document.getElementById('generatorForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('generateBtn').disabled = true;
            document.getElementById('output').style.display = 'none';
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.error) {
                    showError(result.error);
                } else {
                    displayContent(result);
                }
            } catch (error) {
                showError('Error: ' + error.message);
            } finally {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('generateBtn').disabled = false;
            }
        });
        
        function displayContent(result) {
            const output = document.getElementById('output');
            output.innerHTML = '';
            output.style.display = 'block';
            
            if (result.type === 'thread') {
                result.tweets.forEach((tweet, index) => {
                    output.appendChild(createTweetElement(tweet.content, index + 1, tweet.character_count));
                });
            } else {
                output.appendChild(createTweetElement(result.content, null, result.character_count));
            }
        }
        
        function createTweetElement(content, position, charCount) {
            const div = document.createElement('div');
            div.className = 'tweet';
            
            div.innerHTML = `
                <div class="tweet-header">
                    <span>${position ? 'Tweet ' + position : 'Single Tweet'}</span>
                    <span>${charCount}/280 characters</span>
                </div>
                <div class="tweet-content">${escapeHtml(content)}</div>
                <div class="tweet-actions">
                    <button class="action-btn" onclick="copyToClipboard('${escapeHtml(content).replace(/'/g, "\\'")}')">
                        📋 Copy
                    </button>
                    <button class="action-btn" onclick="regenerate()">
                        🔄 Regenerate
                    </button>
                </div>
            `;
            
            return div;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                showSuccess('Copied to clipboard!');
            });
        }
        
        function regenerate() {
            document.getElementById('generateBtn').click();
        }
        
        function showError(message) {
            const output = document.getElementById('output');
            output.innerHTML = `<div class="error">${message}</div>`;
            output.style.display = 'block';
        }
        
        function showSuccess(message) {
            const div = document.createElement('div');
            div.className = 'success';
            div.textContent = message;
            document.body.appendChild(div);
            setTimeout(() => div.remove(), 3000);
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, has_gemini=(unified_gen is not None))

@app.route('/api/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        topic = data.get('topic', '')
        content_type = data.get('type', 'single')
        category = data.get('category', '') or None
        generator_type = data.get('generator', 'simple')
        context = data.get('context', '')
        
        if not topic:
            return jsonify({'error': 'Topic is required'})
        
        # Use appropriate generator
        if generator_type == 'unified' and unified_gen:
            result = unified_gen.generate_tweet(
                topic=topic,
                context=context
            )
            if content_type == 'single':
                return jsonify({
                    'type': 'single',
                    'content': result,
                    'character_count': len(result)
                })
            else:
                # For thread, generate multiple times
                tweets = []
                for i in range(5):
                    tweet = unified_gen.generate_tweet(
                        topic=f"{topic} (part {i+1})",
                        context=context
                    )
                    tweets.append({
                        'content': tweet,
                        'position': i + 1,
                        'character_count': len(tweet)
                    })
                return jsonify({
                    'type': 'thread',
                    'tweets': tweets
                })
        else:
            # Use simple generator
            if content_type == 'thread':
                result = simple_gen.generate_thread(topic, category)
                return jsonify({
                    'type': 'thread',
                    'tweets': result
                })
            else:
                result = simple_gen.generate_single(topic, category)
                return jsonify({
                    'type': 'single',
                    'content': result,
                    'character_count': len(result)
                })
                
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.now().isoformat()})

if __name__ == '__main__':
    print("\n🚀 Starting Twitter/X Content Generator")
    print("=" * 40)
    print("Access at: http://localhost:5000")
    print("=" * 40)
    print("\nPress Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)