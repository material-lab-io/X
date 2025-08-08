#!/usr/bin/env python3
"""Test Sunlust theme with proper encoding"""

import zlib
import string
import requests

def encode_plantuml(text: str) -> str:
    """Encode PlantUML text for URL using proper encoding"""
    # PlantUML's custom base64 alphabet
    maketrans = bytes.maketrans
    base64_alphabet = b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    plantuml_alphabet = b'0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
    
    # Compress using deflate
    zlibbed = zlib.compress(text.encode('utf-8'))
    compressed = zlibbed[2:-4]
    
    # Standard base64
    import base64
    b64encoded = base64.b64encode(compressed)
    
    # Translate to PlantUML alphabet
    translated = b64encoded.translate(maketrans(base64_alphabet, plantuml_alphabet))
    
    return translated.decode('ascii')

# Test with sunlust theme (lowercase)
test_code = """@startuml
!theme sunlust
participant Client
participant Server
Client -> Server: Request
Server -> Client: Response
@enduml"""

print('Testing sunlust theme with PlantUML.com...')
print('PlantUML code:')
print(test_code)
print()

# Encode for PlantUML
encoded = encode_plantuml(test_code)
print(f'Encoded (length {len(encoded)}): {encoded[:50]}...')

# Test with PlantUML.com using ~1 prefix
url = f'http://www.plantuml.com/plantuml/png/~1{encoded}'
print(f'URL: {url[:80]}...')

try:
    response = requests.get(url, timeout=10)
    print(f'Response status: {response.status_code}')
    print(f'Content type: {response.headers.get("content-type")}')
    
    if response.status_code == 200:
        # Check if it's an image or error image
        if 'image' in response.headers.get('content-type', ''):
            # Save and check size
            with open('sunlust_test.png', 'wb') as f:
                f.write(response.content)
            
            if len(response.content) > 1000:  # Proper diagram should be > 1KB
                print('✅ Sunlust theme works! Diagram generated successfully.')
                print(f'Image size: {len(response.content)} bytes')
            else:
                print('⚠️ Small image size - might be an error image')
        else:
            print('❌ Response is not an image')
    else:
        print(f'❌ HTTP error: {response.status_code}')
        
except Exception as e:
    print(f'❌ Error: {e}')