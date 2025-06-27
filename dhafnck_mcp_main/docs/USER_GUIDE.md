# 🚀 DhafnckMCP User Guide

Welcome to DhafnckMCP - your comprehensive Model Context Protocol (MCP) server for task management, agent orchestration, and project management.

## 📋 Table of Contents

1. [What is DhafnckMCP?](#what-is-dhafnckmcp)
2. [Quick Start](#quick-start)
3. [Installation Options](#installation-options)
4. [First Steps](#first-steps)
5. [Core Features](#core-features)
6. [Integration with Cursor IDE](#integration-with-cursor-ide)
7. [Task Management](#task-management)
8. [Multi-Agent System](#multi-agent-system)
9. [Project Management](#project-management)
10. [Troubleshooting](#troubleshooting)
11. [Advanced Usage](#advanced-usage)

## 🎯 What is DhafnckMCP?

DhafnckMCP is a powerful MCP server that provides:

- **Task Management**: Complete task lifecycle with dependencies, subtasks, and progress tracking
- **Multi-Agent Orchestration**: Coordinate specialized AI agents for different aspects of your project
- **Project Management**: Multi-project support with hierarchical organization
- **Cursor Integration**: Seamless integration with Cursor IDE for enhanced development workflow
- **Cloud-Scale Architecture**: Designed to scale from 50 RPS to 1M+ RPS

### Key Benefits

✅ **Productivity**: Streamline your development workflow with intelligent task management  
✅ **Collaboration**: Multi-agent system handles different aspects of your project  
✅ **Scalability**: Architecture designed for growth from small projects to enterprise scale  
✅ **Integration**: Native Cursor IDE integration for seamless development experience  

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** with pip
- **Docker & Docker Compose** (recommended)
- **Cursor IDE** (for full integration)
- **WSL2** (if using Windows)

### Option 1: Docker Setup (Recommended)

The fastest way to get started:

```bash
# 1. Clone the repository
git clone https://github.com/dhafnck/dhafnck_mcp.git
cd dhafnck_mcp_main

# 2. Quick setup with Docker
docker-compose up -d --build

# 3. Verify installation
docker-compose exec dhafnck-mcp python -c "
from src.fastmcp.server.mcp_entry_point import create_dhafnck_mcp_server
server = create_dhafnck_mcp_server()
print('✅ DhafnckMCP Server is running successfully!')
"
```

### Option 2: Python Virtual Environment

For development or custom setups:

```bash
# 1. Clone and navigate
git clone https://github.com/dhafnck/dhafnck_mcp.git
cd dhafnck_mcp_main

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -e .

# 4. Start the server
./run_mcp_server.sh
```

## 📦 Installation Options

### Docker Installation (Production Ready)

**Advantages**: Isolated environment, easy deployment, consistent across systems

```bash
# Full setup with persistent data
mkdir -p data logs config
cp env.example .env
docker-compose up -d --build

# Development mode with hot reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Python Installation (Development)

**Advantages**: Direct access to code, easier debugging, faster iteration

```bash
# Using UV (recommended package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh
uv sync

# Or using pip
pip install -e .
```

### Project-Specific Setup

Set up DhafnckMCP for any project location:

```bash
# Navigate to your project
cd /path/to/your/project

# Run automated setup
python /path/to/dhafnck_mcp_main/setup_project_mcp.py

# This creates:
# - .cursor/rules/ directory structure
# - Project-specific task database
# - MCP configuration for Cursor
```

## 🎯 First Steps

### 1. Verify Installation

```bash
# Check server health
curl -X POST http://localhost:8000/health || echo "Server running in MCP mode"

# Or use the diagnostic script
./diagnose_mcp_connection.sh
```

### 2. Set Up Your First Project

```bash
# Create a new project
python -c "
from src.fastmcp.tools.project_management import create_project
result = create_project('my_first_project', 'My First DhafnckMCP Project')
print(f'✅ Created project: {result}')
"
```

### 3. Create Your First Task

```bash
# Create a task
python -c "
from src.fastmcp.tools.task_management import create_task
result = create_task(
    project_id='my_first_project',
    title='Learn DhafnckMCP',
    description='Explore the features of DhafnckMCP',
    priority='high'
)
print(f'✅ Created task: {result}')
"
```

## ⭐ Core Features

### Task Management

**Complete Lifecycle Management**
- Create, update, complete, and delete tasks
- Set priorities, due dates, and effort estimates
- Add dependencies between tasks
- Track progress with subtasks
- Assign tasks to specialized agents

**Example Workflow**:
```python
# Create a complex task with subtasks
task = create_task(
    title="Build User Authentication",
    description="Implement JWT-based authentication system",
    priority="high",
    assignees=["@coding_agent", "@security_auditor_agent"],
    labels=["backend", "security"],
    estimated_effort="large"
)

# Add subtasks
add_subtask(task_id, {
    "title": "Design JWT token structure",
    "assignee": "@security_auditor_agent"
})

add_subtask(task_id, {
    "title": "Implement token validation",
    "assignee": "@coding_agent"
})
```

### Multi-Agent System

**50+ Specialized Agents** including:
- `@coding_agent` - Feature implementation and bug fixes
- `@system_architect_agent` - Architecture design and technical decisions
- `@test_orchestrator_agent` - Testing strategies and quality assurance
- `@security_auditor_agent` - Security reviews and compliance
- `@devops_agent` - Infrastructure and deployment
- `@ui_designer_agent` - User interface and experience design

**Agent Collaboration**:
```python
# Agents automatically collaborate based on task requirements
task = create_task(
    title="Implement Payment System",
    assignees=["@coding_agent", "@security_auditor_agent", "@test_orchestrator_agent"]
)
# Each agent contributes their expertise to the task
```

### Project Management

**Multi-Project Support**:
- Hierarchical project organization
- Project-specific task trees
- Independent agent assignments per project
- Cross-project reporting and analytics

## 🖥️ Integration with Cursor IDE

### Setup Cursor Integration

1. **Install DhafnckMCP** (see installation options above)

2. **Configure Cursor MCP Settings**:
   ```json
   // In .cursor/mcp.json
   {
     "mcpServers": {
       "dhafnck_mcp": {
         "command": "python",
         "args": ["-m", "fastmcp.server.mcp_entry_point"],
         "env": {
           "PYTHONPATH": "/path/to/dhafnck_mcp_main/src"
         }
       }
     }
   }
   ```

3. **Restart Cursor IDE**

4. **Test Integration**:
   - Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
   - Search for "MCP" commands
   - Try creating a task or project

### Using MCP Tools in Cursor

**Task Management in Cursor**:
```
# In Cursor chat, you can now use:
@dhafnck_mcp create a task for implementing user login
@dhafnck_mcp list all high priority tasks
@dhafnck_mcp assign the authentication task to coding agent
```

**Agent Switching**:
```
# Switch to specialized agents
@coding_agent help me implement this function
@system_architect_agent review this architecture
@test_orchestrator_agent create tests for this component
```

## 📋 Task Management

### Basic Task Operations

```python
# Create task
create_task(
    title="Implement user registration",
    description="Add user registration with email validation",
    priority="high",
    due_date="2024-02-15",
    assignees=["@coding_agent"],
    labels=["backend", "auth"]
)

# Update task
update_task(
    task_id="task_123",
    status="in_progress",
    priority="urgent"
)

# Complete task
complete_task(task_id="task_123")

# List tasks with filters
list_tasks(
    status="todo",
    priority="high",
    assignee="@coding_agent"
)
```

### Advanced Task Features

**Dependencies**:
```python
# Create task dependency
add_task_dependency(
    task_id="task_123",
    depends_on="task_456"
)
```

**Subtasks**:
```python
# Add subtasks for detailed tracking
add_subtask(task_id="task_123", {
    "title": "Design database schema",
    "assignee": "@system_architect_agent"
})
```

**Search and Filtering**:
```python
# Search tasks by content
search_tasks(query="authentication login")

# Filter by multiple criteria
list_tasks(
    labels=["urgent", "bug"],
    status="todo",
    assignee="@coding_agent"
)
```

## 🤖 Multi-Agent System

### Available Agent Categories

**Development Agents**:
- `@coding_agent` - Core development and implementation
- `@code_reviewer_agent` - Code review and quality assurance
- `@development_orchestrator_agent` - Development workflow coordination

**Architecture & Design**:
- `@system_architect_agent` - System architecture and design
- `@tech_spec_agent` - Technical specifications
- `@ui_designer_agent` - User interface design
- `@ux_researcher_agent` - User experience research

**Testing & Quality**:
- `@test_orchestrator_agent` - Testing strategy and coordination
- `@functional_tester_agent` - Functional testing
- `@performance_load_tester_agent` - Performance and load testing
- `@security_auditor_agent` - Security testing and audits

**Operations & Deployment**:
- `@devops_agent` - Infrastructure and deployment
- `@health_monitor_agent` - System monitoring and observability

### Agent Usage Examples

**Collaborative Development**:
```python
# Architecture phase
assign_task("design_system", "@system_architect_agent")

# Implementation phase  
assign_task("implement_features", "@coding_agent")

# Testing phase
assign_task("create_tests", "@test_orchestrator_agent")

# Deployment phase
assign_task("deploy_system", "@devops_agent")
```

**Multi-Agent Task**:
```python
create_task(
    title="Build E-commerce Checkout",
    assignees=[
        "@system_architect_agent",  # Design architecture
        "@coding_agent",           # Implement features
        "@security_auditor_agent", # Security review
        "@test_orchestrator_agent" # Testing strategy
    ]
)
```

## 🏗️ Project Management

### Project Lifecycle

```python
# Create project
create_project(
    project_id="ecommerce_site",
    name="E-commerce Website",
    description="Full-featured e-commerce platform"
)

# Create task trees for different phases
create_task_tree(
    project_id="ecommerce_site",
    tree_id="mvp_phase",
    name="MVP Development Phase"
)

# Assign agents to project
assign_agent_to_project(
    project_id="ecommerce_site",
    agent_id="coding_agent"
)
```

### Multi-Project Management

```python
# List all projects
list_projects()

# Get project status
get_project_status("ecommerce_site")

# Cross-project reporting
get_project_analytics([
    "ecommerce_site",
    "mobile_app",
    "admin_dashboard"
])
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Server Won't Start

**Symptoms**: Import errors, module not found
**Solutions**:
```bash
# Check Python path
echo $PYTHONPATH

# Verify virtual environment
which python
pip list | grep fastmcp

# Reinstall dependencies
pip install -e . --force-reinstall
```

#### 2. Cursor Integration Issues

**Symptoms**: MCP tools not available in Cursor
**Solutions**:
```bash
# Check MCP configuration
cat .cursor/mcp.json

# Verify server can start
python -m fastmcp.server.mcp_entry_point

# Check Cursor logs
# Windows: %APPDATA%\Cursor\logs
# Mac: ~/Library/Logs/Cursor
# Linux: ~/.config/Cursor/logs
```

#### 3. WSL Integration (Windows Users)

**Symptoms**: Spawn errors, path issues
**Solutions**:
```json
// Use wsl.exe in .cursor/mcp.json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "wsl.exe",
      "args": [
        "--cd", "/path/to/project",
        "--exec", "/path/to/.venv/bin/python",
        "-m", "fastmcp.server.mcp_entry_point"
      ]
    }
  }
}
```

#### 4. Docker Issues

**Symptoms**: Container won't start, permission errors
**Solutions**:
```bash
# Fix permissions
sudo chown -R $USER:$USER data logs

# Clean build
docker-compose down
docker system prune -f
docker-compose up --build

# Check logs
docker-compose logs dhafnck-mcp
```

### Diagnostic Tools

```bash
# Comprehensive diagnostics
./diagnose_mcp_connection.sh

# Check server health
curl -X POST http://localhost:8000/health

# Test MCP inspector
npx @modelcontextprotocol/inspector python -m fastmcp.server.mcp_entry_point
```

### Getting Help

1. **Check Logs**: Always start with server logs for error details
2. **Use Diagnostics**: Run the diagnostic scripts provided
3. **MCP Inspector**: Use the inspector for interactive debugging
4. **Documentation**: Refer to specific guides (Docker, WSL, etc.)

## 🚀 Advanced Usage

### Custom Agent Configuration

```yaml
# Create custom agent in yaml-lib/
custom_agent:
  name: "Custom Development Agent"
  role: "Specialized development tasks"
  capabilities:
    - "Custom framework expertise"
    - "Domain-specific knowledge"
  tools:
    - "coding"
    - "testing"
    - "documentation"
```

### API Integration

```python
# Direct API usage
from fastmcp.server.mcp_entry_point import create_dhafnck_mcp_server

server = create_dhafnck_mcp_server()
tools = server.get_tools()

# Execute tool
result = server.execute_tool("create_task", {
    "title": "API Integration Task",
    "priority": "high"
})
```

### Automation Scripts

```python
# Automated project setup
def setup_new_project(name, agents):
    project = create_project(name, f"Automated project: {name}")
    
    for agent in agents:
        assign_agent_to_project(project['id'], agent)
    
    # Create initial tasks
    create_task(
        project_id=project['id'],
        title="Project Setup",
        assignees=agents[:1]
    )
    
    return project
```

### Performance Optimization

```bash
# Production configuration
export FASTMCP_LOG_LEVEL=WARNING
export FASTMCP_ENABLE_RICH_TRACEBACKS=0

# Resource limits in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G
      cpus: '0.5'
```

## 📚 Next Steps

1. **Explore Examples**: Check the `examples/` directory for usage patterns
2. **Read Architecture Docs**: Understand the cloud-scale architecture in `.cursor/rules/technical_architect/`
3. **Join Community**: Connect with other users and contributors
4. **Contribute**: Help improve DhafnckMCP with feedback and contributions

---

**Need Help?** 
- 📖 Check our [troubleshooting guides](./troubleshooting/)
- 🐛 Report issues on GitHub
- 💬 Join our community discussions

**Happy coding with DhafnckMCP!** 🚀 