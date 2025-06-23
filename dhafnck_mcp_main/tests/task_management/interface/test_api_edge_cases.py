"""
Integration tests for API edge cases.
"""

import pytest
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from fastmcp.task_management.interface.consolidated_mcp_tools_v2 import ConsolidatedMCPToolsV2

@pytest.fixture
def mcp_tools():
    """Fixture to provide an instance of ConsolidatedMCPToolsV2."""
    # We can enhance this fixture to use a temporary task file for testing
    return ConsolidatedMCPToolsV2()

@pytest.mark.parametrize(
    "test_name, task_data, expected_error_msg",
    [
        (
            "missing_title",
            {"title": None, "description": "A task without a title", "priority": "medium"},
            "Title is required",
        ),
        (
            "invalid_priority",
            {"title": "Invalid Priority", "description": "A task with invalid priority", "priority": "super high"},
            "Invalid priority",
        ),
        (
            "invalid_label",
            {"title": "Invalid Label", "description": "A task with invalid label", "priority": "medium", "labels": ["!@#$%^"]},
            "Invalid label(s) provided",
        ),
    ],
)
def test_create_task_edge_cases(mcp_tools, test_name, task_data, expected_error_msg):
    """Test creating a task with various edge cases."""
    result = mcp_tools._handle_core_task_operations(
        action="create",
        title=task_data.get("title"),
        description=task_data.get("description"),
        priority=task_data.get("priority"),
        labels=task_data.get("labels"),
        task_id=None,
        status=None,
        details=None,
        estimated_effort=None,
        assignees=None,
        due_date=None,
    )
    assert not result["success"]
    assert expected_error_msg in result["error"]

def test_update_task_invalid_status(mcp_tools):
    """Test updating a task with an invalid status."""
    # First, create a task to update
    create_result = mcp_tools._handle_core_task_operations(
        action="create",
        title="Task to Update",
        description="This task will be updated with an invalid status",
        priority="low",
        task_id=None,
        status=None,
        details=None,
        estimated_effort=None,
        assignees=None,
        labels=None,
        due_date=None
    )
    
    # The create operation should return a dict on success
    assert create_result["success"]
    task_id = create_result["task"]["id"]

    # Now, attempt to update with an invalid status
    update_result = mcp_tools._handle_core_task_operations(
        action="update",
        task_id=task_id,
        status="in_another_dimension",
        title=None,
        description=None,
        priority=None,
        details=None,
        estimated_effort=None,
        assignees=None,
        labels=None,
        due_date=None
    )
    assert not update_result["success"]
    assert "Invalid task status" in update_result["error"] 