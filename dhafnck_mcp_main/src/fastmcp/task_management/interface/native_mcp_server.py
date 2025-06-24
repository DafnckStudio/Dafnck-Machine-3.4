#!/usr/bin/env python3
"""
Native MCP Server with DDD Task Management Integration

This server uses the native MCP protocol (not FastMCP) for proper Cursor integration
while leveraging the full DDD task management system.

IMPORTANT: This server uses native MCP protocol for Cursor compatibility.
The FastMCP-based servers don't integrate properly with Cursor's MCP client.
"""

import asyncio
import os
import sys
import json
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import DDD components (using the fixed imports)
try:
    from fastmcp.task_management.interface.consolidated_mcp_tools_v2 import ConsolidatedMCPToolsV2
    logger.info("✅ DDD components imported successfully")
except Exception as e:
    logger.error(f"❌ Failed to import DDD components: {e}")
    sys.exit(1)

# Create native MCP server instance
logger.info("Creating native MCP server...")
app = Server("dhafnck_mcp_native")
logger.info("Native MCP server created successfully")

# Initialize DDD task management system
logger.info("Initializing DDD task management system...")
try:
    ddd_tools = ConsolidatedMCPToolsV2()
    logger.info("✅ DDD task management system initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize DDD system: {e}")
    sys.exit(1)

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools from the DDD system."""
    logger.info("list_tools() called - registering DDD tools")
    
    tools = [
        Tool(
            name="manage_project",
            description="Complete multi-agent project lifecycle management with orchestration capabilities. Supports creating projects, managing task trees, agent coordination, and workload balancing across development teams.",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["create", "get", "list", "create_tree", "get_tree_status", "orchestrate", "dashboard"],
                        "description": "Project action: create (new project), get (project details), list (all projects), create_tree (new task tree), get_tree_status (tree status), orchestrate (run orchestration), dashboard (orchestration dashboard)"
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
        Tool(
            name="manage_task",
            description="Comprehensive task lifecycle management with 15+ actions including creation, updates, completion tracking, intelligent search, dependency management, and next task recommendations with AI-powered prioritization.",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string", 
                        "enum": ["create", "get", "update", "delete", "complete", "list", "search", "next", "add_dependency", "remove_dependency", "get_dependencies", "clear_dependencies", "get_blocking"],
                        "description": "Task action to perform"
                    },
                    "task_id": {"type": "string", "description": "Task identifier"},
                    "project_id": {"type": "string", "description": "Project identifier"},
                    "title": {"type": "string", "description": "Task title"},
                    "description": {"type": "string", "description": "Task description"},
                    "status": {"type": "string", "enum": ["pending", "in_progress", "completed", "blocked"], "description": "Task status"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "description": "Task priority"},
                    "details": {"type": "string", "description": "Additional task details"},
                    "estimated_effort": {"type": "string", "enum": ["small", "medium", "large", "extra_large"], "description": "Estimated effort"},
                    "assignees": {"type": "array", "items": {"type": "string"}, "description": "Task assignees"},
                    "labels": {"type": "array", "items": {"type": "string"}, "description": "Task labels"},
                    "due_date": {"type": "string", "description": "Due date (ISO format)"},
                    "dependency_data": {"type": "object", "description": "Dependency information"},
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Result limit"},
                    "force_full_generation": {"type": "boolean", "description": "Force full rule generation"}
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="manage_subtask",
            description="Hierarchical subtask management with progress tracking, nested task breakdowns, and automatic parent task status updates for complex project organization.",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["add", "update", "get"], "description": "Subtask action"},
                    "task_id": {"type": "string", "description": "Parent task ID"},
                    "subtask_data": {"type": "object", "description": "Subtask information"}
                },
                "required": ["action", "task_id"]
            }
        ),
        Tool(
            name="manage_agent",
            description="Multi-agent team management with intelligent assignment, workload balancing, role-based task distribution, and agent capability matching for optimal project coordination.",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["register", "assign", "get", "list"], "description": "Agent action"},
                    "project_id": {"type": "string", "description": "Project identifier"},
                    "agent_id": {"type": "string", "description": "Agent identifier"},
                    "name": {"type": "string", "description": "Agent name"},
                    "call_agent": {"type": "string", "description": "Agent call identifier"},
                    "tree_id": {"type": "string", "description": "Task tree identifier"}
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="update_auto_rule",
            description="Direct update of AI assistant context rules for dynamic behavior adaptation. Updates .cursor/rules/auto_rule.mdc with task-specific context and role-based instructions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "New rule content"},
                    "append": {"type": "boolean", "description": "Append to existing rules"}
                },
                "required": ["content"]
            }
        ),
        Tool(
            name="validate_rules",
            description="Comprehensive rule file quality analysis and validation. Checks syntax, structure, completeness, and provides improvement recommendations for Cursor rules.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Rule file path to validate"}
                }
            }
        ),
        Tool(
            name="manage_cursor_rules",
            description="Complete rule file system management including creation, updates, validation, and maintenance of Cursor IDE configuration and AI assistant rules.",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["create", "update", "delete", "list", "validate"], "description": "Rule management action"},
                    "file_path": {"type": "string", "description": "Rule file path"},
                    "content": {"type": "string", "description": "Rule content"},
                    "rule_type": {"type": "string", "description": "Type of rule"}
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="regenerate_auto_rule",
            description="Smart context generation for AI assistant based on current tasks, assigned roles, and project state. Automatically generates optimized .cursor/rules/auto_rule.mdc content.",
            inputSchema={
                "type": "object",
                "properties": {
                    "force_full_generation": {"type": "boolean", "description": "Force complete regeneration"}
                }
            }
        ),
        Tool(
            name="validate_tasks_json",
            description="Tasks.json integrity validation and health checks. Validates data structure, identifies corruption, checks relationships, and provides repair recommendations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "fix_issues": {"type": "boolean", "description": "Automatically fix detected issues"}
                }
            }
        ),
        Tool(
            name="call_agent",
            description="Agent capability loading and role-based integration. Loads agent configurations from YAML files and provides detailed agent information for task assignment and coordination.",
            inputSchema={
                "type": "object",
                "properties": {
                    "name_agent": {"type": "string", "description": "Agent name to call/load"}
                },
                "required": ["name_agent"]
            }
        )
    ]
    
    logger.info(f"Returning {len(tools)} DDD tools")
    return tools

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle tool calls by delegating to the DDD system."""
    logger.info(f"call_tool() called with name: {name}, args: {arguments}")
    
    try:
        # Map tool names to DDD methods
        if name == "manage_project":
            # Call the DDD project management method directly
            result = ddd_tools._multi_agent_tools.create_project(
                arguments.get("project_id", ""),
                arguments.get("name", ""),
                arguments.get("description", "")
            ) if arguments.get("action") == "create" else {}
            
            # Handle other project actions
            action = arguments.get("action")
            if action == "get":
                result = ddd_tools._multi_agent_tools.get_project(arguments.get("project_id", ""))
            elif action == "list":
                result = ddd_tools._multi_agent_tools.list_projects()
            elif action == "orchestrate":
                result = ddd_tools._multi_agent_tools.orchestrate_project(arguments.get("project_id", ""))
            elif action == "dashboard":
                result = ddd_tools._multi_agent_tools.get_orchestration_dashboard(arguments.get("project_id", ""))
            else:
                result = {"success": True, "message": f"Project action '{action}' completed"}
                
        elif name == "manage_task":
            # Use the DDD task management methods
            action = arguments.get("action")
            result = ddd_tools._handle_core_task_operations(
                action=action,
                task_id=arguments.get("task_id"),
                title=arguments.get("title"),
                description=arguments.get("description"),
                status=arguments.get("status"),
                priority=arguments.get("priority"),
                details=arguments.get("details"),
                estimated_effort=arguments.get("estimated_effort"),
                assignees=arguments.get("assignees"),
                labels=arguments.get("labels"),
                due_date=arguments.get("due_date"),
                project_id=arguments.get("project_id"),
                force_full_generation=arguments.get("force_full_generation", False)
            )
            
        elif name == "manage_subtask":
            result = ddd_tools._handle_subtask_operations(
                action=arguments.get("action"),
                task_id=arguments.get("task_id"),
                subtask_data=arguments.get("subtask_data")
            )
            
        elif name == "manage_agent":
            action = arguments.get("action")
            if action == "register":
                result = ddd_tools._multi_agent_tools.register_agent(
                    arguments.get("project_id", ""),
                    arguments.get("agent_id", ""),
                    arguments.get("name", ""),
                    arguments.get("call_agent")
                )
            elif action == "assign":
                result = ddd_tools._multi_agent_tools.assign_agent_to_tree(
                    arguments.get("project_id", ""),
                    arguments.get("agent_id", ""),
                    arguments.get("tree_id", "")
                )
            else:
                result = {"success": True, "message": f"Agent action '{action}' completed"}
                
        elif name == "call_agent":
            # Use the call agent use case
            from fastmcp.task_management.application import CallAgentUseCase
            call_agent_use_case = CallAgentUseCase()
            result = call_agent_use_case.execute(arguments.get("name_agent", ""))
            
        elif name in ["update_auto_rule", "validate_rules", "manage_cursor_rules", "regenerate_auto_rule", "validate_tasks_json"]:
            # Use cursor rules tools
            cursor_tools = ddd_tools._cursor_rules_tools
            if name == "update_auto_rule":
                result = await cursor_tools.update_auto_rule(
                    arguments.get("content", ""),
                    arguments.get("append", False)
                )
            elif name == "validate_rules":
                result = await cursor_tools.validate_rules(arguments.get("file_path"))
            elif name == "manage_cursor_rules":
                result = await cursor_tools.manage_cursor_rules(
                    arguments.get("action", ""),
                    arguments.get("file_path"),
                    arguments.get("content"),
                    arguments.get("rule_type")
                )
            elif name == "regenerate_auto_rule":
                result = await cursor_tools.regenerate_auto_rule(
                    arguments.get("force_full_generation", False)
                )
            elif name == "validate_tasks_json":
                result = await cursor_tools.validate_tasks_json(
                    arguments.get("fix_issues", False)
                )
        else:
            result = {"success": False, "error": f"Unknown tool: {name}"}
            
        # Format response
        if isinstance(result, dict):
            if result.get("success"):
                response_text = f"✅ **{name}** completed successfully\n\n"
                if "message" in result:
                    response_text += result["message"]
                elif "task" in result:
                    task = result["task"]
                    response_text += f"**Task**: {task.get('title', 'N/A')}\n**ID**: {task.get('id', 'N/A')}\n**Status**: {task.get('status', 'N/A')}"
                elif "project" in result:
                    project = result["project"]
                    response_text += f"**Project**: {project.get('name', 'N/A')}\n**ID**: {project.get('id', 'N/A')}"
                else:
                    response_text += json.dumps(result, indent=2)
            else:
                response_text = f"❌ **{name}** failed\n\n**Error**: {result.get('error', 'Unknown error')}"
        else:
            response_text = f"✅ **{name}** completed\n\n{str(result)}"
            
        return [TextContent(type="text", text=response_text)]
        
    except Exception as e:
        logger.error(f"Error in call_tool for {name}: {e}")
        import traceback
        error_details = traceback.format_exc()
        return [TextContent(
            type="text",
            text=f"❌ **Error in {name}**\n\n{str(e)}\n\n```\n{error_details}\n```"
        )]

async def main():
    """Main entry point for the native MCP server."""
    logger.info("Starting native MCP server with DDD integration...")
    
    try:
        # Run the native MCP server
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Native MCP server running with stdio transport...")
            await app.run(read_stream, write_stream, app.create_initialization_options())
    except KeyboardInterrupt:
        logger.info("Native MCP server stopped by user")
    except Exception as e:
        logger.error(f"Native MCP server error: {e}")
        raise

if __name__ == "__main__":
    logger.info("Script started...")
    asyncio.run(main()) 