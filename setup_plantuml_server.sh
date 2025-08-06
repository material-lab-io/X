#!/bin/bash
# Setup and run PlantUML server using Docker

echo "🚀 Setting up PlantUML Server..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker daemon is running
if ! docker info &> /dev/null; then
    echo "❌ Docker daemon is not running. Please start Docker."
    exit 1
fi

# Pull PlantUML server image
echo "📦 Pulling PlantUML server Docker image..."
docker pull plantuml/plantuml-server:jetty

# Check if container already exists
if [ "$(docker ps -aq -f name=plantuml-server)" ]; then
    echo "🔍 Found existing PlantUML container..."
    
    # Check if it's running
    if [ "$(docker ps -q -f name=plantuml-server)" ]; then
        echo "✅ PlantUML server is already running!"
    else
        echo "▶️ Starting existing PlantUML container..."
        docker start plantuml-server
    fi
else
    # Run PlantUML server
    echo "🏃 Starting PlantUML server on port 8080..."
    docker run -d \
        --name plantuml-server \
        -p 8080:8080 \
        --restart unless-stopped \
        plantuml/plantuml-server:jetty
fi

# Wait for server to be ready
echo "⏳ Waiting for PlantUML server to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8080 > /dev/null; then
        echo "✅ PlantUML server is ready at http://localhost:8080"
        echo ""
        echo "📊 Available endpoints:"
        echo "   - Web UI: http://localhost:8080"
        echo "   - PNG generation: http://localhost:8080/png"
        echo "   - SVG generation: http://localhost:8080/svg"
        echo ""
        echo "🛑 To stop the server: docker stop plantuml-server"
        echo "🗑️  To remove the container: docker rm plantuml-server"
        exit 0
    fi
    echo -n "."
    sleep 1
done

echo ""
echo "❌ PlantUML server failed to start within 30 seconds"
exit 1