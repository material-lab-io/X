#!/usr/bin/env python3
"""Test the fixed PlantUML encoding with simple content"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from functions.diagrams.plantuml_generator import PlantUMLGenerator

def test_simple():
    """Test PlantUML with simple content"""
    
    # Initialize generator
    generator = PlantUMLGenerator()
    
    # Disable visual enhancements for testing
    generator.enable_visual_enhancements = False
    generator.enable_ai_optimization = False
    
    # Simple test content
    test_content = """
    Alice -> Bob: Hello
    Bob -> Alice: Hi!
    """
    
    print("Testing simplified PlantUML generation...")
    print("Test content:")
    print(test_content)
    print("="*50)
    
    try:
        result = generator.generate_from_content(
            test_content,
            topic="simple_test",
            output_format='png'
        )
        
        if result['success']:
            print("✅ SUCCESS: Diagram generated successfully!")
            print(f"File saved to: {result['path']}")
            print(f"URL: {result['url']}")
            
            # Check if file is actually an image
            import os
            if os.path.exists(result['path']):
                size = os.path.getsize(result['path'])
                print(f"File size: {size} bytes")
                
                # Check file type
                with open(result['path'], 'rb') as f:
                    header = f.read(8)
                    if header.startswith(b'\x89PNG'):
                        print("✅ File is a valid PNG image")
                    else:
                        print(f"❌ File header: {header.hex()}")
        else:
            print("❌ FAILED: Generation failed")
            print(result)
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple()