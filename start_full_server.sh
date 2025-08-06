#!/bin/bash
# Full-featured Twitter/X Content Generator Server
# Includes all phases (1-4) functionality

echo "🚀 Starting Full Twitter/X Content Generator Server"
echo "=================================================="
echo ""
echo "This server includes:"
echo "✅ Phase 1: Content Generation (Multiple LLMs)"
echo "✅ Phase 2: Style-aware generation with templates"
echo "✅ Phase 3: Mermaid diagram generation"
echo "✅ Phase 4: Twitter publishing integration"
echo ""
echo "📌 SSH Port Forwarding Instructions:"
echo "===================================="
echo ""
echo "From your Windows WSL terminal, run ONE of these:"
echo ""
echo "Option 1 - New SSH connection with port forwarding:"
echo "  ssh -L 5000:localhost:5000 kushagra@your-server"
echo ""
echo "Option 2 - If already connected, open a NEW terminal:"
echo "  ssh -N -L 5000:localhost:5000 kushagra@your-server"
echo ""
echo "Option 3 - For multiple ports (if using preview features):"
echo "  ssh -L 5000:localhost:5000 -L 5001:localhost:5001 kushagra@your-server"
echo ""
echo "Then access in Windows browser: http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================================="
echo ""

# Check Python virtual environment
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Check dependencies
echo "🔍 Checking dependencies..."
MISSING_DEPS=()

# Check core dependencies
python3 -c "import flask" 2>/dev/null || MISSING_DEPS+=("flask")
python3 -c "import google.generativeai" 2>/dev/null || MISSING_DEPS+=("google-generativeai")
python3 -c "import anthropic" 2>/dev/null || MISSING_DEPS+=("anthropic")
python3 -c "import openai" 2>/dev/null || MISSING_DEPS+=("openai")
python3 -c "import tweepy" 2>/dev/null || MISSING_DEPS+=("tweepy")
python3 -c "import click" 2>/dev/null || MISSING_DEPS+=("click")
python3 -c "import rich" 2>/dev/null || MISSING_DEPS+=("rich")

if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
    echo "📦 Installing missing dependencies..."
    pip install "${MISSING_DEPS[@]}"
fi

# Check for config file
if [ ! -f "config.json" ]; then
    echo "⚠️  config.json not found. Creating template..."
    cat > config.json << 'EOF'
{
  "gemini_api_key": "YOUR_GEMINI_API_KEY",
  "claude_api_key": "YOUR_CLAUDE_API_KEY",
  "openai_api_key": "YOUR_OPENAI_API_KEY",
  "api_keys": {
    "gemini": "YOUR_GEMINI_API_KEY",
    "claude": "YOUR_CLAUDE_API_KEY",
    "openai": "YOUR_OPENAI_API_KEY"
  }
}
EOF
    echo "⚠️  Please edit config.json with your API keys!"
fi

# Check for Twitter credentials (optional)
if [ -z "$API_KEY" ] || [ -z "$API_SECRET" ] || [ -z "$ACCESS_TOKEN" ] || [ -z "$ACCESS_TOKEN_SECRET" ]; then
    echo ""
    echo "ℹ️  Twitter API credentials not set (optional)"
    echo "   To enable Twitter posting, set these environment variables:"
    echo "   export API_KEY='your_key'"
    echo "   export API_SECRET='your_secret'"
    echo "   export ACCESS_TOKEN='your_token'"
    echo "   export ACCESS_TOKEN_SECRET='your_token_secret'"
fi

# Kill any existing servers on port 5000
echo ""
echo "🧹 Cleaning up any existing servers..."
pkill -f "python.*web_interface.py" 2>/dev/null || true
pkill -f "python.*final_server.py" 2>/dev/null || true
pkill -f "python.*dynamic_preview_server.py" 2>/dev/null || true
lsof -ti:5000 | xargs kill -9 2>/dev/null || true
sleep 2

# Choose the best server file
SERVER_FILE=""
if [ -f "final_server.py" ]; then
    SERVER_FILE="final_server.py"
elif [ -f "dynamic_preview_server.py" ]; then
    SERVER_FILE="dynamic_preview_server.py"
elif [ -f "web_interface.py" ]; then
    SERVER_FILE="web_interface.py"
else
    echo "❌ No suitable server file found!"
    exit 1
fi

echo ""
echo "🚀 Starting server: $SERVER_FILE"
echo "📍 Server will be available at: http://localhost:5000"
echo ""
echo "🎯 Available Features:"
echo "  - Generate tweets with multiple AI models"
echo "  - Preview generated content"
echo "  - Save tweets to JSON files"
echo "  - Generate Mermaid diagrams (if configured)"
echo "  - Post to Twitter (if credentials configured)"
echo ""

# Start the server
exec python3 "$SERVER_FILE"