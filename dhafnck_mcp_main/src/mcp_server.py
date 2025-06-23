#!/usr/bin/env python3
"""Main MCP Server Entry Point for dhafnck_mcp"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
src_dir = Path(__file__).parent
sys.path.insert(0, str(src_dir))

# Import and run the consolidated server
from fastmcp.task_management.interface.consolidated_mcp_server import main

if __name__ == "__main__":
    main() 