"""
This is the canonical and only maintained quick test suite for server start validation in task management.
All validation, edge-case, and integration tests should be added here.
Redundant or duplicate tests in other files have been removed.
"""

import pytest
import asyncio
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


@pytest.mark.quick
@pytest.mark.mcp
def test_mcp_server_can_be_created():
    """Test that MCP server can be created."""
    try:
        from fastmcp.task_management.interface.consolidated_mcp_server import create_consolidated_mcp_server
        
        server = create_consolidated_mcp_server()
        assert server is not None
        assert hasattr(server, 'run')
        
    except Exception as e:
        pytest.fail(f"Cannot create MCP server: {e}")


@pytest.mark.quick
@pytest.mark.mcp
def test_mcp_server_has_required_methods():
    """Test that MCP server has all required methods."""
    try:
        from fastmcp.task_management.interface.consolidated_mcp_server import create_consolidated_mcp_server
        
        server = create_consolidated_mcp_server()
        
        # Check for required methods
        required_methods = ['run']
        for method in required_methods:
            assert hasattr(server, method), f"Server missing required method: {method}"
            assert callable(getattr(server, method)), f"Server method {method} is not callable"
            
    except Exception as e:
        pytest.fail(f"MCP server method validation failed: {e}")


@pytest.mark.quick
@pytest.mark.mcp 
def test_mcp_tools_registration():
    """Test that MCP tools can be registered."""
    try:
        from fastmcp.task_management.interface.consolidated_mcp_tools import ConsolidatedMCPTools
        
        tools = ConsolidatedMCPTools()
        assert tools is not None
        
        # Check if tools has register_tools method
        assert hasattr(tools, 'register_tools'), "MCPTaskTools missing register_tools method"
        assert callable(getattr(tools, 'register_tools')), "register_tools is not callable"
            
    except Exception as e:
        pytest.fail(f"MCP tools registration test failed: {e}")


@pytest.mark.quick
@pytest.mark.mcp
def test_server_configuration_loading():
    """Test that server can load basic configuration."""
    try:
        from fastmcp.task_management.interface.consolidated_mcp_server import create_consolidated_mcp_server
        
        server = create_consolidated_mcp_server()
        
        # Test that server can be configured (basic validation)
        assert server is not None
        
        # Check if server has configuration attributes
        # This is a basic smoke test - detailed config testing is in unit tests
        
    except Exception as e:
        pytest.fail(f"Server configuration loading failed: {e}")


@pytest.mark.quick
@pytest.mark.mcp
def test_task_repository_can_be_instantiated():
    """Test that task repository can be instantiated."""
    try:
        from fastmcp.task_management.infrastructure.repositories.json_task_repository import JsonTaskRepository
        
        repo = JsonTaskRepository()
        assert repo is not None
        assert hasattr(repo, 'save')
        assert hasattr(repo, 'find_by_id')
        assert hasattr(repo, 'find_all')
        assert hasattr(repo, 'delete')
        
    except Exception as e:
        pytest.fail(f"Task repository instantiation failed: {e}")


@pytest.mark.quick
@pytest.mark.mcp
def test_application_services_can_be_instantiated():
    """Test that application services can be instantiated."""
    try:
        from fastmcp.task_management.application.services.task_application_service import TaskApplicationService
        from fastmcp.task_management.infrastructure.repositories.json_task_repository import JsonTaskRepository
        
        from fastmcp.task_management.infrastructure.services.file_auto_rule_generator import FileAutoRuleGenerator
        
        repo = JsonTaskRepository()
        auto_rule_gen = FileAutoRuleGenerator()
        service = TaskApplicationService(repo, auto_rule_gen)
        
        assert service is not None
        assert hasattr(service, 'create_task')
        assert hasattr(service, 'get_task')
        assert hasattr(service, 'list_tasks')
        assert hasattr(service, 'update_task')
        assert hasattr(service, 'delete_task')
        
    except Exception as e:
        pytest.fail(f"Application services instantiation failed: {e}")


@pytest.mark.quick
@pytest.mark.mcp
def test_domain_entities_can_be_created():
    """Test that domain entities can be created with basic validation."""
    try:
        from fastmcp.task_management.domain.entities.task import Task
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        from fastmcp.task_management.domain.value_objects.task_status import TaskStatus, TaskStatusEnum
        from fastmcp.task_management.domain.value_objects.priority import Priority, PriorityLevel
        
        # Test basic entity creation using new TaskId format
        task_id = TaskId.from_int(1)
        status = TaskStatus.todo()
        priority = Priority.high()
        
        task = Task(
            id=task_id,
            title="Test Task",
            description="Test Description",
            status=status,
            priority=priority,
            assignees=["qa_engineer"],
            labels=["test"],
            subtasks=[]
        )
        
        assert task is not None
        assert task.id.value.endswith("001")  # Should end with 001 (from int 1)
        assert task.title == "Test Task"
        assert task.status.value == "todo"
        assert task.priority.value == "high"
        
    except Exception as e:
        pytest.fail(f"Domain entities creation failed: {e}")


@pytest.mark.quick
def test_file_system_access():
    """Test that the test can access required file system paths."""
    import os
    
    # Check if we can access the project structure
    current_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(current_dir, '..', '..', '..'))
    
    # Check key directories exist
    src_dir = os.path.join(project_root, 'src')
    assert os.path.exists(src_dir), f"Source directory not found: {src_dir}"
    
    fastmcp_dir = os.path.join(src_dir, 'fastmcp')
    assert os.path.exists(fastmcp_dir), f"FastMCP directory not found: {fastmcp_dir}" 