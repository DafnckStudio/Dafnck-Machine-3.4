"""Main FastMCP Server with Task Management Integration"""

import asyncio
import logging
import sys
import os
from typing import Optional
from pathlib import Path

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Ensure the logs directory exists
os.makedirs("logs", exist_ok=True)

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def create_main_server(name: Optional[str] = None):
    """Create and configure the main FastMCP server with task management integration"""
    
    # Use delayed imports to avoid circular import issues
    from fastmcp import FastMCP
    from fastmcp.task_management.interface.consolidated_mcp_tools import ConsolidatedMCPTools
    
    # Initialize FastMCP server
    server_name = name or "FastMCP Server with Task Management"
    mcp = FastMCP(server_name)
    
    # Initialize and register task management tools
    dhafnck_mcp_tools = ConsolidatedMCPTools()
    dhafnck_mcp_tools.register_tools(mcp)
    
    logging.info(f"Main server '{server_name}' initialized with task management tools")
    
    return mcp


def main():
    """Main entry point for the FastMCP server with task management"""
    try:
        # Create server
        mcp = create_main_server()
        
        # Run server (defaults to stdio transport)
        logging.info("Starting FastMCP server with task management...")
        mcp.run()
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    except Exception as e:
        logging.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 