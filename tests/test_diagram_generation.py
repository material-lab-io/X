#!/usr/bin/env python3
"""Test diagram generation directly"""

from gemini_dynamic_generator import generate_dynamic_content
import json

print("Testing diagram generation with both types...")

# Test with both diagram types
result = generate_dynamic_content(
    topic="Docker containers",
    content_type="single",
    template="Conceptual Deep Dive",
    context="",
    diagram_type="both"
)

print("\nResult keys:", list(result.keys()))
if 'diagram' in result:
    print("Diagram keys:", list(result['diagram'].keys()))
    print("Has mermaid_image_path:", 'mermaid_image_path' in result['diagram'])
    print("Has plantuml_image_path:", 'plantuml_image_path' in result['diagram'])
    
    if 'mermaid_image_path' in result['diagram']:
        print(f"Mermaid image: {result['diagram']['mermaid_image_path']}")
    if 'plantuml_image_path' in result['diagram']:
        print(f"PlantUML image: {result['diagram']['plantuml_image_path']}")

print("\nFull result:")
print(json.dumps(result, indent=2))