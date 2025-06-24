#!/usr/bin/env python3
"""
Cursor MCP Server for dhafnck_mcp - Full functionality with proven reliability.
Combines the minimal server structure with all features from consolidated_mcp_tools_v2.py
"""

import asyncio
import logging
import sys
import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add the src directory to Python path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import MCP server components
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Import our comprehensive tool implementations
from fastmcp.task_management.interface.consolidated_mcp_tools_v2 import ConsolidatedMCPToolsV2

# Create server instance
server = Server("dhafnck_mcp")

# Initialize tools implementation
tools_impl = None

def init_tools():
    """Initialize the tools implementation"""
    global tools_impl
    if tools_impl is None:
        try:
            tools_impl = ConsolidatedMCPToolsV2()
            logger.info("ConsolidatedMCPToolsV2 initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize tools: {e}")
            raise

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools - comprehensive set from consolidated_mcp_tools_v2"""
    return [
        # ═══════════════════════════════════════════════════════════════════
        # 🏗️ PROJECT MANAGEMENT TOOLS
        # ═══════════════════════════════════════════════════════════════════
        Tool(
            name="manage_project",
            description="🏗️ PROJECT ORCHESTRATION HUB - Complete multi-agent project lifecycle management",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "The operation to perform",
                        "enum": ["create", "get", "list", "create_tree", "get_tree_status", "orchestrate", "dashboard"]
                    },
                    "project_id": {"type": "string", "description": "Project identifier"},
                    "name": {"type": "string", "description": "Project name"},
                    "description": {"type": "string", "description": "Project description"},
                    "tree_id": {"type": "string", "description": "Task tree identifier"},
                    "tree_name": {"type": "string", "description": "Task tree name"},
                    "tree_description": {"type": "string", "description": "Task tree description"}
                },
                "required": ["action"]
            }
        ),
        
        # ═══════════════════════════════════════════════════════════════════
        # 📋 TASK MANAGEMENT TOOLS
        # ═══════════════════════════════════════════════════════════════════
        Tool(
            name="manage_task",
            description="📋 TASK MANAGEMENT HUB - Comprehensive task lifecycle management with 15+ actions",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "The task operation to perform",
                        "enum": ["create", "get", "update", "delete", "complete", "list", "search", "next", "add_dependency", "remove_dependency", "get_dependencies", "clear_dependencies", "get_blocking_tasks"]
                    },
                    "task_id": {"type": "string", "description": "Task identifier"},
                    "project_id": {"type": "string", "description": "Project identifier"},
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string", "description": "Task description"},
                    "status": {"type": "string", "description": "Task status"},
                    "priority": {"type": "string", "description": "Task priority"},
                    "details": {"type": "string", "description": "Task details"},
                    "estimated_effort": {"type": "string", "description": "Estimated effort"},
                    "assignees": {"type": "array", "items": {"type": "string"}, "description": "Task assignees"},
                    "labels": {"type": "array", "items": {"type": "string"}, "description": "Task labels"},
                    "due_date": {"type": "string", "description": "Due date"},
                    "dependency_data": {"type": "object", "description": "Dependency data"},
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Result limit"},
                    "force_full_generation": {"type": "boolean", "description": "Force full rule generation"}
                },
                "required": ["action"]
            }
        ),
        
        Tool(
            name="manage_subtask",
            description="📝 SUBTASK MANAGEMENT - Hierarchical subtask management with progress tracking",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string", 
                        "description": "Subtask action to perform",
                        "enum": ["add", "add_subtask", "complete", "update", "remove", "list", "list_subtasks"]
                    },
                    "task_id": {"type": "string", "description": "Parent task ID"},
                    "subtask_data": {"type": "object", "description": "Subtask data for operations"}
                },
                "required": ["action", "task_id"]
            }
        ),
        
        # ═══════════════════════════════════════════════════════════════════
        # 🤖 AGENT MANAGEMENT TOOLS
        # ═══════════════════════════════════════════════════════════════════
        Tool(
            name="manage_agent", 
            description="🤖 AGENT COORDINATION HUB - Multi-agent team management and intelligent assignment",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "The agent operation to perform",
                        "enum": ["register", "assign", "get", "list", "get_assignments", "unassign", "update", "unregister", "rebalance", "get_workload"]
                    },
                    "project_id": {"type": "string", "description": "Project identifier"},
                    "agent_id": {"type": "string", "description": "Agent identifier"},
                    "name": {"type": "string", "description": "Agent name"},
                    "call_agent": {"type": "string", "description": "Agent call reference"},
                    "tree_id": {"type": "string", "description": "Task tree identifier"}
                },
                "required": ["action"]
            }
        ),
        
        Tool(
            name="call_agent",
            description="🔍 AGENT INFORMATION - Retrieve agent configuration and capabilities from YAML files",
            inputSchema={
                "type": "object", 
                "properties": {
                    "name_agent": {"type": "string", "description": "Agent name to retrieve information for"}
                },
                "required": ["name_agent"]
            }
        ),
        
        # ═══════════════════════════════════════════════════════════════════
        # 🛠️ CURSOR INTEGRATION TOOLS
        # ═══════════════════════════════════════════════════════════════════
        Tool(
            name="update_auto_rule",
            description="🔧 AUTO RULE UPDATER - Direct update of AI assistant context rules",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "New content for auto_rule.mdc"},
                    "append": {"type": "boolean", "description": "Whether to append to existing content"}
                },
                "required": ["content"]
            }
        ),
        
        Tool(
            name="validate_rules",
            description="✅ RULE VALIDATOR - Comprehensive rule file quality analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "rule_type": {"type": "string", "description": "Type of rules to validate"},
                    "fix_issues": {"type": "boolean", "description": "Whether to fix found issues"}
                }
            }
        ),
        
        Tool(
            name="manage_cursor_rules",
            description="📋 CURSOR RULES MANAGER - Complete rule file system management",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "description": "Rule management action",
                        "enum": ["list", "get", "update", "backup", "restore"]
                    },
                    "rule_name": {"type": "string", "description": "Rule file name"},
                    "content": {"type": "string", "description": "Rule content"},
                    "backup_name": {"type": "string", "description": "Backup name"}
                },
                "required": ["action"]
            }
        ),
        
        Tool(
            name="regenerate_auto_rule",
            description="🔄 CONTEXT REGENERATOR - Smart context generation for AI assistant",
            inputSchema={
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID for context generation"},
                    "force_full": {"type": "boolean", "description": "Force full regeneration"}
                }
            }
        ),
        
        Tool(
            name="validate_tasks_json",
            description="🔍 TASK VALIDATOR - Tasks.json integrity validation",
            inputSchema={
                "type": "object",
                "properties": {
                    "fix_issues": {"type": "boolean", "description": "Whether to fix found issues"}
                }
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls - routes to appropriate implementation"""
    
    # Initialize tools if not already done
    if tools_impl is None:
        init_tools()
    
    try:
        logger.info(f"Tool called: {name} with args: {arguments}")
        
        # ═══════════════════════════════════════════════════════════════════
        # PROJECT MANAGEMENT TOOLS
        # ═══════════════════════════════════════════════════════════════════
        if name == "manage_project":
            result = await handle_manage_project(arguments)
            
        # ═══════════════════════════════════════════════════════════════════
        # TASK MANAGEMENT TOOLS
        # ═══════════════════════════════════════════════════════════════════
        elif name == "manage_task":
            result = await handle_manage_task(arguments)
            
        elif name == "manage_subtask":
            result = await handle_manage_subtask(arguments)
            
        # ═══════════════════════════════════════════════════════════════════
        # AGENT MANAGEMENT TOOLS
        # ═══════════════════════════════════════════════════════════════════
        elif name == "manage_agent":
            result = await handle_manage_agent(arguments)
            
        elif name == "call_agent":
            result = await handle_call_agent(arguments)
            
        # ═══════════════════════════════════════════════════════════════════
        # CURSOR INTEGRATION TOOLS
        # ═══════════════════════════════════════════════════════════════════
        elif name == "update_auto_rule":
            result = await handle_update_auto_rule(arguments)
            
        elif name == "validate_rules":
            result = await handle_validate_rules(arguments)
            
        elif name == "manage_cursor_rules":
            result = await handle_manage_cursor_rules(arguments)
            
        elif name == "regenerate_auto_rule":
            result = await handle_regenerate_auto_rule(arguments)
            
        elif name == "validate_tasks_json":
            result = await handle_validate_tasks_json(arguments)
            
        else:
            result = {"success": False, "error": f"Unknown tool: {name}"}
            
        # Convert result to string for TextContent
        result_text = json.dumps(result, indent=2) if isinstance(result, dict) else str(result)
        return [TextContent(type="text", text=result_text)]
        
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        error_msg = {"success": False, "error": f"Error executing {name}: {str(e)}"}
        return [TextContent(type="text", text=json.dumps(error_msg, indent=2))]

# ═══════════════════════════════════════════════════════════════════
# TOOL IMPLEMENTATION HANDLERS
# ═══════════════════════════════════════════════════════════════════

async def handle_manage_project(arguments: dict) -> dict:
    """Handle project management operations"""
    action = arguments.get("action")
    project_id = arguments.get("project_id")
    name = arguments.get("name")
    description = arguments.get("description", "")
    tree_id = arguments.get("tree_id")
    tree_name = arguments.get("tree_name")
    tree_description = arguments.get("tree_description", "")
    
    if action == "create":
        return tools_impl._multi_agent_tools.create_project(project_id, name, description)
    elif action == "get":
        return tools_impl._multi_agent_tools.get_project(project_id)
    elif action == "list":
        return tools_impl._multi_agent_tools.list_projects()
    elif action == "create_tree":
        return tools_impl._multi_agent_tools.create_task_tree(project_id, tree_id, tree_name, tree_description)
    elif action == "get_tree_status":
        return tools_impl._multi_agent_tools.get_task_tree_status(project_id, tree_id)
    elif action == "orchestrate":
        return tools_impl._multi_agent_tools.orchestrate_project(project_id)
    elif action == "dashboard":
        return tools_impl._multi_agent_tools.get_orchestration_dashboard(project_id)
    else:
        return {"success": False, "error": f"Unknown project action: {action}"}

async def handle_manage_task(arguments: dict) -> dict:
    """Handle task management operations"""
    # Extract all possible arguments
    action = arguments.get("action")
    task_id = arguments.get("task_id")
    project_id = arguments.get("project_id")
    title = arguments.get("title")
    description = arguments.get("description")
    status = arguments.get("status")
    priority = arguments.get("priority")
    details = arguments.get("details")
    estimated_effort = arguments.get("estimated_effort")
    assignees = arguments.get("assignees")
    labels = arguments.get("labels")
    due_date = arguments.get("due_date")
    dependency_data = arguments.get("dependency_data")
    query = arguments.get("query")
    limit = arguments.get("limit")
    force_full_generation = arguments.get("force_full_generation", False)
    
    # Call the original manage_task method from ConsolidatedMCPToolsV2
    return tools_impl._handle_core_task_operations(
        action=action,
        task_id=task_id,
        title=title,
        description=description,
        status=status,
        priority=priority,
        details=details,
        estimated_effort=estimated_effort,
        assignees=assignees,
        labels=labels,
        due_date=due_date,
        project_id=project_id,
        force_full_generation=force_full_generation
    ) if action in ["create", "get", "update", "delete", "complete"] else tools_impl._handle_list_search_next(
        action=action,
        status=status,
        priority=priority,
        assignees=assignees,
        labels=labels,
        limit=limit,
        query=query
    ) if action in ["list", "search", "next"] else tools_impl._handle_dependency_operations(
        action=action,
        task_id=task_id,
        dependency_data=dependency_data
    ) if action in ["add_dependency", "remove_dependency", "get_dependencies", "clear_dependencies", "get_blocking_tasks"] else {
        "success": False, "error": f"Unknown task action: {action}"
    }

async def handle_manage_subtask(arguments: dict) -> dict:
    """Handle subtask management operations"""
    action = arguments.get("action")
    task_id = arguments.get("task_id")
    subtask_data = arguments.get("subtask_data")
    
    return tools_impl._handle_subtask_operations(action, task_id, subtask_data)

async def handle_manage_agent(arguments: dict) -> dict:
    """Handle agent management operations"""
    action = arguments.get("action")
    project_id = arguments.get("project_id")
    agent_id = arguments.get("agent_id")
    name = arguments.get("name")
    call_agent = arguments.get("call_agent")
    tree_id = arguments.get("tree_id")
    
    if action == "register":
        return tools_impl._multi_agent_tools.register_agent(project_id, agent_id, name, call_agent)
    elif action == "assign":
        return tools_impl._multi_agent_tools.assign_agent_to_tree(project_id, agent_id, tree_id)
    elif action == "get":
        project_response = tools_impl._multi_agent_tools.get_project(project_id)
        if not project_response.get("success"):
            return project_response
        agents = project_response.get("project", {}).get("registered_agents", {})
        if agent_id not in agents:
            return {"success": False, "error": f"Agent {agent_id} not found"}
        return {"success": True, "agent": agents[agent_id]}
    elif action == "list":
        project_response = tools_impl._multi_agent_tools.get_project(project_id)
        if not project_response.get("success"):
            return project_response
        agents = project_response.get("project", {}).get("registered_agents", {})
        return {"success": True, "agents": agents, "count": len(agents)}
    elif action == "get_assignments":
        project_response = tools_impl._multi_agent_tools.get_project(project_id)
        if not project_response.get("success"):
            return project_response
        assignments = project_response.get("project", {}).get("agent_assignments", {})
        return {"success": True, "assignments": assignments}
    else:
        return {"success": False, "error": f"Unknown agent action: {action}"}

async def handle_call_agent(arguments: dict) -> dict:
    """Handle agent information retrieval"""
    name_agent = arguments.get("name_agent")
    return tools_impl._call_agent_use_case.execute(name_agent)

async def handle_update_auto_rule(arguments: dict) -> dict:
    """Handle auto rule updates"""
    return tools_impl._cursor_rules_tools._handle_update_auto_rule(arguments)

async def handle_validate_rules(arguments: dict) -> dict:
    """Handle rule validation"""
    return tools_impl._cursor_rules_tools._handle_validate_rules(arguments)

async def handle_manage_cursor_rules(arguments: dict) -> dict:
    """Handle cursor rules management"""
    return tools_impl._cursor_rules_tools._handle_manage_cursor_rules(arguments)

async def handle_regenerate_auto_rule(arguments: dict) -> dict:
    """Handle auto rule regeneration"""
    return tools_impl._cursor_rules_tools._handle_regenerate_auto_rule(arguments)

async def handle_validate_tasks_json(arguments: dict) -> dict:
    """Handle tasks.json validation"""
    return tools_impl._cursor_rules_tools._handle_validate_tasks_json(arguments)

async def main():
    """Run the MCP server"""
    logger.info("Starting Cursor MCP server for dhafnck_mcp...")
    
    # Set environment variables
    os.environ.setdefault("TASKS_JSON_PATH", "/home/daihungpham/agentic-project/.cursor/rules/tasks/tasks.json")
    os.environ.setdefault("TASKS_JSON_BACKUP_PATH", "/home/daihungpham/agentic-project/.cursor/rules/tasks/backup")
    
    # Initialize tools
    try:
        init_tools()
        logger.info("All tools initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize tools: {e}")
        return
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 