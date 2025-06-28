#!/bin/bash

# DhafnckMCP Local Development Startup Script
# Runs the Docker container without authentication for local development

set -e

echo "🚀 Starting DhafnckMCP Server (Local Development - No Authentication)"
echo "=================================================="

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "📁 Script directory: $SCRIPT_DIR"
echo "📁 Project directory: $PROJECT_DIR"

# Change to the project directory
cd "$PROJECT_DIR"

# Container name from docker-compose
CONTAINER_NAME="dhafnck-mcp-server"

# Function to check if container exists
check_container_exists() {
    if docker ps -a --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        return 0  # Container exists
    else
        return 1  # Container doesn't exist
    fi
}

# Function to check if container is running
check_container_running() {
    if docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        return 0  # Container is running
    else
        return 1  # Container is not running
    fi
}

# Check container status and handle accordingly
echo "🔍 Checking existing containers..."
if check_container_exists; then
    if check_container_running; then
        echo "✅ Container '${CONTAINER_NAME}' is already running!"
        echo "🌐 Server should be available at: http://localhost:8000"
        echo "🔍 Health Check: http://localhost:8000/health"
        echo "📊 Server Capabilities: http://localhost:8000/capabilities"
        echo ""
        echo "💡 To view logs: docker logs -f ${CONTAINER_NAME}"
        echo "💡 To stop: docker stop ${CONTAINER_NAME}"
        echo "💡 To restart: docker restart ${CONTAINER_NAME}"
        exit 0
    else
        echo "📦 Container '${CONTAINER_NAME}' exists but is stopped"
        echo "🔄 Starting existing container (preserving data)..."
        docker start ${CONTAINER_NAME}
        echo "✅ Container started successfully!"
        echo "🌐 Server URL: http://localhost:8000"
        echo "💡 To view logs: docker logs -f ${CONTAINER_NAME}"
        exit 0
    fi
else
    echo "🆕 No existing container found, will create new one..."
fi

# Detect if we're running in WSL
if grep -qi microsoft /proc/version 2>/dev/null; then
    echo "🐧 WSL environment detected"
    WSL_MODE=true
else
    WSL_MODE=false
fi

# Create data directories if they don't exist
echo "📁 Creating data directories..."
mkdir -p data/tasks data/projects data/rules logs

# Set proper permissions for data directories (skip if permission denied)
echo "🔐 Setting permissions..."
if [ "$WSL_MODE" = true ]; then
    # In WSL, permission changes might fail but Docker will handle it
    chmod -R 755 data logs 2>/dev/null || echo "⚠️  Permission warnings ignored (normal in WSL - Docker will handle permissions)"
else
    chmod -R 755 data logs
fi

# Build and start the container without authentication
echo "🐳 Building and starting Docker container..."
echo "📂 Working directory: $(pwd)"
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml up --build

echo ""
echo "✅ DhafnckMCP Server is running!"
echo "🌐 Server URL: http://localhost:8000"
echo "🔍 Health Check: http://localhost:8000/health"
echo "📊 Server Capabilities: http://localhost:8000/capabilities"
echo ""
echo "🔓 Authentication is DISABLED for local development"
echo "💡 No tokens required - all requests are allowed"
echo ""
echo "Press Ctrl+C to stop the server" 