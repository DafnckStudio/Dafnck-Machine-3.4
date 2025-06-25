#!/usr/bin/env python3
"""
Simple test script to verify MCP server functionality
"""

import sys
import os
import json
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from fastmcp.server.mcp_entry_point import create_dhafnck_mcp_server

def test_server_creation():
    """Test that the server can be created successfully."""
    try:
        server = create_dhafnck_mcp_server()
        print(f"✅ Server created successfully: {server.name}")
        
        # Test getting tools
        tools = server._tool_manager._tools
        print(f"✅ Server has {len(tools)} tools registered")
        
        # List some tools
        tool_names = list(tools.keys())[:5]  # First 5 tools
        print(f"✅ Sample tools: {tool_names}")
        
        return True
    except Exception as e:
        print(f"❌ Error creating server: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_mcp_config():
    """Test MCP configuration file."""
    config_path = Path.cwd().parent / ".cursor" / "mcp.json"
    
    if not config_path.exists():
        print(f"❌ MCP config not found at {config_path}")
        return False
    
    try:
        with open(config_path) as f:
            config = json.load(f)
        
        dhafnck_config = config.get("mcpServers", {}).get("dhafnck_mcp")
        if not dhafnck_config:
            print("❌ dhafnck_mcp server not found in config")
            return False
        
        print(f"✅ MCP config found")
        print(f"  Command: {dhafnck_config['command']}")
        print(f"  Args: {dhafnck_config['args']}")
        print(f"  CWD: {dhafnck_config['cwd']}")
        
        return True
    except Exception as e:
        print(f"❌ Error reading MCP config: {e}")
        return False

def main():
    print("🧪 Testing DhafnckMCP Server Setup")
    print("=" * 40)
    
    # Set environment variables
    os.environ["PYTHONPATH"] = "dhafnck_mcp_main/src"
    os.environ["TASKS_JSON_PATH"] = ".cursor/rules/tasks/tasks.json"
    
    success = True
    
    print("\n1. Testing server creation...")
    success &= test_server_creation()
    
    print("\n2. Testing MCP configuration...")
    success &= test_mcp_config()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ All tests passed! MCP server should work correctly.")
    else:
        print("❌ Some tests failed. Check the errors above.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 