#!/bin/bash
# Setup script for Mermaid diagram rendering

echo "🔧 Setting up Mermaid diagram rendering..."
echo "=========================================="

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install Node.js/npm first."
    echo "   Without npm, diagrams will be rendered using the Kroki.io web API."
    exit 0
fi

# Check if user has sudo access
if sudo -n true 2>/dev/null; then
    echo "✅ Installing Mermaid CLI globally..."
    sudo npm install -g @mermaid-js/mermaid-cli
else
    echo "⚠️  No sudo access. Installing Mermaid CLI locally..."
    npm install @mermaid-js/mermaid-cli
    echo ""
    echo "📝 Add this to your PATH to use mmdc command:"
    echo "   export PATH=\"$PWD/node_modules/.bin:\$PATH\""
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📊 Mermaid rendering options:"
echo "   1. CLI (if installed): Fast, local rendering"
echo "   2. Kroki.io API: Always available, no installation needed"
echo ""
echo "🚀 Test the diagram generator:"
echo "   venv/bin/python mermaid_diagram_generator.py \"Docker architecture\" --render"