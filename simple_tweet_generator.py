#!/usr/bin/env python3
"""
Simple tweet generator using pattern matching and templates
Works without external API dependencies
"""

import json
import random
from datetime import datetime
from pathlib import Path
import re

class SimpleTweetGenerator:
    def __init__(self):
        """Initialize with the posts dataset"""
        with open("extracted_threads_final.json", 'r') as f:
            self.posts = json.load(f)
        
        # Extract patterns from existing posts
        self.hooks = [p['content']['hook'] for p in self.posts if p['content']['hook']]
        self.extract_patterns()
    
    def extract_patterns(self):
        """Extract common patterns from the dataset"""
        self.hook_patterns = []
        self.content_patterns = []
        
        for post in self.posts:
            # Analyze hook patterns
            hook = post['content']['hook']
            if hook:
                # Extract pattern types
                if hook.endswith('?'):
                    self.hook_patterns.append("question")
                elif "never" in hook.lower() or "always" in hook.lower():
                    self.hook_patterns.append("absolute_statement")
                elif any(char.isdigit() for char in hook):
                    self.hook_patterns.append("numbered_list")
                else:
                    self.hook_patterns.append("statement")
        
        # Analyze technical keywords by category
        self.technical_terms = {
            "AI Agent Testing": ["agents", "LLM", "testing", "benchmark", "autonomous", "speedrun"],
            "Docker": ["containers", "Docker", "Linux", "namespaces", "cgroups", "pods"],
            "Video Models": ["video", "LLaVA", "SlowFast", "visual", "multi-modal", "captioning"],
            "LLMs": ["transformers", "language models", "fine-tuning", "attention", "GPT"],
            "DevTools": ["Kubernetes", "networking", "orchestration", "deployment"],
            "Agentic Coding": ["AI agents", "frameworks", "multi-agent", "orchestrator"]
        }
    
    def generate_hook(self, topic: str, style: str = "statement") -> str:
        """Generate a hook based on patterns"""
        topic_lower = topic.lower()
        
        hook_templates = {
            "question": [
                f"Ever wondered how {topic} really works?",
                f"What if I told you {topic} could be 10x faster?",
                f"Why is everyone talking about {topic}?"
            ],
            "absolute_statement": [
                f"We've never seen {topic} implemented this efficiently.",
                f"Everyone's doing {topic} wrong. Here's why.",
                f"The truth about {topic} nobody wants to admit."
            ],
            "numbered_list": [
                f"5 ways {topic} will change your workflow",
                f"3 hidden features in {topic} you're not using",
                f"7 {topic} techniques that actually work"
            ],
            "statement": [
                f"Let's talk about {topic} and why it matters.",
                f"{topic.title()} is more powerful than you think.",
                f"Breaking down {topic} into simple concepts."
            ]
        }
        
        # Choose style based on existing patterns or random
        if style == "random":
            style = random.choice(list(hook_templates.keys()))
        
        if style in hook_templates:
            return random.choice(hook_templates[style])
        
        return f"Let's explore {topic} 🚀"
    
    def generate_technical_content(self, topic: str, category: str, length: int = 200) -> str:
        """Generate technical content based on category patterns"""
        # Get relevant technical terms
        terms = self.technical_terms.get(category, [])
        
        content_templates = {
            "explanation": f"""Understanding {topic}:

Key concepts:
- Core architecture and design principles
- Performance optimization techniques
- Real-world implementation patterns

This approach improves efficiency by reducing overhead and maximizing throughput.""",
            
            "tutorial": f"""Step-by-step guide to {topic}:

1. Set up your environment
2. Understand the core concepts
3. Implement the basic structure
4. Optimize for production
5. Monitor and iterate

Each step builds on the previous, creating a robust solution.""",
            
            "insight": f"""After working with {topic}, here's what I learned:

The key insight is understanding how components interact at a fundamental level. 
By focusing on the underlying patterns, we can build more efficient systems.

This changes how we think about architecture and scaling.""",
            
            "announcement": f"""Excited to share our work on {topic}!

We've developed a new approach that:
• Reduces complexity by 50%
• Improves performance significantly
• Makes implementation straightforward

Open-sourced with full documentation."""
        }
        
        # Choose a template
        template_type = random.choice(list(content_templates.keys()))
        content = content_templates[template_type]
        
        # Insert some technical terms
        for term in random.sample(terms, min(2, len(terms))):
            content = content.replace("concepts", f"{term} concepts", 1)
        
        return content[:length] + "..." if len(content) > length else content
    
    def generate_single_tweet(self, topic: str, category: str = None) -> dict:
        """Generate a single tweet"""
        # Determine category from topic if not provided
        if not category:
            category = self.detect_category(topic)
        
        # Generate components
        hook = self.generate_hook(topic, style="random")
        content = self.generate_technical_content(topic, category, length=180)
        
        # Combine for tweet
        tweet_text = f"{hook}\n\n{content}"
        
        # Add hashtags based on category
        hashtags = self.generate_hashtags(category, topic)
        
        if hashtags:
            tweet_text += f"\n\n{' '.join(hashtags)}"
        
        # Ensure it fits in a tweet
        if len(tweet_text) > 280:
            # Trim content part
            available = 280 - len(hook) - len(' '.join(hashtags)) - 10
            content = content[:available] + "..."
            tweet_text = f"{hook}\n\n{content}\n\n{' '.join(hashtags)}"
        
        return {
            "generated_at": datetime.now().isoformat(),
            "model": "pattern-based",
            "topic": topic,
            "category": category,
            "content": {
                "full_text": tweet_text,
                "hook": hook,
                "main_content": content,
                "hashtags": hashtags,
                "character_count": len(tweet_text)
            }
        }
    
    def generate_thread(self, topic: str, category: str = None, length: int = 5) -> dict:
        """Generate a thread of tweets"""
        if not category:
            category = self.detect_category(topic)
        
        tweets = []
        
        # First tweet - hook
        hook = self.generate_hook(topic, style="statement")
        intro = f"{hook}\n\nA thread on {topic} 🧵"
        tweets.append({
            "position": 1,
            "content": intro,
            "character_count": len(intro)
        })
        
        # Content tweets
        content_points = [
            "First, let's understand the fundamentals",
            "The key insight here is efficiency",
            "Here's how to implement this in practice",
            "Common pitfalls to avoid",
            "Resources and next steps"
        ]
        
        for i, point in enumerate(content_points[:length-1], 2):
            tweet_content = f"{i}/\n\n{point}:\n\n"
            detail = self.generate_technical_content(topic, category, length=150)
            tweet_content += detail
            
            tweets.append({
                "position": i,
                "content": tweet_content,
                "character_count": len(tweet_content)
            })
        
        return {
            "generated_at": datetime.now().isoformat(),
            "model": "pattern-based",
            "topic": topic,
            "category": category,
            "thread_type": "educational",
            "tweets": tweets,
            "total_tweets": len(tweets)
        }
    
    def detect_category(self, topic: str) -> str:
        """Detect category from topic keywords"""
        topic_lower = topic.lower()
        
        for category, terms in self.technical_terms.items():
            if any(term.lower() in topic_lower for term in terms):
                return category
        
        return "DevTools"  # default
    
    def generate_hashtags(self, category: str, topic: str) -> list:
        """Generate relevant hashtags"""
        hashtag_map = {
            "AI Agent Testing": ["#AI", "#LLM", "#AIAgents"],
            "Docker": ["#Docker", "#DevOps", "#Containers"],
            "Video Models": ["#AI", "#ComputerVision", "#DeepLearning"],
            "LLMs": ["#LLM", "#AI", "#MachineLearning"],
            "DevTools": ["#DevTools", "#Programming", "#Tech"],
            "Agentic Coding": ["#AI", "#Coding", "#Automation"]
        }
        
        base_tags = hashtag_map.get(category, ["#Tech", "#AI"])
        
        # Add topic-specific tag if short enough
        topic_words = topic.split()
        if len(topic_words) > 0 and len(topic_words[0]) < 15:
            base_tags.append(f"#{topic_words[0]}")
        
        return base_tags[:3]  # Limit to 3 hashtags
    
    def save_output(self, content: dict, output_dir: str = "generated_tweets"):
        """Save generated content"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        content_type = "thread" if "tweets" in content else "single"
        filename = f"{content_type}_{timestamp}.json"
        
        with open(output_path / filename, 'w') as f:
            json.dump(content, f, indent=2)
        
        return output_path / filename

def main():
    """Test the generator"""
    generator = SimpleTweetGenerator()
    
    # Test single tweet
    print("=== Generating Single Tweet ===")
    single = generator.generate_single_tweet("Docker container optimization")
    print(f"\nGenerated Tweet ({single['content']['character_count']} chars):")
    print(single['content']['full_text'])
    
    # Test thread
    print("\n\n=== Generating Thread ===")
    thread = generator.generate_thread("Building AI agents for code generation", category="AI Agent Testing")
    print(f"\nGenerated Thread ({thread['total_tweets']} tweets):")
    for tweet in thread['tweets']:
        print(f"\nTweet {tweet['position']}:")
        print(tweet['content'])
        print(f"({tweet['character_count']} characters)")
    
    # Save outputs
    single_path = generator.save_output(single)
    thread_path = generator.save_output(thread)
    
    print(f"\n\nSaved outputs to:")
    print(f"- {single_path}")
    print(f"- {thread_path}")

if __name__ == "__main__":
    main()