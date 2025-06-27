#!/usr/bin/env python3
"""
Minimal MCP Entry Point for FastMCP Server - No Authentication Tools

This script serves as a minimal entry point for running the FastMCP server
with task management tools only, without authentication tools.
Designed specifically for Cursor MCP integration.
"""

import logging
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any

# Import the FastMCP server class directly
from fastmcp.server.server import FastMCP
from fastmcp.utilities.logging import configure_logging


def create_minimal_dhafnck_mcp_server() -> FastMCP:
    """Create and configure a minimal DhafnckMCP server with only task management tools."""
    
    # Configure logging
    configure_logging(level="INFO")
    logger = logging.getLogger(__name__)
    
    logger.info("Initializing minimal DhafnckMCP server (no auth tools)...")
    
    # Create FastMCP server with task management enabled
    server = FastMCP(
        name="DhafnckMCP - Task Management Only",
        instructions=(
            "A minimal MCP server providing task management, project management, "
            "and agent orchestration tools. Authentication tools are disabled "
            "for simplified local development and Cursor integration."
        ),
        version="2.1.0-minimal",
        # Task management is enabled by default
        enable_task_management=True,
        # Use environment variables for configuration
        task_repository=None,  # Will use default JsonTaskRepository
        projects_file_path=os.environ.get("PROJECTS_FILE_PATH"),
    )
    
    # NO AUTHENTICATION TOOLS - they are permanently disabled in this entry point
    logger.info("Authentication tools are permanently disabled in minimal mode")
    
    # Add minimal health check tool
    @server.tool()
    def health_check() -> dict:
        """Check the health status of the minimal MCP server.
        
        Returns:
            Server health information including available tools
        """
        tools_info = {}
        if server.consolidated_tools:
            config = server.consolidated_tools._config
            enabled_tools = config.get_enabled_tools()
            tools_info = {
                "task_management_enabled": True,
                "enabled_tools_count": sum(1 for enabled in enabled_tools.values() if enabled),
                "total_tools_count": len(enabled_tools),
                "enabled_tools": [name for name, enabled in enabled_tools.items() if enabled]
            }
        else:
            tools_info = {
                "task_management_enabled": False,
                "enabled_tools_count": 0,
                "total_tools_count": 0,
                "enabled_tools": []
            }
        
        return {
            "status": "healthy",
            "server_name": server.name,
            "version": "2.1.0-minimal",
            "mode": "minimal",
            "authentication": {
                "enabled": False,
                "mvp_mode": True,
                "message": "Authentication permanently disabled in minimal mode"
            },
            "task_management": tools_info,
            "environment": {
                "pythonpath": os.environ.get("PYTHONPATH", "not set"),
                "tasks_json_path": os.environ.get("TASKS_JSON_PATH", "not set"),
                "projects_file_path": os.environ.get("PROJECTS_FILE_PATH", "not set"),
                "cursor_agent_dir": os.environ.get("CURSOR_AGENT_DIR_PATH", "not set"),
                "cursor_tools_disabled": os.environ.get("DHAFNCK_DISABLE_CURSOR_TOOLS", "false"),
                "minimal_mode": True
            }
        }
    
    @server.tool()
    def get_server_capabilities() -> dict:
        """Get detailed information about minimal server capabilities.
        
        Returns:
            Comprehensive server capability information
        """
        capabilities = {
            "mode": "minimal",
            "core_features": [
                "Task Management",
                "Project Management", 
                "Agent Orchestration",
                "Cursor Rules Integration (limited)",
                "Multi-Agent Coordination"
            ],
            "disabled_features": [
                "Token-based Authentication",
                "Rate Limiting",
                "Security Logging",
                "User Management"
            ],
            "available_actions": {
                "project_management": [
                    "create", "get", "list", "create_tree", "get_tree_status", 
                    "orchestrate", "get_dashboard"
                ],
                "task_management": [
                    "create", "update", "complete", "list", "search", "get_next",
                    "add_dependency", "remove_dependency", "list_dependencies"
                ],
                "subtask_management": [
                    "add", "update", "remove", "list"
                ],
                "agent_management": [
                    "register", "assign", "get", "list", "get_assignments", 
                    "update", "unregister", "rebalance"
                ],
                "cursor_integration": [
                    "manage_rule"  # Limited cursor integration
                ]
            }
        }
        
        if server.consolidated_tools:
            config = server.consolidated_tools._config
            capabilities["tool_configuration"] = config.get_enabled_tools()
        
        return capabilities
    
    logger.info("Minimal DhafnckMCP server initialized successfully")
    return server


def main():
    """Main entry point for the minimal MCP server."""
    
    try:
        # Create the server
        server = create_minimal_dhafnck_mcp_server()
        
        # Log startup information
        logger = logging.getLogger(__name__)
        logger.info("Starting minimal DhafnckMCP server...")
        
        if server.consolidated_tools:
            config = server.consolidated_tools._config
            enabled_count = sum(1 for enabled in config.get_enabled_tools().values() if enabled)
            logger.info(f"Task management tools loaded: {enabled_count} tools enabled")
        
        # Determine transport from environment or command line arguments
        transport = os.environ.get("FASTMCP_TRANSPORT", "stdio")
        host = os.environ.get("FASTMCP_HOST", "localhost")
        port = int(os.environ.get("FASTMCP_PORT", "8000"))
        
        # Parse command line arguments for transport override
        if len(sys.argv) > 1:
            for i, arg in enumerate(sys.argv[1:], 1):
                if arg == "--transport" and i + 1 < len(sys.argv):
                    transport = sys.argv[i + 1]
                elif arg.startswith("--transport="):
                    transport = arg.split("=", 1)[1]
        
        logger.info(f"Starting minimal server with transport: {transport}")
        
        if transport == "streamable-http":
            logger.info(f"HTTP server will bind to {host}:{port}")
            server.run(transport="streamable-http", host=host, port=port)
        else:
            # Run the server on stdio transport (default for MCP)
            server.run(transport="stdio")
        
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 