#!/usr/bin/env python3
"""Test PlantUML generation without Docker - using public PlantUML server"""

from gemini_dynamic_generator import GeminiDynamicGenerator

# Test PlantUML generation using public server
generator = GeminiDynamicGenerator("AIzaSyC2ZSm7_G9TxUSSrGaOJ2x0ouTDGhGyd9s")

# Simple PlantUML code
plantuml_code = """@startuml
Alice -> Bob: Hello
Bob --> Alice: Hi!
@enduml"""

print("Testing PlantUML generation...")
print(f"Code: {plantuml_code}")

# Use public PlantUML server for testing
result = generator.generate_plantuml_diagram(plantuml_code, "http://www.plantuml.com/plantuml")

if result:
    print(f"✅ Success! Diagram saved to: {result}")
else:
    print("❌ Failed to generate PlantUML diagram")

# Test the full content generation with PlantUML
print("\n\nTesting full content generation with PlantUML...")
from gemini_dynamic_generator import generate_dynamic_content

content = generate_dynamic_content(
    topic="Microservices authentication flow",
    content_type="single",
    template="Conceptual Deep Dive",
    context="Show OAuth2 flow with PlantUML sequence diagram",
    diagram_type="plantuml"
)

print("\nGenerated content:")
import json
print(json.dumps(content, indent=2))