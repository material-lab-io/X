#!/usr/bin/env python3
"""
Web interface for the Twitter/X content generator
Accessible via port forwarding from Windows
"""

from flask import Flask, render_template_string, request, jsonify
import json
from datetime import datetime
from unified_tweet_generator import UnifiedTweetGenerator
import os

app = Flask(__name__)

# Load API key from config
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
        api_key = config.get('api_keys', {}).get('gemini')
except:
    api_key = os.environ.get('GEMINI_API_KEY', '')

# Initialize unified generator with auto-polish
generator = UnifiedTweetGenerator(api_key, auto_polish=True) if api_key else None

# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Twitter/X AI Content Generator</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            max-width: 1200px;
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
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #333;
        }
        input, select, textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
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
            transition: background 0.3s;
        }
        button:hover {
            background: #1a91da;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .output {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 12px;
            border: 1px solid #e1e8ed;
        }
        .tweet {
            background: white;
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 15px;
            border: 1px solid #e1e8ed;
            white-space: pre-wrap;
            font-size: 15px;
            line-height: 1.5;
        }
        .tweet-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .char-count {
            font-size: 14px;
            color: #666;
        }
        .char-count.warning {
            color: #ff6b6b;
        }
        .actions {
            margin-top: 15px;
            display: flex;
            gap: 10px;
        }
        .action-btn {
            padding: 8px 16px;
            font-size: 14px;
            border-radius: 20px;
            background: #f0f0f0;
            color: #333;
            border: none;
            cursor: pointer;
            transition: all 0.3s;
        }
        .action-btn:hover {
            background: #e0e0e0;
        }
        .action-btn.approve {
            background: #28a745;
            color: white;
        }
        .action-btn.approve:hover {
            background: #218838;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        .spinner {
            border: 3px solid #f3f3f3;
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
        .template-info {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        .stat-card {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-number {
            font-size: 32px;
            font-weight: bold;
            color: #1DA1F2;
        }
        .stat-label {
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐦 Twitter/X AI Content Generator</h1>
        <p class="subtitle">Generate high-quality technical content following your style guide</p>
        
        <form id="generatorForm">
            <div class="form-group">
                <label for="topic">Topic / Subject</label>
                <input type="text" id="topic" name="topic" placeholder="e.g., Docker optimization, AI agent debugging" required>
            </div>
            
            <div class="form-group">
                <label for="contentType">Content Type</label>
                <select id="contentType" name="contentType">
                    <option value="single">Single Tweet</option>
                    <option value="thread">Thread (5-7 tweets)</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="template">Template</label>
                <select id="template" name="template">
                    <option value="auto">Auto-select based on context</option>
                    <option value="problem_solution">Problem/Solution (Build in Public)</option>
                    <option value="conceptual">Conceptual Deep Dive</option>
                    <option value="workflow">Workflow/Tools Share</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="context">Additional Context (Optional)</label>
                <textarea id="context" name="context" rows="3" placeholder="e.g., problem: containers failing in CI, solution: fixed Docker networking"></textarea>
            </div>
            
            <div class="form-group">
                <label for="generator">Generator Type</label>
                <select id="generator" name="generator">
                    <option value="style_aware">Style-Aware (Follows Guide)</option>
                    <option value="simple">Simple Pattern-Based</option>
                </select>
            </div>
            
            <button type="submit" id="generateBtn">Generate Content</button>
        </form>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Generating your content...</p>
        </div>
        
        <div id="output" class="output" style="display: none;">
            <h2>Generated Content</h2>
            <div id="generatedContent"></div>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="totalGenerated">0</div>
                <div class="stat-label">Total Generated</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="avgLength">0</div>
                <div class="stat-label">Avg Characters</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="templatesUsed">0</div>
                <div class="stat-label">Templates Used</div>
            </div>
        </div>
    </div>

    <script>
        let stats = {
            total: 0,
            totalChars: 0,
            templates: new Set()
        };

        document.getElementById('generatorForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const formData = new FormData(e.target);
            const data = Object.fromEntries(formData);
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('generateBtn').disabled = true;
            document.getElementById('output').style.display = 'none';
            
            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.error) {
                    alert('Error: ' + result.error);
                } else {
                    displayContent(result);
                    updateStats(result);
                }
            } catch (error) {
                alert('Error generating content: ' + error.message);
            } finally {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('generateBtn').disabled = false;
            }
        });
        
        function displayContent(result) {
            const outputDiv = document.getElementById('generatedContent');
            outputDiv.innerHTML = '';
            
            if (result.template_used) {
                const info = document.createElement('div');
                info.className = 'template-info';
                info.innerHTML = `<strong>Template Used:</strong> ${result.template_used}`;
                outputDiv.appendChild(info);
            }
            
            if (result.content_type === 'thread' && Array.isArray(result.content)) {
                result.content.forEach((tweet, index) => {
                    outputDiv.appendChild(createTweetElement(tweet, index + 1));
                });
            } else {
                outputDiv.appendChild(createTweetElement(result.content));
            }
            
            document.getElementById('output').style.display = 'block';
        }
        
        function createTweetElement(content, position = null) {
            const tweetDiv = document.createElement('div');
            tweetDiv.className = 'tweet';
            
            const headerDiv = document.createElement('div');
            headerDiv.className = 'tweet-header';
            
            const positionSpan = document.createElement('span');
            positionSpan.textContent = position ? `Tweet ${position}` : 'Single Tweet';
            
            const charCount = document.createElement('span');
            charCount.className = 'char-count';
            const chars = content.length;
            charCount.textContent = `${chars}/280`;
            if (chars > 280) {
                charCount.classList.add('warning');
            }
            
            headerDiv.appendChild(positionSpan);
            headerDiv.appendChild(charCount);
            
            const contentDiv = document.createElement('div');
            contentDiv.textContent = content;
            
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'actions';
            
            const copyBtn = document.createElement('button');
            copyBtn.className = 'action-btn';
            copyBtn.textContent = '📋 Copy';
            copyBtn.onclick = () => {
                navigator.clipboard.writeText(content);
                copyBtn.textContent = '✅ Copied!';
                setTimeout(() => {
                    copyBtn.textContent = '📋 Copy';
                }, 2000);
            };
            
            const regenerateBtn = document.createElement('button');
            regenerateBtn.className = 'action-btn';
            regenerateBtn.textContent = '🔄 Regenerate';
            regenerateBtn.onclick = () => {
                document.getElementById('generateBtn').click();
            };
            
            actionsDiv.appendChild(copyBtn);
            actionsDiv.appendChild(regenerateBtn);
            
            tweetDiv.appendChild(headerDiv);
            tweetDiv.appendChild(contentDiv);
            tweetDiv.appendChild(actionsDiv);
            
            return tweetDiv;
        }
        
        function updateStats(result) {
            stats.total++;
            
            if (result.content_type === 'thread' && Array.isArray(result.content)) {
                stats.totalChars += result.content.reduce((sum, tweet) => sum + tweet.length, 0);
            } else {
                stats.totalChars += result.content.length;
            }
            
            if (result.template_used) {
                stats.templates.add(result.template_used);
            }
            
            document.getElementById('totalGenerated').textContent = stats.total;
            document.getElementById('avgLength').textContent = Math.round(stats.totalChars / stats.total);
            document.getElementById('templatesUsed').textContent = stats.templates.size;
        }
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
        content_type = data.get('contentType', 'single')
        template = data.get('template', 'auto')
        context_str = data.get('context', '')
        generator_type = data.get('generator', 'style_aware')
        
        # Parse context
        context = {'topic': topic}
        if context_str:
            # Simple parsing of key:value pairs
            for line in context_str.split(','):
                if ':' in line:
                    key, value = line.split(':', 1)
                    context[key.strip()] = value.strip()
        
        # Check if generator is initialized
        if not generator:
            return jsonify({'error': 'API key not configured'}), 500
        
        # Map template names
        template_map = {
            'conceptual': 'ConceptualDeepDive',
            'workflow': 'WorkflowShare',
            'problem_solution': 'ProblemSolution',
            'auto': 'ConceptualDeepDive'  # default
        }
        
        # Map generator type
        gen_type = 'SimplePatternBased' if generator_type == 'simple' else 'StyleAware'
        
        # Map content type
        cont_type = 'Thread' if content_type == 'thread' else 'SinglePost'
        
        # Generate content using unified generator
        result = generator.generate_content(
            topic=topic,
            content_type=cont_type,
            additional_context=context_str,
            generator_type=gen_type,
            template=template_map.get(template, 'ConceptualDeepDive') if gen_type == 'StyleAware' else None
        )
        
        # Extract content for response
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        content = result['generatedTweets']
        if cont_type == 'SinglePost' and isinstance(content, list):
            content = content[0] if content else ''
        
        template_used = result.get('template')
        
        # Include polishing feedback if available
        response_data = {
            'content': content,
            'content_type': content_type,
            'template_used': template_used,
            'generated_at': result.get('createdAt', datetime.now().isoformat()),
            'keywords': result.get('keywords', []),
            'tone': result.get('tone', 'unknown'),
            'difficulty': result.get('difficultyScore', 0)
        }
        
        if 'polishingFeedback' in result:
            response_data['feedback'] = result['polishingFeedback']
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'Twitter/X Content Generator'})

if __name__ == '__main__':
    print("""
    🚀 Twitter/X Content Generator Web Interface
    ==========================================
    
    The server is starting on port 5000...
    
    To access from Windows through WSL SSH:
    
    1. In your SSH session, the server will be running at:
       http://localhost:5000
    
    2. In Windows, set up port forwarding:
       - Open a new Command Prompt or PowerShell
       - Run: ssh -L 5000:localhost:5000 [your-ssh-connection]
       
       Example:
       ssh -L 5000:localhost:5000 user@remote-server
    
    3. Open your Windows browser and go to:
       http://localhost:5000
    
    The interface will let you:
    - Generate single tweets or threads
    - Use different templates
    - Copy content with one click
    - Track generation statistics
    
    Press Ctrl+C to stop the server.
    """)
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)