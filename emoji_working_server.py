#!/usr/bin/env python3
"""
Emoji Working Server - Properly displays emojis from generated content
"""

from flask import Flask, render_template_string, request, redirect, url_for
import json
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Simple working template
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Tweet Preview</title>
    <meta charset="UTF-8">
    <style>
        body { 
            font-family: Arial, sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
        }
        h1 { color: #1da1f2; }
        .tweet {
            background: white;
            padding: 20px;
            margin: 10px 0;
            border-radius: 10px;
            border: 1px solid #e1e8ed;
        }
        .tweet-number {
            color: #1da1f2;
            font-weight: bold;
            margin-bottom: 10px;
        }
        .tweet-text {
            white-space: pre-wrap;
            line-height: 1.5;
        }
        .meta {
            color: #666;
            font-size: 14px;
            margin-top: 10px;
        }
        .button {
            display: inline-block;
            padding: 10px 20px;
            background: #1da1f2;
            color: white;
            text-decoration: none;
            border-radius: 20px;
            margin: 10px 5px;
        }
        .button:hover {
            background: #1a91da;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🐦 Tweet Preview</h1>
        <a href="/generate" class="button">Generate New</a>
    </div>
    
    {% if error %}
        <div style="background: #fee; padding: 20px; border-radius: 10px; color: #c00;">
            Error: {{ error }}
        </div>
    {% else %}
        {% for tweet in tweets %}
            <div class="tweet">
                <div class="tweet-number">Tweet {{ loop.index }}</div>
                <div class="tweet-text">{{ tweet.text }}</div>
                <div class="meta">{{ tweet.length }} characters</div>
            </div>
        {% endfor %}
    {% endif %}
</body>
</html>
"""

@app.route('/')
def index():
    return redirect(url_for('preview'))

@app.route('/generate')
def generate():
    return '<h1>Generate page would go here</h1><a href="/preview">View Preview</a>'

@app.route('/preview')
def preview():
    tweets = []
    error = None
    
    try:
        # Read the generated file
        json_path = Path('generated_threads_final.json')
        if not json_path.exists():
            error = "No generated content found"
        else:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Get the tweets
            if data and isinstance(data, list) and len(data) > 0:
                thread_data = data[0]
                raw_tweets = thread_data.get('generatedTweets', [])
                
                for tweet_text in raw_tweets:
                    # This is the key fix - use json.loads to decode Unicode
                    try:
                        # Wrap in quotes to make valid JSON, then decode
                        decoded_text = json.loads('"' + tweet_text + '"')
                    except:
                        # If that fails, try without adding quotes
                        try:
                            decoded_text = json.loads(tweet_text)
                        except:
                            # Last resort - use as is
                            decoded_text = tweet_text
                    
                    tweets.append({
                        'text': decoded_text,
                        'length': len(decoded_text)
                    })
            else:
                error = "Invalid data format"
                
    except Exception as e:
        error = str(e)
        logger.error(f"Error in preview: {e}")
    
    return render_template_string(TEMPLATE, tweets=tweets, error=error)

if __name__ == '__main__':
    print("\n✨ Emoji Working Server")
    print("🔗 http://localhost:5000/preview")
    print("\nThis version properly displays emojis! 🎉\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)