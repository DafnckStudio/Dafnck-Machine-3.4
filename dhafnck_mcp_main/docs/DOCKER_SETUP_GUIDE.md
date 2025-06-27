# 🐳 DhafnckMCP Docker Setup Guide

Complete Docker setup and deployment guide for DhafnckMCP with production-ready configurations.

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Installation Methods](#installation-methods)
4. [Configuration](#configuration)
5. [Production Deployment](#production-deployment)
6. [Development Setup](#development-setup)
7. [Troubleshooting](#troubleshooting)
8. [Advanced Usage](#advanced-usage)

## 🚀 Quick Start

### 30-Second Setup

```bash
# Clone and start
git clone https://github.com/dhafnck/dhafnck_mcp.git
cd dhafnck_mcp_main
docker-compose up -d --build

# Verify
docker-compose exec dhafnck-mcp python -c "
from src.fastmcp.server.mcp_entry_point import create_dhafnck_mcp_server
server = create_dhafnck_mcp_server()
print('✅ DhafnckMCP is running with', len(server.get_tools()), 'tools')
"
```

### What You Get

- **DhafnckMCP Server**: Running on port 8000 (internal)
- **Persistent Storage**: Tasks and projects saved in `./data`
- **Logging**: Application logs in `./logs`
- **Health Monitoring**: Built-in health checks
- **Security**: Non-root user, read-only filesystem

## 📋 Prerequisites

### System Requirements

- **Docker**: 20.10+ (check with `docker --version`)
- **Docker Compose**: 2.0+ (check with `docker-compose --version`)
- **Memory**: 512MB available RAM (1GB recommended)
- **Storage**: 2GB available disk space
- **OS**: Linux, macOS, Windows (with WSL2)

### Quick Installation

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# macOS (with Homebrew)
brew install docker docker-compose

# Windows
# Download Docker Desktop from https://docker.com/products/docker-desktop
```

## 🛠️ Installation Methods

### Method 1: Production Deployment (Recommended)

**Best for**: Production environments, stable deployments

```bash
# 1. Clone and setup
git clone https://github.com/dhafnck/dhafnck_mcp.git
cd dhafnck_mcp_main

# 2. Create persistent directories
mkdir -p data/{tasks,projects,brain} logs config

# 3. Configure environment
cp env.example .env
# Edit .env with your settings (optional)

# 4. Deploy
docker-compose up -d --build

# 5. Verify deployment
docker-compose ps
docker-compose logs -f dhafnck-mcp
```

### Method 2: Development Setup

**Best for**: Development, debugging, code changes

```bash
# 1. Setup with development overrides
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build

# 2. Access development features
docker-compose exec dhafnck-mcp bash
```

### Method 3: Minimal Setup

**Best for**: Testing, CI/CD, resource-constrained environments

```bash
# 1. Run with minimal resources
docker run -d \
  --name dhafnck-mcp \
  --restart unless-stopped \
  -v $(pwd)/data:/data \
  -v $(pwd)/logs:/app/logs \
  -e FASTMCP_LOG_LEVEL=INFO \
  dhafnck/mcp-server:latest
```

## ⚙️ Configuration

### Environment Variables

Create `.env` file for configuration:

```bash
# Core Configuration
FASTMCP_LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR
FASTMCP_ENABLE_RICH_TRACEBACKS=0          # 0 or 1
PYTHONPATH=/app/src                       # Python module path

# Storage Paths
TASKS_JSON_PATH=/data/tasks               # Task data directory
PROJECTS_FILE_PATH=/data/projects/projects.json  # Projects file
BRAIN_DIR_PATH=/data/brain                # Brain data directory

# Optional: Supabase Integration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key

# Optional: Authentication
DHAFNCK_TOKEN=your-custom-token

# Docker Configuration
DOCKER_USER_ID=1000                       # Your user ID
DOCKER_GROUP_ID=1000                      # Your group ID
```

### Volume Configuration

| Host Path | Container Path | Purpose | Required |
|-----------|----------------|---------|----------|
| `./data` | `/data` | Persistent data (tasks, projects) | ✅ Yes |
| `./logs` | `/app/logs` | Application logs | ✅ Yes |
| `./config` | `/app/config` | Configuration files | ❌ Optional |
| `./src` | `/app/src` | Source code (dev mode) | 🔧 Dev only |

### Port Configuration

```yaml
# docker-compose.yml
ports:
  - "8000:8000"  # HTTP API (optional, for debugging)
  # MCP communication happens via STDIO, not HTTP
```

## 🏭 Production Deployment

### Production docker-compose.yml

```yaml
version: '3.8'

services:
  dhafnck-mcp:
    build:
      context: .
      dockerfile: Dockerfile
      target: production
    container_name: dhafnck-mcp-prod
    restart: unless-stopped
    
    # Resource limits
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.1'
    
    # Security
    security_opt:
      - no-new-privileges:true
    read_only: true
    
    # Volumes
    volumes:
      - ./data:/data
      - ./logs:/app/logs
      - /tmp:/tmp
    
    # Environment
    env_file:
      - .env
    environment:
      - FASTMCP_LOG_LEVEL=WARNING
      - FASTMCP_ENABLE_RICH_TRACEBACKS=0
    
    # Health check
    healthcheck:
      test: ["CMD", "python", "-c", "from src.fastmcp.server.mcp_entry_point import create_dhafnck_mcp_server; create_dhafnck_mcp_server()"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    
    # Logging
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### Production Checklist

- [ ] **Environment Variables**: Configure all required variables
- [ ] **Persistent Storage**: Ensure data directory is backed up
- [ ] **Resource Limits**: Set appropriate memory and CPU limits
- [ ] **Security**: Enable security options and read-only filesystem
- [ ] **Health Checks**: Configure health monitoring
- [ ] **Logging**: Set up log rotation and monitoring
- [ ] **Backup**: Implement data backup strategy
- [ ] **Monitoring**: Set up container monitoring

## 🔧 Development Setup

### Development Features

```bash
# Start with development overrides
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Features enabled:
# - Source code mounted for hot reload
# - Debug logging enabled
# - Development tools installed
# - Interactive shell access
```

### Development Commands

```bash
# Access container shell
docker-compose exec dhafnck-mcp bash

# View logs in real-time
docker-compose logs -f dhafnck-mcp

# Restart after code changes
docker-compose restart dhafnck-mcp

# Run tests inside container
docker-compose exec dhafnck-mcp pytest

# Debug with Python
docker-compose exec dhafnck-mcp python -c "
from src.fastmcp.server.mcp_entry_point import create_dhafnck_mcp_server
server = create_dhafnck_mcp_server()
print('Tools:', [tool.name for tool in server.get_tools()])
"
```

### Hot Reload Setup

```yaml
# docker-compose.dev.yml
version: '3.8'

services:
  dhafnck-mcp:
    volumes:
      - ./src:/app/src:ro  # Mount source code
    environment:
      - FASTMCP_LOG_LEVEL=DEBUG
      - FASTMCP_ENABLE_RICH_TRACEBACKS=1
    # Remove read-only for development
    read_only: false
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Container Won't Start

**Symptoms**:
```
Error: Cannot start service dhafnck-mcp: OCI runtime create failed
```

**Solutions**:
```bash
# Check Docker daemon
sudo systemctl status docker

# Check logs
docker-compose logs dhafnck-mcp

# Clean build
docker-compose down
docker system prune -f
docker-compose up --build
```

#### 2. Permission Errors

**Symptoms**:
```
PermissionError: [Errno 13] Permission denied: '/data/tasks'
```

**Solutions**:
```bash
# Fix ownership
sudo chown -R $USER:$USER data logs

# Or use user mapping in .env
echo "DOCKER_USER_ID=$(id -u)" >> .env
echo "DOCKER_GROUP_ID=$(id -g)" >> .env
```

#### 3. Memory Issues

**Symptoms**:
```
Container killed due to memory limit
```

**Solutions**:
```bash
# Increase memory limit
# In docker-compose.yml:
deploy:
  resources:
    limits:
      memory: 2G  # Increase from 1G
```

#### 4. Build Failures

**Symptoms**:
```
ERROR: failed to solve: process "/bin/sh -c pip install -e ." did not complete successfully
```

**Solutions**:
```bash
# Clean Docker cache
docker builder prune -f

# Build without cache
docker-compose build --no-cache

# Check disk space
df -h
```

#### 5. WSL Integration Issues

**Symptoms**:
```
Error: Cannot connect to the Docker daemon at unix:///var/run/docker.sock
```

**Solutions**:
```bash
# Start Docker Desktop
# Ensure WSL integration is enabled in Docker Desktop settings

# Or install Docker directly in WSL
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

### Diagnostic Commands

```bash
# Container status
docker-compose ps

# Resource usage
docker stats dhafnck-mcp

# Container inspection
docker inspect dhafnck-mcp-prod

# Network information
docker network ls
docker network inspect dhafnck_mcp_main_default

# Volume information
docker volume ls
docker volume inspect dhafnck_mcp_main_data
```

### Debug Mode

```bash
# Enable debug logging
FASTMCP_LOG_LEVEL=DEBUG docker-compose up

# Run with interactive mode
docker-compose run --rm dhafnck-mcp bash

# Test server manually
docker-compose exec dhafnck-mcp python -m fastmcp.server.mcp_entry_point
```

## 🚀 Advanced Usage

### Multi-Container Setup

```yaml
# docker-compose.advanced.yml
version: '3.8'

services:
  dhafnck-mcp:
    build: .
    depends_on:
      - redis
      - postgres
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://user:pass@postgres:5432/dhafnck
      
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
      
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=dhafnck
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  redis_data:
  postgres_data:
```

### Custom Docker Image

```dockerfile
# Dockerfile.custom
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ /app/src/
WORKDIR /app

# Custom entrypoint
COPY custom-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/custom-entrypoint.sh

ENTRYPOINT ["custom-entrypoint.sh"]
CMD ["python", "-m", "fastmcp.server.mcp_entry_point"]
```

### Container Orchestration

```bash
# Using Docker Swarm
docker swarm init
docker stack deploy -c docker-compose.yml dhafnck-stack

# Using Kubernetes
kubectl apply -f k8s/
kubectl get pods -l app=dhafnck-mcp

# Using Portainer
docker run -d -p 9000:9000 --name portainer \
  -v /var/run/docker.sock:/var/run/docker.sock \
  portainer/portainer-ce
```

### Performance Optimization

```yaml
# Optimized configuration
services:
  dhafnck-mcp:
    # Use multi-stage build
    build:
      context: .
      target: production
    
    # Optimize resources
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.25'
    
    # Optimize storage
    volumes:
      - type: bind
        source: ./data
        target: /data
        bind:
          propagation: cached
    
    # Optimize networking
    networks:
      - dhafnck-net
    
    # Optimize logging
    logging:
      driver: "json-file"
      options:
        max-size: "1m"
        max-file: "1"

networks:
  dhafnck-net:
    driver: bridge
```

### Backup and Recovery

```bash
# Backup data
docker run --rm -v dhafnck_mcp_main_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/dhafnck-backup-$(date +%Y%m%d).tar.gz -C /data .

# Restore data
docker run --rm -v dhafnck_mcp_main_data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/dhafnck-backup-20240101.tar.gz -C /data

# Database backup (if using external DB)
docker-compose exec postgres pg_dump -U user dhafnck > backup.sql
```

## 📊 Monitoring and Maintenance

### Health Monitoring

```bash
# Container health
docker-compose ps
docker-compose exec dhafnck-mcp python -c "
from src.fastmcp.server.mcp_entry_point import create_dhafnck_mcp_server
server = create_dhafnck_mcp_server()
print('Health: OK, Tools:', len(server.get_tools()))
"

# Resource monitoring
docker stats dhafnck-mcp --no-stream

# Log monitoring
docker-compose logs --tail=100 dhafnck-mcp
```

### Maintenance Tasks

```bash
# Update to latest version
git pull
docker-compose pull
docker-compose up -d --build

# Clean up old images
docker image prune -f

# Clean up old containers
docker container prune -f

# Clean up volumes (careful!)
docker volume prune -f
```

### Performance Tuning

```bash
# Optimize Docker daemon
# In /etc/docker/daemon.json:
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2"
}

# Restart Docker
sudo systemctl restart docker
```

## 📚 Next Steps

1. **Production Deployment**: Use the production configuration examples
2. **Monitoring Setup**: Implement health checks and monitoring
3. **Backup Strategy**: Set up automated backups
4. **Security Review**: Review security configurations
5. **Performance Testing**: Test under expected load

---

**Need Help?**
- 📖 Check the [main documentation](./USER_GUIDE.md)
- 🐛 Report Docker-specific issues on GitHub
- 💬 Join our community for Docker support

**Happy containerizing with DhafnckMCP!** 🐳 