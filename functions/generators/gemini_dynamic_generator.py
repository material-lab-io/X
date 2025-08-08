#!/usr/bin/env python3
"""
Dynamic tweet generator using Gemini API for real-time content generation
Generates high-quality technical content with optional Mermaid or PlantUML diagrams
"""

import json
import google.generativeai as genai
from datetime import datetime
from pathlib import Path
import re
import subprocess
import base64
import os
import sys
import requests
import urllib.parse
from typing import Dict, List, Optional, Tuple

# Add path for diagram generators
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'diagrams'))

class GeminiDynamicGenerator:
    def __init__(self, api_key: str):
        """Initialize with Gemini API key"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Initialize PlantUML generator
        try:
            from plantuml_generator import PlantUMLGenerator
            self.plantuml_generator = PlantUMLGenerator()
        except ImportError:
            print("Warning: PlantUML generator not available")
            self.plantuml_generator = None
        
    def generate_content(self, topic: str, content_type: str, template: str, context: str = "", diagram_type: str = "mermaid", auto_theme: bool = True, manual_theme: str = None) -> Dict:
        """Generate dynamic content using Gemini API"""
        
        # Build the prompt based on template
        prompt = self._build_prompt(topic, content_type, template, context, diagram_type)
        
        try:
            # Generate content
            response = self.model.generate_content(prompt)
            print(f"[DEBUG] Gemini raw response length: {len(response.text)}")
            print(f"[DEBUG] Gemini response preview: {response.text[:200]}...")
            
            # Parse the response
            content_data = self._parse_gemini_response(response.text, content_type)
            
            # Inject PlantUML theme if PlantUML diagram exists
            if diagram_type in ["plantuml", "both"]:
                if "diagram" in content_data and content_data["diagram"]:
                    if "plantuml_code" in content_data["diagram"]:
                        plantuml_code = content_data["diagram"]["plantuml_code"]
                        import re
                        
                        # Remove any existing theme directive
                        plantuml_code = re.sub(r'!theme\s+\w+\s*\n?', '', plantuml_code)
                        
                        if manual_theme:
                            # Use manually selected theme
                            theme_name = manual_theme
                            theme_desc = f"Manually selected theme: {manual_theme}"
                            print(f"[DEBUG] Using manual PlantUML theme: {theme_name}")
                        elif auto_theme:
                            # Auto-select theme based on topic and context
                            try:
                                from auto_theme_selector import auto_select_theme
                                theme_name, theme_desc = auto_select_theme(topic, context)
                                print(f"[DEBUG] Auto-selected PlantUML theme: {theme_name} - {theme_desc}")
                            except ImportError:
                                print("[DEBUG] Auto theme selector not available, using default")
                                theme_name = "plain"
                                theme_desc = "Default theme"
                        else:
                            # No theme selected
                            theme_name = "plain"
                            theme_desc = "Default theme"
                        
                        # Add selected theme after @startuml
                        if plantuml_code.strip().startswith('@startuml'):
                            plantuml_code = plantuml_code.replace('@startuml', f'@startuml\n!theme {theme_name}', 1)
                        else:
                            plantuml_code = f'@startuml\n!theme {theme_name}\n{plantuml_code}\n@enduml'
                        
                        content_data["diagram"]["plantuml_code"] = plantuml_code
                        content_data["diagram"]["theme"] = theme_name
                        content_data["diagram"]["theme_description"] = theme_desc
            
            # Add metadata
            content_data.update({
                "topic": topic,
                "content_type": content_type,
                "template": template,
                "generated_at": datetime.now().isoformat(),
                "generator": "gemini_dynamic"
            })
            
            return content_data
            
        except Exception as e:
            print(f"Error generating content: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_response(topic, content_type)
    
    def _build_prompt(self, topic: str, content_type: str, template: str, context: str, diagram_type: str = "mermaid") -> str:
        """Build detailed prompt for Gemini"""
        
        base_prompt = f"""You are a technical content expert creating Twitter/X posts for developers and technical founders.

Topic: {topic}
Content Type: {content_type}
Template Style: {template}
Additional Context: {context if context else "None provided"}

Requirements:
1. Generate technically deep, insightful content
2. Each tweet must be 180-260 characters (count precisely)
3. Use authentic technical language, not marketing speak
4. Include specific examples, tools, or commands where relevant
5. For threads: number tweets as n/N format
6. Start threads with compelling hooks
7. End threads with actionable CTAs

"""
        
        if content_type == "thread":
            base_prompt += """Thread Requirements:
- Generate 5-10 tweets maximum
- Each tweet must be self-contained but connected
- Include technical depth in each tweet
- Use bullets (•), emojis strategically
- Format: {"tweets": [{"position": 1, "content": "text", "character_count": N}]}

"""
        else:
            base_prompt += """Single Post Requirements:
- One powerful, complete thought
- Include specific technical insight
- Format: {"tweet": {"content": "text", "character_count": N}}

"""
        
        # Template-specific instructions
        template_prompts = {
            "Problem/Solution": """Focus on:
- Real problem you encountered
- Specific solution with code/config
- Measurable outcome
- Learning for others
""",
            "Conceptual Deep Dive": """Focus on:
- Core technical concept explanation
- Why it matters for builders
- Implementation details
- Common misconceptions
""",
            "Workflow/Tool Share": """Focus on:
- Specific workflow or tool usage
- Step-by-step if applicable
- Time/efficiency gains
- Integration tips
"""
        }
        
        base_prompt += template_prompts.get(template, "")
        
        # Diagram instructions based on type
        if diagram_type == "plantuml":
            base_prompt += """
Diagram Generation:
For technical concepts that benefit from visualization, generate a PlantUML diagram.

PlantUML Rules:
1. Start with @startuml and end with @enduml
2. Do NOT include theme directives (!theme) - these will be added automatically
3. Do NOT include URLs or comments starting with 'http'
4. Use proper component syntax: [ComponentName] for components
5. Use proper queue/database syntax: database "Name" as alias OR queue "Name" as alias
6. NEVER use semicolons (;) at the end of lines - PlantUML doesn't need them

Valid PlantUML examples (NO SEMICOLONS):
- Component: @startuml\n[Order Service] --> [Kafka]\n[Kafka] --> [Payment Service]\n@enduml
- With actors: @startuml\nactor User\nUser -> [API Gateway]\n[API Gateway] -> [Service]\n@enduml
- With queue: @startuml\nqueue "Kafka" as K\n[Service1] -> K\nK -> [Service2]\n@enduml

Format: {"diagram": {"plantuml_code": "@startuml\\n...\\n@enduml", "tweet_position": N}}
"""
        elif diagram_type == "both":
            base_prompt += """
Diagram Generation:
Generate BOTH Mermaid and PlantUML diagrams for the same concept.

PlantUML Rules:
- Start with @startuml and end with @enduml
- NO theme directives or URLs
- Use [ComponentName] for components
- Use queue "Name" as alias for message queues
- NO SEMICOLONS at end of lines

Mermaid Rules:
- Use graph TD or graph LR
- Proper node syntax: A[Label]

Format: {"diagram": {
  "mermaid_code": "graph TD\\nA[Service1] --> B[Service2]",
  "plantuml_code": "@startuml\\n[Service1] --> [Service2]\\n@enduml",
  "tweet_position": N
}}
"""
        else:  # default to mermaid
            base_prompt += """
Diagram Generation:
For technical concepts that benefit from visualization (architecture comparisons, workflows, relationships):
1. Include a Mermaid.js diagram that clarifies the concept
2. Attach it to the most relevant tweet position
3. Keep diagrams simple and focused
4. Use appropriate diagram types (flowchart for processes, graph for relationships)

Format: {"diagram": {"mermaid_code": "graph TD\\n...", "tweet_position": N}}
"""
        
        base_prompt += """
For single tweets: tweet_position = 1
For threads: choose the tweet that best explains the visual concept

Example scenarios that benefit from diagrams:
- Architecture comparisons
- Data flow illustrations
- Process workflows
- System relationships

Output valid JSON only. No markdown formatting around the JSON.
"""
        
        return base_prompt
    
    def _parse_gemini_response(self, response_text: str, content_type: str) -> Dict:
        """Parse Gemini response into structured format"""
        try:
            # Clean response - remove markdown code blocks if present
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            # Fix common Gemini formatting issues
            # Replace position: X/Y with position: X
            import re
            cleaned = re.sub(r'"position":\s*(\d+)/\d+', r'"position": \1', cleaned)
            
            # Parse JSON
            data = json.loads(cleaned.strip())
            
            # Validate and clean data
            if content_type == "thread":
                if "tweets" in data:
                    # Ensure character counts are accurate and position is integer
                    for tweet in data["tweets"]:
                        tweet["character_count"] = len(tweet["content"])
                        # Ensure position is an integer
                        if "position" in tweet:
                            tweet["position"] = int(tweet["position"])
                else:
                    raise ValueError("No tweets found in response")
            else:
                if "tweet" in data:
                    data["tweet"]["character_count"] = len(data["tweet"]["content"])
                else:
                    raise ValueError("No tweet found in response")
            
            return data
            
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Error parsing Gemini response: {e}")
            print(f"Raw response: {response_text[:500]}...")
            print(f"Content type: {content_type}")
            return self._fallback_response("", content_type)
    
    def _fallback_response(self, topic: str, content_type: str) -> Dict:
        """Fallback response if generation fails"""
        if content_type == "thread":
            return {
                "tweets": [
                    {
                        "position": 1,
                        "content": f"Exploring {topic} - Thread generation in progress...",
                        "character_count": 50
                    }
                ],
                "error": "Generation failed - using fallback"
            }
        else:
            return {
                "tweet": {
                    "content": f"Insights on {topic} coming soon...",
                    "character_count": 35
                },
                "error": "Generation failed - using fallback"
            }
    
    def generate_diagram(self, mermaid_code: str) -> Optional[str]:
        """Generate PNG from Mermaid code"""
        try:
            print(f"Generating diagram from Mermaid code: {mermaid_code[:50]}...")
            # Save Mermaid code to temp file
            temp_mmd = Path("temp_diagram.mmd")
            temp_mmd.write_text(mermaid_code)
            
            # Generate PNG using mmdc (mermaid CLI)
            output_path = Path("generated_tweets/diagrams")
            output_path.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            png_path = output_path / f"diagram_{timestamp}.png"
            
            # Run mermaid CLI with no-sandbox for server environments
            result = subprocess.run([
                "mmdc", "-i", str(temp_mmd), "-o", str(png_path),
                "-t", "dark", "-b", "transparent", "-p", "puppeteer-config.json"
            ], capture_output=True, text=True, env={**os.environ, "PUPPETEER_ARGS": "--no-sandbox --disable-setuid-sandbox"})
            
            if result.returncode == 0:
                temp_mmd.unlink()  # Clean up
                print(f"✅ Diagram generated successfully: {png_path}")
                return str(png_path)
            else:
                print(f"❌ Mermaid generation failed: {result.stderr}")
                print(f"Command was: mmdc -i {temp_mmd} -o {png_path}")
                return None
                
        except Exception as e:
            print(f"❌ Error generating diagram: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def generate_plantuml_diagram(self, plantuml_code: str, topic: str = None) -> Optional[str]:
        """Generate PNG from PlantUML code using the new PlantUML generator"""
        if not self.plantuml_generator:
            print("Warning: PlantUML generator not initialized, using fallback method")
            return self._generate_plantuml_fallback(plantuml_code)
        
        try:
            print(f"Generating PlantUML diagram for topic: {topic}")
            result = self.plantuml_generator.generate_from_content(
                content=plantuml_code,
                topic=topic,
                output_format='png'
            )
            
            if result['success']:
                print(f"✅ PlantUML diagram generated: {result['path']}")
                return result['path']
            else:
                print(f"❌ PlantUML generation failed: {result.get('error')}")
                return self._generate_plantuml_fallback(plantuml_code)
                
        except Exception as e:
            print(f"Error generating PlantUML: {e}")
            return self._generate_plantuml_fallback(plantuml_code)
    
    def _generate_plantuml_fallback(self, plantuml_code: str) -> Optional[str]:
        """Fallback method using direct server calls"""
        try:
            # Try local server first, then fallback to Kroki.io
            servers = ["http://localhost:8080", "https://kroki.io"]
            
            for server in servers:
                try:
                    print(f"Trying PlantUML server: {server}")
                    if "kroki.io" in server:
                        result = self._generate_plantuml_with_kroki(plantuml_code)
                    else:
                        result = self._generate_plantuml_with_server(plantuml_code, server)
                    if result:
                        return result
                except Exception as e:
                    print(f"Server {server} failed: {e}")
                    continue
            
            print("❌ All PlantUML servers failed")
            return None
                
        except Exception as e:
            print(f"❌ Error in PlantUML generation: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _generate_plantuml_with_server(self, plantuml_code: str, server_url: str) -> Optional[str]:
        """Helper method to generate PlantUML with a specific server"""
        try:
            
            # Ensure PlantUML code is properly formatted
            if not plantuml_code.strip().startswith('@startuml'):
                plantuml_code = '@startuml\n' + plantuml_code
            if not plantuml_code.strip().endswith('@enduml'):
                plantuml_code = plantuml_code + '\n@enduml'
            
            # For public PlantUML server, use form submission
            if "plantuml.com" in server_url:
                # Use form-based API for public server
                form_url = f"{server_url}/form"
                form_data = {
                    'text': plantuml_code,
                    'url': '',
                    'fmt': 'png',
                    'index': '0'
                }
                response = requests.post(form_url, data=form_data, timeout=15)
                
                if response.status_code == 200 and response.content:
                    # Save PNG
                    output_path = Path("generated_tweets/diagrams/plantuml")
                    output_path.mkdir(parents=True, exist_ok=True)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    png_path = output_path / f"plantuml_{timestamp}.png"
                    
                    with open(png_path, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"✅ PlantUML diagram generated successfully: {png_path}")
                    return str(png_path)
                else:
                    return None
            else:
                # Use standard encoding for local server
                import zlib
                import string
                
                # PlantUML encoding (deflate + custom base64)
                # Use compression level 9 and remove both header and checksum for PlantUML
                compressed = zlib.compress(plantuml_code.encode('utf-8'), 9)[2:-4]
                
                # Custom base64 encoding for PlantUML
                encode_table = string.ascii_uppercase + string.ascii_lowercase + string.digits + '-_'
                encoded = ''
                for i in range(0, len(compressed), 3):
                    if i+2 < len(compressed):
                        encoded += encode_table[(compressed[i] >> 2) & 0x3F]
                        encoded += encode_table[((compressed[i] & 0x3) << 4) | ((compressed[i+1] >> 4) & 0xF)]
                        encoded += encode_table[((compressed[i+1] & 0xF) << 2) | ((compressed[i+2] >> 6) & 0x3)]
                        encoded += encode_table[compressed[i+2] & 0x3F]
                    elif i+1 < len(compressed):
                        encoded += encode_table[(compressed[i] >> 2) & 0x3F]
                        encoded += encode_table[((compressed[i] & 0x3) << 4) | ((compressed[i+1] >> 4) & 0xF)]
                        encoded += encode_table[((compressed[i+1] & 0xF) << 2)]
                    else:
                        encoded += encode_table[(compressed[i] >> 2) & 0x3F]
                        encoded += encode_table[((compressed[i] & 0x3) << 4)]
                
                # Generate PNG using PlantUML server
                # Try with ~1 prefix for HUFFMAN encoding as suggested by PlantUML
                png_url = f"{server_url}/png/~1{encoded}"
                
                response = requests.get(png_url, timeout=10)
                if response.status_code == 200:
                    # Save PNG
                    output_path = Path("generated_tweets/diagrams/plantuml")
                    output_path.mkdir(parents=True, exist_ok=True)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    png_path = output_path / f"plantuml_{timestamp}.png"
                    
                    with open(png_path, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"✅ PlantUML diagram generated successfully: {png_path}")
                    return str(png_path)
                else:
                    print(f"❌ PlantUML server returned status {response.status_code}")
                    return None
                
        except Exception as e:
            raise e  # Re-raise to be handled by the calling method
    
    def _generate_plantuml_with_kroki(self, plantuml_code: str) -> Optional[str]:
        """Generate PlantUML using Kroki.io service"""
        try:
            import base64
            import zlib
            import re
            
            # Clean up PlantUML code for better compatibility
            # Use a simple approach - wrap identifiers with spaces in quotes
            lines = plantuml_code.split('\n')
            cleaned_lines = []
            
            for line in lines:
                # Skip empty lines and @startuml/@enduml
                if not line.strip() or line.strip() in ['@startuml', '@enduml']:
                    cleaned_lines.append(line)
                    continue
                    
                # For arrows (both --> and .>), quote the identifiers
                if '-->' in line or '.>' in line:
                    # Determine arrow type
                    arrow = '-->' if '-->' in line else '.>'
                    
                    # Split by arrow and label
                    if ':' in line:
                        arrow_part, label = line.split(':', 1)
                    else:
                        arrow_part = line
                        label = None
                    
                    # Quote identifiers with spaces/special chars
                    parts = arrow_part.split(arrow)
                    if len(parts) == 2:
                        left = parts[0].strip()
                        right = parts[1].strip()
                        
                        # Quote if contains spaces or special chars
                        if ' ' in left or '/' in left or '.' in left or ',' in left:
                            left = f'"{left}"'
                        if ' ' in right or '/' in right or '.' in right or ',' in right:
                            right = f'"{right}"'
                        
                        new_line = f"{left} {arrow} {right}"
                        if label:
                            new_line += f" : {label.strip()}"
                        cleaned_lines.append(new_line)
                    else:
                        cleaned_lines.append(line)
                else:
                    cleaned_lines.append(line)
            
            cleaned_code = '\n'.join(cleaned_lines)
            
            print(f"[DEBUG] Cleaned PlantUML code:\n{cleaned_code}")
            
            # Kroki expects deflated then base64 encoded PlantUML code
            compressed = zlib.compress(cleaned_code.encode('utf-8'))
            encoded = base64.urlsafe_b64encode(compressed).decode('utf-8')
            
            # Generate PNG using Kroki
            kroki_url = f"https://kroki.io/plantuml/png/{encoded}"
            
            response = requests.get(kroki_url, timeout=15)
            if response.status_code == 200 and response.content:
                # Check if it's actually an image
                if response.headers.get('content-type', '').startswith('image/'):
                    # Save PNG
                    output_path = Path("generated_tweets/diagrams/plantuml")
                    output_path.mkdir(parents=True, exist_ok=True)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    png_path = output_path / f"plantuml_{timestamp}.png"
                    
                    with open(png_path, 'wb') as f:
                        f.write(response.content)
                    
                    print(f"✅ PlantUML diagram generated successfully via Kroki: {png_path}")
                    return str(png_path)
                else:
                    print(f"❌ Kroki returned non-image content type: {response.headers.get('content-type')}")
                    return None
            else:
                print(f"❌ Kroki returned status {response.status_code}")
                if response.text:
                    print(f"Kroki error: {response.text[:200]}")
                return None
                
        except Exception as e:
            raise e
    
    def save_generated_content(self, content: Dict) -> Path:
        """Save generated content to file"""
        output_dir = Path("generated_tweets")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        topic_slug = re.sub(r'[^a-zA-Z0-9]+', '_', content.get("topic", "content"))[:30]
        content_type = content.get('content_type', 'content')
        filename = f"{content_type}_{topic_slug}_{timestamp}.json"
        
        filepath = output_dir / filename
        with open(filepath, 'w') as f:
            json.dump(content, f, indent=2)
        
        return filepath

# Wrapper function for easy integration
def generate_dynamic_content(topic: str, content_type: str = "thread", 
                           template: str = "Conceptual Deep Dive", 
                           context: str = "", api_key: str = None,
                           diagram_type: str = "mermaid",
                           auto_theme: bool = True,
                           manual_theme: str = None) -> Dict:
    """Generate content dynamically using Gemini"""
    
    if not api_key:
        api_key = "AIzaSyC2ZSm7_G9TxUSSrGaOJ2x0ouTDGhGyd9s"
    
    generator = GeminiDynamicGenerator(api_key)
    content = generator.generate_content(topic, content_type, template, context, diagram_type, auto_theme, manual_theme)
    
    # Generate diagram(s) if included
    if "diagram" in content:
        diagram_data = content["diagram"]
        tweet_position = diagram_data.get("tweet_position")
        diagram_paths = {}
        
        print(f"[DEBUG] Generating diagrams. Has mermaid: {'mermaid_code' in diagram_data}, Has plantuml: {'plantuml_code' in diagram_data}")
        
        # Generate Mermaid diagram
        if "mermaid_code" in diagram_data:
            mermaid_path = generator.generate_diagram(diagram_data["mermaid_code"])
            print(f"[DEBUG] Generated Mermaid diagram: {mermaid_path}")
            if mermaid_path:
                diagram_paths["mermaid"] = mermaid_path
                content["diagram"]["mermaid_image_path"] = mermaid_path
        
        # Generate PlantUML diagram
        if "plantuml_code" in diagram_data:
            plantuml_path = generator.generate_plantuml_diagram(
                diagram_data["plantuml_code"], 
                topic=topic
            )
            print(f"[DEBUG] Generated PlantUML diagram: {plantuml_path}")
            if plantuml_path:
                diagram_paths["plantuml"] = plantuml_path
                content["diagram"]["plantuml_image_path"] = plantuml_path
        
        # Attach diagram(s) to specific tweet if position is specified
        if tweet_position and diagram_paths:
            # Use the first available diagram path for tweet attachment
            primary_path = diagram_paths.get("mermaid") or diagram_paths.get("plantuml")
            
            if content_type == "thread" and "tweets" in content:
                # Find the tweet at the specified position
                for tweet in content["tweets"]:
                    if tweet.get("position") == tweet_position:
                        tweet["diagram_path"] = primary_path
                        tweet["diagram_paths"] = diagram_paths
                        tweet["has_diagram"] = True
                        break
            elif content_type == "single" and "tweet" in content:
                # Attach to single tweet
                content["tweet"]["diagram_path"] = primary_path
                content["tweet"]["diagram_paths"] = diagram_paths
                content["tweet"]["has_diagram"] = True
    
    # Save content
    saved_path = generator.save_generated_content(content)
    content["saved_path"] = str(saved_path)
    
    return content

if __name__ == "__main__":
    # Test the generator
    test_content = generate_dynamic_content(
        topic="Building resilient microservices with circuit breakers",
        content_type="thread",
        template="Problem/Solution",
        context="Focus on real-world implementation with code examples"
    )
    
    print(json.dumps(test_content, indent=2))