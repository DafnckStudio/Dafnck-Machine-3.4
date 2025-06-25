# WSL MCP Server Quick Fix Guide

## 🚨 Problem
MCP server works in WSL but Cursor can't connect: "Connection Error - Check if your MCP server is running"

## ⚡ Quick Solution

Replace your `.cursor/mcp.json` MCP server configuration with:

```json
{
  "mcpServers": {
    "your_server_name": {
      "command": "wsl.exe",
      "args": [
        "--cd", "/home/username/your-project-path",
        "--exec", "/home/username/your-project-path/.venv/bin/python",
        "-m", "your.module.entry_point"
      ],
      "env": {
        "PYTHONPATH": "src",
        "YOUR_ENV_VARS": "values"
      }
    }
  }
}
```

## 🔧 For dhafnck_mcp specifically:

```json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "wsl.exe",
      "args": [
        "--cd", "/home/daihungpham/agentic-project",
        "--exec", "/home/daihungpham/agentic-project/dhafnck_mcp_main/.venv/bin/python",
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

## ✅ Steps:
1. Update `.cursor/mcp.json` with the configuration above
2. Replace paths with your actual paths
3. Save the file
4. **Completely close and reopen Cursor**
5. Check if your MCP tools are now available

## 🔍 Why This Works:
- `wsl.exe` allows Cursor (Windows) to properly execute commands in WSL
- `--cd` sets the working directory in WSL
- `--exec` runs the Python command with full path to virtual environment
- Environment variables are properly passed through

## 📋 Checklist:
- [ ] Used `wsl.exe` as command
- [ ] Used absolute WSL paths (starting with `/home/`)
- [ ] Included all required environment variables
- [ ] Restarted Cursor completely
- [ ] Verified MCP tools are now available

For detailed troubleshooting, see: [WSL_MCP_TROUBLESHOOTING_GUIDE.md](./WSL_MCP_TROUBLESHOOTING_GUIDE.md) 