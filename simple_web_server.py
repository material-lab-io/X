#!/usr/bin/env python3
"""
Simple web server for Twitter/X content generator using built-in Python modules
No external dependencies required!
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from simple_tweet_generator import SimpleTweetGenerator
from style_aware_generator import StyleAwareTweetGenerator
from datetime import datetime

# Initialize generators
simple_generator = SimpleTweetGenerator()
style_generator = StyleAwareTweetGenerator()

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Twitter/X Content Generator</title>
    <meta charset="utf-8">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
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
        h1 {
            color: #1DA1F2;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            font-weight: bold;
            margin-bottom: 5px;
        }
        input, select, textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        button {
            background: #1DA1F2;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover {
            background: #1a91da;
        }
        .output {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            display: none;
        }
        .tweet {
            background: white;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 10px;
            border: 1px solid #e1e8ed;
            white-space: pre-wrap;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }
        .char-count {
            font-size: 14px;
            color: #666;
            margin-top: 5px;
        }
        .copy-btn {
            background: #28a745;
            color: white;
            padding: 5px 15px;
            border: none;
            border-radius: 15px;
            font-size: 14px;
            cursor: pointer;
            margin-top: 10px;
        }
        .error {
            color: #dc3545;
            padding: 10px;
            background: #f8d7da;
            border-radius: 5px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🐦 Twitter/X Content Generator</h1>
        <p>Generate high-quality technical content for Twitter/X</p>
        
        <form id="genForm" onsubmit="generateContent(event)">
            <div class="form-group">
                <label>Topic</label>
                <input type="text" id="topic" placeholder="e.g., Docker optimization" required>
            </div>
            
            <div class="form-group">
                <label>Content Type</label>
                <select id="contentType">
                    <option value="single">Single Tweet</option>
                    <option value="thread">Thread (5 tweets)</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>Generator</label>
                <select id="generator">
                    <option value="style">Style-Aware (Follows Guide)</option>
                    <option value="simple">Simple Pattern-Based</option>
                </select>
            </div>
            
            <div class="form-group">
                <label>Context (Optional)</label>
                <textarea id="context" rows="3" placeholder="e.g., problem: containers failing, solution: fixed networking"></textarea>
            </div>
            
            <button type="submit">Generate Content</button>
        </form>
        
        <div id="output" class="output"></div>
    </div>
    
    <script>
        async function generateContent(e) {
            e.preventDefault();
            
            const data = {
                topic: document.getElementById('topic').value,
                contentType: document.getElementById('contentType').value,
                generator: document.getElementById('generator').value,
                context: document.getElementById('context').value
            };
            
            const output = document.getElementById('output');
            output.style.display = 'block';
            output.innerHTML = '<p>Generating...</p>';
            
            try {
                const response = await fetch('/api/generate', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.error) {
                    output.innerHTML = `<div class="error">Error: ${result.error}</div>`;
                } else {
                    displayResult(result);
                }
            } catch (err) {
                output.innerHTML = `<div class="error">Error: ${err.message}</div>`;
            }
        }
        
        function displayResult(result) {
            const output = document.getElementById('output');
            output.innerHTML = '<h2>Generated Content</h2>';
            
            if (Array.isArray(result.content)) {
                // Thread
                result.content.forEach((tweet, i) => {
                    output.innerHTML += createTweetHTML(tweet, i + 1);
                });
            } else {
                // Single tweet
                output.innerHTML += createTweetHTML(result.content);
            }
        }
        
        function createTweetHTML(content, num = null) {
            const chars = content.length;
            const header = num ? `Tweet ${num}` : 'Generated Tweet';
            return `
                <div class="tweet">
                    <strong>${header}</strong>
                    <div>${content}</div>
                    <div class="char-count">${chars}/280 characters</div>
                    <button class="copy-btn" onclick="copyText('${content.replace(/'/g, "\\'")}')">Copy</button>
                </div>
            `;
        }
        
        function copyText(text) {
            navigator.clipboard.writeText(text).then(() => {
                alert('Copied to clipboard!');
            });
        }
    </script>
</body>
</html>
"""

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode())
        else:
            self.send_error(404)
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/api/generate':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode())
                result = self.generate_content(data)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                error_response = {'error': str(e)}
                self.wfile.write(json.dumps(error_response).encode())
        else:
            self.send_error(404)
    
    def generate_content(self, data):
        """Generate tweet content based on request data"""
        topic = data.get('topic', '')
        content_type = data.get('contentType', 'single')
        generator_type = data.get('generator', 'simple')
        context_str = data.get('context', '')
        
        # Parse context
        context = {'topic': topic}
        if context_str:
            # Simple parsing
            if 'problem:' in context_str:
                parts = context_str.split('problem:')
                if len(parts) > 1:
                    problem_part = parts[1].split(',')[0].strip()
                    context['problem'] = problem_part
            if 'solution:' in context_str:
                parts = context_str.split('solution:')
                if len(parts) > 1:
                    solution_part = parts[1].split(',')[0].strip()
                    context['solution'] = solution_part
        
        # Generate content
        if generator_type == 'simple':
            if content_type == 'single':
                result = simple_generator.generate_single_tweet(topic)
                content = result['content']['full_text']
            else:
                result = simple_generator.generate_thread(topic)
                content = [tweet['content'] for tweet in result['tweets']]
        else:
            # Style-aware generator
            result = style_generator.generate_style_aware_tweet(topic, context)
            content = result['content']
        
        return {
            'content': content,
            'type': content_type,
            'generated_at': datetime.now().isoformat()
        }
    
    def log_message(self, format, *args):
        """Override to reduce console spam"""
        if '/api/' in args[0]:
            return
        super().log_message(format, *args)

def run_server(port=5000):
    """Run the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    
    print(f"""
🚀 Twitter/X Content Generator Server Started!
============================================

Server running at: http://localhost:{port}

📌 To access from Windows through WSL/SSH:

1. Keep this terminal running

2. In Windows, set up port forwarding:
   ssh -L {port}:localhost:{port} kushagra@your-server

3. Open in Windows browser:
   http://localhost:{port}

Press Ctrl+C to stop the server
============================================
    """)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\nServer stopped.")

if __name__ == '__main__':
    run_server()