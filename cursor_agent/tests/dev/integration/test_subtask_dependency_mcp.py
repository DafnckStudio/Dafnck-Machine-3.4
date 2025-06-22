"""Integration Tests for Subtask and Dependency MCP Tools"""

import pytest
import tempfile
import os
from pathlib import Path
from task_mcp.interface.mcp_tools import MCPTaskTools
from task_mcp.infrastructure.repositories.json_task_repository import JsonTaskRepository
from task_mcp.domain import TaskId


@pytest.mark.integration
class TestSubtaskDependencyMCPIntegration:
    """Integration tests for subtask and dependency MCP tools"""
    
    def setup_method(self):
        """Set up test fixtures"""
        # Create temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.write('{"tasks": []}')
        self.temp_file.close()
        
        # Initialize MCP tools with temporary repository
        self.mcp_tools = MCPTaskTools()
        self.mcp_tools._task_repository = JsonTaskRepository(self.temp_file.name)
        
        # Recreate the task service with the new repository
        from task_mcp.application.services.task_application_service import TaskApplicationService
        from task_mcp.infrastructure.services.file_auto_rule_generator import FileAutoRuleGenerator
        
        auto_rule_generator = FileAutoRuleGenerator()
        self.mcp_tools._task_service = TaskApplicationService(
            self.mcp_tools._task_repository,
            auto_rule_generator
        )
        
        # Create test tasks using proper DTOs
        from task_mcp.application.dtos.task_dto import CreateTaskRequest
        
        task1_request = CreateTaskRequest(
            title="Test Task 1",
            description="First test task"
        )
        task2_request = CreateTaskRequest(
            title="Test Task 2",
            description="Second test task"
        )
        
        self.task1_response = self.mcp_tools._task_service.create_task(task1_request)
        self.task2_response = self.mcp_tools._task_service.create_task(task2_request)
        
        self.task1_id = self.task1_response.id
        self.task2_id = self.task2_response.id
    
    def teardown_method(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_add_subtask_mcp_tool(self):
        """Test add_subtask MCP tool"""
        # Simulate MCP tool call
        result = {
            "task_id": self.task1_id,
            "title": "Test Subtask",
            "description": "Test subtask description"
        }
        
        # Call the actual use case (simulating MCP tool behavior)
        from task_mcp.application.use_cases.manage_subtasks import AddSubtaskRequest
        request = AddSubtaskRequest(**result)
        response = self.mcp_tools._task_service.add_subtask(request)
        
        assert response.task_id == self.task1_id
        assert response.subtask["title"] == "Test Subtask"
        assert response.subtask["description"] == "Test subtask description"
        assert response.subtask["completed"] is False
        assert response.progress["total"] == 1
        assert response.progress["completed"] == 0
    
    def test_subtask_workflow_integration(self):
        """Test complete subtask workflow through MCP tools"""
        # Add subtask
        from task_mcp.application.use_cases.manage_subtasks import AddSubtaskRequest
        add_request = AddSubtaskRequest(
            task_id=self.task1_id,
            title="Integration Test Subtask",
            description="Test description"
        )
        add_response = self.mcp_tools._task_service.add_subtask(add_request)
        subtask_id = add_response.subtask["id"]
        
        # Update subtask
        from task_mcp.application.use_cases.manage_subtasks import UpdateSubtaskRequest
        update_request = UpdateSubtaskRequest(
            task_id=self.task1_id,
            subtask_id=subtask_id,
            title="Updated Subtask Title",
            completed=True
        )
        update_response = self.mcp_tools._task_service.update_subtask(update_request)
        
        assert update_response.subtask["title"] == "Updated Subtask Title"
        assert update_response.subtask["completed"] is True
        assert update_response.progress["completed"] == 1
        assert update_response.progress["percentage"] == 100.0
        
        # Get all subtasks
        get_response = self.mcp_tools._task_service.get_subtasks(self.task1_id)
        
        assert len(get_response["subtasks"]) == 1
        assert get_response["progress"]["total"] == 1
        assert get_response["progress"]["completed"] == 1
        
        # Remove subtask
        remove_response = self.mcp_tools._task_service.remove_subtask(self.task1_id, subtask_id)
        
        assert remove_response["success"] is True
        assert remove_response["progress"]["total"] == 0
    
    def test_add_dependency_mcp_tool(self):
        """Test add_dependency MCP tool"""
        # Call the dependency use case
        from task_mcp.application.use_cases.manage_dependencies import AddDependencyRequest
        request = AddDependencyRequest(
            task_id=self.task1_id,
            dependency_id=self.task2_id
        )
        response = self.mcp_tools._task_service.add_dependency(request)
        
        assert response.success is True
        assert response.task_id == self.task1_id
        assert self.task2_id in response.dependencies
        assert "added successfully" in response.message
    
    def test_dependency_workflow_integration(self):
        """Test complete dependency workflow through MCP tools"""
        # Add dependency
        from task_mcp.application.use_cases.manage_dependencies import AddDependencyRequest
        add_request = AddDependencyRequest(
            task_id=self.task1_id,
            dependency_id=self.task2_id
        )
        add_response = self.mcp_tools._task_service.add_dependency(add_request)
        
        assert add_response.success is True
        assert self.task2_id in add_response.dependencies
        
        # Get dependencies
        get_response = self.mcp_tools._task_service.get_dependencies(self.task1_id)
        
        assert self.task2_id in get_response["dependency_ids"]
        assert len(get_response["dependencies"]) == 1
        
        dependency_detail = get_response["dependencies"][0]
        assert dependency_detail["id"] == self.task2_id
        assert dependency_detail["title"] == "Test Task 2"
        
        # Get blocking tasks (reverse dependencies)
        blocking_response = self.mcp_tools._task_service.get_blocking_tasks(self.task2_id)
        
        assert blocking_response["task_id"] == self.task2_id
        assert blocking_response["blocking_count"] == 1
        
        blocking_task = blocking_response["blocking_tasks"][0]
        assert blocking_task["id"] == self.task1_id
        assert blocking_task["title"] == "Test Task 1"
        
        # Remove dependency
        remove_response = self.mcp_tools._task_service.remove_dependency(self.task1_id, self.task2_id)
        
        assert remove_response.success is True
        assert self.task2_id not in remove_response.dependencies
        
        # Verify dependency removed
        final_get_response = self.mcp_tools._task_service.get_dependencies(self.task1_id)
        assert len(final_get_response["dependency_ids"]) == 0
    
    def test_mixed_subtasks_and_dependencies(self):
        """Test tasks with both subtasks and dependencies"""
        # Add dependency
        from task_mcp.application.use_cases.manage_dependencies import AddDependencyRequest
        dep_request = AddDependencyRequest(
            task_id=self.task1_id,
            dependency_id=self.task2_id
        )
        self.mcp_tools._task_service.add_dependency(dep_request)
        
        # Add subtasks
        from task_mcp.application.use_cases.manage_subtasks import AddSubtaskRequest
        subtask1_request = AddSubtaskRequest(
            task_id=self.task1_id,
            title="Subtask 1"
        )
        subtask2_request = AddSubtaskRequest(
            task_id=self.task1_id,
            title="Subtask 2"
        )
        
        subtask1_response = self.mcp_tools._task_service.add_subtask(subtask1_request)
        subtask2_response = self.mcp_tools._task_service.add_subtask(subtask2_request)
        
        # Complete one subtask
        self.mcp_tools._task_service.complete_subtask(
            self.task1_id, 
            subtask1_response.subtask["id"]
        )
        
        # Verify task has both dependencies and subtasks
        task_response = self.mcp_tools._task_service.get_task(self.task1_id)
        
        assert len(task_response.dependencies) == 1
        assert len(task_response.subtasks) == 2
        
        # Check subtask progress
        subtask_response = self.mcp_tools._task_service.get_subtasks(self.task1_id)
        assert subtask_response["progress"]["total"] == 2
        assert subtask_response["progress"]["completed"] == 1
        assert subtask_response["progress"]["percentage"] == 50.0
        
        # Check dependencies
        dep_response = self.mcp_tools._task_service.get_dependencies(self.task1_id)
        assert len(dep_response["dependency_ids"]) == 1
        assert self.task2_id in dep_response["dependency_ids"]
    
    def test_persistence_across_operations(self):
        """Test that subtasks and dependencies persist across repository operations"""
        # Add subtask and dependency
        from task_mcp.application.use_cases.manage_subtasks import AddSubtaskRequest
        from task_mcp.application.use_cases.manage_dependencies import AddDependencyRequest
        
        subtask_request = AddSubtaskRequest(
            task_id=self.task1_id,
            title="Persistent Subtask"
        )
        dep_request = AddDependencyRequest(
            task_id=self.task1_id,
            dependency_id=self.task2_id
        )
        
        subtask_response = self.mcp_tools._task_service.add_subtask(subtask_request)
        self.mcp_tools._task_service.add_dependency(dep_request)
        
        # Create new repository instance with same file
        new_repository = JsonTaskRepository(self.temp_file.name)
        
        # Verify data persisted
        reloaded_task = new_repository.find_by_id(
            TaskId.from_string(self.task1_id)
        )
        
        assert len(reloaded_task.subtasks) == 1
        assert reloaded_task.subtasks[0]["title"] == "Persistent Subtask"
        assert len(reloaded_task.dependencies) == 1
        assert reloaded_task.get_dependency_ids() == [self.task2_id]
    
    def test_error_handling_integration(self):
        """Test error handling in MCP tools integration"""
        # Test adding subtask to non-existent task
        from task_mcp.application.use_cases.manage_subtasks import AddSubtaskRequest
        invalid_request = AddSubtaskRequest(
            task_id=999,
            title="Invalid Subtask"
        )
        
        with pytest.raises(Exception):  # Should raise TaskNotFoundError
            self.mcp_tools._task_service.add_subtask(invalid_request)
        
        # Test adding dependency to non-existent task
        from task_mcp.application.use_cases.manage_dependencies import AddDependencyRequest
        invalid_dep_request = AddDependencyRequest(
            task_id=999,
            dependency_id=self.task2_id
        )
        
        with pytest.raises(Exception):  # Should raise TaskNotFoundError
            self.mcp_tools._task_service.add_dependency(invalid_dep_request) 