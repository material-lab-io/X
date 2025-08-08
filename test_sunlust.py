#!/usr/bin/env python3
"""Test Sunlust theme issue"""

import base64
import zlib
import requests

# Test PlantUML with Sunlust theme
test_code = """@startuml
!theme Sunlust
participant Client
participant Server
Client -> Server: Request
Server -> Client: Response
@enduml"""

print('Testing Sunlust theme...')
print('PlantUML code:')
print(test_code)

# Test with Kroki
compressed = zlib.compress(test_code.encode('utf-8'), 9)
kroki_encoded = base64.urlsafe_b64encode(compressed).decode('ascii').rstrip('=')

url = f'https://kroki.io/plantuml/png/{kroki_encoded}'
print(f'\nKroki URL: {url[:80]}...')

try:
    response = requests.get(url, timeout=10)
    print(f'Response status: {response.status_code}')
    print(f'Content type: {response.headers.get("content-type")}')
    
    if response.status_code == 200 and 'image' in response.headers.get('content-type', ''):
        print('✅ Sunlust theme works!')
        with open('sunlust_test.png', 'wb') as f:
            f.write(response.content)
        print('Saved as sunlust_test.png')
    else:
        print('❌ Sunlust theme failed')
        if response.status_code != 200:
            print(f'Error response: {response.text[:500]}')
except Exception as e:
    print(f'Error: {e}')