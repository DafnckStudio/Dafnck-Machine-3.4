#!/bin/bash

set -e

echo "🐳 Building and Publishing DhafnckMCP Docker Image..."

# Configuration
IMAGE_NAME="dhafnck/mcp-server"
VERSION=$(grep '^version = ' pyproject.toml | cut -d '"' -f 2)
LATEST_TAG="latest"

echo "📋 Build Configuration:"
echo "   Image: $IMAGE_NAME"
echo "   Version: $VERSION"
echo "   Tags: $VERSION, $LATEST_TAG"

# Check if we're in the right directory
if [ ! -f "Dockerfile" ]; then
    echo "❌ Error: Dockerfile not found. Must be run from the project root directory"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build the Docker image
echo "🔨 Building Docker image..."
docker build \
    --tag "$IMAGE_NAME:$VERSION" \
    --tag "$IMAGE_NAME:$LATEST_TAG" \
    --target runtime \
    .

# Test the built image
echo "🧪 Testing the built image..."
docker run --rm "$IMAGE_NAME:$VERSION" python -c "
from src.fastmcp.server.mcp_entry_point import create_dhafnck_mcp_server
server = create_dhafnck_mcp_server()
tools = server.get_tools()
print(f'✅ Image test passed: {len(tools)} tools available')
"

# Check if user is logged in to Docker Hub
if ! docker info | grep -q "Username:"; then
    echo "🔐 Please log in to Docker Hub:"
    docker login
fi

# Push the images
echo "📤 Pushing images to Docker Hub..."
docker push "$IMAGE_NAME:$VERSION"
docker push "$IMAGE_NAME:$LATEST_TAG"

# Create multi-architecture manifest (optional)
if command -v docker buildx &> /dev/null; then
    echo "🏗️ Creating multi-architecture build..."
    docker buildx create --use --name dhafnck-builder 2>/dev/null || true
    docker buildx build \
        --platform linux/amd64,linux/arm64 \
        --tag "$IMAGE_NAME:$VERSION" \
        --tag "$IMAGE_NAME:$LATEST_TAG" \
        --target runtime \
        --push \
        .
fi

echo "✅ Docker image published successfully!"
echo "🐳 Pull with: docker pull $IMAGE_NAME:$VERSION"
echo "🚀 Run with: docker run -p 8000:8000 $IMAGE_NAME:$VERSION"

# Display image information
echo ""
echo "📊 Image Information:"
docker images "$IMAGE_NAME" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" 