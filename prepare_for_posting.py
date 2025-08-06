#!/usr/bin/env python3
"""
Adapter script to prepare Gemini-generated content for posting
Converts new format to format expected by tweet_diagram_binder.py
"""

import json
import sys
from pathlib import Path
from typing import Dict, List

def convert_to_posting_format(input_file: str) -> Dict:
    """Convert Gemini format to posting format"""
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Convert tweets from objects to strings
    if 'tweets' in data and isinstance(data['tweets'], list):
        tweet_texts = []
        diagram_positions = {}
        
        for tweet in data['tweets']:
            if isinstance(tweet, dict):
                tweet_texts.append(tweet['content'])
                
                # Track which tweets have diagrams
                if tweet.get('has_diagram') and tweet.get('diagram_path'):
                    position = tweet['position'] - 1  # 0-indexed
                    diagram_positions[position] = tweet['diagram_path']
            else:
                # Already a string
                tweet_texts.append(tweet)
        
        # Create posting format
        posting_data = {
            'topic': data.get('topic', 'Generated Content'),
            'tweets': tweet_texts,
            'diagram': data.get('diagram', {}),
            'generated_at': data.get('generated_at'),
            'generator': data.get('generator', 'gemini_dynamic')
        }
        
        # If we have specific diagram attachments, include them
        if diagram_positions:
            posting_data['diagram_attachments'] = diagram_positions
        
        return posting_data
    
    # Single tweet format
    elif 'tweet' in data and isinstance(data['tweet'], dict):
        tweet = data['tweet']
        posting_data = {
            'topic': data.get('topic', 'Generated Content'),
            'tweets': [tweet['content']],
            'generated_at': data.get('generated_at'),
            'generator': data.get('generator', 'gemini_dynamic')
        }
        
        # Include diagram if attached to single tweet
        if tweet.get('has_diagram') and tweet.get('diagram_path'):
            posting_data['diagram'] = {
                'image_path': tweet['diagram_path'],
                'tweet_position': 1
            }
        
        return posting_data
    
    # Return as-is if already in correct format
    return data

def main():
    if len(sys.argv) < 2:
        print("Usage: prepare_for_posting.py <input_file> [output_file]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        # Convert format
        posting_data = convert_to_posting_format(input_file)
        
        # Save to output file or print
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(posting_data, f, indent=2)
            print(f"✅ Converted and saved to: {output_file}")
        else:
            # Save with _posting suffix
            input_path = Path(input_file)
            output_path = input_path.parent / f"{input_path.stem}_posting.json"
            with open(output_path, 'w') as f:
                json.dump(posting_data, f, indent=2)
            print(f"✅ Converted and saved to: {output_path}")
            
        print(f"📝 Topic: {posting_data['topic']}")
        print(f"🐦 Tweets: {len(posting_data['tweets'])}")
        if 'diagram' in posting_data or 'diagram_attachments' in posting_data:
            print(f"📊 Has diagram attachments")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()