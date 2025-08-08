#!/usr/bin/env python3
"""Test PlantUML generation directly with thread diagram code"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'functions', 'diagrams'))

from plantuml_generator import PlantUMLGenerator

# PlantUML code from the thread generation
plantuml_code = """@startuml
!theme bluegray
[User] --> [API Gateway];
[API Gateway] --> [Service A];
[API Gateway] --> [Service B];
[Service A] --> [Database];
[Service B] --> [Database];
[Database] --> [API Gateway];
@enduml"""

print("Testing PlantUML with thread diagram code...")
print("="*50)
print(plantuml_code)
print("="*50)

generator = PlantUMLGenerator()

try:
    result = generator.generate_from_content(
        plantuml_code,
        topic="thread_test",
        output_format='png'
    )
    
    if result['success']:
        print(f"✅ SUCCESS: PlantUML diagram generated!")
        print(f"  Path: {result['path']}")
        print(f"  URL: {result['url']}")
        
        # Check file size
        if os.path.exists(result['path']):
            size = os.path.getsize(result['path'])
            print(f"  File size: {size} bytes")
    else:
        print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
        
except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    traceback.print_exc()