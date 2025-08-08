#!/usr/bin/env python3
"""Test generation for Hardik Tatta platform launch"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'functions', 'generators'))

from gemini_dynamic_generator import GeminiDynamicGenerator

# Initialize generator
api_key = "AIzaSyBav2kap2T_sUDsE5M1XxOsEsgTKSXNTbM"
generator = GeminiDynamicGenerator(api_key)

# Test topic and context
topic = "Announcing the official launch of our new social media and hiring platform"
context = """Platform: Hardik Tatta - Social networking meets smart hiring
Core: Authentic connections + powerful hiring tools. Build real relationships, not just browse job listings.
Differentiator: Anti-corporate networking. Professional growth through genuine community.
Audience: Job seekers, recruiters, professionals
Tone: Bold, energetic, exciting
CTA: Join us today! Build your future
Visuals: Launch video/logo splash/interface GIF"""

print("Testing generation for Hardik Tatta platform...")
print("="*60)
print(f"Topic: {topic}")
print(f"Context provided: Yes")
print("="*60)

try:
    # Generate content
    result = generator.generate_content(
        topic=topic,
        content_type="thread",
        template="Real World Scenario",
        context=context,
        diagram_type="mermaid"
    )
    
    print(f"\nResult keys: {list(result.keys())}")
    
    if 'error' in result:
        print(f"❌ ERROR: {result['error']}")
        if 'tweets' in result:
            print(f"Fallback content: {result['tweets'][0]['content']}")
    elif 'tweets' in result:
        print(f"✅ SUCCESS: Generated {len(result['tweets'])} tweets")
        print("\nGenerated tweets:")
        for i, tweet in enumerate(result['tweets'], 1):
            print(f"\nTweet {i}:")
            print(f"{tweet['content']}")
            print(f"({tweet['character_count']} chars)")
    else:
        print("❌ Unexpected result structure")
        
except Exception as e:
    print(f"❌ Exception: {e}")
    import traceback
    traceback.print_exc()