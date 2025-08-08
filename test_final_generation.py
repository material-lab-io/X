#!/usr/bin/env python3
"""Final test for complete generation with PlantUML"""

import requests
import json
import time

SERVER_URL = "http://localhost:6969"

# Test data
test_data = {
    "topic": "Microservices Architecture: Building scalable e-commerce with Docker, Kubernetes, and Kafka",
    "type": "thread",
    "style": "conceptual-deep-dive",
    "include_diagram": True,
    "diagram_type": "both"
}

print("🚀 Testing complete generation with PlantUML...")
print(f"Topic: {test_data['topic']}")
print("="*80)

try:
    response = requests.post(
        f"{SERVER_URL}/generate",
        json=test_data,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"✅ Generation successful!")
        print(f"Generator: {result.get('generator', 'unknown')}")
        
        # Check tweets
        if 'tweets' in result and result['tweets']:
            tweets = result['tweets']
            print(f"\n📱 Generated {len(tweets)} tweets:")
            
            # Check if it's real content or fallback
            first_content = tweets[0].get('content', '')
            if "Exploring" in first_content and "Thread generation in progress" in first_content:
                print("⚠️ WARNING: Fallback message detected!")
            else:
                for i, tweet in enumerate(tweets[:2], 1):
                    print(f"\nTweet {i}:")
                    print(f"  {tweet.get('content', '')[:100]}...")
                    print(f"  ({tweet.get('character_count', 0)} chars)")
        
        # Check for PlantUML diagram
        print("\n📊 Diagram Status:")
        if 'diagram_data' in result and result['diagram_data']:
            diagram_data = result['diagram_data']
            if 'plantuml_code' in diagram_data:
                print("✅ PlantUML code present")
                print(f"  Theme: {diagram_data.get('theme', 'none')}")
                # Show first few lines of PlantUML code
                lines = diagram_data['plantuml_code'].split('\n')[:5]
                for line in lines:
                    print(f"    {line}")
            
            if 'plantuml_image_path' in diagram_data:
                print(f"✅ PlantUML image path: {diagram_data['plantuml_image_path']}")
            elif 'plantuml_path' in diagram_data:
                print(f"✅ PlantUML path: {diagram_data['plantuml_path']}")
            else:
                print("❌ No PlantUML image path found")
                
            if 'mermaid_image_path' in diagram_data:
                print(f"✅ Mermaid image path: {diagram_data['mermaid_image_path']}")
        else:
            print("❌ No diagram data in response")
        
        # Save full result for inspection
        with open('test_final_result.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("\n💾 Full result saved to test_final_result.json")
        
    else:
        print(f"❌ Request failed: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "="*80)