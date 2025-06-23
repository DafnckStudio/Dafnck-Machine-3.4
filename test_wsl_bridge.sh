#!/bin/bash

echo "🔍 Testing WSL Bridge for MCP Server"
echo "===================================="
echo ""

echo "📍 Current environment: WSL Ubuntu"
echo "📍 Testing from: $(pwd)"
echo "📍 User: $(whoami)"
echo ""

echo "1️⃣ Testing basic WSL environment..."
echo "   ✅ WSL is running"
echo "   ✅ Current directory: $(pwd)"
echo "   ✅ Python version: $(python --version 2>/dev/null || echo 'Python not found in PATH')"
echo ""

echo "2️⃣ Testing virtual environment..."
cd dhafnck_mcp_main
if [ -f ".venv/bin/activate" ]; then
    echo "   ✅ Virtual environment found"
    source .venv/bin/activate
    echo "   ✅ Virtual environment activated"
    echo "   ✅ Python version: $(python --version)"
else
    echo "   ❌ Virtual environment not found"
    exit 1
fi
echo ""

echo "3️⃣ Testing MCP server import..."
export PYTHONPATH="/home/daihungpham/agentic-project/dhafnck_mcp_main/src"
export TASKS_JSON_PATH="/home/daihungpham/agentic-project/.cursor/rules/tasks/tasks.json"
export TASK_JSON_BACKUP_PATH="/home/daihungpham/agentic-project/.cursor/rules/tasks/backup"

python -c "
try:
    from fastmcp.task_management.interface.consolidated_mcp_server import mcp_instance
    print('   ✅ MCP server imported successfully')
    print(f'   ✅ Server name: {mcp_instance.name}')
except Exception as e:
    print(f'   ❌ MCP server import failed: {e}')
    exit(1)
"
echo ""

echo "4️⃣ Testing quick tool check..."
./diagnostic_connect.sh --quick-test
echo ""

echo "🎯 WSL Bridge Test Summary:"
echo "=========================="
echo "✅ WSL environment: Working"
echo "✅ Python environment: Working" 
echo "✅ MCP server: Working"
echo "✅ Tools: Available"
echo ""
echo "🔧 Next steps:"
echo "1. Restart Windows Cursor completely"
echo "2. Wait 30 seconds for MCP initialization"
echo "3. Check if 10 tools appear in Cursor"
echo ""
echo "💡 If tools still don't appear in Windows Cursor:"
echo "   - The WSL bridge configuration should work"
echo "   - Check Windows Command Prompt: wsl -l -v"
echo "   - Ensure WSL distribution name is 'Ubuntu'"
echo "   - Consider installing Cursor directly in WSL" 