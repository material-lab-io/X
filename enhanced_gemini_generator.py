#!/usr/bin/env python3
"""
Enhanced Gemini Generator with Advanced Prompting Strategy
Generates high-quality, deeply informative Twitter/X content with diagrams
Inspired by technical educators like @iximiuz
"""

import json
import os
from typing import Dict, List, Optional, Union
from datetime import datetime
from pathlib import Path
import google.generativeai as genai
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedGeminiGenerator:
    """Advanced Gemini generator with configurable prompting strategy"""
    
    def __init__(self, api_key: str, debug_mode: bool = False):
        """Initialize with API key and debug mode"""
        self.api_key = api_key
        self.debug_mode = debug_mode
        genai.configure(api_key=api_key)
        # Use the latest available Gemini model
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
    def build_unified_prompt(self, config: Dict) -> str:
        """Build a comprehensive prompt based on user configuration"""
        
        # Extract configuration with defaults
        topic = config.get('topic', '')
        content_type = config.get('content_type', 'thread')
        template = config.get('template', 'Conceptual Deep Dive')
        audience = config.get('audience', 'intermediate developers')
        tone = config.get('tone', 'technical yet approachable')
        goal = config.get('goal', 'explain complex concepts clearly')
        depth = config.get('depth', 'intermediate')
        max_words_per_post = config.get('length_constraints', {}).get('max_words_per_post', 50)
        min_tweets = config.get('length_constraints', {}).get('min_tweets', 5)
        max_tweets = config.get('length_constraints', {}).get('max_tweets', 7)
        include_diagrams = config.get('include_diagrams', True)
        diagram_type = config.get('diagram_type', 'auto-detect')
        inspiration = config.get('inspiration', '@iximiuz')
        
        # Build the comprehensive prompt
        prompt = f"""You are an expert technical content creator for Twitter/X, creating deeply informative content in the style of {inspiration}.

CONFIGURATION:
- Topic: {topic}
- Content Type: {content_type}
- Template: {template}
- Target Audience: {audience}
- Tone: {tone}
- Goal: {goal}
- Technical Depth: {depth}
- Max Words per Tweet: {max_words_per_post}
- Thread Length: {min_tweets}-{max_tweets} tweets
- Include Diagrams: {include_diagrams}
- Diagram Type: {diagram_type}

CONTENT GENERATION RULES:
1. Generate ORIGINAL, DYNAMIC content based on the topic. Never reuse pre-stored content.
2. Each tweet must be concise yet information-dense (max {max_words_per_post} words).
3. Use technical accuracy while maintaining accessibility for {audience}.
4. Include practical examples, real-world applications, and actionable insights.

THREAD STRUCTURE (for threads):
- Tweet 1: Compelling hook that introduces the problem/concept
- Tweet 2: Why this matters (impact, relevance, common misconceptions)
- Tweets 3-N: Step-by-step breakdown with concrete examples
- Diagram placement: Insert where it adds most value (specify in output)
- Final Tweet: Summary, key takeaways, or call to action

SINGLE POST STRUCTURE (for single posts):
- Opening: Hook + core insight
- Middle: Key technical details or example
- Closing: Practical application or thought-provoking question

"""

        # Add template-specific instructions
        if template == "Conceptual Deep Dive":
            prompt += """
TEMPLATE: Conceptual Deep Dive
- Start with a fundamental question or observation
- Break down complex concepts into digestible parts
- Use analogies where helpful
- Include technical details progressively
- End with practical implications
"""
        elif template == "Problem/Solution":
            prompt += """
TEMPLATE: Problem/Solution
- Start by clearly stating a real problem developers face
- Explain why existing solutions fall short
- Present your solution with clear benefits
- Include implementation details or examples
- End with results or impact
"""
        elif template == "Workflow/Tool Share":
            prompt += """
TEMPLATE: Workflow/Tool Share
- Start with the workflow challenge or inefficiency
- Introduce the tool/technique as a solution
- Walk through setup and usage step-by-step
- Include tips, tricks, or lesser-known features
- End with productivity gains or outcomes
"""

        # Add diagram instructions if enabled
        if include_diagrams:
            prompt += f"""
DIAGRAM REQUIREMENTS:
- Include a technical diagram to visualize key concepts
- Diagram type: {diagram_type}
- For Mermaid: Use clear, simple syntax (flowchart, sequence, or state diagram)
- For PlantUML: Use proper UML syntax - for component diagrams use [ComponentName] with --> arrows, for sequence diagrams use participant declarations and -> arrows. NEVER use !include statements or external libraries as they are not supported by Kroki
- If auto-detect: Choose based on content (architecture->component, flow->sequence, etc.)
- Provide a clear diagram_description explaining what to visualize
"""

        # Add output format instructions
        prompt += """
OUTPUT FORMAT:
Generate a JSON response with this EXACT structure:
{
  "tweets": [
    {
      "position": 1,
      "text": "Tweet content here (keep under word limit)",
      "has_diagram": false,
      "diagram_description": null
    },
    {
      "position": 2,
      "text": "Tweet content here",
      "has_diagram": true,
      "diagram_description": "Architecture diagram showing microservices communicating via message queue"
    }
  ],
  "metadata": {
    "total_tweets": 5,
    "estimated_read_time": "2 minutes",
    "key_concepts": ["concept1", "concept2"],
    "diagram_placement": 3,
    "diagram_type": "mermaid"
  },
  "diagrams": {
    "mermaid_code": "graph TD\\n    A[Service] --> B[Queue]",
    "plantuml_code": "@startuml\\n[Container 1] --> [Bridge] : veth1\\n[Bridge] --> [Container 2] : veth2\\n@enduml"
  }
}

CRITICAL REQUIREMENTS:
1. Generate completely NEW content based on the provided topic
2. Ensure technical accuracy while maintaining readability
3. Each tweet must stand alone but contribute to the thread narrative
4. Mark EXACTLY which tweet should have the diagram attached
5. Provide working diagram code that visualizes the key concept (PlantUML must not use any !include statements)
6. Follow Twitter best practices: clear breaks, strategic emoji use (sparingly)

Now generate the content for: {topic}
"""
        
        return prompt
    
    def generate_content(self, config: Dict) -> Dict:
        """Generate content using the enhanced prompting strategy"""
        
        # Build the prompt
        prompt = self.build_unified_prompt(config)
        
        # Log prompt if in debug mode
        if self.debug_mode:
            logger.info("=" * 80)
            logger.info("DEBUG MODE: GEMINI PROMPT")
            logger.info("=" * 80)
            logger.info(prompt)
            logger.info("=" * 80)
        
        try:
            # Generate content
            response = self.model.generate_content(prompt)
            raw_response = response.text
            
            # Log response if in debug mode
            if self.debug_mode:
                logger.info("=" * 80)
                logger.info("DEBUG MODE: GEMINI RESPONSE")
                logger.info("=" * 80)
                logger.info(raw_response)
                logger.info("=" * 80)
            
            # Parse JSON response
            # Handle code block markers if present
            if '```json' in raw_response:
                json_start = raw_response.find('```json') + 7
                json_end = raw_response.find('```', json_start)
                json_str = raw_response[json_start:json_end].strip()
            else:
                json_str = raw_response.strip()
            
            result = json.loads(json_str)
            
            # Validate and enhance result
            result = self._validate_and_enhance_result(result, config)
            
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"Raw response: {raw_response[:500]}...")
            return self._create_error_response(f"JSON parsing error: {str(e)}", config)
        except Exception as e:
            logger.error(f"Generation error: {e}")
            return self._create_error_response(f"Generation error: {str(e)}", config)
    
    def _validate_and_enhance_result(self, result: Dict, config: Dict) -> Dict:
        """Validate and enhance the generated result"""
        
        # Ensure required fields exist
        if 'tweets' not in result:
            raise ValueError("Missing 'tweets' field in response")
        
        # Add default metadata if missing
        if 'metadata' not in result:
            result['metadata'] = {}
        
        # Calculate character counts
        for tweet in result['tweets']:
            if 'text' in tweet:
                tweet['character_count'] = len(tweet['text'])
                tweet['word_count'] = len(tweet['text'].split())
        
        # Add generation metadata
        result['metadata'].update({
            'generated_at': datetime.now().isoformat(),
            'config': config,
            'generator': 'enhanced_gemini',
            'debug_mode': self.debug_mode
        })
        
        return result
    
    def _create_error_response(self, error_msg: str, config: Dict) -> Dict:
        """Create a structured error response"""
        return {
            'error': error_msg,
            'tweets': [],
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'config': config,
                'generator': 'enhanced_gemini',
                'debug_mode': self.debug_mode
            }
        }
    
    def generate_diagram_code(self, description: str, diagram_type: str) -> Dict[str, str]:
        """Generate diagram code based on description"""
        
        prompt = f"""Generate a {diagram_type} diagram based on this description:
{description}

Requirements:
- Create clear, professional diagram code
- Use appropriate diagram type for the content
- Keep it simple but informative
- Include proper labels and relationships

Output format:
{{
  "mermaid_code": "diagram code here",
  "plantuml_code": "@startuml\\n...\\n@enduml"
}}
"""
        
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())
            return result
        except Exception as e:
            logger.error(f"Diagram generation error: {e}")
            return {
                "mermaid_code": "graph LR\n    A[Error] --> B[Failed to generate]",
                "plantuml_code": "@startuml\nError -> Failed\n@enduml"
            }


def create_enhanced_content(config: Dict, api_key: str, debug_mode: bool = False) -> Dict:
    """Main function to create enhanced content"""
    
    generator = EnhancedGeminiGenerator(api_key, debug_mode)
    result = generator.generate_content(config)
    
    # Process diagrams if needed
    if config.get('include_diagrams', False) and 'tweets' in result:
        for tweet in result['tweets']:
            if tweet.get('has_diagram') and tweet.get('diagram_description'):
                # Generate diagram code if not already present
                if 'diagrams' not in result:
                    diagram_code = generator.generate_diagram_code(
                        tweet['diagram_description'],
                        config.get('diagram_type', 'mermaid')
                    )
                    result['diagrams'] = diagram_code
    
    # Save to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"generated_tweets/enhanced_{config['content_type']}_{timestamp}.json"
    
    os.makedirs('generated_tweets', exist_ok=True)
    with open(filename, 'w') as f:
        json.dump(result, f, indent=2)
    
    result['saved_path'] = filename
    
    return result


# Example usage
if __name__ == "__main__":
    # Example configuration
    example_config = {
        "topic": "How container networking actually works under the hood",
        "content_type": "thread",
        "template": "Conceptual Deep Dive",
        "audience": "intermediate DevOps engineers",
        "tone": "technical yet approachable",
        "goal": "demystify container networking internals",
        "depth": "intermediate",
        "length_constraints": {
            "max_words_per_post": 50,
            "min_tweets": 5,
            "max_tweets": 7
        },
        "include_diagrams": True,
        "diagram_type": "auto-detect",
        "inspiration": "@iximiuz"
    }
    
    # Generate content
    api_key = "YOUR_GEMINI_API_KEY"
    result = create_enhanced_content(example_config, api_key, debug_mode=True)
    
    print(json.dumps(result, indent=2))