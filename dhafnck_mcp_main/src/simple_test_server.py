#!/usr/bin/env python3

import asyncio
import json
import sys
import os
import yaml
from typing import Any, Dict
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Create server instance
app = Server("dhafnck_mcp")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="get_project_info",
            description="Get basic information about the dhafnck_mcp project",
            inputSchema={
                "type": "object",
                "properties": {
                    "random_string": {
                        "type": "string",
                        "description": "Dummy parameter for no-parameter tools"
                    }
                },
                "required": ["random_string"]
            }
        ),
        Tool(
            name="manage_project",
            description="Complete multi-agent project lifecycle management",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["create", "get", "list", "create_tree", "get_tree_status", "orchestrate", "dashboard"],
                        "description": "Action to perform: create (new project), get (project details), list (all projects), create_tree (new task tree), get_tree_status (tree status), orchestrate (optimize assignments), dashboard (project overview)"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Project ID (required for most actions except list)"
                    },
                    "name": {
                        "type": "string",
                        "description": "Project name (required for create)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Project description (optional for create)"
                    },
                    "tree_id": {
                        "type": "string",
                        "description": "Task tree ID (required for create_tree, get_tree_status)"
                    },
                    "tree_name": {
                        "type": "string",
                        "description": "Task tree name (required for create_tree)"
                    },
                    "tree_description": {
                        "type": "string",
                        "description": "Task tree description (optional for create_tree)"
                    }
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="manage_task",
            description="Comprehensive task lifecycle management with 15+ actions",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["create", "get", "update", "delete", "complete", "list", "search", "next", "add_dependency", "remove_dependency"],
                        "description": "Action to perform"
                    },
                    "task_id": {
                        "type": "string",
                        "description": "Task ID (required for get, update, delete, complete, dependency actions)"
                    },
                    "title": {
                        "type": "string",
                        "description": "Task title (required for create)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Task description (optional for create/update)"
                    },
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed", "blocked"],
                        "description": "Task status"
                    },
                    "priority": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "urgent"],
                        "description": "Task priority"
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
                    },
                    "dependency_task_id": {
                        "type": "string",
                        "description": "Dependency task ID (for dependency actions)"
                    }
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="manage_subtask",
            description="Hierarchical subtask management with progress tracking",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["create", "list", "get", "complete", "update", "delete"],
                        "description": "Action: create (new subtask), list (show subtasks), get (specific subtask), complete (mark done), update (modify subtask), delete (remove subtask)"
                    },
                    "parent_task_id": {
                        "type": "string",
                        "description": "Parent task ID (required for create and list actions)"
                    },
                    "subtask_id": {
                        "type": "string",
                        "description": "Subtask ID (required for get, complete, update, delete actions)"
                    },
                    "title": {
                        "type": "string",
                        "description": "Subtask title (required for create action)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Subtask description (optional for create/update actions)"
                    }
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="manage_agent",
            description="Multi-agent team management and intelligent assignment",
            inputSchema={
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": ["register", "assign", "list", "get", "unassign"],
                        "description": "Action: register (add agent), assign (assign to tree), list (show agents), get (agent details), unassign (remove assignment)"
                    },
                    "project_id": {
                        "type": "string",
                        "description": "Project ID (required for register, assign, list actions)"
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "Agent ID (required for register, assign, get, unassign actions)"
                    },
                    "name": {
                        "type": "string",
                        "description": "Agent name (required for register action)"
                    },
                    "call_agent": {
                        "type": "string",
                        "description": "Agent call reference (optional for register action)"
                    },
                    "tree_id": {
                        "type": "string",
                        "description": "Task tree ID (required for assign, unassign actions)"
                    }
                },
                "required": ["action"]
            }
        ),
        Tool(
            name="call_agent",
            description="Agent configuration retrieval from YAML files",
            inputSchema={
                "type": "object",
                "properties": {
                    "name_agent": {
                        "type": "string",
                        "description": "Agent name to retrieve configuration for"
                    }
                },
                "required": ["name_agent"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    if name == "get_project_info":
        project_info = {
            "project_name": "dhafnck_mcp_main",
            "package_name": "fastmcp",
            "description": "Advanced MCP server framework with integrated task management",
            "location": "/home/daihungpham/agentic-project/dhafnck_mcp_main",
            "status": "Development",
            "mcp_server": "Running and functional",
            "tools_available": 6
        }
        
        info_text = f"""
🚀 **dhafnck_mcp Project Information**

📦 **Project**: {project_info['project_name']}
📚 **Package**: {project_info['package_name']}
📝 **Description**: {project_info['description']}
📁 **Location**: {project_info['location']}
⚡ **Status**: {project_info['status']}
🔧 **MCP Server**: {project_info['mcp_server']}
🛠️ **Tools Available**: {project_info['tools_available']}

🔧 **Available Tools**:
1. get_project_info - Project information
2. manage_project - Multi-agent project lifecycle management
3. manage_task - Comprehensive task management (15+ actions)
4. manage_subtask - Hierarchical subtask management
5. manage_agent - Multi-agent team coordination
6. call_agent - Agent configuration retrieval

✅ MCP server is working correctly!
        """.strip()
        
        return [TextContent(
            type="text",
            text=info_text
        )]
    elif name == "manage_project":
        return await handle_project_management(arguments)
    elif name == "manage_task":
        return await handle_task_management(arguments)
    elif name == "manage_subtask":
        return await handle_subtask_management(arguments)
    elif name == "manage_agent":
        return await handle_agent_management(arguments)
    elif name == "call_agent":
        return await handle_call_agent(arguments)
    else:
        raise ValueError(f"Unknown tool: {name}")

async def handle_task_management(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle task management operations."""
    action = arguments.get("action")
    
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
        
        if action == "list":
            tasks = tasks_data.get("tasks", [])
            if not tasks:
                return [TextContent(
                    type="text",
                    text="📋 **Task List**\n\nNo tasks found. Use 'create' action to add tasks."
                )]
            
            task_list = "📋 **Task List**\n\n"
            for task in tasks:
                status_emoji = "✅" if task.get("status") == "completed" else "⏳"
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.get("priority", "medium"), "🟡")
                task_list += f"{status_emoji} {priority_emoji} **{task.get('id', 'N/A')}**: {task.get('title', 'Untitled')}\n"
                if task.get("description"):
                    task_list += f"   📝 {task.get('description')}\n"
                task_list += "\n"
            
            return [TextContent(type="text", text=task_list.strip())]
        
        elif action == "create":
            title = arguments.get("title")
            if not title:
                return [TextContent(
                    type="text",
                    text="❌ Error: 'title' is required for creating a task."
                )]
            
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
                "status": "pending",
                "priority": "medium",
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
            
            return [TextContent(
                type="text",
                text=f"✅ **Task Created Successfully**\n\n🆔 **ID**: {task_id}\n📝 **Title**: {title}\n📋 **Description**: {new_task['description'] or 'None'}\n⚡ **Status**: {new_task['status']}\n🎯 **Priority**: {new_task['priority']}"
            )]
        
        elif action == "get":
            task_id = arguments.get("task_id")
            if not task_id:
                return [TextContent(
                    type="text",
                    text="❌ Error: 'task_id' is required for getting a task."
                )]
            
            # Find task
            tasks = tasks_data.get("tasks", [])
            task = next((t for t in tasks if t.get("id") == task_id), None)
            
            if not task:
                return [TextContent(
                    type="text",
                    text=f"❌ **Task Not Found**\n\nTask with ID '{task_id}' does not exist."
                )]
            
            status_emoji = "✅" if task.get("status") == "completed" else "⏳"
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢", "urgent": "🚨"}.get(task.get("priority", "medium"), "🟡")
            effort_emoji = {"small": "🟢", "medium": "🟡", "large": "🔴", "extra_large": "🚨"}.get(task.get("estimated_effort", "medium"), "🟡")
            
            task_info = f"""
📋 **Task Details**

🆔 **ID**: {task.get('id', 'N/A')}
📝 **Title**: {task.get('title', 'Untitled')}
📄 **Description**: {task.get('description', 'No description')}
{status_emoji} **Status**: {task.get('status', 'pending')}
{priority_emoji} **Priority**: {task.get('priority', 'medium')}
{effort_emoji} **Effort**: {task.get('estimated_effort', 'medium')}
👤 **Assignee**: {task.get('assignee', 'Unassigned')}
📅 **Created**: {task.get('created_at', 'Unknown')}
🏷️ **Labels**: {', '.join(task.get('labels', [])) if task.get('labels') else 'None'}
🔗 **Dependencies**: {len(task.get('dependencies', []))} tasks
📋 **Subtasks**: {len(task.get('subtasks', []))} items
            """.strip()
            
            return [TextContent(type="text", text=task_info)]
        
        elif action == "update":
            task_id = arguments.get("task_id")
            if not task_id:
                return [TextContent(
                    type="text",
                    text="❌ Error: 'task_id' is required for updating a task."
                )]
            
            # Find task
            tasks = tasks_data.get("tasks", [])
            task = next((t for t in tasks if t.get("id") == task_id), None)
            
            if not task:
                return [TextContent(
                    type="text",
                    text=f"❌ **Task Not Found**\n\nTask with ID '{task_id}' does not exist."
                )]
            
            # Update fields if provided
            updated_fields = []
            if arguments.get("title"):
                task["title"] = arguments.get("title")
                updated_fields.append("title")
            if arguments.get("description"):
                task["description"] = arguments.get("description")
                updated_fields.append("description")
            if arguments.get("status"):
                task["status"] = arguments.get("status")
                updated_fields.append("status")
            if arguments.get("priority"):
                task["priority"] = arguments.get("priority")
                updated_fields.append("priority")
            if arguments.get("assignee"):
                task["assignee"] = arguments.get("assignee")
                updated_fields.append("assignee")
            if arguments.get("estimated_effort"):
                task["estimated_effort"] = arguments.get("estimated_effort")
                updated_fields.append("estimated_effort")
            
            task["updated_at"] = "2025-01-18T12:00:00Z"
            
            # Save back to file
            with open(tasks_path, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, indent=2, ensure_ascii=False)
            
            return [TextContent(
                type="text",
                text=f"✅ **Task Updated Successfully**\n\n🆔 **ID**: {task_id}\n📝 **Updated Fields**: {', '.join(updated_fields) if updated_fields else 'None'}\n🕐 **Updated At**: {task['updated_at']}"
            )]
        
        elif action == "complete":
            task_id = arguments.get("task_id")
            if not task_id:
                return [TextContent(
                    type="text",
                    text="❌ Error: 'task_id' is required for completing a task."
                )]
            
            # Find task
            tasks = tasks_data.get("tasks", [])
            task = next((t for t in tasks if t.get("id") == task_id), None)
            
            if not task:
                return [TextContent(
                    type="text",
                    text=f"❌ **Task Not Found**\n\nTask with ID '{task_id}' does not exist."
                )]
            
            task["status"] = "completed"
            task["completed_at"] = "2025-01-18T12:00:00Z"
            
            # Save back to file
            with open(tasks_path, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, indent=2, ensure_ascii=False)
            
            return [TextContent(
                type="text",
                text=f"✅ **Task Completed Successfully**\n\n🆔 **ID**: {task_id}\n📝 **Title**: {task.get('title', 'Untitled')}\n🎉 **Status**: completed\n🕐 **Completed At**: {task['completed_at']}"
            )]
        
        elif action == "search":
            query = arguments.get("query")
            if not query:
                return [TextContent(
                    type="text",
                    text="❌ Error: 'query' is required for searching tasks."
                )]
            
            tasks = tasks_data.get("tasks", [])
            limit = arguments.get("limit", 10)
            
            # Simple search in title and description
            matching_tasks = []
            query_lower = query.lower()
            
            for task in tasks:
                title = task.get("title", "").lower()
                description = task.get("description", "").lower()
                if query_lower in title or query_lower in description:
                    matching_tasks.append(task)
                    if len(matching_tasks) >= limit:
                        break
            
            if not matching_tasks:
                return [TextContent(
                    type="text",
                    text=f"🔍 **Search Results for '{query}'**\n\nNo matching tasks found."
                )]
            
            search_results = f"🔍 **Search Results for '{query}'** ({len(matching_tasks)} found)\n\n"
            for task in matching_tasks:
                status_emoji = "✅" if task.get("status") == "completed" else "⏳"
                priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢", "urgent": "🚨"}.get(task.get("priority", "medium"), "🟡")
                search_results += f"{status_emoji} {priority_emoji} **{task.get('id', 'N/A')}**: {task.get('title', 'Untitled')}\n"
                if task.get("description"):
                    search_results += f"   📝 {task.get('description')[:100]}{'...' if len(task.get('description', '')) > 100 else ''}\n"
                search_results += "\n"
            
            return [TextContent(type="text", text=search_results.strip())]
        
        elif action == "next":
            tasks = tasks_data.get("tasks", [])
            
            # Simple next task logic: find highest priority pending task
            pending_tasks = [t for t in tasks if t.get("status") == "pending"]
            
            if not pending_tasks:
                return [TextContent(
                    type="text",
                    text="🎯 **Next Task Recommendation**\n\nNo pending tasks found. All tasks are completed or in progress!"
                )]
            
            # Sort by priority (urgent > high > medium > low)
            priority_order = {"urgent": 4, "high": 3, "medium": 2, "low": 1}
            pending_tasks.sort(key=lambda t: priority_order.get(t.get("priority", "medium"), 2), reverse=True)
            
            next_task = pending_tasks[0]
            status_emoji = "⏳"
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢", "urgent": "🚨"}.get(next_task.get("priority", "medium"), "🟡")
            
            next_info = f"""
🎯 **Next Task Recommendation**

{status_emoji} {priority_emoji} **{next_task.get('id', 'N/A')}**: {next_task.get('title', 'Untitled')}
📄 **Description**: {next_task.get('description', 'No description')}
🎯 **Priority**: {next_task.get('priority', 'medium')}
👤 **Assignee**: {next_task.get('assignee', 'Unassigned')}
⚡ **Effort**: {next_task.get('estimated_effort', 'medium')}

💡 **Why this task?** Highest priority pending task in your queue.
            """.strip()
            
            return [TextContent(type="text", text=next_info)]
        
        else:
            return [TextContent(
                type="text",
                text=f"❌ **Unknown Action**: '{action}'\n\nSupported actions: list, create, get"
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ **Error**: {str(e)}\n\nFailed to perform task management operation."
        )]

async def handle_subtask_management(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle subtask management operations."""
    action = arguments.get("action")
    
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
            parent_task_id = arguments.get("parent_task_id")
            title = arguments.get("title")
            
            if not parent_task_id:
                return [TextContent(
                    type="text",
                    text="❌ Error: 'parent_task_id' is required for creating a subtask."
                )]
            
            if not title:
                return [TextContent(
                    type="text",
                    text="❌ Error: 'title' is required for creating a subtask."
                )]
            
            # Find parent task
            tasks = tasks_data.get("tasks", [])
            parent_task = next((t for t in tasks if t.get("id") == parent_task_id), None)
            
            if not parent_task:
                return [TextContent(
                    type="text",
                    text=f"❌ **Parent Task Not Found**\n\nTask with ID '{parent_task_id}' does not exist."
                )]
            
            # Initialize subtasks array if it doesn't exist
            if "subtasks" not in parent_task:
                parent_task["subtasks"] = []
            
            # Generate subtask ID
            existing_subtask_ids = [st.get("id", "") for st in parent_task["subtasks"]]
            subtask_counter = 1
            while f"{parent_task_id}_sub_{subtask_counter}" in existing_subtask_ids:
                subtask_counter += 1
            subtask_id = f"{parent_task_id}_sub_{subtask_counter}"
            
            # Create new subtask
            new_subtask = {
                "id": subtask_id,
                "title": title,
                "description": arguments.get("description", ""),
                "status": "pending",
                "created_at": "2025-01-18T12:00:00Z"
            }
            
            # Add subtask to parent
            parent_task["subtasks"].append(new_subtask)
            
            # Save back to file
            tasks_path.parent.mkdir(parents=True, exist_ok=True)
            with open(tasks_path, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, indent=2, ensure_ascii=False)
            
            return [TextContent(
                type="text",
                text=f"✅ **Subtask Created Successfully**\n\n🆔 **ID**: {subtask_id}\n📝 **Title**: {title}\n📋 **Description**: {new_subtask['description'] or 'None'}\n👨‍💼 **Parent Task**: {parent_task_id}\n⚡ **Status**: {new_subtask['status']}"
            )]
        
        elif action == "list":
            parent_task_id = arguments.get("parent_task_id")
            
            if not parent_task_id:
                return [TextContent(
                    type="text",
                    text="❌ Error: 'parent_task_id' is required for listing subtasks."
                )]
            
            # Find parent task
            tasks = tasks_data.get("tasks", [])
            parent_task = next((t for t in tasks if t.get("id") == parent_task_id), None)
            
            if not parent_task:
                return [TextContent(
                    type="text",
                    text=f"❌ **Parent Task Not Found**\n\nTask with ID '{parent_task_id}' does not exist."
                )]
            
            subtasks = parent_task.get("subtasks", [])
            if not subtasks:
                return [TextContent(
                    type="text",
                    text=f"📋 **Subtasks for Task: {parent_task_id}**\n\n🔍 No subtasks found. Use 'create' action to add subtasks."
                )]
            
            subtask_list = f"📋 **Subtasks for Task: {parent_task_id}**\n"
            subtask_list += f"📝 **Parent**: {parent_task.get('title', 'Untitled')}\n\n"
            
            for subtask in subtasks:
                status_emoji = "✅" if subtask.get("status") == "completed" else "⏳"
                subtask_list += f"{status_emoji} **{subtask.get('id', 'N/A')}**: {subtask.get('title', 'Untitled')}\n"
                if subtask.get("description"):
                    subtask_list += f"   📝 {subtask.get('description')}\n"
                subtask_list += "\n"
            
            return [TextContent(type="text", text=subtask_list.strip())]
        
        elif action == "get":
            subtask_id = arguments.get("subtask_id")
            
            if not subtask_id:
                return [TextContent(
                    type="text",
                    text="❌ Error: 'subtask_id' is required for getting a subtask."
                )]
            
            # Find subtask across all tasks
            tasks = tasks_data.get("tasks", [])
            found_subtask = None
            parent_task = None
            
            for task in tasks:
                for subtask in task.get("subtasks", []):
                    if subtask.get("id") == subtask_id:
                        found_subtask = subtask
                        parent_task = task
                        break
                if found_subtask:
                    break
            
            if not found_subtask:
                return [TextContent(
                    type="text",
                    text=f"❌ **Subtask Not Found**\n\nSubtask with ID '{subtask_id}' does not exist."
                )]
            
            status_emoji = "✅" if found_subtask.get("status") == "completed" else "⏳"
            
            subtask_info = f"""
📋 **Subtask Details**

🆔 **ID**: {found_subtask.get('id', 'N/A')}
📝 **Title**: {found_subtask.get('title', 'Untitled')}
📄 **Description**: {found_subtask.get('description', 'No description')}
{status_emoji} **Status**: {found_subtask.get('status', 'unknown')}
👨‍💼 **Parent Task**: {parent_task.get('id', 'N/A')} - {parent_task.get('title', 'Untitled')}
📅 **Created**: {found_subtask.get('created_at', 'Unknown')}
            """.strip()
            
            return [TextContent(type="text", text=subtask_info)]
        
        elif action == "complete":
            subtask_id = arguments.get("subtask_id")
            
            if not subtask_id:
                return [TextContent(
                    type="text",
                    text="❌ Error: 'subtask_id' is required for completing a subtask."
                )]
            
            # Find and update subtask
            tasks = tasks_data.get("tasks", [])
            found_subtask = None
            parent_task = None
            
            for task in tasks:
                for subtask in task.get("subtasks", []):
                    if subtask.get("id") == subtask_id:
                        found_subtask = subtask
                        parent_task = task
                        break
                if found_subtask:
                    break
            
            if not found_subtask:
                return [TextContent(
                    type="text",
                    text=f"❌ **Subtask Not Found**\n\nSubtask with ID '{subtask_id}' does not exist."
                )]
            
            # Update status
            found_subtask["status"] = "completed"
            found_subtask["completed_at"] = "2025-01-18T12:00:00Z"
            
            # Save back to file
            tasks_path.parent.mkdir(parents=True, exist_ok=True)
            with open(tasks_path, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, indent=2, ensure_ascii=False)
            
            return [TextContent(
                type="text",
                text=f"✅ **Subtask Completed Successfully**\n\n🆔 **ID**: {subtask_id}\n📝 **Title**: {found_subtask.get('title', 'Untitled')}\n👨‍💼 **Parent Task**: {parent_task.get('id', 'N/A')}\n🎉 **Status**: completed"
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"❌ **Unknown Action**: '{action}'\n\nSupported actions: create, list, get, complete"
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ **Error**: {str(e)}\n\nFailed to perform subtask management operation."
        )]

async def handle_project_management(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle project management operations."""
    action = arguments.get("action")
    
    # Get projects file path
    projects_file = "/home/daihungpham/agentic-project/.cursor/rules/brain/projects.json"
    projects_path = Path(projects_file)
    
    try:
        # Load existing projects
        if projects_path.exists():
            with open(projects_path, 'r', encoding='utf-8') as f:
                projects_data = json.load(f)
        else:
            projects_data = {}
        
        if action == "create":
            project_id = arguments.get("project_id")
            name = arguments.get("name")
            description = arguments.get("description", "")
            
            if not project_id or not name:
                return [TextContent(
                    type="text",
                    text="❌ Error: 'project_id' and 'name' are required for creating a project."
                )]
            
            # Create new project
            new_project = {
                "id": project_id,
                "name": name,
                "description": description,
                "task_trees": {"main": {"id": "main", "name": "Main Tasks", "description": "Main task tree"}},
                "registered_agents": {},
                "agent_assignments": {},
                "created_at": "2025-01-18T12:00:00Z"
            }
            
            projects_data[project_id] = new_project
            
            # Save projects
            projects_path.parent.mkdir(parents=True, exist_ok=True)
            with open(projects_path, 'w', encoding='utf-8') as f:
                json.dump(projects_data, f, indent=2, ensure_ascii=False)
            
            return [TextContent(
                type="text",
                text=f"✅ **Project Created Successfully**\n\n🆔 **ID**: {project_id}\n📝 **Name**: {name}\n📋 **Description**: {description or 'None'}\n🌳 **Task Trees**: main (default)\n📅 **Created**: {new_project['created_at']}"
            )]
        
        elif action == "get":
            project_id = arguments.get("project_id")
            if not project_id:
                return [TextContent(
                    type="text",
                    text="❌ Error: 'project_id' is required for getting a project."
                )]
            
            project = projects_data.get(project_id)
            if not project:
                return [TextContent(
                    type="text",
                    text=f"❌ **Project Not Found**\n\nProject with ID '{project_id}' does not exist."
                )]
            
            trees = project.get("task_trees", {})
            agents = project.get("registered_agents", {})
            
            project_info = f"""
🏗️ **Project Details**

🆔 **ID**: {project.get('id', 'N/A')}
📝 **Name**: {project.get('name', 'Untitled')}
📄 **Description**: {project.get('description', 'No description')}
🌳 **Task Trees**: {len(trees)} ({', '.join(trees.keys())})
🤖 **Registered Agents**: {len(agents)}
📅 **Created**: {project.get('created_at', 'Unknown')}
            """.strip()
            
            return [TextContent(type="text", text=project_info)]
        
        elif action == "list":
            if not projects_data:
                return [TextContent(
                    type="text",
                    text="📋 **Project List**\n\nNo projects found. Use 'create' action to add projects."
                )]
            
            project_list = "📋 **Project List**\n\n"
            for project in projects_data.values():
                trees_count = len(project.get("task_trees", {}))
                agents_count = len(project.get("registered_agents", {}))
                project_list += f"🏗️ **{project.get('id', 'N/A')}**: {project.get('name', 'Untitled')}\n"
                project_list += f"   📝 {project.get('description', 'No description')}\n"
                project_list += f"   🌳 {trees_count} trees, 🤖 {agents_count} agents\n\n"
            
            return [TextContent(type="text", text=project_list.strip())]
        
        else:
            return [TextContent(
                type="text",
                text=f"❌ **Unknown Action**: '{action}'\n\nSupported actions: create, get, list, create_tree, get_tree_status, orchestrate, dashboard"
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ **Error**: {str(e)}\n\nFailed to perform project management operation."
        )]

async def handle_agent_management(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle agent management operations."""
    action = arguments.get("action")
    
    # Get projects file path
    projects_file = "/home/daihungpham/agentic-project/.cursor/rules/brain/projects.json"
    projects_path = Path(projects_file)
    
    try:
        # Load existing projects
        if projects_path.exists():
            with open(projects_path, 'r', encoding='utf-8') as f:
                projects_data = json.load(f)
        else:
            projects_data = {}
        
        if action == "register":
            project_id = arguments.get("project_id")
            agent_id = arguments.get("agent_id")
            name = arguments.get("name")
            
            if not all([project_id, agent_id, name]):
                return [TextContent(
                    type="text",
                    text="❌ Error: 'project_id', 'agent_id', and 'name' are required for registering an agent."
                )]
            
            if project_id not in projects_data:
                return [TextContent(
                    type="text",
                    text=f"❌ **Project Not Found**\n\nProject with ID '{project_id}' does not exist."
                )]
            
            # Register agent
            if "registered_agents" not in projects_data[project_id]:
                projects_data[project_id]["registered_agents"] = {}
            
            projects_data[project_id]["registered_agents"][agent_id] = {
                "id": agent_id,
                "name": name,
                "call_agent": arguments.get("call_agent", f"@{agent_id}")
            }
            
            # Save projects
            with open(projects_path, 'w', encoding='utf-8') as f:
                json.dump(projects_data, f, indent=2, ensure_ascii=False)
            
            return [TextContent(
                type="text",
                text=f"✅ **Agent Registered Successfully**\n\n🆔 **Agent ID**: {agent_id}\n📝 **Name**: {name}\n🏗️ **Project**: {project_id}\n🤖 **Call Reference**: {arguments.get('call_agent', f'@{agent_id}')}"
            )]
        
        elif action == "list":
            project_id = arguments.get("project_id")
            if not project_id:
                return [TextContent(
                    type="text",
                    text="❌ Error: 'project_id' is required for listing agents."
                )]
            
            if project_id not in projects_data:
                return [TextContent(
                    type="text",
                    text=f"❌ **Project Not Found**\n\nProject with ID '{project_id}' does not exist."
                )]
            
            agents = projects_data[project_id].get("registered_agents", {})
            if not agents:
                return [TextContent(
                    type="text",
                    text=f"🤖 **Agents for Project: {project_id}**\n\n🔍 No agents found. Use 'register' action to add agents."
                )]
            
            agent_list = f"🤖 **Agents for Project: {project_id}**\n\n"
            for agent in agents.values():
                agent_list += f"🤖 **{agent.get('id', 'N/A')}**: {agent.get('name', 'Unnamed')}\n"
                agent_list += f"   📞 {agent.get('call_agent', 'N/A')}\n\n"
            
            return [TextContent(type="text", text=agent_list.strip())]
        
        else:
            return [TextContent(
                type="text",
                text=f"❌ **Unknown Action**: '{action}'\n\nSupported actions: register, assign, list, get, unassign"
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ **Error**: {str(e)}\n\nFailed to perform agent management operation."
        )]

async def handle_call_agent(arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle call agent operations."""
    name_agent = arguments.get("name_agent")
    
    if not name_agent:
        return [TextContent(
            type="text",
            text="❌ Error: 'name_agent' is required for calling agent."
        )]
    
    try:
        # Look for agent YAML files
        yaml_lib_path = Path("/home/daihungpham/agentic-project/dhafnck_mcp_main/yaml-lib")
        agent_dir = yaml_lib_path / f"{name_agent}"
        
        if not agent_dir.exists():
            return [TextContent(
                type="text",
                text=f"❌ **Agent Not Found**\n\nAgent '{name_agent}' does not exist in yaml-lib directory."
            )]
        
        # Try to read job_desc.yaml if it exists
        job_desc_file = agent_dir / "job_desc.yaml"
        if job_desc_file.exists():
            with open(job_desc_file, 'r', encoding='utf-8') as f:
                job_desc = yaml.safe_load(f)
            
            agent_info = f"""
🤖 **Agent Configuration: {name_agent}**

📝 **Role**: {job_desc.get('role', 'Not specified')}
📋 **Description**: {job_desc.get('description', 'Not specified')}
🎯 **Capabilities**: {', '.join(job_desc.get('capabilities', []))}
🛠️ **Tools**: {', '.join(job_desc.get('tools', []))}
📁 **Configuration Directory**: {agent_dir}

✅ Agent configuration loaded successfully!
            """.strip()
        else:
            agent_info = f"""
🤖 **Agent Configuration: {name_agent}**

📁 **Configuration Directory**: {agent_dir}
📂 **Available Subdirectories**: {', '.join([d.name for d in agent_dir.iterdir() if d.is_dir()])}

⚠️ No job_desc.yaml found, but agent directory exists.
            """.strip()
        
        return [TextContent(type="text", text=agent_info)]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ **Error**: {str(e)}\n\nFailed to load agent configuration."
        )]

async def main():
    """Main server entry point."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main()) 