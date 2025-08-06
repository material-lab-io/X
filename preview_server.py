#!/usr/bin/env python3
"""
Flask Preview Server for Twitter/X Content Generator
Integrates Phase 1-4 modules for visual preview without posting
"""

from flask import Flask, render_template_string, jsonify, request, send_file
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import logging
import base64
from typing import Dict, List, Optional
import traceback

# Import Phase 1-4 modules
from unified_tweet_generator import UnifiedTweetGenerator
from diagram_automation_pipeline import DiagramAutomationPipeline
from tweet_diagram_binder import TweetDiagramBinder
from posting_summary import PostingSummary

# Twitter publisher is optional for preview
try:
    from twitter_publisher import TwitterPublisher
except ImportError:
    TwitterPublisher = None
    print("⚠️  Twitter publisher not available (tweepy not installed) - preview mode only")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Initialize components
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
        GEMINI_API_KEY = config.get('api_keys', {}).get('gemini')
except:
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# Global state for preview
preview_state = {
    'threads': [],
    'diagrams': {},
    'logs': [],
    'last_run': None
}

# HTML Template for preview
PREVIEW_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tweet Thread Preview - Phase 4</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background-color: #f7f9fa;
            color: #14171a;
            line-height: 1.5;
        }
        
        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            text-align: center;
            margin-bottom: 30px;
            padding: 20px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }
        
        h1 {
            color: #1da1f2;
            font-size: 24px;
            margin-bottom: 10px;
        }
        
        .status {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 500;
            background: #e8f5fd;
            color: #1da1f2;
        }
        
        .controls {
            display: flex;
            gap: 10px;
            justify-content: center;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        
        button {
            padding: 10px 20px;
            border: none;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 5px;
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
        
        .thread-container {
            margin-top: 30px;
        }
        
        .thread-header {
            background: white;
            padding: 20px;
            border-radius: 16px 16px 0 0;
            border-bottom: 1px solid #e1e8ed;
        }
        
        .thread-topic {
            font-size: 18px;
            font-weight: 700;
            color: #14171a;
        }
        
        .thread-meta {
            margin-top: 5px;
            font-size: 14px;
            color: #657786;
        }
        
        .tweet {
            background: white;
            padding: 20px;
            border-left: 1px solid #e1e8ed;
            border-right: 1px solid #e1e8ed;
            position: relative;
        }
        
        .tweet:last-child {
            border-bottom: 1px solid #e1e8ed;
            border-radius: 0 0 16px 16px;
        }
        
        .tweet::before {
            content: '';
            position: absolute;
            left: 30px;
            top: -1px;
            bottom: -1px;
            width: 2px;
            background: #cfd9de;
        }
        
        .tweet:last-child::before {
            bottom: 50%;
        }
        
        .tweet-number {
            position: absolute;
            left: 20px;
            top: 20px;
            width: 20px;
            height: 20px;
            background: #1da1f2;
            color: white;
            border-radius: 50%;
            font-size: 10px;
            font-weight: bold;
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 1;
        }
        
        .tweet-content {
            margin-left: 40px;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-size: 15px;
            line-height: 1.5;
        }
        
        .tweet-meta {
            margin-left: 40px;
            margin-top: 10px;
            font-size: 13px;
            color: #657786;
            display: flex;
            gap: 15px;
        }
        
        .diagram-container {
            margin: 15px 0 15px 40px;
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #e1e8ed;
            background: #f7f9fa;
        }
        
        .diagram-container img {
            width: 100%;
            height: auto;
            display: block;
        }
        
        .diagram-label {
            padding: 8px 12px;
            background: #e8f5fd;
            font-size: 12px;
            color: #1da1f2;
            font-weight: 500;
        }
        
        .logs-section {
            margin-top: 30px;
            background: white;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.12);
        }
        
        .logs-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .logs-title {
            font-size: 16px;
            font-weight: 600;
        }
        
        .log-entry {
            padding: 8px 12px;
            margin-bottom: 5px;
            border-radius: 6px;
            font-size: 13px;
            font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
        }
        
        .log-info {
            background: #f0f9ff;
            color: #0369a1;
        }
        
        .log-success {
            background: #f0fdf4;
            color: #15803d;
        }
        
        .log-warning {
            background: #fefce8;
            color: #a16207;
        }
        
        .log-error {
            background: #fef2f2;
            color: #b91c1c;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #657786;
        }
        
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #e1e8ed;
            border-top-color: #1da1f2;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .error-message {
            background: #fef2f2;
            color: #b91c1c;
            padding: 15px;
            border-radius: 8px;
            margin: 20px 0;
            font-size: 14px;
        }
        
        @media (max-width: 600px) {
            .container {
                padding: 10px;
            }
            
            .controls {
                flex-direction: column;
            }
            
            button {
                width: 100%;
                justify-content: center;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🐦 Tweet Thread Preview</h1>
            <p style="color: #657786; margin-top: 5px;">Phase 4: Complete Pipeline Dry Run</p>
            <div class="status" id="status">Ready</div>
        </header>
        
        <div class="controls">
            <button class="btn-primary" onclick="runPreview()">
                🔁 Run Preview
            </button>
            <button class="btn-secondary" onclick="regenerateThreads()">
                📝 Regenerate Threads
            </button>
            <button class="btn-disabled" disabled title="Coming soon">
                🚀 Post to Twitter
            </button>
        </div>
        
        <div id="content">
            <!-- Dynamic content will be loaded here -->
        </div>
    </div>
    
    <script>
        let isLoading = false;
        
        async function runPreview() {
            if (isLoading) return;
            isLoading = true;
            
            const status = document.getElementById('status');
            const content = document.getElementById('content');
            
            status.textContent = 'Running...';
            status.style.background = '#fff3cd';
            status.style.color = '#856404';
            
            content.innerHTML = '<div class="loading"><div class="spinner"></div><p>Running pipeline...</p></div>';
            
            try {
                const response = await fetch('/api/preview/run', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                
                const data = await response.json();
                
                if (data.success) {
                    status.textContent = 'Success';
                    status.style.background = '#d1ecf1';
                    status.style.color = '#0c5460';
                    displayPreview(data);
                } else {
                    throw new Error(data.error || 'Unknown error');
                }
            } catch (error) {
                status.textContent = 'Error';
                status.style.background = '#f8d7da';
                status.style.color = '#721c24';
                content.innerHTML = `<div class="error-message">❌ ${error.message}</div>`;
            } finally {
                isLoading = false;
            }
        }
        
        async function regenerateThreads() {
            if (isLoading) return;
            isLoading = true;
            
            const status = document.getElementById('status');
            status.textContent = 'Generating...';
            
            try {
                const response = await fetch('/api/preview/regenerate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'}
                });
                
                const data = await response.json();
                
                if (data.success) {
                    await runPreview();
                } else {
                    throw new Error(data.error || 'Failed to regenerate');
                }
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                isLoading = false;
            }
        }
        
        function displayPreview(data) {
            const content = document.getElementById('content');
            let html = '';
            
            // Display threads
            if (data.threads && data.threads.length > 0) {
                data.threads.forEach((thread, threadIdx) => {
                    html += `
                        <div class="thread-container">
                            <div class="thread-header">
                                <div class="thread-topic">${thread.topic}</div>
                                <div class="thread-meta">
                                    ${thread.tweets.length} tweets • 
                                    ${thread.diagrams_count || 0} diagrams
                                </div>
                            </div>
                    `;
                    
                    thread.tweets.forEach((tweet, idx) => {
                        html += `
                            <div class="tweet">
                                <div class="tweet-number">${idx + 1}</div>
                                <div class="tweet-content">${escapeHtml(tweet.text)}</div>
                        `;
                        
                        if (tweet.image_path && tweet.image_data) {
                            html += `
                                <div class="diagram-container">
                                    <div class="diagram-label">📊 ${tweet.image_name || 'Diagram'}</div>
                                    <img src="data:image/png;base64,${tweet.image_data}" 
                                         alt="Diagram for tweet ${idx + 1}">
                                </div>
                            `;
                        }
                        
                        html += `
                                <div class="tweet-meta">
                                    <span>${tweet.text.length} chars</span>
                                    ${tweet.image_path ? '<span>📸 Has media</span>' : ''}
                                </div>
                            </div>
                        `;
                    });
                    
                    html += '</div>';
                });
            } else {
                html += '<div class="error-message">No threads to display</div>';
            }
            
            // Display logs
            if (data.logs && data.logs.length > 0) {
                html += `
                    <div class="logs-section">
                        <div class="logs-header">
                            <div class="logs-title">📋 Pipeline Logs</div>
                            <span style="font-size: 12px; color: #657786;">${data.logs.length} entries</span>
                        </div>
                `;
                
                data.logs.forEach(log => {
                    html += `<div class="log-entry log-${log.level}">${escapeHtml(log.message)}</div>`;
                });
                
                html += '</div>';
            }
            
            content.innerHTML = html;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        // Load initial state on page load
        window.addEventListener('load', () => {
            runPreview();
        });
    </script>
</body>
</html>
"""


def log_message(message: str, level: str = "info"):
    """Add a log message to the preview state"""
    preview_state['logs'].append({
        'timestamp': datetime.now().isoformat(),
        'level': level,
        'message': message
    })
    logger.log(getattr(logging, level.upper(), logging.INFO), message)


def load_or_generate_threads() -> List[Dict]:
    """Load existing threads or generate new ones"""
    log_message("Loading thread data...")
    
    # First try to load existing generated_threads_final.json
    thread_file = Path("generated_threads_final.json")
    if thread_file.exists():
        try:
            with open(thread_file, 'r') as f:
                threads = json.load(f)
                log_message(f"Loaded {len(threads)} threads from generated_threads_final.json", "success")
                return threads if isinstance(threads, list) else [threads]
        except Exception as e:
            log_message(f"Error loading threads: {str(e)}", "error")
    
    # If not found, try sample threads
    sample_files = ["sample_thread_docker.json", "sample_thread_microservices.json"]
    threads = []
    
    for sample_file in sample_files:
        if Path(sample_file).exists():
            try:
                with open(sample_file, 'r') as f:
                    thread = json.load(f)
                    threads.append(thread)
                    log_message(f"Loaded sample thread: {thread.get('topic', 'Unknown')}", "info")
            except Exception as e:
                log_message(f"Error loading {sample_file}: {str(e)}", "warning")
    
    if not threads:
        log_message("No threads found, creating default thread", "warning")
        # Create a default thread
        threads = [{
            "topic": "Docker Best Practices",
            "generatedTweets": [
                "🐳 Let's talk about Docker best practices that will save you hours of debugging!",
                "1️⃣ Always use specific image tags, never 'latest'. Your future self will thank you.",
                "2️⃣ Multi-stage builds are your friend. Here's why:\n\n📊 [Build Process Diagram]",
                "3️⃣ Keep your images small. Alpine Linux is great, but watch out for missing libraries!",
                "What's your favorite Docker optimization tip? Share below! 👇"
            ]
        }]
    
    return threads


def process_thread_with_diagrams(thread_data: Dict, binder: TweetDiagramBinder) -> Dict:
    """Process a single thread and bind diagrams"""
    topic = thread_data.get('topic', 'Unknown')
    log_message(f"Processing thread: {topic}")
    
    # Prepare tweets with diagram binding
    prepared_tweets = binder.prepare_thread_with_media(thread_data, dry_run=True)
    
    # Convert to preview format
    preview_tweets = []
    for tweet in prepared_tweets:
        tweet_data = {
            'text': tweet['text'],
            'image_path': tweet.get('image_path')
        }
        
        # If there's an image, try to load it
        if tweet_data['image_path'] and Path(tweet_data['image_path']).exists():
            try:
                with open(tweet_data['image_path'], 'rb') as img_file:
                    tweet_data['image_data'] = base64.b64encode(img_file.read()).decode('utf-8')
                    tweet_data['image_name'] = Path(tweet_data['image_path']).name
                    log_message(f"Loaded diagram: {tweet_data['image_name']}", "success")
            except Exception as e:
                log_message(f"Failed to load image: {str(e)}", "error")
        
        preview_tweets.append(tweet_data)
    
    return {
        'topic': topic,
        'tweets': preview_tweets,
        'diagrams_count': sum(1 for t in preview_tweets if t.get('image_data'))
    }


@app.route('/')
def index():
    """Redirect to preview page"""
    return '<script>window.location.href = "/preview";</script>'


@app.route('/preview')
def preview():
    """Main preview page"""
    return render_template_string(PREVIEW_TEMPLATE)


@app.route('/api/preview/run', methods=['POST'])
def run_preview():
    """Run the complete Phase 1-4 pipeline in dry-run mode"""
    global preview_state
    
    # Clear previous logs
    preview_state['logs'] = []
    preview_state['threads'] = []
    
    try:
        # Step 1: Load or generate threads
        log_message("=== Phase 1-4 Pipeline Starting ===", "info")
        threads = load_or_generate_threads()
        
        # Step 2: Initialize diagram binder
        log_message("Initializing diagram binder...", "info")
        binder = TweetDiagramBinder(diagram_dir="/home/kushagra/X/optimized")
        
        # Check for automated_diagrams as fallback
        if len(binder.available_diagrams) == 0:
            alt_dir = Path("automated_diagrams/png")
            if alt_dir.exists():
                log_message(f"No diagrams in optimized/, trying {alt_dir}", "warning")
                binder = TweetDiagramBinder(diagram_dir=str(alt_dir))
        
        log_message(f"Found {len(binder.available_diagrams)} diagrams", "info")
        
        # Step 3: Process each thread
        processed_threads = []
        for thread in threads:
            try:
                processed = process_thread_with_diagrams(thread, binder)
                processed_threads.append(processed)
                log_message(f"✓ Processed: {processed['topic']}", "success")
            except Exception as e:
                log_message(f"Failed to process thread: {str(e)}", "error")
        
        # Update state
        preview_state['threads'] = processed_threads
        preview_state['last_run'] = datetime.now().isoformat()
        
        log_message(f"=== Pipeline Complete: {len(processed_threads)} threads ===", "success")
        
        return jsonify({
            'success': True,
            'threads': processed_threads,
            'logs': preview_state['logs'],
            'timestamp': preview_state['last_run']
        })
        
    except Exception as e:
        log_message(f"Pipeline error: {str(e)}", "error")
        log_message(traceback.format_exc(), "error")
        return jsonify({
            'success': False,
            'error': str(e),
            'logs': preview_state['logs']
        }), 500


@app.route('/api/preview/regenerate', methods=['POST'])
def regenerate_threads():
    """Regenerate threads using the unified generator"""
    try:
        if not GEMINI_API_KEY:
            return jsonify({
                'success': False,
                'error': 'Gemini API key not configured'
            }), 400
        
        log_message("Regenerating threads with unified generator...", "info")
        
        # Initialize generator
        generator = UnifiedTweetGenerator(GEMINI_API_KEY, auto_polish=True, auto_diagram=True)
        
        # Generate sample threads
        topics = [
            ("Docker Container Optimization", "TechnicalThread"),
            ("Microservices Best Practices", "ConceptualDeepDive")
        ]
        
        threads = []
        for topic, template in topics:
            try:
                result = generator.generate_thread(topic, template)
                threads.append(result)
                log_message(f"Generated thread: {topic}", "success")
            except Exception as e:
                log_message(f"Failed to generate {topic}: {str(e)}", "error")
        
        # Save to generated_threads_final.json
        with open("generated_threads_final.json", "w") as f:
            json.dump(threads, f, indent=2)
        
        return jsonify({
            'success': True,
            'message': f'Generated {len(threads)} threads'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/preview/status')
def get_status():
    """Get current preview status"""
    return jsonify({
        'has_threads': len(preview_state['threads']) > 0,
        'thread_count': len(preview_state['threads']),
        'last_run': preview_state['last_run'],
        'log_count': len(preview_state['logs'])
    })


if __name__ == '__main__':
    # Find an available port
    import socket
    def find_free_port():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    
    # Try ports in order: 5002, 5003, 5004, or find a free one
    for port in [5002, 5003, 5004]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            if result != 0:  # Port is free
                break
        except:
            pass
    else:
        port = find_free_port()
    
    print(f"🚀 Starting Preview Server on http://localhost:{port}")
    print(f"📋 Navigate to http://localhost:{port}/preview to see the visual preview")
    print("✨ Press Ctrl+C to stop the server")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=port, debug=True)