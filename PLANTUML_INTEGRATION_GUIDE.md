# PlantUML Integration Guide

This guide explains how to use the new PlantUML diagram support alongside Mermaid.js in the Twitter/X content generator.

## 🚀 Features Added

1. **Diagram Type Selection**: Choose between Mermaid, PlantUML, or both
2. **Separate Storage**: PlantUML diagrams saved in `generated_tweets/diagrams/plantuml/`
3. **Dual Display**: View both diagram types when "both" is selected
4. **Code Viewing**: Separate buttons to view/copy Mermaid or PlantUML code

## 📋 How to Use

### 1. Web Interface (http://localhost:5000)

1. **Check "Include Diagram"** checkbox
2. **Select Diagram Type**:
   - `Mermaid.js`: Traditional Mermaid diagrams (default)
   - `PlantUML`: PlantUML diagrams for sequence, class, component diagrams
   - `Both`: Generate both types for comparison

3. **Generate Content** as usual

### 2. PlantUML Server Setup

#### Option A: Local Docker Server (Recommended)
```bash
# Start PlantUML server with Docker
./setup_plantuml_server.sh

# Server will run on http://localhost:8080
```

#### Option B: Use Public PlantUML Server
The system can fall back to using http://www.plantuml.com/plantuml if local server isn't available.

### 3. API Usage

```python
from gemini_dynamic_generator import generate_dynamic_content

# Generate with PlantUML
result = generate_dynamic_content(
    topic="OAuth2 authentication flow",
    content_type="thread",
    template="Conceptual Deep Dive",
    context="Show sequence diagram of OAuth2 flow",
    diagram_type="plantuml"  # or "mermaid" or "both"
)

# Generate with both diagram types
result = generate_dynamic_content(
    topic="Microservices architecture",
    content_type="thread",
    template="Conceptual Deep Dive",
    context="Compare monolith vs microservices",
    diagram_type="both"
)
```

## 📊 Diagram Type Comparison

### When to Use Mermaid.js:
- Flow charts and graphs
- Simple architecture diagrams
- State diagrams
- Git graphs

### When to Use PlantUML:
- Sequence diagrams (excellent support)
- Class diagrams with relationships
- Component diagrams
- Use case diagrams
- Activity diagrams
- Complex architectural diagrams

## 🎨 Example Prompts

### For PlantUML Sequence Diagrams:
- "OAuth2 authentication flow between client, auth server, and resource server"
- "Microservices communication during order processing"
- "Database transaction flow with rollback scenarios"

### For PlantUML Class Diagrams:
- "Domain model for e-commerce system"
- "Design patterns implementation structure"
- "API gateway architecture with services"

### For Both Types:
- "Compare Docker vs Podman architecture" (flow vs component view)
- "Event-driven architecture" (event flow vs system components)

## 📁 File Structure

```
generated_tweets/
├── diagrams/
│   ├── diagram_20240804_*.png          # Mermaid diagrams
│   └── plantuml/
│       └── plantuml_20240804_*.png     # PlantUML diagrams
└── thread_*.json                       # Generated content with diagram references
```

## 🔧 Configuration

The system uses these servers by default:
- **Mermaid**: Local `mmdc` CLI tool
- **PlantUML**: 
  - Local: `http://localhost:8080` (if Docker server is running)
  - Fallback: `http://www.plantuml.com/plantuml` (public server)

## 🐛 Troubleshooting

### PlantUML Diagrams Not Generating?
1. Check if Docker is running: `docker ps`
2. Start PlantUML server: `./setup_plantuml_server.sh`
3. Or use public server (automatic fallback)

### Mermaid Diagrams Not Generating?
1. Ensure `mmdc` is installed: `which mmdc`
2. Check puppeteer config: `cat puppeteer-config.json`

### Both Types Selected but Only One Shows?
- Check browser console for errors
- Verify both diagram codes were generated in the JSON response

## 📝 JSON Response Structure

When diagrams are generated, the response includes:

```json
{
  "diagram": {
    "mermaid_code": "graph TD...",
    "mermaid_image_path": "generated_tweets/diagrams/diagram_123.png",
    "plantuml_code": "@startuml...",
    "plantuml_image_path": "generated_tweets/diagrams/plantuml/plantuml_123.png",
    "tweet_position": 2
  }
}
```

## 🎯 Best Practices

1. **Choose the Right Tool**:
   - Mermaid for simple flows and graphs
   - PlantUML for detailed technical diagrams

2. **Context Matters**:
   - Mention diagram type preference in context
   - Be specific about what to visualize

3. **Performance**:
   - Local PlantUML server is faster than public
   - Mermaid is generally faster for simple diagrams

The system now provides full flexibility to choose the best diagram tool for your technical content!