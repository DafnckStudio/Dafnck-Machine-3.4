#!/bin/bash

# Script to run the DhafnckMCP server for testing with MCP Inspector
# This script sets up the proper environment and runs the server

# Set working directory to project root
cd /home/daihungpham/agentic-project

# Set environment variables
export PYTHONPATH="dhafnck_mcp_main/src"
export TASKS_JSON_PATH=".cursor/rules/tasks/tasks.json"
export TASK_JSON_BACKUP_PATH=".cursor/rules/tasks/backup"
export MCP_TOOL_CONFIG=".cursor/tool_config.json"
export AGENTS_OUTPUT_DIR=".cursor/rules/agents"
export AUTO_RULE_PATH=".cursor/rules/auto_rule.mdc"
export BRAIN_DIR_PATH=".cursor/rules/brain"
export PROJECTS_FILE_PATH=".cursor/rules/brain/projects.json"
export PROJECT_ROOT_PATH="."
export CURSOR_AGENT_DIR_PATH="dhafnck_mcp_main/yaml-lib"
export AGENT_YAML_LIB_PATH="dhafnck_mcp_main/yaml-lib"

# Run the MCP server
exec dhafnck_mcp_main/.venv/bin/python -m fastmcp.server.mcp_entry_point 