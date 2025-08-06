# Diagram Attachment Guide

This guide explains how to generate content with attached Mermaid diagrams using the Gemini-powered system.

## Overview

The system now supports:
1. **Dynamic content generation** via Gemini API
2. **Automatic diagram creation** when relevant to the topic
3. **Smart attachment** to the most appropriate tweet in a thread
4. **Visual preview** in the web interface at http://localhost:5000

## How It Works

### 1. Generate Content with Diagrams

Access the web interface at http://localhost:5000 and:
- Enter your topic (e.g., "How circuit breakers protect microservices")
- Select content type (Single/Thread)
- Choose a template (Conceptual Deep Dive works well for technical topics)
- Add context mentioning visual elements help understanding
- Click "Generate Content"

### 2. Diagram Generation Process

When you generate content:
1. Gemini analyzes the topic and determines if a diagram would help
2. If yes, it generates Mermaid.js code for the diagram
3. The system converts Mermaid code to PNG using `mmdc`
4. The diagram is attached to the most relevant tweet
5. In the web preview, you'll see the diagram displayed under its tweet

### 3. File Structure

Generated content is saved with this structure:
```
generated_tweets/
├── thread_[topic]_[timestamp].json    # Main content file
└── diagrams/
    └── diagram_[timestamp].png        # Generated diagram image
```

### 4. Content Format

The saved JSON includes diagram attachments:
```json
{
  "tweets": [
    {
      "position": 2,
      "content": "Tweet text...",
      "character_count": 250,
      "diagram_path": "generated_tweets/diagrams/diagram_123.png",
      "has_diagram": true
    }
  ],
  "diagram": {
    "mermaid_code": "graph TD...",
    "tweet_position": 2,
    "image_path": "generated_tweets/diagrams/diagram_123.png"
  }
}
```

### 5. Publishing with Diagrams

To post content with diagrams:

```bash
# Step 1: Generate content (via web UI or API)
# This creates the JSON file with diagram attachments

# Step 2: Convert to posting format (if needed)
python prepare_for_posting.py generated_tweets/thread_your_topic_123.json

# Step 3: Post with diagrams (dry run first)
python post_generated_content.py generated_tweets/thread_your_topic_123_posting.json --dry-run

# Step 4: Actually post
python post_generated_content.py generated_tweets/thread_your_topic_123_posting.json
```

## Examples of Topics That Generate Good Diagrams

1. **Architecture Comparisons**
   - "Docker vs Podman architecture differences"
   - "Monolith vs Microservices data flow"

2. **System Workflows**
   - "How circuit breakers protect microservices"
   - "CI/CD pipeline stages explained"

3. **Data Flow Patterns**
   - "Event sourcing in distributed systems"
   - "How Kafka handles message delivery"

4. **State Machines**
   - "OAuth 2.0 authorization flow"
   - "Database transaction states"

## Troubleshooting

### Diagram Not Generating?
- Ensure your topic would benefit from visualization
- Add context like "explain with visual flow" or "show the architecture"
- Check server logs for Mermaid generation errors

### Diagram Not Displaying?
- Verify the PNG file exists in `generated_tweets/diagrams/`
- Check browser console for image loading errors
- Ensure the server is running (diagram route at `/diagram/<path>`)

### Publishing Issues?
- Use `prepare_for_posting.py` to convert formats
- Check that diagram paths are correct
- Run with `--dry-run` first to preview

## Best Practices

1. **Clear Visual Concepts**: Topics with clear relationships, flows, or comparisons work best
2. **Context Matters**: Mention visualization needs in the context field
3. **Keep It Simple**: Complex diagrams may not render well on Twitter's mobile view
4. **Test First**: Always preview in the web UI before publishing

## API Usage

For programmatic access:
```python
from gemini_dynamic_generator import generate_dynamic_content

result = generate_dynamic_content(
    topic="Your technical topic",
    content_type="thread",
    template="Conceptual Deep Dive",
    context="Include visual diagram showing the flow"
)

# Check if diagram was generated
if result.get('diagram') and result['diagram'].get('image_path'):
    print(f"Diagram created: {result['diagram']['image_path']}")
```

The system intelligently determines when diagrams add value and automatically handles the entire generation and attachment process!