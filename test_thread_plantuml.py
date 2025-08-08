#!/usr/bin/env python3
"""Test PlantUML generation for threads"""

import requests
import json

# Test for THREAD (not single)
response = requests.post(
    "http://localhost:6969/generate",
    json={
        "topic": "Microservices Architecture with Docker and Kubernetes",
        "type": "thread",  # THREAD not single
        "style": "conceptual-deep-dive",
        "include_diagram": True,
        "diagram_type": "both"
    },
    timeout=30
)

print("Testing THREAD generation with PlantUML...")
print("="*80)

if response.status_code == 200:
    data = response.json()
    
    print(f"✅ Response received")
    print(f"Generator: {data.get('generator')}")
    print(f"Success: {data.get('success')}")
    
    # Check tweets
    if 'tweets' in data:
        print(f"\n📱 Generated {len(data['tweets'])} tweets")
        if data['tweets']:
            print(f"First tweet: {data['tweets'][0].get('content', '')[:80]}...")
    
    # Check for diagrams
    print("\n📊 Diagram Status:")
    if 'diagram_data' in data:
        print("✅ diagram_data present")
        print(f"  Keys: {list(data['diagram_data'].keys())}")
        
        if 'plantuml_code' in data['diagram_data']:
            print("✅ PlantUML code present")
            code = data['diagram_data']['plantuml_code']
            print(f"  First line: {code.split(chr(10))[0] if code else 'Empty'}")
            
        if 'plantuml_image_path' in data['diagram_data']:
            print(f"✅ PlantUML image path: {data['diagram_data']['plantuml_image_path']}")
        else:
            print("❌ No plantuml_image_path")
            
        if 'mermaid_image_path' in data['diagram_data']:
            print(f"✅ Mermaid image path: {data['diagram_data']['mermaid_image_path']}")
    else:
        print("❌ No diagram_data in response")
        if 'diagram' in data:
            print("  But 'diagram' field exists (old format?)")
    
    # Save for inspection
    with open('test_thread_result.json', 'w') as f:
        json.dump(data, f, indent=2)
    print("\n💾 Full result saved to test_thread_result.json")
    
else:
    print(f"❌ Request failed: {response.status_code}")

print("="*80)