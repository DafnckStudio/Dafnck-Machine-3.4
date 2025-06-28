# WSL MCP Server Troubleshooting Guide

## 🚨 Problem: MCP Server Not Connecting in WSL Environment

### Symptoms
- Cursor shows "Connection Error - Check if your MCP server is running and proxy token is correct"
- MCP server works perfectly when tested directly in WSL
- Other MCP servers (sequential-thinking, github, memory) work fine
- Cursor logs show `spawn /bin/sh ENOENT` or similar spawn errors
- 0 tools available from your MCP server despite server being functional

### Root Cause
**WSL Integration Issue**: Cursor (running on Windows) cannot properly execute shell commands or spawn processes in the WSL environment using standard Unix paths and commands.

---

## 🔍 Diagnostic Steps

### 1. Verify Server Functionality
First, confirm your MCP server works in WSL:

```bash
cd /home/username/your-project
source dhafnck_mcp_main/.venv/bin/activate
python -m fastmcp.server.mcp_entry_point
```

If the server starts successfully and shows your tools, the issue is WSL integration, not the server itself.

### 2. Check Cursor Logs
Look for MCP-related errors:

```bash
# Check Cursor logs (note the capital C)
ls ~/.config/Cursor/logs/
tail -f ~/.config/Cursor/logs/main.log
```

### 3. Test Process Spawning
Try this to confirm WSL spawn issues:

```bash
# This should work in WSL
echo "WSL works"

# But Cursor from Windows cannot spawn this directly
```

---

## ✅ Solutions

### Solution 1: WSL.exe with Direct Arguments (Recommended)

Update your `.cursor/mcp.json` configuration:

```json
{
  "mcpServers": {
    "your_mcp_server": {
      "command": "wsl.exe",
      "args": [
        "--cd", "/home/username/your-project",
        "--exec", "/home/username/your-project/path/to/.venv/bin/python",
        "-m", "your.module.entry_point"
      ],
      "env": {
        "PYTHONPATH": "src",
        "OTHER_ENV_VAR": "value"
      }
    }
  }
}
```

**Example for dhafnck_mcp**:
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
        "RULES_DIR": ".cursor/rules"
      }
    }
  }
}
```

### Solution 2: WSL Bridge Script (Alternative)

Create a bridge script if you need more complex setup:

**Create `wsl_mcp_bridge.sh`**:
```bash
#!/bin/bash
set -e

# Navigate to project directory
cd /home/username/your-project

# Set environment variables
export PYTHONPATH="src"
export YOUR_ENV_VAR="value"

# Activate virtual environment and run server
source path/to/.venv/bin/activate
exec python -m your.module.entry_point
```

**Make it executable**:
```bash
chmod +x wsl_mcp_bridge.sh
```

**Update `.cursor/mcp.json`**:
```json
{
  "mcpServers": {
    "your_mcp_server": {
      "command": "wsl",
      "args": ["-e", "/home/username/your-project/wsl_mcp_bridge.sh"]
    }
  }
}
```

---

## 🔧 Configuration Examples

### Standard Python MCP Server in WSL
```json
{
  "mcpServers": {
    "my_server": {
      "command": "wsl.exe",
      "args": [
        "--cd", "/home/username/project",
        "--exec", "/home/username/project/.venv/bin/python",
        "-m", "my_server.main"
      ],
      "env": {
        "PYTHONPATH": "src"
      }
    }
  }
}
```

### Node.js MCP Server in WSL
```json
{
  "mcpServers": {
    "my_node_server": {
      "command": "wsl.exe",
      "args": [
        "--cd", "/home/username/project",
        "--exec", "node",
        "dist/index.js"
      ]
    }
  }
}
```

---

## 🚀 Testing Your Fix

### 1. Restart Cursor
After updating the configuration:
1. Save `.cursor/mcp.json`
2. Completely close Cursor
3. Reopen Cursor
4. Check if your MCP tools are now available

### 2. Verify Tools Available
Look for your MCP server tools in:
- Cursor's command palette
- MCP tool suggestions
- Tool availability indicators

### 3. Test Tool Execution
Try executing one of your MCP tools to confirm full functionality.

---

## 🐛 Common Issues and Fixes

### Issue: "command not found: wsl.exe"
**Solution**: Use `wsl` instead of `wsl.exe`:
```json
"command": "wsl"
```

### Issue: Path not found errors
**Solution**: Use absolute paths for all WSL paths:
```json
"args": ["--cd", "/home/username/full/path/to/project"]
```

### Issue: Virtual environment not activated
**Solution**: Use full path to Python in virtual environment:
```json
"/home/username/project/.venv/bin/python"
```

### Issue: Environment variables not set
**Solution**: Add all required environment variables to the `env` section:
```json
"env": {
  "PYTHONPATH": "src",
  "PATH": "/home/username/project/.venv/bin:$PATH"
}
```

### Issue: Permission denied
**Solution**: Ensure your bridge script is executable:
```bash
chmod +x your_bridge_script.sh
```

---

## 📋 Checklist for WSL MCP Setup

- [ ] MCP server works when tested directly in WSL
- [ ] Using `wsl.exe` or `wsl` as command
- [ ] Using absolute paths for all WSL directories
- [ ] All required environment variables set
- [ ] Virtual environment path is correct
- [ ] Bridge script is executable (if using)
- [ ] Cursor completely restarted after configuration changes
- [ ] No conflicting MCP server processes running

---

## 🔍 Advanced Debugging

### Enable Detailed Logging
Add logging to your bridge script:
```bash
#!/bin/bash
echo "Starting MCP server at $(date)" >> /tmp/mcp_debug.log
echo "Current directory: $(pwd)" >> /tmp/mcp_debug.log
echo "Python path: $PYTHONPATH" >> /tmp/mcp_debug.log

# Your server startup code here
```

### Monitor Process Creation
Watch for process creation in WSL:
```bash
# In WSL terminal
ps aux | grep python | grep mcp
```

### Check Port Usage
Verify no port conflicts:
```bash
netstat -tlnp | grep :your_port
```

---

## 💡 Best Practices

1. **Use Absolute Paths**: Always use full WSL paths in configuration
2. **Test Incrementally**: Test server functionality before integration
3. **Environment Isolation**: Use virtual environments for Python servers
4. **Logging**: Add comprehensive logging for debugging
5. **Documentation**: Document your specific configuration for team members

---

## 📚 Related Resources

- [MCP Protocol Documentation](https://spec.modelcontextprotocol.io/)
- [Cursor MCP Integration Guide](https://cursor.sh/mcp)
- [WSL Documentation](https://docs.microsoft.com/en-us/windows/wsl/)
- [FastMCP Documentation](https://fastmcp.com/)

---

## 🤝 Contributing

If you encounter additional WSL MCP issues or have solutions, please contribute to this guide by documenting:
- The specific error message
- Your environment details
- The working solution
- Any additional configuration required

---

*Last updated: January 2025*
*Tested with: Cursor, WSL2 Ubuntu, Python 3.12.3* 