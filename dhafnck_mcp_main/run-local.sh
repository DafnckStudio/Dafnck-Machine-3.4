#!/bin/bash

# DhafnckMCP Local Development Startup Script
# Runs the Docker container without authentication for local development

set -e

echo "🚀 Starting DhafnckMCP Server (Local Development - No Authentication)"
echo "=================================================="

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
docker-compose -f docker-compose.yml -f docker-compose.local.yml up --build

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