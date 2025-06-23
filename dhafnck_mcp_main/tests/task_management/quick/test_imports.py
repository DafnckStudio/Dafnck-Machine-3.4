"""
Quick Test: Module Import Validation
Task 1.1 - MCP Server Startup Testing (Part 1)
Duration: < 30 seconds
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


import pytest


@pytest.mark.quick
def test_can_import_mcp_server():
    """Test that MCP server module can be imported."""
    try:
        from fastmcp.dhafnck_mcp.interface.ddd_mcp_server import create_mcp_server, main
        from fastmcp.dhafnck_mcp.interface.mcp_tools import MCPTaskTools
        assert create_mcp_server is not None
        assert main is not None
        assert MCPTaskTools is not None
    except ImportError as e:
        pytest.fail(f"Cannot import MCP server modules: {e}")


@pytest.mark.quick  
def test_can_import_domain_entities():
    """Test that domain entities can be imported."""
    try:
        from fastmcp.dhafnck_mcp.domain.entities.task import Task
        from fastmcp.dhafnck_mcp.domain.value_objects.task_id import TaskId
        from fastmcp.dhafnck_mcp.domain.value_objects.task_status import TaskStatus, TaskStatusEnum
        from fastmcp.dhafnck_mcp.domain.value_objects.priority import Priority, PriorityLevel
        
        assert Task is not None
        assert TaskId is not None
        assert TaskStatus is not None
        assert TaskStatusEnum is not None
        assert Priority is not None
        assert PriorityLevel is not None
    except ImportError as e:
        pytest.fail(f"Cannot import domain entities: {e}")


@pytest.mark.quick
def test_can_import_application_services():
    """Test that application services can be imported."""
    try:
        from fastmcp.dhafnck_mcp.application.services.task_application_service import TaskApplicationService
        from fastmcp.dhafnck_mcp.application.use_cases.create_task import CreateTaskUseCase
        from fastmcp.dhafnck_mcp.application.use_cases.get_task import GetTaskUseCase
        from fastmcp.dhafnck_mcp.application.use_cases.list_tasks import ListTasksUseCase
        from fastmcp.dhafnck_mcp.application.use_cases.update_task import UpdateTaskUseCase
        from fastmcp.dhafnck_mcp.application.use_cases.delete_task import DeleteTaskUseCase
        from fastmcp.dhafnck_mcp.application.use_cases.search_tasks import SearchTasksUseCase
        
        assert TaskApplicationService is not None
        assert CreateTaskUseCase is not None
        assert GetTaskUseCase is not None
        assert ListTasksUseCase is not None
        assert UpdateTaskUseCase is not None
        assert DeleteTaskUseCase is not None
        assert SearchTasksUseCase is not None
    except ImportError as e:
        pytest.fail(f"Cannot import application services: {e}")


@pytest.mark.quick
def test_can_import_infrastructure():
    """Test that infrastructure components can be imported."""
    try:
        from fastmcp.dhafnck_mcp.infrastructure.repositories.json_task_repository import JsonTaskRepository
        from fastmcp.dhafnck_mcp.infrastructure.services.file_auto_rule_generator import FileAutoRuleGenerator
        
        assert JsonTaskRepository is not None
        assert FileAutoRuleGenerator is not None
    except ImportError as e:
        pytest.fail(f"Cannot import infrastructure components: {e}")


@pytest.mark.quick
def test_can_import_mcp_tools():
    """Test that MCP tools can be imported."""
    try:
        from fastmcp.dhafnck_mcp.interface.mcp_tools import MCPTaskTools
        
        assert MCPTaskTools is not None
    except ImportError as e:
        pytest.fail(f"Cannot import MCP tools: {e}")


@pytest.mark.quick
def test_can_import_events():
    """Test that domain events can be imported."""
    try:
        from fastmcp.dhafnck_mcp.domain.events.task_events import TaskCreated, TaskUpdated, TaskRetrieved, TaskDeleted
        
        assert TaskCreated is not None
        assert TaskUpdated is not None
        assert TaskRetrieved is not None
        assert TaskDeleted is not None
    except ImportError as e:
        pytest.fail(f"Cannot import domain events: {e}")


@pytest.mark.quick
def test_can_import_exceptions():
    """Test that domain exceptions can be imported."""
    try:
        from fastmcp.dhafnck_mcp.domain.exceptions.task_exceptions import TaskNotFoundError, InvalidTaskStateError, InvalidTaskTransitionError
        
        assert TaskNotFoundError is not None
        assert InvalidTaskStateError is not None
        assert InvalidTaskTransitionError is not None
    except ImportError as e:
        pytest.fail(f"Cannot import domain exceptions: {e}")


@pytest.mark.quick
def test_python_path_setup():
    """Test that Python path is correctly configured."""
    import sys
    import os
    
    # Check if src directory is in path
    src_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src')
    src_path = os.path.abspath(src_path)
    
    # This test ensures the imports above will work
    assert any(src_path in path for path in sys.path) or os.path.exists(src_path) 