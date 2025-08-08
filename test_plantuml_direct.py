#!/usr/bin/env python3
"""Test PlantUML generation directly"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'functions', 'diagrams'))

from plantuml_generator import PlantUMLGenerator

# Simple PlantUML code for microservices
plantuml_code = """@startuml
!theme bluegray

actor User
component "API Gateway" as GW
component "Order Service" as OS
component "Inventory Service" as IS
component "Payment Service" as PS
queue "Kafka" as K

User -> GW : Request
GW -> OS : REST
OS -> K : Publish Event
K -> IS : Consume Event
K -> PS : Consume Event

note right of K
  Event-driven
  communication
end note

@enduml"""

print("Testing PlantUML generation with clean code...")
print("="*50)
print("PlantUML Code:")
print(plantuml_code)
print("="*50)

# Initialize generator
generator = PlantUMLGenerator()

# Generate diagram
try:
    result = generator.generate_from_content(
        plantuml_code,
        topic="microservices_test",
        output_format='png'
    )
    
    if result['success']:
        print(f"✅ SUCCESS: Diagram generated!")
        print(f"  Path: {result['path']}")
        print(f"  URL: {result['url']}")
        print(f"  Type: {result['type']}")
        
        # Check if file exists and is valid
        if os.path.exists(result['path']):
            size = os.path.getsize(result['path'])
            print(f"  File size: {size} bytes")
            
            # Check if it's a PNG
            with open(result['path'], 'rb') as f:
                header = f.read(8)
                if header.startswith(b'\x89PNG'):
                    print("  ✅ Valid PNG file!")
                else:
                    print(f"  ❌ Not a PNG file (header: {header.hex()})")
    else:
        print(f"❌ FAILED: {result.get('error', 'Unknown error')}")
        
except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    traceback.print_exc()