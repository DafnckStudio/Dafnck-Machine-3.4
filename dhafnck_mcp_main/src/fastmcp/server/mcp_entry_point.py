#!/usr/bin/env python3
"""
MCP Entry Point for FastMCP Server with Consolidated Tools

This script serves as the entry point for running the FastMCP server with
integrated task management and agent orchestration tools.
"""

import logging
import sys
import os
from pathlib import Path

# Import the FastMCP server class directly
from fastmcp.server.server import FastMCP
from fastmcp.utilities.logging import configure_logging


def create_dhafnck_mcp_server() -> FastMCP:
    """Create and configure the DhafnckMCP server with all consolidated tools."""
    
    # Configure logging
    configure_logging(level="INFO")
    logger = logging.getLogger(__name__)
    
    logger.info("Initializing DhafnckMCP server with consolidated tools...")
    
    # Create FastMCP server with task management enabled
    server = FastMCP(
        name="DhafnckMCP - Task Management & Agent Orchestration",
        instructions=(
            "A comprehensive MCP server providing task management, project management, "
            "agent orchestration, and cursor rules integration capabilities. "
            "This server includes tools for managing projects, tasks, subtasks, agents, "
            "and automated rule generation."
        ),
        version="2.0.0",
        # Task management is enabled by default
        enable_task_management=True,
        # Use environment variables for configuration
        task_repository=None,  # Will use default JsonTaskRepository
        projects_file_path=os.environ.get("PROJECTS_FILE_PATH"),
    )
    
    # Add a simple health check tool
    @server.tool()
    def health_check() -> dict:
        """Check the health status of the MCP server.
        
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
            "version": "2.0.0",
            "task_management": tools_info,
            "environment": {
                "pythonpath": os.environ.get("PYTHONPATH", "not set"),
                "tasks_json_path": os.environ.get("TASKS_JSON_PATH", "not set"),
                "projects_file_path": os.environ.get("PROJECTS_FILE_PATH", "not set"),
                "cursor_agent_dir": os.environ.get("CURSOR_AGENT_DIR_PATH", "not set")
            }
        }
    
    @server.tool()
    def get_server_capabilities() -> dict:
        """Get detailed information about server capabilities and configuration.
        
        Returns:
            Comprehensive server capability information
        """
        capabilities = {
            "core_features": [
                "Task Management",
                "Project Management", 
                "Agent Orchestration",
                "Cursor Rules Integration",
                "Multi-Agent Coordination"
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
                    "update_auto_rule", "validate_rules", "manage_cursor_rules",
                    "regenerate_auto_rule", "validate_tasks_json"
                ]
            }
        }
        
        if server.consolidated_tools:
            config = server.consolidated_tools._config
            capabilities["tool_configuration"] = config.get_enabled_tools()
        
        return capabilities
    
    logger.info("DhafnckMCP server initialized successfully")
    return server


def main():
    """Main entry point for the MCP server."""
    
    try:
        # Create the server
        server = create_dhafnck_mcp_server()
        
        # Log startup information
        logger = logging.getLogger(__name__)
        logger.info("Starting DhafnckMCP server...")
        
        if server.consolidated_tools:
            config = server.consolidated_tools._config
            enabled_count = sum(1 for enabled in config.get_enabled_tools().values() if enabled)
            logger.info(f"Task management tools loaded: {enabled_count} tools enabled")
        
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