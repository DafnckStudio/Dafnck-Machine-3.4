#!/usr/bin/env python3
"""
Test script to verify FastMCP server integration with consolidated MCP tools.
"""

import sys
import logging
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from fastmcp import FastMCP
from fastmcp.utilities.logging import configure_logging

# Configure logging
configure_logging(level="INFO")
logger = logging.getLogger(__name__)


def test_server_creation():
    """Test creating a server with task management tools."""
    logger.info("Testing server creation with task management...")
    
    try:
        # Create server with task management enabled
        server = FastMCP(
            name="Test Server",
            instructions="Test server with task management",
            enable_task_management=True
        )
        
        logger.info("✅ Server created successfully")
        
        # Check if consolidated tools are available
        if server.consolidated_tools:
            logger.info("✅ Consolidated MCP tools are available")
            
            # Get tool configuration
            config = server.consolidated_tools._config
            enabled_tools = config.get_enabled_tools()
            
            logger.info(f"📋 Enabled tools ({len(enabled_tools)}):")
            for tool_name, enabled in enabled_tools.items():
                status = "✅" if enabled else "❌"
                logger.info(f"  {status} {tool_name}")
            
            # Use assertions instead of return
            assert server.consolidated_tools is not None, "Consolidated MCP tools should be available"
            assert len(enabled_tools) > 0, "Should have enabled tools"
        else:
            logger.error("❌ Consolidated MCP tools not available")
            assert False, "Consolidated MCP tools not available"
            
    except Exception as e:
        logger.error(f"❌ Failed to create server: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Failed to create server: {e}"


def test_server_without_task_management():
    """Test creating a server without task management tools."""
    logger.info("Testing server creation without task management...")
    
    try:
        # Create server with task management disabled
        server = FastMCP(
            name="Test Server No Tasks",
            instructions="Test server without task management",
            enable_task_management=False
        )
        
        logger.info("✅ Server created successfully")
        
        # Check that consolidated tools are not available
        if server.consolidated_tools is None:
            logger.info("✅ Consolidated MCP tools correctly disabled")
            # Use assertion instead of return
            assert server.consolidated_tools is None, "Consolidated MCP tools should be disabled"
        else:
            logger.error("❌ Consolidated MCP tools should be disabled")
            assert False, "Consolidated MCP tools should be disabled"
            
    except Exception as e:
        logger.error(f"❌ Failed to create server: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Failed to create server: {e}"


def test_manual_registration():
    """Test manual registration of task management tools."""
    logger.info("Testing manual task management tool registration...")
    
    try:
        # Create server with task management disabled initially
        server = FastMCP(
            name="Test Manual Registration",
            instructions="Test manual registration",
            enable_task_management=False
        )
        
        logger.info("✅ Server created without task management")
        
        # Manually register task management tools
        success = server.register_task_management_tools()
        
        if success and server.consolidated_tools:
            logger.info("✅ Manual registration successful")
            # Use assertion instead of return
            assert success, "Manual registration should succeed"
            assert server.consolidated_tools is not None, "Consolidated tools should be available after manual registration"
        else:
            logger.error("❌ Manual registration failed")
            assert False, "Manual registration failed"
            
    except Exception as e:
        logger.error(f"❌ Manual registration test failed: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Manual registration test failed: {e}"


async def test_async_operations():
    """Test async operations with the server."""
    logger.info("Testing async server operations...")
    
    try:
        server = FastMCP(
            name="Async Test Server",
            enable_task_management=True
        )
        
        # Test getting tools
        tools = await server.get_tools()
        logger.info(f"✅ Retrieved {len(tools)} tools")
        
        # List some of the tools
        task_tools = [name for name in tools.keys() if 'task' in name.lower() or 'project' in name.lower()]
        if task_tools:
            logger.info(f"📋 Task-related tools found: {task_tools[:5]}")  # Show first 5
        
        # Use assertions instead of return
        assert len(tools) > 0, "Should have at least some tools"
        assert any('task' in name.lower() or 'project' in name.lower() for name in tools.keys()), "Should have task-related tools"
        
    except Exception as e:
        logger.error(f"❌ Async operations test failed: {e}")
        import traceback
        traceback.print_exc()
        assert False, f"Async operations test failed: {e}"


def main():
    """Run all tests."""
    logger.info("🧪 Starting FastMCP server integration tests...")
    
    tests = [
        ("Server Creation with Task Management", test_server_creation),
        ("Server Creation without Task Management", test_server_without_task_management),
        ("Manual Tool Registration", test_manual_registration),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n🔍 Running test: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Run async test
    logger.info(f"\n🔍 Running test: Async Operations")
    try:
        import asyncio
        async_result = asyncio.run(test_async_operations())
        results.append(("Async Operations", async_result))
    except Exception as e:
        logger.error(f"❌ Async test crashed: {e}")
        results.append(("Async Operations", False))
    
    # Summary
    logger.info(f"\n📊 Test Results Summary:")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"  {status}: {test_name}")
    
    logger.info(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed!")
        return 0
    else:
        logger.error("💥 Some tests failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 