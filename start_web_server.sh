#!/bin/bash
# Start the Twitter/X Content Generator Web Interface

echo "🚀 Starting Twitter/X Content Generator Web Interface..."
echo "=================================================="
echo ""
echo "The server will start on port 5000."
echo ""
echo "📌 To access from Windows (through WSL SSH):"
echo ""
echo "1. Keep this terminal running"
echo ""
echo "2. Set up SSH port forwarding:"
echo "   Option A - If you're using SSH directly:"
echo "   ssh -L 5000:localhost:5000 your-user@your-server"
echo ""
echo "   Option B - If already connected, open a new terminal:"
echo "   ssh -N -L 5000:localhost:5000 your-user@your-server"
echo ""
echo "3. Open in Windows browser:"
echo "   http://localhost:5000"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================================="
echo ""

# Check if Flask is installed
if ! python3 -c "import flask" 2>/dev/null; then
    echo "⚠️  Flask not installed. Install with:"
    echo "   pip3 install flask --user"
    echo "   or"
    echo "   sudo apt-get install python3-flask"
    exit 1
fi

# Start the web server
python3 web_interface.py