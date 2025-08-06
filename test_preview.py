#!/usr/bin/env python3
"""
Direct test of Unicode handling - generates an HTML preview file
"""

import json
from pathlib import Path
from html import escape

def safe_json_loads(text):
    """Safely decode Unicode escape sequences"""
    try:
        return json.loads(f'"{text}"')
    except:
        try:
            return json.loads(text)
        except:
            return text

# Read the generated file
json_path = Path('generated_threads_final.json')
if not json_path.exists():
    print("Error: generated_threads_final.json not found")
    exit(1)

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Generate HTML
html = """
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
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 { color: #1da1f2; margin: 0 0 10px 0; }
        h2 { color: #333; text-align: center; }
        .tweet {
            background: white;
            padding: 20px;
            margin: 15px 0;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            position: relative;
            padding-left: 60px;
        }
        .tweet-number {
            position: absolute;
            left: 20px;
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
        .tweet-text {
            white-space: pre-wrap;
            line-height: 1.5;
            font-size: 16px;
            color: #14171a;
        }
        .meta {
            color: #657786;
            font-size: 14px;
            margin-top: 10px;
            padding-top: 10px;
            border-top: 1px solid #e1e8ed;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🐦 Tweet Preview</h1>
        <p style="color: #666; margin: 0;">Generated content with proper emoji display</p>
    </div>
"""

if data and isinstance(data, list) and len(data) > 0:
    thread_data = data[0]
    topic = thread_data.get('topic', 'Generated Thread')
    raw_tweets = thread_data.get('generatedTweets', [])
    
    html += f'<h2>{escape(topic)}</h2>'
    
    for i, tweet_text in enumerate(raw_tweets, 1):
        # Decode Unicode properly
        decoded_text = safe_json_loads(tweet_text)
        safe_text = escape(decoded_text)
        
        html += f'''
        <div class="tweet">
            <div class="tweet-number">{i}</div>
            <div class="tweet-text">{safe_text}</div>
            <div class="meta">
                <strong>{len(decoded_text)}</strong> characters
                {' • Contains emojis' if any(ord(c) > 127 for c in decoded_text) else ''}
            </div>
        </div>
        '''
        
        # Print to console for debugging
        print(f"\nTweet {i}:")
        print(f"Original: {repr(tweet_text[:100])}")
        print(f"Decoded: {decoded_text[:100]}")

html += """
</body>
</html>
"""

# Save the HTML file
output_path = Path('tweet_preview.html')
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"\n✅ Preview generated successfully!")
print(f"📄 Open tweet_preview.html in your browser")
print(f"🔗 file://{output_path.absolute()}")