#!/usr/bin/env python3
"""
MCP Entry Point for FastMCP Server with Consolidated Tools

This script serves as the entry point for running the FastMCP server with
integrated task management, agent orchestration, and authentication.
"""

import logging
import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any

# Import the FastMCP server class directly
from fastmcp.server.server import FastMCP
from fastmcp.utilities.logging import configure_logging

# Import authentication system
from fastmcp.auth import AuthMiddleware, TokenValidator, TokenValidationError, RateLimitError


def create_dhafnck_mcp_server() -> FastMCP:
    """Create and configure the DhafnckMCP server with all consolidated tools."""
    
    # Configure logging
    configure_logging(level="INFO")
    logger = logging.getLogger(__name__)
    
    logger.info("Initializing DhafnckMCP server with consolidated tools and authentication...")
    
    # Initialize authentication middleware
    auth_middleware = AuthMiddleware()
    
    # Create FastMCP server with task management enabled
    server = FastMCP(
        name="DhafnckMCP - Task Management & Agent Orchestration",
        instructions=(
            "A comprehensive MCP server providing task management, project management, "
            "agent orchestration, cursor rules integration, and secure authentication. "
            "This server includes tools for managing projects, tasks, subtasks, agents, "
            "automated rule generation, and token-based authentication."
        ),
        version="2.1.0",
        # Task management is enabled by default
        enable_task_management=True,
        # Use environment variables for configuration
        task_repository=None,  # Will use default JsonTaskRepository
        projects_file_path=os.environ.get("PROJECTS_FILE_PATH"),
    )
    
    # Add authentication tools
    @server.tool()
    async def validate_token(token: str) -> dict:
        """
        Validate an authentication token.
        
        Args:
            token: The authentication token to validate
            
        Returns:
            Token validation result with user information
        """
        try:
            token_info = await auth_middleware.authenticate_request(token)
            
            if not token_info:
                return {
                    "valid": True,
                    "message": "Authentication disabled or MVP mode",
                    "user_id": "mvp_user",
                    "auth_enabled": auth_middleware.enabled
                }
            
            return {
                "valid": True,
                "user_id": token_info.user_id,
                "created_at": token_info.created_at.isoformat(),
                "expires_at": token_info.expires_at.isoformat() if token_info.expires_at else None,
                "usage_count": token_info.usage_count,
                "last_used": token_info.last_used.isoformat() if token_info.last_used else None,
                "auth_enabled": auth_middleware.enabled
            }
            
        except TokenValidationError as e:
            return {
                "valid": False,
                "error": str(e),
                "error_type": "validation_error",
                "auth_enabled": auth_middleware.enabled
            }
        except RateLimitError as e:
            return {
                "valid": False,
                "error": str(e),
                "error_type": "rate_limit_error",
                "auth_enabled": auth_middleware.enabled
            }
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return {
                "valid": False,
                "error": "Internal validation error",
                "error_type": "internal_error",
                "auth_enabled": auth_middleware.enabled
            }
    
    @server.tool()
    async def get_rate_limit_status(token: str) -> dict:
        """
        Get rate limit status for a token.
        
        Args:
            token: The authentication token
            
        Returns:
            Current rate limit status
        """
        try:
            status = await auth_middleware.get_rate_limit_status(token)
            return {
                "success": True,
                "rate_limits": status
            }
        except Exception as e:
            logger.error(f"Rate limit status error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @server.tool()
    async def revoke_token(token: str) -> dict:
        """
        Revoke an authentication token.
        
        Args:
            token: The token to revoke
            
        Returns:
            Revocation result
        """
        try:
            success = await auth_middleware.revoke_token(token)
            return {
                "success": success,
                "message": "Token revoked successfully" if success else "Failed to revoke token"
            }
        except Exception as e:
            logger.error(f"Token revocation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    @server.tool()
    def get_auth_status() -> dict:
        """
        Get authentication system status.
        
        Returns:
            Authentication system status and configuration
        """
        return auth_middleware.get_auth_status()
    
    @server.tool()
    def generate_token() -> dict:
        """
        Generate a new secure authentication token.
        
        Returns:
            New token information
        """
        try:
            if not auth_middleware.enabled:
                return {
                    "success": False,
                    "error": "Authentication is disabled",
                    "token": None
                }
            
            # Generate token using Supabase client
            token = auth_middleware.token_validator.supabase_client.generate_token()
            
            return {
                "success": True,
                "token": token,
                "message": "Token generated successfully",
                "instructions": (
                    "Store this token securely. Use it in the 'token' parameter "
                    "for authenticated MCP operations. Token expires in 30 days by default."
                )
            }
        except Exception as e:
            logger.error(f"Token generation error: {e}")
            return {
                "success": False,
                "error": str(e),
                "token": None
            }
    
    # Add a health check tool with authentication status
    @server.tool()
    def health_check() -> dict:
        """Check the health status of the MCP server.
        
        Returns:
            Server health information including available tools and auth status
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
            "version": "2.1.0",
            "authentication": auth_middleware.get_auth_status(),
            "task_management": tools_info,
            "environment": {
                "pythonpath": os.environ.get("PYTHONPATH", "not set"),
                "tasks_json_path": os.environ.get("TASKS_JSON_PATH", "not set"),
                "projects_file_path": os.environ.get("PROJECTS_FILE_PATH", "not set"),
                "cursor_agent_dir": os.environ.get("CURSOR_AGENT_DIR_PATH", "not set"),
                "auth_enabled": os.environ.get("DHAFNCK_AUTH_ENABLED", "true"),
                "mvp_mode": os.environ.get("DHAFNCK_MVP_MODE", "false"),
                "supabase_configured": bool(os.environ.get("SUPABASE_URL"))
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
                "Multi-Agent Coordination",
                "Token-based Authentication",
                "Rate Limiting",
                "Security Logging"
            ],
            "available_actions": {
                "authentication": [
                    "validate_token", "get_rate_limit_status", "revoke_token",
                    "get_auth_status", "generate_token"
                ],
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
            },
            "security_features": {
                "authentication_enabled": auth_middleware.enabled,
                "mvp_mode": auth_middleware.mvp_mode,
                "rate_limiting": auth_middleware.enabled,
                "token_caching": auth_middleware.enabled,
                "security_logging": auth_middleware.enabled,
                "supabase_integration": auth_middleware.token_validator.supabase_client.enabled if auth_middleware.token_validator else False
            }
        }
        
        if server.consolidated_tools:
            config = server.consolidated_tools._config
            capabilities["tool_configuration"] = config.get_enabled_tools()
        
        return capabilities
    
    logger.info("DhafnckMCP server initialized successfully with authentication")
    return server


def main():
    """Main entry point for the MCP server."""
    
    try:
        # Create the server
        server = create_dhafnck_mcp_server()
        
        # Log startup information
        logger = logging.getLogger(__name__)
        logger.info("Starting DhafnckMCP server with authentication...")
        
        if server.consolidated_tools:
            config = server.consolidated_tools._config
            enabled_count = sum(1 for enabled in config.get_enabled_tools().values() if enabled)
            logger.info(f"Task management tools loaded: {enabled_count} tools enabled")
        
        # Log authentication status
        auth_status = os.environ.get("DHAFNCK_AUTH_ENABLED", "true")
        mvp_mode = os.environ.get("DHAFNCK_MVP_MODE", "false")
        supabase_configured = bool(os.environ.get("SUPABASE_URL"))
        
        logger.info(f"Authentication: {auth_status}, MVP Mode: {mvp_mode}, Supabase: {supabase_configured}")
        
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
        
        logger.info(f"Starting server with transport: {transport}")
        
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