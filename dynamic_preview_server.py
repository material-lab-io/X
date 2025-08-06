#!/usr/bin/env python3
"""
Dynamic Flask Preview Server with Full Generation Pipeline
Integrates Phase 1-4 for custom topic generation and preview
"""

from flask import Flask, render_template_string, request, redirect, url_for, jsonify, flash
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import logging
import base64
import traceback
from typing import Dict, List, Optional

# Import Phase 1-4 modules
sys.path.append(str(Path(__file__).parent))

try:
    from unified_tweet_generator import UnifiedTweetGenerator
    print("✓ Imported unified_tweet_generator")
except ImportError as e:
    print(f"⚠️ Could not import unified_tweet_generator: {e}")
    UnifiedTweetGenerator = None

try:
    from diagram_automation_pipeline import DiagramAutomationPipeline
    print("✓ Imported diagram_automation_pipeline")
except ImportError as e:
    print(f"⚠️ Could not import diagram_automation_pipeline: {e}")
    DiagramAutomationPipeline = None

try:
    from tweet_diagram_binder import TweetDiagramBinder
    print("✓ Imported tweet_diagram_binder")
except ImportError as e:
    print(f"⚠️ Could not import tweet_diagram_binder: {e}")
    TweetDiagramBinder = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-for-flash-messages'

# Load API key
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
        GEMINI_API_KEY = config.get('api_keys', {}).get('gemini')
except:
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# Global state for current generation
current_generation = {
    'topic': None,
    'content_type': None,
    'template': None,
    'context': None,
    'generated_at': None,
    'threads': []
}

# Base template for consistent styling
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Tweet Generator{% endblock %}</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            background-color: #f7f9fa;
            color: #14171a;
            line-height: 1.5;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: white;
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
            margin-bottom: 20px;
            text-align: center;
        }
        
        h1 {
            color: #1da1f2;
            font-size: 28px;
            margin-bottom: 5px;
        }
        
        .subtitle {
            color: #657786;
            font-size: 16px;
        }
        
        .main-content {
            background: white;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #14171a;
        }
        
        input[type="text"],
        textarea,
        select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 16px;
            font-family: inherit;
            transition: border-color 0.2s;
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
        
        .radio-group,
        .checkbox-group {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        
        .radio-item,
        .checkbox-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        input[type="radio"],
        input[type="checkbox"] {
            width: 18px;
            height: 18px;
            cursor: pointer;
        }
        
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 30px;
            flex-wrap: wrap;
        }
        
        button,
        .button {
            padding: 12px 24px;
            border: none;
            border-radius: 24px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            transition: all 0.2s;
        }
        
        .btn-primary {
            background: #1da1f2;
            color: white;
        }
        
        .btn-primary:hover {
            background: #1a91da;
        }
        
        .btn-secondary {
            background: #e1e8ed;
            color: #14171a;
        }
        
        .btn-secondary:hover {
            background: #d1d8dd;
        }
        
        .btn-disabled {
            background: #e1e8ed;
            color: #657786;
            cursor: not-allowed;
            opacity: 0.6;
        }
        
        .alert {
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .alert-success {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .alert-info {
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }
        
        /* Preview specific styles */
        .thread {
            margin-bottom: 30px;
            border-bottom: 1px solid #e1e8ed;
            padding-bottom: 30px;
        }
        
        .thread:last-child {
            border-bottom: none;
            padding-bottom: 0;
        }
        
        .thread-header {
            margin-bottom: 20px;
        }
        
        .thread-topic {
            font-size: 22px;
            font-weight: 700;
            color: #14171a;
            margin-bottom: 5px;
        }
        
        .thread-meta {
            font-size: 14px;
            color: #657786;
        }
        
        .tweet-card {
            position: relative;
            background: #f8f9fa;
            border: 1px solid #e1e8ed;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            transition: all 0.2s;
        }
        
        .tweet-card:hover {
            border-color: #1da1f2;
            box-shadow: 0 2px 8px rgba(29, 161, 242, 0.1);
        }
        
        .tweet-number {
            position: absolute;
            left: -15px;
            top: 20px;
            width: 30px;
            height: 30px;
            background: #1da1f2;
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 14px;
            font-weight: bold;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .tweet-content {
            white-space: pre-wrap;
            word-wrap: break-word;
            line-height: 1.5;
            margin-bottom: 10px;
        }
        
        .tweet-meta {
            display: flex;
            gap: 15px;
            font-size: 13px;
            color: #657786;
        }
        
        .diagram-container {
            margin: 15px 0;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #e1e8ed;
            background: white;
        }
        
        .diagram-label {
            padding: 10px 15px;
            background: #e8f5fd;
            color: #1da1f2;
            font-size: 14px;
            font-weight: 500;
            border-bottom: 1px solid #e1e8ed;
        }
        
        .diagram-image {
            display: block;
            width: 100%;
            height: auto;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #657786;
        }
        
        .spinner {
            display: inline-block;
            width: 30px;
            height: 30px;
            border: 3px solid #e1e8ed;
            border-top-color: #1da1f2;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 10px;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .help-text {
            font-size: 14px;
            color: #657786;
            margin-top: 5px;
        }
        
        @media (max-width: 600px) {
            .container {
                padding: 10px;
            }
            
            .main-content {
                padding: 20px;
            }
            
            .button-group {
                flex-direction: column;
            }
            
            button, .button {
                width: 100%;
                justify-content: center;
            }
        }
    </style>
    {% block extra_style %}{% endblock %}
</head>
<body>
    <div class="container">
        <header>
            <h1>🐦 AI Tweet Generator</h1>
            <p class="subtitle">Generate, preview, and publish Twitter threads with diagrams</p>
        </header>
        
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <div class="main-content">
            {% block content %}{% endblock %}
        </div>
    </div>
    
    {% block extra_script %}{% endblock %}
</body>
</html>
"""

# Generate form template
GENERATE_TEMPLATE = """
{% extends base_template %}

{% block title %}Generate Thread - Tweet Generator{% endblock %}

{% block content %}
<h2>Generate New Thread</h2>
<p style="color: #657786; margin-bottom: 30px;">
    Create custom Twitter threads with AI-generated content and automatic diagram integration.
</p>

<form method="POST" action="{{ url_for('generate') }}">
    <div class="form-group">
        <label for="topic">Topic / Subject *</label>
        <input type="text" id="topic" name="topic" required 
               placeholder="e.g., Docker Container Optimization, Microservices Best Practices"
               value="{{ request.form.get('topic', '') }}">
        <p class="help-text">What do you want to create a thread about?</p>
    </div>
    
    <div class="form-group">
        <label>Content Type *</label>
        <div class="radio-group">
            <div class="radio-item">
                <input type="radio" id="single" name="content_type" value="single" 
                       {% if request.form.get('content_type') == 'single' %}checked{% endif %}>
                <label for="single">Single Post</label>
            </div>
            <div class="radio-item">
                <input type="radio" id="thread" name="content_type" value="thread" checked
                       {% if request.form.get('content_type', 'thread') == 'thread' %}checked{% endif %}>
                <label for="thread">Thread (Multiple Tweets)</label>
            </div>
        </div>
    </div>
    
    <div class="form-group">
        <label for="template">Template *</label>
        <select id="template" name="template" required>
            <option value="">Select a template...</option>
            <option value="ProblemSolution" {% if request.form.get('template') == 'ProblemSolution' %}selected{% endif %}>
                Problem/Solution (Build in Public)
            </option>
            <option value="ConceptualDeepDive" {% if request.form.get('template') == 'ConceptualDeepDive' %}selected{% endif %}>
                Conceptual Deep Dive
            </option>
            <option value="WorkflowShare" {% if request.form.get('template') == 'WorkflowShare' %}selected{% endif %}>
                Workflow / Tools Share
            </option>
            <option value="TechnicalBreakdown" {% if request.form.get('template') == 'TechnicalBreakdown' %}selected{% endif %}>
                Technical Breakdown
            </option>
            <option value="LearningShare" {% if request.form.get('template') == 'LearningShare' %}selected{% endif %}>
                Learning Share
            </option>
        </select>
        <p class="help-text">Choose the style and structure for your content</p>
    </div>
    
    <div class="form-group">
        <label for="context">Additional Context (Optional)</label>
        <textarea id="context" name="context" 
                  placeholder="Add any specific details, target audience, or key points you want to include...">{{ request.form.get('context', '') }}</textarea>
        <p class="help-text">Provide extra information to guide the AI generation</p>
    </div>
    
    <div class="button-group">
        <button type="submit" class="btn-primary">
            🧠 Generate Thread
        </button>
        <a href="{{ url_for('preview') }}" class="button btn-secondary">
            👁️ View Last Preview
        </a>
    </div>
</form>
{% endblock %}
"""

# Preview template
PREVIEW_TEMPLATE = """
{% extends base_template %}

{% block title %}Preview - Tweet Generator{% endblock %}

{% block content %}
{% if threads %}
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
        <div>
            <h2>Thread Preview</h2>
            {% if generation_info %}
                <p style="color: #657786; font-size: 14px;">
                    Generated: {{ generation_info.generated_at }}<br>
                    Template: {{ generation_info.template }}
                </p>
            {% endif %}
        </div>
        <div class="button-group">
            <a href="{{ url_for('generate') }}" class="button btn-secondary">
                ⬅️ Edit Inputs
            </a>
            <form method="POST" action="{{ url_for('regenerate') }}" style="display: inline;">
                <button type="submit" class="btn-primary">
                    🔁 Regenerate
                </button>
            </form>
            <button class="btn-disabled" disabled title="Coming soon">
                🚀 Post to Twitter
            </button>
        </div>
    </div>
    
    {% for thread in threads %}
        <div class="thread">
            <div class="thread-header">
                <div class="thread-topic">{{ thread.topic }}</div>
                <div class="thread-meta">
                    {{ thread.tweets|length }} tweets
                    {% if thread.diagram_count %} • {{ thread.diagram_count }} diagrams{% endif %}
                </div>
            </div>
            
            {% for tweet in thread.tweets %}
                <div class="tweet-card">
                    <div class="tweet-number">{{ loop.index }}</div>
                    <div class="tweet-content">{{ tweet.text }}</div>
                    
                    {% if tweet.image_data %}
                        <div class="diagram-container">
                            <div class="diagram-label">
                                📊 {{ tweet.image_name or 'Diagram' }}
                            </div>
                            <img class="diagram-image" 
                                 src="data:image/png;base64,{{ tweet.image_data }}" 
                                 alt="{{ tweet.image_name or 'Diagram' }}">
                        </div>
                    {% elif tweet.image_path %}
                        <div class="diagram-container">
                            <div class="diagram-label">
                                📊 Diagram: {{ tweet.image_path }}
                            </div>
                            <div style="padding: 20px; text-align: center; color: #657786;">
                                (Image not loaded)
                            </div>
                        </div>
                    {% endif %}
                    
                    <div class="tweet-meta">
                        <span>{{ tweet.text|length }} chars</span>
                        {% if tweet.image_data or tweet.image_path %}
                            <span>📸 Has media</span>
                        {% endif %}
                    </div>
                </div>
            {% endfor %}
        </div>
    {% endfor %}
    
{% else %}
    <div style="text-align: center; padding: 60px 20px;">
        <h2 style="color: #657786; margin-bottom: 20px;">No threads to preview</h2>
        <p style="color: #657786; margin-bottom: 30px;">
            Generate a new thread to see it here
        </p>
        <a href="{{ url_for('generate') }}" class="button btn-primary">
            📝 Generate Thread
        </a>
    </div>
{% endif %}
{% endblock %}
"""

@app.route('/')
def index():
    """Redirect to generate page"""
    return redirect(url_for('generate'))

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    """Generate form and handle generation"""
    if request.method == 'POST':
        # Get form data
        topic = request.form.get('topic', '').strip()
        content_type = request.form.get('content_type', 'thread')
        template = request.form.get('template', '')
        context = request.form.get('context', '').strip()
        
        # Validate inputs
        if not topic:
            flash('Please enter a topic', 'error')
            return render_template_string(GENERATE_TEMPLATE, base_template=BASE_TEMPLATE)
        
        if not template:
            flash('Please select a template', 'error')
            return render_template_string(GENERATE_TEMPLATE, base_template=BASE_TEMPLATE)
        
        # Store generation parameters
        global current_generation
        current_generation = {
            'topic': topic,
            'content_type': content_type,
            'template': template,
            'context': context,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            # Generate content
            logger.info(f"Generating thread for topic: {topic}")
            
            if UnifiedTweetGenerator and GEMINI_API_KEY:
                # Use actual generator
                generator = UnifiedTweetGenerator(
                    api_key=GEMINI_API_KEY,
                    auto_polish=True,
                    auto_diagram=True
                )
                
                if content_type == 'thread':
                    result = generator.generate_thread(topic, template, context)
                else:
                    result = generator.generate_single_tweet(topic, template, context)
                
                # Save to file
                output_file = Path("generated_threads_final.json")
                with open(output_file, 'w') as f:
                    json.dump([result] if isinstance(result, dict) else result, f, indent=2)
                
                flash(f'Successfully generated {content_type} for "{topic}"', 'success')
                
                # Run diagram automation if available
                if DiagramAutomationPipeline and Path("generated_threads_final.json").exists():
                    try:
                        pipeline = DiagramAutomationPipeline()
                        with open("generated_threads_final.json", 'r') as f:
                            thread_data = json.load(f)
                        
                        for thread in (thread_data if isinstance(thread_data, list) else [thread_data]):
                            pipeline.process_thread_output(thread)
                        
                        logger.info("Diagram automation completed")
                    except Exception as e:
                        logger.warning(f"Diagram automation failed: {e}")
                
            else:
                # Fallback: Create sample data
                logger.warning("Using fallback sample generation")
                
                sample_thread = {
                    "topic": topic,
                    "template": template,
                    "contentType": content_type,
                    "generatedTweets": [
                        f"🚀 Let's explore {topic}! This is going to be an exciting deep dive.",
                        f"First, let's understand the fundamentals of {topic}.",
                        f"Here's a visual representation:\n\n📊 [Diagram Placeholder]",
                        f"The key benefits include improved performance and better scalability.",
                        f"What's your experience with {topic}? Share your thoughts below! 💭"
                    ] if content_type == 'thread' else [
                        f"💡 Quick tip about {topic}: Always consider the context and best practices. What's your approach?"
                    ]
                }
                
                # Add context if provided
                if context:
                    sample_thread['context'] = context
                
                # Save sample
                with open("generated_threads_final.json", 'w') as f:
                    json.dump([sample_thread], f, indent=2)
                
                flash(f'Generated sample {content_type} for "{topic}" (API not configured)', 'info')
            
            return redirect(url_for('preview'))
            
        except Exception as e:
            logger.error(f"Generation error: {e}")
            logger.error(traceback.format_exc())
            flash(f'Error generating content: {str(e)}', 'error')
            return render_template_string(GENERATE_TEMPLATE, base_template=BASE_TEMPLATE)
    
    # GET request - show form
    return render_template_string(GENERATE_TEMPLATE, base_template=BASE_TEMPLATE)

@app.route('/preview')
def preview():
    """Preview generated threads with diagrams"""
    try:
        # Load generated threads
        thread_file = Path("generated_threads_final.json")
        if not thread_file.exists():
            return render_template_string(PREVIEW_TEMPLATE, 
                                        base_template=BASE_TEMPLATE,
                                        threads=None)
        
        with open(thread_file, 'r') as f:
            threads_data = json.load(f)
            if not isinstance(threads_data, list):
                threads_data = [threads_data]
        
        # Process threads with diagram binding
        processed_threads = []
        
        if TweetDiagramBinder:
            # Try to use actual binder
            try:
                binder = TweetDiagramBinder()
                
                for thread_data in threads_data:
                    # Prepare tweets with media
                    prepared_tweets = binder.prepare_thread_with_media(thread_data, dry_run=True)
                    
                    # Convert to preview format with base64 images
                    preview_tweets = []
                    for tweet in prepared_tweets:
                        tweet_obj = {
                            'text': tweet['text'],
                            'image_path': tweet.get('image_path')
                        }
                        
                        # Load and encode image if available
                        if tweet_obj['image_path'] and Path(tweet_obj['image_path']).exists():
                            try:
                                with open(tweet_obj['image_path'], 'rb') as img:
                                    tweet_obj['image_data'] = base64.b64encode(img.read()).decode('utf-8')
                                    tweet_obj['image_name'] = Path(tweet_obj['image_path']).name
                            except Exception as e:
                                logger.error(f"Failed to load image: {e}")
                        
                        preview_tweets.append(tweet_obj)
                    
                    processed_threads.append({
                        'topic': thread_data.get('topic', 'Thread'),
                        'tweets': preview_tweets,
                        'diagram_count': sum(1 for t in preview_tweets if 'image_data' in t)
                    })
                    
            except Exception as e:
                logger.warning(f"Binder failed, using simple processing: {e}")
                processed_threads = _simple_process_threads(threads_data)
        else:
            # Fallback to simple processing
            processed_threads = _simple_process_threads(threads_data)
        
        return render_template_string(PREVIEW_TEMPLATE,
                                    base_template=BASE_TEMPLATE,
                                    threads=processed_threads,
                                    generation_info=current_generation)
                                    
    except Exception as e:
        logger.error(f"Preview error: {e}")
        logger.error(traceback.format_exc())
        flash(f'Error loading preview: {str(e)}', 'error')
        return redirect(url_for('generate'))

def _simple_process_threads(threads_data):
    """Simple thread processing without full binder"""
    processed = []
    for thread in threads_data:
        tweets = thread.get('generatedTweets', thread.get('tweets', []))
        preview_tweets = []
        
        for tweet in tweets:
            if isinstance(tweet, str):
                preview_tweets.append({'text': tweet})
            else:
                preview_tweets.append(tweet)
        
        processed.append({
            'topic': thread.get('topic', 'Thread'),
            'tweets': preview_tweets,
            'diagram_count': 0
        })
    
    return processed

@app.route('/regenerate', methods=['POST'])
def regenerate():
    """Regenerate with same parameters"""
    if not current_generation.get('topic'):
        flash('No previous generation found', 'error')
        return redirect(url_for('generate'))
    
    # Create form data from stored generation
    form_data = {
        'topic': current_generation['topic'],
        'content_type': current_generation.get('content_type', 'thread'),
        'template': current_generation['template'],
        'context': current_generation.get('context', '')
    }
    
    # Resubmit to generate
    with app.test_request_context('/generate', method='POST', data=form_data):
        return generate()

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'has_api_key': bool(GEMINI_API_KEY),
        'modules': {
            'unified_tweet_generator': UnifiedTweetGenerator is not None,
            'diagram_automation': DiagramAutomationPipeline is not None,
            'tweet_diagram_binder': TweetDiagramBinder is not None
        }
    })

if __name__ == '__main__':
    # Find available port
    import socket
    for port in [5000, 5001, 5002, 5003, 8000]:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        if result != 0:  # Port is free
            break
    else:
        port = 8082
    
    print(f"\n🚀 Dynamic Tweet Generator Server")
    print(f"📍 URL: http://localhost:{port}/")
    print(f"📝 Generate: http://localhost:{port}/generate")
    print(f"👁️ Preview: http://localhost:{port}/preview")
    print(f"\n✨ Features:")
    print(f"   - Custom topic input")
    print(f"   - Multiple templates")
    print(f"   - Automatic diagram generation")
    print(f"   - Visual thread preview")
    print(f"\nPress Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)