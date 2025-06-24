# Claude Code Project Configuration

You are the AI used within the AI editor Cursor, so you can view, edit, create, and run files within the project directory. If you are asked to identify the cause of a bug, fix a bug, edit a file, or create a file, please execute the following function. Please do not ask me (human) to give you a file or ask you to create a file, but you (AI) can do it by executing the following functions. If an error occurs and you are unable to execute the function, please consult with us.

edit_file: Edit an existing file, create a new file
read_file: Read the contents of a file
grep_search: Search in the codebase based on a specific creator
list_dir: Get a list of files and folders in a specific directory”

Please edit the file in small chunks

ALWAYS use sequential-thinking mcp for analyze complex request or tasks, then use task
ALWAYS read `.cursor/rules/main_objectif.mdc` first to understand project context
Fix root causes, not symptoms
Detailed summaries without missing important details
No root directory file creation without permission
ALWAYS ask before creating new files
Respect project structure unless changes requested
Monitor for requests that would exceed Pro plan token limits
If a request would require paid usage beyond Pro limits, I must immediately terminate the response and inform you to start a new chat if you want to proceed with paid usage


CONTINUE_AUTOMATIC : ON
if CONTINUE_AUTOMATIC = OFF, terminate chat if task is completed, else continue same task

USE_ABSOLUTE_PATH_FROM_ROOT_PROJECT = ON
If USE_ABSOLUTE_PATH_FROM_ROOT_PROJECT is set to ON, you must use the absolute path from the ROOT_PATH when creating or updating files to avoid path issues when working with different projects in the same folder.

ROOT_PATH on WSL Ubuntu: /home/<username>/agentic-project

username : daihungpham

PLAN_ACTUAL : @migration_plan.md


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
- **MANDATORY: Use MCP dhafnck_mcp server for ALL task operations**
- Use `manage_task` tool with MCP protocol - never direct database access
- Task data located at: `.cursor/rules/tasks/tasks.json`
- Follow workflow in: `.cursor/rules/02_AI-DOCS/TaskManagement/dhafnck_mcp_workflow.mdc`

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
- `dhafnck_mcp` - Custom task management server (REQUIRED for all task operations)
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