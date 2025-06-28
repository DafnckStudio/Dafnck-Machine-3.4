#!/bin/bash

# MCP Inspector Launcher for DhafnckMCP Server
# This script starts the MCP inspector with the correct configuration

echo "🚀 Starting MCP Inspector for DhafnckMCP Server..."
echo "📍 Working directory: $(pwd)"

# Check if we're in the right directory
if [[ ! -d ".venv" ]]; then
    echo "❌ Error: .venv directory not found. Please run this script from dhafnck_mcp_main directory"
    exit 1
fi

# Check if virtual environment exists
if [[ ! -f ".venv/bin/python" ]]; then
    echo "❌ Error: Virtual environment not found. Please create it first with 'python -m venv .venv'"
    exit 1
fi

# Set environment variables for better debugging
export PYTHONPATH="dhafnck_mcp_main/src"
export TASKS_JSON_PATH=".cursor/rules/tasks/tasks.json"
export PROJECTS_FILE_PATH=".cursor/rules/brain/projects.json"
export CURSOR_AGENT_DIR_PATH="dhafnck_mcp_main/yaml-lib"

echo "✅ Environment variables set:"
echo "   PYTHONPATH: $PYTHONPATH"
echo "   TASKS_JSON_PATH: $TASKS_JSON_PATH"
echo "   PROJECTS_FILE_PATH: $PROJECTS_FILE_PATH"
echo "   CURSOR_AGENT_DIR_PATH: $CURSOR_AGENT_DIR_PATH"

echo ""
echo "🔧 Starting MCP Inspector..."
echo "   Server: fastmcp.server.mcp_entry_point"
echo "   Python: $(pwd)/.venv/bin/python"

echo ""
echo "📋 Once started, you'll see:"
echo "   - Proxy server on 127.0.0.1:6277"
echo "   - Inspector URL: http://localhost:6274"
echo "   - Authentication token for secure access"

echo ""
echo "🎯 Quick Test Tools:"
echo "   - health_check: Verify server status"
echo "   - get_server_capabilities: See all available features"
echo "   - create_task: Test task management"
echo "   - create_project: Test project management"

echo ""
echo "Press Ctrl+C to stop the inspector"
echo "=========================================="

# Start the MCP inspector with the correct command
npx @modelcontextprotocol/inspector "$(pwd)/.venv/bin/python" -m fastmcp.server.mcp_entry_point 