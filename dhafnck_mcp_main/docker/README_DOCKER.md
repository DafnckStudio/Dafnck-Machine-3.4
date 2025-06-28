# 🐳 DhafnckMCP Docker System Guide

Complete guide for using the DhafnckMCP Docker system for development and deployment.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [System Overview](#-system-overview)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [Usage Commands](#-usage-commands)
- [Configuration](#-configuration)
- [Development Mode](#-development-mode)
- [Troubleshooting](#-troubleshooting)
- [Architecture](#-architecture)
- [Advanced Usage](#-advanced-usage)

## 🚀 Quick Start

### 1. Start the Server
```bash
# Navigate to project root
cd dhafnck_mcp_main

# Start the server (creates container if needed)
./scripts/manage-docker.sh start
```

### 2. Verify It's Working
```bash
# Check server health
./scripts/manage-docker.sh health

# View server status
./scripts/manage-docker.sh status
```

### 3. Connect Your MCP Client
- **MCP Server URL**: `http://localhost:8000/mcp/`
- **Authentication**: Disabled (local development)
- **Available Tools**: 6 MCP tools for task management

## 🏗️ System Overview

The DhafnckMCP Docker system provides:

- **🔧 Easy Management**: Simple scripts for all Docker operations
- **📦 Containerized MCP Server**: Full MCP server with task management tools
- **🔄 Development Mode**: Local development without authentication
- **📊 Health Monitoring**: Built-in health checks and status monitoring
- **💾 Data Persistence**: Persistent volumes for tasks, projects, and logs

## 📋 Prerequisites

### Required Software
- **Docker Desktop** or **Docker Engine** (20.10+)
- **Docker Compose** (v2.0+)
- **bash** shell (for management scripts)
- **curl** and **netcat** (for health checks)

### System Requirements
- **OS**: Linux (WSL2), macOS, or Windows with Docker Desktop
- **RAM**: Minimum 1GB available for Docker
- **Storage**: 2GB free space for images and volumes

### Verify Prerequisites
```bash
# Check Docker version
docker --version
docker-compose --version

# Test Docker is running
docker ps
```

## 🛠️ Installation & Setup

### 1. Clone and Navigate
```bash
git clone <repository-url>
cd dhafnck_mcp_main
```

### 2. Make Scripts Executable
```bash
chmod +x scripts/manage-docker.sh
```

### 3. Create Required Directories
```bash
# These are created automatically, but you can create them manually:
mkdir -p docker/data/{tasks,projects,rules}
mkdir -p docker/logs
```

### 4. Start the System
```bash
./scripts/manage-docker.sh start
```

## 🎮 Usage Commands

### Management Script Commands

```bash
# Start the container (creates if doesn't exist)
./scripts/manage-docker.sh start

# Stop the running container
./scripts/manage-docker.sh stop

# Restart the container
./scripts/manage-docker.sh restart

# Show live logs (Ctrl+C to exit)
./scripts/manage-docker.sh logs

# Check container status and resource usage
./scripts/manage-docker.sh status

# Verify server health
./scripts/manage-docker.sh health

# Open shell inside container for debugging
./scripts/manage-docker.sh shell

# Remove container (preserves data volumes)
./scripts/manage-docker.sh remove

# Complete cleanup and rebuild
./scripts/manage-docker.sh cleanup

# Show help and available commands
./scripts/manage-docker.sh help
```

### Direct Docker Commands

```bash
# View all containers
docker ps -a

# View container logs
docker logs dhafnck-mcp-server -f

# Execute commands in container
docker exec -it dhafnck-mcp-server /bin/bash

# View resource usage
docker stats dhafnck-mcp-server

# View volumes
docker volume ls | grep dhafnck
```

## ⚙️ Configuration

### Environment Variables

The system uses these key environment variables:

```bash
# Core MCP Configuration
PYTHONPATH=/app/src
FASTMCP_LOG_LEVEL=INFO
FASTMCP_TRANSPORT=streamable-http
FASTMCP_HOST=0.0.0.0
FASTMCP_PORT=8000

# Authentication (disabled in local mode)
DHAFNCK_AUTH_ENABLED=false
DHAFNCK_MVP_MODE=false

# Data Paths
TASKS_JSON_PATH=/data/tasks
PROJECTS_FILE_PATH=/data/projects/projects.json
CURSOR_RULES_DIR=/data/rules

# Development Settings
DHAFNCK_DISABLE_CURSOR_TOOLS=true
DEV_MODE=1
```

### Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| `docker-compose.yml` | Main container configuration | `docker/docker-compose.yml` |
| `docker-compose.local.yml` | Local development overrides | `docker/docker-compose.local.yml` |
| `docker-compose.dev.yml` | Development-specific settings | `docker/docker-compose.dev.yml` |
| `Dockerfile` | Container build instructions | `docker/Dockerfile` |

### Customizing Configuration

1. **For local development**: Modify `docker-compose.local.yml`
2. **For production**: Modify `docker-compose.yml`
3. **Environment variables**: Create `.env` file in `docker/` directory

Example `.env` file:
```bash
# docker/.env
FASTMCP_LOG_LEVEL=DEBUG
DHAFNCK_AUTH_ENABLED=true
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-anon-key
```

## 🔧 Development Mode

### Features
- **No Authentication**: Direct access without tokens
- **Live Logs**: Verbose logging for debugging
- **Debug Port**: Additional port 8001 available
- **Cursor Tools Disabled**: Simplified tool set for development

### Switching Modes

```bash
# Use local development mode (default)
docker-compose -f docker-compose.yml -f docker-compose.local.yml up -d

# Use development mode with more debugging
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# Use production mode
docker-compose -f docker-compose.yml up -d
```

### Development Workflow

1. **Start in development mode**:
   ```bash
   ./scripts/manage-docker.sh start
   ```

2. **Monitor logs during development**:
   ```bash
   ./scripts/manage-docker.sh logs
   ```

3. **Test changes**:
   ```bash
   # Restart after code changes
   ./scripts/manage-docker.sh restart
   ```

4. **Debug issues**:
   ```bash
   # Open shell in container
   ./scripts/manage-docker.sh shell
   
   # Check server status
   ./scripts/manage-docker.sh status
   ```

## 🐛 Troubleshooting

### Common Issues and Solutions

#### 1. Container Won't Start
```bash
# Check Docker is running
docker ps

# Check for port conflicts
netstat -tulpn | grep 8000

# View detailed error logs
./scripts/manage-docker.sh logs

# Clean up and restart
./scripts/manage-docker.sh cleanup
./scripts/manage-docker.sh start
```

#### 2. Volume Mount Errors
```bash
# Ensure data directories exist
mkdir -p docker/data/{tasks,projects,rules}

# Remove problematic volumes
docker volume rm docker_dhafnck_data docker_dhafnck_logs 2>/dev/null || true

# Restart with fresh volumes
./scripts/manage-docker.sh cleanup
./scripts/manage-docker.sh start
```

#### 3. Health Check Failures
```bash
# Check if port is accessible
nc -z localhost 8000

# Verify container is running
docker ps | grep dhafnck

# Check server logs for errors
./scripts/manage-docker.sh logs
```

#### 4. Permission Issues (Linux/WSL2)
```bash
# Fix directory permissions
sudo chown -R $USER:$USER docker/data docker/logs

# Or run with user override
docker-compose up -d --user $(id -u):$(id -g)
```

#### 5. WSL2 Specific Issues
```bash
# Restart Docker Desktop
# Or restart WSL2
wsl --shutdown
# Then restart Docker Desktop

# Check WSL2 integration
docker context ls
```

### Diagnostic Commands

```bash
# Full system status
./scripts/manage-docker.sh status

# Container inspection
docker inspect dhafnck-mcp-server

# Network inspection
docker network ls
docker network inspect docker_default

# Volume inspection
docker volume ls
docker volume inspect docker_dhafnck_data
```

### Log Analysis

```bash
# View recent logs
docker logs dhafnck-mcp-server --tail 50

# Search for specific errors
docker logs dhafnck-mcp-server 2>&1 | grep -i error

# Follow logs in real-time
./scripts/manage-docker.sh logs
```

## 🏛️ Architecture

### Container Structure
```
dhafnck-mcp-server/
├── /app/                    # Application code
│   ├── src/                 # Source code
│   ├── .venv/               # Python virtual environment
│   └── logs/                # Application logs
├── /data/                   # Persistent data
│   ├── tasks/               # Task management data
│   ├── projects/            # Project configurations
│   └── rules/               # Cursor rules and contexts
└── /app/config/             # Configuration files
```

### Network Configuration
- **Container Name**: `dhafnck-mcp-server`
- **Internal Port**: 8000
- **External Port**: 8000 (mapped to localhost:8000)
- **Additional Port**: 8001 (development mode only)
- **Network**: `docker_default` bridge network

### Volume Mapping
| Volume | Purpose | Mount Point |
|--------|---------|-------------|
| `docker_dhafnck_data` | Task and project data | `/data` |
| `docker_dhafnck_logs` | Application logs | `/app/logs` |
| `./config` | Configuration files | `/app/config` (read-only) |

### Resource Limits
- **Memory Limit**: 512MB
- **Memory Reservation**: 256MB
- **CPU Limit**: 0.5 cores
- **CPU Reservation**: 0.1 cores

## 🚀 Advanced Usage

### Custom Builds
```bash
# Build custom image
docker build -t dhafnck/mcp-server:custom -f docker/Dockerfile .

# Use custom image
docker-compose -f docker-compose.yml up -d
```

### Multiple Environments
```bash
# Production environment
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Staging environment
docker-compose -f docker-compose.yml -f docker-compose.staging.yml up -d

# Testing environment
docker-compose -f docker-compose.yml -f docker-compose.test.yml up -d
```

### Scaling (Future)
```bash
# Scale to multiple instances
docker-compose up -d --scale dhafnck-mcp=3

# Load balancer configuration needed for multiple instances
```

### Backup and Restore
```bash
# Backup data volumes
docker run --rm -v docker_dhafnck_data:/data -v $(pwd):/backup alpine tar czf /backup/dhafnck-data-backup.tar.gz -C /data .

# Restore data volumes
docker run --rm -v docker_dhafnck_data:/data -v $(pwd):/backup alpine tar xzf /backup/dhafnck-data-backup.tar.gz -C /data
```

### Monitoring
```bash
# Resource monitoring
docker stats dhafnck-mcp-server

# Health monitoring
watch -n 5 './scripts/manage-docker.sh health'

# Log monitoring
tail -f docker/logs/*.log
```

## 📚 Additional Resources

### Related Documentation
- [Project Architecture](../.cursor/rules/technical_architect/index.mdc)
- [Task Management Workflow](../.cursor/rules/02_AI-DOCS/TaskManagement/task_management_workflow.mdc)
- [Multi-Agent Orchestration](../.cursor/rules/02_AI-DOCS/MultiAgentOrchestration/README.mdc)

### External Links
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)

### Support
- **Issues**: Check container logs with `./scripts/manage-docker.sh logs`
- **Debugging**: Use `./scripts/manage-docker.sh shell` for container access
- **Health**: Monitor with `./scripts/manage-docker.sh health`

---

**Last Updated**: 2025-06-28  
**Version**: 2.0.0  
**Compatibility**: Docker 20.10+, Docker Compose v2.0+ 