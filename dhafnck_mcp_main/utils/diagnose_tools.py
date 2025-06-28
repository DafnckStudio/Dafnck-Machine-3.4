#!/usr/bin/env python3
"""
Comprehensive diagnostic script to understand tool registration issues
"""

import os
import sys
import json
import logging
from pathlib import Path

# Set up environment variables for testing
os.environ["DHAFNCK_AUTH_ENABLED"] = "false"
os.environ["DHAFNCK_DISABLE_CURSOR_TOOLS"] = "true"

# Add the source directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from fastmcp.server.server import FastMCP
from fastmcp.server.mcp_entry_point import create_dhafnck_mcp_server

def diagnose_environment():
    """Check environment variables"""
    print("=== ENVIRONMENT VARIABLES ===")
    print(f"DHAFNCK_AUTH_ENABLED: {os.environ.get('DHAFNCK_AUTH_ENABLED', 'NOT SET')}")
    print(f"DHAFNCK_DISABLE_CURSOR_TOOLS: {os.environ.get('DHAFNCK_DISABLE_CURSOR_TOOLS', 'NOT SET')}")
    print()

def diagnose_tool_config():
    """Check tool configuration file"""
    print("=== TOOL CONFIGURATION ===")
    config_path = Path(".cursor/tool_config.json")
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"Tool config file exists: {config_path}")
        print(f"Config content: {json.dumps(config, indent=2)}")
    else:
        print(f"Tool config file does not exist: {config_path}")
    print()

def diagnose_server_creation():
    """Test server creation and tool registration"""
    print("=== SERVER CREATION DIAGNOSTIC ===")
    
    try:
        # Configure logging to see what's happening
        logging.basicConfig(level=logging.INFO)
        
        print("Creating server...")
        server = create_dhafnck_mcp_server()
        
        print(f"Server created: {server.name}")
        print(f"Task management enabled: {getattr(server, '_enable_task_management', 'Unknown')}")
        
        # Get registered tools
        tools = []
        if hasattr(server, '_tools'):
            tools = list(server._tools.keys())
        elif hasattr(server, 'tools'):
            tools = list(server.tools.keys())
        
        print(f"Total tools registered: {len(tools)}")
        print("Registered tools:")
        for i, tool in enumerate(sorted(tools), 1):
            print(f"  {i:2d}. {tool}")
        
        # Check for specific tool categories
        auth_tools = [t for t in tools if t in ['validate_token', 'generate_token', 'get_auth_status', 'revoke_token', 'get_rate_limit_status']]
        cursor_tools = [t for t in tools if t in ['update_auto_rule', 'validate_rules', 'regenerate_auto_rule', 'validate_tasks_json']]
        task_tools = [t for t in tools if t in ['manage_project', 'manage_task', 'manage_subtask', 'manage_agent', 'call_agent']]
        core_tools = [t for t in tools if t in ['health_check', 'get_server_capabilities']]
        
        print(f"\nTool categories:")
        print(f"  Auth tools ({len(auth_tools)}): {auth_tools}")
        print(f"  Cursor tools ({len(cursor_tools)}): {cursor_tools}")
        print(f"  Task tools ({len(task_tools)}): {task_tools}")
        print(f"  Core tools ({len(core_tools)}): {core_tools}")
        
        # Test health check if available
        if 'health_check' in tools:
            print("\n=== HEALTH CHECK ===")
            health_tool = server._tools.get('health_check') or server.tools.get('health_check')
            if health_tool:
                try:
                    # Call the health check function directly
                    if hasattr(health_tool, 'func'):
                        result = health_tool.func()
                    else:
                        result = health_tool()
                    print(f"Health check result: {json.dumps(result, indent=2)}")
                except Exception as e:
                    print(f"Health check error: {e}")
        
    except Exception as e:
        print(f"Error creating server: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("DHAFNCK MCP TOOLS DIAGNOSTIC")
    print("=" * 50)
    
    diagnose_environment()
    diagnose_tool_config()
    diagnose_server_creation()

if __name__ == "__main__":
    main() 