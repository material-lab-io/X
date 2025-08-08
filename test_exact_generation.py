#!/usr/bin/env python3
"""Test the exact generation that's failing"""

import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'functions', 'generators'))

from gemini_dynamic_generator import GeminiDynamicGenerator

# Test topic
topic = "Microservices Architecture Pattern: Building a scalable e-commerce platform with Docker, Kubernetes, and event-driven communication using Apache Kafka"
content_type = "thread"
template = "Conceptual Deep Dive"

print("Testing with exact topic...")
print(f"Topic: {topic}")
print(f"Type: {content_type}")
print(f"Template: {template}")
print("="*80)

# Try to load API key from config
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
        api_key = config.get('api_keys', {}).get('gemini')
        if not api_key:
            api_key = config.get('gemini_api_key')
        print(f"API Key loaded: {api_key[:15]}...")
except Exception as e:
    print(f"Error loading config: {e}")
    api_key = "AIzaSyAMOvO0_b0o5LdvZgZBVqZ3mSfBwBukzgY"

try:
    # Initialize generator
    generator = GeminiDynamicGenerator(api_key)
    
    # Generate content
    result = generator.generate_content(
        topic=topic,
        content_type=content_type,
        template=template,
        context="Focus on architectural decisions and trade-offs",
        diagram_type="both"
    )
    
    print("\nResult structure:")
    print(f"Keys: {list(result.keys())}")
    
    if 'error' in result:
        print(f"\n❌ ERROR in result: {result['error']}")
        if 'tweets' in result:
            print(f"Fallback tweets: {result['tweets']}")
    
    if 'tweets' in result and not result.get('error'):
        print(f"\n✅ SUCCESS: Generated {len(result['tweets'])} tweets")
        for i, tweet in enumerate(result['tweets'][:2], 1):
            print(f"\nTweet {i}:")
            print(f"  Content: {tweet['content'][:100]}...")
            print(f"  Length: {tweet['character_count']} chars")
    elif 'tweet' in result:
        print(f"\n✅ Single tweet generated")
        print(f"  Content: {result['tweet']['content'][:100]}...")
    
    # Save result for inspection
    with open('test_generation_result.json', 'w') as f:
        json.dump(result, f, indent=2)
        print(f"\nFull result saved to test_generation_result.json")
        
except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")
    import traceback
    traceback.print_exc()