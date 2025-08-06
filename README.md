# Twitter/X AI Content Generator - Comprehensive System

A production-ready AI-powered content generation system for Twitter/X, featuring multi-model LLM support, diagram generation, and advanced thread creation capabilities.

## 🚀 Features

- **Multi-Model LLM Support**: Gemini, Claude, and OpenAI with automatic fallback
- **Advanced Thread Generation**: Create engaging multi-tweet threads with context awareness
- **Diagram Integration**: Generate Mermaid and PlantUML diagrams alongside content
- **9 Content Styles**: From explanatory to problem-solving to build-in-public
- **Character Optimization**: Ensures tweets stay within optimal length (180-260 chars)
- **Web Interface**: Full-featured Flask web application
- **CLI Tools**: Command-line interface for batch operations
- **Twitter Publishing**: Direct posting to Twitter/X with API integration

## 📦 Installation

### Prerequisites

- Python 3.8+
- Node.js 16+ (for Mermaid diagrams)
- Docker (optional, for PlantUML server)

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/material-lab-io/X.git
cd X/XPosts
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

3. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

4. **Install Node dependencies (for diagram generation)**
```bash
npm install
```

5. **Configure API keys**

Create a `config.json` file:
```json
{
  "api_keys": {
    "gemini": "YOUR_GEMINI_API_KEY",
    "anthropic": "YOUR_CLAUDE_API_KEY",
    "openai": "YOUR_OPENAI_API_KEY"
  }
}
```

## 🎯 Quick Start

### Web Interface (Recommended)

```bash
# Start the comprehensive server
python comprehensive_server.py

# Access at http://localhost:5000
```

### CLI Interface

```bash
# Interactive mode
python tweet_cli.py

# Generate with topic
python tweet_cli.py "Docker containerization best practices"
```

## 🔧 Core Components

### Main Server
- `comprehensive_server.py` - Full-featured web server with all capabilities
- Port: 5000 (configurable)
- Features: Thread generation, diagram support, multi-model LLM

### Generators
- `gemini_dynamic_generator.py` - Gemini API integration with dynamic templates
- `enhanced_gemini_generator.py` - Enhanced version with better prompt engineering
- `simple_tweet_generator.py` - Fallback pattern-based generator
- `unified_tweet_generator.py` - Unified interface for all generators

### Diagram Generation
- `mermaid_diagram_generator.py` - Mermaid.js diagram creation
- Requires: Node.js, Puppeteer, @mermaid-js/mermaid-cli
- Output: PNG images in `generated_diagrams/`

### CLI Tools
- `tweet_cli.py` - Interactive content generation with feedback loop
- `phase4_demo.py` - Demonstration of full pipeline
- `batch_post_threads.sh` - Batch posting to Twitter

### Publishing
- `twitter_publisher.py` - Twitter API integration
- `post_generated_content.py` - Post saved content
- Requires Twitter API credentials

## 📝 Usage Examples

### Generate Single Tweet
```python
from gemini_dynamic_generator import GeminiDynamicGenerator

generator = GeminiDynamicGenerator(api_key="YOUR_KEY")
result = generator.generate_content(
    topic="Docker architecture",
    content_type="single",
    template="Conceptual Deep Dive"
)
```

### Generate Thread with Diagram
Via web interface:
1. Enter topic
2. Select "Thread" as content type
3. Check "Include Diagram"
4. Select "Mermaid.js" as diagram type
5. Click Generate

### Batch Processing
```bash
# Generate multiple threads
./batch_post_threads.sh --dry-run

# Post to Twitter (requires API credentials)
export API_KEY="your_key"
export API_SECRET="your_secret"
export ACCESS_TOKEN="your_token"
export ACCESS_TOKEN_SECRET="your_token_secret"
./batch_post_threads.sh
```

## 🎨 Content Styles

1. **Explanatory** - Clear educational content
2. **Problem/Solution** - Address specific challenges
3. **Workflow/Tool Share** - Share processes and tools
4. **Observational** - Industry insights
5. **First Principles** - Fundamental concepts
6. **Tool Comparison** - Compare technologies
7. **Debugging Story** - Share debugging experiences
8. **Build in Public** - Share building journey
9. **Conceptual Deep Dive** - In-depth technical exploration

## 🐳 Docker Support (Optional)

For PlantUML diagram generation:
```bash
docker run -d -p 8080:8080 plantuml/plantuml-server:jetty
```

## 📊 Data Files

- `extracted_threads_final.json` - Training examples
- `twitter_style_guide.json` - Style rules and guidelines
- `twitter_templates.json` - Content templates
- `posts_analysis_detailed.json` - Analytics data
- `feedback_log.json` - User feedback tracking

## 🔌 API Configuration

### Gemini (Primary)
```python
api_key = "YOUR_GEMINI_API_KEY"
model = "gemini-2.0-flash-exp"
```

### Environment Variables (Twitter)
```bash
export API_KEY='your_twitter_api_key'
export API_SECRET='your_twitter_api_secret'
export ACCESS_TOKEN='your_access_token'
export ACCESS_TOKEN_SECRET='your_access_token_secret'
```

## 🚦 Testing

```bash
# Test generation
python test_generation.py

# Test diagram creation
python test_diagram_generation.py

# Test full pipeline
python test_phase4_complete.py
```

## 📁 Project Structure

```
XPosts/
├── comprehensive_server.py      # Main web server
├── gemini_dynamic_generator.py  # Gemini API integration
├── mermaid_diagram_generator.py # Diagram generation
├── tweet_cli.py                 # CLI interface
├── twitter_publisher.py         # Twitter posting
├── config.json                  # API configuration
├── requirements.txt             # Python dependencies
├── package.json                 # Node dependencies
├── generated_tweets/            # Generated content
├── generated_diagrams/          # Generated diagrams
└── templates/                   # HTML templates
```

## 🛠️ Troubleshooting

### Port Already in Use
```bash
# Kill process on port 5000
fuser -k 5000/tcp

# Or use different port
python comprehensive_server.py --port 8080
```

### Diagram Generation Issues
```bash
# Ensure Puppeteer is installed
npm install puppeteer

# Check Mermaid CLI
npx mmdc --version
```

### API Rate Limits
- Implement exponential backoff
- Use fallback models when primary fails
- Cache generated content

## 📜 License

MIT License - See LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Open pull request

## 🔗 Links

- Repository: https://github.com/material-lab-io/X
- Issues: https://github.com/material-lab-io/X/issues

## 📞 Support

For issues or questions, please open an issue on GitHub.

---

Built with ❤️ for the tech community