# Flask Preview Server Guide

A complete visual preview system for the Twitter/X content generation pipeline (Phase 1-4).

## 🚀 Quick Start

```bash
# Start the preview server
./start_preview_server.sh

# Or manually
venv/bin/python preview_server.py
```

Then navigate to: **http://localhost:5001/preview**

> Note: The preview server runs on port 5001 to avoid conflicts with the main server on port 5000.

## 🎯 Features

### Visual Tweet Thread Preview
- **Mobile-friendly responsive design**
- **Real-time thread visualization** with Twitter-like styling
- **Diagram integration** showing matched images inline
- **Character counts** for each tweet
- **Thread continuity** with visual connectors

### Pipeline Integration
- **Phase 1**: Unified tweet generation
- **Phase 2**: Mermaid diagram rendering
- **Phase 3**: Automated diagram processing
- **Phase 4**: Tweet-diagram binding

### Interactive Controls
- **🔁 Run Preview**: Execute the full pipeline in dry-run mode
- **📝 Regenerate Threads**: Create new content with AI
- **🚀 Post to Twitter**: (Disabled in preview mode)

## 📸 Screenshot

The preview shows:
```
┌─────────────────────────────────┐
│    🐦 Tweet Thread Preview      │
│  Phase 4: Complete Pipeline     │
│         [Ready]                 │
├─────────────────────────────────┤
│  [🔁 Run] [📝 Regen] [🚀 Post] │
├─────────────────────────────────┤
│ Thread: Docker Lifecycle        │
│ ┌─────────────────────────────┐ │
│ │ 1. Ever wondered what...    │ │
│ │    (125 chars)              │ │
│ ├─────────────────────────────┤ │
│ │ 2. Docker containers go...  │ │
│ │    (140 chars)              │ │
│ ├─────────────────────────────┤ │
│ │ 3. Here's a visual...       │ │
│ │    📊 [State Diagram]       │ │
│ │    [PNG Image Display]      │ │
│ │    (89 chars) 📸 Has media  │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```

## 🔧 Architecture

### Endpoints

1. **GET `/preview`**
   - Main preview interface
   - Responsive HTML with embedded JavaScript

2. **POST `/api/preview/run`**
   - Executes the complete pipeline
   - Returns JSON with threads and logs

3. **POST `/api/preview/regenerate`**
   - Generates new threads using AI
   - Updates `generated_threads_final.json`

4. **GET `/api/preview/status`**
   - Current preview state and statistics

### Data Flow

```
1. Load threads from JSON
2. Initialize diagram binder
3. Match diagrams to tweets
4. Encode images as base64
5. Return formatted preview data
```

## 📁 File Structure

```
preview_server.py        # Main Flask application
start_preview_server.sh  # Startup script
generated_threads_final.json  # Thread data

/preview endpoint files:
- HTML template (embedded)
- CSS styling (mobile-first)
- JavaScript (async fetch)
```

## 🎨 Styling Features

### Twitter-like Design
- Blue accent colors (#1da1f2)
- Thread connectors
- Tweet numbering
- Character counts
- Media indicators

### Mobile Responsive
- Flexible container widths
- Touch-friendly buttons
- Readable font sizes
- Proper viewport settings

### Visual Feedback
- Loading spinners
- Status indicators
- Error messages
- Success confirmations

## 📊 Diagram Integration

The preview automatically:
1. Searches for diagrams in `/home/kushagra/X/optimized/`
2. Falls back to `automated_diagrams/png/` if needed
3. Matches diagrams using keyword similarity
4. Embeds images as base64 data URIs
5. Shows diagram labels and metadata

## 🔍 Logging System

Real-time pipeline logs showing:
- **Info**: General process steps
- **Success**: Completed operations
- **Warning**: Non-critical issues
- **Error**: Failed operations

## ⚙️ Configuration

### Environment Variables
```bash
# Optional for regeneration
export GEMINI_API_KEY='your-key'

# Not needed for preview
# export API_KEY='twitter-key'
# export API_SECRET='twitter-secret'
```

### Custom Diagram Directory
Edit `preview_server.py`:
```python
binder = TweetDiagramBinder(diagram_dir="/your/custom/path")
```

## 🧪 Testing

### Manual Test
1. Start server: `./start_preview_server.sh`
2. Open browser: http://localhost:5000/preview
3. Click "Run Preview" to see the pipeline
4. Check logs for any issues

### API Test
```bash
# Test preview run
curl -X POST http://localhost:5000/api/preview/run

# Check status
curl http://localhost:5000/api/preview/status
```

## 🐛 Troubleshooting

### Common Issues

1. **"No diagrams found"**
   - Check diagram directories exist
   - Verify PNG files are present
   - Look at logs for path issues

2. **"Failed to load image"**
   - Check file permissions
   - Verify image file size < 5MB
   - Ensure valid PNG format

3. **"No threads to display"**
   - Create `generated_threads_final.json`
   - Or click "Regenerate Threads"
   - Check JSON format is valid

### Debug Mode
```python
# Enable debug logging
app.run(debug=True)

# Check browser console
# F12 → Console tab
```

## 🚀 Production Deployment

For production use:
1. Set `debug=False` in `app.run()`
2. Use proper WSGI server (gunicorn)
3. Add authentication if needed
4. Configure HTTPS/SSL
5. Set up proper logging

## 📝 Notes

- Preview mode doesn't post to Twitter
- Images are embedded as base64 (larger HTML)
- Supports multiple thread formats
- Mobile-first responsive design
- No external CDN dependencies

The preview server provides a complete visual representation of your Twitter threads before posting!