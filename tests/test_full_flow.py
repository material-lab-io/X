#!/usr/bin/env python3
"""Test the full generation flow to debug the issue"""

import requests
import json

# Test single tweet generation
print("Testing single tweet generation...")
response = requests.post('http://localhost:5000/generate', json={
    'topic': 'Docker containers',
    'content_type': 'single', 
    'style': 'explanatory',
    'include_diagram': True,
    'diagram_type': 'mermaid'
})

data = response.json()
print(f"Success: {data.get('success')}")
print(f"Has tweets: {'tweets' in data and len(data['tweets']) > 0}")
if data.get('tweets'):
    print(f"First tweet: {data['tweets'][0]['content'][:100]}...")
print(f"Has diagram: {data.get('diagram_data') is not None}")
print()

# Test thread generation 
print("Testing thread generation...")
response = requests.post('http://localhost:5000/generate', json={
    'topic': 'Python decorators',
    'content_type': 'thread',
    'style': 'explanatory', 
    'include_diagram': True,
    'diagram_type': 'both'
})

data = response.json()
print(f"Success: {data.get('success')}")
print(f"Has tweets: {'tweets' in data and len(data['tweets']) > 0}")
if data.get('tweets'):
    print(f"Number of tweets: {len(data['tweets'])}")
    print(f"First tweet: {data['tweets'][0]['content'][:100]}...")
print(f"Has diagram: {data.get('diagram_data') is not None}")

# Check for fallback message
for tweet in data.get('tweets', []):
    if 'Thread generation in progress' in tweet['content']:
        print("WARNING: Found fallback message in tweets!")
        print(f"Full tweet: {tweet}")