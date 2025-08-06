#!/usr/bin/env python3
"""
Unified Twitter/X Content Generator
Integrates structured inputs, style guide, and Gemini API for high-quality content generation
"""

import json
import argparse
import sys
from datetime import datetime, timezone
from typing import List, Dict, Optional, Literal
import re
import google.generativeai as genai
from thread_polisher import ThreadPolisher
from mermaid_diagram_generator import MermaidDiagramGenerator

# Type definitions
ContentType = Literal["SinglePost", "Thread"]
GeneratorType = Literal["StyleAware", "SimplePatternBased"]
TemplateType = Literal["ConceptualDeepDive", "WorkflowShare", "ProblemSolution"]

class UnifiedTweetGenerator:
    def __init__(self, api_key: str, auto_polish: bool = True, auto_diagram: bool = True):
        """Initialize the generator with Gemini API key"""
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.style_guide = None
        self.templates = None
        self.auto_polish = auto_polish
        self.polisher = ThreadPolisher() if auto_polish else None
        self.auto_diagram = auto_diagram
        self.diagram_generator = MermaidDiagramGenerator() if auto_diagram else None
        
    def load_style_guide(self) -> Dict:
        """Load the style guide and templates from JSON files"""
        # Helper function to load from multiple locations
        def load_json_file(filename):
            import os
            possible_paths = [
                filename,
                f"data/{filename}",
                f"../../data/{filename}",
                os.path.join(os.path.dirname(__file__), f"../../data/{filename}")
            ]
            
            for path in possible_paths:
                try:
                    with open(path, 'r') as f:
                        return json.load(f)
                except FileNotFoundError:
                    continue
            return None
        
        # Load style guide
        self.style_guide = load_json_file('twitter_style_guide.json')
        if not self.style_guide:
            print("Warning: twitter_style_guide.json not found. Using basic generation.")
            self.style_guide = {}
        
        # Load templates
        self.templates = load_json_file('twitter_templates.json')
        if not self.templates:
            # Extract templates from style guide if separate file doesn't exist
            self.templates = self.style_guide.get('templates', {})
        
        return self.style_guide
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from generated content"""
        # Common words to filter out
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                      'of', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during',
                      'how', 'when', 'why', 'what', 'where', 'who', 'which', 'their', 'your',
                      'its', 'our', 'my', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                      'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                      'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'}
        
        # Extract words (alphanumeric + common tech symbols)
        words = re.findall(r'\b[\w\-\.]+\b', text.lower())
        
        # Filter and get unique keywords
        keywords = []
        word_counts = {}
        
        for word in words:
            if len(word) > 2 and word not in stop_words and not word.isdigit():
                word_counts[word] = word_counts.get(word, 0) + 1
        
        # Sort by frequency and get top keywords
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, _ in sorted_words[:10]]
        
        return keywords
    
    def assess_difficulty(self, text: str, keywords: List[str]) -> int:
        """Assess content difficulty on a scale of 1-5"""
        difficulty_indicators = {
            'beginner': ['basic', 'simple', 'introduction', 'getting started', 'first'],
            'intermediate': ['implement', 'configure', 'optimize', 'integrate'],
            'advanced': ['architecture', 'scale', 'distributed', 'performance', 'algorithm'],
            'expert': ['kernel', 'low-level', 'internals', 'compiler', 'assembly']
        }
        
        text_lower = text.lower()
        score = 2  # Default to intermediate
        
        # Check for difficulty indicators
        if any(word in text_lower for word in difficulty_indicators['beginner']):
            score = 1
        elif any(word in text_lower for word in difficulty_indicators['expert']):
            score = 5
        elif any(word in text_lower for word in difficulty_indicators['advanced']):
            score = 4
        elif any(word in text_lower for word in difficulty_indicators['intermediate']):
            score = 3
            
        # Adjust based on technical keyword density
        tech_keywords = [k for k in keywords if any(c in k for c in ['-', '_', '.']) or k in ['api', 'sdk', 'cli', 'gpu', 'cpu']]
        if len(tech_keywords) > 5:
            score = min(5, score + 1)
            
        return score
    
    def detect_tone(self, text: str) -> str:
        """Detect the tone of the generated content"""
        tone_indicators = {
            'educational': ['learn', 'understand', 'explain', 'how to', 'guide', 'tutorial'],
            'inspirational': ['amazing', 'incredible', 'game-changer', 'revolutionary', 'breakthrough'],
            'conversational': ['hey', "here's", "let's", 'you', 'your', "I've", "we've"],
            'analytical': ['analysis', 'data', 'metrics', 'performance', 'comparison', 'benchmark'],
            'problem-solving': ['issue', 'fix', 'solve', 'debug', 'error', 'problem', 'solution']
        }
        
        text_lower = text.lower()
        tone_scores = {}
        
        for tone, indicators in tone_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            if score > 0:
                tone_scores[tone] = score
        
        if tone_scores:
            return max(tone_scores.items(), key=lambda x: x[1])[0]
        return 'informative'  # Default tone
    
    def split_into_tweets(self, text: str, max_length: int = 280) -> List[str]:
        """Split text into tweet-sized chunks for threads"""
        tweets = []
        
        # First, split by natural paragraph breaks
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        current_tweet = ""
        tweet_number = 1
        
        for paragraph in paragraphs:
            # Check if paragraph itself is too long
            if len(paragraph) > max_length - 10:  # Leave room for numbering
                # Split long paragraphs by sentences
                sentences = re.split(r'(?<=[.!?])\s+', paragraph)
                for sentence in sentences:
                    if len(current_tweet) + len(sentence) + 1 > max_length - 10:
                        if current_tweet:
                            tweets.append(f"{tweet_number}/ {current_tweet.strip()}")
                            tweet_number += 1
                            current_tweet = sentence
                    else:
                        current_tweet += (" " if current_tweet else "") + sentence
            else:
                # Try to fit whole paragraph
                if len(current_tweet) + len(paragraph) + 2 > max_length - 10:
                    if current_tweet:
                        tweets.append(f"{tweet_number}/ {current_tweet.strip()}")
                        tweet_number += 1
                        current_tweet = paragraph
                else:
                    current_tweet += ("\n\n" if current_tweet else "") + paragraph
        
        # Don't forget the last tweet
        if current_tweet:
            tweets.append(f"{tweet_number}/ {current_tweet.strip()}")
        
        # Add thread count to all tweets
        total_tweets = len(tweets)
        tweets = [tweet.replace("/", f"/{total_tweets}") for tweet in tweets]
        
        return tweets
    
    def construct_simple_prompt(self, topic: str, content_type: ContentType, 
                                additional_context: Optional[str]) -> str:
        """Construct a simple prompt for basic pattern generation"""
        prompt = f"""Generate a {'Twitter/X thread' if content_type == 'Thread' else 'single Twitter/X post'} about: {topic}

Requirements:
- Start with an engaging hook
- Be concise and informative
- Use clear, technical language
- Include practical insights
"""
        
        if additional_context:
            prompt += f"\nAdditional context: {additional_context}"
        
        if content_type == "Thread":
            prompt += "\n- Create 3-5 connected tweets that build on each other"
            prompt += "\n- Each tweet should be valuable standalone but better together"
        else:
            prompt += "\n- Keep it under 280 characters"
            prompt += "\n- Make every word count"
        
        return prompt
    
    def construct_style_aware_prompt(self, topic: str, content_type: ContentType,
                                     template: TemplateType, additional_context: Optional[str]) -> str:
        """Construct a prompt using style guide and templates"""
        if not self.style_guide:
            return self.construct_simple_prompt(topic, content_type, additional_context)
        
        # Get template structure
        template_map = {
            "ConceptualDeepDive": "first_principles",
            "WorkflowShare": "workflow_tool_share", 
            "ProblemSolution": "build_in_public"
        }
        
        template_key = template_map.get(template, "first_principles")
        template_structure = None
        
        # Try to get template from templates file or style guide
        if self.templates and template_key in self.templates:
            template_structure = self.templates[template_key]
        elif 'templates' in self.style_guide and template_key in self.style_guide['templates']:
            template_structure = self.style_guide['templates'][template_key]
        
        # Build the prompt
        prompt = f"""Generate a {'Twitter/X thread' if content_type == 'Thread' else 'Twitter/X post'} about: {topic}

Style Guidelines:
"""
        
        # Add writing rules
        if 'writing_rules' in self.style_guide:
            rules = self.style_guide['writing_rules']
            if 'hooks' in rules:
                prompt += f"\nHooks: Use {', '.join(rules['hooks'].get('types', ['engaging']))} style openings"
            if 'structure' in rules:
                prompt += f"\nStructure: {json.dumps(rules['structure'])}"
            if 'formatting' in rules:
                prompt += f"\nFormatting: {json.dumps(rules['formatting'])}"
        
        # Add template structure if available
        if template_structure:
            prompt += f"\n\nFollow this {template} template structure:"
            if isinstance(template_structure, dict):
                for key, value in template_structure.items():
                    prompt += f"\n- {key}: {value}"
            else:
                prompt += f"\n{template_structure}"
        
        # Add tone guidance
        if 'tone_variations' in self.style_guide:
            prompt += f"\n\nTone options: {', '.join(self.style_guide['tone_variations'])}"
            prompt += "\nChoose the most appropriate tone for this topic."
        
        # Add additional context
        if additional_context:
            prompt += f"\n\nAdditional context: {additional_context}"
        
        # Add content type specific instructions
        if content_type == "Thread":
            prompt += "\n\nThread requirements:"
            prompt += "\n- Create 3-5 connected tweets"
            prompt += "\n- Each tweet max 280 characters"
            prompt += "\n- Number them as 1/, 2/, etc."
            prompt += "\n- Ensure narrative flow between tweets"
        else:
            prompt += "\n\nSingle post requirements:"
            prompt += "\n- Maximum 280 characters"
            prompt += "\n- Complete thought in one tweet"
        
        # Add philosophy reminder
        if 'core_philosophy' in self.style_guide:
            prompt += f"\n\nRemember: {self.style_guide['core_philosophy']}"
        
        return prompt
    
    def generate_content(self, topic: str, content_type: ContentType,
                         additional_context: Optional[str], generator_type: GeneratorType,
                         template: Optional[TemplateType]) -> Dict:
        """Main generation function that orchestrates the entire process"""
        # Load style guide if using StyleAware mode
        if generator_type == "StyleAware":
            self.load_style_guide()
        
        # Construct appropriate prompt
        if generator_type == "SimplePatternBased":
            prompt = self.construct_simple_prompt(topic, content_type, additional_context)
        else:
            prompt = self.construct_style_aware_prompt(topic, content_type, template, additional_context)
        
        try:
            # Generate content using Gemini
            response = self.model.generate_content(prompt)
            generated_text = response.text.strip()
            
            # Split into tweets if needed
            if content_type == "Thread":
                tweets = self.split_into_tweets(generated_text)
            else:
                # For single post, ensure it's under 280 chars
                if len(generated_text) > 280:
                    # Try to intelligently truncate
                    generated_text = generated_text[:277] + "..."
                tweets = [generated_text]
            
            # Polish the tweets if auto_polish is enabled
            original_tweets = tweets.copy()
            feedback = None
            
            if self.auto_polish and self.polisher:
                # Detect template for polishing
                template_for_polish = None
                if template:
                    template_map = {
                        "ConceptualDeepDive": "conceptual_deep_dive",
                        "WorkflowShare": "workflow_tool_share",
                        "ProblemSolution": "build_in_public"
                    }
                    template_for_polish = template_map.get(template)
                
                # Polish the tweets
                tweets, detected_template = self.polisher.polish_thread(tweets, template_for_polish)
                
                # Generate feedback
                feedback = self.polisher.generate_feedback(original_tweets, tweets, detected_template)
            
            # Extract metadata from polished tweets
            full_text = " ".join(tweets)
            keywords = self.extract_keywords(full_text)
            tone = self.detect_tone(full_text)
            difficulty = self.assess_difficulty(full_text, keywords)
            
            # Generate diagram if enabled and appropriate
            diagram_info = None
            if self.auto_diagram and self.diagram_generator:
                # Generate diagram for Conceptual Deep Dive templates
                if template == "ConceptualDeepDive" or (not template and "architecture" in topic.lower()):
                    # Determine diagram type based on content
                    if any(word in topic.lower() for word in ["workflow", "process", "pipeline"]):
                        diagram_type = "workflow"
                    elif any(word in topic.lower() for word in ["state", "behavior", "agent"]):
                        diagram_type = "state"
                    elif any(word in topic.lower() for word in ["api", "sequence", "interaction"]):
                        diagram_type = "sequence"
                    else:
                        diagram_type = "architecture"
                    
                    # Generate diagram
                    diagram_result = self.diagram_generator.generate_diagram_for_topic(
                        topic, diagram_type, {"content": full_text}
                    )
                    
                    # Save diagram code
                    diagram_filename = f"diagram_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mmd"
                    diagram_path = f"generated_diagrams/{diagram_filename}"
                    
                    # Create directory if needed
                    import os
                    os.makedirs("generated_diagrams", exist_ok=True)
                    
                    with open(diagram_path, 'w') as f:
                        f.write(diagram_result["diagram_code"])
                    
                    diagram_info = {
                        "type": diagram_type,
                        "code_path": diagram_path,
                        "code": diagram_result["diagram_code"],
                        "explanation": diagram_result.get("explanation", ""),
                        "placement": diagram_result.get("placement_recommendation", {}),
                        "render_method": diagram_result["render_method"]
                    }
                    
                    # Insert placeholder in recommended tweet
                    placement = diagram_result.get("placement_recommendation", {})
                    tweet_num = placement.get("tweet_number", 3) - 1  # 0-indexed
                    placeholder = placement.get("placeholder", "📊 [Flowchart Attached Below]")
                    
                    if 0 <= tweet_num < len(tweets):
                        # Add placeholder to the end of the recommended tweet
                        tweets[tweet_num] = tweets[tweet_num].rstrip() + f"\n\n{placeholder}"
                    
                    # Try to render PNG
                    png_path = diagram_path.replace('.mmd', '.png')
                    if self.diagram_generator.render_diagram(
                        diagram_result["diagram_code"], png_path
                    ):
                        diagram_info["image_path"] = png_path
                        diagram_info["render_status"] = "success"
                    else:
                        diagram_info["render_status"] = "failed"
            
            # Build response
            result = {
                "topic": topic,
                "generatorType": generator_type,
                "template": template if generator_type == "StyleAware" else None,
                "contentType": content_type,
                "generatedTweets": tweets,
                "keywords": keywords,
                "tone": tone,
                "difficultyScore": difficulty,
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "polished": self.auto_polish
            }
            
            # Add original tweets and feedback if polishing was done
            if self.auto_polish and feedback:
                result["originalTweets"] = original_tweets
                result["polishingFeedback"] = feedback
            
            # Add diagram info if generated
            if diagram_info:
                result["diagram"] = diagram_info
            
            return result
            
        except Exception as e:
            print(f"Error generating content: {e}")
            return {
                "error": str(e),
                "topic": topic,
                "generatorType": generator_type,
                "createdAt": datetime.now(timezone.utc).isoformat()
            }


def main():
    """CLI interface for the unified tweet generator"""
    parser = argparse.ArgumentParser(description="Generate Twitter/X content with style awareness")
    
    parser.add_argument("topic", help="Topic for the content (e.g., 'Docker caching tips')")
    parser.add_argument("--content-type", choices=["SinglePost", "Thread"], 
                        default="SinglePost", help="Type of content to generate")
    parser.add_argument("--context", help="Additional context (e.g., recent bugs, tech used)")
    parser.add_argument("--generator", choices=["StyleAware", "SimplePatternBased"],
                        default="StyleAware", help="Generator type to use")
    parser.add_argument("--template", choices=["ConceptualDeepDive", "WorkflowShare", "ProblemSolution"],
                        default="ConceptualDeepDive", help="Template to use (only for StyleAware)")
    parser.add_argument("--api-key", help="Gemini API key (or set GEMINI_API_KEY env var)")
    parser.add_argument("--output", help="Output file for JSON result")
    parser.add_argument("--no-polish", action="store_true", help="Disable automatic polishing")
    parser.add_argument("--polish-only", help="Polish existing tweets from JSON file (skips generation)")
    parser.add_argument("--no-diagram", action="store_true", help="Disable automatic diagram generation")
    parser.add_argument("--diagram-only", action="store_true", help="Generate diagram for topic (skips tweet generation)")
    
    args = parser.parse_args()
    
    # Get API key
    api_key = args.api_key
    if not api_key:
        # Try to load from config file
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
                api_key = config.get('api_keys', {}).get('gemini')
        except:
            pass
    
    if not api_key:
        import os
        api_key = os.environ.get('GEMINI_API_KEY')
    
    if not api_key:
        print("Error: Gemini API key required. Provide via --api-key, config.json, or GEMINI_API_KEY env var")
        sys.exit(1)
    
    # Handle polish-only mode
    if args.polish_only:
        # Load tweets from file and polish them
        try:
            with open(args.polish_only, 'r') as f:
                data = json.load(f)
            
            # Extract tweets
            if isinstance(data, list):
                tweets = data
            elif isinstance(data, dict):
                tweets = data.get('generatedTweets', data.get('tweets', []))
            else:
                print("Error: Invalid input format for polish-only mode")
                sys.exit(1)
            
            # Polish the tweets
            polisher = ThreadPolisher()
            template = None
            if args.template:
                template_map = {
                    "ConceptualDeepDive": "conceptual_deep_dive",
                    "WorkflowShare": "workflow_tool_share",
                    "ProblemSolution": "build_in_public"
                }
                template = template_map.get(args.template)
            
            polished_tweets, detected_template = polisher.polish_thread(tweets, template)
            feedback = polisher.generate_feedback(tweets, polished_tweets, detected_template)
            
            result = {
                "originalTweets": tweets,
                "polishedTweets": polished_tweets,
                "feedback": feedback,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result, f, indent=2)
                print(f"Polished results saved to {args.output}")
            else:
                print(json.dumps(result, indent=2))
            
            return
        except Exception as e:
            print(f"Error in polish-only mode: {e}")
            sys.exit(1)
    
    # Handle diagram-only mode
    if args.diagram_only:
        diagram_gen = MermaidDiagramGenerator()
        diagram_type = "architecture"  # Default
        
        # Determine type from topic
        if "workflow" in args.topic.lower() or "process" in args.topic.lower():
            diagram_type = "workflow"
        elif "state" in args.topic.lower() or "agent" in args.topic.lower():
            diagram_type = "state"
        elif "api" in args.topic.lower() or "sequence" in args.topic.lower():
            diagram_type = "sequence"
        
        result = diagram_gen.generate_diagram_for_topic(args.topic, diagram_type)
        
        if args.output:
            # Save diagram code
            with open(args.output, 'w') as f:
                f.write(result["diagram_code"])
            print(f"Diagram code saved to {args.output}")
            
            # Try to render
            png_path = args.output.replace('.mmd', '.png')
            if diagram_gen.render_diagram(result["diagram_code"], png_path):
                print(f"Rendered to {png_path}")
        else:
            print(result["diagram_code"])
        
        return
    
    # Create generator with auto-polish and auto-diagram settings
    generator = UnifiedTweetGenerator(
        api_key, 
        auto_polish=not args.no_polish,
        auto_diagram=not args.no_diagram
    )
    
    # Generate content
    result = generator.generate_content(
        topic=args.topic,
        content_type=args.content_type,
        additional_context=args.context,
        generator_type=args.generator,
        template=args.template if args.generator == "StyleAware" else None
    )
    
    # Output results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Results saved to {args.output}")
    else:
        print(json.dumps(result, indent=2))
    
    # Also print a human-readable version
    if "error" not in result:
        print("\n" + "="*50)
        print("Generated Content:")
        print("="*50)
        for i, tweet in enumerate(result['generatedTweets'], 1):
            print(f"\nTweet {i}:")
            print(tweet)
            print(f"[{len(tweet)} characters]")
        
        print(f"\nTone: {result['tone']}")
        print(f"Difficulty: {result['difficultyScore']}/5")
        print(f"Keywords: {', '.join(result['keywords'][:5])}")
        
        # Show polishing feedback if available
        if 'polishingFeedback' in result:
            feedback = result['polishingFeedback']
            print("\n" + "="*50)
            print("Polishing Feedback:")
            print("="*50)
            print(f"Template: {feedback['templateUsed']}")
            print(f"Clarity Score: {feedback['clarityScore']}/5")
            print(f"Tone Consistency: {feedback['toneConsistency']}/5")
            print(f"Engagement Potential: {feedback['engagementPotential']}/5")
            print(f"\nActionable Feedback:")
            for item in feedback['actionableFeedback']:
                print(f"  • {item}")
        
        # Show diagram info if available
        if 'diagram' in result:
            diagram = result['diagram']
            print("\n" + "="*50)
            print("Generated Diagram:")
            print("="*50)
            print(f"Type: {diagram['type']}")
            print(f"Code saved to: {diagram['code_path']}")
            if 'image_path' in diagram:
                print(f"Image rendered to: {diagram['image_path']}")
            else:
                print("Image rendering failed - use code file with Mermaid renderer")
            print(f"\nDiagram Explanation:")
            print(diagram.get('explanation', 'No explanation available'))
            
            if 'placement' in diagram and diagram['placement']:
                placement = diagram['placement']
                print(f"\nPlacement Recommendation:")
                print(f"  • Insert at Tweet {placement.get('tweet_number', 3)}")
                print(f"  • Reasoning: {placement.get('reasoning', '')}")
                print(f"  • Placeholder: {placement.get('placeholder', '')}")
            
            print(f"\nDiagram Code Preview:")
            print("-" * 30)
            print(diagram['code'][:300] + "..." if len(diagram['code']) > 300 else diagram['code'])


if __name__ == "__main__":
    main()