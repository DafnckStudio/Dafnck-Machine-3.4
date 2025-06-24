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

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create server instance
logger.info("Creating MCP server...")
app = Server("dhafnck_mcp_simple")
logger.info("MCP server created successfully")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    logger.info("list_tools() called - registering tools")
    try:
        tools = [
            Tool(
                name="manage_task",
                description="Comprehensive task lifecycle management (simplified JSON-based)",
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
        logger.info(f"Returning {len(tools)} tools")
        return tools
    except Exception as e:
        logger.error(f"Error in list_tools: {e}")
        raise

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    logger.info(f"call_tool() called with name: {name}")
    if name == "manage_task":
        return await handle_task_management(arguments)
    else:
        logger.warning(f"Unknown tool called: {name}")
        return [TextContent(
            type="text", 
            text=f"❌ **Unknown tool**: {name}"
        )]

async def handle_task_management(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle task management operations using direct JSON manipulation."""
    action = arguments.get("action")
    logger.info(f"handle_task_management called with action: {action}")
    
    # Get tasks file path from environment or default
    tasks_file = os.getenv("TASKS_JSON_PATH", "/home/daihungpham/agentic-project/.cursor/rules/tasks/tasks.json")
    tasks_path = Path(tasks_file)
    
    try:
        # Load existing tasks
        if tasks_path.exists():
            with open(tasks_path, 'r', encoding='utf-8') as f:
                tasks_data = json.load(f)
        else:
            tasks_data = {"tasks": []}
        
        if action == "create":
            title = arguments.get("title")
            if not title:
                return [TextContent(
                    type="text",
                    text="❌ **Error**: Title is required for task creation"
                )]
            
            logger.info("Creating task with direct JSON manipulation...")
            
            # Generate simple task ID
            existing_ids = [task.get("id", "") for task in tasks_data.get("tasks", [])]
            task_counter = 1
            while f"task_{task_counter}" in existing_ids:
                task_counter += 1
            task_id = f"task_{task_counter}"
            
            # Create new task
            new_task = {
                "id": task_id,
                "title": title,
                "description": arguments.get("description", ""),
                "status": arguments.get("status", "pending"),
                "priority": arguments.get("priority", "medium"),
                "assignee": arguments.get("assignee", ""),
                "estimated_effort": arguments.get("estimated_effort", "medium"),
                "created_at": "2025-01-18T12:00:00Z"
            }
            
            # Add to tasks
            if "tasks" not in tasks_data:
                tasks_data["tasks"] = []
            tasks_data["tasks"].append(new_task)
            
            # Save back to file
            tasks_path.parent.mkdir(parents=True, exist_ok=True)
            with open(tasks_path, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Task created successfully: {task_id}")
            
            task_info = f"""
✅ **Task Created Successfully**

🆔 **ID**: {task_id}
📝 **Title**: {title}
📄 **Description**: {new_task['description'] or 'No description'}
📊 **Status**: {new_task['status']}
⭐ **Priority**: {new_task['priority']}
👤 **Assignee**: {new_task['assignee'] or 'Unassigned'}
💼 **Effort**: {new_task['estimated_effort']}
📅 **Created**: {new_task['created_at']}
            """.strip()
            
            return [TextContent(type="text", text=task_info)]
            
        elif action == "get":
            task_id = arguments.get("task_id")
            if not task_id:
                return [TextContent(
                    type="text",
                    text="❌ **Error**: Task ID is required"
                )]
            
            logger.info(f"Getting task: {task_id}")
            
            # Find task
            tasks = tasks_data.get("tasks", [])
            task = next((t for t in tasks if t.get("id") == task_id), None)
            
            if not task:
                return [TextContent(
                    type="text",
                    text=f"❌ **Task Not Found**: Task with ID '{task_id}' does not exist"
                )]
            
            status_emoji = "✅" if task.get("status") == "completed" else "⏳"
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢", "urgent": "🚨"}.get(task.get("priority", "medium"), "🟡")
            
            task_info = f"""
📋 **Task Details**

🆔 **ID**: {task.get('id', 'N/A')}
📝 **Title**: {task.get('title', 'Untitled')}
📄 **Description**: {task.get('description', 'No description')}
{status_emoji} **Status**: {task.get('status', 'pending')}
{priority_emoji} **Priority**: {task.get('priority', 'medium')}
💼 **Effort**: {task.get('estimated_effort', 'medium')}
👤 **Assignee**: {task.get('assignee', 'Unassigned')}
📅 **Created**: {task.get('created_at', 'Unknown')}
            """.strip()
            
            return [TextContent(type="text", text=task_info)]
                
        elif action == "list":
            logger.info("Listing tasks...")
            
            tasks = tasks_data.get("tasks", [])
            if not tasks:
                return [TextContent(
                    type="text",
                    text="📋 **Task List**\n\n🔍 No tasks found. Use 'create' action to add tasks."
                )]
            
            task_list = "📋 **Task List**\n\n"
            for task in tasks:
                status_emoji = "✅" if task.get("status") == "completed" else "⏳"
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢", "urgent": "🚨"}.get(task.get("priority", "medium"), "🟡")
                task_list += f"{status_emoji} {priority_emoji} **{task.get('id', 'N/A')}**: {task.get('title', 'Untitled')}\n"
                if task.get("assignee"):
                    task_list += f"   👤 {task.get('assignee')}\n"
                task_list += "\n"
            
            logger.info(f"Found {len(tasks)} tasks")
            task_list += f"📊 **Total**: {len(tasks)} tasks"
            return [TextContent(type="text", text=task_list)]
            
        elif action == "complete":
            task_id = arguments.get("task_id")
            if not task_id:
                return [TextContent(
                    type="text",
                    text="❌ **Error**: Task ID is required"
                )]
            
            # Find task
            tasks = tasks_data.get("tasks", [])
            task = next((t for t in tasks if t.get("id") == task_id), None)
            
            if not task:
                return [TextContent(
                    type="text",
                    text=f"❌ **Task Not Found**: Task with ID '{task_id}' does not exist"
                )]
            
            task["status"] = "completed"
            task["completed_at"] = "2025-01-18T12:00:00Z"
            
            # Save back to file
            with open(tasks_path, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, indent=2, ensure_ascii=False)
            
            return [TextContent(
                type="text",
                text=f"✅ **Task Completed Successfully**\n\n🆔 **ID**: {task_id}\n📝 **Title**: {task.get('title', 'Untitled')}\n📊 **Status**: completed"
            )]
                
        else:
            return [TextContent(
                type="text",
                text=f"❌ **Unknown Action**: '{action}'\n\nSupported actions: create, get, update, delete, complete, list, search"
            )]
            
    except Exception as e:
        logger.error(f"Error in handle_task_management: {e}", exc_info=True)
        return [TextContent(
            type="text",
            text=f"❌ **Error**: {str(e)}\n\nFailed to perform task management operation."
        )]

async def main():
    """Main server entry point."""
    logger.info("Starting MCP server main...")
    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("stdio_server started, running app...")
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    logger.info("Script started...")
    asyncio.run(main()) 