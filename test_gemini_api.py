#!/usr/bin/env python3
"""Test Gemini API directly"""

import google.generativeai as genai

# Configure API
genai.configure(api_key="AIzaSyC2ZSm7_G9TxUSSrGaOJ2x0ouTDGhGyd9s")
model = genai.GenerativeModel('gemini-1.5-flash')

# Simple test
try:
    print("Testing Gemini API...")
    response = model.generate_content("Say hello in 5 words")
    print(f"Response: {response.text}")
    print("✅ API is working!")
except Exception as e:
    print(f"❌ API Error: {e}")
    import traceback
    traceback.print_exc()

# Test with our prompt format
try:
    print("\n\nTesting with tweet generation prompt...")
    prompt = """Generate a single tweet about Docker containers.
    Format: {"tweet": {"content": "text", "character_count": N}}
    Output valid JSON only."""
    
    response = model.generate_content(prompt)
    print(f"Response: {response.text}")
    
    # Try to parse
    import json
    data = json.loads(response.text.strip())
    print(f"✅ Parsed successfully: {data}")
    
except Exception as e:
    print(f"❌ Generation Error: {e}")
    import traceback
    traceback.print_exc()