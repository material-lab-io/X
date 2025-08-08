#!/usr/bin/env python3
"""List available Gemini models"""

import google.generativeai as genai

# Configure with API key
api_key = "AIzaSyB7i99R6V4BqB79lQ_VsWrmrAmqgkRhnKU"
genai.configure(api_key=api_key)

# List all available models
print("Available Gemini models:")
print("=" * 60)

for model in genai.list_models():
    print(f"\nModel: {model.name}")
    print(f"  Display name: {model.display_name}")
    print(f"  Supported methods: {', '.join(model.supported_generation_methods)}")
    if hasattr(model, 'description'):
        print(f"  Description: {model.description}")