#!/usr/bin/env python3
"""Test what the server is returning for thread generation"""

import requests
import json

# Test URL
url = "http://localhost:5000/generate"

# Test data - similar to what browser might send
test_data = {
    "topic": "Docker containers",
    "content_type": "thread",
    "style": "explanatory",
    "context": "",
    "include_diagram": True,
    "diagram_type": "mermaid"
}

print("Sending request to server...")
print(f"Data: {json.dumps(test_data, indent=2)}")

response = requests.post(url, json=test_data)

print(f"\nResponse status: {response.status_code}")
print("\nResponse JSON:")
data = response.json()
print(json.dumps(data, indent=2))

# Check if we got fallback
if data.get('tweets'):
    first_tweet = data['tweets'][0]
    if 'Thread generation in progress' in first_tweet.get('content', ''):
        print("\n⚠️  WARNING: Got fallback response!")
        print(f"Generator used: {data.get('generator', 'unknown')}")
        print(f"Error in response: {data.get('error', 'No error field')}")