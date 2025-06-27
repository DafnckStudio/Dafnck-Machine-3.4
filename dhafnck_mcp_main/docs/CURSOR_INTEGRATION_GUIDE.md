# 🖥️ DhafnckMCP Cursor Integration Guide

Complete guide for integrating DhafnckMCP with Cursor IDE for enhanced development workflow.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [Using MCP Tools in Cursor](#using-mcp-tools-in-cursor)
6. [Multi-Agent Workflow](#multi-agent-workflow)
7. [Project-Specific Setup](#project-specific-setup)
8. [Troubleshooting](#troubleshooting)
9. [Advanced Configuration](#advanced-configuration)

## 🎯 Overview

### What is MCP Integration?

Model Context Protocol (MCP) integration allows Cursor IDE to communicate directly with DhafnckMCP server, enabling:

- **Task Management**: Create, update, and track tasks directly from Cursor
- **Agent Coordination**: Switch between specialized AI agents for different tasks
- **Project Management**: Manage multiple projects with hierarchical organization
- **Context Awareness**: AI assistant automatically adapts to your project context
- **Workflow Automation**: Automated rule generation and context synchronization

### Benefits

✅ **Seamless Workflow**: Manage tasks without leaving your IDE  
✅ **Intelligent Assistance**: AI agents specialized for different development phases  
✅ **Context Preservation**: Maintain project context across sessions  
✅ **Multi-Project Support**: Work on multiple projects with independent task management  
✅ **Automated Documentation**: Auto-generate project rules and context  

## 📋 Prerequisites

### System Requirements

- **Cursor IDE**: Latest version (download from [cursor.sh](https://cursor.sh))
- **DhafnckMCP Server**: Installed and running (see [User Guide](./USER_GUIDE.md))
- **Python 3.8+**: Required for MCP server
- **WSL2**: Required for Windows users

### Platform-Specific Requirements

#### Windows (WSL2)
```bash
# Ensure WSL2 is installed and configured
wsl --version
wsl --list --verbose

# Install Ubuntu or preferred distribution
wsl --install -d Ubuntu
```

#### macOS
```bash
# No additional requirements
# Ensure Python is available
python3 --version
```

#### Linux
```bash
# Ensure Python and pip are installed
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

## 🚀 Installation & Setup

### Step 1: Install DhafnckMCP

Choose your preferred installation method:

#### Option A: Docker (Recommended)
```bash
git clone https://github.com/dhafnck/dhafnck_mcp.git
cd dhafnck_mcp_main
docker-compose up -d --build
```

#### Option B: Python Virtual Environment
```bash
git clone https://github.com/dhafnck/dhafnck_mcp.git
cd dhafnck_mcp_main
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows
pip install -e .
```

### Step 2: Verify Installation

```bash
# Test the server
cd dhafnck_mcp_main
./diagnose_mcp_connection.sh

# Expected output:
# ✅ DhafnckMCP Server is healthy
# ✅ 25+ tools available
# ✅ Ready for Cursor integration
```

### Step 3: Configure Cursor MCP

#### For Standard Setup (Linux/Mac)

Create or edit `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "python",
      "args": ["-m", "fastmcp.server.mcp_entry_point"],
      "cwd": "/path/to/dhafnck_mcp_main",
      "env": {
        "PYTHONPATH": "/path/to/dhafnck_mcp_main/src",
        "TASKS_JSON_PATH": ".cursor/rules/tasks/tasks.json",
        "PROJECTS_FILE_PATH": ".cursor/rules/brain/projects.json",
        "CURSOR_AGENT_DIR_PATH": "/path/to/dhafnck_mcp_main/yaml-lib"
      }
    }
  }
}
```

#### For WSL Setup (Windows)

```json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "wsl.exe",
      "args": [
        "--cd", "/home/username/agentic-project/dhafnck_mcp_main",
        "--exec", "/home/username/agentic-project/dhafnck_mcp_main/.venv/bin/python",
        "-m", "fastmcp.server.mcp_entry_point"
      ],
      "env": {
        "PYTHONPATH": "/home/username/agentic-project/dhafnck_mcp_main/src",
        "TASKS_JSON_PATH": ".cursor/rules/tasks/tasks.json",
        "PROJECTS_FILE_PATH": ".cursor/rules/brain/projects.json"
      }
    }
  }
}
```

#### For Docker Setup

```json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "docker",
      "args": [
        "exec", "-i", "dhafnck-mcp",
        "python", "-m", "fastmcp.server.mcp_entry_point"
      ],
      "env": {
        "PYTHONPATH": "/app/src"
      }
    }
  }
}
```

### Step 4: Restart Cursor

1. Close Cursor IDE completely
2. Restart Cursor
3. Open your project
4. Wait for MCP initialization (check status bar)

### Step 5: Test Integration

1. Open Cursor chat (Ctrl+L or Cmd+L)
2. Try these test commands:
   ```
   @dhafnck_mcp health check
   @dhafnck_mcp list available tools
   @dhafnck_mcp create a test task
   ```

## ⚙️ Configuration

### Environment Variables

Configure these in your MCP configuration:

| Variable | Purpose | Default | Example |
|----------|---------|---------|---------|
| `PYTHONPATH` | Python module path | - | `/path/to/dhafnck_mcp_main/src` |
| `TASKS_JSON_PATH` | Task database location | `.cursor/rules/tasks/tasks.json` | Relative to project root |
| `PROJECTS_FILE_PATH` | Projects database | `.cursor/rules/brain/projects.json` | Relative to project root |
| `CURSOR_AGENT_DIR_PATH` | Agent configurations | `dhafnck_mcp_main/yaml-lib` | Path to agent YAML files |
| `FASTMCP_LOG_LEVEL` | Logging level | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

### Project Structure

DhafnckMCP creates this structure in your project:

```
your-project/
├── .cursor/
│   ├── mcp.json                    # MCP server configuration
│   └── rules/
│       ├── tasks/
│       │   ├── tasks.json          # Project tasks
│       │   └── backup/             # Task backups
│       ├── brain/
│       │   └── projects.json       # Project data
│       ├── auto_rule.mdc           # Auto-generated rules
│       └── contexts/               # Context files
└── your-project-files...
```

### Automated Setup

Use the setup script for quick configuration:

```bash
# Navigate to your project
cd /path/to/your/project

# Run automated setup
python /path/to/dhafnck_mcp_main/setup_project_mcp.py

# This automatically:
# - Creates .cursor/rules/ structure
# - Generates mcp.json configuration
# - Sets up project-specific task database
# - Configures environment variables
```

## 🛠️ Using MCP Tools in Cursor

### Basic Commands

#### Task Management
```
# Create tasks
@dhafnck_mcp create a task to implement user authentication

# List tasks
@dhafnck_mcp show all high priority tasks

# Update tasks
@dhafnck_mcp mark task "implement auth" as in progress

# Complete tasks
@dhafnck_mcp complete the authentication task
```

#### Project Management
```
# Create project
@dhafnck_mcp create a new project called "E-commerce Site"

# List projects
@dhafnck_mcp show all my projects

# Get project status
@dhafnck_mcp show status of current project
```

#### Agent Management
```
# List available agents
@dhafnck_mcp show all available agents

# Assign agents to tasks
@dhafnck_mcp assign coding agent to the auth task

# Switch to specific agent
@coding_agent help me implement this function
@system_architect_agent review this architecture
```

### Advanced Usage

#### Complex Task Creation
```
@dhafnck_mcp create a task with these details:
- Title: Build Payment System
- Priority: High
- Assignees: coding_agent, security_auditor_agent
- Labels: backend, payment, security
- Due date: 2024-02-15
- Description: Implement Stripe payment integration with security audit
```

#### Dependency Management
```
@dhafnck_mcp create task "Setup Database" that must be completed before "Implement Auth"
```

#### Search and Filtering
```
@dhafnck_mcp find all tasks with label "urgent"
@dhafnck_mcp show tasks assigned to coding_agent that are in progress
```

## 🤖 Multi-Agent Workflow

### Available Agents

#### Development Agents
- `@coding_agent` - Feature implementation, bug fixes
- `@code_reviewer_agent` - Code review, quality assurance
- `@development_orchestrator_agent` - Development workflow coordination

#### Architecture & Design
- `@system_architect_agent` - System architecture, technical decisions
- `@tech_spec_agent` - Technical specifications
- `@ui_designer_agent` - User interface design
- `@ux_researcher_agent` - User experience research

#### Testing & Quality
- `@test_orchestrator_agent` - Testing strategy, coordination
- `@functional_tester_agent` - Functional testing
- `@performance_load_tester_agent` - Performance testing
- `@security_auditor_agent` - Security audits, compliance

#### Operations
- `@devops_agent` - Infrastructure, deployment
- `@health_monitor_agent` - Monitoring, observability

### Agent Switching Workflow

```
# 1. Architecture Phase
@system_architect_agent design the overall system architecture

# 2. Implementation Phase
@coding_agent implement the user authentication system

# 3. Review Phase
@code_reviewer_agent review the authentication implementation

# 4. Testing Phase
@test_orchestrator_agent create comprehensive tests for auth

# 5. Security Phase
@security_auditor_agent audit the authentication system

# 6. Deployment Phase
@devops_agent set up deployment for the auth system
```

### Automatic Agent Assignment

DhafnckMCP automatically assigns appropriate agents based on task type:

```python
# Task automatically assigned to relevant agents
@dhafnck_mcp create a security-critical payment processing task

# System automatically assigns:
# - @coding_agent (implementation)
# - @security_auditor_agent (security review)
# - @test_orchestrator_agent (testing)
```

## 🏗️ Project-Specific Setup

### Multi-Project Workflow

DhafnckMCP supports multiple projects with independent task management:

```bash
# Project 1: Web Application
cd /home/user/webapp
python dhafnck_mcp_main/setup_project_mcp.py

# Project 2: Mobile App
cd /home/user/mobile-app
python dhafnck_mcp_main/setup_project_mcp.py

# Each project has independent:
# - Task databases
# - Agent assignments
# - Context rules
# - Project configurations
```

### Project Templates

Create project templates for common setups:

```json
// .cursor/mcp.template.json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "{{COMMAND}}",
      "args": ["{{ARGS}}"],
      "env": {
        "PROJECT_ROOT_PATH": "{{PROJECT_PATH}}",
        "TASKS_JSON_PATH": ".cursor/rules/tasks/tasks.json",
        "PROJECTS_FILE_PATH": ".cursor/rules/brain/projects.json"
      }
    }
  }
}
```

### Context Synchronization

DhafnckMCP automatically synchronizes context between sessions:

- **Auto-rule Generation**: Creates `.cursor/rules/auto_rule.mdc` with project-specific rules
- **Context Preservation**: Maintains task and project state across sessions
- **Agent Memory**: Agents remember previous interactions and decisions

## 🔧 Troubleshooting

### Common Issues

#### 1. MCP Server Not Found

**Symptoms**:
- "Failed to connect to MCP server" in Cursor
- MCP tools not available in chat

**Solutions**:
```bash
# Check server status
cd dhafnck_mcp_main
./diagnose_mcp_connection.sh

# Verify Python path
which python
echo $PYTHONPATH

# Test server manually
python -m fastmcp.server.mcp_entry_point
```

#### 2. WSL Integration Issues (Windows)

**Symptoms**:
- "spawn /bin/sh ENOENT" errors
- MCP server fails to start

**Solutions**:
```json
// Use full WSL path in .cursor/mcp.json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "wsl.exe",
      "args": [
        "--cd", "/home/username/agentic-project/dhafnck_mcp_main",
        "--exec", "/home/username/agentic-project/dhafnck_mcp_main/.venv/bin/python",
        "-m", "fastmcp.server.mcp_entry_point"
      ]
    }
  }
}
```

#### 3. Permission Errors

**Symptoms**:
- "Permission denied" when accessing files
- Tasks not saving

**Solutions**:
```bash
# Fix directory permissions
chmod -R 755 .cursor/rules/
chown -R $USER:$USER .cursor/rules/

# Create missing directories
mkdir -p .cursor/rules/{tasks,brain,contexts}
```

#### 4. Docker Integration Issues

**Symptoms**:
- MCP server can't connect to Docker container
- "Container not found" errors

**Solutions**:
```bash
# Ensure container is running
docker-compose ps

# Check container logs
docker-compose logs dhafnck-mcp

# Test container connectivity
docker-compose exec dhafnck-mcp python -c "print('Container accessible')"
```

### Diagnostic Tools

#### MCP Inspector

Use the MCP Inspector for interactive debugging:

```bash
cd dhafnck_mcp_main
npx @modelcontextprotocol/inspector python -m fastmcp.server.mcp_entry_point

# Opens web interface at http://localhost:6274
# Use this to test MCP tools interactively
```

#### Cursor Logs

Check Cursor logs for detailed error information:

- **Windows**: `%APPDATA%\Cursor\logs\`
- **macOS**: `~/Library/Logs/Cursor/`
- **Linux**: `~/.config/Cursor/logs/`

#### Server Health Check

```bash
# Comprehensive health check
./diagnose_mcp_connection.sh

# Manual health check
python -c "
from src.fastmcp.server.mcp_entry_point import create_dhafnck_mcp_server
server = create_dhafnck_mcp_server()
tools = server.get_tools()
print(f'✅ Server healthy with {len(tools)} tools')
"
```

### Getting Help

1. **Check Logs**: Start with Cursor and server logs
2. **Use Diagnostics**: Run the diagnostic scripts
3. **Test Components**: Isolate the issue (server, MCP, Cursor)
4. **Community Support**: Join our Discord/GitHub discussions

## 🚀 Advanced Configuration

### Custom Agent Configuration

Create custom agents for specialized tasks:

```yaml
# yaml-lib/custom_agent/custom_agent.yaml
name: "Custom Development Agent"
role: "Specialized for your specific framework/domain"
capabilities:
  - "Framework-specific expertise"
  - "Domain knowledge"
  - "Custom workflows"
tools:
  - "coding"
  - "testing"
  - "documentation"
contexts:
  - "Your project context"
  - "Framework-specific patterns"
```

### Environment-Specific Configurations

#### Development Environment
```json
// .cursor/mcp.dev.json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "python",
      "args": ["-m", "fastmcp.server.mcp_entry_point"],
      "env": {
        "FASTMCP_LOG_LEVEL": "DEBUG",
        "FASTMCP_ENABLE_RICH_TRACEBACKS": "1"
      }
    }
  }
}
```

#### Production Environment
```json
// .cursor/mcp.prod.json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "docker",
      "args": ["exec", "-i", "dhafnck-mcp-prod", "python", "-m", "fastmcp.server.mcp_entry_point"],
      "env": {
        "FASTMCP_LOG_LEVEL": "WARNING"
      }
    }
  }
}
```

### Performance Optimization

#### Memory Optimization
```json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "env": {
        "PYTHONPATH": "/path/to/src",
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

#### Connection Pooling
```python
# Custom server configuration
# In your project's MCP setup
{
  "connection_pool_size": 10,
  "max_concurrent_requests": 5,
  "request_timeout": 30
}
```

### Integration with CI/CD

```yaml
# .github/workflows/mcp-integration.yml
name: MCP Integration Test

on: [push, pull_request]

jobs:
  test-mcp:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install DhafnckMCP
        run: |
          cd dhafnck_mcp_main
          pip install -e .
      - name: Test MCP Server
        run: |
          python -m fastmcp.server.mcp_entry_point --test
      - name: Test MCP Tools
        run: |
          python -c "
          from src.fastmcp.server.mcp_entry_point import create_dhafnck_mcp_server
          server = create_dhafnck_mcp_server()
          assert len(server.get_tools()) > 20
          print('✅ MCP integration test passed')
          "
```

## 📚 Best Practices

### Project Organization

1. **One MCP Config Per Project**: Each project should have its own `.cursor/mcp.json`
2. **Consistent Directory Structure**: Use the standard `.cursor/rules/` structure
3. **Environment Variables**: Use environment variables for path configuration
4. **Version Control**: Include `.cursor/rules/` in version control (except sensitive data)

### Task Management

1. **Descriptive Titles**: Use clear, descriptive task titles
2. **Proper Labeling**: Use consistent labels for filtering and organization
3. **Agent Assignment**: Assign appropriate agents based on task type
4. **Dependencies**: Set up task dependencies for complex workflows

### Agent Usage

1. **Specialized Agents**: Use specific agents for their expertise areas
2. **Agent Switching**: Switch agents as you move through different phases
3. **Context Preservation**: Let agents maintain context across interactions
4. **Collaborative Tasks**: Use multiple agents for complex tasks

### Performance

1. **Resource Limits**: Set appropriate resource limits for MCP server
2. **Log Management**: Configure appropriate log levels and rotation
3. **Connection Management**: Monitor MCP connection health
4. **Cleanup**: Regularly clean up old tasks and data

## 📈 Monitoring & Analytics

### Usage Metrics

Track MCP usage with built-in analytics:

```python
# Get usage statistics
@dhafnck_mcp show usage statistics for this month
@dhafnck_mcp show most active agents
@dhafnck_mcp show task completion rates
```

### Performance Monitoring

```bash
# Monitor MCP server performance
@dhafnck_mcp show server performance metrics
@dhafnck_mcp show memory usage
@dhafnck_mcp show response times
```

### Health Monitoring

```bash
# Regular health checks
@dhafnck_mcp run health check
@dhafnck_mcp show system status
@dhafnck_mcp validate configuration
```

---

**Need Help?**
- 📖 Check the [User Guide](./USER_GUIDE.md) for general usage
- 🐳 See [Docker Setup Guide](./DOCKER_SETUP_GUIDE.md) for containerized deployment
- 🐛 Report integration issues on GitHub
- 💬 Join our community for Cursor-specific support

**Happy coding with DhafnckMCP and Cursor!** 🚀 