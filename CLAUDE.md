# Claude Code Project Configuration

## Project Overview
This is an agentic project with task management capabilities using MCP (Model Context Protocol) servers.

## Key Directories
- `dhafnck_mcp_main/` - Main MCP task management implementation
- `.cursor/rules/` - Cursor-specific rules and configurations
- `.cursor/rules/tasks/` - Task management data

## Important Rules

### Path Management
- **USE_ABSOLUTE_PATH_FROM_ROOT_PROJECT = ON**
- Root path: `/home/daihungpham/agentic-project`
- Always use absolute paths when creating/updating files

### Task Management
- Use MCP task_management server for all task operations
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
- `task_management` - Custom task management server
- `sequential-thinking` - Enhanced reasoning
- `github` - GitHub integration