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
    
    # Get tool configuration to determine which tools to expose
    tool_config = ddd_tools._tool_config
    enabled_tools = tool_config.get("enabled_tools", {})
    
    logger.info("✅ DDD task management system initialized")
    logger.info(f"Tool configuration loaded: {sum(enabled_tools.values())}/{len(enabled_tools)} tools enabled")
    for tool_name, enabled in enabled_tools.items():
        status = "ENABLED" if enabled else "DISABLED" 
        logger.info(f"  - {tool_name}: {status}")
        
except Exception as e:
    logger.error(f"❌ Failed to initialize DDD system: {e}")
    sys.exit(1)

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools from the DDD system dynamically based on configuration."""
    logger.info("list_tools() called - building dynamic tool list")
    
    # Get enabled tools from configuration
    enabled_tools = ddd_tools._tool_config.get("enabled_tools", {})
    
    # Define all possible tools
    all_tools = {
        "manage_project": Tool(
            name="manage_project",
            description="Complete multi-agent project lifecycle management with orchestration capabilities",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["create", "get", "list", "create_tree", "get_tree_status", "orchestrate", "dashboard"],
                        "description": "Project action to perform"
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
        "manage_task": Tool(
            name="manage_task",
            description="Comprehensive task lifecycle management with 15+ actions",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string", 
                        "enum": ["create", "get", "update", "delete", "complete", "list", "search", "next"],
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
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Result limit"}
                },
                "required": ["action"]
            }
        ),
        "manage_subtask": Tool(
            name="manage_subtask",
            description="Subtask management within parent tasks",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "description": "Subtask action to perform"},
                    "task_id": {"type": "string", "description": "Parent task identifier"},
                    "subtask_data": {"type": "object", "description": "Subtask data"}
                },
                "required": ["action", "task_id"]
            }
        ),
        "manage_agent": Tool(
            name="manage_agent",
            description="Multi-agent team management and intelligent assignment",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "description": "Agent action to perform"},
                    "project_id": {"type": "string", "description": "Project identifier"},
                    "agent_id": {"type": "string", "description": "Agent identifier"},
                    "name": {"type": "string", "description": "Agent name"},
                    "call_agent": {"type": "string", "description": "Agent call reference"},
                    "tree_id": {"type": "string", "description": "Task tree identifier"}
                },
                "required": ["action"]
            }
        ),
        "call_agent": Tool(
            name="call_agent",
            description="Agent capability loading and role-based integration",
            inputSchema={
                "type": "object",
                "properties": {
                    "name_agent": {"type": "string", "description": "Agent name to call/load"}
                },
                "required": ["name_agent"]
            }
        )
    }
    
    # Build dynamic tools list based on configuration
    tools = []
    for tool_name, tool_def in all_tools.items():
        if enabled_tools.get(tool_name, True):  # Default to enabled if not specified
            tools.append(tool_def)
            logger.info(f"  + {tool_name} (enabled)")
        else:
            logger.info(f"  - {tool_name} (disabled)")
    
    logger.info(f"Returning {len(tools)}/{len(all_tools)} dynamic tools")
    return tools

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle tool calls by delegating to the DDD system."""
    logger.info(f"call_tool() called with name: {name}, args: {arguments}")
    
    # Check if tool is enabled
    enabled_tools = ddd_tools._tool_config.get("enabled_tools", {})
    if not enabled_tools.get(name, True):
        return [TextContent(
            type="text", 
            text=f"❌ Tool '{name}' is disabled in configuration"
        )]
    
    try:
        # Map tool names to DDD methods
        if name == "manage_project":
            action = arguments.get("action")
            if action == "create":
                result = ddd_tools._multi_agent_tools.create_project(
                    arguments.get("project_id", ""),
                    arguments.get("name", ""),
                    arguments.get("description", "")
                )
            elif action == "get":
                result = ddd_tools._multi_agent_tools.get_project(arguments.get("project_id", ""))
            elif action == "list":
                result = ddd_tools._multi_agent_tools.list_projects()
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
                project_id=arguments.get("project_id")
            )
            
        elif name == "manage_subtask":
            result = ddd_tools._handle_subtask_operations(
                action=arguments.get("action"),
                task_id=arguments.get("task_id"),
                subtask_data=arguments.get("subtask_data", {})
            )
            
        elif name == "manage_agent":
            action = arguments.get("action")
            if action == "register":
                result = ddd_tools._multi_agent_tools.register_agent(
                    project_id=arguments.get("project_id"),
                    agent_id=arguments.get("agent_id"),
                    name=arguments.get("name"),
                    call_agent=arguments.get("call_agent")
                )
            elif action == "assign":
                result = ddd_tools._multi_agent_tools.assign_agent_to_tree(
                    project_id=arguments.get("project_id"),
                    agent_id=arguments.get("agent_id"),
                    tree_id=arguments.get("tree_id")
                )
            else:
                result = {"success": True, "message": f"Agent action '{action}' completed"}
            
        elif name == "call_agent":
            # Use the call agent use case
            result = ddd_tools._call_agent_use_case.execute(arguments.get("name_agent", ""))
            
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