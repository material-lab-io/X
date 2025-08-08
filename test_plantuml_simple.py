#!/usr/bin/env python3
"""Simple test for PlantUML generation using POST method"""

import requests

def test_plantuml_post():
    """Test PlantUML generation using POST method"""
    
    # Simple PlantUML code
    plantuml_code = """@startuml
participant Client
participant Server
Client -> Server: Request
Server -> Client: Response
@enduml"""
    
    print("Testing PlantUML with POST method...")
    print("PlantUML code:")
    print(plantuml_code)
    print("="*50)
    
    # Try POST to plantuml.com
    url = "http://www.plantuml.com/plantuml/png"
    
    print(f"Sending POST request to: {url}")
    
    try:
        response = requests.post(
            url,
            data={'text': plantuml_code},
            timeout=15
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response content-type: {response.headers.get('content-type')}")
        print(f"Response size: {len(response.content)} bytes")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'image' in content_type.lower():
                print("✅ SUCCESS: Valid PNG image received!")
                # Save the image
                with open('test_plantuml_post_output.png', 'wb') as f:
                    f.write(response.content)
                print("Saved as: test_plantuml_post_output.png")
            else:
                print(f"❌ ERROR: Response is not an image (content-type: {content_type})")
                # Show first part of response for debugging
                print("Response preview:")
                if response.text:
                    print(response.text[:500])
        else:
            print(f"❌ ERROR: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_plantuml_post()