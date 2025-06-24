#!/usr/bin/env python3

import asyncio
import os
import sys
import json
import logging
from typing import Any, Dict
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# DDD imports with correct paths
from fastmcp.task_management.application import TaskApplicationService
from fastmcp.task_management.infrastructure import JsonTaskRepository, FileAutoRuleGenerator
from fastmcp.task_management.application.dtos import (
    CreateTaskRequest,
    UpdateTaskRequest,
    ListTasksRequest,
    SearchTasksRequest,
    TaskResponse
)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create server instance
logger.info("Creating DDD MCP server...")
app = Server("dhafnck_mcp_ddd")

# Find the project root dynamically (looks for pyproject.toml or .git)
def find_project_root():
    current = Path(__file__).resolve()
    for parent in [current] + list(current.parents):
        if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
            return parent
    # Fallback: use parent of src/
    return current.parent.parent

PROJECT_ROOT = find_project_root()
TASKS_JSON_PATH = PROJECT_ROOT / ".cursor" / "rules" / "tasks" / "tasks.json"

# Initialize DDD components
try:
    task_repository = JsonTaskRepository(file_path=str(TASKS_JSON_PATH))
    auto_rule_generator = FileAutoRuleGenerator()
    task_service = TaskApplicationService(task_repository, auto_rule_generator)
    logger.info("DDD components initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize DDD components: {e}")
    raise

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    logger.info("list_tools() called - registering DDD tools")
    try:
        tools = [
            Tool(
                name="manage_task",
                description="Comprehensive task lifecycle management using DDD architecture",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["create", "get", "update", "delete", "complete", "list", "search"],
                            "description": "Action to perform: create (new task), get (retrieve task), update (modify task), delete (remove task), complete (mark done), list (filter tasks), search (query tasks)"
                        },
                        "task_id": {
                            "type": "string",
                            "description": "Task ID (required for get, update, delete, complete actions)"
                        },
                        "title": {
                            "type": "string",
                            "description": "Task title (required for create action)"
                        },
                        "description": {
                            "type": "string",
                            "description": "Task description (optional for create/update actions)"
                        },
                        "status": {
                            "type": "string",
                            "enum": ["pending", "in_progress", "completed", "blocked"],
                            "description": "Task status"
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "medium", "high", "urgent"],
                            "description": "Task priority level"
                        },
                        "assignee": {
                            "type": "string",
                            "description": "Task assignee (agent name with @ prefix)"
                        },
                        "estimated_effort": {
                            "type": "string",
                            "enum": ["small", "medium", "large", "extra_large"],
                            "description": "Estimated effort level"
                        },
                        "query": {
                            "type": "string",
                            "description": "Search query (for search action)"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of results (for list/search actions)"
                        }
                    },
                    "required": ["action"]
                }
            )
        ]
        logger.info(f"Returning {len(tools)} DDD tools")
        return tools
    except Exception as e:
        logger.error(f"Error in list_tools: {e}")
        raise

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    logger.info(f"call_tool() called with name: {name}")
    if name == "manage_task":
        return await handle_task_management_ddd(arguments)
    else:
        logger.warning(f"Unknown tool called: {name}")
        return [TextContent(
            type="text", 
            text=f"❌ **Unknown tool**: {name}"
        )]

async def handle_task_management_ddd(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle task management operations using DDD architecture."""
    action = arguments.get("action")
    logger.info(f"handle_task_management_ddd called with action: {action}")
    
    try:
        if action == "create":
            title = arguments.get("title")
            if not title:
                return [TextContent(
                    type="text",
                    text="❌ **Error**: Title is required for task creation"
                )]
            
            logger.info("Creating task using DDD architecture...")
            
            # Create request DTO
            request = CreateTaskRequest(
                title=title,
                description=arguments.get("description", ""),
                status=arguments.get("status", "pending"),
                priority=arguments.get("priority", "medium"),
                estimated_effort=arguments.get("estimated_effort", "medium"),
                assignees=[arguments.get("assignee")] if arguments.get("assignee") else []
            )
            
            # Call application service
            response = task_service.create_task(request)
            
            if response.success:
                task = response.task
                task_info = f"""
✅ **Task Created Successfully (DDD)**

🆔 **ID**: {task.id}
📝 **Title**: {task.title}
📄 **Description**: {task.description or 'No description'}
📊 **Status**: {task.status}
⭐ **Priority**: {task.priority}
👤 **Assignees**: {', '.join(task.assignees) if task.assignees else 'Unassigned'}
💼 **Effort**: {task.estimated_effort}
📅 **Created**: {task.created_at}
                """.strip()
                
                return [TextContent(type="text", text=task_info)]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ **Task Creation Failed**: {response.message}"
                )]
                
        elif action == "get":
            task_id = arguments.get("task_id")
            if not task_id:
                return [TextContent(
                    type="text",
                    text="❌ **Error**: Task ID is required"
                )]
            
            logger.info(f"Getting task using DDD: {task_id}")
            
            # Get task using application service
            task = task_service.get_task(task_id)
            
            if task:
                task_response = TaskResponse.from_domain(task)
                status_emoji = "✅" if task_response.status == "completed" else "⏳"
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢", "urgent": "🚨"}.get(task_response.priority, "🟡")
                
                task_info = f"""
📋 **Task Details (DDD)**

🆔 **ID**: {task_response.id}
📝 **Title**: {task_response.title}
📄 **Description**: {task_response.description or 'No description'}
{status_emoji} **Status**: {task_response.status}
{priority_emoji} **Priority**: {task_response.priority}
💼 **Effort**: {task_response.estimated_effort}
👤 **Assignees**: {', '.join(task_response.assignees) if task_response.assignees else 'Unassigned'}
📅 **Created**: {task_response.created_at}
                """.strip()
                
                return [TextContent(type="text", text=task_info)]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ **Task Not Found**: Task with ID '{task_id}' does not exist"
                )]
                
        elif action == "list":
            logger.info("Listing tasks using DDD...")
            
            # Create list request
            request = ListTasksRequest(
                status=arguments.get("status"),
                priority=arguments.get("priority"),
                limit=arguments.get("limit")
            )
            
            # Get tasks using application service
            response = task_service.list_tasks(request)
            
            if not response.tasks:
                return [TextContent(
                    type="text",
                    text="📋 **Task List (DDD)**\n\n🔍 No tasks found. Use 'create' action to add tasks."
                )]
            
            task_list = "📋 **Task List (DDD)**\n\n"
            for task in response.tasks:
                status_emoji = "✅" if task.status == "completed" else "⏳"
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢", "urgent": "🚨"}.get(task.priority, "🟡")
                task_list += f"{status_emoji} {priority_emoji} **{task.id}**: {task.title}\n"
                if task.assignees:
                    task_list += f"   👤 {', '.join(task.assignees)}\n"
                task_list += "\n"
            
            logger.info(f"Found {response.count} tasks")
            task_list += f"📊 **Total**: {response.count} tasks"
            return [TextContent(type="text", text=task_list)]
            
        elif action == "complete":
            task_id = arguments.get("task_id")
            if not task_id:
                return [TextContent(
                    type="text",
                    text="❌ **Error**: Task ID is required"
                )]
            
            # Update task status using DDD
            request = UpdateTaskRequest(
                task_id=task_id,
                status="completed"
            )
            
            response = task_service.update_task(request)
            
            if response.success:
                task = response.task
                return [TextContent(
                    type="text",
                    text=f"✅ **Task Completed Successfully (DDD)**\n\n🆔 **ID**: {task.id}\n📝 **Title**: {task.title}\n📊 **Status**: {task.status}"
                )]
            else:
                return [TextContent(
                    type="text",
                    text=f"❌ **Task Completion Failed**: {response.message}"
                )]
                
        else:
            return [TextContent(
                type="text",
                text=f"❌ **Unknown Action**: '{action}'\n\nSupported actions: create, get, update, delete, complete, list, search"
            )]
            
    except Exception as e:
        logger.error(f"Error in handle_task_management_ddd: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"❌ **DDD Error**: {str(e)}\n\nFailed to perform task management operation using DDD architecture."
        )]

async def main():
    """Main server entry point."""
    logger.info("Starting DDD MCP server main...")
    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("stdio_server started, running DDD app...")
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    logger.info("DDD Script started...")
    asyncio.run(main()) 