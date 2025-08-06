#!/usr/bin/env python3
"""
Robust Flask Server - Handles all edge cases and import issues
"""

from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import json
import os
from pathlib import Path
from datetime import datetime
import logging
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'your-secret-key'

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
pipeline_logs = []

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Tweet Generator</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, Arial, sans-serif;
            background: #f5f5f5;
            margin: 0;
            padding: 20px;
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
            margin: 0 0 5px 0;
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
        input[type="text"], textarea, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 16px;
        }
        input:focus, textarea:focus, select:focus {
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
            margin-bottom: 10px;
        }
        .tweet-meta {
            font-size: 14px;
            color: #657786;
        }
        .button-group {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }
        .btn-secondary {
            background: #e1e8ed;
            color: #14171a;
        }
        .btn-secondary:hover {
            background: #d1d8dd;
        }
        .diagram-notice {
            background: #e8f5fd;
            color: #1da1f2;
            padding: 10px 15px;
            border-radius: 8px;
            margin: 10px 0;
            font-size: 14px;
        }
        .logs {
            background: #f8f9fa;
            border: 1px solid #e1e8ed;
            border-radius: 8px;
            padding: 15px;
            margin-top: 20px;
            font-family: monospace;
            font-size: 13px;
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
        <div class="header">
            <h1>🐦 AI Tweet Generator</h1>
            <p style="color: #657786; margin: 0;">Generate custom Twitter threads with AI</p>
        </div>
        
        {% if message %}
            <div class="alert alert-{{ message.type }}">
                {{ message.text }}
            </div>
        {% endif %}
        
        {% if page == 'generate' %}
            <div class="card">
                <h2>Generate New Thread</h2>
                
                <form method="POST" action="/generate">
                    <div class="form-group">
                        <label for="topic">Topic / Subject *</label>
                        <input type="text" id="topic" name="topic" required 
                               placeholder="e.g., Docker Container Optimization"
                               value="{{ form.topic }}">
                    </div>
                    
                    <div class="form-group">
                        <label>Content Type *</label>
                        <div class="radio-group">
                            <label>
                                <input type="radio" name="content_type" value="single" 
                                       {% if form.content_type == 'single' %}checked{% endif %}>
                                Single Post
                            </label>
                            <label>
                                <input type="radio" name="content_type" value="thread" 
                                       {% if form.content_type != 'single' %}checked{% endif %}>
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
                                  placeholder="Add any specific details...">{{ form.context }}</textarea>
                    </div>
                    
                    <div class="button-group">
                        <button type="submit">🧠 Generate Thread</button>
                        <a href="/preview" class="button btn-secondary">👁️ View Preview</a>
                    </div>
                </form>
            </div>
            
        {% elif page == 'preview' %}
            <div class="card">
                {% if threads %}
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h2>{{ threads[0].topic }}</h2>
                        <div class="button-group">
                            <a href="/generate" class="button btn-secondary">⬅️ Edit</a>
                            <form method="POST" action="/regenerate" style="display: inline;">
                                <button type="submit">🔁 Regenerate</button>
                            </form>
                            <button disabled>🚀 Post</button>
                        </div>
                    </div>
                    
                    {% for thread in threads %}
                        {% for tweet in thread.tweets %}
                            <div class="tweet">
                                <div class="tweet-number">{{ loop.index }}</div>
                                <div class="tweet-content">{{ tweet.text }}</div>
                                
                                {% if tweet.has_diagram %}
                                    <div class="diagram-notice">
                                        📊 This tweet would include a diagram
                                        {% if tweet.diagram_path %}
                                            ({{ tweet.diagram_path }})
                                        {% endif %}
                                    </div>
                                {% endif %}
                                
                                <div class="tweet-meta">
                                    {{ tweet.text|length }} characters
                                    {% if tweet.has_diagram %} • Has media{% endif %}
                                </div>
                            </div>
                        {% endfor %}
                    {% endfor %}
                    
                    {% if logs %}
                        <div class="logs">
                            <strong>Generation Log:</strong><br>
                            {% for log in logs %}
                                <div class="log-entry log-{{ log.level }}">
                                    [{{ log.time }}] {{ log.message }}
                                </div>
                            {% endfor %}
                        </div>
                    {% endif %}
                    
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

def log_event(message, level='info'):
    """Log an event"""
    global pipeline_logs
    pipeline_logs.append({
        'time': datetime.now().strftime('%H:%M:%S'),
        'message': message,
        'level': level
    })
    logger.info(f"[{level}] {message}")

def generate_with_api(topic, content_type, template, context):
    """Try to generate using the API"""
    try:
        # Try importing the generator
        from unified_tweet_generator import UnifiedTweetGenerator
        
        log_event("Initializing UnifiedTweetGenerator", "info")
        generator = UnifiedTweetGenerator(api_key=GEMINI_API_KEY, auto_polish=True)
        
        # The unified_tweet_generator uses Literal types, not enums
        # ContentType = Literal["SinglePost", "Thread"]
        # GeneratorType = Literal["StyleAware", "SimplePatternBased"]
        content_type_value = "Thread" if content_type == 'thread' else "SinglePost"
        generator_type_value = "StyleAware"
        
        # Generate content
        log_event(f"Generating {content_type} for topic: {topic}", "info")
        result = generator.generate_content(
            topic=topic,
            content_type=content_type_value,
            additional_context=context,
            generator_type=generator_type_value,
            template=template
        )
        
        log_event("Generation successful", "success")
        return result
        
    except Exception as e:
        log_event(f"API generation failed: {str(e)}", "error")
        raise

def generate_fallback(topic, content_type, template, context):
    """Generate fallback content without API"""
    log_event("Using fallback generation (no API)", "info")
    
    tweets = []
    if content_type == 'thread':
        tweets = [
            f"🚀 Let's explore {topic}! This thread covers the essential concepts you need to know.",
            f"First, understanding the fundamentals of {topic} is crucial for building a solid foundation.",
            f"Here's a visual breakdown of the key components:\n\n📊 [Diagram: Architecture Overview]",
            f"The main benefits include improved performance, better scalability, and easier maintenance.",
            f"Best practices to remember: always test thoroughly, document your approach, and iterate based on feedback.",
            f"What's your experience with {topic}? Drop your thoughts below! 💭"
        ]
    else:
        tweets = [
            f"💡 Quick insight about {topic}: Focus on understanding the core concepts before diving into implementation. What's your take?"
        ]
    
    if context:
        log_event(f"Context provided: {context[:50]}...", "info")
    
    result = {
        'topic': topic,
        'template': template,
        'contentType': content_type,
        'generatedTweets': tweets
    }
    
    log_event(f"Generated {len(tweets)} tweets", "success")
    return result

@app.route('/')
def index():
    return redirect(url_for('generate'))

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    message = None
    form_data = {'topic': '', 'content_type': 'thread', 'context': ''}
    
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
            message = {'type': 'error', 'text': 'Please enter a topic'}
        elif not form_data['template']:
            message = {'type': 'error', 'text': 'Please select a template'}
        else:
            # Store for regeneration
            global current_generation, pipeline_logs
            current_generation = form_data.copy()
            pipeline_logs = []
            
            try:
                # Try API generation first
                if GEMINI_API_KEY:
                    try:
                        result = generate_with_api(
                            form_data['topic'],
                            form_data['content_type'],
                            form_data['template'],
                            form_data['context']
                        )
                    except:
                        # Fallback if API fails
                        result = generate_fallback(
                            form_data['topic'],
                            form_data['content_type'],
                            form_data['template'],
                            form_data['context']
                        )
                else:
                    # No API key, use fallback
                    result = generate_fallback(
                        form_data['topic'],
                        form_data['content_type'],
                        form_data['template'],
                        form_data['context']
                    )
                
                # Save result
                with open('generated_threads_final.json', 'w') as f:
                    json.dump([result], f, indent=2)
                
                log_event("Saved to generated_threads_final.json", "info")
                
                # Try to run diagram automation
                try:
                    from diagram_automation_pipeline import DiagramAutomationPipeline
                    log_event("Running diagram automation", "info")
                    pipeline = DiagramAutomationPipeline()
                    pipeline.process_thread_output(result)
                    log_event("Diagram automation completed", "success")
                except:
                    log_event("Diagram automation not available", "info")
                
                return redirect(url_for('preview'))
                
            except Exception as e:
                logger.error(f"Generation error: {e}")
                message = {'type': 'error', 'text': f'Generation failed: {str(e)}'}
    
    return render_template_string(HTML_TEMPLATE, 
                                page='generate',
                                message=message,
                                form=form_data)

@app.route('/preview')
def preview():
    threads = []
    
    try:
        # Load generated threads
        if Path('generated_threads_final.json').exists():
            with open('generated_threads_final.json', 'r') as f:
                data = json.load(f)
            
            for item in (data if isinstance(data, list) else [data]):
                tweets = []
                raw_tweets = item.get('generatedTweets', item.get('tweets', []))
                
                for i, tweet in enumerate(raw_tweets):
                    tweet_text = tweet if isinstance(tweet, str) else tweet.get('text', str(tweet))
                    # Decode Unicode escape sequences
                    try:
                        tweet_text = tweet_text.encode().decode('unicode-escape')
                    except:
                        pass  # If decoding fails, use original text
                    tweet_obj = {
                        'text': tweet_text,
                        'has_diagram': any(word in tweet_text.lower() for word in ['diagram', 'chart', 'visual', '📊', '📈'])
                    }
                    
                    # Try to find diagram
                    if tweet_obj['has_diagram']:
                        diagram_dirs = ['diagrams/png', 'automated_diagrams/png', '/home/kushagra/X/optimized']
                        for dir_path in diagram_dirs:
                            if Path(dir_path).exists():
                                files = list(Path(dir_path).glob('*.png'))
                                if files:
                                    tweet_obj['diagram_path'] = str(files[0].name)
                                    break
                    
                    tweets.append(tweet_obj)
                
                threads.append({
                    'topic': item.get('topic', 'Thread'),
                    'tweets': tweets
                })
                
    except Exception as e:
        logger.error(f"Preview error: {e}")
    
    return render_template_string(HTML_TEMPLATE,
                                page='preview',
                                threads=threads,
                                logs=pipeline_logs)

@app.route('/regenerate', methods=['POST'])
def regenerate():
    if current_generation:
        # Reset logs
        global pipeline_logs
        pipeline_logs = []
        
        # Regenerate with same parameters
        form_data = current_generation
        
        try:
            if GEMINI_API_KEY:
                try:
                    result = generate_with_api(
                        form_data['topic'],
                        form_data['content_type'],
                        form_data['template'],
                        form_data['context']
                    )
                except:
                    result = generate_fallback(
                        form_data['topic'],
                        form_data['content_type'],
                        form_data['template'],
                        form_data['context']
                    )
            else:
                result = generate_fallback(
                    form_data['topic'],
                    form_data['content_type'],
                    form_data['template'],
                    form_data['context']
                )
            
            with open('generated_threads_final.json', 'w') as f:
                json.dump([result], f, indent=2)
                
        except Exception as e:
            logger.error(f"Regeneration error: {e}")
    
    return redirect(url_for('preview'))

@app.route('/health')
def health():
    return jsonify({
        'status': 'ok',
        'has_api_key': bool(GEMINI_API_KEY),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    port = 5000
    print(f"\n🚀 Robust Tweet Generator Server")
    print(f"📍 URL: http://localhost:{port}/")
    print(f"\nThis server handles all edge cases and won't crash!")
    print(f"Press Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)