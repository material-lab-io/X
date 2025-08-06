#!/usr/bin/env python3
"""
Simple working web server for Twitter/X content generation
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from simple_tweet_generator import SimpleTweetGenerator

class TweetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = """
<!DOCTYPE html>
<html>
<head>
    <title>Twitter/X Content Generator</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        h1 { color: #1DA1F2; }
        textarea, input, select { width: 100%; padding: 10px; margin: 10px 0; }
        button { background: #1DA1F2; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #1a8cd8; }
        .tweet { background: #f8f9fa; padding: 15px; border-radius: 10px; margin: 10px 0; }
        .char-count { color: #657786; font-size: 14px; }
    </style>
</head>
<body>
    <h1>🐦 Twitter/X Content Generator</h1>
    <form method="GET" action="/generate">
        <label>Topic:</label>
        <input type="text" name="topic" placeholder="e.g., Docker optimization" required>
        
        <label>Category:</label>
        <select name="category">
            <option value="">Auto-detect</option>
            <option value="ai_agents">AI Agents</option>
            <option value="docker">Docker</option>
            <option value="video_models">Video Models</option>
            <option value="llms">LLMs</option>
            <option value="devtools">DevTools</option>
            <option value="coding">Coding</option>
        </select>
        
        <label>Type:</label>
        <select name="type">
            <option value="single">Single Tweet</option>
            <option value="thread">Thread</option>
        </select>
        
        <button type="submit">Generate</button>
    </form>
</body>
</html>
"""
            self.wfile.write(html.encode())
        
        elif self.path.startswith('/generate'):
            # Parse query parameters
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            
            topic = params.get('topic', [''])[0]
            category = params.get('category', [''])[0] or None
            tweet_type = params.get('type', ['single'])[0]
            
            # Generate content
            generator = SimpleTweetGenerator()
            
            if tweet_type == 'thread':
                result = generator.generate_thread(topic, category)
                content = result
            else:
                result = generator.generate_single(topic, category)
                content = [{'content': result, 'position': 1, 'character_count': len(result)}]
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Generated Content</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }}
        h1 {{ color: #1DA1F2; }}
        .tweet {{ background: #f8f9fa; padding: 15px; border-radius: 10px; margin: 10px 0; }}
        .char-count {{ color: #657786; font-size: 14px; }}
        button {{ background: #1DA1F2; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }}
        button:hover {{ background: #1a8cd8; }}
    </style>
</head>
<body>
    <h1>Generated Content</h1>
    <a href="/">← Back</a>
    <hr>
"""
            
            for tweet in content:
                html += f"""
    <div class="tweet">
        <strong>Tweet {tweet['position']}</strong>
        <p>{tweet['content']}</p>
        <div class="char-count">{tweet['character_count']}/280 characters</div>
        <button onclick="navigator.clipboard.writeText(`{tweet['content'].replace('`', '\\`')}`)">📋 Copy</button>
    </div>
"""
            
            html += """
</body>
</html>
"""
            self.wfile.write(html.encode())
        
        else:
            self.send_response(404)
            self.end_headers()

def run_server(port=5000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, TweetHandler)
    print(f"Server running on http://localhost:{port}")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()