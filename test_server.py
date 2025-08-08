#!/usr/bin/env python3
"""Test script to diagnose server issues"""

import requests
import json

# Test the server
url = "http://localhost:6969/generate"

# Simple test case
test_data = {
    "topic": "Docker best practices",
    "content_type": "thread",
    "style": "explanatory",
    "context": "",
    "include_diagram": True,
    "diagram_type": "mermaid"
}

print("Testing server with simple request...")
print(f"Request data: {json.dumps(test_data, indent=2)}")

try:
    response = requests.post(url, json=test_data)
    result = response.json()
    
    print(f"\nResponse status: {response.status_code}")
    
    if 'error' in result:
        print(f"ERROR in response: {result['error']}")
    
    if 'tweets' in result:
        print(f"SUCCESS: Got {len(result['tweets'])} tweets")
        for i, tweet in enumerate(result['tweets'][:2], 1):
            print(f"  Tweet {i}: {tweet['content'][:80]}...")
    elif 'tweet' in result:
        print(f"SUCCESS: Got single tweet")
        print(f"  Content: {result['tweet']['content'][:80]}...")
    else:
        print(f"Unexpected response format. Keys: {list(result.keys())}")
        
    if result.get('diagram_data'):
        print("\nDiagram data present!")
        
except Exception as e:
    print(f"Error testing server: {e}")