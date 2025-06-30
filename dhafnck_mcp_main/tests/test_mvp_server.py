#!/usr/bin/env python3
"""
MVP MCP Server Test Script

This script tests the core functionality of the DhafnckMCP server
to ensure it's ready for MVP deployment.
"""

import asyncio
import json
import logging
from pathlib import Path

import pytest
import pytest_asyncio
from src.fastmcp.server.mcp_entry_point import create_dhafnck_mcp_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@pytest_asyncio.fixture
async def server():
    """Create a server instance for testing."""
    print("🧪 Creating server for testing...")
    
    try:
        server = create_dhafnck_mcp_server()
        print(f"✅ Server created successfully: {server.name}")
        yield server
    except Exception as e:
        print(f"❌ Server creation failed: {e}")
        raise


@pytest.mark.asyncio
async def test_server_creation():
    """Test that the server can be created successfully."""
    print("🧪 Testing server creation...")
    
    try:
        server = create_dhafnck_mcp_server()
        print(f"✅ Server created successfully: {server.name}")
        assert server is not None
        assert hasattr(server, 'name')
    except Exception as e:
        print(f"❌ Server creation failed: {e}")
        pytest.fail(f"Server creation failed: {e}")


@pytest.mark.asyncio
async def test_health_check(server):
    """Test the health check functionality."""
    print("\n🧪 Testing health check...")
    
    try:
        # Call the health check using the server's _mcp_call_tool method
        result = await server._mcp_call_tool("health_check", {})
        health_data = json.loads(result[0].text)
        print(f"✅ Health check passed: Status = {health_data.get('status', 'unknown')}")
        assert health_data.get('status') is not None
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        pytest.fail(f"Health check failed: {e}")


@pytest.mark.asyncio
async def test_server_capabilities(server):
    """Test the server capabilities functionality."""
    print("\n🧪 Testing server capabilities...")
    
    try:
        result = await server._mcp_call_tool("get_server_capabilities", {})
        capabilities = json.loads(result[0].text)
        print(f"✅ Server capabilities retrieved:")
        print(f"   Core features: {len(capabilities['core_features'])}")
        print(f"   Available actions: {len(capabilities['available_actions'])}")
        assert 'core_features' in capabilities
        assert 'available_actions' in capabilities
    except Exception as e:
        print(f"❌ Server capabilities test failed: {e}")
        pytest.fail(f"Server capabilities test failed: {e}")


@pytest.mark.asyncio
async def test_task_management(server):
    """Test basic task management functionality."""
    print("\n🧪 Testing task management...")
    
    try:
        # Test manage_project tool
        result = await server._mcp_call_tool("manage_project", {
            "action": "create",
            "project_id": "mvp_test_project",
            "name": "MVP Test Project",
            "description": "Test project for MVP validation"
        })
        project_result = json.loads(result[0].text)
        if project_result.get("success"):
            print("✅ Project creation successful")
        else:
            print(f"❌ Project creation failed: {project_result}")
            pytest.fail(f"Project creation failed: {project_result}")
        
        # Test manage_task tool
        result = await server._mcp_call_tool("manage_task", {
            "action": "create",
            "project_id": "mvp_test_project",
            "title": "MVP Test Task",
            "description": "Test task for MVP validation",
            "priority": "medium",
            "status": "todo"
        })
        task_result = json.loads(result[0].text)
        if task_result.get("success"):
            print("✅ Task creation successful")
            assert task_result.get("success") is True
        else:
            print(f"❌ Task creation failed: {task_result}")
            pytest.fail(f"Task creation failed: {task_result}")
            
    except Exception as e:
        print(f"❌ Task management test failed: {e}")
        pytest.fail(f"Task management test failed: {e}")


@pytest.mark.asyncio
async def test_tool_listing(server):
    """Test that all expected tools are available."""
    print("\n🧪 Testing tool availability...")
    
    try:
        tools = await server.get_tools()
        expected_tools = [
            "health_check",
            "get_server_capabilities", 
            "manage_project",
            "manage_task",
            "manage_subtask",
            "manage_agent",
            "call_agent"
        ]
        
        available_tools = list(tools.keys())
        print(f"✅ Available tools ({len(available_tools)}): {', '.join(available_tools)}")
        
        missing_tools = [tool for tool in expected_tools if tool not in available_tools]
        if missing_tools:
            print(f"⚠️  Missing expected tools: {missing_tools}")
            pytest.fail(f"Missing expected tools: {missing_tools}")
        else:
            print("✅ All expected tools are available")
        
        assert len(missing_tools) == 0
        
    except Exception as e:
        print(f"❌ Tool listing test failed: {e}")
        pytest.fail(f"Tool listing test failed: {e}")


# Keep the main function for standalone execution
async def main():
    """Run all MVP server tests."""
    print("🚀 Starting MVP MCP Server Tests")
    print("=" * 50)
    
    test_results = []
    
    try:
        # Test 1: Server Creation
        server = create_dhafnck_mcp_server()
        test_results.append(True)
        
        # Test 2: Tool Listing
        tools = await server.get_tools()
        expected_tools = [
            "health_check",
            "get_server_capabilities", 
            "manage_project",
            "manage_task",
            "manage_subtask",
            "manage_agent",
            "call_agent"
        ]
        
        available_tools = list(tools.keys())
        print(f"✅ Available tools ({len(available_tools)}): {', '.join(available_tools)}")
        
        missing_tools = [tool for tool in expected_tools if tool not in available_tools]
        tools_ok = len(missing_tools) == 0
        test_results.append(tools_ok)
        
        # Test 3: Health Check
        result = await server._mcp_call_tool("health_check", {})
        health_data = json.loads(result[0].text)
        health_ok = health_data.get('status') is not None
        test_results.append(health_ok)
        
        # Test 4: Server Capabilities
        result = await server._mcp_call_tool("get_server_capabilities", {})
        capabilities = json.loads(result[0].text)
        capabilities_ok = 'core_features' in capabilities and 'available_actions' in capabilities
        test_results.append(capabilities_ok)
        
        # Test 5: Task Management
        result = await server._mcp_call_tool("manage_project", {
            "action": "create",
            "project_id": "mvp_test_project",
            "name": "MVP Test Project",
            "description": "Test project for MVP validation"
        })
        project_result = json.loads(result[0].text)
        task_mgmt_ok = project_result.get("success", False)
        test_results.append(task_mgmt_ok)
        
    except Exception as e:
        print(f"❌ Critical test failure: {e}")
        test_results.append(False)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 MVP Server Test Summary")
    print("=" * 50)
    
    passed = sum(test_results)
    total = len(test_results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! MVP server is ready for deployment.")
        return True
    else:
        print("❌ Some tests failed. MVP server needs attention.")
        return False


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1) 