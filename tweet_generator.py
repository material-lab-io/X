#!/usr/bin/env python3
"""
Multi-model Twitter/X post generator using Gemini, Claude, and other LLMs
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Union
import google.generativeai as genai
from datetime import datetime
import random

class TweetGenerator:
    def __init__(self, config_path: str = "config.json"):
        """Initialize the tweet generator with configuration"""
        self.config = self._load_config(config_path)
        self.posts_data = self._load_posts_data()
        self.setup_gemini()
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        with open(config_path, 'r') as f:
            return json.load(f)
    
    def _load_posts_data(self) -> List[Dict]:
        """Load the extracted posts dataset"""
        posts_path = Path(self.config['paths']['posts_data'])
        with open(posts_path, 'r') as f:
            return json.load(f)
    
    def setup_gemini(self):
        """Configure Gemini API"""
        genai.configure(api_key=self.config['api_keys']['gemini'])
        self.gemini_model = genai.GenerativeModel('gemini-pro')
        
    def get_relevant_examples(self, topic: str, content_type: str = "single", n: int = 3) -> List[Dict]:
        """Retrieve relevant examples from the dataset"""
        # Filter by content category if relevant
        relevant_posts = []
        
        topic_keywords = topic.lower().split()
        
        for post in self.posts_data:
            # Check content category
            category = post['metadata']['contentCategory'].lower()
            content = post['content']['mainBody'].lower()
            
            # Score relevance based on keyword matches
            relevance_score = 0
            for keyword in topic_keywords:
                if keyword in category:
                    relevance_score += 2
                if keyword in content:
                    relevance_score += 1
            
            if relevance_score > 0:
                relevant_posts.append((relevance_score, post))
        
        # Sort by relevance and return top n
        relevant_posts.sort(key=lambda x: x[0], reverse=True)
        return [post for _, post in relevant_posts[:n]]
    
    def build_generation_prompt(self, topic: str, content_type: str, tone: str, examples: List[Dict]) -> str:
        """Build a comprehensive prompt for tweet generation"""
        prompt = f"""You are an expert technical content creator for Twitter/X, specializing in AI, coding, and developer tools.

TASK: Generate a {content_type} Twitter/X post about: {topic}

TONE: {tone}

STYLE GUIDELINES:
- Use clear, concise technical language
- Include relevant emojis sparingly (1-2 per tweet)
- Add 2-3 relevant hashtags
- Hook readers in the first line
- Provide actionable insights or learnings
- Keep single tweets under 280 characters
- For threads, each tweet should be 200-250 characters

EXAMPLES OF HIGH-QUALITY POSTS:
"""
        
        # Add examples
        for i, example in enumerate(examples, 1):
            prompt += f"\nExample {i}:\n"
            prompt += f"Hook: {example['content']['hook']}\n"
            prompt += f"Content: {example['content']['mainBody'][:200]}...\n"
            prompt += f"Style: {', '.join(example['metadata']['tone'])}\n"
        
        if content_type == "thread":
            prompt += "\n\nGenerate a thread with 5-7 tweets. Format as:\n"
            prompt += "Tweet 1: [content]\nTweet 2: [content]\n..."
        else:
            prompt += "\n\nGenerate a single tweet with high engagement potential."
        
        prompt += "\n\nInclude relevant links or resources if applicable."
        
        return prompt
    
    def generate_single_tweet(self, topic: str, tone: str = "Technical") -> Dict:
        """Generate a single tweet using Gemini"""
        examples = self.get_relevant_examples(topic, "single", n=3)
        prompt = self.build_generation_prompt(topic, "single tweet", tone, examples)
        
        try:
            response = self.gemini_model.generate_content(prompt)
            
            # Parse the response
            tweet_content = response.text.strip()
            
            # Extract components (basic parsing - can be enhanced)
            lines = tweet_content.split('\n')
            main_content = lines[0] if lines else tweet_content
            
            # Extract hashtags
            import re
            hashtags = re.findall(r'#\w+', tweet_content)
            
            # Extract links
            links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', tweet_content)
            
            result = {
                "generated_at": datetime.now().isoformat(),
                "model": "gemini-pro",
                "topic": topic,
                "tone": tone,
                "content": {
                    "full_text": tweet_content,
                    "main_text": main_content,
                    "hashtags": hashtags,
                    "links": links
                },
                "metadata": {
                    "character_count": len(tweet_content),
                    "examples_used": len(examples)
                }
            }
            
            return result
            
        except Exception as e:
            print(f"Error generating tweet: {e}")
            return None
    
    def generate_thread(self, topic: str, tone: str = "Technical", length: int = 5) -> Dict:
        """Generate a thread of tweets using Gemini"""
        examples = self.get_relevant_examples(topic, "thread", n=3)
        prompt = self.build_generation_prompt(topic, f"thread of {length} tweets", tone, examples)
        
        try:
            response = self.gemini_model.generate_content(prompt)
            
            # Parse the thread
            thread_text = response.text.strip()
            tweets = []
            
            # Split by "Tweet" markers or newlines
            import re
            tweet_parts = re.split(r'Tweet \d+:|^\d+\.|^\d+\)', thread_text, flags=re.MULTILINE)
            tweet_parts = [part.strip() for part in tweet_parts if part.strip()]
            
            for i, tweet in enumerate(tweet_parts[:length], 1):
                tweets.append({
                    "position": i,
                    "content": tweet.strip(),
                    "character_count": len(tweet.strip())
                })
            
            result = {
                "generated_at": datetime.now().isoformat(),
                "model": "gemini-pro",
                "topic": topic,
                "tone": tone,
                "thread_type": "generated",
                "tweets": tweets,
                "metadata": {
                    "total_tweets": len(tweets),
                    "total_characters": sum(t["character_count"] for t in tweets),
                    "examples_used": len(examples)
                }
            }
            
            return result
            
        except Exception as e:
            print(f"Error generating thread: {e}")
            return None
    
    def save_generation(self, content: Dict, filename: Optional[str] = None):
        """Save generated content to file"""
        output_dir = Path(self.config['paths']['output_dir'])
        output_dir.mkdir(exist_ok=True)
        
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            content_type = "thread" if "tweets" in content else "single"
            filename = f"{content_type}_{timestamp}.json"
        
        output_path = output_dir / filename
        with open(output_path, 'w') as f:
            json.dump(content, f, indent=2)
        
        print(f"Saved to: {output_path}")
        return output_path

def main():
    """Example usage"""
    generator = TweetGenerator()
    
    # Example 1: Generate a single tweet
    print("Generating single tweet about Docker optimization...")
    single_tweet = generator.generate_single_tweet(
        topic="Docker container optimization techniques",
        tone="Technical"
    )
    
    if single_tweet:
        print("\nGenerated Tweet:")
        print(single_tweet['content']['full_text'])
        print(f"\nCharacter count: {single_tweet['metadata']['character_count']}")
        generator.save_generation(single_tweet)
    
    # Example 2: Generate a thread
    print("\n\nGenerating thread about AI agents...")
    thread = generator.generate_thread(
        topic="Building autonomous AI agents for code generation",
        tone="Technical",
        length=5
    )
    
    if thread:
        print("\nGenerated Thread:")
        for tweet in thread['tweets']:
            print(f"\nTweet {tweet['position']}:")
            print(tweet['content'])
        generator.save_generation(thread)

if __name__ == "__main__":
    main()