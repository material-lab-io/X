#!/usr/bin/env python3
"""Check if all required dependencies are available"""

import sys
import os
from pathlib import Path

print("🔍 Checking dependencies for Dynamic Tweet Generator...\n")

# Check Python version
print(f"Python: {sys.version}")
print(f"Python executable: {sys.executable}\n")

# Check required modules
modules_to_check = [
    ('flask', 'Flask web framework'),
    ('unified_tweet_generator', 'Tweet generation engine'),
    ('diagram_automation_pipeline', 'Diagram processing'),
    ('tweet_diagram_binder', 'Tweet-diagram binding'),
    ('tweepy', 'Twitter API (optional)'),
]

all_good = True
optional_missing = []

for module_name, description in modules_to_check:
    try:
        if module_name in ['unified_tweet_generator', 'diagram_automation_pipeline', 'tweet_diagram_binder']:
            # Add current directory to path for local modules
            sys.path.insert(0, str(Path(__file__).parent))
        
        __import__(module_name)
        print(f"✅ {module_name:<30} - {description}")
    except ImportError as e:
        if 'optional' in description.lower():
            print(f"⚠️  {module_name:<30} - {description} [Not installed]")
            optional_missing.append(module_name)
        else:
            print(f"❌ {module_name:<30} - {description} [MISSING]")
            all_good = False

# Check for API keys
print("\n🔑 API Configuration:")
config_file = Path("config.json")
has_config = config_file.exists()
has_env = 'GEMINI_API_KEY' in os.environ if 'os' in sys.modules else False

if has_config:
    print("✅ config.json found")
elif has_env:
    print("✅ GEMINI_API_KEY environment variable set")
else:
    print("⚠️  No API key configuration found (will use demo mode)")

# Check for required files
print("\n📁 Required Files:")
required_files = [
    ('twitter_style_guide.json', 'Style guidelines'),
    ('twitter_templates.json', 'Content templates'),
]

for filename, description in required_files:
    if Path(filename).exists():
        print(f"✅ {filename:<30} - {description}")
    else:
        print(f"⚠️  {filename:<30} - {description} [Not found]")

# Summary
print("\n" + "="*50)
if all_good:
    print("✅ All core dependencies are installed!")
    print("\nYou can now run: ./start_dynamic_server.sh")
else:
    print("❌ Some dependencies are missing.")
    print("\nPlease run: venv/bin/pip install -r requirements.txt")

if optional_missing:
    print(f"\n⚠️  Optional modules not installed: {', '.join(optional_missing)}")
    print("   These are only needed for posting to Twitter")

import os
os._exit(0 if all_good else 1)