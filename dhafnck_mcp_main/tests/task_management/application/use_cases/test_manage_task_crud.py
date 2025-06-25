"""
This is the canonical and only maintained test suite for the MCP task CRUD tool interface.
All validation, edge-case, and integration tests should be added here.
Redundant or duplicate tests in other files have been removed.
"""

import pytest
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from fastmcp.task_management.interface.consolidated_mcp_tools import ConsolidatedMCPTools

@pytest.fixture
def mcp_tools(temp_tasks_file):
    """Fixture to provide an instance of ConsolidatedMCPTools with temporary task file."""
    from fastmcp.task_management.infrastructure.repositories.json_task_repository import JsonTaskRepository
    from fastmcp.task_management.application.services.task_application_service import TaskApplicationService
    from fastmcp.task_management.application.use_cases.create_task import CreateTaskUseCase
    from fastmcp.task_management.application.use_cases.get_task import GetTaskUseCase
    from fastmcp.task_management.application.use_cases.update_task import UpdateTaskUseCase
    from fastmcp.task_management.application.use_cases.delete_task import DeleteTaskUseCase
    from fastmcp.task_management.application.use_cases.list_tasks import ListTasksUseCase
    from fastmcp.task_management.application.use_cases.complete_task import CompleteTaskUseCase
    from fastmcp.task_management.infrastructure.services.file_auto_rule_generator import FileAutoRuleGenerator
    
    # Create repository with temporary file
    repository = JsonTaskRepository(str(temp_tasks_file))
    
    # Create tools with custom dependencies (it creates TaskApplicationService internally)
    tools = ConsolidatedMCPTools(
        task_repository=repository
    )
    
    return tools

def create_test_task(mcp_tools, title="A test task"):
    """Helper function to create a task for testing."""
    # First, create the project
    project_result = mcp_tools._project_manager.create_project(
        project_id="default_project",
        name="Test Project",
        description="Project for testing tasks"
    )
    if not project_result["success"]:
        # Project might already exist, which is fine
        pass
    
    # Then create the task tree
    tree_result = mcp_tools._project_manager.create_task_tree(
        project_id="default_project",
        tree_id="main",
        tree_name="Main Task Tree",
        tree_description="Main task tree for testing"
    )
    if not tree_result["success"]:
        # Task tree might already exist, which is fine
        pass
    
    # Now create the task
    result = mcp_tools._task_handler.handle_core_operations(
        action="create",
        project_id="default_project",
        task_tree_id="main", 
        user_id="default_id",
        task_id=None,
        title=title,
        description="This is a test task.",
        status=None,
        priority="high",
        details=None,
        estimated_effort=None,
        assignees=None,
        labels=["testing"],
        due_date=None
    )
    assert result["success"]
    return result["task"]["id"]

def test_create_task_happy_path(mcp_tools):
    """Test successful creation of a task."""
    # First, create the project
    project_result = mcp_tools._project_manager.create_project(
        project_id="default_project",
        name="Test Project",
        description="Project for testing tasks"
    )
    assert project_result["success"]
    
    # Then create the task tree
    tree_result = mcp_tools._project_manager.create_task_tree(
        project_id="default_project",
        tree_id="main",
        tree_name="Main Task Tree",
        tree_description="Main task tree for testing"
    )
    assert tree_result["success"]
    
    # Now create the task
    result = mcp_tools._task_handler.handle_core_operations(
        action="create",
        project_id="default_project",
        task_tree_id="main",
        user_id="default_id", 
        task_id=None,
        title="A new task",
        description="This is a test task.",
        status=None,
        priority="high",
        details=None,
        estimated_effort=None,
        assignees=None,
        labels=["testing", "happy-path"],
        due_date=None
    )
    assert result["success"]
    assert result["action"] == "create"
    assert result["task"]["title"] == "A new task"

def test_get_task_happy_path(mcp_tools):
    """Test fetching an existing task."""
    task_id = create_test_task(mcp_tools, "Task for get test")
    
    result = mcp_tools._task_handler.handle_core_operations(
        action="get",
        project_id="default_project",
        task_tree_id="main",
        user_id="default_id",
        task_id=task_id,
        title=None,
        description=None,
        status=None,
        priority=None,
        details=None,
        estimated_effort=None,
        assignees=None,
        labels=None,
        due_date=None
    )
    assert result["success"]
    assert result["action"] == "get"
    assert result["task"]["id"] == task_id

def test_update_task_happy_path(mcp_tools):
    """Test updating an existing task."""
    task_id = create_test_task(mcp_tools, "Task for update test")

    update_result = mcp_tools._task_handler.handle_core_operations(
        action="update",
        project_id="default_project",
        task_tree_id="main",
        user_id="default_id",
        task_id=task_id,
        title="An updated task title",
        description=None,
        status="in_progress",
        priority=None,
        details=None,
        estimated_effort=None,
        assignees=None,
        labels=None,
        due_date=None
    )
    assert update_result["success"]
    assert update_result["action"] == "update"
    assert update_result["task"]["title"] == "An updated task title"
    assert update_result["task"]["status"] == "in_progress"

def test_delete_task_happy_path(mcp_tools):
    """Test deleting an existing task."""
    task_id = create_test_task(mcp_tools, "Task for delete test")

    delete_result = mcp_tools._task_handler.handle_core_operations(
        action="delete",
        project_id="default_project",
        task_tree_id="main",
        user_id="default_id",
        task_id=task_id,
        title=None,
        description=None,
        status=None,
        priority=None,
        details=None,
        estimated_effort=None,
        assignees=None,
        labels=None,
        due_date=None
    )
    assert delete_result["success"]
    assert delete_result["action"] == "delete"

    # Verify task is deleted
    get_result = mcp_tools._task_handler.handle_core_operations(
        action="get",
        project_id="default_project",
        task_tree_id="main",
        user_id="default_id",
        task_id=task_id,
        title=None,
        description=None,
        status=None,
        priority=None,
        details=None,
        estimated_effort=None,
        assignees=None,
        labels=None,
        due_date=None
    )
    assert not get_result["success"] 