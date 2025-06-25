"""Consolidated DDD-based MCP Server with Multi-Agent Support

NOTE: Ensure PYTHONPATH is set to dhafnck_mcp_main/src before running this server, or DDD imports will fail silently.
"""

import asyncio
import logging
import sys
import os
from typing import TYPE_CHECKING

# Package imports - no need for sys.path manipulation with proper package structure

from fastmcp.task_management.interface.consolidated_mcp_tools import ConsolidatedMCPTools

if TYPE_CHECKING:
    from fastmcp.server.server import FastMCP


def create_consolidated_mcp_server() -> "FastMCP":
    """Create and configure the consolidated MCP server with multi-agent support"""
    
    # Import FastMCP at runtime to avoid circular imports
    from fastmcp.server.server import FastMCP
    
    # Initialize FastMCP server
    mcp = FastMCP("Task Management Consolidated with Multi-Agent Support")
    
    # Initialize and register consolidated tools v2 with reorganized structure
    consolidated_tools = ConsolidatedMCPTools()
    consolidated_tools.register_tools(mcp)
    
    # Note: Multi-agent tools are now integrated into ConsolidatedMCPTools
    
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