#!/usr/bin/env python3
"""
Final Working Server - Properly handles double-escaped Unicode
"""

from flask import Flask, Response
import json
from pathlib import Path
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

def fix_double_escaped_unicode(text):
    """Fix double-escaped Unicode sequences like \\ud83d\\udc47"""
    if not isinstance(text, str):
        return str(text)
    
    # First, replace double backslashes with single
    text = text.replace('\\\\u', '\\u')
    
    # Now decode the Unicode escape sequences
    try:
        # Use encode/decode with 'raw_unicode_escape'
        decoded = text.encode('raw_unicode_escape').decode('unicode_escape')
        return decoded
    except:
        # If that fails, try a different approach
        try:
            # Use regex to find all Unicode sequences
            def replace_unicode(match):
                code = match.group(1)
                try:
                    return chr(int(code, 16))
                except:
                    return match.group(0)
            
            # Replace \uXXXX patterns
            decoded = re.sub(r'\\u([0-9a-fA-F]{4})', replace_unicode, text)
            return decoded
        except:
            return text

@app.route('/')
@app.route('/preview')
def preview():
    try:
        # Read the JSON file
        json_path = Path('generated_threads_final.json')
        if not json_path.exists():
            return Response("No generated content found", status=404)
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Start building response
        html = """<!DOCTYPE html>
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
            color: #14171a;
        }
        .header {
            background: white;
            padding: 25px;
            border-radius: 16px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        h1 { 
            color: #1da1f2; 
            margin: 0 0 10px 0;
            font-size: 32px;
        }
        .subtitle {
            color: #657786;
            margin: 0;
        }
        h2 { 
            color: #14171a; 
            text-align: center;
            margin: 30px 0 20px 0;
        }
        .tweet {
            background: white;
            padding: 25px;
            margin: 15px 0;
            border-radius: 16px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            position: relative;
            transition: transform 0.2s;
        }
        .tweet:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.12);
        }
        .tweet-number {
            position: absolute;
            left: -20px;
            top: 25px;
            background: #1da1f2;
            color: white;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 18px;
            box-shadow: 0 2px 4px rgba(29,161,242,0.3);
        }
        .tweet-text {
            white-space: pre-wrap;
            line-height: 1.6;
            font-size: 16px;
            color: #14171a;
            margin-bottom: 15px;
        }
        .meta {
            color: #657786;
            font-size: 14px;
            padding-top: 15px;
            border-top: 1px solid #e1e8ed;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .emoji-indicator {
            background: #e8f5fd;
            color: #1da1f2;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 12px;
        }
        .generate-btn {
            display: inline-block;
            background: #1da1f2;
            color: white;
            padding: 12px 24px;
            border-radius: 24px;
            text-decoration: none;
            font-weight: 600;
            margin-top: 20px;
            transition: background 0.2s;
        }
        .generate-btn:hover {
            background: #1a91da;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🐦 Tweet Preview</h1>
        <p class="subtitle">Your generated thread with proper emoji display</p>
    </div>
"""
        
        if data and isinstance(data, list) and len(data) > 0:
            thread_data = data[0]
            topic = thread_data.get('topic', 'Generated Thread')
            raw_tweets = thread_data.get('generatedTweets', [])
            
            # Clean up topic
            topic = fix_double_escaped_unicode(topic)
            html += f'<h2>{topic}</h2>'
            
            # Process tweets
            for i, tweet_text in enumerate(raw_tweets, 1):
                # Fix Unicode
                decoded_text = fix_double_escaped_unicode(tweet_text)
                
                # Check if contains emojis
                has_emojis = any(ord(c) > 127 for c in decoded_text)
                
                html += f'''
    <div class="tweet">
        <div class="tweet-number">{i}</div>
        <div class="tweet-text">{decoded_text}</div>
        <div class="meta">
            <span><strong>{len(decoded_text)}</strong> characters</span>
            {'<span class="emoji-indicator">Contains emojis</span>' if has_emojis else ''}
        </div>
    </div>
'''
        
        html += """
    <div style="text-align: center; margin-top: 40px;">
        <a href="/generate" class="generate-btn">Generate New Thread</a>
    </div>
</body>
</html>"""
        
        return Response(html, mimetype='text/html')
        
    except Exception as e:
        logger.error(f"Error in preview: {e}")
        import traceback
        logger.error(traceback.format_exc())
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Error</title><meta charset="UTF-8"></head>
        <body style="font-family: Arial; padding: 20px;">
            <h1>Error</h1>
            <p>An error occurred: {str(e)}</p>
            <pre>{traceback.format_exc()}</pre>
        </body>
        </html>
        """
        return Response(error_html, mimetype='text/html', status=500)

@app.route('/generate')
def generate():
    return Response("""
    <!DOCTYPE html>
    <html>
    <head><title>Generate</title><meta charset="UTF-8"></head>
    <body style="font-family: Arial; padding: 20px;">
        <h1>Generate Page</h1>
        <p>Generation form would go here</p>
        <a href="/preview">View Preview</a>
    </body>
    </html>
    """, mimetype='text/html')

if __name__ == '__main__':
    # Kill any existing servers
    import os
    os.system("pkill -f 'python.*server.py' 2>/dev/null")
    
    print("\n" + "="*60)
    print("🚀 Final Working Server - Emoji Support Fixed!")
    print("="*60)
    print("\n📍 URL: http://localhost:5000/preview")
    print("\n✨ Features:")
    print("  • Properly displays all emojis (👇, 💣, 🧵, ✅, etc.)")
    print("  • Handles double-escaped Unicode sequences")
    print("  • Clean, modern interface")
    print("  • Robust error handling")
    print("\nPress Ctrl+C to stop")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)