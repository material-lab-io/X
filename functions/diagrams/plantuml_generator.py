#!/usr/bin/env python3
"""
PlantUML Diagram Generator Module
Supports dynamic diagram generation from Gemini outputs with local/remote server fallback
Enhanced with automatic style injection for visual improvements
"""

import os
import re
import json
import base64
import requests
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import logging
import zlib

# Import style injector and AI optimizer
try:
    from .style_injector import PlantUMLStyleInjector
except ImportError:
    from style_injector import PlantUMLStyleInjector
    
try:
    from .ai_optimizer import PlantUMLAIOptimizer
except ImportError:
    from ai_optimizer import PlantUMLAIOptimizer

logger = logging.getLogger(__name__)

class PlantUMLGenerator:
    """
    PlantUML diagram generator with support for multiple diagram types
    and dynamic content from AI models
    """
    
    def __init__(self, server_url: str = "http://localhost:8080", fallback_url: str = "http://www.plantuml.com/plantuml"):
        """
        Initialize PlantUML generator with style injection support
        
        Args:
            server_url: Primary PlantUML server URL (local Docker)
            fallback_url: Fallback public PlantUML server
        """
        self.server_url = server_url
        self.fallback_url = fallback_url
        self.output_dir = Path("generated_tweets/diagrams/plantuml")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Create enhanced output directory
        self.enhanced_dir = Path("generated_tweets/diagrams/plantuml/enhanced")
        self.enhanced_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize style injector
        self.style_injector = PlantUMLStyleInjector()
        
        # Initialize AI optimizer
        self.ai_optimizer = PlantUMLAIOptimizer()
        
        # Default style settings
        self.default_theme = 'brand'  # Use brand theme by default
        self.default_layout = 'vertical'
        self.enable_visual_enhancements = False  # Disable for now - causing issues
        self.enable_ai_optimization = False  # Disable AI optimization - it's corrupting service names
        
        # Supported diagram types with their start tags
        self.diagram_types = {
            'class': '@startclass',
            'sequence': '@startsequence', 
            'activity': '@startactivity',
            'component': '@startcomponent',
            'state': '@startstate',
            'usecase': '@startusecase',
            'deployment': '@startdeployment',
            'object': '@startobject',
            'generic': '@startuml'
        }
        
    def _check_server_health(self, url: str) -> bool:
        """Check if PlantUML server is accessible"""
        try:
            response = requests.get(f"{url}/png/SyfFKj2rKt3CoKnELR1Io4ZDoSa70000", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def _get_active_server(self) -> str:
        """Get the active PlantUML server URL"""
        if self._check_server_health(self.server_url):
            logger.info(f"Using local PlantUML server: {self.server_url}")
            return self.server_url
        else:
            logger.warning(f"Local server unavailable, using fallback: {self.fallback_url}")
            return self.fallback_url
    
    def _encode_plantuml_hex(self, text: str) -> str:
        """Encode PlantUML text using hexadecimal encoding (more reliable)"""
        return text.encode('utf-8').hex()
    
    def _encode_plantuml(self, text: str) -> str:
        """Encode PlantUML text for URL using proper DEFLATE encoding"""
        import string
        
        # Step 1: Compress using deflate with maximum compression
        compressed = zlib.compress(text.encode('utf-8'), 9)[2:-4]  # Remove zlib headers and checksum
        
        # Step 2: Custom base64 encoding for PlantUML
        # PlantUML uses a specific alphabet
        encode_table = string.ascii_uppercase + string.ascii_lowercase + string.digits + '-_'
        
        encoded = ''
        for i in range(0, len(compressed), 3):
            if i+2 < len(compressed):
                b1, b2, b3 = compressed[i], compressed[i+1], compressed[i+2]
                encoded += encode_table[b1 >> 2]
                encoded += encode_table[((b1 & 0x3) << 4) | (b2 >> 4)]
                encoded += encode_table[((b2 & 0xF) << 2) | (b3 >> 6)]
                encoded += encode_table[b3 & 0x3F]
            elif i+1 < len(compressed):
                b1, b2 = compressed[i], compressed[i+1]
                encoded += encode_table[b1 >> 2]
                encoded += encode_table[((b1 & 0x3) << 4) | (b2 >> 4)]
                encoded += encode_table[(b2 & 0xF) << 2]
            else:
                b1 = compressed[i]
                encoded += encode_table[b1 >> 2]
                encoded += encode_table[(b1 & 0x3) << 4]
                
        return encoded
    
    def _detect_diagram_type(self, content: str) -> str:
        """Detect the type of PlantUML diagram from content"""
        content_lower = content.lower()
        
        for dtype, start_tag in self.diagram_types.items():
            if start_tag in content_lower:
                return dtype
                
        # Check for specific keywords if no explicit start tag
        if 'class' in content_lower and '->' not in content_lower:
            return 'class'
        elif '->' in content_lower or 'participant' in content_lower:
            return 'sequence'
        elif 'component' in content_lower or '[' in content_lower:
            return 'component'
        elif 'activity' in content_lower or 'start' in content_lower:
            return 'activity'
            
        return 'generic'
    
    def _normalize_plantuml_content(self, content: str) -> str:
        """Normalize and validate PlantUML content"""
        # Remove any existing @startuml/@enduml tags
        content = re.sub(r'@start[a-z]*\s*\n?', '', content, flags=re.IGNORECASE)
        content = re.sub(r'@end[a-z]*\s*\n?', '', content, flags=re.IGNORECASE)
        
        # Clean up the content
        content = content.strip()
        
        # Detect diagram type
        diagram_type = self._detect_diagram_type(content)
        
        # Add only @startuml/@enduml wrapper (PlantUML handles diagram types automatically)
        wrapped = f"@startuml\n{content}\n@enduml"
            
        return wrapped
    
    def generate_from_content(self, content: str, topic: str = None, 
                            output_format: str = 'png', theme: str = None,
                            layout: str = None, enable_icons: bool = None,
                            optimize_layout: bool = None) -> Dict[str, Any]:
        """
        Generate PlantUML diagram from content with optional visual enhancements
        
        Args:
            content: PlantUML diagram content (from Gemini or user)
            topic: Optional topic for filename generation
            output_format: Output format (png, svg, txt)
            theme: Visual theme to apply (dark/light/brand)
            layout: Layout orientation (vertical/horizontal)
            enable_icons: Whether to include icon libraries
            
        Returns:
            Dict with diagram info including path, URL, and metadata
        """
        try:
            # Normalize the content
            normalized_content = self._normalize_plantuml_content(content)
            
            # Detect diagram type
            diagram_type = self._detect_diagram_type(normalized_content)
            
            # Apply AI optimization if enabled
            optimize_layout = optimize_layout if optimize_layout is not None else self.enable_ai_optimization
            optimization_result = None
            
            if optimize_layout:
                try:
                    optimization_result = self.ai_optimizer.optimize(normalized_content, topic)
                    if optimization_result['improved']:
                        normalized_content = optimization_result['optimized']
                        logger.info(f"AI optimization applied: {optimization_result['optimizations']}")
                except Exception as e:
                    logger.warning(f"AI optimization failed: {e}")
                    # Continue without optimization
            
            # Apply visual enhancements if enabled
            if self.enable_visual_enhancements:
                theme = theme or self.default_theme
                layout = layout or self.default_layout
                enable_icons = enable_icons if enable_icons is not None else True
                
                # Inject styles
                enhanced_content = self.style_injector.inject_styles(
                    normalized_content,
                    theme=theme,
                    layout=layout,
                    enable_icons=enable_icons,
                    diagram_type=diagram_type
                )
                
                # Use enhanced content for generation
                content_to_render = enhanced_content
                use_enhanced_dir = True
            else:
                content_to_render = normalized_content
                use_enhanced_dir = False
            
            # Get active server
            server = self._get_active_server()
            
            # For plantuml.com, use hex encoding which is more reliable
            if "plantuml.com" in server:
                # Use hexadecimal encoding for plantuml.com
                encoded = self._encode_plantuml_hex(content_to_render)
                use_hex = True
            else:
                # Use standard encoding for local servers
                encoded = self._encode_plantuml(content_to_render)
                use_hex = False
            
            # For plantuml.com, use hex-encoded URL directly (most reliable)
            if "plantuml.com" in server:
                # Ensure content has @startuml/@enduml tags
                if not content_to_render.strip().startswith('@startuml'):
                    content_to_render = '@startuml\n' + content_to_render
                if not content_to_render.strip().endswith('@enduml'):
                    content_to_render = content_to_render + '\n@enduml'
                
                # PlantUML.com supports themes but they need to be lowercase
                import re
                theme_match = re.search(r'!theme\s+(\w+)', content_to_render)
                if theme_match:
                    theme_name = theme_match.group(1).lower()
                    content_to_render = re.sub(r'!theme\s+\w+', f'!theme {theme_name}', content_to_render)
                
                # Re-encode with the potentially modified content
                encoded = self._encode_plantuml_hex(content_to_render)
                
                # Use hex-encoded URL directly (most reliable method for plantuml.com)
                diagram_url = f"{server}/{output_format}/~h{encoded}"
            else:
                # For local server, use standard encoding without prefix
                diagram_url = f"{server}/{output_format}/{encoded}"
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            topic_slug = re.sub(r'[^a-zA-Z0-9]+', '_', topic or 'diagram')[:30]
            
            # Add theme and optimization to filename if enhanced
            if use_enhanced_dir:
                if optimize_layout and optimization_result and optimization_result['improved']:
                    # Save to optimized directory
                    optimized_dir = Path("generated_tweets/diagrams/plantuml/optimized")
                    optimized_dir.mkdir(parents=True, exist_ok=True)
                    filename = f"plantuml_{diagram_type}_{theme}_optimized_{topic_slug}_{timestamp}.{output_format}"
                    filepath = optimized_dir / filename
                else:
                    filename = f"plantuml_{diagram_type}_{theme}_{topic_slug}_{timestamp}.{output_format}"
                    filepath = self.enhanced_dir / filename
            else:
                filename = f"plantuml_{diagram_type}_{topic_slug}_{timestamp}.{output_format}"
                filepath = self.output_dir / filename
            
            # Download and save diagram
            response = requests.get(diagram_url, timeout=10)
            response.raise_for_status()
            
            # Check if the response is actually an image
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type.lower():
                logger.error(f"PlantUML server returned non-image content: {content_type}")
                # Try to extract error message if it's HTML
                if 'html' in content_type.lower():
                    import re
                    error_match = re.search(r'<body[^>]*>(.*?)</body>', response.text, re.DOTALL)
                    if error_match:
                        logger.error(f"PlantUML error: {error_match.group(1)[:500]}")
                return {
                    'success': False,
                    'error': 'PlantUML server returned non-image content',
                    'content_type': content_type
                }
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"PlantUML diagram saved: {filepath}")
            
            result = {
                'success': True,
                'path': str(filepath),
                'filename': filename,
                'url': diagram_url,
                'type': diagram_type,
                'content': normalized_content,
                'format': output_format,
                'server': server,
                'timestamp': timestamp
            }
            
            # Add style information if enhanced
            if use_enhanced_dir:
                result.update({
                    'enhanced': True,
                    'theme': theme,
                    'layout': layout,
                    'icons_enabled': enable_icons,
                    'enhanced_content': content_to_render
                })
            
            # Add optimization information
            if optimization_result and optimization_result['improved']:
                result.update({
                    'optimized': True,
                    'optimizations': optimization_result['optimizations'],
                    'optimization_report': optimization_result
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating PlantUML diagram: {e}")
            return {
                'success': False,
                'error': str(e),
                'content': content
            }
    
    def generate_from_prompt(self, prompt: str, diagram_type: str = 'auto') -> Dict[str, Any]:
        """
        Generate PlantUML diagram from a natural language prompt
        This will be called after Gemini generates the PlantUML code
        
        Args:
            prompt: Natural language description or PlantUML code from Gemini
            diagram_type: Type of diagram to generate
            
        Returns:
            Dict with diagram info
        """
        # Check if prompt already contains PlantUML code
        if '@start' in prompt or '->' in prompt or 'class' in prompt.lower():
            # It's already PlantUML code from Gemini
            return self.generate_from_content(prompt)
        else:
            # It's a description that needs to be converted
            # This would normally go through Gemini first
            logger.warning("Received description instead of PlantUML code. Please use Gemini to generate PlantUML first.")
            return {
                'success': False,
                'error': 'PlantUML code required. Please generate with Gemini first.',
                'prompt': prompt
            }
    
    def parse_plantuml_blocks(self, text: str) -> List[str]:
        """
        Extract PlantUML code blocks from text
        Handles various formats including markdown code blocks
        
        Args:
            text: Text containing PlantUML blocks
            
        Returns:
            List of PlantUML code blocks
        """
        blocks = []
        
        # Pattern 1: @startuml...@enduml blocks
        pattern1 = r'@start[a-z]*.*?@end[a-z]*'
        matches1 = re.findall(pattern1, text, re.DOTALL | re.IGNORECASE)
        blocks.extend(matches1)
        
        # Pattern 2: ```plantuml...``` markdown blocks
        pattern2 = r'```plantuml\s*(.*?)```'
        matches2 = re.findall(pattern2, text, re.DOTALL)
        blocks.extend(matches2)
        
        # Pattern 3: ```uml...``` or ```puml...``` blocks
        pattern3 = r'```(?:uml|puml)\s*(.*?)```'
        matches3 = re.findall(pattern3, text, re.DOTALL)
        blocks.extend(matches3)
        
        return blocks
    
    def batch_generate(self, contents: List[str], topics: List[str] = None) -> List[Dict[str, Any]]:
        """
        Generate multiple PlantUML diagrams in batch
        
        Args:
            contents: List of PlantUML contents
            topics: Optional list of topics for naming
            
        Returns:
            List of generation results
        """
        results = []
        topics = topics or [None] * len(contents)
        
        for content, topic in zip(contents, topics):
            result = self.generate_from_content(content, topic)
            results.append(result)
            
        return results
    
    def get_sample_diagrams(self) -> Dict[str, str]:
        """
        Get sample PlantUML code for different diagram types
        These are templates that can be modified by Gemini
        """
        return {
            'sequence': """
participant Client
participant Server
participant Database

Client -> Server: Request
Server -> Database: Query
Database --> Server: Result
Server --> Client: Response
            """,
            
            'class': """
class User {
  -id: Long
  -email: String
  +login()
  +logout()
}

class Order {
  -id: Long
  -status: String
  +process()
}

User "1" --> "*" Order : places
            """,
            
            'component': """
component [Web Server] as WS
component [Application] as App
component [Database] as DB

WS --> App : HTTP
App --> DB : SQL
            """,
            
            'activity': """
start
:Initialize;
if (Check condition?) then (yes)
  :Process A;
else (no)
  :Process B;
endif
:Finalize;
stop
            """
        }


# Standalone testing
if __name__ == "__main__":
    generator = PlantUMLGenerator()
    
    # Test with a simple sequence diagram
    test_content = """
    Alice -> Bob: Hello
    Bob --> Alice: Hi there!
    """
    
    result = generator.generate_from_content(test_content, "test_sequence")
    
    if result['success']:
        print(f"✅ Diagram generated: {result['path']}")
        print(f"   Type: {result['type']}")
        print(f"   Server: {result['server']}")
    else:
        print(f"❌ Generation failed: {result['error']}")