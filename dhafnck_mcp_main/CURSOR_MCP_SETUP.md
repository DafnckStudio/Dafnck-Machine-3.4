# DhafnckMCP Cursor Setup Guide

Complete setup guide for integrating DhafnckMCP with Cursor IDE across different environments.

## 🚀 Quick Start

1. **Generate your API token** at [DhafnckMCP Dashboard](https://your-domain.com/dashboard)
2. **Choose your environment** (Docker recommended for beginners)
3. **Copy the configuration** to your `mcp.json` file
4. **Restart Cursor** to activate the MCP server

## 📋 Environment Configurations

### 🐳 Docker Setup (Recommended)

**Best for:** Beginners, isolated environments, cross-platform compatibility

```json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "DHAFNCK_TOKEN=your_token_here",
        "-v", "dhafnck-data:/data",
        "dhafnck/mcp-server:latest"
      ],
      "env": {
        "DHAFNCK_TOKEN": "your_token_here"
      },
      "transport": "stdio",
      "debug": true
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
      "env": {},
      "transport": "stdio"
    }
  }
}
```

**Setup Steps:**
1. Install Docker Desktop and ensure it's running
2. Pull the DhafnckMCP Docker image: `docker pull dhafnck/mcp-server:latest`
3. Replace `your_token_here` with your actual API token
4. Add configuration to your `mcp.json` file
5. Restart Cursor

### 🪟 WSL (Windows Subsystem for Linux)

**Best for:** Windows users who want native performance with WSL2

```json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "wsl.exe",
      "args": [
        "--cd", "/home/<username>/agentic-project",
        "--exec", "/home/<username>/agentic-project/dhafnck_mcp_main/.venv/bin/python",
        "-m", "fastmcp.server.mcp_entry_point"
      ],
      "env": {
        "PYTHONPATH": "dhafnck_mcp_main/src",
        "TASKS_JSON_PATH": ".cursor/rules/tasks/tasks.json",
        "TASK_JSON_BACKUP_PATH": ".cursor/rules/tasks/backup",
        "MCP_TOOL_CONFIG": ".cursor/tool_config.json",
        "AGENTS_OUTPUT_DIR": ".cursor/rules/agents",
        "AUTO_RULE_PATH": ".cursor/rules/auto_rule.mdc",
        "BRAIN_DIR_PATH": ".cursor/rules/brain",
        "PROJECTS_FILE_PATH": ".cursor/rules/brain/projects.json",
        "PROJECT_ROOT_PATH": ".",
        "CURSOR_AGENT_DIR_PATH": "dhafnck_mcp_main/yaml-lib",
        "AGENT_YAML_LIB_PATH": "dhafnck_mcp_main/yaml-lib",
        "DHAFNCK_TOKEN": "your_token_here"
      },
      "transport": "stdio",
      "debug": true
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
      "env": {},
      "transport": "stdio"
    }
  }
}
```

**Setup Steps:**
1. Replace `<username>` with your actual Windows username
2. Ensure WSL2 is installed and running
3. Navigate to `/home/<username>/agentic-project` in WSL
4. Activate the virtual environment: `source dhafnck_mcp_main/.venv/bin/activate`
5. Install dependencies: `pip install -e dhafnck_mcp_main/`
6. Replace `your_token_here` with your actual API token
7. Add configuration to your `mcp.json` file
8. Restart Cursor

### 🐧🍎 Linux/macOS Native

**Best for:** Linux and macOS users who prefer native execution

```json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "/home/<username>/agentic-project/dhafnck_mcp_main/.venv/bin/python",
      "args": [
        "-m",
        "fastmcp.server.mcp_entry_point"
      ],
      "cwd": "/home/<username>/agentic-project",
      "env": {
        "PYTHONPATH": "dhafnck_mcp_main/src",
        "TASKS_JSON_PATH": ".cursor/rules/tasks/tasks.json",
        "TASK_JSON_BACKUP_PATH": ".cursor/rules/tasks/backup",
        "MCP_TOOL_CONFIG": ".cursor/tool_config.json",
        "AGENTS_OUTPUT_DIR": ".cursor/rules/agents",
        "AUTO_RULE_PATH": ".cursor/rules/auto_rule.mdc",
        "BRAIN_DIR_PATH": ".cursor/rules/brain",
        "PROJECTS_FILE_PATH": ".cursor/rules/brain/projects.json",
        "PROJECT_ROOT_PATH": ".",
        "CURSOR_AGENT_DIR_PATH": "dhafnck_mcp_main/yaml-lib",
        "AGENT_YAML_LIB_PATH": "dhafnck_mcp_main/yaml-lib",
        "DHAFNCK_TOKEN": "your_token_here"
      },
      "transport": "stdio",
      "debug": true
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
      "env": {},
      "transport": "stdio"
    }
  }
}
```

**Setup Steps:**
1. Replace `<username>` with your actual username
2. Ensure Python 3.10+ is installed
3. Navigate to `/home/<username>/agentic-project` (or equivalent on macOS)
4. Activate the virtual environment: `source dhafnck_mcp_main/.venv/bin/activate`
5. Install dependencies: `pip install -e dhafnck_mcp_main/`
6. Replace `your_token_here` with your actual API token
7. Add configuration to your `mcp.json` file
8. Restart Cursor

## 🧠 Sequential Thinking MCP (Recommended)

The Sequential Thinking MCP is highly recommended for enhanced problem-solving capabilities. It provides:

- **Complex Problem Solving**: Break down complex tasks into manageable steps
- **Multi-step Reasoning**: Chain thoughts together for better analysis
- **Adaptive Thinking**: Adjust approach based on intermediate results
- **Better Planning**: Structured approach to task planning and execution

### Why Include It?

When working with DhafnckMCP's task management and agent orchestration features, the Sequential Thinking MCP enhances:

1. **Task Planning**: Better breakdown of complex projects
2. **Agent Coordination**: More sophisticated multi-agent workflows  
3. **Problem Analysis**: Deeper analysis of technical challenges
4. **Decision Making**: Structured approach to architecture decisions

## 🛠️ Available MCP Tools

Once configured, you'll have access to these powerful tools:

### Core Task Management
- `manage_project` - Create and manage projects
- `manage_task` - Full task lifecycle management
- `manage_subtask` - Break down complex tasks
- `manage_agent` - Multi-agent team coordination

### Agent System
- `call_agent` - Switch to specialized agent roles
- `update_auto_rule` - Dynamic context management
- `regenerate_auto_rule` - Smart rule generation

### System Management
- `validate_rules` - Rule system health checks
- `manage_cursor_rules` - Cursor rules administration
- `validate_tasks_json` - Task database integrity

### Enhanced Reasoning (with Sequential Thinking)
- `sequentialthinking` - Complex problem-solving and analysis

## 📍 Finding Your mcp.json File

### Windows
```
%APPDATA%\Cursor\User\mcp.json
```

### macOS
```
~/Library/Application Support/Cursor/User/mcp.json
```

### Linux
```
~/.config/Cursor/User/mcp.json
```

## 🔧 Configuration Steps

1. **Open Cursor Settings**
   - Press `Cmd/Ctrl + ,`
   - Search for "MCP" or navigate to Extensions → MCP

2. **Create or Edit mcp.json**
   - If the file doesn't exist, create it in the location above
   - Add your chosen configuration from this guide

3. **Replace Placeholders**
   - `your_token_here` → Your actual API token
   - `<username>` → Your system username

4. **Restart Cursor**
   - Close and reopen Cursor completely
   - Check the MCP status in the bottom status bar

## 🐛 Troubleshooting

### Common Issues

**MCP Server Not Starting**
- Check that your API token is valid
- Ensure all paths are correct for your system
- Verify Docker is running (for Docker setup)
- Check Cursor's developer console for errors

**Permission Errors (WSL/Linux/macOS)**
- Ensure the Python executable has proper permissions
- Check that the virtual environment is activated
- Verify all file paths exist and are accessible

**Token Authentication Errors**
- Generate a new token from the dashboard
- Ensure the token is correctly copied without extra spaces
- Check that the DHAFNCK_TOKEN environment variable is set

### Debug Mode

All configurations include `"debug": true` which provides detailed logging:
- Check Cursor's developer console (Help → Toggle Developer Tools)
- Look for MCP-related log messages
- Use logs to identify specific issues

## 🚀 Next Steps

After successful setup:

1. **Test the Connection**: Try using `@dhafnck_mcp` in Cursor chat
2. **Explore Tools**: Use `manage_project` to create your first project
3. **Agent Switching**: Try `call_agent` with different agent roles
4. **Complex Tasks**: Use Sequential Thinking for multi-step problems

## 📚 Additional Resources

- [DhafnckMCP Documentation](https://github.com/dhafnck/dhafnck_mcp)
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [Cursor MCP Guide](https://docs.cursor.com/mcp)
- [Sequential Thinking MCP](https://github.com/modelcontextprotocol/servers/tree/main/src/sequential-thinking)

## 💬 Support

- [GitHub Issues](https://github.com/dhafnck/dhafnck_mcp/issues)
- [Community Discussions](https://github.com/dhafnck/dhafnck_mcp/discussions)
- [Documentation](https://github.com/dhafnck/dhafnck_mcp/wiki)

---

**Happy coding with DhafnckMCP! 🎉** 