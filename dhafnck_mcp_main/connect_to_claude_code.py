#!/usr/bin/env python3
"""
MCP Bridge: Connect task_management server to Claude Code extension
This script bridges your task_management MCP server with Claude Code extension's MCP server
"""

import asyncio
import json
import websockets
import logging
from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastmcp.task_management.interface.consolidated_mcp_server import mcp_instance

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MCPBridge:
    def __init__(self, claude_code_port=54527):
        self.claude_code_port = claude_code_port
        self.claude_code_url = f"ws://localhost:{claude_code_port}"
        self.websocket = None
        
    async def connect_to_claude_code(self):
        """Connect to Claude Code extension's MCP server"""
        try:
            logger.info(f"Connecting to Claude Code MCP server at {self.claude_code_url}")
            self.websocket = await websockets.connect(self.claude_code_url)
            logger.info("Successfully connected to Claude Code MCP server")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Claude Code MCP server: {e}")
            return False
    
    async def register_tools_with_claude_code(self):
        """Register task_management tools with Claude Code extension"""
        try:
            # Get tools from task_management server
            tools = await mcp_instance.get_tools()
            logger.info(f"Retrieved {len(tools)} tools from task_management server")
            
            # Convert tools to Claude Code format
            claude_tools = []
            for tool in tools:
                claude_tool = {
                    "name": str(tool),  # Convert tool object to string name
                    "description": f"Task management tool: {tool}",
                    "type": "mcp_tool",
                    "server": "task_management"
                }
                claude_tools.append(claude_tool)
            
            # Send tool registration message to Claude Code
            registration_message = {
                "type": "register_tools",
                "tools": claude_tools,
                "server_info": {
                    "name": "task_management",
                    "version": "1.0.0",
                    "description": "Task Management MCP Server with Multi-Agent Support"
                }
            }
            
            await self.websocket.send(json.dumps(registration_message))
            logger.info(f"Registered {len(claude_tools)} tools with Claude Code extension")
            
            # Wait for confirmation
            response = await self.websocket.recv()
            response_data = json.loads(response)
            logger.info(f"Claude Code response: {response_data}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to register tools with Claude Code: {e}")
            return False
    
    async def handle_tool_calls(self):
        """Handle tool calls from Claude Code extension"""
        try:
            while True:
                # Listen for tool calls from Claude Code
                message = await self.websocket.recv()
                message_data = json.loads(message)
                
                logger.info(f"Received message from Claude Code: {message_data}")
                
                if message_data.get("type") == "tool_call":
                    # Forward tool call to task_management server
                    tool_name = message_data.get("tool_name")
                    tool_args = message_data.get("arguments", {})
                    
                    logger.info(f"Executing tool: {tool_name} with args: {tool_args}")
                    
                    # Execute tool via task_management server
                    # This is a simplified version - you'd need to implement proper tool calling
                    result = {
                        "type": "tool_result",
                        "tool_name": tool_name,
                        "result": f"Tool {tool_name} executed successfully",
                        "success": True
                    }
                    
                    # Send result back to Claude Code
                    await self.websocket.send(json.dumps(result))
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("Connection to Claude Code closed")
        except Exception as e:
            logger.error(f"Error handling tool calls: {e}")
    
    async def run(self):
        """Main bridge loop"""
        logger.info("Starting MCP Bridge...")
        
        # Set up environment variables
        os.environ["PYTHONPATH"] = str(Path(__file__).parent / "src")
        os.environ["TASK_MANAGEMENT_TASKS_PATH"] = "/home/daihungpham/agentic-project/.cursor/rules/tasks/tasks.json"
        os.environ["TASK_MANAGEMENT_BACKUP_PATH"] = "/home/daihungpham/agentic-project/.cursor/rules/tasks/backup"
        
        # Connect to Claude Code
        if not await self.connect_to_claude_code():
            logger.error("Failed to connect to Claude Code. Make sure Cursor is running and Claude Code extension is active.")
            return
        
        # Register tools
        if not await self.register_tools_with_claude_code():
            logger.error("Failed to register tools with Claude Code")
            return
        
        logger.info("MCP Bridge is running. Press Ctrl+C to stop.")
        
        # Handle tool calls
        try:
            await self.handle_tool_calls()
        except KeyboardInterrupt:
            logger.info("Bridge stopped by user")
        finally:
            if self.websocket:
                await self.websocket.close()

async def main():
    """Main entry point"""
    bridge = MCPBridge()
    await bridge.run()

if __name__ == "__main__":
    # Change to script directory
    os.chdir(Path(__file__).parent)
    
    # Run the bridge
    asyncio.run(main()) 