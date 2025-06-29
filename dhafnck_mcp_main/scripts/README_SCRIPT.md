# DhafnckMCP Scripts Documentation

## 📋 Index

This directory contains various scripts for managing, deploying, and debugging the DhafnckMCP server. Below is an index of all available scripts organized by category:

### 🐳 Docker Management Scripts
- [dev-docker.sh](#dev-dockersh) - Development Docker container management with live reload
- [manage-docker.sh](#manage-dockersh) - Production Docker container management
- [manage_container.sh](#manage_containersh) - Container lifecycle management
- [docker-entrypoint.sh](#docker-entrypointsh) - Docker container entry point script
- [run-docker-local.sh](#run-docker-localsh) - Local Docker development environment

### 🚀 Deployment Scripts
- [deploy-mvp.sh](#deploy-mvpsh) - Complete MVP deployment pipeline
- [deploy-frontend.sh](#deploy-frontendsh) - Frontend deployment to Vercel
- [publish-docker.sh](#publish-dockersh) - Docker image publishing to registry

### 🔧 MCP Server Management
- [run_mcp_server.sh](#run_mcp_serversh) - Basic MCP server startup
- [run_mcp_server_with_logging.sh](#run_mcp_server_with_loggingsh) - MCP server with enhanced logging
- [restart_mcp.sh](#restart_mcpsh) - Quick MCP server restart
- [wsl_mcp_bridge.sh](#wsl_mcp_bridgesh) - WSL-specific MCP bridge

### 🔍 Debugging & Diagnostics
- [diagnostic_connect.sh](#diagnostic_connectsh) - Comprehensive MCP connection diagnostics
- [diagnose_mcp_connection.sh](#diagnose_mcp_connectionsh) - Quick MCP connection troubleshooting
- [check_cursor_logs.sh](#check_cursor_logssh) - Cursor IDE log analysis
- [start_inspector.sh](#start_inspectorsh) - MCP Inspector startup

---

## 📖 Detailed Script Documentation

### dev-docker.sh
**Purpose**: Development Docker container management with live code reloading

**Features**:
- Start/stop/restart development containers
- Live code reloading for development
- Container health monitoring
- Interactive shell access
- Development test runner
- Volume and container cleanup

**Usage**:
```bash
./dev-docker.sh [COMMAND]

Commands:
  start     - Start development container with live reload
  stop      - Stop development container
  restart   - Restart development container
  logs      - Show container logs
  shell     - Open shell in development container
  test      - Run tests in development container
  status    - Show container status
  clean     - Clean up development containers and volumes
```

**Key Features**:
- Uses `docker-compose.yml` and `docker-compose.dev.yml`
- Provides live reload for development
- Includes health checks and status monitoring
- Supports interactive debugging

---

### manage-docker.sh
**Purpose**: Production Docker container management and lifecycle control

**Features**:
- Container lifecycle management (start/stop/restart)
- Health monitoring and status checks
- Log viewing and debugging
- Resource usage monitoring
- Container cleanup and rebuilding

**Usage**:
```bash
./manage-docker.sh <command>

Commands:
  start     - Start the container (or create if doesn't exist)
  stop      - Stop the running container
  restart   - Restart the container
  logs      - Show container logs (follow mode)
  status    - Show container status
  health    - Check server health
  shell     - Open shell inside container
  remove    - Stop and remove container (preserves volumes)
  cleanup   - Remove container and rebuild from scratch
```

**Key Features**:
- Comprehensive container status reporting
- Resource usage monitoring
- Health check endpoints
- Volume preservation during cleanup

---

### diagnostic_connect.sh
**Purpose**: Comprehensive MCP server connection diagnostics and troubleshooting

**Features**:
- Complete environment validation
- Path and configuration verification
- Server startup testing
- Tool loading diagnostics
- WSL/Cursor/Claude Desktop compatibility checks
- Detailed error reporting and suggestions

**Usage**:
```bash
./diagnostic_connect.sh
```

**Diagnostic Areas**:
- Project structure validation
- Python environment checks
- Virtual environment verification
- Server import and startup testing
- Tool manager functionality
- MCP protocol compliance
- Configuration file validation

**Key Features**:
- Color-coded output for easy reading
- Comprehensive error reporting
- Automatic fix suggestions
- Environment-specific diagnostics

---

### deploy-mvp.sh
**Purpose**: Complete MVP deployment pipeline orchestration

**Features**:
- Pre-deployment validation
- Docker image building and testing
- Frontend deployment to Vercel
- Docker image publishing
- Documentation updates
- Deployment announcements

**Usage**:
```bash
./deploy-mvp.sh [production|preview] [skip_tests]

# Examples:
./deploy-mvp.sh preview          # Preview deployment
./deploy-mvp.sh production       # Production deployment
./deploy-mvp.sh preview true     # Skip tests in preview
```

**Deployment Steps**:
1. Pre-deployment validation
2. Docker image build and test
3. Frontend deployment
4. Docker image publishing
5. Documentation updates
6. Launch announcement

**Key Features**:
- Environment-specific deployments
- Comprehensive validation
- Rollback capabilities
- Deployment logging and tracking

---

### run_mcp_server.sh
**Purpose**: Basic MCP server startup with proper environment configuration

**Features**:
- Environment variable setup
- Python path configuration
- Server startup with proper context

**Usage**:
```bash
./run_mcp_server.sh
```

**Environment Variables Set**:
- `PYTHONPATH`: Python module search path
- `TASKS_JSON_PATH`: Task storage location
- `TASK_JSON_BACKUP_PATH`: Backup storage location
- `MCP_TOOL_CONFIG`: Tool configuration file
- `AGENTS_OUTPUT_DIR`: Agent output directory
- Various other project-specific paths

**Key Features**:
- Proper working directory setup
- Complete environment configuration
- Compatible with MCP Inspector

---

### check_cursor_logs.sh
**Purpose**: Cursor IDE log analysis for MCP connection troubleshooting

**Features**:
- Cursor log directory detection
- MCP-specific error searching
- Recent log file analysis
- Error pattern recognition
- Troubleshooting suggestions

**Usage**:
```bash
./check_cursor_logs.sh
```

**Search Patterns**:
- dhafnck_mcp specific errors
- General MCP connection issues
- Server startup failures
- Renderer process errors

**Key Features**:
- Cross-platform log directory detection
- Pattern-based error identification
- Contextual error reporting
- Troubleshooting recommendations

---

### diagnose_mcp_connection.sh
**Purpose**: Quick MCP connection troubleshooting and validation

**Features**:
- Connection status checking
- Configuration validation
- Server responsiveness testing
- Common issue identification

**Usage**:
```bash
./diagnose_mcp_connection.sh
```

**Key Features**:
- Quick diagnostic checks
- Configuration file validation
- Server health verification
- Common fix suggestions

---

### manage_container.sh
**Purpose**: Advanced container lifecycle management with monitoring

**Features**:
- Container creation and management
- Health monitoring
- Log aggregation
- Performance monitoring
- Cleanup and maintenance

**Usage**:
```bash
./manage_container.sh [command]
```

**Key Features**:
- Advanced container operations
- Health and performance monitoring
- Automated maintenance tasks
- Comprehensive logging

---

### docker-entrypoint.sh
**Purpose**: Docker container initialization and startup orchestration

**Features**:
- Container environment setup
- Service initialization
- Health check implementation
- Graceful shutdown handling

**Usage**: 
Automatically executed when Docker container starts

**Key Features**:
- Environment validation
- Service startup orchestration
- Health monitoring
- Signal handling for graceful shutdown

---

### run-docker-local.sh
**Purpose**: Local Docker development environment setup

**Features**:
- Local development container setup
- Volume mounting for development
- Port mapping configuration
- Development-specific optimizations

**Usage**:
```bash
./run-docker-local.sh
```

**Key Features**:
- Development-optimized configuration
- Live code reloading
- Debug port exposure
- Local volume mounting

---

### deploy-frontend.sh
**Purpose**: Frontend deployment to Vercel platform

**Features**:
- Vercel deployment automation
- Environment configuration
- Build optimization
- Deployment verification

**Usage**:
```bash
./deploy-frontend.sh [--production]
```

**Key Features**:
- Automated Vercel deployment
- Environment-specific configurations
- Build optimization
- Deployment status verification

---

### publish-docker.sh
**Purpose**: Docker image publishing to container registry

**Features**:
- Image building and tagging
- Registry authentication
- Multi-platform support
- Version management

**Usage**:
```bash
./publish-docker.sh
```

**Key Features**:
- Automated image publishing
- Version tagging
- Registry management
- Multi-platform builds

---

### run_mcp_server_with_logging.sh
**Purpose**: MCP server startup with enhanced logging and debugging

**Features**:
- Enhanced logging configuration
- Debug output capture
- Log file management
- Error tracking

**Usage**:
```bash
./run_mcp_server_with_logging.sh
```

**Key Features**:
- Comprehensive logging
- Debug information capture
- Log rotation and management
- Error tracking and reporting

---

### restart_mcp.sh
**Purpose**: Quick MCP server restart utility

**Features**:
- Fast server restart
- Process cleanup
- Environment reset
- Status verification

**Usage**:
```bash
./restart_mcp.sh
```

**Key Features**:
- Quick restart capability
- Process management
- Environment cleanup
- Status verification

---

### wsl_mcp_bridge.sh
**Purpose**: WSL-specific MCP server bridge and compatibility layer

**Features**:
- WSL environment detection
- Path translation
- Network bridge setup
- Compatibility fixes

**Usage**:
```bash
./wsl_mcp_bridge.sh
```

**Key Features**:
- WSL-specific optimizations
- Path and network handling
- Compatibility layer
- Environment adaptation

---

### start_inspector.sh
**Purpose**: MCP Inspector startup for debugging and development

**Features**:
- MCP Inspector initialization
- Debug interface setup
- Tool inspection capabilities
- Development debugging

**Usage**:
```bash
./start_inspector.sh
```

**Key Features**:
- Interactive debugging interface
- Tool inspection and testing
- Development utilities
- Real-time monitoring

---

## 🛠️ Common Usage Patterns

### Development Workflow
1. Start development environment: `./dev-docker.sh start`
2. Monitor logs: `./dev-docker.sh logs -f`
3. Run tests: `./dev-docker.sh test`
4. Debug issues: `./diagnostic_connect.sh`

### Production Deployment
1. Deploy MVP: `./deploy-mvp.sh production`
2. Monitor container: `./manage-docker.sh status`
3. Check health: `./manage-docker.sh health`
4. View logs: `./manage-docker.sh logs`

### Troubleshooting
1. Check connections: `./diagnose_mcp_connection.sh`
2. Analyze Cursor logs: `./check_cursor_logs.sh`
3. Full diagnostics: `./diagnostic_connect.sh`
4. Restart services: `./restart_mcp.sh`

---

## 📋 Prerequisites

### System Requirements
- Docker and Docker Compose
- Python 3.8+
- Node.js 16+ (for frontend deployment)
- WSL2 (for Windows users)

### Environment Setup
- Virtual environment: `dhafnck_mcp_main/.venv`
- Project root: `/home/daihungpham/agentic-project`
- Configuration files in `.cursor/` directory

### Required Permissions
- All scripts should be executable: `chmod +x *.sh`
- Docker access for container management
- Network access for deployments

---

## 🔧 Configuration

### Environment Variables
Key environment variables used across scripts:
- `PYTHONPATH`: Python module search path
- `TASKS_JSON_PATH`: Task storage location
- `PROJECT_ROOT_PATH`: Project root directory
- `CURSOR_AGENT_DIR_PATH`: Agent configuration directory

### Configuration Files
- `.cursor/mcp.json`: MCP server configuration
- `docker-compose.yml`: Docker service definitions
- `pyproject.toml`: Python project configuration
- `frontend/.env.local`: Frontend environment variables

---

## 🚨 Troubleshooting

### Common Issues
1. **Container won't start**: Check Docker service and permissions
2. **MCP connection failed**: Run diagnostic scripts
3. **Port conflicts**: Check for other services on required ports
4. **Permission denied**: Ensure scripts are executable

### Debug Commands
```bash
# Check container status
./manage-docker.sh status

# View detailed diagnostics
./diagnostic_connect.sh

# Check Cursor logs
./check_cursor_logs.sh

# Test server startup
./run_mcp_server_with_logging.sh
```

---

## 📚 Additional Resources

### Related Documentation
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [Docker Documentation](https://docs.docker.com/)
- [Cursor IDE Documentation](https://cursor.sh/)

### Support
For issues and questions:
1. Check the diagnostic scripts output
2. Review the troubleshooting section
3. Examine container and application logs
4. Consult the project documentation

---

*Last updated: 2024-12-29*
*Version: 2.0*
*Maintainer: DhafnckMCP Team* 