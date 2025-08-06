#!/usr/bin/env python3
"""
Comprehensive Twitter/X Content Generator Server
With proper folder structure imports
"""

from flask import Flask, render_template_string, request, jsonify, send_file
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import logging
import base64
import io
import random
import re

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))

# Add functions directory to path
sys.path.append(str(Path(__file__).parent / 'functions' / 'generators'))
sys.path.append(str(Path(__file__).parent / 'functions' / 'diagrams'))

# Import the dynamic Gemini generator
try:
    # Try new location first
    from functions.generators.gemini_dynamic_generator import GeminiDynamicGenerator, generate_dynamic_content
    gemini_api_key = "AIzaSyAMOvO0_b0o5LdvZgZBVqZ3mSfBwBukzgY"
    gemini_generator = GeminiDynamicGenerator(gemini_api_key)
    print("✓ Loaded Gemini dynamic generator from functions/")
except:
    try:
        # Fallback to original location
        from gemini_dynamic_generator import GeminiDynamicGenerator, generate_dynamic_content
        gemini_api_key = "AIzaSyAMOvO0_b0o5LdvZgZBVqZ3mSfBwBukzgY"
        gemini_generator = GeminiDynamicGenerator(gemini_api_key)
        print("✓ Loaded Gemini dynamic generator from root")
    except Exception as e:
        print(f"⚠️ Could not load Gemini generator: {e}")
        gemini_generator = None

# Import enhanced Gemini generator
try:
    from functions.generators.enhanced_gemini_generator import create_enhanced_content
    print("✓ Loaded enhanced Gemini generator from functions/")
    enhanced_generator_available = True
except:
    try:
        from enhanced_gemini_generator import create_enhanced_content
        print("✓ Loaded enhanced Gemini generator from root")
        enhanced_generator_available = True
    except Exception as e:
        print(f"⚠️ Could not load enhanced generator: {e}")
        enhanced_generator_available = False

# Legacy generators (kept for fallback)
try:
    from functions.generators.simple_tweet_generator import SimpleTweetGenerator
    simple_generator = SimpleTweetGenerator()
    print("✓ Loaded simple generator from functions/")
except:
    try:
        from simple_tweet_generator import SimpleTweetGenerator
        simple_generator = SimpleTweetGenerator()
        print("✓ Loaded simple generator from root")
    except Exception as e:
        print(f"⚠️ Could not load simple generator: {e}")
        simple_generator = None

# Diagram generator
try:
    from functions.diagrams.mermaid_diagram_generator import MermaidDiagramGenerator
    diagram_generator = MermaidDiagramGenerator()
    print("✓ Loaded diagram generator from functions/")
except:
    try:
        from mermaid_diagram_generator import MermaidDiagramGenerator
        diagram_generator = MermaidDiagramGenerator()
        print("✓ Loaded diagram generator from root")
    except Exception as e:
        print(f"⚠️ Could not load diagram generator: {e}")
        diagram_generator = None# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load configuration
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
        API_KEYS = {
            'gemini': config.get('gemini_api_key') or config.get('api_keys', {}).get('gemini'),
            'claude': config.get('claude_api_key') or config.get('api_keys', {}).get('claude'),
            'openai': config.get('openai_api_key') or config.get('api_keys', {}).get('openai')
        }
except Exception as e:
    logger.warning(f"Could not load config.json: {e}")
    API_KEYS = {}

def optimize_tweet_length(text, min_chars, max_chars, is_final=False):
    """Optimize tweet to fit within character limits while maintaining completeness"""
    
    # First, clean up the text
    text = re.sub(r'\s+', ' ', text).strip()
    
    # If already in range, return as is
    if min_chars <= len(text) <= max_chars:
        return text
    
    # If too short, add context or expand
    if len(text) < min_chars:
        if is_final:
            # Add a call-to-action for final tweets
            additions = [
                "\n\nFollow for more technical insights.",
                "\n\nWhat's your experience with this?",
                "\n\nTry this approach and let me know!",
                "\n\nMore deep dives coming soon.",
            ]
            for addition in additions:
                if len(text + addition) <= max_chars:
                    return text + addition
        return text
    
    # If too long, intelligently truncate
    if len(text) > max_chars:
        # Try to break at sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', text)
        result = ""
        
        for sentence in sentences:
            if len(result + sentence) <= max_chars - 3:  # Leave room for "..."
                result += sentence + " "
            else:
                # If we haven't added any sentences yet, truncate the first one
                if not result and len(sentence) > max_chars - 3:
                    return sentence[:max_chars-3] + "..."
                break
        
        result = result.strip()
        if result and not result[-1] in '.!?':
            result += "..."
            
        return result
    
    return text

def generate_optimized_tweet_content(topic, style, position=1, total=1, context=""):
    """Generate optimized tweet content following specific length guidelines"""
    
    # Define character limits based on position
    if position == 1:  # First tweet (hook)
        min_chars, max_chars = 180, 240
    elif position == total:  # Final tweet
        min_chars, max_chars = 150, 220
    else:  # Middle tweets
        min_chars, max_chars = 180, 260
    
    # Template structures for different styles
    style_templates = {
        'explanatory': {
            'single': [
                "{topic} explained: {core_insight}. The key is {key_point} which enables {benefit}.",
                "Understanding {topic} starts with {foundation}. Once you grasp this, {outcome} becomes clear.",
                "The secret to {topic}? {insight}. This changes how you approach {application}.",
            ],
            'first': [
                "Let me explain {topic} in a way that clicked for me:",
                "After years of {topic}, here's what actually matters:",
                "The truth about {topic} that nobody talks about:",
            ],
            'middle': [
                "The core principle: {principle}.\n\nThis means {implication} in practice.",
                "Key insight: {insight}.\n\nWhy? Because {reasoning}.",
                "Most miss this: {overlooked}.\n\nBut it's crucial for {importance}.",
            ],
            'final': [
                "Bottom line: {summary}.\n\nStart with {first_step}.",
                "Remember: {key_takeaway}.\n\nThis transforms {transformation}.",
                "Try this: {action}.\n\nYou'll see {result} immediately.",
            ]
        },
        'observational': {
            'single': [
                "Pattern I've noticed with {topic}: {observation}. The implications are {implications}.",
                "Interesting: {topic} always {pattern}. This suggests {conclusion}.",
                "After seeing {topic} in production: {insight}. Changes everything.",
            ],
            'first': [
                "Something fascinating about {topic} I discovered:",
                "Pattern recognition time. {topic} edition:",
                "Observation from the trenches on {topic}:",
            ],
            'middle': [
                "What I see: {observation}.\n\nWhat it means: {meaning}.",
                "The pattern: {pattern}.\n\nThe exception: {exception}.",
                "Success cases: {success}.\n\nFailure cases: {failure}.",
            ],
            'final': [
                "The pattern is clear: {conclusion}.",
                "Watch for this in your work.",
                "Once you see it, you can't unsee it.",
            ]
        },
        'first-principles': {
            'single': [
                "{topic} fundamentally = {equation}. Everything else is implementation detail.",
                "Break {topic} to atoms: {components}. Rebuild: {reconstruction}.",
                "Physics of {topic}: {constraints} + {forces} = {outcome}.",
            ],
            'first': [
                "Let's derive {topic} from first principles:",
                "Forget what you know about {topic}. Start from physics:",
                "Breaking {topic} down to fundamental truths:",
            ],
            'middle': [
                "Constraint 1: {constraint1}.\nConstraint 2: {constraint2}.\n\nResult: {result}.",
                "Base principle: {principle}.\n\nThis forces {consequence}.",
                "The atoms: {atoms}.\n\nThe bonds: {bonds}.",
            ],
            'final': [
                "Therefore: {conclusion}.\n\nElegant, inevitable.",
                "The rest is just engineering.",
                "Simple laws, complex outcomes.",
            ]
        },
        'tool-comparison': {
            'single': [
                "{tool1} vs {tool2}: {tool1} excels at {strength1}, {tool2} at {strength2}. Choose based on {criteria}.",
                "Used both {tool1} and {tool2}. Winner depends on {context}. {tool1} for {use1}, {tool2} for {use2}.",
                "{tool1} vs {tool2} isn't about features. It's about {philosophy}.",
            ],
            'first': [
                "{tool1} vs {tool2} after 6 months with both:",
                "The real difference between {tool1} and {tool2}:",
                "Stop debating {tool1} vs {tool2}. Here's what matters:",
            ],
            'middle': [
                "{tool1} wins:\n• {win1}\n• {win2}\n\n{tool2} wins:\n• {win3}\n• {win4}",
                "Performance: {tool1} {perf1}.\n{tool2} {perf2}.\n\nContext matters.",
                "Developer experience:\n{tool1}: {dx1}\n{tool2}: {dx2}",
            ],
            'final': [
                "Pick {tool1} if {criteria1}.\nPick {tool2} if {criteria2}.",
                "Both are excellent. Know your constraints.",
                "My choice: {choice} because {reason}.",
            ]
        },
        'debugging-story': {
            'single': [
                "Bug that haunted me: {bug}. Root cause: {cause}. Lesson: {lesson}.",
                "Spent 6 hours on {bug}. Solution was {solution}. Always check {check}.",
                "Production down. Cause: {cause}. Fix: {fix}. Now I always {practice}.",
            ],
            'first': [
                "3am. Production down. This is that story:",
                "The bug that taught me {lesson}:",
                "Debugging war story from last week:",
            ],
            'middle': [
                "Symptom: {symptom}.\nHypothesis: {hypothesis}.\nReality: {reality}.",
                "Tried: {attempt1}. Failed.\nTried: {attempt2}. Failed.\nThen: {breakthrough}.",
                "The logs said {log}.\nThe metrics showed {metric}.\nBut the real issue? {issue}.",
            ],
            'final': [
                "Lesson: {lesson}.\n\nNow part of our runbook.",
                "Cost: 6 hours.\nValue: Priceless knowledge.",
                "Always {practice}. Always.",
            ]
        },
        'build-in-public': {
            'single': [
                "{project} update: {milestone}! {metric} and growing. Next: {next_goal}.",
                "Building {project}: {achievement}. Learned {lesson}. Pivoting {pivot}.",
                "{project} hit {metric}! The key was {key_factor}. Building in public works.",
            ],
            'first': [
                "{project} update - Day {day}:",
                "Big milestone for {project}:",
                "Building in public update:",
            ],
            'middle': [
                "Stats:\n• {metric1}\n• {metric2}\n• {metric3}\n\nFeeling {emotion}.",
                "What worked: {success}.\n\nWhat didn't: {failure}.",
                "User feedback: \"{feedback}\"\n\nImplementing {change}.",
            ],
            'final': [
                "Next: {next_step}.\n\nFollow the journey.",
                "Lesson: {lesson}.\n\nOnward!",
                "Thanks for the support! 🚀",
            ]
        },
        'problem-solution': {
            'single': [
                "Problem: {problem}. Solution: {solution}. Result: {result}.",
                "Faced {problem}. Built {solution}. Impact: {impact}.",
                "Common issue: {problem}. My fix: {solution}. Try it.",
            ],
            'first': [
                "Problem I kept hitting: {problem}",
                "Solved a painful issue today:",
                "If you struggle with {problem}, here's help:",
            ],
            'middle': [
                "The problem: {detailed_problem}.\n\nWhy it happens: {cause}.",
                "My solution:\n1. {step1}\n2. {step2}\n3. {step3}",
                "Results:\n• Before: {before}\n• After: {after}",
            ],
            'final': [
                "Try this approach.\nSaved me hours weekly.",
                "Code/details in replies.",
                "What problems are you solving?",
            ]
        },
        'conceptual-deep-dive': {
            'single': [
                "{concept} is just {analogy}. Once you see it this way, {insight}.",
                "Mental model for {concept}: {model}. This unlocks {capability}.",
                "{concept} clicked when I realized {realization}. Game changer.",
            ],
            'first': [
                "Let's go deep on {concept}:",
                "Mental model that changed how I see {concept}:",
                "{concept} finally clicked. Here's how:",
            ],
            'middle': [
                "Think of it as {analogy}.\n\nThis reveals {insight}.",
                "Layer 1: {layer1}.\nLayer 2: {layer2}.\nConnection: {connection}.",
                "Common mistake: {mistake}.\n\nReality: {reality}.",
            ],
            'final': [
                "Now {concept} is intuitive.\n\nPractice this model.",
                "This lens changes everything.",
                "What concepts should I dive into next?",
            ]
        },
        'workflow-tool-share': {
            'single': [
                "My {workflow} setup: {tool1} → {tool2} → {tool3}. Speed: {improvement}.",
                "Workflow hack: {hack}. Saves {time_saved} daily. Here's how: {how}.",
                "Tool combo that 10x'd my {task}: {combo}. Can't work without it now.",
            ],
            'first': [
                "Workflow that cut my {task} time by {percent}%:",
                "My {workflow} stack after much experimentation:",
                "Tool setup I wish I'd found sooner:",
            ],
            'middle': [
                "Step 1: {tool1} for {purpose1}.\nStep 2: {tool2} for {purpose2}.",
                "Key integration: {integration}.\n\nThis enables {capability}.",
                "Config that matters:\n{config1}\n{config2}",
            ],
            'final': [
                "Total setup time: 30min.\nTime saved: Hours weekly.",
                "Try it for a week. Thank me later.",
                "What's in your workflow?",
            ]
        }
    }
    
    # Get the appropriate template based on style
    templates = style_templates.get(style, style_templates['explanatory'])
    
    # Determine which template type to use
    if total == 1:
        template_list = templates['single']
    elif position == 1:
        template_list = templates['first']
    elif position == total:
        template_list = templates['final']
    else:
        template_list = templates['middle']
    
    # Select a random template
    template = random.choice(template_list)
    
    # Create context-aware replacements
    replacements = generate_contextual_replacements(topic, style, context)
    
    # Fill in the template
    tweet = template
    for key, value in replacements.items():
        tweet = tweet.replace(f"{{{key}}}", value)
    
    # Add thread position indicator for multi-tweet threads
    if total > 1 and position > 1:
        tweet = f"{position}/{total}\n\n{tweet}"
    
    # For first tweet in thread, add thread emoji
    if total > 1 and position == 1:
        tweet = f"{tweet}\n\n🧵"
    
    # Optimize length
    is_final = (position == total)
    tweet = optimize_tweet_length(tweet, min_chars, max_chars, is_final)
    
    return tweet

def generate_contextual_replacements(topic, style, context):
    """Generate contextually relevant replacements for template variables"""
    
    # Base replacements
    replacements = {
        'topic': topic,
        'project': topic,
        'concept': topic,
        'workflow': topic,
        'task': 'development workflow',
        'day': str(random.randint(30, 150)),
        'percent': str(random.choice([50, 60, 70, 80])),
        'time_saved': f"{random.randint(1, 3)} hours",
    }
    
    # Style-specific replacements
    if 'docker' in topic.lower() or 'podman' in topic.lower():
        replacements.update({
            'tool1': 'Docker',
            'tool2': 'Podman',
            'strength1': 'ecosystem maturity',
            'strength2': 'rootless security',
            'criteria': 'your security requirements',
            'use1': 'development environments',
            'use2': 'production deployments',
            'win1': 'Vast ecosystem',
            'win2': 'Familiar workflows',
            'win3': 'Rootless by default',
            'win4': 'No daemon needed',
            'perf1': 'faster with caching',
            'perf2': 'lighter memory footprint',
            'dx1': 'Smooth, well-documented',
            'dx2': 'Clean, security-first',
            'criteria1': 'you need ecosystem',
            'criteria2': 'security is paramount',
            'choice': 'Podman for production',
            'reason': 'security requirements',
            'philosophy': 'security vs convenience',
        })
    
    # Technical concept replacements
    replacements.update({
        'core_insight': 'architecture beats implementation',
        'key_point': 'separation of concerns',
        'benefit': 'maintainable systems',
        'foundation': 'understanding the constraints',
        'outcome': 'elegant solutions',
        'insight': 'constraints drive creativity',
        'application': 'system design',
        'principle': 'single responsibility',
        'implication': 'cleaner interfaces',
        'reasoning': 'complexity compounds',
        'overlooked': 'the cost of abstractions',
        'importance': 'long-term maintenance',
        'summary': 'design for change',
        'first_step': 'mapping dependencies',
        'key_takeaway': 'simplicity scales',
        'transformation': 'how you architect',
        'action': 'refactor one module',
        'result': 'cleaner boundaries',
        'observation': 'the best systems evolve',
        'implications': 'profound',
        'pattern': 'follows similar paths',
        'conclusion': 'principles matter',
        'meaning': 'architecture emerges',
        'exception': 'when constraints change',
        'success': 'Clear boundaries',
        'failure': 'Tangled dependencies',
        'equation': 'constraints + interfaces',
        'components': 'data, logic, presentation',
        'reconstruction': 'clean architecture',
        'constraints': 'latency requirements',
        'forces': 'user expectations',
        'constraint1': 'Network is unreliable',
        'constraint2': 'Storage is slow',
        'consequence': 'caching strategies',
        'atoms': 'functions',
        'bonds': 'interfaces',
        'bug': 'race condition in cache',
        'cause': 'missing mutex',
        'lesson': 'concurrent access needs guards',
        'solution': 'proper locking',
        'check': 'thread safety',
        'symptom': '404s under load',
        'hypothesis': 'cache invalidation',
        'reality': 'race condition',
        'attempt1': 'Increase cache TTL',
        'attempt2': 'Add more servers',
        'breakthrough': 'Found the race',
        'log': 'intermittent 404s',
        'metric': 'spike in errors',
        'issue': 'concurrent writes',
        'practice': 'mutex everything',
        'milestone': 'hit 1000 users',
        'metric': '1000 active users',
        'next_goal': '10k by December',
        'achievement': 'automated deployments',
        'pivot': 'to async processing',
        'key_factor': 'user feedback loops',
        'metric1': '1000 users',
        'metric2': '99.9% uptime',
        'metric3': '<100ms response',
        'emotion': 'energized',
        'feedback': 'This saves me hours!',
        'change': 'batch processing',
        'next_step': 'API v2',
        'problem': 'slow build times',
        'detailed_problem': 'Docker builds taking 20+ minutes',
        'step1': 'Layer caching',
        'step2': 'Multi-stage builds',
        'step3': 'BuildKit',
        'before': '20 min builds',
        'after': '2 min builds',
        'impact': '10x faster iteration',
        'analogy': 'LEGO blocks',
        'model': 'composition over inheritance',
        'capability': 'flexible systems',
        'realization': 'it\'s all about interfaces',
        'layer1': 'Data flow',
        'layer2': 'Control flow',
        'connection': 'State management',
        'mistake': 'thinking it\'s complex',
        'hack': 'tmux + fzf + ripgrep',
        'how': 'fuzzy search everything',
        'combo': 'vim + tmux + lazygit',
        'purpose1': 'editing',
        'purpose2': 'terminal management',
        'integration': 'shared clipboard',
        'config1': 'set -g mouse on',
        'config2': 'bind-key -T copy-mode',
        'improvement': '3x faster',
    })
    
    return replacements

# HTML Template remains the same
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Twitter/X Content Generator - Build in Public</title>
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
            background-color: #f5f5f5;
            color: #14171a;
            line-height: 1.6;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: white;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 30px;
            text-align: center;
        }
        
        h1 {
            color: #1da1f2;
            font-size: 32px;
            margin-bottom: 10px;
        }
        
        .subtitle {
            color: #657786;
            font-size: 18px;
        }
        
        .phase-indicators {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        
        .phase {
            background: #e8f5fd;
            color: #1da1f2;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 500;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
        }
        
        .section {
            background: white;
            padding: 30px;
            border-radius: 16px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        h2 {
            color: #14171a;
            font-size: 24px;
            margin-bottom: 20px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            font-weight: 600;
            margin-bottom: 8px;
            color: #14171a;
        }
        
        input[type="text"],
        textarea,
        select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 16px;
            font-family: inherit;
            transition: border-color 0.2s;
        }
        
        input[type="text"]:focus,
        textarea:focus,
        select:focus {
            outline: none;
            border-color: #1da1f2;
        }
        
        textarea {
            min-height: 100px;
            resize: vertical;
        }
        
        .radio-group {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        
        .radio-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        button {
            background: #1da1f2;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 24px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            width: 100%;
        }
        
        button:hover {
            background: #1a91da;
        }
        
        button:disabled {
            background: #aab8c2;
            cursor: not-allowed;
        }
        
        .results {
            margin-top: 30px;
        }
        
        .tweet-card {
            background: #f8f9fa;
            border: 1px solid #e1e8ed;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 15px;
            position: relative;
        }
        
        .tweet-number {
            position: absolute;
            top: 10px;
            right: 10px;
            background: #1da1f2;
            color: white;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 14px;
        }
        
        .tweet-content {
            white-space: pre-wrap;
            word-wrap: break-word;
            margin-bottom: 10px;
        }
        
        .tweet-meta {
            display: flex;
            gap: 15px;
            font-size: 14px;
            color: #657786;
        }
        
        .diagram-preview {
            margin: 20px 0;
            padding: 20px;
            background: #f0f9ff;
            border-radius: 12px;
            text-align: center;
        }
        
        .diagram-preview img {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .status {
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }
        
        .status.success {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .status.info {
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            color: #657786;
        }
        
        .spinner {
            display: inline-block;
            width: 30px;
            height: 30px;
            border: 3px solid #e1e8ed;
            border-top-color: #1da1f2;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .actions {
            display: flex;
            gap: 10px;
            margin-top: 20px;
            flex-wrap: wrap;
        }
        
        .btn-secondary {
            background: #e1e8ed;
            color: #14171a;
        }
        
        .btn-secondary:hover {
            background: #d1d8dd;
        }
        
        .feature-list {
            list-style: none;
            padding: 0;
        }
        
        .feature-list li {
            padding: 8px 0;
            color: #657786;
        }
        
        .feature-list li:before {
            content: "✓ ";
            color: #1da1f2;
            font-weight: bold;
        }
        
        .style-note {
            background: #e8f5fd;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            font-size: 14px;
            color: #0c5460;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🐦 Twitter/X Content Generator</h1>
            <p class="subtitle">Optimized for Technical Founders Building in Public</p>
            <div class="phase-indicators">
                <span class="phase">Length Optimized</span>
                <span class="phase">Template Based</span>
                <span class="phase">Multi-Style</span>
                <span class="phase">Thread Support</span>
            </div>
        </header>
        
        <div class="main-content">
            <div class="section">
                <h2>Generate Content</h2>
                <div id="generateForm">
                    <div class="form-group">
                        <label for="topic">Topic / Subject *</label>
                        <input type="text" id="topic" name="topic" required 
                               placeholder="e.g., Docker optimization, Kubernetes scaling, Building my SaaS">
                    </div>
                    
                    <div class="form-group">
                        <label>Content Type</label>
                        <div class="radio-group">
                            <div class="radio-item">
                                <input type="radio" id="single" name="content_type" value="single" checked>
                                <label for="single">Single Tweet (180-240 chars)</label>
                            </div>
                            <div class="radio-item">
                                <input type="radio" id="thread" name="content_type" value="thread">
                                <label for="thread">Thread (Optimized lengths)</label>
                            </div>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="style">Style / Template</label>
                        <select id="style" name="style">
                            <option value="conceptual-deep-dive">Conceptual Deep Dive</option>
                            <option value="problem-solution">Problem/Solution</option>
                            <option value="workflow-tool-share">Workflow/Tool Share</option>
                            <option value="explanatory">Explanatory</option>
                            <option value="observational">Observational</option>
                            <option value="first-principles">First Principles</option>
                            <option value="tool-comparison">Tool Comparison</option>
                            <option value="debugging-story">Debugging Story</option>
                            <option value="build-in-public">Build in Public</option>
                            <option value="problem-solution">Problem/Solution</option>
                            <option value="conceptual-deep-dive">Conceptual Deep Dive</option>
                            <option value="workflow-tool-share">Workflow/Tool Share</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="context">Additional Context (optional)</label>
                        <textarea id="context" name="context" 
                                  placeholder="Any specific angle, metrics, or details to include"></textarea>
                    </div>
                    
                    <!-- Enhanced Generator Options -->
                    <div style="background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #1DA1F2;">🚀 Enhanced Generator Options</h3>
                        
                        <div class="form-group">
                            <label>
                                <input type="checkbox" id="use_enhanced" name="use_enhanced" onchange="toggleEnhancedOptions()">
                                Use Enhanced Generator (iximiuz-style deep content)
                            </label>
                        </div>
                        
                        <div id="enhancedOptions" style="display: none;">
                            <div class="form-group">
                                <label for="audience">Target Audience</label>
                                <input type="text" id="audience" name="audience" placeholder="e.g., intermediate DevOps engineers" value="intermediate developers">
                            </div>
                            
                            <div class="form-group">
                                <label for="tone">Tone</label>
                                <select id="tone" name="tone">
                                    <option value="technical yet approachable">Technical yet approachable</option>
                                    <option value="deeply technical">Deeply technical</option>
                                    <option value="conversational">Conversational</option>
                                    <option value="educational">Educational</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label for="goal">Content Goal</label>
                                <input type="text" id="goal" name="goal" placeholder="e.g., demystify container networking" value="explain complex concepts clearly">
                            </div>
                            
                            <div class="form-group">
                                <label for="depth">Technical Depth</label>
                                <select id="depth" name="depth">
                                    <option value="basic">Basic</option>
                                    <option value="intermediate" selected>Intermediate</option>
                                    <option value="advanced">Advanced</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label for="max_words_per_post">Max Words per Tweet</label>
                                <input type="number" id="max_words_per_post" name="max_words_per_post" value="50" min="30" max="70">
                            </div>
                            
                            <div class="form-group">
                                <label>Thread Length (for threads)</label>
                                <div style="display: flex; gap: 10px;">
                                    <input type="number" id="min_tweets" name="min_tweets" value="5" min="3" max="10" style="width: 80px;">
                                    <span>to</span>
                                    <input type="number" id="max_tweets" name="max_tweets" value="7" min="3" max="15" style="width: 80px;">
                                    <span>tweets</span>
                                </div>
                            </div>
                            
                            <div class="form-group">
                                <label for="inspiration">Style Inspiration</label>
                                <select id="inspiration" name="inspiration">
                                    <option value="@iximiuz">@iximiuz (Visual systems explanations)</option>
                                    <option value="@rasbt">@rasbt (ML/AI deep dives)</option>
                                    <option value="@kelseyhightower">@kelseyhightower (Cloud/K8s wisdom)</option>
                                    <option value="custom">Custom style</option>
                                </select>
                            </div>
                            
                            <div class="form-group">
                                <label>
                                    <input type="checkbox" id="debug_prompt_mode" name="debug_prompt_mode">
                                    Debug Mode (log prompts & responses)
                                </label>
                            </div>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label>
                            <input type="checkbox" id="include_diagram" name="include_diagram">
                            Include Diagram
                        </label>
                    </div>
                    
                    <div class="form-group" id="diagramTypeGroup" style="display: none;">
                        <label for="diagram_type">Diagram Type</label>
                        <select id="diagram_type" name="diagram_type">
                            <option value="mermaid" selected>Mermaid.js</option>
                            <option value="plantuml">PlantUML</option>
                            <option value="both">Both (Mermaid + PlantUML)</option>
                        </select>
                    </div>
                    
                    <button type="button" id="generateBtn" onclick="generateContent()">Generate Content</button>
                </div>
                
                <div class="style-note">
                    <strong>Length Guidelines:</strong><br>
                    • Single tweets: 180-240 characters<br>
                    • Thread first tweet: 180-240 characters<br>
                    • Thread middle tweets: 180-260 characters<br>
                    • Thread final tweet: 150-220 characters
                </div>
                
                <div id="status"></div>
            </div>
            
            <div class="section">
                <h2>Template Styles</h2>
                <ul class="feature-list">
                    <li><strong>Problem/Solution:</strong> Clear problem statement → solution → impact</li>
                    <li><strong>Conceptual Deep Dive:</strong> Mental models and analogies</li>
                    <li><strong>Workflow/Tool Share:</strong> Practical setups and configurations</li>
                    <li><strong>Build in Public:</strong> Progress updates with metrics</li>
                    <li><strong>Tool Comparison:</strong> Practical trade-offs and use cases</li>
                    <li><strong>Debugging Story:</strong> War stories with lessons learned</li>
                    <li><strong>Explanatory:</strong> Clear technical explanations</li>
                    <li><strong>Observational:</strong> Pattern recognition insights</li>
                    <li><strong>First Principles:</strong> Breaking down to fundamentals</li>
                </ul>
                
                <h3 style="margin-top: 30px;">Recent Generations</h3>
                <div id="recent"></div>
            </div>
        </div>
        
        <div id="results"></div>
    </div>
    
    <script>
        // Toggle diagram type selector
        document.getElementById('include_diagram').addEventListener('change', function() {
            const diagramTypeGroup = document.getElementById('diagramTypeGroup');
            diagramTypeGroup.style.display = this.checked ? 'block' : 'none';
        });
        
        async function generateContent() {
            const statusDiv = document.getElementById('status');
            const resultsDiv = document.getElementById('results');
            const generateBtn = document.getElementById('generateBtn');
            
            // Get form data manually
            const topic = document.getElementById('topic').value;
            if (!topic || topic.trim() === '') {
                alert('Please enter a topic');
                return;
            }
            
            const content_type = document.querySelector('input[name="content_type"]:checked').value;
            const style = document.getElementById('style').value;
            const context = document.getElementById('context').value;
            const include_diagram = document.getElementById('include_diagram').checked;
            const diagram_type = include_diagram ? document.getElementById('diagram_type').value : 'mermaid';
            const use_enhanced = document.getElementById('use_enhanced').checked;
            
            const data = {
                topic: topic,
                content_type: content_type,
                style: style,
                context: context,
                include_diagram: include_diagram,
                diagram_type: diagram_type
            };
            
            // Add enhanced options if enabled
            if (use_enhanced) {
                data.template = {
                    'explanatory': 'Conceptual Deep Dive',
                    'problem-solution': 'Problem/Solution',
                    'workflow-tool-share': 'Workflow/Tool Share'
                }[style] || 'Conceptual Deep Dive';
                
                data.audience = document.getElementById('audience').value;
                data.tone = document.getElementById('tone').value;
                data.goal = document.getElementById('goal').value;
                data.depth = document.getElementById('depth').value;
                data.max_words_per_post = parseInt(document.getElementById('max_words_per_post').value);
                data.min_tweets = parseInt(document.getElementById('min_tweets').value);
                data.max_tweets = parseInt(document.getElementById('max_tweets').value);
                data.inspiration = document.getElementById('inspiration').value;
                data.debug_prompt_mode = document.getElementById('debug_prompt_mode').checked;
            }
            
            console.log('Sending request with data:', data);
            
            // Show loading
            generateBtn.disabled = true;
            generateBtn.textContent = 'Generating...';
            statusDiv.innerHTML = '<div class="loading"><div class="spinner"></div><p>Creating optimized content...</p></div>';
            resultsDiv.innerHTML = '';
            
            try {
                const endpoint = use_enhanced ? '/generate_enhanced' : '/generate';
                const response = await fetch(endpoint, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                });
                
                console.log('Response status:', response.status);
                const result = await response.json();
                console.log('Full response:', result);
                
                if (result.success) {
                    statusDiv.innerHTML = '<div class="status success">✅ Content generated with optimized lengths!</div>';
                    console.log('Generated result:', result);
                    displayResults(result);
                    
                    // Show debug log if available
                    if (result.debug_log) {
                        console.log('=== ENHANCED GENERATOR DEBUG LOG ===');
                        console.log(result.debug_log);
                        console.log('=== END DEBUG LOG ===');
                    }
                } else {
                    console.error('Generation failed:', result);
                    statusDiv.innerHTML = `<div class="status error">❌ Error: ${result.error}</div>`;
                }
            } catch (error) {
                statusDiv.innerHTML = `<div class="status error">❌ Error: ${error.message}</div>`;
            } finally {
                generateBtn.disabled = false;
                generateBtn.textContent = 'Generate Content';
            }
        }
        
        function displayResults(data) {
            const resultsDiv = document.getElementById('results');
            console.log('Response data:', data);  // Debug logging
            console.log('diagram_data:', data.diagram_data);  // Debug logging
            let html = '<div class="section results">';
            html += '<h2>Generated Content</h2>';
            
            // Display tweets
            if (data.tweets && data.tweets.length > 0) {
                data.tweets.forEach((tweet, index) => {
                    // Handle both string tweets and object tweets
                    const tweetContent = typeof tweet === 'string' ? tweet : tweet.content || JSON.stringify(tweet);
                    const charCount = typeof tweet === 'string' ? tweet.length : tweet.character_count || tweetContent.length;
                    
                    // Determine if this is optimal length
                    let lengthStatus = '';
                    if (data.content_type === 'single' || index === 0) {
                        lengthStatus = charCount >= 180 && charCount <= 240 ? '✓ Optimal' : 'Adjusted';
                    } else if (index === data.tweets.length - 1) {
                        lengthStatus = charCount >= 150 && charCount <= 220 ? '✓ Optimal' : 'Adjusted';
                    } else {
                        lengthStatus = charCount >= 180 && charCount <= 260 ? '✓ Optimal' : 'Adjusted';
                    }
                    
                    html += `
                        <div class="tweet-card">
                            <div class="tweet-number">${index + 1}</div>
                            <div class="tweet-content">${escapeHtml(tweetContent)}</div>
                            ${tweet.has_diagram && tweet.diagram_path ? `
                                <div class="tweet-diagram">
                                    <img src="/diagram/${encodeURIComponent(tweet.diagram_path)}" alt="Diagram for tweet ${index + 1}" style="max-width: 100%; height: auto; margin: 10px 0; border-radius: 8px; border: 1px solid #e1e8ed;">
                                    <p style="font-size: 12px; color: #657786; margin-top: 5px;">📊 Attached diagram</p>
                                </div>
                            ` : ''}
                            <div class="tweet-meta">
                                <span>Characters: ${charCount}/280</span>
                                <span>Length: ${lengthStatus}</span>
                                <span>Style: ${data.style}</span>
                                ${tweet.has_diagram ? '<span>📊 Has Diagram</span>' : ''}
                            </div>
                        </div>
                    `;
                });
            }
            
            // Display diagram if available
            console.log('Checking diagram display:', {
                has_diagram_data: !!data.diagram_data,
                has_image_path: !!(data.diagram_data && data.diagram_data.image_path),
                image_path: data.diagram_data ? data.diagram_data.image_path : 'none'
            });
            
            if (data.diagram_data && (data.diagram_data.mermaid_image_path || data.diagram_data.plantuml_image_path || data.diagram_data.image_path)) {
                console.log('Displaying diagram(s):', data.diagram_data);
                html += `<div class="diagram-preview" style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 20px;">`;
                html += `<h3 style="margin-bottom: 15px;">📊 Generated Diagram${data.diagram_data.mermaid_image_path && data.diagram_data.plantuml_image_path ? 's' : ''}</h3>`;
                
                // Display Mermaid diagram if available
                if (data.diagram_data.mermaid_image_path || data.diagram_data.image_path) {
                    const mermaidPath = data.diagram_data.mermaid_image_path || data.diagram_data.image_path;
                    html += `
                        <div style="margin-bottom: 20px;">
                            ${data.diagram_data.plantuml_image_path ? '<h4>Mermaid.js Diagram:</h4>' : ''}
                            <div style="text-align: center;">
                                <img src="/diagram/${encodeURIComponent(mermaidPath)}?t=${Date.now()}" 
                                     alt="Mermaid diagram" 
                                     style="max-width: 100%; height: auto; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" 
                                     onerror="console.error('Failed to load Mermaid diagram:', this.src);">
                            </div>
                            <div style="margin-top: 10px; text-align: center;">
                                <button onclick="toggleDiagramCode('mermaid')" style="background: #1DA1F2; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer;">
                                    🔍 View Mermaid Code
                                </button>
                            </div>
                            <div id="mermaidCodeSection" style="display: none; margin-top: 15px;">
                                <p style="font-weight: bold; margin-bottom: 10px;">Mermaid Diagram Code:</p>
                                <pre style="text-align: left; background: #282c34; color: #abb2bf; padding: 15px; border-radius: 8px; overflow-x: auto;">${escapeHtml(data.diagram || data.diagram_data.mermaid_code || '')}</pre>
                                <button onclick="copyDiagramCode('mermaid')" style="margin-top: 10px; background: #28a745; color: white; border: none; padding: 6px 12px; border-radius: 5px; cursor: pointer;">
                                    📋 Copy Mermaid Code
                                </button>
                            </div>
                        </div>
                    `;
                    window.currentMermaidCode = data.diagram || data.diagram_data.mermaid_code || '';
                }
                
                // Display PlantUML diagram if available
                if (data.diagram_data.plantuml_image_path) {
                    html += `
                        <div>
                            ${data.diagram_data.mermaid_image_path ? '<h4>PlantUML Diagram:</h4>' : ''}
                            <div style="text-align: center;">
                                <img src="/diagram/${encodeURIComponent(data.diagram_data.plantuml_image_path)}?t=${Date.now()}" 
                                     alt="PlantUML diagram" 
                                     style="max-width: 100%; height: auto; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);" 
                                     onerror="console.error('Failed to load PlantUML diagram:', this.src);">
                            </div>
                            <div style="margin-top: 10px; text-align: center;">
                                <button onclick="toggleDiagramCode('plantuml')" style="background: #9b59b6; color: white; border: none; padding: 8px 16px; border-radius: 5px; cursor: pointer;">
                                    🔍 View PlantUML Code
                                </button>
                            </div>
                            <div id="plantumlCodeSection" style="display: none; margin-top: 15px;">
                                <p style="font-weight: bold; margin-bottom: 10px;">PlantUML Diagram Code:</p>
                                <pre style="text-align: left; background: #282c34; color: #abb2bf; padding: 15px; border-radius: 8px; overflow-x: auto;">${escapeHtml(data.diagram_data.plantuml_code || '')}</pre>
                                <button onclick="copyDiagramCode('plantuml')" style="margin-top: 10px; background: #28a745; color: white; border: none; padding: 6px 12px; border-radius: 5px; cursor: pointer;">
                                    📋 Copy PlantUML Code
                                </button>
                            </div>
                        </div>
                    `;
                    window.currentPlantUMLCode = data.diagram_data.plantuml_code || '';
                }
                
                html += `</div>`;
            } else if (data.diagram) {
                // Fallback to showing just the code if no image
                console.log('No diagram_data, showing code only');
                html += `
                    <div class="diagram-preview" style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-top: 20px;">
                        <h3>📊 Generated Diagram</h3>
                        <p style="color: #666; font-style: italic;">⏳ Diagram image generation pending...</p>
                        <p style="font-weight: bold; margin-top: 15px;">Mermaid diagram code:</p>
                        <pre style="text-align: left; background: #282c34; color: #abb2bf; padding: 15px; border-radius: 8px; overflow-x: auto;">${escapeHtml(data.diagram)}</pre>
                    </div>
                `;
            }
            
            // Action buttons
            html += `
                <div class="actions">
                    <button onclick='saveAsJson(${JSON.stringify(data)})'>💾 Save as JSON</button>
                    <button class="btn-secondary" onclick='copyAllTweets()'>📋 Copy All</button>
                </div>
            `;
            
            // Store data globally for the copy function
            window.currentData = data;
            
            html += '</div>';
            resultsDiv.innerHTML = html;
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
        
        function toggleEnhancedOptions() {
            const useEnhanced = document.getElementById('use_enhanced').checked;
            const enhancedOptions = document.getElementById('enhancedOptions');
            enhancedOptions.style.display = useEnhanced ? 'block' : 'none';
        }
        
        function saveAsJson(data) {
            const filename = `thread_${data.topic.replace(/[^a-z0-9]/gi, '_')}_${Date.now()}.json`;
            const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            a.click();
            URL.revokeObjectURL(url);
        }
        
        function copyAllTweets() {
            if (window.currentData && window.currentData.tweets) {
                const tweets = window.currentData.tweets.map(tweet => 
                    typeof tweet === 'string' ? tweet : tweet.content || JSON.stringify(tweet)
                );
                const text = tweets.join('\\n\\n---\\n\\n');
                navigator.clipboard.writeText(text).then(() => {
                    alert('Copied all tweets to clipboard!');
                });
            }
        }
        
        function toggleDiagramCode(type) {
            const codeSection = document.getElementById(type + 'CodeSection');
            if (codeSection) {
                codeSection.style.display = codeSection.style.display === 'none' ? 'block' : 'none';
            }
        }
        
        function copyDiagramCode(type) {
            let code = '';
            if (type === 'mermaid' && window.currentMermaidCode) {
                code = window.currentMermaidCode;
            } else if (type === 'plantuml' && window.currentPlantUMLCode) {
                code = window.currentPlantUMLCode;
            }
            
            if (code) {
                navigator.clipboard.writeText(code).then(() => {
                    alert(type.charAt(0).toUpperCase() + type.slice(1) + ' code copied to clipboard!');
                }).catch(err => {
                    console.error('Failed to copy:', err);
                    alert('Failed to copy code');
                });
            }
        }
        
        // Backward compatibility
        function toggleMermaidCode() { toggleDiagramCode('mermaid'); }
        function copyMermaidCode() { copyDiagramCode('mermaid'); }
        
        // Load recent generations
        async function loadRecent() {
            try {
                const response = await fetch('/recent');
                const data = await response.json();
                const recentDiv = document.getElementById('recent');
                
                if (data.recent && data.recent.length > 0) {
                    let html = '';
                    data.recent.forEach(item => {
                        html += `<div style="padding: 10px 0; border-bottom: 1px solid #e1e8ed;">
                            <strong>${item.topic}</strong><br>
                            <small style="color: #657786;">${item.timestamp}</small>
                        </div>`;
                    });
                    recentDiv.innerHTML = html;
                } else {
                    recentDiv.innerHTML = '<p style="color: #657786;">No recent generations</p>';
                }
            } catch (error) {
                console.error('Could not load recent:', error);
            }
        }
        
        // Load on page load
        loadRecent();
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['GET'])
def generate_get():
    # Redirect GET requests to home page
    return render_template_string(HTML_TEMPLATE)

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        topic = data.get('topic', '')
        content_type = data.get('content_type', 'single')
        style = data.get('style', 'explanatory')
        context = data.get('context', '')
        include_diagram = data.get('include_diagram', False)
        diagram_type = data.get('diagram_type', 'mermaid')
        
        if not topic:
            return jsonify({'success': False, 'error': 'No topic provided'})
        
        # Map style to template name for Gemini
        template_map = {
            'explanatory': 'Conceptual Deep Dive',
            'problem-solution': 'Problem/Solution',
            'workflow-tool-share': 'Workflow/Tool Share',
            'observational': 'Conceptual Deep Dive',
            'first-principles': 'Conceptual Deep Dive',
            'tool-comparison': 'Problem/Solution',
            'debugging-story': 'Problem/Solution',
            'build-in-public': 'Workflow/Tool Share',
            'conceptual-deep-dive': 'Conceptual Deep Dive'
        }
        
        template = template_map.get(style, 'Conceptual Deep Dive')
        
        print(f"[DEBUG] Request received: topic='{topic}', type={content_type}, style={style}", flush=True)
        print(f"[DEBUG] Gemini generator available: {gemini_generator is not None}", flush=True)
        
        # Use Gemini dynamic generator if available
        if gemini_generator:
            try:
                print(f"[DEBUG] Generating content with Gemini: topic='{topic}', type={content_type}, template={template}, diagram_type={diagram_type}")
                # Generate content dynamically
                result = generate_dynamic_content(
                    topic=topic,
                    content_type=content_type,
                    template=template,
                    context=context,
                    api_key=gemini_api_key,
                    diagram_type=diagram_type
                )
                print(f"[DEBUG] Gemini result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                if 'error' in result:
                    print(f"[DEBUG] Generation error: {result['error']}")
                if 'tweet' in result:
                    print(f"[DEBUG] Tweet generated: {result['tweet'].get('content', 'No content')[:100]}...")
                if 'tweets' in result:
                    print(f"[DEBUG] Thread generated with {len(result['tweets'])} tweets")
                
                # Extract tweets from result
                if content_type == 'thread' and 'tweets' in result:
                    tweets = [{
                        'position': tweet['position'],
                        'content': tweet['content'],
                        'character_count': tweet['character_count'],
                        'diagram_path': tweet.get('diagram_path'),
                        'has_diagram': tweet.get('has_diagram', False)
                    } for tweet in result['tweets']]
                elif content_type == 'single' and 'tweet' in result:
                    tweets = [{
                        'position': 1,
                        'content': result['tweet']['content'],
                        'character_count': result['tweet']['character_count'],
                        'diagram_path': result['tweet'].get('diagram_path'),
                        'has_diagram': result['tweet'].get('has_diagram', False)
                    }]
                else:
                    # Fallback if structure is different
                    print(f"[DEBUG] Unexpected result structure. Keys: {list(result.keys())}")
                    if 'error' in result:
                        print(f"[DEBUG] Result contains error: {result['error']}")
                    tweets = []
                
                # Extract diagram if present
                diagram = None
                diagram_data = None
                if 'diagram' in result and result['diagram']:
                    diagram = result['diagram'].get('mermaid_code')
                    diagram_data = result['diagram']  # Keep full diagram data
                
                # Return the generated content
                return jsonify({
                    'success': True,
                    'tweets': tweets,
                    'diagram': diagram,
                    'diagram_data': diagram_data,
                    'style': style,
                    'topic': topic,
                    'content_type': content_type,
                    'saved_as': result.get('saved_path', 'generated'),
                    'generator': 'gemini_dynamic'
                })
                
            except Exception as gemini_error:
                import traceback
                logger.warning(f"Gemini generation failed: {gemini_error}")
                logger.warning(f"Traceback: {traceback.format_exc()}")
                # Fall through to legacy generation
        
        # Fallback to legacy optimized generator
        tweets = []
        
        if content_type == 'thread':
            # Generate a thread with optimized lengths
            thread_length = random.randint(3, 5)  # Vary thread length
            for i in range(1, thread_length + 1):
                tweet = generate_optimized_tweet_content(topic, style, i, thread_length, context)
                tweets.append(tweet)
        else:
            # Generate a single tweet with optimal length
            tweet = generate_optimized_tweet_content(topic, style, 1, 1, context)
            tweets.append(tweet)
        
        # Generate diagram if requested (fallback)
        diagram = None
        if include_diagram:
            # Create a contextually relevant diagram
            if 'comparison' in style or 'vs' in topic.lower():
                diagram = f"""graph LR
    A[Option 1] --> C[Decision Point]
    B[Option 2] --> C
    C --> D[Choose based on context]
    
    style A fill:#1DA1F2,color:#fff
    style B fill:#17BF63,color:#fff
    style D fill:#E1E8ED,color:#14171A"""
            elif 'workflow' in style or 'process' in topic.lower():
                diagram = f"""graph TD
    A[Input] --> B[Process]
    B --> C{Decision}
    C -->|Yes| D[Action 1]
    C -->|No| E[Action 2]
    D --> F[Output]
    E --> F
    
    style A fill:#1DA1F2,color:#fff
    style F fill:#28a745,color:#fff"""
            else:
                diagram = f"""graph TD
    A[{topic}] --> B[Analysis]
    B --> C[Implementation]
    C --> D[Results]
    
    style A fill:#1DA1F2,color:#fff
    style D fill:#28a745,color:#fff"""
        
        # Save to generated_tweets directory
        save_dir = Path('generated_tweets')
        save_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{save_dir}/thread_{topic.replace(' ', '_')}_{timestamp}.json"
        
        save_data = {
            'topic': topic,
            'style': style,
            'content_type': content_type,
            'tweets': tweets,
            'diagram': diagram,
            'generated_at': datetime.now().isoformat(),
            'generator': 'fallback_optimized'
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'tweets': tweets,
            'diagram': diagram,
            'diagram_data': None,  # No diagram data for fallback
            'style': style,
            'topic': topic,
            'content_type': content_type,
            'saved_as': filename
        })
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/recent', methods=['GET'])
def recent():
    try:
        save_dir = Path('generated_tweets')
        if not save_dir.exists():
            return jsonify({'recent': []})
        
        # Get recent files
        files = list(save_dir.glob('*.json'))
        files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        recent = []
        for file in files[:5]:  # Last 5 files
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    recent.append({
                        'topic': data.get('topic', 'Unknown'),
                        'timestamp': data.get('generated_at', file.stat().st_mtime)
                    })
            except:
                pass
        
        return jsonify({'recent': recent})
    except Exception as e:
        return jsonify({'recent': []})

@app.route('/generate_enhanced', methods=['POST'])
def generate_enhanced():
    """Enhanced generation endpoint with full configuration support"""
    try:
        data = request.json
        
        # Build configuration for enhanced generator
        config = {
            'topic': data.get('topic', ''),
            'content_type': data.get('content_type', 'thread'),
            'template': data.get('template', 'Conceptual Deep Dive'),
            'audience': data.get('audience', 'intermediate developers'),
            'tone': data.get('tone', 'technical yet approachable'),
            'goal': data.get('goal', 'explain complex concepts clearly'),
            'depth': data.get('depth', 'intermediate'),
            'length_constraints': {
                'max_words_per_post': data.get('max_words_per_post', 50),
                'min_tweets': data.get('min_tweets', 5),
                'max_tweets': data.get('max_tweets', 7)
            },
            'include_diagrams': data.get('include_diagrams', True),
            'diagram_type': data.get('diagram_type', 'both'),
            'inspiration': data.get('inspiration', '@iximiuz')
        }
        
        # Check if debug mode is enabled
        debug_mode = data.get('debug_prompt_mode', False)
        
        if not config['topic']:
            return jsonify({'success': False, 'error': 'No topic provided'})
        
        if not enhanced_generator_available:
            return jsonify({'success': False, 'error': 'Enhanced generator not available'})
        
        # Generate content
        result = create_enhanced_content(config, gemini_api_key, debug_mode)
        
        # Process the result
        if 'error' in result:
            return jsonify({
                'success': False,
                'error': result['error']
            })
        
        # Format tweets for display
        tweets = []
        if 'tweets' in result:
            for tweet_data in result['tweets']:
                tweet = {
                    'position': tweet_data.get('position', 1),
                    'content': tweet_data.get('text', ''),
                    'character_count': tweet_data.get('character_count', len(tweet_data.get('text', ''))),
                    'word_count': tweet_data.get('word_count', 0),
                    'has_diagram': tweet_data.get('has_diagram', False),
                    'diagram_description': tweet_data.get('diagram_description', '')
                }
                tweets.append(tweet)
        
        # Process diagrams
        diagram_data = None
        if 'diagrams' in result and result['diagrams']:
            diagram_data = result['diagrams']
            
            # Generate actual diagram images if we have the code
            if diagram_generator:
                # Generate Mermaid diagram
                if 'mermaid_code' in diagram_data and diagram_data['mermaid_code']:
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    output_path = f"generated_tweets/diagrams/enhanced_mermaid_{timestamp}.png"
                    os.makedirs("generated_tweets/diagrams", exist_ok=True)
                    success = diagram_generator.render_diagram(diagram_data['mermaid_code'], output_path)
                    if success:
                        diagram_data['mermaid_image_path'] = output_path
                
                # Generate PlantUML diagram using gemini_generator
                if 'plantuml_code' in diagram_data and diagram_data['plantuml_code'] and gemini_generator:
                    plantuml_path = gemini_generator.generate_plantuml_diagram(diagram_data['plantuml_code'])
                    if plantuml_path:
                        diagram_data['plantuml_image_path'] = plantuml_path
        
        # Return enhanced response
        return jsonify({
            'success': True,
            'tweets': tweets,
            'diagram_data': diagram_data,
            'metadata': result.get('metadata', {}),
            'style': config['template'],
            'topic': config['topic'],
            'content_type': config['content_type'],
            'saved_as': result.get('saved_path', 'generated'),
            'generator': 'enhanced_gemini',
            'debug_log': result.get('debug_log', '') if debug_mode else None
        })
        
    except Exception as e:
        logger.error(f"Enhanced generation error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/diagram/<path:filename>')
def serve_diagram(filename):
    """Serve diagram images"""
    try:
        # Decode the filename
        diagram_path = Path(filename)
        
        # Security check - ensure path is within generated_tweets/diagrams
        if not str(diagram_path).startswith('generated_tweets/diagrams/'):
            return "Invalid path", 403
            
        if diagram_path.exists() and diagram_path.is_file():
            return send_file(str(diagram_path), mimetype='image/png')
        else:
            return "Diagram not found", 404
    except Exception as e:
        logger.error(f"Error serving diagram: {e}")
        return "Error serving diagram", 500

if __name__ == '__main__':
    print("\n🚀 Starting Optimized Twitter/X Content Generator")
    print("=" * 50)
    print("✨ Features:")
    print("   • Length-optimized tweets (180-260 chars)")
    print("   • 9 template styles for different content types")
    print("   • Smart thread generation with proper flow")
    print("   • Context-aware content generation")
    print("\n📍 Server running at: http://localhost:5000")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)