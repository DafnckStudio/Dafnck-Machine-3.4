# Claude Code Project Configuration

## Project Overview
This is an agentic project with task management capabilities using MCP (Model Context Protocol) servers.

## Key Directories
- `dhafnck_mcp_main/` - Main MCP task management implementation
- `.cursor/rules/` - Cursor-specific rules and configurations
- `.cursor/rules/tasks/` - Task management data

## Important Rules

### MCP Protocol Priority
- **ALWAYS USE MCP TOOLS WHEN AVAILABLE**
- Never create CLI scripts or direct API calls when MCP tools exist
- Use proper MCP tool calls through the protocol interface
- Follow MCP workflow patterns defined in documentation

### Path Management
- **USE_ABSOLUTE_PATH_FROM_ROOT_PROJECT = ON**
- Root path: `/home/daihungpham/agentic-project`
- Always use absolute paths when creating/updating files

### Task Management
- **MANDATORY: Use MCP task_management server for ALL task operations**
- Use `manage_task` tool with MCP protocol - never direct database access
- Task data located at: `.cursor/rules/tasks/tasks.json`
- Follow workflow in: `.cursor/rules/02_AI-DOCS/TaskManagement/task_management_workflow.mdc`

### Testing
- Virtual environment: `dhafnck_mcp_main/.venv`
- All tests located in: `dhafnck_mcp_main/tests/`
- Run tests with: `cd dhafnck_mcp_main && uv sync && python -m pytest`

### Agent System
- Agent configurations: `.cursor/rules/agents/`
- Multi-agent orchestration docs: `.cursor/rules/02_AI-DOCS/MultiAgentOrchestration/`
- Automatic role switching based on task assignees

### Commands
- Force quit commands running longer than 10 seconds
- Always try exit command after terminal operations

## Referenced Files
- Main objectives: `.cursor/rules/main_objectif.mdc`
- Migration plan: `.cursor/rules/migration_plan.md`
- Auto-generated rules: `.cursor/rules/auto_rule.mdc`

## MCP Servers
- `task_management` - Custom task management server (REQUIRED for all task operations)
- `sequential-thinking` - Enhanced reasoning
- `github` - GitHub integration

## MCP Usage Guidelines
- **FIRST PRIORITY**: Check if MCP tools are available for the task
- **USE MCP TOOLS**: Instead of writing custom scripts or direct API calls
- **TOOL EXAMPLES**:
  - Task management: Use `manage_task`, `manage_project`, `manage_agent` tools
  - Never bypass MCP by accessing JSON files directly
  - Always follow the MCP workflow patterns
- **DEBUGGING**: If MCP tools fail, fix the MCP server rather than bypassing it