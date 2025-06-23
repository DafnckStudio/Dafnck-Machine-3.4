#!/bin/bash
echo "🔄 Restarting dhafnck_mcp server..."

# Kill any existing processes
pkill -f "mcp_server.py" 2>/dev/null || true
pkill -f "dhafnck_mcp" 2>/dev/null || true

# Wait a moment
sleep 2

# Set environment
cd /home/daihungpham/agentic-project
export PYTHONPATH=/home/daihungpham/agentic-project/dhafnck_mcp_main/src

# Activate virtual environment and start server
source dhafnck_mcp_main/.venv/bin/activate

echo "✅ Starting MCP server with 10 tools..."
python dhafnck_mcp_main/src/fastmcp/task_management/interface/consolidated_mcp_server.py 