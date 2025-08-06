# Phase 3: Automation Pipeline Guide

This guide covers the complete automation pipeline for extracting, rendering, and managing Mermaid diagrams from your Twitter/X thread outputs.

## 🎯 Overview

The automation pipeline performs these tasks:
1. **Extract** Mermaid diagrams from thread JSON outputs
2. **Save** diagrams as `.mmd` files with proper naming
3. **Render** diagrams to PNG images using Mermaid CLI
4. **Track** metadata for all processed diagrams
5. **Generate** an index for easy access

## 📦 Components

### 1. `diagram_automation_pipeline.py`
Core automation module with:
- `DiagramAutomationPipeline` class
- Mermaid code extraction
- PNG rendering via `mmdc`
- Metadata tracking
- Batch processing support

### 2. `run_automation_demo.py`
Demo script showing complete workflow:
- Creates sample threads
- Processes diagrams
- Generates output structure

### 3. `batch_process_diagrams.sh`
Production batch processing:
- Finds all thread JSON files
- Processes in bulk
- Generates summary report

## 🚀 Quick Start

### Single Thread Processing
```bash
# Process one thread output
venv/bin/python diagram_automation_pipeline.py generated_thread.json

# Process with custom output directory
venv/bin/python diagram_automation_pipeline.py thread.json --output-dir my_diagrams
```

### Batch Processing
```bash
# Process all generated threads
./batch_process_diagrams.sh

# Process specific files
venv/bin/python diagram_automation_pipeline.py *.json --index
```

### Demo Mode
```bash
# Run the complete demo
venv/bin/python run_automation_demo.py
```

## 📁 Output Structure

```
diagrams/
├── index.json                 # Master index of all diagrams
├── mmd/                       # Mermaid source files
│   ├── docker-architecture.mmd
│   └── microservices-flow.mmd
├── png/                       # Rendered images
│   ├── docker-architecture.png
│   └── microservices-flow.png
└── metadata/                  # Processing metadata
    ├── docker-architecture_metadata.json
    └── microservices-flow_metadata.json
```

## 🔧 API Usage

### Python Integration
```python
from diagram_automation_pipeline import DiagramAutomationPipeline

# Initialize pipeline
pipeline = DiagramAutomationPipeline(output_dir="my_diagrams")

# Process thread output
with open('thread_output.json', 'r') as f:
    thread_data = json.load(f)

result = pipeline.process_thread_output(thread_data)

# Check results
print(f"Extracted: {result['diagrams_extracted']} diagrams")
print(f"Rendered: {result['diagrams_rendered']} PNGs")
```

### Extract Diagrams Only
```python
# Extract from content string
content = "Here's a diagram: ```mermaid\ngraph TD\n  A --> B\n```"
diagrams = pipeline.extract_mermaid_diagrams(content, topic="My Topic")

# Save individually
for diagram in diagrams:
    path = pipeline.save_mermaid_file(diagram)
    print(f"Saved: {path}")
```

## 📊 Metadata Format

Each processed diagram generates metadata:
```json
{
  "topic": "Docker Architecture",
  "processed_at": "2025-08-03T11:30:00Z",
  "diagram_count": 1,
  "diagrams": [{
    "filename": "docker-architecture",
    "hash": "abc123",
    "mmd_path": "diagrams/mmd/docker-architecture.mmd",
    "png_path": "diagrams/png/docker-architecture.png",
    "png_rendered": true,
    "code_length": 245,
    "diagram_type": "flowchart"
  }],
  "thread_info": {
    "tweet_count": 6,
    "template": "ConceptualDeepDive",
    "keywords": ["docker", "containers", "architecture"]
  }
}
```

## 🛠️ Configuration

### Custom Puppeteer Config
For Mermaid CLI sandbox issues:
```json
{
  "args": ["--no-sandbox", "--disable-setuid-sandbox"]
}
```

### Environment Setup
```bash
# Ensure Mermaid CLI is in PATH
export PATH="/home/kushagra/X/XPosts/node_modules/.bin:$PATH"

# Activate Python environment
source venv/bin/activate
```

## 📈 Advanced Features

### 1. Diagram Type Detection
Automatically detects:
- Flowcharts (`graph TD/LR/TB`)
- Sequence diagrams
- State diagrams
- Class diagrams
- Gantt charts

### 2. Collision Avoidance
- Unique filenames based on topic slugs
- Hash-based deduplication
- Prevents overwriting existing diagrams

### 3. Partial Processing
- Skip rendering with `--no-render`
- Extract only without saving
- Metadata-only generation

## 🔍 Troubleshooting

### Mermaid CLI Not Found
```bash
# Check installation
which mmdc

# Reinstall if needed
npm install @mermaid-js/mermaid-cli
```

### Rendering Failures
- Check `puppeteer-config.json` exists
- Verify diagram syntax
- Check console for detailed errors

### Permission Issues
```bash
# Make scripts executable
chmod +x *.py *.sh

# Check output directory permissions
chmod 755 diagrams/
```

## 📝 Integration Examples

### With Tweet Generator
```bash
# Generate thread with diagram
venv/bin/python unified_tweet_generator.py "Docker Best Practices" \
  --template ConceptualDeepDive \
  --output docker_thread.json

# Process the diagram
venv/bin/python diagram_automation_pipeline.py docker_thread.json
```

### CI/CD Pipeline
```yaml
# GitHub Actions example
- name: Process Diagrams
  run: |
    source venv/bin/activate
    python diagram_automation_pipeline.py generated/*.json --index
    
- name: Upload Artifacts
  uses: actions/upload-artifact@v2
  with:
    name: diagrams
    path: diagrams/
```

## 🎯 Best Practices

1. **Regular Processing**: Run after each content generation session
2. **Version Control**: Commit `.mmd` files, optionally `.png`
3. **Naming Convention**: Use descriptive topics for better filenames
4. **Batch Processing**: Process multiple threads together for efficiency
5. **Metadata Review**: Check metadata for rendering failures

## 🚀 Next Steps

1. **Upload to CDN**: Host PNG files for Twitter embedding
2. **Automate Publishing**: Integrate with Twitter API
3. **Analytics**: Track diagram engagement metrics
4. **Templates**: Create reusable diagram templates

The automation pipeline is now complete and ready for production use!