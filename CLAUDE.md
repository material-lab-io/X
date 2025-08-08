# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered Twitter/X content generation system using multi-model orchestration (Gemini, Claude, OpenAI) with automatic fallback. Generates authentic technical content following the "Hub and Spoke" distribution model, with integrated diagram generation and Twitter publishing capabilities.

## Essential Commands

### Initial Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install Python dependencies  
pip install -r XPosts/requirements.txt

# Install Node dependencies for diagram generation
cd XPosts && npm install
```

### Primary Entry Points
```bash
# 1. Pipeline Wrapper (RECOMMENDED) - All functionality with CLI
cd XPosts && python pipeline.py --interactive
cd XPosts && python pipeline.py "Your topic" --type thread --diagram

# 2. Interactive CLI with feedback loop
cd XPosts && python tweet_cli.py
cd XPosts && python tweet_cli.py "Docker best practices"

# 3. Web Interface (port 5000)
cd XPosts && python comprehensive_server.py

# 4. Alternative servers
cd XPosts && python comprehensive_server_updated.py  # Enhanced version
cd XPosts && python diagnostic_server.py           # Debugging server
```

### Testing
```bash
# Core functionality tests
cd XPosts && python tests/test_generation.py
cd XPosts && python tests/test_full_flow.py
cd XPosts && python tests/test_phase4_complete.py

# Diagram generation tests
cd XPosts && python tests/test_diagram_generation.py
cd XPosts && python functions/diagrams/mermaid_diagram_generator.py "topic"

# API tests
cd XPosts && python tests/test_gemini_api.py
cd XPosts && python tests/test_twitter_publisher.py
```

### Content Analysis & Reporting
```bash
# Analyze generated content patterns
cd XPosts && python functions/analyzers/analyze_posts.py --detailed

# Feedback trend analysis
cd XPosts && python functions/analyzers/feedback_analyzer.py --trends

# Posting summary report
cd XPosts && python posting_summary.py --report
```

### Batch Operations
```bash
# Batch post threads with dry-run
cd XPosts && ./scripts/batch/batch_post_threads.sh --dry-run

# Process multiple diagrams
cd XPosts && ./scripts/batch/batch_process_diagrams.sh

# Diagram automation pipeline
cd XPosts && python diagram_automation_pipeline.py

# Bind diagrams to existing threads
cd XPosts && python tweet_diagram_binder.py generated_tweets/thread_*.json
```

## Architecture

### Multi-Layer Generation System

```
User Input → Pipeline/Server
    ↓
Generator Selection (Multi-Model Fallback)
    ├── Primary: Gemini API (gemini_dynamic_generator.py)
    ├── Secondary: Claude API (tweet_generator.py)
    ├── Tertiary: OpenAI API
    └── Fallback: Template-based (simple_tweet_generator.py)
    ↓
Style Guide + Template Application (10+ styles)
    ↓
Character Optimization (180-260 chars)
    ↓
Optional: Diagram Generation (Mermaid/PlantUML)
    ↓
Output: JSON + Optional PNG/SVG
    ↓
Optional: Twitter Publishing
```

### Key Components

**Generators** (`functions/generators/`):
- `gemini_dynamic_generator.py` - Primary Gemini implementation
- `enhanced_gemini_generator.py` - Enhanced prompts version
- `tweet_generator.py` - Multi-model orchestrator
- `unified_tweet_generator.py` - Integrated approach
- `style_aware_generator.py` - Style enforcement layer
- `simple_tweet_generator.py` - Template-based fallback (no API)

**Diagram Tools** (`functions/diagrams/`):
- `mermaid_diagram_generator.py` - Mermaid diagram generation
- `plantuml_generator.py` - PlantUML support
- `thread_diagram_generator.py` - Per-thread diagrams
- `ai_optimizer.py` - AI-powered diagram optimization

**Publishers** (`functions/publishers/`):
- `twitter_publisher.py` - Main Twitter API integration
- `post_generated_content.py` - Content preparation

**Analyzers** (`functions/analyzers/`):
- `analyze_posts.py` - Content performance analysis
- `feedback_analyzer.py` - User feedback processing

### Data Files
- `data/extracted_threads_final.json` - Training examples (required)
- `data/twitter_style_guide.json` - Style rules and hooks
- `data/twitter_templates.json` - 10+ content templates
- `data/posts_analysis_detailed.json` - Performance analytics
- `generated_tweets/` - Output directory with JSON and diagrams

## Configuration

### API Keys (config.json)
```json
{
  "api_keys": {
    "gemini": "your_key",
    "anthropic": "your_key",
    "openai": "your_key"
  }
}
```

### Twitter API (environment variables)
```bash
export API_KEY='your_twitter_api_key'
export API_SECRET='your_twitter_api_secret'
export ACCESS_TOKEN='your_access_token'
export ACCESS_TOKEN_SECRET='your_access_token_secret'
```

### Port Configuration
- Main server: Port 5000 (comprehensive_server.py)
- SSH forwarding: `ssh -L 5000:localhost:5000 user@server`

## Common Development Tasks

### Generate Content with Specific Style
```bash
# Pipeline with template selection
cd XPosts && python pipeline.py "Docker optimization" \
  --type thread \
  --template "Conceptual Deep Dive" \
  --diagram

# Interactive CLI with category selection
cd XPosts && python tweet_cli.py
```

### Debug Generation Issues
```bash
# Check server logs
cd XPosts && tail -f logs/comprehensive_server.log

# Test individual generators
cd XPosts && python -c "
from functions.generators.gemini_dynamic_generator import GeminiDynamicGenerator
gen = GeminiDynamicGenerator('your_api_key')
result = gen.generate_content('Test topic', 'single', 'Problem-Solution')
print(result)
"

# Run diagnostic server
cd XPosts && python diagnostic_server.py
```

### Work with Diagrams
```bash
# Generate standalone diagram
cd XPosts && python functions/diagrams/mermaid_diagram_generator.py \
  "microservices architecture"

# Attach diagram to existing thread
cd XPosts && python tweet_diagram_binder.py \
  generated_tweets/thread_*.json \
  --diagram-dir /home/kushagra/X/optimized

# Automated diagram pipeline
cd XPosts && python diagram_automation_pipeline.py
```

## CLI Feedback Options

When using `tweet_cli.py`, respond with:
- `g` (Great) - Save as successful
- `o` (Good) - Save with positive feedback  
- `t` (Try Again) - Regenerate same prompt
- `e` (Edit) - Manual editing
- `s` (Change Style) - Switch tone
- `v` (Save) - Save current version

## Content Templates

Available templates (defined in `data/twitter_templates.json`):
1. Problem-Solution
2. Did You Know
3. Quick Tips
4. Myth Buster
5. Tool Spotlight
6. Before/After
7. Common Mistakes
8. Conceptual Deep Dive
9. Real World Scenario
10. Startup Announcement

## Technical Categories

Supported categories:
- AI Agent Testing
- Docker
- Video Models  
- LLMs
- DevTools
- Agentic Coding

## Content Philosophy

Following the "Hub and Spoke" model:
- Social media is distribution, not destination
- Focus on genuine technical insights from real work
- Educational content over engagement farming
- Pattern: Share → Educate → Build Trust
- Writing principles: Be specific, show don't tell, avoid platitudes