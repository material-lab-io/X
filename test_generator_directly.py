#!/usr/bin/env python3
"""Test the Gemini generator directly"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'functions', 'generators'))

from gemini_dynamic_generator import GeminiDynamicGenerator

# Initialize generator
api_key = "AIzaSyAMOvO0_b0o5LdvZgZBVqZ3mSfBwBukzgY"
generator = GeminiDynamicGenerator(api_key)

# Test with the same topic
topic = "Building a Real-Time Analytics Platform: From Data Ingestion to Dashboard - Architecture Deep Dive"
content_type = "thread"
template = "Conceptual Deep Dive"

print(f"Testing generation for topic: {topic[:50]}...")
print(f"Content type: {content_type}")
print(f"Template: {template}")
print("="*50)

try:
    result = generator.generate_content(topic, content_type, template)
    
    if 'error' in result:
        print(f"❌ Generation failed: {result['error']}")
    elif 'tweets' in result:
        print(f"✅ Generated {len(result['tweets'])} tweets")
        for i, tweet in enumerate(result['tweets'], 1):
            print(f"\nTweet {i} ({tweet.get('character_count', 0)} chars):")
            print(tweet['content'])
    else:
        print("❌ Unexpected result format:")
        print(result)
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()