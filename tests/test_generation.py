#!/usr/bin/env python3
"""Test content generation directly"""

import json
from gemini_dynamic_generator import GeminiDynamicGenerator

def test_generation():
    print("Testing content generation...")
    
    # Initialize generator with API key
    api_key = "AIzaSyAMOvO0_b0o5LdvZgZBVqZ3mSfBwBukzgY"
    gen = GeminiDynamicGenerator(api_key)
    
    # Test content generation
    print("\n1. Testing content generation...")
    result = gen.generate_content(
        topic="Docker architecture",
        content_type="thread",
        template="Conceptual Deep Dive"
    )
    print(f"Result: {json.dumps(result, indent=2)[:500]}...")
    
    print("\nTest complete!")

if __name__ == "__main__":
    test_generation()