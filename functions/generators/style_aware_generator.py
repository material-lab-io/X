#!/usr/bin/env python3
"""
Style-aware tweet generator that follows the Twitter/X writing guide
"""

import json
import random
from datetime import datetime
from pathlib import Path
import os

class StyleAwareTweetGenerator:
    def __init__(self):
        """Initialize with style guide and templates"""
        # Helper function to load JSON from multiple locations
        def load_json_file(filename, default=None):
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
            
            print(f"Warning: {filename} not found, using default")
            return default or {}
        
        # Load style guide
        self.style_guide = load_json_file('twitter_style_guide.json', {
            'writing_rules': {'hooks': {'types': {}}}
        })
        
        # Load templates
        templates_data = load_json_file('twitter_templates.json', {'templates': []})
        self.templates = templates_data.get('templates', [])
        
        # Load existing posts for pattern learning
        self.example_posts = load_json_file('extracted_threads_final.json', [])
    
    def generate_hook(self, topic, hook_type=None):
        """Generate a hook following the style guide"""
        hooks = self.style_guide['writing_rules']['hooks']['types']
        
        if not hook_type:
            hook_type = random.choice(list(hooks.keys()))
        
        hook_template = hooks[hook_type]['example']
        
        # Customize based on topic
        if hook_type == 'provocative_question':
            return hook_template.replace('{topic}', topic)
        elif hook_type == 'you_hook':
            # Extract pain point from topic
            pain_point = f"{topic} causing issues"
            return hook_template.replace('{pain_point}', pain_point)
        elif hook_type == 'surprising_statement':
            claim = f"{topic} isn't what you think"
            return hook_template.replace('{bold_claim}', claim)
        
        return f"Let's talk about {topic} 🚀"
    
    def apply_formatting(self, text):
        """Apply style guide formatting rules"""
        # Add line breaks for readability
        sentences = text.split('. ')
        formatted = []
        
        current_para = []
        for sentence in sentences:
            current_para.append(sentence)
            if len(current_para) >= 2:  # Max 2 sentences per paragraph
                formatted.append('. '.join(current_para) + '.')
                formatted.append('')  # Empty line for whitespace
                current_para = []
        
        if current_para:
            formatted.append('. '.join(current_para) + '.')
        
        return '\n'.join(formatted).strip()
    
    def add_functional_emoji(self, text, topic_category):
        """Add functional emoji based on content"""
        emoji_map = self.style_guide['writing_rules']['formatting']['emoji']['patterns']
        
        # Add topic emoji
        if 'docker' in topic_category.lower():
            text = text.replace('Docker', '🐳 Docker', 1)
        elif 'ai' in topic_category.lower() or 'agent' in topic_category.lower():
            text = text.replace('AI', '🤖 AI', 1)
        
        return text
    
    def generate_from_template(self, template_name, context):
        """Generate content using a specific template"""
        template = next(t for t in self.templates if t['template_name'] == template_name)
        
        if template_name == "Build-in-Public: Problem/Solution Walkthrough":
            return self.generate_problem_solution(template, context)
        elif template_name == "First Principles Conceptual Deep Dive":
            return self.generate_conceptual_dive(template, context)
        elif template_name == "Here's My Workflow Tool Share":
            return self.generate_workflow_share(template, context)
    
    def generate_problem_solution(self, template, context):
        """Generate a problem/solution post"""
        structure = template['structure']
        
        # Build the post
        post_parts = []
        
        # Hook
        hook = structure['hook']['example']
        if context.get('problem'):
            hook = f"Ever struggled with {context['problem']}? I just spent hours on this."
        post_parts.append(hook)
        post_parts.append('')  # Whitespace
        
        # Context
        if context.get('feature') and context.get('issue'):
            context_text = f"While building {context['feature']}, I ran into {context['issue']}."
            post_parts.append(context_text)
            post_parts.append('')
        
        # Failed attempts
        if context.get('failed_attempt'):
            fail_text = f"First tried {context['failed_attempt']}. Didn't work because of edge cases."
            post_parts.append(fail_text)
            post_parts.append('')
            post_parts.append('[Screenshot of error]')
            post_parts.append('')
        
        # Solution
        if context.get('solution'):
            solution_text = f"The fix: {context['solution']}"
            post_parts.append('💡 ' + solution_text)
            post_parts.append('')
            post_parts.append('```')
            post_parts.append(context.get('code', '# Your solution code here'))
            post_parts.append('```')
            post_parts.append('')
        
        # Takeaway
        post_parts.append('Hope this saves someone else the debugging time!')
        post_parts.append('')
        post_parts.append('#Docker #DevOps #buildinpublic')
        
        return '\n'.join(post_parts)
    
    def generate_conceptual_dive(self, template, context):
        """Generate a conceptual deep dive thread"""
        structure = template['structure']
        tweets = []
        
        # Tweet 1 - Hook
        topic = context.get('topic', 'this concept')
        analogy = context.get('analogy', 'surprisingly simple')
        tweet1 = f"{topic} might seem complex, but it's actually {analogy}.\n\nLet's break down the core intuition from scratch. 🧵"
        tweets.append(tweet1)
        
        # Tweet 2 - Foundation
        foundation = context.get('foundation', 'the basics')
        tweet2 = f"2/\n\nFirst, understand {foundation}.\n\nThink of it like this: {context.get('foundation_analogy', 'building blocks that stack together')}.\n\n[Diagram showing concept]"
        tweets.append(tweet2)
        
        # Tweet 3 - Key insight
        insight = context.get('key_insight', 'the crucial part')
        tweet3 = f"3/\n\nNow, here's {insight}.\n\nThe magic happens when {context.get('mechanism', 'components interact')}.\n\n[Visual explanation]"
        tweets.append(tweet3)
        
        # Tweet 4 - Practical
        tweet4 = f"4/\n\nIn practice, this means:\n\n```\n{context.get('code_example', '# Practical implementation')}\n```\n\nNotice how it {context.get('code_insight', 'elegantly solves the problem')}."
        tweets.append(tweet4)
        
        # Tweet 5 - Summary
        summary = context.get('summary', f'{topic} in a nutshell')
        tweet5 = f"5/\n\nTL;DR: {summary}\n\nUnderstanding this unlocks {context.get('benefits', 'powerful capabilities')}.\n\n#AI #DeepLearning #TechEducation"
        tweets.append(tweet5)
        
        return tweets
    
    def generate_workflow_share(self, template, context):
        """Generate a workflow/tools share post"""
        structure = template['structure']
        
        # Build the post
        post_parts = []
        
        # Hook
        activity = context.get('activity', 'coding')
        num_tools = context.get('num_tools', 3)
        hook = f"I spend most of my day {activity}.\n\nHere are {num_tools} tools that save me hours every week 👇"
        post_parts.append(hook)
        post_parts.append('')
        
        # Tools
        tools = context.get('tools', [])
        for i, tool in enumerate(tools[:3], 1):
            tool_section = [
                f"{i}. {tool['name']}",
                f"Why it's great: {tool['benefit']}",
                f"My use case: {tool['use_case']}",
                '',
                f"[Terminal GIF showing {tool['name']}]",
                ''
            ]
            post_parts.extend(tool_section)
        
        # Conclusion
        post_parts.append(f"These tools combined save me {context.get('time_saved', 'hours')} per week.")
        post_parts.append('')
        post_parts.append("What's your favorite productivity tool?")
        post_parts.append('')
        post_parts.append('#DevTools #Productivity #Workflow')
        
        return '\n'.join(post_parts)
    
    def validate_content(self, content):
        """Validate content against style guide rules"""
        validations = {
            'has_hook': False,
            'proper_formatting': False,
            'includes_visual': False,
            'appropriate_length': False,
            'has_value': False
        }
        
        lines = content.split('\n') if isinstance(content, str) else content[0].split('\n')
        
        # Check hook (first line should be engaging)
        if lines and len(lines[0]) > 20:
            validations['has_hook'] = True
        
        # Check formatting (should have empty lines)
        if '\n\n' in (content if isinstance(content, str) else '\n'.join(content)):
            validations['proper_formatting'] = True
        
        # Check for visual placeholders
        if '[' in (content if isinstance(content, str) else '\n'.join(content)):
            validations['includes_visual'] = True
        
        # Check length
        char_count = len(content) if isinstance(content, str) else sum(len(t) for t in content)
        if 100 < char_count < 2000:
            validations['appropriate_length'] = True
        
        # Check value (has actionable content)
        value_keywords = ['how', 'why', 'fix', 'solution', 'saves', 'tool', 'tip']
        content_lower = (content if isinstance(content, str) else '\n'.join(content)).lower()
        if any(keyword in content_lower for keyword in value_keywords):
            validations['has_value'] = True
        
        return validations
    
    def generate_style_aware_tweet(self, topic, context=None):
        """Main generation function that follows the style guide"""
        if not context:
            context = {'topic': topic}
        
        # Determine best template based on context
        if 'problem' in context or 'issue' in context:
            template_name = "Build-in-Public: Problem/Solution Walkthrough"
        elif 'explain' in context or 'concept' in context:
            template_name = "First Principles Conceptual Deep Dive"
        elif 'tools' in context or 'workflow' in context:
            template_name = "Here's My Workflow Tool Share"
        else:
            # Default to problem/solution for most practical value
            template_name = "Build-in-Public: Problem/Solution Walkthrough"
            context['problem'] = f"optimizing {topic}"
            context['solution'] = f"a better approach to {topic}"
        
        # Generate content
        content = self.generate_from_template(template_name, context)
        
        # Validate
        validations = self.validate_content(content)
        
        return {
            'content': content,
            'template_used': template_name,
            'validations': validations,
            'generated_at': datetime.now().isoformat()
        }

def main():
    """Demo the style-aware generator"""
    generator = StyleAwareTweetGenerator()
    
    # Example 1: Problem/Solution
    print("=== Problem/Solution Example ===")
    context1 = {
        'problem': 'Docker containers failing in CI but not locally',
        'feature': 'our AI agent testing pipeline',
        'issue': 'non-deterministic test failures',
        'failed_attempt': 'adding sleep timers',
        'solution': 'properly handling async container startup',
        'code': 'docker-compose up -d --wait'
    }
    result1 = generator.generate_style_aware_tweet('Docker CI issues', context1)
    print(result1['content'])
    print(f"\nValidations: {result1['validations']}")
    
    # Example 2: Conceptual Deep Dive
    print("\n\n=== Conceptual Deep Dive Example ===")
    context2 = {
        'topic': 'How AI agents actually work',
        'analogy': 'like a really smart assistant with tools',
        'foundation': 'the agent loop',
        'foundation_analogy': 'a continuous cycle of observe → think → act',
        'key_insight': 'the reasoning step',
        'mechanism': 'the LLM decides which tool to use',
        'code_example': 'agent.run(task="analyze code")',
        'summary': 'Agents = LLM + Tools + Loop',
        'benefits': 'autonomous problem-solving'
    }
    result2 = generator.generate_style_aware_tweet('AI agents', context2)
    if isinstance(result2['content'], list):
        for i, tweet in enumerate(result2['content'], 1):
            print(f"\nTweet {i}:")
            print(tweet)
    
    # Example 3: Workflow Share
    print("\n\n=== Workflow Share Example ===")
    context3 = {
        'activity': 'debugging AI agents in the terminal',
        'num_tools': 3,
        'tools': [
            {
                'name': 'jq',
                'benefit': 'Parse agent JSON logs instantly',
                'use_case': 'cat agent.log | jq .errors'
            },
            {
                'name': 'fzf',
                'benefit': 'Fuzzy search through agent outputs',
                'use_case': 'history | fzf to find that working command'
            },
            {
                'name': 'tmux',
                'benefit': 'Monitor multiple agents simultaneously',
                'use_case': 'Split panes for logs, metrics, and tests'
            }
        ],
        'time_saved': '2-3 hours'
    }
    result3 = generator.generate_style_aware_tweet('terminal workflow', context3)
    print(result3['content'])

if __name__ == "__main__":
    main()