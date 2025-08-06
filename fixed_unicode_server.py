#!/usr/bin/env python3
"""
Fixed Unicode Server - Handles surrogate pairs properly
"""

from flask import Flask, Response
import json
from pathlib import Path
import re

app = Flask(__name__)

def fix_surrogates(text):
    """Fix Unicode surrogate pairs and escape sequences"""
    if not isinstance(text, str):
        return str(text)
    
    # First, handle double-escaped sequences
    text = text.replace('\\\\u', '\\u')
    
    # Fix surrogate pairs (e.g., \ud83d\udc47 -> 👇)
    def replace_surrogate_pair(match):
        high = match.group(1)
        low = match.group(2)
        try:
            # Convert surrogate pair to actual Unicode character
            high_val = int(high, 16)
            low_val = int(low, 16)
            # Formula for surrogate pairs
            codepoint = 0x10000 + (high_val - 0xD800) * 0x400 + (low_val - 0xDC00)
            return chr(codepoint)
        except:
            return match.group(0)
    
    # Match surrogate pairs like \ud83d\udc47
    text = re.sub(r'\\u([dD][89aAbB][0-9a-fA-F]{2})\\u([dD][c-fC-F][0-9a-fA-F]{2})', 
                  replace_surrogate_pair, text)
    
    # Fix single Unicode escapes (non-surrogates)
    def replace_unicode(match):
        code = match.group(1)
        try:
            return chr(int(code, 16))
        except:
            return match.group(0)
    
    # Replace remaining \uXXXX patterns
    text = re.sub(r'\\u([0-9a-fA-F]{4})', replace_unicode, text)
    
    return text

@app.route('/')
@app.route('/preview')
def preview():
    try:
        json_path = Path('generated_threads_final.json')
        
        # Start HTML
        html = """<!DOCTYPE html>
<html>
<head>
    <title>Tweet Preview</title>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: -apple-system, Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .header {
            background: white;
            padding: 30px;
            border-radius: 16px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        h1 {
            color: #1da1f2;
            margin: 0 0 10px 0;
            font-size: 36px;
        }
        .subtitle {
            color: #657786;
            font-size: 16px;
        }
        .tweet {
            background: white;
            padding: 25px;
            margin: 20px 0;
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
        }
        .tweet-text {
            white-space: pre-wrap;
            word-wrap: break-word;
            line-height: 1.6;
            font-size: 16px;
            color: #14171a;
        }
        .meta {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 1px solid #e1e8ed;
            color: #657786;
            font-size: 14px;
            display: flex;
            justify-content: space-between;
        }
        .char-count {
            font-weight: 600;
        }
        .emoji-badge {
            background: #e8f5fd;
            color: #1da1f2;
            padding: 2px 10px;
            border-radius: 12px;
            font-size: 12px;
        }
        .error {
            background: #fee;
            color: #c00;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🐦 Tweet Preview</h1>
        <p class="subtitle">Your generated thread with working emojis!</p>
    </div>
"""
        
        if not json_path.exists():
            html += '<div class="error">No generated content found</div>'
        else:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if data and len(data) > 0:
                thread = data[0]
                topic = fix_surrogates(thread.get('topic', 'Thread'))
                
                html += f'<h2 style="text-align: center; color: #14171a; margin: 30px 0;">{topic}</h2>'
                
                tweets = thread.get('generatedTweets', [])
                for i, tweet in enumerate(tweets, 1):
                    # Fix all Unicode issues
                    fixed_tweet = fix_surrogates(tweet)
                    
                    # Check for emojis
                    has_emojis = any(ord(c) > 0x1F000 for c in fixed_tweet)
                    
                    html += f'''
    <div class="tweet">
        <div class="tweet-number">{i}</div>
        <div class="tweet-text">{fixed_tweet}</div>
        <div class="meta">
            <span class="char-count">{len(fixed_tweet)} characters</span>
            {'<span class="emoji-badge">Contains emojis</span>' if has_emojis else ''}
        </div>
    </div>
'''
        
        html += """
</body>
</html>"""
        
        return Response(html, mimetype='text/html', charset='utf-8')
        
    except Exception as e:
        import traceback
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head><title>Error</title><meta charset="UTF-8"></head>
        <body style="font-family: Arial; padding: 20px;">
            <h1>Error</h1>
            <pre>{str(e)}\n\n{traceback.format_exc()}</pre>
        </body>
        </html>
        """
        return Response(error_html, mimetype='text/html')

@app.route('/test')
def test():
    return 'Server is working!'

if __name__ == '__main__':
    # Kill existing servers
    import os
    os.system("pkill -f 'python.*server.py' 2>/dev/null")
    
    print("\n" + "="*60)
    print("✨ FIXED UNICODE SERVER")
    print("="*60)
    print("\n🔗 http://localhost:5000/preview")
    print("\n✅ This server properly handles:")
    print("   • Unicode surrogate pairs (\\ud83d\\udc47 → 👇)")
    print("   • Double-escaped sequences")
    print("   • All emoji types")
    print("\nPress Ctrl+C to stop")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)