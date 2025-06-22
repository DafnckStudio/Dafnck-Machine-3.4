#!/usr/bin/env python3
"""Test script to verify task management integration"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from fastmcp.task_management.interface.consolidated_mcp_tools_v2 import ConsolidatedMCPToolsV2
    print("✓ ConsolidatedMCPToolsV2 imported successfully")
    
    # Test tool creation
    tools = ConsolidatedMCPToolsV2()
    print("✓ ConsolidatedMCPToolsV2 instance created successfully")
    
    # Check if we can create a mock FastMCP-like object
    class MockFastMCP:
        def __init__(self):
            self.tools = []
        
        def tool(self):
            def decorator(func):
                self.tools.append(func.__name__)
                return func
            return decorator
    
    mock_mcp = MockFastMCP()
    tools.register_tools(mock_mcp)
    
    print(f"✓ Tools registered successfully: {len(mock_mcp.tools)} tools")
    print(f"  Registered tools: {', '.join(mock_mcp.tools[:5])}{'...' if len(mock_mcp.tools) > 5 else ''}")
    
    print("\n✅ Task management integration test PASSED!")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Task management integration test FAILED!")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    print("Task management integration test FAILED!")
    sys.exit(1) 