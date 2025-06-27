#!/bin/bash

set -e

echo "🚀 DhafnckMCP MVP Deployment & Launch"
echo "======================================"

# Configuration
PRODUCTION_MODE=${1:-"preview"}
SKIP_TESTS=${2:-"false"}

if [ "$PRODUCTION_MODE" = "production" ]; then
    echo "🌟 PRODUCTION DEPLOYMENT MODE"
    read -p "Are you sure you want to deploy to production? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Deployment cancelled"
        exit 1
    fi
else
    echo "🧪 PREVIEW DEPLOYMENT MODE"
fi

echo ""
echo "📋 Deployment Plan:"
echo "   1. Pre-deployment validation"
echo "   2. Build and test Docker image"
echo "   3. Deploy frontend to Vercel"
echo "   4. Publish Docker image"
echo "   5. Update documentation"
echo "   6. Announce launch"
echo ""

# Step 1: Pre-deployment validation
echo "🔍 Step 1: Pre-deployment validation..."

# Check if all required files exist
REQUIRED_FILES=("Dockerfile" "docker-compose.yml" "frontend/package.json" "pyproject.toml")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Required file missing: $file"
        exit 1
    fi
done

# Check if environment variables are set up
if [ ! -f "frontend/.env.local" ] && [ "$PRODUCTION_MODE" = "production" ]; then
    echo "❌ Frontend environment variables not configured"
    echo "   Please copy frontend/env.example to frontend/.env.local and configure"
    exit 1
fi

echo "✅ Pre-deployment validation passed"

# Step 2: Build and test Docker image
echo ""
echo "🐳 Step 2: Building and testing Docker image..."

# Build the image locally first
docker build -t dhafnck/mcp-server:test --target runtime .

# Test the image
echo "🧪 Testing Docker image..."
docker run --rm dhafnck/mcp-server:test python -c "
from src.fastmcp.server.mcp_entry_point import create_dhafnck_mcp_server
server = create_dhafnck_mcp_server()
tools = server.get_tools()
print(f'✅ Docker image test passed: {len(tools)} tools available')
" || {
    echo "❌ Docker image test failed"
    exit 1
}

# Run tests if not skipped
if [ "$SKIP_TESTS" != "true" ]; then
    echo "🧪 Running test suite..."
    if command -v uv &> /dev/null; then
        uv run pytest tests/ -v --tb=short || {
            echo "❌ Tests failed"
            exit 1
        }
    else
        echo "⚠️  UV not found, skipping tests"
    fi
fi

echo "✅ Docker image build and test completed"

# Step 3: Deploy frontend to Vercel
echo ""
echo "🌐 Step 3: Deploying frontend to Vercel..."

if [ "$PRODUCTION_MODE" = "production" ]; then
    ./scripts/deploy-frontend.sh --production
else
    ./scripts/deploy-frontend.sh
fi

echo "✅ Frontend deployment completed"

# Step 4: Publish Docker image
echo ""
echo "📤 Step 4: Publishing Docker image..."

if [ "$PRODUCTION_MODE" = "production" ]; then
    ./scripts/publish-docker.sh
else
    echo "🧪 Skipping Docker publish in preview mode"
    echo "   To publish: ./scripts/publish-docker.sh"
fi

echo "✅ Docker image publishing completed"

# Step 5: Update documentation
echo ""
echo "📚 Step 5: Updating documentation..."

# Update README with deployment information
TIMESTAMP=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
VERSION=$(grep '^version = ' pyproject.toml | cut -d '"' -f 2)

cat >> DEPLOYMENT_LOG.md << EOF

## Deployment: $VERSION
**Date**: $TIMESTAMP
**Mode**: $PRODUCTION_MODE
**Status**: ✅ Completed

### Components Deployed:
- Frontend: Vercel deployment
- Backend: Docker image dhafnck/mcp-server:$VERSION
- Documentation: Updated

### Next Steps:
1. Test the deployed application
2. Monitor for any issues
3. Gather user feedback
4. Plan next iteration

---

EOF

echo "✅ Documentation updated"

# Step 6: Announce launch
echo ""
echo "🎉 Step 6: Launch announcement..."

cat << EOF

🚀 DhafnckMCP MVP Successfully Deployed!
======================================

🌐 Frontend: Available on Vercel
🐳 Backend: dhafnck/mcp-server:$VERSION
📚 Documentation: Updated with deployment info

📋 What's Next:
1. Test the complete user flow
2. Monitor application performance
3. Gather user feedback
4. Document any issues
5. Plan next development iteration

🔗 Quick Start:
   docker run -p 8000:8000 dhafnck/mcp-server:$VERSION

📖 Full documentation available in docs/

Thank you for using DhafnckMCP! 🎉

EOF

# Create a deployment summary
cat > DEPLOYMENT_SUMMARY.md << EOF
# DhafnckMCP MVP Deployment Summary

**Deployment Date**: $TIMESTAMP
**Version**: $VERSION
**Mode**: $PRODUCTION_MODE

## Deployment Status: ✅ SUCCESS

### Components:
- ✅ Frontend deployed to Vercel
- ✅ Docker image built and tested
$([ "$PRODUCTION_MODE" = "production" ] && echo "- ✅ Docker image published to Docker Hub" || echo "- 🧪 Docker image ready for publishing")
- ✅ Documentation updated

### Access Information:
- **Docker Image**: \`dhafnck/mcp-server:$VERSION\`
- **Frontend**: Check Vercel deployment output
- **Documentation**: Available in \`docs/\` directory

### Post-Deployment Tasks:
- [ ] Verify all services are running correctly
- [ ] Test end-to-end user flow
- [ ] Monitor application logs
- [ ] Gather initial user feedback
- [ ] Update project status

---
Generated on $TIMESTAMP
EOF

echo "✅ MVP deployment completed successfully!"
echo "📄 Deployment summary saved to DEPLOYMENT_SUMMARY.md" 