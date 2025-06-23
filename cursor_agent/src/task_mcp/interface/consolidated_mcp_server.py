"""Consolidated DDD-based MCP Server with Multi-Agent Support"""

import logging

from fastmcp import FastMCP

# Package imports - no need for sys.path manipulation with proper package structure

# Handle both relative and absolute imports
try:
    from .consolidated_mcp_tools_v2 import ConsolidatedMCPToolsV2
except ImportError:
    # When run as script, use absolute import
    from task_mcp.interface.consolidated_mcp_tools_v2 import ConsolidatedMCPToolsV2


def create_consolidated_mcp_server() -> FastMCP:
    """Create and configure the consolidated MCP server with multi-agent support"""

    # Initialize consolidated tools first
    consolidated_tools = ConsolidatedMCPToolsV2()

    # Initialize FastMCP server and pass the tools directly
    mcp = FastMCP(
        "Task Management Consolidated with Multi-Agent Support",
        tools=consolidated_tools.get_all_tools(),
    )

    # The registration call is no longer needed as tools are passed in constructor
    # consolidated_tools.register_tools(mcp)

    return mcp


def main():
    """Main entry point for the consolidated MCP server"""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    try:
        # Create server
        mcp = create_consolidated_mcp_server()

        # Run server
        mcp.run()
    except KeyboardInterrupt:
        logging.info("Consolidated server stopped by user")
    except Exception as e:
        logging.error(f"Consolidated server error: {e}")
        raise


if __name__ == "__main__":
    main()
