#!/bin/bash
# Test if the server is working

echo "🔍 Testing Tweet Generator Server..."
echo "===================================="

# Kill any existing Python servers on port 5000
echo "1. Cleaning up any existing servers..."
pkill -f "python3.*simple_web_server.py" 2>/dev/null || true
pkill -f "python3.*web_interface.py" 2>/dev/null || true
sleep 2

# Start the server in background
echo "2. Starting server on port 5000..."
python3 simple_web_server.py > server.log 2>&1 &
SERVER_PID=$!
echo "   Server PID: $SERVER_PID"

# Wait for server to start
echo "3. Waiting for server to start..."
sleep 3

# Test if server is responding
echo "4. Testing server response..."
if curl -s http://localhost:5000 > /dev/null; then
    echo "   ✅ Server is running and responding!"
    echo ""
    echo "📌 Now set up port forwarding from Windows:"
    echo "   ssh -L 5000:localhost:5000 kushagra@your-server"
    echo ""
    echo "Then open in Windows browser:"
    echo "   http://localhost:5000"
    echo ""
    echo "To stop the server, run:"
    echo "   kill $SERVER_PID"
else
    echo "   ❌ Server is not responding"
    echo "   Check server.log for errors"
    kill $SERVER_PID 2>/dev/null
fi

echo "===================================="