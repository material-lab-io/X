#!/bin/bash

# Start the Flask preview server

echo "🚀 Starting Tweet Preview Server..."
echo "=================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python -m venv venv && venv/bin/pip install -r requirements.txt"
    exit 1
fi

# Check if Flask is installed
if ! venv/bin/python -c "import flask" 2>/dev/null; then
    echo "📦 Installing Flask..."
    venv/bin/pip install flask
fi

# Check for API credentials (optional for preview)
if [ -z "$API_KEY" ]; then
    echo "ℹ️  Twitter API credentials not set (not required for preview)"
    echo "   To enable posting, set: API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET"
    echo ""
fi

# Create sample diagrams if optimized directory doesn't exist
if [ ! -d "/home/kushagra/X/optimized" ] && [ -d "automated_diagrams/png" ]; then
    echo "📊 Using automated_diagrams for preview..."
fi

echo "🌐 Server will start on an available port"
echo "📱 Mobile-friendly preview with full Phase 1-4 integration"
echo ""
echo "ℹ️  The server will find an available port automatically"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="
echo ""

# Start the Flask server
venv/bin/python preview_server.py