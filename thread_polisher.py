#!/usr/bin/env python3
"""
Thread Polisher and Feedback Annotator
High-skill technical writing assistant for improving LLM-generated Twitter/X threads
"""

import json
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import argparse
import sys

class ThreadPolisher:
    def __init__(self):
        """Initialize the thread polisher with style guide rules"""
        self.style_guide = self._load_style_guide()
        self.templates = self._load_templates()
        
    def _load_style_guide(self) -> Dict:
        """Load style guide from JSON file"""
        try:
            with open('twitter_style_guide.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Warning: twitter_style_guide.json not found")
            return {}
    
    def _load_templates(self) -> Dict:
        """Load templates from JSON file"""
        try:
            with open('twitter_templates.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Fallback templates if file not found
            return {
                "conceptual_deep_dive": {
                    "structure": ["Hook with surprising fact", "Break down concept", "Show implications", "CTA"],
                    "focus": "First principles thinking"
                },
                "workflow_tool_share": {
                    "structure": ["Problem statement", "Tool/workflow intro", "Step-by-step", "Results", "Tips"],
                    "focus": "Practical implementation"
                },
                "build_in_public": {
                    "structure": ["Current challenge", "Solution approach", "Code/implementation", "Lessons learned"],
                    "focus": "Transparency and learning"
                }
            }
    
    def detect_template(self, tweets: List[str]) -> str:
        """Detect which template the thread most closely follows"""
        content = " ".join(tweets).lower()
        
        # Keywords for each template type
        template_indicators = {
            "conceptual_deep_dive": ["understand", "concept", "why", "fundamentally", "principle", "theory"],
            "workflow_tool_share": ["workflow", "tool", "setup", "configure", "step", "process", "how to"],
            "build_in_public": ["building", "struggling", "solved", "learned", "mistake", "progress"]
        }
        
        scores = {}
        for template, keywords in template_indicators.items():
            score = sum(1 for keyword in keywords if keyword in content)
            scores[template] = score
        
        # Return template with highest score, default to workflow
        return max(scores.items(), key=lambda x: x[1])[0] if max(scores.values()) > 0 else "workflow_tool_share"
    
    def polish_hook(self, tweet: str) -> str:
        """Polish the opening hook of a thread"""
        # Remove weak openings
        weak_openings = [
            "here's a thread about",
            "let me tell you about",
            "thread:",
            "🧵",
            "1/"
        ]
        
        tweet_lower = tweet.lower()
        for weak in weak_openings:
            if tweet_lower.startswith(weak):
                tweet = tweet[len(weak):].strip()
        
        # Add strong hook patterns if missing
        if not any(tweet.startswith(p) for p in ["?", "Did you know", "Stop", "Here's how", "I just"]):
            # Analyze content to determine best hook type
            if "?" in tweet:
                # Already has a question, just clean it up
                pass
            elif any(word in tweet.lower() for word in ["slow", "problem", "issue", "struggle"]):
                tweet = f"Struggling with {tweet.lower().replace('struggling with', '').strip()}?"
            elif any(word in tweet.lower() for word in ["fast", "quick", "speed", "optimize"]):
                tweet = f"Want to {tweet.strip()}?"
            else:
                # Default to "Here's how" pattern
                tweet = f"Here's how {tweet.strip()}"
        
        return tweet.strip()
    
    def fix_repetition(self, tweets: List[str]) -> List[str]:
        """Remove repetitive content between tweets"""
        polished = []
        seen_concepts = set()
        
        for i, tweet in enumerate(tweets):
            # Extract key phrases (3-5 word sequences)
            words = tweet.lower().split()
            phrases = set()
            for j in range(len(words) - 2):
                phrase = " ".join(words[j:j+3])
                if len(phrase) > 10:  # Meaningful phrases only
                    phrases.add(phrase)
            
            # Check overlap with previous tweets
            overlap = phrases & seen_concepts
            
            if len(overlap) > 2:  # Significant repetition detected
                # Rephrase or skip repetitive parts
                if i > 0:
                    tweet = f"Building on that: {tweet}"
                    # Remove the repetitive phrase
                    for phrase in overlap:
                        tweet = tweet.replace(phrase, "").replace("  ", " ")
            
            seen_concepts.update(phrases)
            polished.append(tweet.strip())
        
        return polished
    
    def enhance_technical_depth(self, tweet: str, context: str = "") -> str:
        """Add technical depth to generic statements"""
        # Map generic terms to specific technical details
        enhancements = {
            "faster": "up to 10x faster",
            "better performance": "reduced latency by 80%",
            "more efficient": "O(log n) vs O(n²)",
            "saves time": "cuts build time from 15min to 3min",
            "improves": "boosts throughput",
            "optimize": "optimize with caching strategies",
            "ai model": "transformer-based model",
            "container": "Docker container with multi-stage builds"
        }
        
        for generic, specific in enhancements.items():
            if generic in tweet.lower() and specific not in tweet:
                tweet = tweet.replace(generic, specific)
                tweet = tweet.replace(generic.capitalize(), specific)
        
        return tweet
    
    def add_code_snippets(self, tweet: str) -> str:
        """Add inline code formatting where appropriate"""
        # Pattern for common code elements
        code_patterns = [
            (r'\b(docker run|docker build|git|npm|pip install|python|bash|curl)\b', r'`\1`'),
            (r'\b([A-Za-z]+\.[A-Za-z]+\(\))\b', r'`\1`'),  # method calls
            (r'\b(--?[a-z-]+)\b', r'`\1`'),  # CLI flags
            (r'\b([A-Z_]+=[^\s]+)\b', r'`\1`'),  # Environment variables
        ]
        
        for pattern, replacement in code_patterns:
            tweet = re.sub(pattern, replacement, tweet)
        
        # Avoid double backticks
        tweet = tweet.replace("``", "`")
        
        return tweet
    
    def strengthen_cta(self, tweet: str) -> str:
        """Strengthen call-to-action in final tweet"""
        weak_ctas = [
            "hope this helps",
            "that's it",
            "the end",
            "thanks for reading"
        ]
        
        strong_ctas = [
            "What's your approach? Reply below 👇",
            "Have you tried this? Share your results!",
            "Follow for more deep dives like this",
            "DM me if you need help implementing this",
            "Which technique surprised you most?",
            "RT if this saved you debugging time!"
        ]
        
        # Remove weak CTAs
        tweet_lower = tweet.lower()
        for weak in weak_ctas:
            if weak in tweet_lower:
                tweet = tweet.replace(weak, "").replace(weak.capitalize(), "")
        
        # Add strong CTA if missing
        if not any(cta.lower() in tweet_lower for cta in ["reply", "share", "follow", "dm", "?"]):
            import random
            tweet = tweet.strip() + "\n\n" + random.choice(strong_ctas)
        
        return tweet.strip()
    
    def polish_thread(self, tweets: List[str], template: Optional[str] = None) -> Tuple[List[str], str]:
        """Main polishing function - Phase 1"""
        # Detect template if not specified
        if not template:
            template = self.detect_template(tweets)
        
        polished_tweets = tweets.copy()
        
        # 1. Polish the hook (first tweet)
        if polished_tweets:
            polished_tweets[0] = self.polish_hook(polished_tweets[0])
        
        # 2. Remove repetition
        polished_tweets = self.fix_repetition(polished_tweets)
        
        # 3. Enhance technical depth
        for i in range(len(polished_tweets)):
            polished_tweets[i] = self.enhance_technical_depth(polished_tweets[i])
            polished_tweets[i] = self.add_code_snippets(polished_tweets[i])
        
        # 4. Strengthen CTA (last tweet)
        if polished_tweets:
            polished_tweets[-1] = self.strengthen_cta(polished_tweets[-1])
        
        # 5. Ensure proper numbering
        total = len(polished_tweets)
        for i in range(len(polished_tweets)):
            # Remove existing numbering
            polished_tweets[i] = re.sub(r'^\d+/\d*\s*', '', polished_tweets[i])
            # Add consistent numbering
            polished_tweets[i] = f"{i+1}/{total} {polished_tweets[i]}"
        
        return polished_tweets, template
    
    def analyze_clarity(self, tweets: List[str]) -> float:
        """Score clarity from 1-5"""
        clarity_score = 5.0
        
        for tweet in tweets:
            # Deduct for overly long sentences
            sentences = re.split(r'[.!?]', tweet)
            for sentence in sentences:
                if len(sentence.split()) > 25:
                    clarity_score -= 0.2
            
            # Deduct for jargon without explanation
            jargon = ["DDPM", "transformer", "diffusion", "embeddings", "tokenizer"]
            for term in jargon:
                if term in tweet and "(" not in tweet:  # No explanation provided
                    clarity_score -= 0.1
            
            # Deduct for passive voice
            if any(passive in tweet for passive in ["was done", "is being", "has been"]):
                clarity_score -= 0.1
        
        return max(1.0, round(clarity_score, 1))
    
    def analyze_tone_consistency(self, tweets: List[str]) -> float:
        """Score tone consistency from 1-5"""
        tone_markers = {
            "casual": ["hey", "okay", "gonna", "wanna", "lol"],
            "formal": ["therefore", "moreover", "consequently", "thus"],
            "technical": ["implementation", "architecture", "algorithm", "optimization"],
            "engaging": ["you", "your", "let's", "imagine", "think about"]
        }
        
        tweet_tones = []
        for tweet in tweets:
            tweet_lower = tweet.lower()
            tone_scores = {}
            for tone, markers in tone_markers.items():
                score = sum(1 for marker in markers if marker in tweet_lower)
                tone_scores[tone] = score
            
            dominant_tone = max(tone_scores.items(), key=lambda x: x[1])[0]
            tweet_tones.append(dominant_tone)
        
        # Calculate consistency
        most_common_tone = max(set(tweet_tones), key=tweet_tones.count)
        consistency = tweet_tones.count(most_common_tone) / len(tweet_tones)
        
        return round(3.0 + (consistency * 2), 1)  # Scale to 3-5 range
    
    def analyze_engagement_potential(self, tweets: List[str]) -> float:
        """Score engagement potential from 1-5"""
        score = 3.0  # Base score
        
        full_thread = " ".join(tweets)
        
        # Boost for questions
        score += 0.5 * len(re.findall(r'\?', full_thread))
        
        # Boost for specific examples
        if any(pattern in full_thread for pattern in ["for example", "e.g.", "here's how", "step "]):
            score += 0.5
        
        # Boost for results/metrics
        if re.search(r'\d+[x%]|from \d+ to \d+', full_thread):
            score += 0.5
        
        # Boost for emojis (but not too many)
        emoji_count = len(re.findall(r'[\U0001F300-\U0001F9FF]', full_thread))
        if 2 <= emoji_count <= 8:
            score += 0.3
        
        # Boost for CTA
        if any(cta in full_thread.lower() for cta in ["reply", "share", "what do you think", "dm me"]):
            score += 0.4
        
        return min(5.0, round(score, 1))
    
    def check_completeness(self, tweets: List[str], template: str) -> bool:
        """Check if thread follows template structure"""
        template_requirements = {
            "conceptual_deep_dive": ["hook", "explanation", "implication"],
            "workflow_tool_share": ["problem", "solution", "steps"],
            "build_in_public": ["challenge", "approach", "result"]
        }
        
        requirements = template_requirements.get(template, [])
        full_content = " ".join(tweets).lower()
        
        return all(req in full_content or any(syn in full_content for syn in [req + "s", req + "ed"]) 
                  for req in requirements)
    
    def generate_feedback(self, original: List[str], polished: List[str], template: str) -> Dict:
        """Generate detailed feedback - Phase 2"""
        feedback = {
            "templateUsed": template.replace("_", " ").title(),
            "clarityScore": self.analyze_clarity(polished),
            "toneConsistency": self.analyze_tone_consistency(polished),
            "engagementPotential": self.analyze_engagement_potential(polished),
            "completeness": self.check_completeness(polished, template),
            "actionableFeedback": []
        }
        
        # Generate specific feedback
        actionable = []
        
        # Check for repetition
        word_freq = {}
        for tweet in polished:
            for word in tweet.lower().split():
                if len(word) > 4:  # Significant words only
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        overused = [word for word, count in word_freq.items() if count > len(polished)]
        if overused:
            actionable.append(f"The word '{overused[0]}' appears too frequently - vary your vocabulary")
        
        # Check for code examples
        has_code = any('`' in tweet for tweet in polished)
        if not has_code and template == "workflow_tool_share":
            actionable.append("Add a real code snippet or CLI example to make it more practical")
        
        # Check hook strength
        if polished and not any(polished[0].startswith(p) for p in ["?", "Did", "Stop", "Here's", "Want"]):
            actionable.append("Opening hook could be stronger - start with a question or bold statement")
        
        # Check CTA
        if polished and not any(word in polished[-1].lower() for word in ["reply", "share", "follow", "dm", "?"]):
            actionable.append("Ending CTA could be stronger - encourage discussion or sharing")
        
        # Check thread length
        if len(polished) < 3:
            actionable.append("Thread is too short - expand with more details or examples")
        elif len(polished) > 10:
            actionable.append("Thread is too long - consider splitting into multiple threads")
        
        feedback["actionableFeedback"] = actionable if actionable else ["Thread is well-structured!"]
        
        return feedback


def main():
    """CLI interface for thread polishing"""
    parser = argparse.ArgumentParser(description="Polish and analyze Twitter/X threads")
    parser.add_argument("input_file", help="JSON file containing raw thread")
    parser.add_argument("--template", choices=["conceptual_deep_dive", "workflow_tool_share", "build_in_public"],
                        help="Template to use (auto-detected if not specified)")
    parser.add_argument("--output", help="Output file for polished thread")
    parser.add_argument("--feedback-only", action="store_true", help="Only generate feedback, don't polish")
    
    args = parser.parse_args()
    
    # Load input thread
    try:
        with open(args.input_file, 'r') as f:
            data = json.load(f)
            
        # Extract tweets from various possible formats
        if isinstance(data, list):
            tweets = data
        elif isinstance(data, dict):
            tweets = data.get('generatedTweets', data.get('tweets', data.get('thread', [])))
        else:
            print("Error: Invalid input format")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error loading input file: {e}")
        sys.exit(1)
    
    # Initialize polisher
    polisher = ThreadPolisher()
    
    if args.feedback_only:
        # Only analyze, don't polish
        template = args.template or polisher.detect_template(tweets)
        feedback = polisher.generate_feedback(tweets, tweets, template)
        print(json.dumps(feedback, indent=2))
    else:
        # Polish and analyze
        polished_tweets, template = polisher.polish_thread(tweets, args.template)
        feedback = polisher.generate_feedback(tweets, polished_tweets, template)
        
        result = {
            "original": tweets,
            "polished": polished_tweets,
            "feedback": feedback,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Output results
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Results saved to {args.output}")
        else:
            print("=== POLISHED THREAD ===")
            for tweet in polished_tweets:
                print(f"\n{tweet}")
                print(f"[{len(tweet)} characters]")
            
            print("\n=== FEEDBACK ===")
            print(json.dumps(feedback, indent=2))


if __name__ == "__main__":
    main()