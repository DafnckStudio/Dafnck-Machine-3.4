#!/usr/bin/env python3
"""
Minimal MCP server for dhafnck_mcp - guaranteed to work with Cursor.
This is a simplified version to test basic connectivity.
"""

import asyncio
import logging
import sys
import os
import json
from pathlib import Path

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

# Create server instance
server = Server("dhafnck_mcp")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools"""
    return [
        Tool(
            name="hello_world",
            description="Simple test tool to verify MCP connection",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name to greet"
                    }
                },
                "required": ["name"]
            }
        ),
        Tool(
            name="list_tasks",
            description="List tasks from tasks.json file",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="create_project",
            description="Create a new project",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_id": {"type": "string", "description": "Project ID"},
                    "name": {"type": "string", "description": "Project name"},
                    "description": {"type": "string", "description": "Project description"}
                },
                "required": ["project_id", "name"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    try:
        logger.info(f"Tool called: {name} with args: {arguments}")
        
        if name == "hello_world":
            name_to_greet = arguments.get("name", "World")
            result = f"Hello, {name_to_greet}! MCP server is working correctly."
            
        elif name == "list_tasks":
            tasks_file = "/home/daihungpham/agentic-project/.cursor/rules/tasks/tasks.json"
            try:
                if os.path.exists(tasks_file):
                    with open(tasks_file, 'r') as f:
                        tasks = json.load(f)
                    result = f"Found {len(tasks)} tasks in tasks.json"
                else:
                    result = "tasks.json file not found"
            except Exception as e:
                result = f"Error reading tasks.json: {e}"
                
        elif name == "create_project":
            project_id = arguments.get("project_id", "")
            project_name = arguments.get("name", "")
            description = arguments.get("description", "")
            
            result = {
                "success": True,
                "message": f"Project '{project_name}' created successfully",
                "project": {
                    "id": project_id,
                    "name": project_name,
                    "description": description
                }
            }
            result = json.dumps(result, indent=2)
            
        else:
            result = f"Unknown tool: {name}"
            
        return [TextContent(type="text", text=result)]
        
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        error_msg = f"Error executing {name}: {str(e)}"
        return [TextContent(type="text", text=error_msg)]

async def main():
    """Run the MCP server"""
    logger.info("Starting minimal MCP server for dhafnck_mcp...")
    
    # Set environment variables
    os.environ.setdefault("TASKS_JSON_PATH", "/home/daihungpham/agentic-project/.cursor/rules/tasks/tasks.json")
    
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