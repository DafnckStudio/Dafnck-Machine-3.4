"""Edge case tests for use cases to improve coverage from 80-95% to 95%+"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from fastmcp.dhafnck_mcp.application.use_cases.complete_task import CompleteTaskUseCase
from fastmcp.dhafnck_mcp.application.use_cases.create_task import CreateTaskUseCase
from fastmcp.dhafnck_mcp.application.use_cases.delete_task import DeleteTaskUseCase
from fastmcp.dhafnck_mcp.application.use_cases.list_tasks import ListTasksUseCase
from fastmcp.dhafnck_mcp.application.use_cases.update_task import UpdateTaskUseCase
from fastmcp.dhafnck_mcp.application.use_cases.manage_subtasks import ManageSubtasksUseCase, AddSubtaskRequest, UpdateSubtaskRequest
from fastmcp.dhafnck_mcp.application.dtos.task_dto import CreateTaskRequest, UpdateTaskRequest, ListTasksRequest, TaskResponse, UpdateTaskResponse
from fastmcp.dhafnck_mcp.domain.exceptions.task_exceptions import TaskNotFoundError
from fastmcp.dhafnck_mcp.domain.entities.task import Task
from fastmcp.dhafnck_mcp.domain.value_objects.task_id import TaskId
from fastmcp.dhafnck_mcp.domain.value_objects.task_status import TaskStatus
from fastmcp.dhafnck_mcp.domain.value_objects.priority import Priority


class TestCompleteTaskEdgeCases:
    """Edge cases for CompleteTaskUseCase to improve coverage from 87% to 95%+"""

    @pytest.fixture
    def mock_repository(self):
        return Mock()

    @pytest.fixture
    def mock_auto_rule_generator(self):
        return Mock()

    @pytest.fixture
    def complete_task_use_case(self, mock_repository):
        return CompleteTaskUseCase(mock_repository)

    def test_complete_task_with_subtasks_completion(self, complete_task_use_case, mock_repository):
        """Test completing task that has subtasks - should complete all subtasks"""
        # Create a task with subtasks
        task = Task.create(
            id=TaskId.generate(),
            title="Parent Task",
            description="Task with subtasks"
        )
        
        # Add subtasks
        task.add_subtask({"title": "Subtask 1", "description": "First subtask"})
        task.add_subtask({"title": "Subtask 2", "description": "Second subtask"})
        
        mock_repository.find_by_id.return_value = task
        mock_repository.save.return_value = None
        
        # Complete the task
        result = complete_task_use_case.execute(str(task.id))
        
        # Verify task is completed
        assert result["success"] is True
        assert task.status.is_done()
        
        # Verify all subtasks are completed
        for subtask in task.subtasks:
            assert subtask["completed"] is True
        
        mock_repository.save.assert_called_once_with(task)

    def test_complete_task_already_completed(self, complete_task_use_case, mock_repository):
        """Test completing a task that's already completed"""
        task = Task.create(
            id=TaskId.generate(),
            title="Already Completed",
            description="This task is already done"
        )
        task.complete_task()  # Already completed
        
        mock_repository.find_by_id.return_value = task
        
        result = complete_task_use_case.execute(str(task.id))
        
        assert result["success"] is False
        assert "already completed" in result["message"]
        # Should not save if already completed
        mock_repository.save.assert_not_called()

    def test_complete_task_not_found_error_handling(self, complete_task_use_case, mock_repository):
        """Test error handling when task is not found"""
        mock_repository.find_by_id.side_effect = TaskNotFoundError("Task not found")
        
        with pytest.raises(TaskNotFoundError):
            complete_task_use_case.execute("20250101001")

    def test_complete_task_repository_save_error(self, complete_task_use_case, mock_repository):
        """Test error handling when repository save fails"""
        task = Task.create(
            id=TaskId.generate(),
            title="Test Task",
            description="Test"
        )
        
        mock_repository.find_by_id.return_value = task
        mock_repository.save.side_effect = Exception("Database error")
        
        with pytest.raises(Exception, match="Database error"):
            complete_task_use_case.execute(str(task.id))


class TestCreateTaskEdgeCases:
    """Edge cases for CreateTaskUseCase to improve coverage from 88% to 95%+"""

    @pytest.fixture
    def mock_repository(self):
        return Mock()

    @pytest.fixture
    def mock_auto_rule_generator(self):
        return Mock()

    @pytest.fixture
    def create_task_use_case(self, mock_repository, mock_auto_rule_generator):
        return CreateTaskUseCase(mock_repository, mock_auto_rule_generator)

    def test_create_task_with_invalid_priority(self, create_task_use_case):
        """Test creating task with invalid priority value"""
        request = CreateTaskRequest(
            title="Test Task",
            description="Test description",
            priority="invalid_priority"  # Invalid priority
        )
        
        # Should handle invalid priority gracefully
        with pytest.raises(ValueError):
            create_task_use_case.execute(request)

    def test_create_task_with_invalid_estimated_effort(self, create_task_use_case, mock_repository):
        """Test creating task with invalid estimated effort"""
        mock_repository.get_next_id.return_value = TaskId.generate()
        
        request = CreateTaskRequest(
            title="Test Task",
            description="Test description",
            estimated_effort="invalid_effort"  # Invalid effort
        )
        
        # Should handle invalid effort gracefully (just store as string)
        result = create_task_use_case.execute(request)
        assert result is not None
        assert result.task.title == "Test Task"

    def test_create_task_repository_save_failure(self, create_task_use_case, mock_repository):
        """Test handling repository save failure during task creation"""
        request = CreateTaskRequest(
            title="Test Task",
            description="Test description"
        )
        
        mock_repository.get_next_id.return_value = TaskId.generate()
        mock_repository.save.side_effect = Exception("Database connection failed")
        
        result = create_task_use_case.execute(request)
        
        assert result.success is False
        assert "Failed to create task: Database connection failed" in str(result.message)


class TestDeleteTaskEdgeCases:
    """Edge cases for DeleteTaskUseCase to improve coverage from 95% to 100%"""

    @pytest.fixture
    def mock_repository(self):
        return Mock()

    @pytest.fixture
    def delete_task_use_case(self, mock_repository):
        return DeleteTaskUseCase(mock_repository)

    def test_delete_task_repository_error(self, delete_task_use_case, mock_repository):
        """Test handling repository error during deletion"""
        mock_repository.delete.side_effect = Exception("Database error during deletion")
        
        with pytest.raises(Exception, match="Database error during deletion"):
            delete_task_use_case.execute("20250101001")


class TestListTasksEdgeCases:
    """Edge cases for ListTasksUseCase to improve coverage from 95% to 100%"""

    @pytest.fixture
    def mock_repository(self):
        return Mock()

    @pytest.fixture
    def list_tasks_use_case(self, mock_repository):
        return ListTasksUseCase(mock_repository)

    def test_list_tasks_repository_error(self, list_tasks_use_case, mock_repository):
        """Test handling repository error during listing"""
        request = ListTasksRequest()
        mock_repository.find_by_criteria.side_effect = Exception("Database connection error")
        
        with pytest.raises(Exception, match="Database connection error"):
            list_tasks_use_case.execute(request)


class TestUpdateTaskEdgeCases:
    """Edge cases for UpdateTaskUseCase to improve coverage from 83% to 95%+"""

    @pytest.fixture
    def mock_repository(self):
        return Mock()

    @pytest.fixture
    def mock_auto_rule_generator(self):
        return Mock()

    @pytest.fixture
    def update_task_use_case(self, mock_repository, mock_auto_rule_generator):
        return UpdateTaskUseCase(mock_repository, mock_auto_rule_generator)

    def test_update_task_invalid_status(self, update_task_use_case, mock_repository):
        """Test updating task with invalid status"""
        task = Task.create(
            id=TaskId.generate(),
            title="Test Task",
            description="Test"
        )
        
        mock_repository.find_by_id.return_value = task
        
        request = UpdateTaskRequest(
            task_id=str(task.id),
            status="invalid_status"  # Invalid status
        )
        
        with pytest.raises(ValueError):
            update_task_use_case.execute(request)

    def test_update_task_invalid_priority(self, update_task_use_case, mock_repository):
        """Test updating task with invalid priority"""
        task = Task.create(
            id=TaskId.generate(),
            title="Test Task",
            description="Test"
        )
        
        mock_repository.find_by_id.return_value = task
        
        request = UpdateTaskRequest(
            task_id=str(task.id),
            priority="invalid_priority"  # Invalid priority
        )
        
        with pytest.raises(ValueError):
            update_task_use_case.execute(request)

    def test_update_task_invalid_estimated_effort(self, update_task_use_case, mock_repository):
        """Test updating task with invalid estimated effort - should use default"""
        task = Task.create(
            id=TaskId.generate(),
            title="Test Task",
            description="Test"
        )
        
        mock_repository.find_by_id.return_value = task
        mock_repository.save.return_value = None
        
        request = UpdateTaskRequest(
            task_id=str(task.id),
            estimated_effort="invalid_effort"  # Invalid effort
        )
        
        # Should succeed and use default "medium" effort
        result = update_task_use_case.execute(request)
        assert isinstance(result, UpdateTaskResponse)
        assert result.success is True
        assert result.task.estimated_effort == "medium"

    def test_update_task_empty_assignees_list(self, update_task_use_case, mock_repository):
        """Test updating task with empty assignees list"""
        task = Task.create(
            id=TaskId.generate(),
            title="Test Task",
            description="Test"
        )
        
        mock_repository.find_by_id.return_value = task
        mock_repository.save.return_value = None
        
        request = UpdateTaskRequest(
            task_id=str(task.id),
            assignees=[]  # Empty list
        )
        
        result = update_task_use_case.execute(request)
        assert isinstance(result, UpdateTaskResponse)
        assert result.success is True
        assert result.task.assignees == []

    def test_update_task_empty_labels_list(self, update_task_use_case, mock_repository):
        """Test updating task with empty labels list"""
        task = Task.create(
            id=TaskId.generate(),
            title="Test Task",
            description="Test"
        )
        
        mock_repository.find_by_id.return_value = task
        mock_repository.save.return_value = None
        
        request = UpdateTaskRequest(
            task_id=str(task.id),
            labels=[]  # Empty list
        )
        
        result = update_task_use_case.execute(request)
        assert isinstance(result, UpdateTaskResponse)
        assert result.success is True
        assert result.task.labels == []

    def test_update_task_repository_save_error(self, update_task_use_case, mock_repository):
        """Test handling repository save error during update"""
        task = Task.create(
            id=TaskId.generate(),
            title="Test Task",
            description="Test"
        )
        
        mock_repository.find_by_id.return_value = task
        mock_repository.save.side_effect = Exception("Save failed")
        
        request = UpdateTaskRequest(
            task_id=str(task.id),
            title="Updated Title"
        )
        
        with pytest.raises(Exception, match="Save failed"):
            update_task_use_case.execute(request)

    def test_update_task_auto_rule_generation_error(self, update_task_use_case, mock_repository, mock_auto_rule_generator):
        """Test handling auto rule generation error during update"""
        task = Task.create(
            id=TaskId.generate(),
            title="Test Task",
            description="Test"
        )
        
        mock_repository.find_by_id.return_value = task
        mock_repository.save.return_value = None
        mock_auto_rule_generator.generate_rules_for_task.side_effect = Exception("Rule generation failed")
        
        request = UpdateTaskRequest(
            task_id=str(task.id),
            title="Updated Title"
        )
        
        # Should complete successfully even if rule generation fails
        result = update_task_use_case.execute(request)
        assert isinstance(result, UpdateTaskResponse)
        assert result.success is True
        assert result.task.title == "Updated Title"


class TestManageSubtasksEdgeCases:
    """Edge cases for ManageSubtasksUseCase to improve coverage from 80% to 95%+"""

    @pytest.fixture
    def mock_repository(self):
        return Mock()

    @pytest.fixture
    def manage_subtasks_use_case(self, mock_repository):
        return ManageSubtasksUseCase(mock_repository)

    def test_add_subtask_to_nonexistent_task(self, manage_subtasks_use_case, mock_repository):
        """Test adding subtask to non-existent task should raise TaskNotFoundError"""
        mock_repository.find_by_id.return_value = None
        
        request = AddSubtaskRequest(task_id="20250101999", title="Subtask")

        with pytest.raises(TaskNotFoundError):
            manage_subtasks_use_case.add_subtask(request)

    def test_complete_subtask_invalid_id(self, manage_subtasks_use_case, mock_repository):
        """Test completing subtask with invalid ID should return success: False"""
        task = Task.create(id=TaskId.generate(), title="Test Task", description="Test")
        task.add_subtask({"title": "Subtask 1"})
        mock_repository.find_by_id.return_value = task
        
        # This subtask ID does not exist
        result = manage_subtasks_use_case.complete_subtask(str(task.id), 999)
        assert result["success"] is False

    def test_update_subtask_invalid_id(self, manage_subtasks_use_case, mock_repository):
        """Test updating subtask with invalid subtask ID should raise ValueError"""
        task = Task.create(id=TaskId.generate(), title="Test Task", description="Test")
        mock_repository.find_by_id.return_value = task
        
        request = UpdateSubtaskRequest(
            task_id=str(task.id),
            subtask_id=999,  # Non-existent subtask
            title="Updated"
        )
        
        with pytest.raises(ValueError, match="Subtask 999 not found"):
            manage_subtasks_use_case.update_subtask(request)

    def test_remove_subtask_invalid_id(self, manage_subtasks_use_case, mock_repository):
        """Test removing subtask with invalid subtask ID should return success: False"""
        task = Task.create(id=TaskId.generate(), title="Test Task", description="Test")
        mock_repository.find_by_id.return_value = task
        
        result = manage_subtasks_use_case.remove_subtask(str(task.id), 999)
        assert result["success"] is False

    def test_repo_save_error_on_add_subtask(self, manage_subtasks_use_case, mock_repository):
        """Test repository save error during add_subtask"""
        task = Task.create(id=TaskId.generate(), title="Test Task", description="Test")
        mock_repository.find_by_id.return_value = task
        mock_repository.save.side_effect = Exception("Database error")
        
        request = AddSubtaskRequest(task_id=str(task.id), title="New Subtask")
        
        with pytest.raises(Exception, match="Database error"):
            manage_subtasks_use_case.add_subtask(request)

    def test_repo_save_error_on_complete_subtask(self, manage_subtasks_use_case, mock_repository):
        """Test repository save error during complete_subtask"""
        task = Task.create(id=TaskId.generate(), title="Test Task", description="Test")
        added_subtask = task.add_subtask({"title": "Subtask 1"})
        mock_repository.find_by_id.return_value = task
        mock_repository.save.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            manage_subtasks_use_case.complete_subtask(str(task.id), added_subtask['id'])

    def test_repo_save_error_on_update_subtask(self, manage_subtasks_use_case, mock_repository):
        """Test repository save error during update_subtask"""
        task = Task.create(id=TaskId.generate(), title="Test Task", description="Test")
        added_subtask = task.add_subtask({"title": "Subtask 1"})
        mock_repository.find_by_id.return_value = task
        mock_repository.save.side_effect = Exception("Database error")

        request = UpdateSubtaskRequest(
            task_id=str(task.id),
            subtask_id=added_subtask['id'],
            title="Updated Title"
        )
        
        with pytest.raises(Exception, match="Database error"):
            manage_subtasks_use_case.update_subtask(request)

    def test_repo_save_error_on_remove_subtask(self, manage_subtasks_use_case, mock_repository):
        """Test repository save error during remove_subtask"""
        task = Task.create(id=TaskId.generate(), title="Test Task", description="Test")
        added_subtask = task.add_subtask({"title": "Subtask 1"})
        mock_repository.find_by_id.return_value = task
        mock_repository.save.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            manage_subtasks_use_case.remove_subtask(str(task.id), added_subtask['id']) 