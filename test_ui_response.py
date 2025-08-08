#!/usr/bin/env python3
"""Test what the UI is actually returning"""

import requests
import json

# Make the same request the UI would make
response = requests.post(
    "http://localhost:6969/generate",
    json={
        "topic": "Test microservices with Kafka",
        "type": "single",
        "style": "conceptual-deep-dive",
        "include_diagram": True,
        "diagram_type": "both"
    },
    timeout=30
)

if response.status_code == 200:
    data = response.json()
    print("Response structure:")
    print(json.dumps(data, indent=2))
    
    # Check for PlantUML in response
    if 'diagram_data' in data:
        print("\n✅ diagram_data present")
        if 'plantuml_image_path' in data['diagram_data']:
            print(f"✅ plantuml_image_path: {data['diagram_data']['plantuml_image_path']}")
        else:
            print("❌ No plantuml_image_path in diagram_data")
            print(f"Keys in diagram_data: {list(data['diagram_data'].keys())}")
    else:
        print("❌ No diagram_data in response")
else:
    print(f"Error: {response.status_code}")