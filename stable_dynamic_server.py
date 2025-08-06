#!/usr/bin/env python3
"""
Stable Dynamic Flask Server - Simplified version
"""

from flask import Flask, render_template_string, request, redirect, url_for, jsonify, flash
import json
import os
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-for-flash-messages'

# Try to load API key
GEMINI_API_KEY = None
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
        GEMINI_API_KEY = config.get('api_keys', {}).get('gemini')
except:
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# Store current generation
current_generation = {}

# Simple HTML template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Tweet Generator</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            background: #f5f5f5;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
        }
        .card {
            background: white;
            padding: 30px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        h1 {
            color: #1da1f2;
            margin-bottom: 10px;
        }
        h2 {
            color: #14171a;
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
        input[type="text"],
        textarea,
        select {
            width: 100%;
            padding: 10px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 16px;
        }
        input[type="text"]:focus,
        textarea:focus,
        select:focus {
            outline: none;
            border-color: #1da1f2;
        }
        textarea {
            min-height: 100px;
            resize: vertical;
        }
        .radio-group {
            display: flex;
            gap: 20px;
        }
        button {
            background: #1da1f2;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 24px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
        }
        button:hover {
            background: #1a91da;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .alert-success {
            background: #d1ecf1;
            color: #0c5460;
        }
        .alert-error {
            background: #f8d7da;
            color: #721c24;
        }
        .alert-info {
            background: #fff3cd;
            color: #856404;
        }
        .tweet {
            background: #f8f9fa;
            border: 1px solid #e1e8ed;
            border-radius: 8px;
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
            font-size: 14px;
        }
        .tweet-content {
            white-space: pre-wrap;
            margin-bottom: 10px;
        }
        .tweet-meta {
            font-size: 13px;
            color: #657786;
        }
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        .help-text {
            font-size: 14px;
            color: #657786;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        {% if page == 'generate' %}
            <div class="card">
                <h1>🐦 AI Tweet Generator</h1>
                <p style="color: #657786;">Generate custom Twitter threads with AI</p>
            </div>
            
            {% if message %}
                <div class="alert alert-{{ message_type }}">
                    {{ message }}
                </div>
            {% endif %}
            
            <div class="card">
                <h2>Generate New Thread</h2>
                
                <form method="POST" action="/generate">
                    <div class="form-group">
                        <label for="topic">Topic / Subject *</label>
                        <input type="text" id="topic" name="topic" required 
                               placeholder="e.g., Docker Container Optimization"
                               value="{{ topic or '' }}">
                        <p class="help-text">What do you want to create a thread about?</p>
                    </div>
                    
                    <div class="form-group">
                        <label>Content Type *</label>
                        <div class="radio-group">
                            <label>
                                <input type="radio" name="content_type" value="single"> 
                                Single Post
                            </label>
                            <label>
                                <input type="radio" name="content_type" value="thread" checked> 
                                Thread
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
                        <textarea id="context" name="context" 
                                  placeholder="Add any specific details...">{{ context or '' }}</textarea>
                    </div>
                    
                    <div class="button-group">
                        <button type="submit">🧠 Generate Thread</button>
                        <button type="button" onclick="window.location.href='/preview'">
                            👁️ View Preview
                        </button>
                    </div>
                </form>
            </div>
            
        {% elif page == 'preview' %}
            <div class="card">
                <h1>🐦 Thread Preview</h1>
                <p style="color: #657786;">Review your generated content</p>
            </div>
            
            <div class="card">
                {% if threads %}
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h2>{{ threads[0].topic }}</h2>
                        <div class="button-group">
                            <button onclick="window.location.href='/generate'">
                                ⬅️ Edit
                            </button>
                            <button onclick="regenerate()">
                                🔁 Regenerate
                            </button>
                            <button disabled>
                                🚀 Post
                            </button>
                        </div>
                    </div>
                    
                    {% for thread in threads %}
                        {% for tweet in thread.tweets %}
                            <div class="tweet">
                                <div class="tweet-number">{{ loop.index }}</div>
                                <div class="tweet-content">{{ tweet.text }}</div>
                                <div class="tweet-meta">
                                    {{ tweet.text|length }} characters
                                    {% if '[Diagram' in tweet.text %}
                                        • 📊 Contains diagram placeholder
                                    {% endif %}
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
    
    <script>
        function regenerate() {
            fetch('/regenerate', {method: 'POST'})
                .then(() => window.location.reload());
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return redirect(url_for('generate'))

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        # Get form data
        topic = request.form.get('topic', '').strip()
        content_type = request.form.get('content_type', 'thread')
        template = request.form.get('template', '')
        context = request.form.get('context', '').strip()
        
        if not topic or not template:
            return render_template_string(HTML_TEMPLATE, 
                page='generate',
                message='Please fill all required fields',
                message_type='error',
                topic=topic,
                context=context
            )
        
        # Store for regeneration
        global current_generation
        current_generation = {
            'topic': topic,
            'content_type': content_type,
            'template': template,
            'context': context
        }
        
        try:
            # Try to use actual generator
            if GEMINI_API_KEY:
                try:
                    from unified_tweet_generator import UnifiedTweetGenerator
                    generator = UnifiedTweetGenerator(GEMINI_API_KEY, auto_polish=True)
                    
                    if content_type == 'thread':
                        result = generator.generate_thread(topic, template, context)
                    else:
                        result = generator.generate_single_tweet(topic, template, context)
                    
                    # Save result
                    with open('generated_threads_final.json', 'w') as f:
                        json.dump([result], f, indent=2)
                    
                    logger.info(f"Generated {content_type} for {topic}")
                    
                except Exception as e:
                    logger.error(f"Generation failed: {e}")
                    raise
            else:
                # Create sample data
                tweets = []
                if content_type == 'thread':
                    tweets = [
                        f"🚀 Let's explore {topic}! This thread will cover the key concepts and best practices.",
                        f"First, understanding the fundamentals of {topic} is crucial for success.",
                        f"Here's a visual breakdown:\n\n📊 [Diagram Placeholder]",
                        f"The main benefits include improved performance and scalability.",
                        f"What's your experience with {topic}? Share your thoughts! 💭"
                    ]
                else:
                    tweets = [f"💡 Quick tip about {topic}: Always consider best practices and context."]
                
                result = {
                    'topic': topic,
                    'template': template,
                    'generatedTweets': tweets
                }
                
                with open('generated_threads_final.json', 'w') as f:
                    json.dump([result], f, indent=2)
            
            return redirect(url_for('preview'))
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return render_template_string(HTML_TEMPLATE,
                page='generate',
                message=f'Generation failed: {str(e)}',
                message_type='error',
                topic=topic,
                context=context
            )
    
    # GET request
    return render_template_string(HTML_TEMPLATE, page='generate')

@app.route('/preview')
def preview():
    try:
        # Load generated threads
        if Path('generated_threads_final.json').exists():
            with open('generated_threads_final.json', 'r') as f:
                data = json.load(f)
                
            threads = []
            for item in (data if isinstance(data, list) else [data]):
                tweets = []
                raw_tweets = item.get('generatedTweets', item.get('tweets', []))
                
                for tweet in raw_tweets:
                    if isinstance(tweet, str):
                        tweets.append({'text': tweet})
                    else:
                        tweets.append(tweet)
                
                threads.append({
                    'topic': item.get('topic', 'Thread'),
                    'tweets': tweets
                })
            
            return render_template_string(HTML_TEMPLATE, page='preview', threads=threads)
        else:
            return render_template_string(HTML_TEMPLATE, page='preview', threads=None)
            
    except Exception as e:
        logger.error(f"Preview error: {e}")
        return redirect(url_for('generate'))

@app.route('/regenerate', methods=['POST'])
def regenerate():
    if current_generation:
        # Resubmit the form data
        return generate()
    return redirect(url_for('generate'))

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'has_api_key': bool(GEMINI_API_KEY)})

if __name__ == '__main__':
    port = 5000
    print(f"\n🚀 Stable Dynamic Server Starting")
    print(f"📍 Generate: http://localhost:{port}/generate")
    print(f"👁️ Preview: http://localhost:{port}/preview")
    print(f"\nPress Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)