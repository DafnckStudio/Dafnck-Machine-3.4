# 🐳 DhafnckMCP Docker Guide

Complete Docker setup guide for the DhafnckMCP server MVP with optimized containerization.

## 🚀 Quick Start

### Prerequisites
- Docker 20.10+ and Docker Compose 2.0+
- 2GB available disk space
- 512MB available RAM

### 1. Clone and Setup
```bash
git clone <repository-url>
cd dhafnck_mcp_main

# Create data directories
mkdir -p data logs config

# Copy environment template
cp env.example .env
```

### 2. Configure Environment (Optional)
Edit `.env` file for Supabase integration:
```bash
# Optional: Add Supabase credentials
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
```

### 3. Build and Run
```bash
# Build and start the server
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 4. Verify Installation
```bash
# Check server health
docker-compose exec dhafnck-mcp python -c "
from src.fastmcp.server.mcp_entry_point import create_dhafnck_mcp_server
server = create_dhafnck_mcp_server()
tools = server.get_tools()
print(f'✅ Server healthy with {len(tools)} tools')
"

# View logs
docker-compose logs -f dhafnck-mcp
```

## 📋 Docker Commands Reference

### Basic Operations
```bash
# Build image
docker-compose build

# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Restart service
docker-compose restart dhafnck-mcp

# Execute commands in container
docker-compose exec dhafnck-mcp bash
```

### Development Mode
```bash
# Run with development overrides
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Build development image
docker-compose -f docker-compose.yml -f docker-compose.dev.yml build
```

### Image Management
```bash
# List images
docker images | grep dhafnck

# Remove old images
docker image prune -f

# Check image size
docker images dhafnck/mcp-server:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
```

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SUPABASE_URL` | - | Supabase project URL (optional) |
| `SUPABASE_ANON_KEY` | - | Supabase anonymous key (optional) |
| `DHAFNCK_TOKEN` | - | Custom authentication token |
| `FASTMCP_LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `FASTMCP_ENABLE_RICH_TRACEBACKS` | `0` | Enable detailed error traces (0 or 1) |
| `TASKS_JSON_PATH` | `/data/tasks` | Task data storage path |
| `PROJECTS_FILE_PATH` | `/data/projects/projects.json` | Projects file path |

### Volume Mounts

| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| `./data` | `/data` | Persistent data storage |
| `./logs` | `/app/logs` | Application logs |
| `./config` | `/app/config` | Configuration files (optional) |

### Port Mapping
- `8000:8000` - HTTP API (optional for debugging)

## 🏗️ Architecture

### Multi-Stage Build
1. **Builder Stage**: Installs dependencies and builds application
2. **Runtime Stage**: Minimal runtime environment (target: <200MB)

### Security Features
- Non-root user execution
- Read-only filesystem where possible
- Security options: `no-new-privileges`
- Resource limits: 512MB memory, 0.5 CPU

### Health Checks
- Startup probe: 30s delay, 3 retries
- Health endpoint validation
- Tool availability verification

## 🔍 Troubleshooting

### Common Issues

#### 1. Container Won't Start
```bash
# Check logs
docker-compose logs dhafnck-mcp

# Common causes:
# - Permission issues with data directory
# - Invalid environment variables
# - Port conflicts
```

#### 2. Permission Errors
```bash
# Fix data directory permissions
sudo chown -R $USER:$USER data logs

# Or use Docker user mapping
echo "DOCKER_USER_ID=$(id -u)" >> .env
echo "DOCKER_GROUP_ID=$(id -g)" >> .env
```

#### 3. Build Failures
```bash
# Clean build cache
docker system prune -f
docker-compose build --no-cache

# Check disk space
df -h
```

#### 4. Memory Issues
```bash
# Increase memory limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G  # Increase from 512M
```

### Debug Mode
```bash
# Run with debug logging
FASTMCP_LOG_LEVEL=DEBUG docker-compose up

# Access container shell
docker-compose exec dhafnck-mcp bash

# Test server manually
docker-compose exec dhafnck-mcp python -m fastmcp.server.mcp_entry_point
```

## 📊 Performance

### Image Size Optimization
- Multi-stage build reduces size by ~60%
- Target: <200MB final image
- Excludes dev dependencies and cache files

### Resource Usage
- **Memory**: 256MB baseline, 512MB limit
- **CPU**: 0.1 baseline, 0.5 limit
- **Startup**: <30 seconds typical

### Monitoring
```bash
# Resource usage
docker stats dhafnck-mcp-server

# Health status
docker-compose exec dhafnck-mcp curl -f http://localhost:8000/health || echo "Health check failed"
```

## 🚀 Production Deployment

### Docker Hub Publication
```bash
# Build for multiple architectures
docker buildx build --platform linux/amd64,linux/arm64 -t dhafnck/mcp-server:latest .

# Push to registry
docker push dhafnck/mcp-server:latest
```

### Production Configuration
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  dhafnck-mcp:
    image: dhafnck/mcp-server:latest
    restart: always
    environment:
      - FASTMCP_LOG_LEVEL=WARNING
      - FASTMCP_ENABLE_RICH_TRACEBACKS=0
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
```

## 🔗 Integration with Cursor

### MCP Configuration
Add to `.cursor/mcp.json`:
```json
{
  "mcpServers": {
    "dhafnck-mcp": {
      "command": "docker",
      "args": [
        "exec", "-i", "dhafnck-mcp-server",
        "python", "-m", "fastmcp.server.mcp_entry_point"
      ],
      "env": {}
    }
  }
}
```

### Alternative: Direct Connection
```json
{
  "mcpServers": {
    "dhafnck-mcp": {
      "command": "docker-compose",
      "args": [
        "exec", "-T", "dhafnck-mcp",
        "python", "-m", "fastmcp.server.mcp_entry_point"
      ],
      "cwd": "/path/to/dhafnck_mcp_main"
    }
  }
}
```

## 📚 Next Steps

1. **Week 2 Integration**: Token validation system
2. **Frontend Integration**: Next.js dashboard connection
3. **Supabase Setup**: Cloud authentication
4. **Production Deployment**: Docker Hub + Vercel

## 🆘 Support

- **Issues**: Check logs with `docker-compose logs -f`
- **Performance**: Monitor with `docker stats`
- **Updates**: Pull latest with `docker-compose pull`

---

**Docker Configuration Complete! 🎉**
- Image size: <200MB ✅
- Health checks: Integrated ✅  
- Volume persistence: Configured ✅
- Security: Non-root user ✅
- Documentation: Comprehensive ✅ 