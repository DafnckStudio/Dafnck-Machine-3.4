"""Consolidated DDD-based MCP Server with Multi-Agent Support"""

import asyncio
import logging
import sys
import os
from fastmcp import FastMCP

# Package imports - no need for sys.path manipulation with proper package structure

from fastmcp.dhafnck_mcp.interface.consolidated_mcp_tools_v2 import ConsolidatedMCPToolsV2


def create_consolidated_mcp_server() -> FastMCP:
    """Create and configure the consolidated MCP server with multi-agent support"""
    
    # Initialize FastMCP server
    mcp = FastMCP("Task Management Consolidated with Multi-Agent Support")
    
    # Initialize and register consolidated tools v2 with reorganized structure
    consolidated_tools = ConsolidatedMCPToolsV2()
    consolidated_tools.register_tools(mcp)
    
    # Note: Multi-agent tools are now integrated into ConsolidatedMCPToolsV2
    
    return mcp


# Create a single instance of the server to be imported by the CLI runner
mcp_instance = create_consolidated_mcp_server()


def main():
    """Main entry point for the consolidated MCP server"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Run the pre-configured server instance
        mcp_instance.run()
    except KeyboardInterrupt:
        logging.info("Consolidated server stopped by user")
    except Exception as e:
        logging.error(f"Consolidated server error: {e}")
        raise


if __name__ == "__main__":
    main() 