# Twitter/X AI Content Generator

A comprehensive AI-powered content generation system for Twitter/X, featuring multi-model LLM support, diagram generation, and advanced thread creation capabilities.

## Quick Start

```bash
# Run the web server
python comprehensive_server.py

# Or use the pipeline wrapper
python pipeline.py --interactive

# Or generate content directly
python pipeline.py "Your topic here" --type thread --diagram
```

## Project Structure

```
XPosts/
├── comprehensive_server.py  # Main web server (port 5000)
├── pipeline.py             # Pipeline wrapper for all functionality
├── functions/              # Core functionality modules
│   ├── generators/         # Content generation modules
│   ├── diagrams/          # Diagram generation
│   ├── publishers/        # Twitter publishing
│   └── analyzers/         # Content analysis
├── data/                  # Data files and configurations
├── scripts/               # Utility scripts
├── utils/                 # Helper utilities
├── docs/                  # Documentation
└── generated_tweets/      # Generated content output
```

## Features

- **Multi-Model LLM Support**: Gemini, Claude, and OpenAI with automatic fallback
- **Advanced Thread Generation**: Create engaging multi-tweet threads
- **Diagram Integration**: Generate Mermaid and PlantUML diagrams
- **9 Content Styles**: Various templates for different content types
- **Character Optimization**: Ensures tweets stay within optimal length
- **Web Interface**: User-friendly Flask web application
- **Twitter Publishing**: Direct posting to Twitter/X

## Documentation

See the `docs/` folder for detailed documentation:
- `docs/README.md` - Full documentation
- `docs/CLAUDE.md` - Claude Code instructions

## Configuration

Create a `config.json` file with your API keys:
```json
{
  "api_keys": {
    "gemini": "YOUR_API_KEY",
    "anthropic": "YOUR_API_KEY",
    "openai": "YOUR_API_KEY"
  }
}
```

## License

MIT License