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
project_id: dhafnck_mcp_main
task_tree_id: <name-branche-actual> (v2.1---multiple-projects-support)
projet_path_root: /home/daihungpham/agentic-project/dhafnck_mcp_main

# Main objectif : buid mcp server dhafnck_mcp (dhafnck_mcp_main)

**Tip: Read the logic in cursor_agent to fix issues in dhafnck_mcp_main.

**See the full Multi-Agent Orchestration documentation:**
@.cursor/rules/02_AI-DOCS/MultiAgentOrchestration/README.mdc

MUST follow @task-management.mdc

## Command executes: 
- MUST do when use terminal commande: try exit commande 
- when commande is longer than 20 sec force quit for see result

run terminal commande →
    ├── force quit if run more than 20s
    └── see result

## Tools calls on chat need counter on background

## 📋 **IMPORTANT: CONTEXT SYNCHRONIZATION**
- **Trigger**: Every time `get_task` or `do_next` is called via MCP server
- **Target File**: `.cursor/rules/auto_rule.mdc`
- **Purpose**: Provides precise, task-specific context and rules for AI assistant
- **When get_task is called**: AI assistant should ALWAYS check this file (main_objectif.mdc) for updated context
- **Auto-generated rules**: The `.cursor/rules/auto_rule.mdc` file is automatically updated with task-specific context
- **Context precision**: This ensures the AI has the most precise and relevant context for the current task
- **Role alignment**: AI behavior automatically adapts to the assigned role and current phase

## 🔄 **AUTOMATIC AGENT ROLE SWITCHING**
- **Trigger**: Every time `get_task` or `do_next` is called via MCP server
- **Process**: System automatically extracts assignee from task and calls appropriate agent
- **Format**: All assignees use "@" prefix (e.g., `@coding_agent`, `@functional_tester_agent`)
- **Agent Call**: Automatically executes `call_agent(name_agent="agent_name")` (strips "@" prefix)
- **YAML Loading**: Loads specialized configuration from `cursor_agent/yaml-lib/[agent_name]/`
- **Role Switch**: AI adopts the appropriate expertise, behavior, and knowledge for the task
- **Primary Assignee**: Only the first assignee in the list triggers automatic switching
- **Documentation**: See @.cursor/rules/02_AI-DOCS/MultiAgentOrchestration/Agent_Auto_Switch_Workflow.mdc for complete details

### Ensures context files is relative with task and subtask
@contextmaster.mdc : ALWAYS trigger after complete task or subtask

## Use MCP Server dhafnck_mcp when possible 
MUST follow @dhafnck_mcp_Workflow.mdc

see @dhafnck_mcp_MCP_Server_Documentation.mdc for more details

- ALWAYS use the dhafnck_mcp MCP server for task operations
- Use dhafnck_mcp MCP to manage tasks
- ALWAYS use the MCP server first; NEVER access `.cursor/rules/tasks/tasks.json` directly unless the user requests it (AI does not have permission)

## 🎯 **AUTO_RULE.MDC GENERATION AUTOMATIC** 
don't edit this file by ai, it generate automatic on task management

## TEST MUST to activate virtual environment
cursor_agent/.venv

