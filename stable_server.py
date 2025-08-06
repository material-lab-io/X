#!/usr/bin/env python3
"""
Stable Server - Robust error handling and Unicode support
"""

from flask import Flask, Response, request, redirect, url_for
import json
from pathlib import Path
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def safe_json_loads(text):
    """Safely decode Unicode escape sequences"""
    try:
        # Try direct json.loads with quotes
        return json.loads(f'"{text}"')
    except:
        try:
            # Try without quotes
            return json.loads(text)
        except:
            # Return as-is
            return text

@app.route('/')
def index():
    return redirect(url_for('preview'))

@app.route('/generate')
def generate():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Generate</title>
        <meta charset="UTF-8">
    </head>
    <body>
        <h1>Generate Page</h1>
        <p>This would be the generation form</p>
        <a href="/preview">View Preview</a>
    </body>
    </html>
    """
    return Response(html, mimetype='text/html')

@app.route('/preview')
def preview():
    try:
        # Start building HTML
        html_parts = ["""
<!DOCTYPE html>
<html>
<head>
    <title>Tweet Preview</title>
    <meta charset="UTF-8">
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, Arial, sans-serif; 
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
        h1 { color: #1da1f2; margin: 0 0 10px 0; }
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
            font-size: 16px;
        }
        .meta {
            color: #666;
            font-size: 14px;
            margin-top: 10px;
        }
        .error {
            background: #fee;
            padding: 20px;
            border-radius: 10px;
            color: #c00;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🐦 Tweet Preview</h1>
        <p style="color: #666; margin: 0;">Displaying generated content with proper emoji support</p>
    </div>
"""]
        
        # Try to load and display tweets
        json_path = Path('generated_threads_final.json')
        
        if not json_path.exists():
            html_parts.append('<div class="error">No generated content found. Generate some content first!</div>')
        else:
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                if data and isinstance(data, list) and len(data) > 0:
                    thread_data = data[0]
                    raw_tweets = thread_data.get('generatedTweets', [])
                    
                    # Add topic if available
                    topic = thread_data.get('topic', 'Generated Thread')
                    html_parts.append(f'<h2 style="text-align: center; color: #333;">{topic}</h2>')
                    
                    # Process each tweet
                    for i, tweet_text in enumerate(raw_tweets, 1):
                        # Decode Unicode
                        decoded_text = safe_json_loads(tweet_text)
                        
                        # Escape HTML but preserve newlines
                        from html import escape
                        safe_text = escape(decoded_text)
                        
                        html_parts.append(f'''
                        <div class="tweet">
                            <div class="tweet-number">Tweet {i}</div>
                            <div class="tweet-text">{safe_text}</div>
                            <div class="meta">{len(decoded_text)} characters</div>
                        </div>
                        ''')
                else:
                    html_parts.append('<div class="error">No tweets found in the data</div>')
                    
            except Exception as e:
                logger.error(f"Error reading JSON: {e}")
                html_parts.append(f'<div class="error">Error reading data: {str(e)}</div>')
        
        html_parts.append('</body></html>')
        
        # Return complete HTML
        return Response(''.join(html_parts), mimetype='text/html')
        
    except Exception as e:
        logger.error(f"Critical error in preview: {e}")
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Error</title><meta charset="UTF-8"></head>
        <body>
            <h1>Server Error</h1>
            <p>An error occurred: {str(e)}</p>
            <p><a href="/">Try again</a></p>
        </body>
        </html>
        """
        return Response(error_html, mimetype='text/html', status=500)

@app.route('/health')
def health():
    return Response('OK', mimetype='text/plain')

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Stable Tweet Preview Server")
    print("="*50)
    print("\nURLs:")
    print("  Preview: http://localhost:5000/preview")
    print("  Health:  http://localhost:5000/health")
    print("\nFeatures:")
    print("  ✓ Proper Unicode/emoji handling")
    print("  ✓ Robust error handling")
    print("  ✓ Clean, simple interface")
    print("\nPress Ctrl+C to stop")
    print("="*50 + "\n")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except Exception as e:
        print(f"\nError starting server: {e}")
        sys.exit(1)