# Cursor MCP Connection Debug Guide

## 🔍 Method 1: Cursor Developer Console (Best for Real-time Errors)

### Steps:
1. **Open Developer Console**:
   - Press `Ctrl + Shift + I` (or `Cmd + Shift + I` on Mac)
   - Or: `Ctrl + Shift + P` → "Developer: Toggle Developer Tools"

2. **Go to Console Tab**:
   - Look for red error messages
   - Search for "mcp", "dhafnck", or "server" in the console

3. **Look for MCP-specific errors**:
   ```
   MCP server 'dhafnck_mcp' failed to start
   Error spawning process: ...
   Connection timeout: ...
   Protocol error: ...
   ```

4. **Check Network Tab**:
   - Look for failed connections to localhost ports
   - Check for WebSocket connection failures

## 🔍 Method 2: Cursor Command Palette Diagnostics

### Steps:
1. **Open Command Palette**: `Ctrl + Shift + P`
2. **Type**: "MCP" or "Model Context Protocol"
3. **Look for**:
   - "MCP: Show Server Status"
   - "MCP: Restart Servers"
   - "MCP: Show Logs"
   - "Developer: Show Running Extensions"

## 🔍 Method 3: Cursor Settings/Preferences

### Steps:
1. **Open Settings**: `Ctrl + ,`
2. **Search for**: "MCP" or "Model Context Protocol"
3. **Check**:
   - Server configuration
   - Connection status
   - Debug settings

## 🔍 Method 4: Manual MCP Server Testing

### Test with MCP Inspector:
```bash
# Kill any running processes first
pkill -f "fastmcp.server.mcp_entry_point"

# Start with inspector for detailed logs
cd /home/daihungpham/agentic-project/dhafnck_mcp_main
npx @modelcontextprotocol/inspector /home/daihungpham/agentic-project/dhafnck_mcp_main/.venv/bin/python -m fastmcp.server.mcp_entry_point
```

### Direct Server Test:
```bash
# Test the exact command Cursor uses
cd /home/daihungpham/agentic-project
PYTHONPATH="dhafnck_mcp_main/src" \
TASKS_JSON_PATH=".cursor/rules/tasks/tasks.json" \
PROJECT_ROOT_PATH="." \
/home/daihungpham/agentic-project/dhafnck_mcp_main/.venv/bin/python -m fastmcp.server.mcp_entry_point
```

## 🔍 Method 5: Enable Verbose Logging

### Update .cursor/mcp.json for more logs:
```json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "/home/daihungpham/agentic-project/dhafnck_mcp_main/.venv/bin/python",
      "args": ["-m", "fastmcp.server.mcp_entry_point"],
      "cwd": "/home/daihungpham/agentic-project",
      "env": {
        "PYTHONPATH": "dhafnck_mcp_main/src",
        "TASKS_JSON_PATH": ".cursor/rules/tasks/tasks.json",
        "PROJECT_ROOT_PATH": ".",
        "PYTHONUNBUFFERED": "1",
        "MCP_DEBUG": "1"
      },
      "transport": "stdio",
      "debug": true
    }
  }
}
```

## 🔍 Method 6: Check Cursor Log Files

### Cursor log locations:
- **Linux**: `~/.config/cursor/logs/`
- **Windows**: `%APPDATA%/cursor/logs/`
- **macOS**: `~/Library/Logs/cursor/`

### Commands to check logs:
```bash
# Check recent Cursor logs
ls -la ~/.config/cursor/logs/
tail -f ~/.config/cursor/logs/main.log
grep -i "mcp\|dhafnck" ~/.config/cursor/logs/*.log
```

## 🔍 Method 7: Process Monitoring

### Check if Cursor is trying to start the server:
```bash
# Monitor process creation
watch -n 1 'ps aux | grep -E "(python.*fastmcp|dhafnck)" | grep -v grep'

# Check system logs
journalctl -f | grep -i cursor
```

## 🎯 Common Error Patterns to Look For:

### 1. **Path Issues**:
```
Error: ENOENT: no such file or directory
spawn dhafnck_mcp_main/.venv/bin/python ENOENT
```

### 2. **Permission Issues**:
```
Error: EACCES: permission denied
```

### 3. **Python/Module Issues**:
```
ModuleNotFoundError: No module named 'fastmcp'
ImportError: cannot import name
```

### 4. **Port/Connection Issues**:
```
Error: EADDRINUSE: address already in use
Connection refused
Timeout waiting for server
```

### 5. **Protocol Issues**:
```
Invalid MCP response
Protocol version mismatch
JSON-RPC error
```

## 🛠️ Quick Debug Script

Run this to get comprehensive debug info:
```bash
cd /home/daihungpham/agentic-project
./dhafnck_mcp_main/diagnose_mcp_connection.sh
```

## 🎯 Next Steps Based on Error Type:

1. **If you see path errors**: Use absolute paths in mcp.json
2. **If you see module errors**: Check PYTHONPATH and virtual environment
3. **If you see permission errors**: Check file permissions and ownership
4. **If you see port errors**: Kill conflicting processes
5. **If you see no errors but no connection**: Check Cursor's MCP client logs

## 📝 Debug Checklist:

- [ ] Check Cursor Developer Console for errors
- [ ] Try MCP Inspector for server testing
- [ ] Check Cursor log files
- [ ] Monitor process creation
- [ ] Test server manually with exact Cursor command
- [ ] Check for conflicting processes
- [ ] Verify all file paths and permissions
- [ ] Test with minimal server configuration 