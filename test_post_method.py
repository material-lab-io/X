#!/usr/bin/env python3
"""Test PlantUML POST method with themes"""

import requests

# Test with sunlust theme
test_code = """@startuml
!theme sunlust
participant Client
participant Server
Client -> Server: Request
Server -> Client: Response
@enduml"""

print('Testing PlantUML POST method with sunlust theme...')
print('PlantUML code:')
print(test_code)
print()

# Use POST method
post_url = "http://www.plantuml.com/plantuml/png"

try:
    response = requests.post(
        post_url,
        data={'text': test_code},
        timeout=15
    )
    
    print(f'Response status: {response.status_code}')
    print(f'Content type: {response.headers.get("content-type")}')
    print(f'Content length: {len(response.content)} bytes')
    
    if response.status_code == 200 and response.content:
        # Save the image
        with open('sunlust_post_test.png', 'wb') as f:
            f.write(response.content)
        
        if len(response.content) > 1000:
            print('✅ SUCCESS! PlantUML generated with sunlust theme via POST')
            print('Saved as: sunlust_post_test.png')
        else:
            print('⚠️ Small file size - might be an error image')
            # Check first few bytes
            if response.content[:4] == b'\x89PNG':
                print('It is a PNG file')
    else:
        print(f'❌ Failed with status {response.status_code}')
        
except Exception as e:
    print(f'❌ Error: {e}')