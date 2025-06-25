#!/bin/bash

echo "🔍 MCP Connection Diagnostic Tool"
echo "=================================="
echo ""

# Check if we're in the right directory
echo "📍 Current directory: $(pwd)"
echo "📍 Expected directory: /home/daihungpham/agentic-project"
echo ""

# Check if the MCP configuration file exists
echo "🔧 Checking MCP configuration..."
if [[ -f ".cursor/mcp.json" ]]; then
    echo "✅ .cursor/mcp.json exists"
    echo "📋 dhafnck_mcp configuration:"
    jq '.mcpServers.dhafnck_mcp' .cursor/mcp.json 2>/dev/null || echo "❌ Error reading JSON"
else
    echo "❌ .cursor/mcp.json not found"
fi
echo ""

# Check if the virtual environment exists
echo "🐍 Checking Python virtual environment..."
if [[ -f "dhafnck_mcp_main/.venv/bin/python" ]]; then
    echo "✅ Virtual environment exists"
    echo "📋 Python version: $(dhafnck_mcp_main/.venv/bin/python --version)"
else
    echo "❌ Virtual environment not found at dhafnck_mcp_main/.venv/bin/python"
fi
echo ""

# Test if the MCP server module can be imported
echo "📦 Testing MCP server module..."
cd /home/daihungpham/agentic-project
export PYTHONPATH="dhafnck_mcp_main/src"
export TASKS_JSON_PATH=".cursor/rules/tasks/tasks.json"
export PROJECT_ROOT_PATH="."

if dhafnck_mcp_main/.venv/bin/python -c "
import sys
sys.path.insert(0, 'dhafnck_mcp_main/src')
from fastmcp.server.mcp_entry_point import create_dhafnck_mcp_server
server = create_dhafnck_mcp_server()
print('✅ MCP server can be created successfully')
print(f'✅ Server name: {server.name}')
if hasattr(server, 'consolidated_tools') and server.consolidated_tools:
    config = server.consolidated_tools._config
    enabled_tools = config.get_enabled_tools()
    enabled_count = sum(1 for enabled in enabled_tools.values() if enabled)
    print(f'✅ Tools enabled: {enabled_count}/10')
else:
    print('❌ No consolidated tools found')
" 2>/dev/null; then
    echo "✅ MCP server module test passed"
else
    echo "❌ MCP server module test failed"
    echo "🔍 Trying with debug output..."
    dhafnck_mcp_main/.venv/bin/python -c "
import sys
sys.path.insert(0, 'dhafnck_mcp_main/src')
from fastmcp.server.mcp_entry_point import create_dhafnck_mcp_server
server = create_dhafnck_mcp_server()
print('Server created')
" 2>&1 | head -10
fi
echo ""

# Check for running MCP processes
echo "🔍 Checking for running MCP processes..."
RUNNING_PROCESSES=$(ps aux | grep -E "(python.*fastmcp|mcp.*python)" | grep -v grep | wc -l)
if [[ $RUNNING_PROCESSES -gt 0 ]]; then
    echo "⚠️  Found $RUNNING_PROCESSES running MCP processes:"
    ps aux | grep -E "(python.*fastmcp|mcp.*python)" | grep -v grep | awk '{print "   - PID " $2 ": " $11 " " $12 " " $13}'
    echo "💡 You may need to kill these processes: pkill -f 'fastmcp.server.mcp_entry_point'"
else
    echo "✅ No conflicting MCP processes running"
fi
echo ""

# Check required directories and files
echo "📁 Checking required directories and files..."
REQUIRED_PATHS=(
    ".cursor/rules/tasks/tasks.json"
    ".cursor/rules/brain/projects.json"
    "dhafnck_mcp_main/yaml-lib"
    "dhafnck_mcp_main/src/fastmcp"
)

for path in "${REQUIRED_PATHS[@]}"; do
    if [[ -e "$path" ]]; then
        echo "✅ $path exists"
    else
        echo "❌ $path missing"
        if [[ "$path" == ".cursor/rules/tasks/tasks.json" ]]; then
            echo "   💡 Creating missing tasks.json..."
            mkdir -p ".cursor/rules/tasks"
            echo '{"tasks": [], "metadata": {"version": "1.0", "created": "'$(date -Iseconds)'"}}' > "$path"
            echo "   ✅ Created $path"
        fi
    fi
done
echo ""

echo "🎯 Next Steps:"
echo "1. If all checks pass, restart Cursor completely (close and reopen)"
echo "2. After restart, check if dhafnck_mcp tools appear in the MCP tools list"
echo "3. If still not working, try: Ctrl+Shift+P → 'Developer: Reload Window'"
echo "4. Check Cursor's developer console for MCP connection errors"
echo ""
echo "🔗 Expected tools after connection:"
echo "   - health_check"
echo "   - get_server_capabilities"
echo "   - manage_task"
echo "   - manage_project"
echo "   - manage_agent"
echo "   - call_agent"
echo "   - update_auto_rule"
echo "   - validate_rules"
echo "   - manage_cursor_rules"
echo "   - validate_tasks_json" 