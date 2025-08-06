#!/usr/bin/env python3
import requests
import json
import pprint

url = 'http://localhost:5000/generate_enhanced'
data = {
    'topic': 'Building a microservices architecture with Docker and Kubernetes',
    'config': {
        'content_type': 'thread',
        'template': 'technical-tutorial',
        'audience': 'intermediate developers learning cloud native',
        'tone': 'educational and practical',
        'goal': 'teach microservices deployment patterns',
        'depth': 'intermediate',
        'words_per_tweet': 50,
        'thread_length': '5-7',
        'include_diagrams': True,
        'diagram_type': 'both',
        'debug_prompt': False
    }
}

print("Sending request to enhanced generator...")
response = requests.post(url, json=data, timeout=60)
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    
    print("\n=== RESPONSE STRUCTURE ===")
    print(f"Success: {result.get('success')}")
    print(f"Keys in response: {list(result.keys())}")
    
    if 'diagram_data' in result:
        print("\n=== DIAGRAM DATA ===")
        dd = result['diagram_data']
        if dd:
            print(f"Keys in diagram_data: {list(dd.keys())}")
            print(f"Has mermaid_code: {'mermaid_code' in dd}")
            print(f"Has plantuml_code: {'plantuml_code' in dd}")
            print(f"Has mermaid_image_path: {'mermaid_image_path' in dd}")
            print(f"Has plantuml_image_path: {'plantuml_image_path' in dd}")
            
            if 'plantuml_code' in dd:
                print(f"\nPlantUML code length: {len(dd['plantuml_code'])}")
                print("PlantUML code preview:")
                print(dd['plantuml_code'][:200] + "..." if len(dd['plantuml_code']) > 200 else dd['plantuml_code'])
            
            if 'plantuml_image_path' in dd:
                print(f"\nPlantUML image path: {dd['plantuml_image_path']}")
        else:
            print("diagram_data is None or empty")
    else:
        print("\nNo diagram_data in response")
    
    if 'tweets' in result:
        print(f"\nNumber of tweets: {len(result['tweets'])}")
else:
    print(f"Error: {response.text}")