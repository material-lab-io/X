#!/usr/bin/env python3
"""Test PlantUML encoding fix"""

import zlib
import string
import requests

def encode_plantuml(text: str) -> str:
    """Encode PlantUML text for URL using proper encoding"""
    # PlantUML uses DEFLATE compression with custom base64
    compressed = zlib.compress(text.encode('utf-8'), 9)[2:-4]  # Remove zlib headers and checksum
    
    # PlantUML's custom base64 alphabet
    encode_table = string.ascii_uppercase + string.ascii_lowercase + string.digits + '-_'
    
    encoded = ''
    for i in range(0, len(compressed), 3):
        if i+2 < len(compressed):
            b1, b2, b3 = compressed[i], compressed[i+1], compressed[i+2]
            encoded += encode_table[b1 >> 2]
            encoded += encode_table[((b1 & 0x3) << 4) | (b2 >> 4)]
            encoded += encode_table[((b2 & 0xF) << 2) | (b3 >> 6)]
            encoded += encode_table[b3 & 0x3F]
        elif i+1 < len(compressed):
            b1, b2 = compressed[i], compressed[i+1]
            encoded += encode_table[b1 >> 2]
            encoded += encode_table[((b1 & 0x3) << 4) | (b2 >> 4)]
            encoded += encode_table[(b2 & 0xF) << 2]
        else:
            b1 = compressed[i]
            encoded += encode_table[b1 >> 2]
            encoded += encode_table[(b1 & 0x3) << 4]
            
    return encoded

# Test PlantUML code
test_code = """@startuml
participant Client
participant Server
Client -> Server: Request
Server -> Client: Response
@enduml"""

print("Testing PlantUML encoding fix...")
print("Test code:")
print(test_code)
print("\n" + "="*50)

# Encode the PlantUML code
encoded = encode_plantuml(test_code)
print(f"Encoded (length {len(encoded)}): {encoded[:50]}...")

# Test with PlantUML.com server - with HUFFMAN header
url_with_header = f"http://www.plantuml.com/plantuml/png/~1{encoded}"
print(f"\nTesting URL with ~1 header: {url_with_header[:80]}...")

response = requests.get(url_with_header, timeout=10)
print(f"Response status: {response.status_code}")
print(f"Response content type: {response.headers.get('content-type')}")

if response.status_code == 200:
    # Check if it's an image or error
    if 'image' in response.headers.get('content-type', ''):
        print("✅ SUCCESS: Valid PNG image received!")
        # Save to test file
        with open('test_plantuml_output.png', 'wb') as f:
            f.write(response.content)
        print("Saved as: test_plantuml_output.png")
    else:
        print("❌ ERROR: Response is not an image")
        print(f"Response preview: {response.text[:200]}")
else:
    print(f"❌ ERROR: HTTP {response.status_code}")

# Also test without header for comparison
print("\n" + "="*50)
url_without_header = f"http://www.plantuml.com/plantuml/png/{encoded}"
print(f"Testing URL without ~1 header: {url_without_header[:80]}...")

response2 = requests.get(url_without_header, timeout=10)
print(f"Response status: {response2.status_code}")
if response2.status_code == 200 and 'image' in response2.headers.get('content-type', ''):
    print("✅ Works without header too!")
else:
    print("❌ Doesn't work without header")