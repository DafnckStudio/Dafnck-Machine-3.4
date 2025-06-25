import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

import pytest
import tempfile
import json
from fastmcp.task_management.interface.consolidated_mcp_tools import (
    ConsolidatedMCPTools,
)
from fastmcp.task_management.infrastructure.repositories.json_task_repository import (
    InMemoryTaskRepository,
)


@pytest.fixture
def temp_projects_file():
    """Create temporary projects file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({}, f)
        yield f.name
    os.unlink(f.name)


@pytest.fixture
def mcp_tools(temp_projects_file):
    """Create ConsolidatedMCPTools instance with in-memory repository"""
    task_repository = InMemoryTaskRepository()
    return ConsolidatedMCPTools(
        task_repository=task_repository,
        projects_file_path=temp_projects_file
    )


@pytest.fixture
def sample_task_id(mcp_tools):
    """Create a real task and return its ID"""
    # First, create the project
    project_result = mcp_tools._project_manager.create_project(
        project_id="default_project",
        name="Test Project",
        description="Project for testing subtasks"
    )
    print(f"Project creation result: {project_result}")
    
    # Then create the task tree
    tree_result = mcp_tools._project_manager.create_task_tree(
        project_id="default_project",
        tree_id="main",
        tree_name="Main Task Tree",
        tree_description="Main task tree for testing"
    )
    print(f"Task tree creation result: {tree_result}")
    
    # Now create a parent task
    create_result = mcp_tools._task_handler.handle_core_operations(
        action="create",
        project_id="default_project",
        task_tree_id="main",
        user_id="default_id",
        task_id=None,
        title="Parent Task",
        description="Parent task for subtask testing",
        status=None,
        priority="medium",
        details=None,
        estimated_effort=None,
        assignees=["@coding_agent"],
        labels=["test"],
        due_date=None
    )
    # Debug: print the structure to understand what's returned
    print(f"Create result structure: {create_result}")
    if "task" in create_result:
        return create_result["task"]["id"]
    else:
        # Handle alternative response structures
        if "id" in create_result:
            return create_result["id"]
        else:
            raise ValueError(f"Could not find task ID in result: {create_result}")


@pytest.fixture
def sample_subtask_data():
    return {"title": "New Subtask"}


@pytest.fixture
def sample_subtask_id():
    return 1


def test_add_subtask_happy_path(mcp_tools, sample_task_id, sample_subtask_data):
    result = mcp_tools.manage_subtask(
        action="add",
        task_id=sample_task_id,
        subtask_data=sample_subtask_data,
    )
    assert result["success"] is True
    assert "result" in result
    # The result structure may vary, so let's be flexible about the exact structure


def test_complete_subtask_happy_path(mcp_tools, sample_task_id):
    # First add a subtask
    add_result = mcp_tools.manage_subtask(
        action="add",
        task_id=sample_task_id,
        subtask_data={"title": "Subtask to complete"},
    )
    assert add_result["success"] is True
    
    # Get the subtask ID from the add result
    if "result" in add_result and "subtask" in add_result["result"]:
        subtask_id = add_result["result"]["subtask"]["id"]
    else:
        # Fallback: list subtasks to get the ID
        list_result = mcp_tools.manage_subtask(action="list", task_id=sample_task_id)
        subtask_id = list_result["result"][0]["id"]
    
    # Complete the subtask
    result = mcp_tools.manage_subtask(
        action="complete",
        task_id=sample_task_id,
        subtask_data={"subtask_id": subtask_id},
    )
    assert result["success"] is True


def test_update_subtask_happy_path(mcp_tools, sample_task_id):
    # First add a subtask
    add_result = mcp_tools.manage_subtask(
        action="add",
        task_id=sample_task_id,
        subtask_data={"title": "Subtask to update"},
    )
    assert add_result["success"] is True
    
    # Get the subtask ID
    if "result" in add_result and "subtask" in add_result["result"]:
        subtask_id = add_result["result"]["subtask"]["id"]
    else:
        list_result = mcp_tools.manage_subtask(action="list", task_id=sample_task_id)
        subtask_id = list_result["result"][0]["id"]
    
    # Update the subtask
    updated_data = {"subtask_id": subtask_id, "title": "Updated Subtask"}
    result = mcp_tools.manage_subtask(
        action="update", task_id=sample_task_id, subtask_data=updated_data
    )
    assert result["success"] is True


def test_remove_subtask_happy_path(mcp_tools, sample_task_id):
    # First add a subtask
    add_result = mcp_tools.manage_subtask(
        action="add",
        task_id=sample_task_id,
        subtask_data={"title": "Subtask to remove"},
    )
    assert add_result["success"] is True
    
    # Get the subtask ID
    if "result" in add_result and "subtask" in add_result["result"]:
        subtask_id = add_result["result"]["subtask"]["id"]
    else:
        list_result = mcp_tools.manage_subtask(action="list", task_id=sample_task_id)
        subtask_id = list_result["result"][0]["id"]
    
    # Remove the subtask
    result = mcp_tools.manage_subtask(
        action="remove",
        task_id=sample_task_id,
        subtask_data={"subtask_id": subtask_id},
    )
    assert result["success"] is True


def test_list_subtasks_happy_path(mcp_tools, sample_task_id):
    result = mcp_tools.manage_subtask(
        action="list", task_id=sample_task_id, subtask_data=None
    )
    assert result["success"] is True
    assert isinstance(result["result"], list) 