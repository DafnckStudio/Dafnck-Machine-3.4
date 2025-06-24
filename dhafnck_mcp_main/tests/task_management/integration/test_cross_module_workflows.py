"""
This is the canonical and only maintained test suite for cross-module workflow integration tests in task management.
All validation, edge-case, and integration tests should be added here.
Redundant or duplicate tests in other files have been removed.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


import pytest
from fastmcp.task_management.interface.consolidated_mcp_tools import (
    ConsolidatedMCPTools,
)

@pytest.fixture(scope="module")
def mcp_tools():
    return ConsolidatedMCPTools()

def test_project_task_workflow(mcp_tools):
    # 1. Create a project
    project_id = "workflow_proj"
    create_project_result = mcp_tools._multi_agent_tools.create_project(
        project_id=project_id, name="Workflow Test Project"
    )
    assert create_project_result["success"] is True

    # 2. Create a task
    task_title = "Workflow Task"
    create_task_result = mcp_tools._handle_core_task_operations(
        action="create",
        title=task_title,
        description="A task for workflow testing",
        status="todo",
        priority="high",
        assignees=["@coding_agent"],
        labels=["workflow"],
        task_id=None,
        details=None,
        estimated_effort=None,
        due_date=None,
        project_id=project_id,
    )
    assert create_task_result["success"] is True
    task_id = create_task_result["task"]["id"]

    # 3. Get the task
    get_task_result = mcp_tools._handle_core_task_operations(
        action="get", task_id=task_id,
        title=None,
        description=None,
        status=None,
        priority=None,
        assignees=None,
        labels=None,
        details=None,
        estimated_effort=None,
        due_date=None,
        project_id=None,
    )
    assert get_task_result["success"] is True
    assert get_task_result["task"]["title"] == task_title

    # 4. Update the task
    updated_title = "Updated Workflow Task"
    update_task_result = mcp_tools._handle_core_task_operations(
        action="update",
        task_id=task_id,
        title=updated_title,
        description=None,
        status=None,
        priority=None,
        assignees=None,
        labels=None,
        details=None,
        estimated_effort=None,
        due_date=None,
        project_id=None,
    )
    assert update_task_result["success"] is True
    assert update_task_result["task"]["title"] == updated_title

    # 5. Delete the task
    delete_task_result = mcp_tools._handle_core_task_operations(
        action="delete", task_id=task_id,
        title=None,
        description=None,
        status=None,
        priority=None,
        assignees=None,
        labels=None,
        details=None,
        estimated_effort=None,
        due_date=None,
        project_id=None,
    )
    assert delete_task_result["success"] is True

    # Verify deletion
    get_deleted_task_result = mcp_tools._handle_core_task_operations(
        action="get", task_id=task_id,
        title=None,
        description=None,
        status=None,
        priority=None,
        assignees=None,
        labels=None,
        details=None,
        estimated_effort=None,
        due_date=None,
        project_id=None,
    )
    assert get_deleted_task_result["success"] is False 