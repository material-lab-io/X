#!/usr/bin/env python3
"""Test Gemini API key"""

import google.generativeai as genai

# Read API key from config
import json
with open('config.json', 'r') as f:
    config = json.load(f)
    api_key = config['api_keys']['gemini']

print(f"Testing Gemini API key: {api_key[:10]}...")

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Simple test prompt
    response = model.generate_content("Say 'API key is working!' if you can read this.")
    print(f"✅ API Response: {response.text}")
    print("API key is valid and working!")
    
except Exception as e:
    print(f"❌ API Error: {e}")
    print("API key may be invalid or there's a connection issue")