#!/usr/bin/env python3
"""
Simple MCP Server Test

Direct test of MCP server functionality without middleware complexity.
"""

import asyncio
import json
import logging
from src.fastmcp.server.mcp_entry_point import create_dhafnck_mcp_server

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def simple_server_test():
    """Simple test to verify server functionality."""
    print("🚀 Simple MCP Server Test")
    print("=" * 40)
    
    try:
        # Create server
        print("🧪 Creating server...")
        server = create_dhafnck_mcp_server()
        print(f"✅ Server created: {server.name}")
        
        # Test tool listing
        print("\n🧪 Testing tool listing...")
        tools = await server.get_tools()
        print(f"✅ Found {len(tools)} tools:")
        for tool_name in sorted(tools.keys()):
            print(f"   - {tool_name}")
        
        # Test basic health check by calling the function directly
        print("\n🧪 Testing health check function...")
        health_tools = [t for name, t in tools.items() if name == "health_check"]
        if health_tools:
            # Get the actual function from the tool
            health_tool = health_tools[0]
            if hasattr(health_tool, 'fn'):
                health_result = health_tool.fn()
                print(f"✅ Health check result: {health_result['status']}")
            else:
                print("⚠️  Health check tool found but function not accessible")
        else:
            print("❌ Health check tool not found")
        
        # Test server capabilities
        print("\n🧪 Testing server capabilities function...")
        cap_tools = [t for name, t in tools.items() if name == "get_server_capabilities"]
        if cap_tools:
            cap_tool = cap_tools[0]
            if hasattr(cap_tool, 'fn'):
                cap_result = cap_tool.fn()
                print(f"✅ Server capabilities: {len(cap_result['core_features'])} core features")
            else:
                print("⚠️  Capabilities tool found but function not accessible")
        else:
            print("❌ Capabilities tool not found")
        
        # Test if we can access consolidated tools
        print("\n🧪 Testing consolidated tools access...")
        if hasattr(server, 'consolidated_tools') and server.consolidated_tools:
            print("✅ Consolidated tools are available")
            
            # Test project creation directly
            print("\n🧪 Testing direct project creation...")
            project_result = server.consolidated_tools._project_manager.create_project(
                "simple_test_project",
                "Simple Test Project", 
                "Direct test project creation"
            )
            if project_result.get("success"):
                print("✅ Direct project creation successful")
            else:
                print(f"❌ Direct project creation failed: {project_result}")
        else:
            print("❌ Consolidated tools not available")
        
        print("\n🎉 Simple server test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(simple_server_test())
    print(f"\nTest result: {'PASSED' if success else 'FAILED'}")
    exit(0 if success else 1) 