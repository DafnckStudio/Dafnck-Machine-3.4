#!/usr/bin/env python3
"""
Debug MCP Server - Minimal implementation to test call_agent tool
"""

import asyncio
import os
import sys
import json
import logging
from typing import Any, Dict, List
from pathlib import Path

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set PYTHONPATH for imports
sys.path.insert(0, '/home/daihungpham/agentic-project/dhafnck_mcp_main/src')

# Import our fixed call_agent implementation
try:
    from fastmcp.task_management.interface.consolidated_mcp_tools_v2 import ConsolidatedMCPToolsV2
    logger.info("✅ DDD components imported successfully")
    ddd_tools = ConsolidatedMCPToolsV2()
    logger.info("✅ DDD tools initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to import DDD components: {e}")
    ddd_tools = None

# Create server instance
app = Server("dhafnck_mcp_debug")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools - hardcoded call_agent only for debugging."""
    logger.info("list_tools() called - returning hardcoded call_agent tool")
    
    tools = [
        Tool(
            name="call_agent",
            description="Retrieve agent YAML configurations and metadata for debugging",
            inputSchema={
                "type": "object",
                "properties": {
                    "name_agent": {
                        "type": "string", 
                        "description": "Agent name to call/load (e.g., 'coding_agent')"
                    }
                },
                "required": ["name_agent"]
            }
        )
    ]
    
    logger.info(f"Returning {len(tools)} tools")
    return tools

@app.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    logger.info(f"call_tool() called with name: {name}, args: {arguments}")
    
    try:
        if name == "call_agent":
            if ddd_tools is None:
                return [TextContent(
                    type="text",
                    text="❌ **Error**: DDD tools not available"
                )]
            
            name_agent = arguments.get("name_agent", "")
            if not name_agent:
                return [TextContent(
                    type="text",
                    text="❌ **Error**: name_agent parameter is required"
                )]
            
            # Call the fixed call_agent implementation
            result = ddd_tools._call_agent_use_case.execute(name_agent)
            
            if result.get("success"):
                agent_info = result.get("agent_info", {})
                
                response_text = f"""✅ **Agent '{name_agent}' loaded successfully**

📋 **Agent Information:**
• **Name**: {agent_info.get('name', 'N/A')}
• **Role**: {agent_info.get('role_definition', 'N/A')}
• **When to use**: {agent_info.get('when_to_use', 'N/A')}
• **Groups**: {', '.join(agent_info.get('groups', []))}
• **Persona**: {agent_info.get('persona', 'N/A')}

🔧 **Available keys**: {', '.join(agent_info.keys())}
"""
            else:
                response_text = f"❌ **Failed to load agent '{name_agent}'**\n\nError: {result.get('error', 'Unknown error')}"
            
            return [TextContent(type="text", text=response_text)]
        
        else:
            return [TextContent(
                type="text",
                text=f"❌ **Unknown tool**: {name}\n\nAvailable tools: call_agent"
            )]
            
    except Exception as e:
        logger.error(f"Error in call_tool: {e}")
        import traceback
        error_details = traceback.format_exc()
        return [TextContent(
            type="text",
            text=f"❌ **Error in {name}**\n\n{str(e)}\n\n```\n{error_details}\n```"
        )]

async def main():
    """Main entry point for the debug MCP server."""
    logger.info("Starting debug MCP server...")
    
    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Debug MCP server running with stdio transport...")
            await app.run(read_stream, write_stream, app.create_initialization_options())
    except KeyboardInterrupt:
        logger.info("Debug server stopped by user")
    except Exception as e:
        logger.error(f"Debug server error: {e}")
        raise

if __name__ == "__main__":
    logger.info("Debug script started...")
    asyncio.run(main())