#!/usr/bin/env python3
"""
Test script to verify MCP agent assignment functionality works correctly
after fixing the legacy role resolution issues.
"""

import sys
import os
import json
from datetime import datetime

# Adjust path for direct script execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from task_mcp.interface.consolidated_mcp_tools_v2 import ConsolidatedMCPToolsV2
from task_mcp.domain.enums.agent_roles import AgentRole, resolve_legacy_role

def test_legacy_role_resolution():
    """Test that legacy role resolution works correctly"""
    print("=== Testing Legacy Role Resolution ===")
    
    test_cases = [
        ("coding_agent", "coding_agent"),          # Direct valid role
        ("coding-agent", "coding_agent"),          # Hyphen to underscore
        ("senior_developer", "coding_agent"),      # Legacy mapping
        ("@coding_agent", "coding_agent"),         # @ prefix removal
        ("qa_engineer", "functional_tester_agent"), # Legacy mapping
        ("not_a_real_agent", None),               # Invalid role
        ("", None),                               # Empty string
        (None, None),                             # None input
    ]
    
    for input_role, expected in test_cases:
        result = resolve_legacy_role(input_role) if input_role is not None else None
        status = "✅" if result == expected else "❌"
        print(f"{status} {input_role} → {result} (expected: {expected})")
    
    print()

def test_mcp_task_assignment():
    """Test MCP task assignment with various agent formats"""
    print("=== Testing MCP Task Assignment ===")
    
    # Initialize MCP tools
    mcp_tools = ConsolidatedMCPToolsV2()
    
    # Test cases with different assignee formats
    test_cases = [
        {
            "name": "Direct valid agent",
            "assignees": ["coding_agent"],
            "expected_assignees": ["coding_agent"]
        },
        {
            "name": "Hyphenated agent name",
            "assignees": ["coding-agent"],
            "expected_assignees": ["coding_agent"]
        },
        {
            "name": "Legacy role mapping",
            "assignees": ["senior_developer"],
            "expected_assignees": ["coding_agent"]
        },
        {
            "name": "@ prefix agent",
            "assignees": ["@coding_agent"],
            "expected_assignees": ["coding_agent"]
        },
        {
            "name": "Multiple assignees with mixed formats",
            "assignees": ["coding_agent", "senior_developer", "@functional_tester_agent"],
            "expected_assignees": ["coding_agent", "coding_agent", "functional_tester_agent"]
        },
        {
            "name": "Invalid agent (should be kept as-is for backward compatibility)",
            "assignees": ["not_a_real_agent"],
            "expected_assignees": ["not_a_real_agent"]
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\nTest {i+1}: {test_case['name']}")
        
        # Create a task with the test assignees
        result = mcp_tools._handle_core_task_operations(
            action="create",
            task_id=None,
            title=f"Test Task {i+1}",
            description="Test task for agent assignment",
            status="todo",
            priority="medium",
            details="",
            estimated_effort="",
            assignees=test_case["assignees"],
            labels=[],
            due_date=None
        )
        
        if result.get("success"):
            actual_assignees = result["task"]["assignees"]
            expected_assignees = test_case["expected_assignees"]
            
            # For multiple assignees, we need to handle potential duplicates
            if actual_assignees == expected_assignees:
                print(f"✅ Assignees correctly resolved: {actual_assignees}")
            else:
                print(f"❌ Expected: {expected_assignees}, Got: {actual_assignees}")
        else:
            print(f"❌ Task creation failed: {result.get('error', 'Unknown error')}")

def test_agent_role_validation():
    """Test AgentRole enum validation"""
    print("\n=== Testing AgentRole Validation ===")
    
    test_cases = [
        ("coding_agent", True),
        ("functional_tester_agent", True),
        ("coding-agent", False),  # Hyphenated version should be false
        ("senior_developer", False),  # Legacy role should be false
        ("not_a_real_agent", False),
        ("", False),
    ]
    
    for role, expected in test_cases:
        result = AgentRole.is_valid_role(role)
        status = "✅" if result == expected else "❌"
        print(f"{status} AgentRole.is_valid_role('{role}') = {result} (expected: {expected})")

def main():
    """Run all tests"""
    print("Testing MCP Agent Assignment Fix")
    print("=" * 50)
    
    test_legacy_role_resolution()
    test_agent_role_validation()
    test_mcp_task_assignment()
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    main() 