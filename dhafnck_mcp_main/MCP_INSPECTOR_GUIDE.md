# MCP Inspector Guide for DhafnckMCP Server

## 🚀 Quick Start

The MCP Inspector is working correctly with your DhafnckMCP server! Here's how to use it:

### 1. Start the MCP Inspector

```bash
cd /home/<username>/agentic-project/dhafnck_mcp_main
npx @modelcontextprotocol/inspector /home/<username>/agentic-project/dhafnck_mcp_main/.venv/bin/python -m fastmcp.server.mcp_entry_point
```

### 2. Access the Inspector

The inspector will start and provide you with:
- **Proxy server**: `127.0.0.1:6277`
- **Inspector URL**: `http://localhost:6274`
- **Authentication token**: A unique session token for security

Example output:
```
🔗 Open inspector with token pre-filled:
   http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=378a9063539dce6655f5ce25075308806d0db86c198a010756e0c8970dc398be
```

#### 💡 **Cursor IDE Integration**
**Important**: To test the MCP tools directly in Cursor IDE:
1. Press `Ctrl + Shift + P` to open the command palette
2. Type "MCP" or search for MCP-related commands
3. Use the URL provided by the inspector for testing tools
4. This allows you to test MCP functionality directly within your development environment

## 🛠️ Available Tools

Your DhafnckMCP server provides comprehensive task management and agent orchestration capabilities:

### Core Features
- **Task Management**: Create, update, complete, list, and search tasks
- **Project Management**: Full project lifecycle management
- **Agent Orchestration**: Multi-agent coordination and assignment
- **Cursor Rules Integration**: Automated rule generation and validation
- **Multi-Agent Coordination**: Advanced agent collaboration

### Key Tools You Can Test

#### 1. Health Check
```json
{
  "name": "health_check",
  "arguments": {}
}
```

#### 2. Server Capabilities
```json
{
  "name": "get_server_capabilities",
  "arguments": {}
}
```

#### 3. Task Management
```json
{
  "name": "create_task",
  "arguments": {
    "title": "Test Task",
    "description": "Testing MCP connection",
    "priority": "medium"
  }
}
```

#### 4. Project Management
```json
{
  "name": "create_project",
  "arguments": {
    "name": "Test Project",
    "description": "Testing project creation via MCP"
  }
}
```

## 🔧 Configuration Details

### Environment Variables
Your server is configured with these environment variables:
- `PYTHONPATH`: `dhafnck_mcp_main/src`
- `TASKS_JSON_PATH`: `.cursor/rules/tasks/tasks.json`
- `PROJECTS_FILE_PATH`: `.cursor/rules/brain/projects.json`
- `CURSOR_AGENT_DIR_PATH`: `dhafnck_mcp_main/yaml-lib`

### Server Configuration
- **Name**: "DhafnckMCP - Task Management & Agent Orchestration"
- **Version**: "2.0.0"
- **Transport**: STDIO
- **Task Management**: Enabled
- **Multi-Agent Support**: Enabled

## 🎯 Testing Workflow

### 1. Basic Connection Test
1. Start the inspector with the command above
2. **Option A - Browser**: Open the provided URL in your browser
3. **Option B - Cursor IDE**: Press `Ctrl + Shift + P` and search for MCP commands
4. Use the authentication token if required
5. Try the `health_check` tool to verify connection

### 2. Feature Testing
1. **Health Check**: Verify server status
2. **Get Capabilities**: See all available features
3. **Create Task**: Test task management
4. **List Tasks**: Verify task persistence
5. **Create Project**: Test project management

### 3. Advanced Testing
1. **Agent Management**: Register and assign agents
2. **Task Dependencies**: Create complex task relationships
3. **Cursor Integration**: Test auto-rule generation
4. **Multi-Agent Orchestration**: Test agent coordination

## 🐛 Troubleshooting

### WSL Connection Issues

If you're experiencing MCP connection issues in WSL environment (Cursor on Windows with WSL), see our dedicated guides:

- **Quick Fix**: [WSL_MCP_QUICK_FIX.md](./WSL_MCP_QUICK_FIX.md) - Immediate solution for WSL connection problems
- **Detailed Guide**: [WSL_MCP_TROUBLESHOOTING_GUIDE.md](./WSL_MCP_TROUBLESHOOTING_GUIDE.md) - Comprehensive troubleshooting for WSL environments

### Common Issues

#### 1. "ENOENT" Error
- **Cause**: Incorrect file path or WSL integration issue
- **Solution**: Use the full path as shown in the quick start command, or see WSL guides above

#### 2. Module Import Error
- **Cause**: PYTHONPATH not set correctly
- **Solution**: Ensure you're in the correct directory and virtual environment is activated

#### 3. Connection Timeout
- **Cause**: Server taking too long to start
- **Solution**: Check server logs and ensure all dependencies are installed

#### 4. WSL Spawn Errors (`spawn /bin/sh ENOENT`)
- **Cause**: Cursor (Windows) cannot spawn processes in WSL environment
- **Solution**: Use `wsl.exe` command in `.cursor/mcp.json` configuration (see WSL guides)

### Debug Commands

```bash
# Activate virtual environment
cd /home/<username>/agentic-project/dhafnck_mcp_main
source .venv/bin/activate

# Test module import
python -c "from fastmcp.server.mcp_entry_point import main; print('Module import successful')"

# Check environment variables
env | grep -E "(PYTHONPATH|TASKS_JSON_PATH|PROJECTS_FILE_PATH)"
```

## 📊 Expected Results

When working correctly, you should see:

### Health Check Response
```json
{
  "status": "healthy",
  "server_name": "DhafnckMCP - Task Management & Agent Orchestration",
  "version": "2.0.0",
  "task_management": {
    "task_management_enabled": true,
    "enabled_tools_count": 25+,
    "enabled_tools": ["create_task", "get_task", "list_tasks", ...]
  }
}
```

### Capabilities Response
```json
{
  "core_features": [
    "Task Management",
    "Project Management", 
    "Agent Orchestration",
    "Cursor Rules Integration",
    "Multi-Agent Coordination"
  ],
  "available_actions": {
    "project_management": [...],
    "task_management": [...],
    "agent_management": [...]
  }
}
```

## 🔗 Integration with Cursor

This MCP server integrates seamlessly with Cursor IDE through the `.cursor/mcp.json` configuration:

```json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "/home/<username>/agentic-project/dhafnck_mcp_main/.venv/bin/python",
      "args": ["-m", "fastmcp.server.mcp_entry_point"],
      "cwd": "/home/<username>/agentic-project",
      "env": { ... }
    }
  }
}
```

### 🎮 **Using MCP Tools in Cursor IDE**
1. **Start the Inspector**: Run the inspector command to get the authentication URL
2. **Open Command Palette**: Press `Ctrl + Shift + P` in Cursor
3. **Search MCP Commands**: Type "MCP" to find available MCP-related commands
4. **Test Tools**: Use the inspector URL for testing and debugging MCP tools
5. **Direct Integration**: Once configured, MCP tools are available directly in the Cursor chat interface

## 🎉 Success Indicators

Your MCP server is working correctly when you see:
- ✅ Inspector starts without errors
- ✅ Health check returns "healthy" status
- ✅ Task management tools are enabled
- ✅ Server capabilities show all expected features
- ✅ You can create and manage tasks/projects through the inspector

## 📝 Notes

- The server uses STDIO transport for MCP communication
- All tools are consolidated into a single server instance
- Task management is enabled by default
- The server supports both synchronous and asynchronous operations
- Multi-agent coordination is built-in and ready to use 