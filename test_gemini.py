#!/usr/bin/env python3
"""Test Gemini generator"""

import json
from gemini_dynamic_generator import generate_dynamic_content

# Test generation
result = generate_dynamic_content(
    topic="The real difference between Docker and Podman",
    content_type="thread",
    template="Conceptual Deep Dive",
    context="Focus on technical architecture differences",
    api_key="AIzaSyC2ZSm7_G9TxUSSrGaOJ2x0ouTDGhGyd9s"
)

print("Generated content:")
print(json.dumps(result, indent=2))