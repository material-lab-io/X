#!/usr/bin/env python3
"""Test Kroki.io for PlantUML generation"""

import base64
import requests

# Test PlantUML code
test_code = """@startuml
participant Client
participant Server
Client -> Server: Request
Server -> Client: Response
@enduml"""

print("Testing Kroki.io PlantUML generation...")
print("Test code:")
print(test_code)
print("\n" + "="*50)

# Encode for Kroki.io (simple base64 URL-safe encoding)
kroki_encoded = base64.urlsafe_b64encode(test_code.encode('utf-8')).decode('ascii')
print(f"Kroki encoded (length {len(kroki_encoded)}): {kroki_encoded[:50]}...")

# Test with Kroki.io
kroki_url = f"https://kroki.io/plantuml/png/{kroki_encoded}"
print(f"\nKroki URL: {kroki_url[:80]}...")

response = requests.get(kroki_url, timeout=10)
print(f"Response status: {response.status_code}")
print(f"Response content type: {response.headers.get('content-type')}")

if response.status_code == 200:
    if 'image' in response.headers.get('content-type', ''):
        print("✅ SUCCESS: Valid PNG image received from Kroki!")
        with open('test_kroki_output.png', 'wb') as f:
            f.write(response.content)
        print("Saved as: test_kroki_output.png")
    else:
        print("❌ ERROR: Response is not an image")
        print(f"Response: {response.text[:200]}")
else:
    print(f"❌ ERROR: HTTP {response.status_code}")
    print(f"Response: {response.text[:200]}")