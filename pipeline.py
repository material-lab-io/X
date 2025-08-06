#!/usr/bin/env python3
"""
Main Pipeline Wrapper for Twitter/X Content Generation System
Coordinates all components for content generation, analysis, and publishing
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add function directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'functions', 'generators'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'functions', 'diagrams'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'functions', 'publishers'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'functions', 'analyzers'))

class ContentPipeline:
    """Main pipeline coordinator for content generation"""
    
    def __init__(self, config_path: str = "config.json"):
        """Initialize pipeline with configuration"""
        self.config = self._load_config(config_path)
        self.generators = self._initialize_generators()
        self.diagram_generator = self._initialize_diagram_generator()
        self.publisher = self._initialize_publisher()
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from multiple possible locations"""
        possible_paths = [
            config_path,
            'data/config.json',
            os.path.join(os.path.dirname(__file__), config_path),
            os.path.join(os.path.dirname(__file__), 'data', 'config.json')
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        return json.load(f)
                except Exception as e:
                    print(f"Error loading config from {path}: {e}")
        
        print("Warning: No config file found, using defaults")
        return {
            'api_keys': {
                'gemini': 'AIzaSyAMOvO0_b0o5LdvZgZBVqZ3mSfBwBukzgY'
            }
        }
    
    def _initialize_generators(self) -> Dict:
        """Initialize all available generators"""
        generators = {}
        
        # Try to load Gemini generator
        try:
            from gemini_dynamic_generator import GeminiDynamicGenerator
            api_key = self.config.get('api_keys', {}).get('gemini') or self.config.get('gemini_api_key')
            if api_key:
                generators['gemini'] = GeminiDynamicGenerator(api_key)
                print("✓ Initialized Gemini generator")
        except Exception as e:
            print(f"⚠️ Could not initialize Gemini generator: {e}")
        
        # Try to load enhanced generator
        try:
            from enhanced_gemini_generator import EnhancedGeminiGenerator
            api_key = self.config.get('api_keys', {}).get('gemini') or self.config.get('gemini_api_key')
            if api_key:
                generators['enhanced'] = EnhancedGeminiGenerator(api_key)
                print("✓ Initialized Enhanced generator")
        except Exception as e:
            print(f"⚠️ Could not initialize Enhanced generator: {e}")
        
        # Try to load simple generator as fallback
        try:
            from simple_tweet_generator import SimpleTweetGenerator
            generators['simple'] = SimpleTweetGenerator()
            print("✓ Initialized Simple generator (fallback)")
        except Exception as e:
            print(f"⚠️ Could not initialize Simple generator: {e}")
        
        return generators
    
    def _initialize_diagram_generator(self):
        """Initialize diagram generator"""
        try:
            from mermaid_diagram_generator import MermaidDiagramGenerator
            print("✓ Initialized Mermaid diagram generator")
            return MermaidDiagramGenerator()
        except Exception as e:
            print(f"⚠️ Could not initialize diagram generator: {e}")
            return None
    
    def _initialize_publisher(self):
        """Initialize Twitter publisher"""
        try:
            from twitter_publisher import TwitterPublisher
            # Check for Twitter credentials in environment
            if all(os.getenv(key) for key in ['API_KEY', 'API_SECRET', 'ACCESS_TOKEN', 'ACCESS_TOKEN_SECRET']):
                print("✓ Twitter publisher ready")
                return TwitterPublisher()
            else:
                print("⚠️ Twitter credentials not found in environment")
                return None
        except Exception as e:
            print(f"⚠️ Could not initialize publisher: {e}")
            return None
    
    def generate_content(self, 
                        topic: str,
                        content_type: str = "thread",
                        style: str = "explanatory",
                        include_diagram: bool = False,
                        generator_type: str = "auto") -> Dict[str, Any]:
        """
        Generate content using the pipeline
        
        Args:
            topic: The topic to generate content about
            content_type: Type of content (single, thread, etc.)
            style: Style template to use
            include_diagram: Whether to generate accompanying diagram
            generator_type: Which generator to use (auto, gemini, enhanced, simple)
        
        Returns:
            Generated content with metadata
        """
        result = {
            'topic': topic,
            'content_type': content_type,
            'style': style,
            'generated_at': datetime.now().isoformat(),
            'success': False
        }
        
        # Select generator
        if generator_type == "auto":
            # Try generators in order of preference
            for gen_name in ['gemini', 'enhanced', 'simple']:
                if gen_name in self.generators:
                    generator = self.generators[gen_name]
                    generator_type = gen_name
                    break
            else:
                result['error'] = "No generators available"
                return result
        else:
            generator = self.generators.get(generator_type)
            if not generator:
                result['error'] = f"Generator '{generator_type}' not available"
                return result
        
        # Generate content
        try:
            if hasattr(generator, 'generate_content'):
                content_result = generator.generate_content(
                    topic=topic,
                    content_type=content_type,
                    template=style
                )
            elif hasattr(generator, 'generate_tweet'):
                content_result = generator.generate_tweet(topic, style)
            else:
                result['error'] = "Generator doesn't have a valid generation method"
                return result
            
            result.update(content_result)
            result['generator'] = generator_type
            result['success'] = True
            
            # Generate diagram if requested
            if include_diagram and self.diagram_generator:
                try:
                    diagram_path = self.diagram_generator.generate_from_topic(topic)
                    result['diagram'] = diagram_path
                    print(f"✓ Generated diagram: {diagram_path}")
                except Exception as e:
                    print(f"⚠️ Could not generate diagram: {e}")
            
            # Save generated content
            self._save_content(result)
            
        except Exception as e:
            result['error'] = str(e)
            print(f"❌ Generation failed: {e}")
        
        return result
    
    def _save_content(self, content: Dict[str, Any]):
        """Save generated content to file"""
        output_dir = Path('generated_tweets')
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = output_dir / f"content_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(content, f, indent=2)
        
        print(f"✓ Saved content to {filename}")
    
    def analyze_content(self, content_path: Optional[str] = None) -> Dict[str, Any]:
        """Analyze generated content or existing posts"""
        try:
            from analyze_posts import analyze_posts
            if content_path:
                return analyze_posts(content_path)
            else:
                # Analyze all generated content
                return analyze_posts('generated_tweets/')
        except Exception as e:
            print(f"❌ Analysis failed: {e}")
            return {'error': str(e)}
    
    def publish_content(self, content: Dict[str, Any], dry_run: bool = True) -> bool:
        """Publish content to Twitter"""
        if not self.publisher:
            print("❌ Publisher not available")
            return False
        
        if dry_run:
            print("🔍 DRY RUN - Not actually posting")
            print(f"Would post: {content.get('tweets', content.get('content', 'No content'))}")
            return True
        
        try:
            self.publisher.post_thread(content.get('tweets', [content.get('content')]))
            print("✓ Published to Twitter")
            return True
        except Exception as e:
            print(f"❌ Publishing failed: {e}")
            return False
    
    def run_interactive(self):
        """Run interactive CLI mode"""
        try:
            from tweet_cli import run_interactive_mode
            run_interactive_mode(self)
        except ImportError:
            print("Interactive mode not available")
            print("Starting basic interactive mode...")
            
            while True:
                print("\n" + "="*50)
                topic = input("Enter topic (or 'quit' to exit): ").strip()
                
                if topic.lower() in ['quit', 'exit', 'q']:
                    break
                
                if not topic:
                    continue
                
                content_type = input("Content type (single/thread) [thread]: ").strip() or "thread"
                style = input("Style [explanatory]: ").strip() or "explanatory"
                include_diagram = input("Include diagram? (y/n) [n]: ").strip().lower() == 'y'
                
                print("\n⏳ Generating content...")
                result = self.generate_content(
                    topic=topic,
                    content_type=content_type,
                    style=style,
                    include_diagram=include_diagram
                )
                
                if result.get('success'):
                    print("\n✅ Content generated successfully!")
                    if result.get('tweets'):
                        for i, tweet in enumerate(result['tweets'], 1):
                            print(f"\n[Tweet {i}]")
                            print(tweet.get('content', tweet))
                    elif result.get('content'):
                        print(f"\n{result['content']}")
                else:
                    print(f"\n❌ Generation failed: {result.get('error', 'Unknown error')}")
                
                action = input("\nPublish to Twitter? (y/n) [n]: ").strip().lower()
                if action == 'y':
                    self.publish_content(result, dry_run=False)


def main():
    """Main entry point for the pipeline"""
    parser = argparse.ArgumentParser(description='Twitter/X Content Generation Pipeline')
    parser.add_argument('topic', nargs='?', help='Topic to generate content about')
    parser.add_argument('--type', default='thread', choices=['single', 'thread'],
                       help='Type of content to generate')
    parser.add_argument('--style', default='explanatory',
                       help='Style template to use')
    parser.add_argument('--diagram', action='store_true',
                       help='Include diagram generation')
    parser.add_argument('--generator', default='auto',
                       choices=['auto', 'gemini', 'enhanced', 'simple'],
                       help='Which generator to use')
    parser.add_argument('--publish', action='store_true',
                       help='Publish to Twitter after generation')
    parser.add_argument('--analyze', action='store_true',
                       help='Analyze generated content')
    parser.add_argument('--interactive', action='store_true',
                       help='Run in interactive mode')
    parser.add_argument('--server', action='store_true',
                       help='Start web server')
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = ContentPipeline()
    
    # Handle different modes
    if args.server:
        print("Starting web server...")
        os.system('python comprehensive_server.py')
    elif args.interactive or not args.topic:
        pipeline.run_interactive()
    elif args.analyze:
        result = pipeline.analyze_content()
        print(json.dumps(result, indent=2))
    else:
        # Generate content
        result = pipeline.generate_content(
            topic=args.topic,
            content_type=args.type,
            style=args.style,
            include_diagram=args.diagram,
            generator_type=args.generator
        )
        
        if result.get('success'):
            print("✅ Content generated successfully!")
            if args.publish:
                pipeline.publish_content(result, dry_run=False)
        else:
            print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)


if __name__ == '__main__':
    main()