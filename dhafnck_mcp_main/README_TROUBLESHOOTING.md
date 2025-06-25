# DhafnckMCP Troubleshooting Documentation

This directory contains comprehensive troubleshooting guides for the DhafnckMCP server, especially for WSL environments.

## 📚 Available Guides

### 🚨 WSL Connection Issues
If you're using Cursor on Windows with WSL and experiencing MCP connection problems:

1. **[WSL_MCP_QUICK_FIX.md](./WSL_MCP_QUICK_FIX.md)** - ⚡ **START HERE**
   - Immediate solution for WSL connection problems
   - Quick configuration fix
   - Step-by-step instructions

2. **[WSL_MCP_TROUBLESHOOTING_GUIDE.md](./WSL_MCP_TROUBLESHOOTING_GUIDE.md)** - 🔍 **Detailed Analysis**
   - Comprehensive troubleshooting guide
   - Root cause analysis
   - Multiple solution approaches
   - Advanced debugging techniques

### 🔧 General MCP Server Issues

3. **[MCP_INSPECTOR_GUIDE.md](./MCP_INSPECTOR_GUIDE.md)** - 🛠️ **Testing & Debugging**
   - How to use MCP Inspector for testing
   - Available tools and their usage
   - Integration with Cursor IDE
   - General troubleshooting steps

4. **[cursor_debug_guide.md](./cursor_debug_guide.md)** - 📋 **Cursor-Specific Issues**
   - Cursor IDE specific debugging
   - Log analysis
   - Configuration validation

## 🎯 Quick Problem Identification

### Symptoms → Solution Guide

| Symptom | Likely Cause | Recommended Guide |
|---------|--------------|-------------------|
| "Connection Error - Check if your MCP server is running" | WSL integration issue | [WSL_MCP_QUICK_FIX.md](./WSL_MCP_QUICK_FIX.md) |
| `spawn /bin/sh ENOENT` in logs | WSL spawn error | [WSL_MCP_QUICK_FIX.md](./WSL_MCP_QUICK_FIX.md) |
| Server works in WSL but not in Cursor | WSL configuration | [WSL_MCP_TROUBLESHOOTING_GUIDE.md](./WSL_MCP_TROUBLESHOOTING_GUIDE.md) |
| 0 tools available from MCP server | Connection/configuration issue | [MCP_INSPECTOR_GUIDE.md](./MCP_INSPECTOR_GUIDE.md) |
| Module import errors | Environment/path issue | [MCP_INSPECTOR_GUIDE.md](./MCP_INSPECTOR_GUIDE.md) |
| Port conflicts or process issues | Server startup problem | [cursor_debug_guide.md](./cursor_debug_guide.md) |

## 🔄 Troubleshooting Workflow

1. **Identify Environment**: Are you using WSL with Cursor on Windows?
   - ✅ Yes → Start with [WSL_MCP_QUICK_FIX.md](./WSL_MCP_QUICK_FIX.md)
   - ❌ No → Go to step 2

2. **Test Server Directly**: Does your MCP server work when tested directly?
   - ✅ Yes → Connection issue, see [MCP_INSPECTOR_GUIDE.md](./MCP_INSPECTOR_GUIDE.md)
   - ❌ No → Server issue, check environment and dependencies

3. **Check Cursor Integration**: Are other MCP servers working in Cursor?
   - ✅ Yes → Configuration issue, see [WSL_MCP_TROUBLESHOOTING_GUIDE.md](./WSL_MCP_TROUBLESHOOTING_GUIDE.md)
   - ❌ No → Cursor MCP setup issue, see [cursor_debug_guide.md](./cursor_debug_guide.md)

## 🆘 Emergency Quick Fixes

### WSL Users (Most Common Issue)
Replace your `.cursor/mcp.json` configuration:
```json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "wsl.exe",
      "args": [
        "--cd", "/home/yourusername/agentic-project",
        "--exec", "/home/yourusername/agentic-project/dhafnck_mcp_main/.venv/bin/python",
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

### Server Test Command
```bash
cd /home/yourusername/agentic-project/dhafnck_mcp_main
source .venv/bin/activate
python -m fastmcp.server.mcp_entry_point
```

## 📞 Getting Help

If these guides don't solve your issue:

1. **Check the specific guide** for your environment and symptoms
2. **Follow the diagnostic steps** in the detailed troubleshooting guide
3. **Collect debug information** using the provided scripts
4. **Document your specific error** messages and environment details

## 🔄 Contributing

Found a new issue or solution? Please update the relevant guide:
- Add new symptoms to the identification table
- Document your specific environment details
- Include the working solution
- Update the workflow if needed

---

*Last updated: January 2025*
*Environment: WSL2 Ubuntu, Cursor IDE, Python 3.12.3* 