#\!/usr/bin/env python3
"""Complete system test for PlantUML generation"""

import requests
import json
import os

SERVER_URL = "http://localhost:6969"

print("="*80)
print("COMPLETE PLANTUML SYSTEM TEST")
print("="*80)

# Test 1: Single post with PlantUML
print("\n📝 TEST 1: Single Post with PlantUML")
print("-"*40)

response = requests.post(
    f"{SERVER_URL}/generate",
    json={
        "topic": "Event-Driven Microservices with Apache Kafka",
        "type": "single",
        "style": "conceptual-deep-dive",
        "include_diagram": True,
        "diagram_type": "both"
    },
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    print(f"✅ Single post generated")
    
    # Check for PlantUML
    if 'diagram_data' in data and data['diagram_data'] and 'plantuml_image_path' in data['diagram_data']:
        path = data['diagram_data']['plantuml_image_path']
        print(f"✅ PlantUML path: {path}")
        
        # Verify file exists
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✅ PlantUML file exists: {size} bytes")
        else:
            print(f"❌ PlantUML file not found at {path}")
    else:
        print("❌ No PlantUML image path in response")
        if 'diagram_data' in data:
            print(f"   Available keys: {list(data['diagram_data'].keys())}")
else:
    print(f"❌ Request failed: {response.status_code}")

# Test 2: Thread with PlantUML
print("\n📝 TEST 2: Thread with PlantUML")
print("-"*40)

response = requests.post(
    f"{SERVER_URL}/generate",
    json={
        "topic": "Building Scalable APIs with GraphQL and REST",
        "type": "thread",
        "style": "conceptual-deep-dive",
        "include_diagram": True,
        "diagram_type": "both"
    },
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    content_type = data.get('content_type', 'unknown')
    tweets_count = len(data.get('tweets', []))
    
    print(f"✅ Thread generated")
    print(f"   Content type: {content_type}")
    print(f"   Tweets: {tweets_count}")
    
    # Check for PlantUML
    if 'diagram_data' in data and data['diagram_data'] and 'plantuml_image_path' in data['diagram_data']:
        path = data['diagram_data']['plantuml_image_path']
        print(f"✅ PlantUML path: {path}")
        
        # Verify file exists
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✅ PlantUML file exists: {size} bytes")
        else:
            print(f"❌ PlantUML file not found at {path}")
    else:
        print("❌ No PlantUML image path in response")
        if 'diagram_data' in data:
            print(f"   Available keys: {list(data['diagram_data'].keys())}")
else:
    print(f"❌ Request failed: {response.status_code}")

print("\n" + "="*80)
print("TEST COMPLETE")
print("="*80)
