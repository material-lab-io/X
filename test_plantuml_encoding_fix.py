#!/usr/bin/env python3
"""Test the fixed PlantUML encoding"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from functions.diagrams.plantuml_generator import PlantUMLGenerator

def test_encoding():
    """Test that the PlantUML encoding works correctly"""
    
    # Initialize generator
    generator = PlantUMLGenerator()
    
    # Test PlantUML content
    test_content = """
    participant Client
    participant Server
    Client -> Server: Request
    Server -> Client: Response
    """
    
    print("Testing PlantUML encoding fix...")
    print("="*50)
    print("Test content:")
    print(test_content)
    print("="*50)
    
    # Test the encoding
    encoded = generator._encode_plantuml(test_content)
    print(f"Encoded string (first 50 chars): {encoded[:50]}...")
    print(f"Encoded length: {len(encoded)}")
    
    # Test URL generation
    server = "http://www.plantuml.com/plantuml"
    url_with_header = f"{server}/png/~1{encoded}"
    url_without_header = f"{server}/png/{encoded}"
    
    print(f"\nURL with HUFFMAN header (~1): {url_with_header[:80]}...")
    print(f"URL without header: {url_without_header[:80]}...")
    
    # Test generation with the fixed encoding
    print("\n" + "="*50)
    print("Testing full generation pipeline...")
    
    try:
        result = generator.generate_from_content(
            test_content,
            topic="test_encoding",
            output_format='png',
            theme='default'
        )
        
        if result['success']:
            print("✅ SUCCESS: Diagram generated successfully!")
            print(f"File saved to: {result['path']}")
            print(f"Backup URL: {result['url']}")
        else:
            print("❌ FAILED: Generation failed")
            print(result)
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_encoding()