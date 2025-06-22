#!/usr/bin/env python3
"""
DDD-based FastMCP Task Management Server

A Model Context Protocol (MCP) server that provides task management tools.
Uses Domain-Driven Design architecture with FastMCP framework.
"""

import logging
import os
import sys
from pathlib import Path

# Import DDD architecture components
from task_mcp.interface.ddd_mcp_server import create_mcp_server

# Ensure the logs directory exists
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=logging.DEBUG,
    filename="logs/mcp_server.log",
    filemode="a",
    format="%(asctime)s [%(levelname)s] %(message)s",
)

# Add console handler
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

logger = logging.getLogger(__name__)


def main():
    """Main entry point for the MCP server"""
    try:
        # Create the DDD-based MCP server
        mcp = create_mcp_server()

        # Run the server
        mcp.run()

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
