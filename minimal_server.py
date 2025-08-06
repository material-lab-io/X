#!/usr/bin/env python3
"""
Minimal Flask Server - Focuses on working Unicode display
"""

from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import json
import os
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load API key
GEMINI_API_KEY = None
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
        GEMINI_API_KEY = config.get('api_keys', {}).get('gemini')
except:
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# Store generation state
current_generation = {}

# Minimal HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Tweet Generator</title>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, Arial, sans-serif;
            background: #f5f5f5;
            margin: 20px;
            line-height: 1.5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        .header {
            background: white;
            padding: 25px;
            border-radius: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            text-align: center;
        }
        h1 {
            color: #1da1f2;
            margin: 0;
        }
        .card {
            background: white;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
        }
        input, textarea, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 16px;
            box-sizing: border-box;
        }
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #1da1f2;
        }
        button, .button {
            background: #1da1f2;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 24px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin-right: 10px;
        }
        button:hover, .button:hover {
            background: #1a91da;
        }
        .btn-secondary {
            background: #e1e8ed;
            color: #14171a;
        }
        .btn-secondary:hover {
            background: #d1d8dd;
        }
        .tweet {
            background: #f8f9fa;
            border: 1px solid #e1e8ed;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            position: relative;
        }
        .tweet-number {
            position: absolute;
            left: -15px;
            top: 20px;
            background: #1da1f2;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
        }
        .tweet-content {
            white-space: pre-wrap;
            word-wrap: break-word;
            font-size: 16px;
            line-height: 1.4;
            margin-bottom: 10px;
        }
        .tweet-meta {
            font-size: 14px;
            color: #657786;
        }
        .radio-group {
            display: flex;
            gap: 20px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐦 AI Tweet Generator</h1>
            <p style="color: #657786; margin: 10px 0 0 0;">Generate custom Twitter threads with AI</p>
        </div>
        
        {% if page == 'generate' %}
            <div class="card">
                <h2>Generate New Thread</h2>
                
                <form method="POST" action="/generate">
                    <div class="form-group">
                        <label for="topic">Topic / Subject *</label>
                        <input type="text" id="topic" name="topic" required 
                               placeholder="e.g., Docker Container Optimization">
                    </div>
                    
                    <div class="form-group">
                        <label>Content Type *</label>
                        <div class="radio-group">
                            <label>
                                <input type="radio" name="content_type" value="single"> Single Post
                            </label>
                            <label>
                                <input type="radio" name="content_type" value="thread" checked> Thread
                            </label>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="template">Template *</label>
                        <select id="template" name="template" required>
                            <option value="">Select a template...</option>
                            <option value="ProblemSolution">Problem/Solution</option>
                            <option value="ConceptualDeepDive">Conceptual Deep Dive</option>
                            <option value="WorkflowShare">Workflow Share</option>
                            <option value="TechnicalBreakdown">Technical Breakdown</option>
                            <option value="LearningShare">Learning Share</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="context">Additional Context (Optional)</label>
                        <textarea id="context" name="context" rows="3"
                                  placeholder="Add any specific details..."></textarea>
                    </div>
                    
                    <button type="submit">🧠 Generate Thread</button>
                    <a href="/preview" class="button btn-secondary">👁️ View Preview</a>
                </form>
            </div>
            
        {% elif page == 'preview' %}
            <div class="card">
                {% if threads %}
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h2>{{ threads[0].topic }}</h2>
                        <div>
                            <a href="/generate" class="button btn-secondary">⬅️ Edit</a>
                            <form method="POST" action="/regenerate" style="display: inline;">
                                <button type="submit">🔁 Regenerate</button>
                            </form>
                        </div>
                    </div>
                    
                    {% for thread in threads %}
                        {% for tweet in thread.tweets %}
                            <div class="tweet">
                                <div class="tweet-number">{{ loop.index }}</div>
                                <div class="tweet-content">{{ tweet.text }}</div>
                                <div class="tweet-meta">
                                    {{ tweet.char_count }} characters
                                </div>
                            </div>
                        {% endfor %}
                    {% endfor %}
                    
                {% else %}
                    <p style="text-align: center; color: #657786;">
                        No threads to preview. 
                        <a href="/generate">Generate a thread</a>
                    </p>
                {% endif %}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

def fix_unicode_properly(text):
    """Fix Unicode escape sequences using json.loads method"""
    if not isinstance(text, str):
        return str(text)
    
    try:
        # Use json.loads to properly decode Unicode escapes
        # Need to wrap in quotes to make it a valid JSON string
        decoded = json.loads(f'"{text}"')
        return decoded
    except:
        # If json.loads fails, return original
        return text

@app.route('/')
def index():
    return redirect(url_for('generate'))

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        form_data = {
            'topic': request.form.get('topic', '').strip(),
            'content_type': request.form.get('content_type', 'thread'),
            'template': request.form.get('template', ''),
            'context': request.form.get('context', '').strip()
        }
        
        if form_data['topic'] and form_data['template']:
            # For now, just redirect to preview to test Unicode display
            return redirect(url_for('preview'))
    
    return render_template_string(HTML_TEMPLATE, page='generate')

@app.route('/preview')
def preview():
    threads = []
    
    try:
        json_file = Path('generated_threads_final.json')
        if json_file.exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for item in (data if isinstance(data, list) else [data]):
                tweets = []
                raw_tweets = item.get('generatedTweets', item.get('tweets', []))
                
                for tweet in raw_tweets:
                    tweet_text = tweet if isinstance(tweet, str) else tweet.get('text', str(tweet))
                    
                    # Fix Unicode properly
                    tweet_text = fix_unicode_properly(tweet_text)
                    
                    tweets.append({
                        'text': tweet_text,
                        'char_count': len(tweet_text)
                    })
                
                threads.append({
                    'topic': item.get('topic', 'Thread'),
                    'tweets': tweets
                })
    
    except Exception as e:
        logger.error(f"Preview error: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    return render_template_string(HTML_TEMPLATE, page='preview', threads=threads)

@app.route('/regenerate', methods=['POST'])
def regenerate():
    return redirect(url_for('preview'))

if __name__ == '__main__':
    port = 5000
    
    # First kill any existing servers
    os.system("pkill -f 'python.*server.py'")
    
    print(f"\n🚀 Minimal Tweet Generator Server")
    print(f"📍 URL: http://localhost:{port}/")
    print(f"\nEmojis will display correctly! 🎉")
    print(f"Press Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)