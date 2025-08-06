#!/usr/bin/env python3
"""
Analyze the extracted Twitter/X posts to understand patterns and styles
"""

import json
from pathlib import Path
from collections import Counter, defaultdict
import statistics
import re

class PostAnalyzer:
    def __init__(self, posts_file: str = "extracted_threads_final.json"):
        """Initialize analyzer with posts data"""
        with open(posts_file, 'r') as f:
            self.posts = json.load(f)
    
    def analyze_all(self):
        """Run all analyses and return comprehensive report"""
        report = {
            "basic_stats": self.get_basic_stats(),
            "content_patterns": self.analyze_content_patterns(),
            "style_analysis": self.analyze_style(),
            "engagement_patterns": self.analyze_engagement_patterns(),
            "technical_depth": self.analyze_technical_depth()
        }
        return report
    
    def get_basic_stats(self):
        """Get basic statistics about the dataset"""
        stats = {
            "total_posts": len(self.posts),
            "content_categories": Counter([p['metadata']['contentCategory'] for p in self.posts]),
            "authors": Counter([p['metadata']['author'] for p in self.posts]),
            "tweet_types": Counter([p['metadata']['tweetType'] for p in self.posts]),
            "audience_levels": Counter([p['metadata']['targetAudienceLevel'] for p in self.posts]),
            "thread_vs_single": {
                "threads": sum(1 for p in self.posts if p['threadInfo']['isThread']),
                "single": sum(1 for p in self.posts if not p['threadInfo']['isThread'])
            }
        }
        return stats
    
    def analyze_content_patterns(self):
        """Analyze content structure patterns"""
        patterns = {
            "hook_patterns": [],
            "content_lengths": [],
            "hashtag_usage": [],
            "mention_usage": [],
            "link_usage": [],
            "emoji_usage": []
        }
        
        for post in self.posts:
            content = post['content']
            
            # Hook analysis
            if content['hook']:
                patterns['hook_patterns'].append({
                    "hook": content['hook'],
                    "length": len(content['hook']),
                    "starts_with_question": content['hook'].strip().endswith('?'),
                    "has_emoji": bool(re.search(r'[^\w\s,.\'"!?-]', content['hook']))
                })
            
            # Content length
            patterns['content_lengths'].append(len(content['mainBody']))
            
            # Feature usage
            patterns['hashtag_usage'].append(len(content['hashtags']))
            patterns['mention_usage'].append(len(content['mentions']))
            patterns['link_usage'].append(len(content['links']))
            patterns['emoji_usage'].append(len(content['emojis']))
        
        # Calculate statistics
        return {
            "avg_content_length": statistics.mean(patterns['content_lengths']),
            "avg_hook_length": statistics.mean([h['length'] for h in patterns['hook_patterns']]),
            "hooks_with_questions": sum(1 for h in patterns['hook_patterns'] if h['starts_with_question']),
            "avg_hashtags": statistics.mean(patterns['hashtag_usage']),
            "avg_mentions": statistics.mean(patterns['mention_usage']),
            "avg_links": statistics.mean(patterns['link_usage']),
            "posts_with_links": sum(1 for l in patterns['link_usage'] if l > 0),
            "hook_examples": [h['hook'] for h in patterns['hook_patterns'][:5]]
        }
    
    def analyze_style(self):
        """Analyze writing style and tone"""
        tone_combinations = []
        keywords_by_category = defaultdict(Counter)
        
        for post in self.posts:
            # Tone analysis
            tone_combinations.append(tuple(sorted(post['metadata']['tone'])))
            
            # Keyword extraction by category
            category = post['metadata']['contentCategory']
            content = post['content']['mainBody'].lower()
            
            # Extract technical terms (simplified)
            words = re.findall(r'\b[a-z]+\b', content)
            technical_terms = [w for w in words if len(w) > 4 and w not in common_words]
            keywords_by_category[category].update(technical_terms)
        
        # Get top keywords per category
        top_keywords = {}
        for category, counter in keywords_by_category.items():
            top_keywords[category] = counter.most_common(10)
        
        return {
            "tone_combinations": Counter(tone_combinations).most_common(5),
            "top_keywords_by_category": top_keywords
        }
    
    def analyze_engagement_patterns(self):
        """Analyze what makes posts engaging (based on available metrics)"""
        high_difficulty_posts = [p for p in self.posts if p['contentInsights']['contentDifficulty'] >= 4]
        
        return {
            "difficulty_distribution": Counter([p['contentInsights']['contentDifficulty'] for p in self.posts]),
            "high_difficulty_topics": [p['metadata']['contentCategory'] for p in high_difficulty_posts],
            "writing_style_tags": Counter([tag for p in self.posts for tag in p['contentInsights']['writingStyleTags']])
        }
    
    def analyze_technical_depth(self):
        """Analyze technical content patterns"""
        technical_indicators = {
            "code_mentions": 0,
            "tools_mentions": 0,
            "metrics_mentions": 0,
            "architecture_mentions": 0
        }
        
        technical_keywords = {
            "code": ["code", "function", "class", "method", "api", "sdk", "library"],
            "tools": ["docker", "kubernetes", "github", "git", "npm", "pip", "bash"],
            "metrics": ["performance", "latency", "throughput", "accuracy", "speed"],
            "architecture": ["architecture", "design", "pattern", "framework", "model", "pipeline"]
        }
        
        for post in self.posts:
            content = post['content']['mainBody'].lower()
            
            for category, keywords in technical_keywords.items():
                if any(keyword in content for keyword in keywords):
                    technical_indicators[f"{category}_mentions"] += 1
        
        return technical_indicators
    
    def generate_report(self):
        """Generate a comprehensive analysis report"""
        analysis = self.analyze_all()
        
        report = f"""
# Twitter/X Posts Analysis Report

## Basic Statistics
- Total posts analyzed: {analysis['basic_stats']['total_posts']}
- Thread vs Single: {analysis['basic_stats']['thread_vs_single']['threads']} threads, {analysis['basic_stats']['thread_vs_single']['single']} single posts

## Content Categories
"""
        for category, count in analysis['basic_stats']['content_categories'].most_common():
            report += f"- {category}: {count} posts\n"
        
        report += f"""
## Content Patterns
- Average content length: {analysis['content_patterns']['avg_content_length']:.0f} characters
- Average hook length: {analysis['content_patterns']['avg_hook_length']:.0f} characters
- Posts with questions in hook: {analysis['content_patterns']['hooks_with_questions']}
- Average hashtags per post: {analysis['content_patterns']['avg_hashtags']:.1f}
- Posts with links: {analysis['content_patterns']['posts_with_links']}

## Writing Style
Most common tone combinations:
"""
        for tones, count in analysis['style_analysis']['tone_combinations'][:3]:
            report += f"- {', '.join(tones)}: {count} posts\n"
        
        report += f"""
## Technical Depth Indicators
- Posts mentioning code concepts: {analysis['technical_depth']['code_mentions']}
- Posts mentioning tools: {analysis['technical_depth']['tools_mentions']}
- Posts mentioning metrics: {analysis['technical_depth']['metrics_mentions']}
- Posts mentioning architecture: {analysis['technical_depth']['architecture_mentions']}

## Example Hooks
"""
        for hook in analysis['content_patterns']['hook_examples']:
            report += f"- \"{hook}\"\n"
        
        return report

# Common words to filter out (simplified)
common_words = {
    "the", "and", "for", "with", "that", "this", "from", "have", "will",
    "can", "are", "not", "but", "what", "when", "how", "more", "been",
    "some", "would", "there", "which", "their", "than", "into", "only"
}

def main():
    analyzer = PostAnalyzer()
    report = analyzer.generate_report()
    
    # Save report
    with open("posts_analysis_report.md", "w") as f:
        f.write(report)
    
    print(report)
    print("\nReport saved to: posts_analysis_report.md")
    
    # Also save detailed JSON analysis
    detailed_analysis = analyzer.analyze_all()
    with open("posts_analysis_detailed.json", "w") as f:
        json.dump(detailed_analysis, f, indent=2)
    
    print("Detailed analysis saved to: posts_analysis_detailed.json")

if __name__ == "__main__":
    main()