#!/usr/bin/env python3
"""Test PlantUML using form generation approach"""

import requests
from urllib.parse import urlencode

def test_plantuml_form():
    """Test PlantUML generation using form submission"""
    
    # Simple PlantUML code
    plantuml_code = """@startuml
Alice -> Bob: Authentication Request
Bob --> Alice: Authentication Response
@enduml"""
    
    print("Testing PlantUML with form submission...")
    print("PlantUML code:")
    print(plantuml_code)
    print("="*50)
    
    # Use the PlantUML web form URL
    base_url = "http://www.plantuml.com/plantuml"
    
    # Try different submission methods
    methods = [
        # Method 1: Direct form URL
        {
            'name': 'Form URL',
            'url': f"{base_url}/form",
            'method': 'post',
            'data': {'text': plantuml_code}
        },
        # Method 2: uml endpoint
        {
            'name': 'UML endpoint',
            'url': f"{base_url}/uml",
            'method': 'post',
            'data': {'text': plantuml_code}
        },
        # Method 3: Direct png with encoded text
        {
            'name': 'PNG with text parameter',
            'url': f"{base_url}/png",
            'method': 'get',
            'params': {'text': plantuml_code}
        }
    ]
    
    for method in methods:
        print(f"\nTrying {method['name']}...")
        print(f"URL: {method['url']}")
        
        try:
            if method['method'] == 'post':
                response = requests.post(
                    method['url'],
                    data=method.get('data', {}),
                    timeout=10
                )
            else:
                response = requests.get(
                    method['url'],
                    params=method.get('params', {}),
                    timeout=10
                )
                
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')
                if 'image' in content_type:
                    print("✅ SUCCESS: Image received!")
                    filename = f"test_{method['name'].replace(' ', '_').lower()}.png"
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    print(f"Saved as: {filename}")
                    break
                else:
                    print(f"❌ Not an image: {content_type}")
                    
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_plantuml_form()