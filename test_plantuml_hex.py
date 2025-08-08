#!/usr/bin/env python3
"""Test PlantUML with hexadecimal encoding"""

import requests

def test_plantuml_hex():
    """Test PlantUML using hexadecimal encoding"""
    
    # Simple PlantUML code
    plantuml_code = """@startuml
Alice -> Bob: Hello
Bob -> Alice: Hi!
@enduml"""
    
    print("Testing PlantUML with HEX encoding...")
    print("PlantUML code:")
    print(plantuml_code)
    print("="*50)
    
    # Convert to hexadecimal
    hex_encoded = plantuml_code.encode('utf-8').hex()
    print(f"Hex encoded (first 50 chars): {hex_encoded[:50]}...")
    print(f"Hex length: {len(hex_encoded)}")
    
    # PlantUML URL with ~h prefix for hex encoding
    url = f"http://www.plantuml.com/plantuml/png/~h{hex_encoded}"
    print(f"\nURL with ~h prefix: {url[:80]}...")
    
    try:
        response = requests.get(url, timeout=10)
        print(f"Response status: {response.status_code}")
        print(f"Response content-type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'image' in content_type:
                print("✅ SUCCESS: Valid PNG image received!")
                with open('test_plantuml_hex.png', 'wb') as f:
                    f.write(response.content)
                print("Saved as: test_plantuml_hex.png")
                return True
            else:
                print(f"❌ ERROR: Not an image ({content_type})")
                if 'html' in content_type:
                    # Try to find error message
                    import re
                    error_match = re.search(r'<p[^>]*>(.*?)</p>', response.text)
                    if error_match:
                        print(f"Error message: {error_match.group(1)[:200]}")
        else:
            print(f"❌ ERROR: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        
    return False

if __name__ == "__main__":
    test_plantuml_hex()