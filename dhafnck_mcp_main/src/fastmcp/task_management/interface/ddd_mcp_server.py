"""DDD-based MCP Server"""

import asyncio
import logging
from fastmcp import FastMCP

from .consolidated_mcp_tools import ConsolidatedMCPTools


def create_mcp_server() -> FastMCP:
    """Create and configure the MCP server with DDD architecture"""
    
    # Initialize FastMCP server
    mcp = FastMCP("Task Management DDD")
    
    # Initialize and register consolidated tools v2 (includes all functionality)
    consolidated_tools = ConsolidatedMCPTools()
    consolidated_tools.register_tools(mcp)
    
    return mcp


def main():
    """Main entry point for the MCP server"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Create server
        mcp = create_mcp_server()
        
        # Run server
        mcp.run()
    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    except Exception as e:
        logging.error(f"Server error: {e}")
        raise


if __name__ == "__main__":
    main() 