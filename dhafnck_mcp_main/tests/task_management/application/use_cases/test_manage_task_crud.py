"""
Integration tests for the manage_task tool's CRUD operations.
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
    tools = ConsolidatedMCPToolsV2()
    # You might want to use a temporary, clean task file for these tests
    # For now, we rely on the default test tasks file, assuming a known state or cleaning it up.
    return tools

def create_test_task(mcp_tools, title="A test task"):
    """Helper function to create a task for testing."""
    result = mcp_tools._handle_core_task_operations(
        action="create",
        title=title,
        description="This is a test task.",
        priority="high",
        labels=["testing"],
        task_id=None,
        status=None,
        details=None,
        estimated_effort=None,
        assignees=None,
        due_date=None
    )
    assert result["success"]
    return result["task"]["id"]

def test_create_task_happy_path(mcp_tools):
    """Test successful creation of a task."""
    result = mcp_tools._handle_core_task_operations(
        action="create",
        title="A new task",
        description="This is a test task.",
        priority="high",
        labels=["testing", "happy-path"],
        task_id=None,
        status=None,
        details=None,
        estimated_effort=None,
        assignees=None,
        due_date=None
    )
    assert result["success"]
    assert result["action"] == "create"
    assert result["task"]["title"] == "A new task"

def test_get_task_happy_path(mcp_tools):
    """Test fetching an existing task."""
    task_id = create_test_task(mcp_tools, "Task for get test")
    
    result = mcp_tools._handle_core_task_operations(
        action="get",
        task_id=task_id,
        title=None,
        description=None,
        priority=None,
        labels=None,
        status=None,
        details=None,
        estimated_effort=None,
        assignees=None,
        due_date=None
    )
    assert result["success"]
    assert result["action"] == "get"
    assert result["task"]["id"] == task_id

def test_update_task_happy_path(mcp_tools):
    """Test updating an existing task."""
    task_id = create_test_task(mcp_tools, "Task for update test")

    update_result = mcp_tools._handle_core_task_operations(
        action="update",
        task_id=task_id,
        title="An updated task title",
        status="in_progress",
        description=None,
        priority=None,
        labels=None,
        details=None,
        estimated_effort=None,
        assignees=None,
        due_date=None
    )
    assert update_result["success"]
    assert update_result["action"] == "update"
    assert update_result["task"]["title"] == "An updated task title"
    assert update_result["task"]["status"] == "in_progress"

def test_delete_task_happy_path(mcp_tools):
    """Test deleting an existing task."""
    task_id = create_test_task(mcp_tools, "Task for delete test")

    delete_result = mcp_tools._handle_core_task_operations(
        action="delete",
        task_id=task_id,
        title=None,
        description=None,
        priority=None,
        labels=None,
        status=None,
        details=None,
        estimated_effort=None,
        assignees=None,
        due_date=None
    )
    assert delete_result["success"]
    assert delete_result["action"] == "delete"

    # Verify task is deleted
    get_result = mcp_tools._handle_core_task_operations(
        action="get",
        task_id=task_id,
        title=None,
        description=None,
        priority=None,
        labels=None,
        status=None,
        details=None,
        estimated_effort=None,
        assignees=None,
        due_date=None
    )
    assert not get_result["success"] 