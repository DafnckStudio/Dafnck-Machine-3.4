#!/bin/bash

# WSL MCP Bridge Script
# This script helps Cursor (running on Windows) connect to the MCP server in WSL

echo "🔗 WSL MCP Bridge starting..." >&2
echo "📍 Working directory: $(pwd)" >&2
echo "📍 Python path: /home/daihungpham/agentic-project/dhafnck_mcp_main/.venv/bin/python" >&2

# Set environment variables
export PYTHONPATH="/home/daihungpham/agentic-project/dhafnck_mcp_main/src"
export TASKS_JSON_PATH="/home/daihungpham/agentic-project/.cursor/rules/tasks/tasks.json"
export PROJECT_ROOT_PATH="/home/daihungpham/agentic-project"
export PYTHONUNBUFFERED=1

# Change to the correct directory
cd /home/daihungpham/agentic-project

# Start the MCP server
echo "🚀 Starting dhafnck_mcp server..." >&2
exec /home/daihungpham/agentic-project/dhafnck_mcp_main/.venv/bin/python -m fastmcp.server.mcp_entry_point 