#!/bin/bash

echo "🚀 Starting Dynamic Tweet Generator Server"
echo "========================================"
echo ""

# Check virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    exit 1
fi

# Check for Gemini API key
if [ -z "$GEMINI_API_KEY" ] && [ ! -f "config.json" ]; then
    echo "⚠️  Warning: No Gemini API key found"
    echo "   The generator will work in demo mode with sample content"
    echo ""
    echo "   To enable full generation, either:"
    echo "   1. Set environment variable: export GEMINI_API_KEY='your-key'"
    echo "   2. Add to config.json: {\"api_keys\": {\"gemini\": \"your-key\"}}"
    echo ""
fi

# Kill any existing servers on our ports
echo "🔧 Checking for existing servers..."
for port in 5000 5001 5002 5003 8000 8080 8081 8082; do
    if lsof -ti:$port >/dev/null 2>&1; then
        echo "   Killing process on port $port"
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
    fi
done

echo ""
echo "🌐 Server will start shortly..."
echo "   Generate URL: http://localhost:PORT/generate"
echo "   Preview URL: http://localhost:PORT/preview"
echo ""
echo "📝 Features:"
echo "   ✓ Custom topic input"
echo "   ✓ Multiple content templates"  
echo "   ✓ Automatic diagram generation"
echo "   ✓ Visual thread preview"
echo "   ✓ Regenerate with same inputs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"
echo ""

# Start the server
venv/bin/python dynamic_preview_server.py