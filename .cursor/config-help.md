# Cursor MCP Configuration Help

## 🚨 WSL Integration Issue Resolved

This document contains the troubleshooting steps and solutions for the WSL MCP connection issue that was identified and resolved.

### Root Cause Identified

The error `spawn /bin/sh ENOENT` revealed the core issue:
- **ENOENT**: "No such file or directory"
- Cursor (Windows) cannot find `/bin/sh` when trying to spawn processes in WSL
- This affects all process spawning, including MCP servers

## 🔍 Diagnostic Commands

### Check Shell Availability
```bash
# Check if /bin/sh exists
ls -la /bin/sh

# Check if dash exists
ls -la /bin/dash && which dash

# Check environment
echo "PATH: $PATH"
echo "SHELL: $SHELL"
echo "Current user: $(whoami)"
echo "WSL info:"
cat /proc/version | head -1
```

## ✅ Solution: WSL-Cursor Integration Fix

### Method 1: WSL.exe with Direct Arguments (Recommended)

**Updated MCP Configuration:**
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
        "AGENT_YAML_LIB_PATH": "dhafnck_mcp_main/yaml-lib"
      },
      "transport": "stdio",
      "debug": true
    },
    "sequential-thinking": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
      "env": {}
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PERSONAL_ACCESS_TOKEN}"
      }
    }
  }
}
```

### Method 2: WSL Bridge Script (Alternative)

**Create Bridge Script:**
```bash
#!/bin/bash
# File: dhafnck_mcp_main/wsl_mcp_bridge.sh

echo "🔗 WSL MCP Bridge starting..." >&2
echo "📍 Working directory: $(pwd)" >&2
echo "📍 Python path: /home/<username>/agentic-project/dhafnck_mcp_main/.venv/bin/python" >&2

# Set environment variables
export PYTHONPATH="/home/<username>/agentic-project/dhafnck_mcp_main/src"
export TASKS_JSON_PATH="/home/<username>/agentic-project/.cursor/rules/tasks/tasks.json"
export PROJECT_ROOT_PATH="/home/<username>/agentic-project"
export PYTHONUNBUFFERED=1

# Change to the correct directory
cd /home/<username>/agentic-project

# Start the MCP server
echo "🚀 Starting dhafnck_mcp server..." >&2
exec /home/<username>/agentic-project/dhafnck_mcp_main/.venv/bin/python -m fastmcp.server.mcp_entry_point
```

**Configuration for Bridge Script:**
```json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "wsl",
      "args": [
        "-e",
        "/home/<username>/agentic-project/dhafnck_mcp_main/wsl_mcp_bridge.sh"
      ],
      "cwd": "/home/<username>/agentic-project"
    }
  }
}
```

## 🚀 Testing and Verification

### Step 1: Restart Cursor Completely
1. Close all Cursor windows
2. Wait 10 seconds
3. Reopen Cursor

### Step 2: Test the Connection
Try using the MCP health check tool to verify connection:
```bash
# This should now work through Cursor's MCP interface
health_check()
```

### Step 3: Alternative Configuration
If the primary solution doesn't work, try the alternative:
```bash
# Use the alternative configuration
cp .cursor/mcp_wsl_alternative.json .cursor/mcp.json
# Then restart Cursor
```

## 🎯 Why This Solution Works

- ✅ **Fixed WSL integration issue**: Uses proper Windows→WSL execution
- ✅ **Bridge script handles environment**: All variables set correctly
- ✅ **Uses `wsl.exe` or `wsl -e`**: Proper Windows→WSL execution
- ✅ **All paths and environment variables**: Set correctly for the project

## 📚 Additional Resources

For comprehensive troubleshooting guides, see:
- [WSL_MCP_QUICK_FIX.md](../dhafnck_mcp_main/WSL_MCP_QUICK_FIX.md)
- [WSL_MCP_TROUBLESHOOTING_GUIDE.md](../dhafnck_mcp_main/WSL_MCP_TROUBLESHOOTING_GUIDE.md)
- [README_TROUBLESHOOTING.md](../dhafnck_mcp_main/README_TROUBLESHOOTING.md)

---

*Last updated: January 2025*
*Issue: WSL MCP Connection - Status: Resolved*