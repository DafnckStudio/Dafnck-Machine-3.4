# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Agentic Project with MCP Task Management

This is an advanced agentic project built around the `dhafnck_mcp` server framework, featuring Model Context Protocol (MCP) integration and sophisticated task management capabilities.

## Core Architecture

The project follows Domain-Driven Design (DDD) principles with these key components:

- **Main MCP Server**: `dhafnck_mcp_main/` - Advanced MCP server framework with integrated task management
- **Task Management System**: Built on DDD architecture with domain, application, infrastructure, and interface layers
- **Multi-Agent Orchestration**: Tools for managing teams of AI agents with automatic role switching
- **Cursor Rules System**: Comprehensive AI context management in `.cursor/rules/`

## Essential Commands

### Development Environment Setup
```bash
# Navigate to main project
cd dhafnck_mcp_main

# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate

# Install development dependencies
uv sync --dev
```

### Testing
```bash
# Run full test suite
pytest

# Run with coverage
pytest --cov=src/fastmcp

# Run specific test categories
pytest -m unit          # Unit tests
pytest -m interface     # Interface tests
pytest -m integration   # Integration tests
```

### Code Quality
```bash
# Lint code
ruff check src/

# Format code
ruff format src/

# Type checking
pyright

# Run pre-commit hooks
pre-commit run --all-files
```

### MCP Server Operations
```bash
# Start MCP server
dhafnck_mcp serve

# Debug MCP server
python src/debug_mcp_server.py

# Test MCP connection
timeout 10 python src/debug_mcp_server.py
```

## Project Configuration

### Path Management
- **ROOT_PATH**: `/home/daihungpham/agentic-project`
- **USE_ABSOLUTE_PATH_FROM_ROOT_PROJECT**: ON
- Always use absolute paths when creating/updating files

### MCP Integration Priority
- **ALWAYS USE MCP TOOLS** when available for task operations
- Primary MCP server: `dhafnck_mcp` (required for all task management)
- Never bypass MCP by accessing JSON files directly
- Use `manage_task`, `manage_project`, `manage_agent` tools through MCP protocol

### Task Management Rules
- **Task Data Location**: `.cursor/rules/tasks/tasks.json`
- **MANDATORY**: Use MCP `dhafnck_mcp` server for ALL task operations
- **Workflow**: Follow `.cursor/rules/02_AI-DOCS/TaskManagement/` documentation
- **Context Sync**: Auto-generated rules in `.cursor/rules/auto_rule.mdc` provide task-specific context

### Agent System
- **Configurations**: `.cursor/rules/agents/` and `dhafnck_mcp_main/yaml-lib/`
- **Auto Role Switching**: Triggered by task assignees with "@" prefix (e.g., `@coding_agent`)
- **Documentation**: `.cursor/rules/02_AI-DOCS/MultiAgentOrchestration/`
- **Agent Calling**: Use `call_agent` MCP tool to load specialized configurations

## Key Development Practices

### File Operations
- Always read `.cursor/rules/main_objectif.mdc` first for project context
- Use sequential-thinking MCP for complex requests
- Fix root causes, not symptoms
- Request permission before creating new files at root level
- Force quit terminal commands running longer than 10 seconds

### MCP Server Development
The `dhafnck_mcp` server is built using FastMCP framework with:

- **Domain Layer**: Business logic and entities (`dhafnck_mcp_main/src/fastmcp/task_management/domain/`)
- **Application Layer**: Use cases and services (`dhafnck_mcp_main/src/fastmcp/task_management/application/`)
- **Infrastructure Layer**: Repositories and external services (`dhafnck_mcp_main/src/fastmcp/task_management/infrastructure/`)
- **Interface Layer**: MCP tools and API endpoints (`dhafnck_mcp_main/src/fastmcp/task_management/interface/`)

### Testing Strategy
- Comprehensive test suite with 77% coverage
- Test categories: unit, interface, integration, architecture, business_rules
- Virtual environment required: `dhafnck_mcp_main/.venv`
- Timeout settings: 3 seconds default, force quit long-running commands

## MCP Tools Available

Core task management tools accessible via MCP protocol:
- `mcp__task_management__manage_project` - Project lifecycle management
- `mcp__task_management__manage_task` - Task CRUD operations
- `mcp__task_management__manage_subtask` - Hierarchical task management
- `mcp__task_management__manage_agent` - Agent registration and coordination
- `mcp__task_management__call_agent` - Agent configuration retrieval
- `mcp__task_management__validate_tasks_json` - Task data validation
- `mcp__task_management__regenerate_auto_rule` - Context rule generation
- `mcp__sequential-thinking__sequentialthinking` - Enhanced reasoning

## Important Files and Directories

### Configuration Files
- `.cursor/rules/main_objectif.mdc` - Project objectives and context
- `.cursor/rules/auto_rule.mdc` - Auto-generated AI context rules
- `.cursor/rules/migration_plan.md` - Current migration plan
- `.claude/settings.local.json` - Claude Code permissions and settings

### Documentation
- `dhafnck_mcp_main/README.md` - MCP server framework documentation
- `.cursor/rules/02_AI-DOCS/` - Comprehensive system documentation
- `.cursor/rules/agents/` - Agent configuration documentation

### Core Implementation
- `dhafnck_mcp_main/src/fastmcp/task_management/` - Main task management implementation
- `dhafnck_mcp_main/tests/` - Test suite
- `dhafnck_mcp_main/yaml-lib/` - Agent YAML configurations

The project emphasizes clean architecture, comprehensive testing, and seamless integration between AI agents and the MCP protocol for advanced task orchestration.