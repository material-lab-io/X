#!/usr/bin/env python3
"""
Complete Dynamic Flask Server with All Phase 1-4 Functionalities
"""

from flask import Flask, render_template_string, request, redirect, url_for, jsonify, flash, send_file
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import logging
import base64
import subprocess
import traceback
from typing import Dict, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key-for-flash-messages'

# Load configuration
GEMINI_API_KEY = None
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
        GEMINI_API_KEY = config.get('api_keys', {}).get('gemini')
except:
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# Store current generation state
current_generation = {}

# Complete HTML template with all features
COMPLETE_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>{% if page == 'generate' %}Generate{% else %}Preview{% endif %} - Tweet Generator</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            background: #f5f5f5;
            line-height: 1.5;
        }
        
        .container {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .header {
            background: white;
            padding: 25px;
            border-radius: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
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
        
        .card {
            background: white;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin-bottom: 20px;
        }
        
        h2 {
            color: #14171a;
            margin-bottom: 20px;
            font-size: 22px;
        }
        
        /* Form Styles */
        .form-group {
            margin-bottom: 25px;
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
            padding: 12px 16px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 16px;
            font-family: inherit;
            transition: all 0.2s;
        }
        
        input:focus,
        textarea:focus,
        select:focus {
            outline: none;
            border-color: #1da1f2;
            box-shadow: 0 0 0 3px rgba(29,161,242,0.1);
        }
        
        textarea {
            min-height: 120px;
            resize: vertical;
        }
        
        .radio-group {
            display: flex;
            gap: 25px;
            margin-top: 10px;
        }
        
        .radio-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        input[type="radio"] {
            width: 18px;
            height: 18px;
            cursor: pointer;
        }
        
        /* Button Styles */
        .button-group {
            display: flex;
            gap: 12px;
            margin-top: 25px;
            flex-wrap: wrap;
        }
        
        button, .button {
            background: #1da1f2;
            color: white;
            border: none;
            padding: 12px 28px;
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
        
        button:hover, .button:hover {
            background: #1a91da;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(29,161,242,0.2);
        }
        
        .btn-secondary {
            background: #e1e8ed;
            color: #14171a;
        }
        
        .btn-secondary:hover {
            background: #d1d8dd;
        }
        
        button:disabled {
            background: #e1e8ed;
            color: #657786;
            cursor: not-allowed;
            opacity: 0.6;
            transform: none;
            box-shadow: none;
        }
        
        /* Alert Styles */
        .alert {
            padding: 16px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
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
        
        /* Tweet Preview Styles */
        .thread-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 25px;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .thread-info h2 {
            margin-bottom: 5px;
        }
        
        .thread-meta {
            font-size: 14px;
            color: #657786;
        }
        
        .tweet {
            background: #f8f9fa;
            border: 1px solid #e1e8ed;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            position: relative;
            transition: all 0.2s;
        }
        
        .tweet:hover {
            border-color: #1da1f2;
            box-shadow: 0 4px 12px rgba(29,161,242,0.08);
        }
        
        .tweet-number {
            position: absolute;
            left: -18px;
            top: 20px;
            background: #1da1f2;
            color: white;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 16px;
            box-shadow: 0 2px 8px rgba(29,161,242,0.3);
        }
        
        .tweet-content {
            white-space: pre-wrap;
            word-wrap: break-word;
            font-size: 16px;
            line-height: 1.5;
            margin-bottom: 15px;
        }
        
        .tweet-meta {
            display: flex;
            gap: 20px;
            font-size: 14px;
            color: #657786;
            align-items: center;
        }
        
        /* Diagram Styles */
        .diagram-container {
            margin: 15px 0;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #e1e8ed;
            background: white;
        }
        
        .diagram-label {
            padding: 12px 16px;
            background: #e8f5fd;
            color: #1da1f2;
            font-size: 14px;
            font-weight: 600;
            border-bottom: 1px solid #e1e8ed;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .diagram-image {
            display: block;
            width: 100%;
            height: auto;
            max-height: 400px;
            object-fit: contain;
            background: #f8f9fa;
        }
        
        .diagram-placeholder {
            padding: 40px;
            text-align: center;
            color: #657786;
            background: #f8f9fa;
        }
        
        /* Status and Logs */
        .status-section {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 12px;
            border: 1px solid #e1e8ed;
        }
        
        .status-header {
            font-weight: 600;
            margin-bottom: 10px;
            color: #14171a;
        }
        
        .log-entry {
            padding: 8px 12px;
            margin: 4px 0;
            border-radius: 6px;
            font-family: monospace;
            font-size: 13px;
        }
        
        .log-info { background: #e3f2fd; color: #1565c0; }
        .log-success { background: #e8f5e9; color: #2e7d32; }
        .log-warning { background: #fff3e0; color: #ef6c00; }
        .log-error { background: #ffebee; color: #c62828; }
        
        /* Loading State */
        .loading {
            text-align: center;
            padding: 60px;
            color: #657786;
        }
        
        .spinner {
            display: inline-block;
            width: 40px;
            height: 40px;
            border: 4px solid #e1e8ed;
            border-top-color: #1da1f2;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 15px;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .help-text {
            font-size: 14px;
            color: #657786;
            margin-top: 6px;
        }
        
        /* Responsive */
        @media (max-width: 600px) {
            .container { padding: 10px; }
            .card { padding: 20px; }
            .button-group { flex-direction: column; }
            button, .button { width: 100%; justify-content: center; }
            .thread-header { flex-direction: column; align-items: flex-start; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐦 AI Tweet Generator</h1>
            <p class="subtitle">
                {% if page == 'generate' %}
                    Generate custom Twitter threads with AI and automatic diagrams
                {% else %}
                    Preview your generated thread with integrated diagrams
                {% endif %}
            </p>
        </div>
        
        {% for message in messages %}
            <div class="alert alert-{{ message.type }}">
                {{ message.text }}
            </div>
        {% endfor %}
        
        {% if page == 'generate' %}
            <div class="card">
                <h2>📝 Generate New Thread</h2>
                
                <form method="POST" action="/generate" id="generateForm">
                    <div class="form-group">
                        <label for="topic">Topic / Subject *</label>
                        <input type="text" id="topic" name="topic" required 
                               placeholder="e.g., Kubernetes Pod Networking, Redis Caching Strategies"
                               value="{{ form_data.topic or '' }}">
                        <p class="help-text">What technical topic do you want to create a thread about?</p>
                    </div>
                    
                    <div class="form-group">
                        <label>Content Type *</label>
                        <div class="radio-group">
                            <div class="radio-item">
                                <input type="radio" id="single" name="content_type" value="single" 
                                       {% if form_data.content_type == 'single' %}checked{% endif %}>
                                <label for="single">Single Post</label>
                            </div>
                            <div class="radio-item">
                                <input type="radio" id="thread" name="content_type" value="thread" 
                                       {% if form_data.content_type != 'single' %}checked{% endif %}>
                                <label for="thread">Thread (Multiple Tweets)</label>
                            </div>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="template">Template Style *</label>
                        <select id="template" name="template" required>
                            <option value="">Select a template...</option>
                            <option value="ProblemSolution" {% if form_data.template == 'ProblemSolution' %}selected{% endif %}>
                                🔧 Problem/Solution (Build in Public)
                            </option>
                            <option value="ConceptualDeepDive" {% if form_data.template == 'ConceptualDeepDive' %}selected{% endif %}>
                                🌊 Conceptual Deep Dive
                            </option>
                            <option value="WorkflowShare" {% if form_data.template == 'WorkflowShare' %}selected{% endif %}>
                                ⚙️ Workflow / Tools Share
                            </option>
                            <option value="TechnicalBreakdown" {% if form_data.template == 'TechnicalBreakdown' %}selected{% endif %}>
                                🔍 Technical Breakdown
                            </option>
                            <option value="LearningShare" {% if form_data.template == 'LearningShare' %}selected{% endif %}>
                                📚 Learning Share
                            </option>
                        </select>
                        <p class="help-text">Choose the style and structure for your content</p>
                    </div>
                    
                    <div class="form-group">
                        <label for="context">Additional Context (Optional)</label>
                        <textarea id="context" name="context" 
                                  placeholder="Add specific details, target audience, key points to cover, or any special requirements...">{{ form_data.context or '' }}</textarea>
                        <p class="help-text">Provide extra information to guide the AI generation</p>
                    </div>
                    
                    <div class="button-group">
                        <button type="submit" id="generateBtn">
                            🧠 Generate Thread
                        </button>
                        <a href="/preview" class="button btn-secondary">
                            👁️ View Last Preview
                        </a>
                    </div>
                </form>
            </div>
            
        {% elif page == 'preview' %}
            <div class="card">
                {% if threads %}
                    <div class="thread-header">
                        <div class="thread-info">
                            <h2>{{ threads[0].topic }}</h2>
                            <div class="thread-meta">
                                {{ threads[0].tweet_count }} tweets
                                {% if threads[0].diagram_count %} • {{ threads[0].diagram_count }} diagrams{% endif %}
                                {% if generation_info.generated_at %} • Generated {{ generation_info.generated_at }}{% endif %}
                            </div>
                        </div>
                        <div class="button-group">
                            <a href="/generate" class="button btn-secondary">
                                ⬅️ Edit Inputs
                            </a>
                            <button onclick="regenerate()">
                                🔁 Regenerate
                            </button>
                            <button disabled title="Coming soon">
                                🚀 Post to Twitter
                            </button>
                        </div>
                    </div>
                    
                    {% for thread in threads %}
                        {% for tweet in thread.tweets %}
                            <div class="tweet">
                                <div class="tweet-number">{{ loop.index }}</div>
                                <div class="tweet-content">{{ tweet.text }}</div>
                                
                                {% if tweet.has_diagram %}
                                    <div class="diagram-container">
                                        <div class="diagram-label">
                                            📊 {{ tweet.diagram_name or 'Diagram' }}
                                            {% if tweet.diagram_matched %}
                                                <span style="font-size: 12px; color: #28a745;">✓ Matched</span>
                                            {% endif %}
                                        </div>
                                        {% if tweet.diagram_image %}
                                            <img class="diagram-image" 
                                                 src="data:image/png;base64,{{ tweet.diagram_image }}" 
                                                 alt="{{ tweet.diagram_name or 'Diagram' }}">
                                        {% else %}
                                            <div class="diagram-placeholder">
                                                {% if tweet.diagram_path %}
                                                    <p>Diagram file: {{ tweet.diagram_path }}</p>
                                                    <p style="font-size: 12px; margin-top: 10px;">
                                                        (Image loading failed)
                                                    </p>
                                                {% else %}
                                                    <p>Diagram will be generated here</p>
                                                {% endif %}
                                            </div>
                                        {% endif %}
                                    </div>
                                {% endif %}
                                
                                <div class="tweet-meta">
                                    <span>{{ tweet.text|length }} chars</span>
                                    {% if tweet.has_diagram %}
                                        <span>📸 Has media</span>
                                    {% endif %}
                                    {% if tweet.keywords %}
                                        <span>🏷️ {{ tweet.keywords|join(', ') }}</span>
                                    {% endif %}
                                </div>
                            </div>
                        {% endfor %}
                    {% endfor %}
                    
                    {% if pipeline_logs %}
                        <div class="status-section">
                            <div class="status-header">📋 Pipeline Execution Log</div>
                            {% for log in pipeline_logs %}
                                <div class="log-entry log-{{ log.level }}">
                                    [{{ log.time }}] {{ log.message }}
                                </div>
                            {% endfor %}
                        </div>
                    {% endif %}
                    
                {% else %}
                    <div style="text-align: center; padding: 60px 20px;">
                        <h2 style="color: #657786; margin-bottom: 20px;">No threads to preview</h2>
                        <p style="color: #657786; margin-bottom: 30px;">
                            Generate a new thread to see it here with automatic diagram integration
                        </p>
                        <a href="/generate" class="button">
                            📝 Generate Your First Thread
                        </a>
                    </div>
                {% endif %}
            </div>
        {% endif %}
    </div>
    
    <script>
        function regenerate() {
            if (confirm('Regenerate the thread with the same parameters?')) {
                fetch('/regenerate', {method: 'POST'})
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            window.location.reload();
                        } else {
                            alert('Regeneration failed: ' + (data.error || 'Unknown error'));
                        }
                    });
            }
        }
        
        // Show loading state on form submit
        const form = document.getElementById('generateForm');
        if (form) {
            form.addEventListener('submit', function() {
                const btn = document.getElementById('generateBtn');
                btn.innerHTML = '⏳ Generating...';
                btn.disabled = true;
            });
        }
    </script>
</body>
</html>
"""

def safe_import(module_name, class_name=None):
    """Safely import a module and optionally get a class from it"""
    try:
        module = __import__(module_name)
        if class_name:
            return getattr(module, class_name)
        return module
    except ImportError as e:
        logger.warning(f"Could not import {module_name}: {e}")
        return None

# Try to import Phase 1-4 modules
UnifiedTweetGenerator = safe_import('unified_tweet_generator', 'UnifiedTweetGenerator')
DiagramAutomationPipeline = safe_import('diagram_automation_pipeline', 'DiagramAutomationPipeline')
TweetDiagramBinder = safe_import('tweet_diagram_binder', 'TweetDiagramBinder')

# Track pipeline execution logs
pipeline_logs = []

def log_pipeline(message, level='info'):
    """Log pipeline execution steps"""
    pipeline_logs.append({
        'time': datetime.now().strftime('%H:%M:%S'),
        'message': message,
        'level': level
    })
    logger.log(getattr(logging, level.upper(), logging.INFO), message)

@app.route('/')
def index():
    return redirect(url_for('generate'))

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    messages = []
    form_data = {}
    
    if request.method == 'POST':
        # Get form data
        form_data = {
            'topic': request.form.get('topic', '').strip(),
            'content_type': request.form.get('content_type', 'thread'),
            'template': request.form.get('template', ''),
            'context': request.form.get('context', '').strip()
        }
        
        # Validate
        if not form_data['topic']:
            messages.append({'type': 'error', 'text': '❌ Please enter a topic'})
        elif not form_data['template']:
            messages.append({'type': 'error', 'text': '❌ Please select a template'})
        else:
            # Store for regeneration
            global current_generation
            current_generation = form_data.copy()
            current_generation['generated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Clear previous logs
            global pipeline_logs
            pipeline_logs = []
            
            try:
                log_pipeline("Starting content generation pipeline", "info")
                
                # Phase 1: Generate content
                if UnifiedTweetGenerator and GEMINI_API_KEY:
                    log_pipeline("Using UnifiedTweetGenerator with Gemini API", "info")
                    
                    generator = UnifiedTweetGenerator(
                        api_key=GEMINI_API_KEY,
                        auto_polish=True,
                        auto_diagram=True
                    )
                    
                    # Use the correct method: generate_content
                    from unified_tweet_generator import ContentType, GeneratorType
                    
                    content_type = ContentType.THREAD if form_data['content_type'] == 'thread' else ContentType.SINGLE
                    
                    result = generator.generate_content(
                        topic=form_data['topic'],
                        content_type=content_type,
                        additional_context=form_data['context'],
                        generator_type=GeneratorType.STYLE_AWARE,
                        template=form_data['template']
                    )
                    
                    log_pipeline(f"Generated {form_data['content_type']} successfully", "success")
                else:
                    # Fallback generation
                    log_pipeline("Using fallback generation (no API key)", "warning")
                    
                    tweets = []
                    if form_data['content_type'] == 'thread':
                        tweets = [
                            f"🚀 Let's explore {form_data['topic']}! This thread will dive deep into the key concepts.",
                            f"Understanding {form_data['topic']} starts with grasping the fundamentals.",
                            f"Here's a visual representation of the architecture:\n\n📊 [Architecture Diagram]",
                            f"The main benefits include improved performance, scalability, and maintainability.",
                            f"Best practices to remember: always test thoroughly and document your approach.",
                            f"What's your experience with {form_data['topic']}? Share your insights below! 💭"
                        ]
                    else:
                        tweets = [f"💡 Quick insight about {form_data['topic']}: Focus on understanding the core concepts before diving into implementation details."]
                    
                    result = {
                        'topic': form_data['topic'],
                        'template': form_data['template'],
                        'contentType': form_data['content_type'],
                        'generatedTweets': tweets
                    }
                
                # Save generated content
                output_file = Path('generated_threads_final.json')
                with open(output_file, 'w') as f:
                    json.dump([result], f, indent=2)
                
                log_pipeline(f"Saved to {output_file}", "info")
                
                # Phase 2: Run diagram automation if available
                if DiagramAutomationPipeline and result.get('diagram'):
                    try:
                        log_pipeline("Running diagram automation pipeline", "info")
                        pipeline = DiagramAutomationPipeline()
                        pipeline_result = pipeline.process_thread_output(result)
                        
                        if pipeline_result.get('diagrams_extracted'):
                            log_pipeline(f"Extracted {pipeline_result['diagrams_extracted']} diagrams", "success")
                        if pipeline_result.get('diagrams_rendered'):
                            log_pipeline(f"Rendered {pipeline_result['diagrams_rendered']} diagrams", "success")
                    except Exception as e:
                        log_pipeline(f"Diagram automation failed: {str(e)}", "warning")
                
                messages.append({'type': 'success', 'text': f'✅ Successfully generated {form_data["content_type"]} for "{form_data["topic"]}"'})
                return redirect(url_for('preview'))
                
            except Exception as e:
                logger.error(f"Generation error: {e}")
                logger.error(traceback.format_exc())
                messages.append({'type': 'error', 'text': f'❌ Generation failed: {str(e)}'})
    
    return render_template_string(COMPLETE_TEMPLATE, 
                                page='generate',
                                messages=messages,
                                form_data=form_data)

@app.route('/preview')
def preview():
    messages = []
    threads = []
    
    try:
        # Load generated threads
        thread_file = Path('generated_threads_final.json')
        if not thread_file.exists():
            return render_template_string(COMPLETE_TEMPLATE,
                                        page='preview',
                                        threads=None,
                                        messages=messages,
                                        generation_info=current_generation,
                                        pipeline_logs=pipeline_logs)
        
        with open(thread_file, 'r') as f:
            thread_data = json.load(f)
            if not isinstance(thread_data, list):
                thread_data = [thread_data]
        
        # Phase 3: Process with diagram binder
        for thread in thread_data:
            processed_tweets = []
            
            # Get raw tweets
            raw_tweets = thread.get('generatedTweets', thread.get('tweets', []))
            
            # Try to use TweetDiagramBinder
            if TweetDiagramBinder:
                try:
                    log_pipeline("Using TweetDiagramBinder for diagram matching", "info")
                    binder = TweetDiagramBinder()
                    
                    # Get prepared tweets with media
                    prepared_tweets = binder.prepare_thread_with_media(thread, dry_run=True)
                    
                    for i, tweet in enumerate(prepared_tweets):
                        tweet_obj = {
                            'text': tweet['text'],
                            'has_diagram': False,
                            'keywords': []
                        }
                        
                        # Check for diagram
                        if tweet.get('image_path'):
                            tweet_obj['has_diagram'] = True
                            tweet_obj['diagram_path'] = tweet['image_path']
                            tweet_obj['diagram_name'] = Path(tweet['image_path']).name
                            tweet_obj['diagram_matched'] = True
                            
                            # Try to load and encode image
                            try:
                                with open(tweet['image_path'], 'rb') as img:
                                    tweet_obj['diagram_image'] = base64.b64encode(img.read()).decode('utf-8')
                                log_pipeline(f"Loaded diagram: {tweet_obj['diagram_name']}", "success")
                            except Exception as e:
                                log_pipeline(f"Failed to load diagram: {e}", "warning")
                        
                        # Extract keywords for display
                        words = tweet_obj['text'].lower().split()
                        tech_keywords = ['docker', 'kubernetes', 'redis', 'python', 'api', 'database', 
                                       'cache', 'microservice', 'container', 'deployment']
                        tweet_obj['keywords'] = [w for w in tech_keywords if w in words][:3]
                        
                        processed_tweets.append(tweet_obj)
                        
                except Exception as e:
                    log_pipeline(f"Binder failed: {e}, using simple processing", "warning")
                    processed_tweets = _simple_process_tweets(raw_tweets)
            else:
                # Simple processing
                processed_tweets = _simple_process_tweets(raw_tweets)
            
            # Add thread to results
            threads.append({
                'topic': thread.get('topic', 'Generated Thread'),
                'tweets': processed_tweets,
                'tweet_count': len(processed_tweets),
                'diagram_count': sum(1 for t in processed_tweets if t.get('has_diagram'))
            })
        
        log_pipeline("Preview ready", "success")
        
    except Exception as e:
        logger.error(f"Preview error: {e}")
        logger.error(traceback.format_exc())
        messages.append({'type': 'error', 'text': f'❌ Error loading preview: {str(e)}'})
    
    return render_template_string(COMPLETE_TEMPLATE,
                                page='preview',
                                threads=threads,
                                messages=messages,
                                generation_info=current_generation,
                                pipeline_logs=pipeline_logs)

def _simple_process_tweets(raw_tweets):
    """Simple tweet processing without binder"""
    processed = []
    for tweet in raw_tweets:
        tweet_text = tweet if isinstance(tweet, str) else tweet.get('text', str(tweet))
        tweet_obj = {
            'text': tweet_text,
            'has_diagram': '[Diagram' in tweet_text or '📊' in tweet_text,
            'keywords': []
        }
        processed.append(tweet_obj)
    return processed

@app.route('/regenerate', methods=['POST'])
def regenerate():
    if not current_generation.get('topic'):
        return jsonify({'success': False, 'error': 'No previous generation found'})
    
    # Clear logs for new generation
    global pipeline_logs
    pipeline_logs = []
    
    # Simulate form submission with stored data
    with app.test_request_context('/generate', method='POST', data=current_generation):
        generate()
    
    return jsonify({'success': True})

@app.route('/api/status')
def api_status():
    """API endpoint for checking system status"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'has_api_key': bool(GEMINI_API_KEY),
        'modules': {
            'unified_tweet_generator': UnifiedTweetGenerator is not None,
            'diagram_automation': DiagramAutomationPipeline is not None,
            'tweet_diagram_binder': TweetDiagramBinder is not None
        },
        'current_generation': current_generation
    })

if __name__ == '__main__':
    port = 5000
    
    print(f"\n🚀 Complete Dynamic Tweet Generator")
    print(f"📍 URLs:")
    print(f"   Generate: http://localhost:{port}/generate")
    print(f"   Preview: http://localhost:{port}/preview")
    print(f"   Status: http://localhost:{port}/api/status")
    print(f"\n✨ All Phase 1-4 Features Included:")
    print(f"   ✓ Custom topic generation")
    print(f"   ✓ Multiple templates")
    print(f"   ✓ Diagram automation")
    print(f"   ✓ Tweet-diagram binding")
    print(f"   ✓ Visual preview")
    print(f"   ✓ Pipeline logging")
    print(f"\nPress Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)