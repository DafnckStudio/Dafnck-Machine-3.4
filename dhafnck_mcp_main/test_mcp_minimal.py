#!/usr/bin/env python3
"""
Minimal MCP server test to verify basic connectivity
"""

import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from fastmcp.server.server import FastMCP

def create_minimal_test_server():
    """Create a minimal test server with just one tool"""
    
    # Create minimal FastMCP server
    server = FastMCP(
        name="MinimalTest - dhafnck_mcp",
        instructions="Minimal test server to verify MCP connectivity"
    )
    
    @server.tool()
    def test_connection() -> dict:
        """Test if the MCP connection is working.
        
        Returns:
            Simple test response
        """
        return {
            "status": "connected",
            "message": "dhafnck_mcp server is working!",
            "server_name": "MinimalTest - dhafnck_mcp"
        }
    
    return server

def main():
    """Main entry point"""
    try:
        server = create_minimal_test_server()
        print("Starting minimal dhafnck_mcp test server...", file=sys.stderr)
        server.run(transport="stdio")
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 