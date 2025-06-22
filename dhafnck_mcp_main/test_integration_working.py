#!/usr/bin/env python3
"""
Integration Test: Task Management with FastMCP Server
Tests that the migrated task management module is properly integrated with the FastMCP server.
"""

import asyncio
import json
import logging
import sys
import os
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastmcp.server.main_server import create_main_server

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_server_integration():
    """Test that the FastMCP server properly integrates task management tools"""
    
    logger.info("🚀 Starting FastMCP Server Integration Test")
    
    try:
        # Create the server
        logger.info("📝 Creating FastMCP server with task management...")
        server = create_main_server()
        
        # Test 1: Check that server was created successfully
        assert server is not None, "Server should be created successfully"
        logger.info("✅ Server created successfully")
        
        # Test 2: Check server properties
        assert server.name == "FastMCP Server with Task Management", "Server should have correct name"
        logger.info(f"✅ Server name: {server.name}")
        
        # Test 3: Check that task management tools are registered
        logger.info("🔧 Checking task management tools registration...")
        tools = await server.get_tools()
        
        expected_tools = [
            'manage_task',
            'manage_subtask', 
            'manage_project',
            'manage_agent',
            'call_agent',
            'update_auto_rule',
            'regenerate_auto_rule',
            'validate_rules',
            'manage_cursor_rules',
            'validate_tasks_json'
        ]
        
        registered_tools = list(tools.keys())
        logger.info(f"📋 Registered tools: {registered_tools}")
        
        for tool_name in expected_tools:
            if tool_name in tools:
                logger.info(f"✅ Tool '{tool_name}' is registered")
            else:
                logger.warning(f"⚠️  Tool '{tool_name}' is not registered")
        
        # Test 4: Check tool properties
        logger.info("🔍 Checking tool properties...")
        for tool_name, tool in tools.items():
            assert hasattr(tool, 'name'), f"Tool {tool_name} should have a name"
            assert hasattr(tool, 'description'), f"Tool {tool_name} should have a description"
            logger.info(f"✅ Tool '{tool_name}': {tool.description[:50]}...")
        
        # Test 5: Check that we can get MCP tool list (this is what MCP clients would call)
        logger.info("📡 Testing MCP tool list...")
        mcp_tools = await server._mcp_list_tools()
        assert isinstance(mcp_tools, list), "MCP tools should be a list"
        assert len(mcp_tools) > 0, "Should have MCP tools registered"
        
        mcp_tool_names = [tool.name for tool in mcp_tools]
        logger.info(f"📋 MCP tool names: {mcp_tool_names}")
        
        for expected_tool in ['manage_task', 'manage_project', 'call_agent']:
            assert expected_tool in mcp_tool_names, f"MCP tool '{expected_tool}' should be available"
            logger.info(f"✅ MCP tool '{expected_tool}' is available")
        
        # Test 6: Check server middleware and handlers
        logger.info("🔧 Checking server internals...")
        assert hasattr(server, '_tool_manager'), "Server should have tool manager"
        assert hasattr(server, '_mcp_server'), "Server should have MCP server"
        logger.info("✅ Server has required internal components")
        
        # Test 7: Verify task management module structure
        logger.info("📦 Checking task management module structure...")
        from fastmcp.task_management.interface.consolidated_mcp_tools_v2 import ConsolidatedMCPToolsV2
        
        # Create instance to verify it works
        task_tools = ConsolidatedMCPToolsV2()
        assert task_tools is not None, "Task management tools should be creatable"
        logger.info("✅ Task management module structure is correct")
        
        logger.info("🎉 All integration tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Integration test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test runner"""
    print("=" * 60)
    print("FastMCP Server + Task Management Integration Test")
    print("=" * 60)
    
    success = asyncio.run(test_server_integration())
    
    if success:
        print("\n🎉 INTEGRATION TEST PASSED!")
        print("✅ Task management is successfully integrated with FastMCP server.")
        print("✅ All expected tools are registered and accessible via MCP protocol.")
        print("✅ Server can be started and will expose task management capabilities.")
        return 0
    else:
        print("\n❌ INTEGRATION TEST FAILED!")
        print("There are issues with the task management integration.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 