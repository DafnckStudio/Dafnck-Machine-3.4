"""Comprehensive tests for UpdateTask use case"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone

from fastmcp.task_management.application.use_cases.update_task import UpdateTaskUseCase
from fastmcp.task_management.application.dtos.task_dto import UpdateTaskRequest
from fastmcp.task_management.infrastructure import InMemoryTaskRepository
from fastmcp.task_management.domain.entities.task import Task
from fastmcp.task_management.domain.value_objects.task_status import TaskStatus, TaskStatusEnum
from fastmcp.task_management.domain.value_objects.priority import Priority, PriorityLevel
from fastmcp.task_management.domain.enums import AgentRole
from fastmcp.task_management.domain.exceptions import TaskNotFoundError


class TestUpdateTaskUseCase:
    """Test UpdateTask use case functionality"""
    
    @pytest.fixture
    def repository(self):
        """Create in-memory repository for testing"""
        return InMemoryTaskRepository()
    
    @pytest.fixture
    def auto_rule_generator(self):
        """Create mock auto rule generator"""
        mock_generator = Mock()
        mock_generator.generate_rule.return_value = {
            "success": True,
            "rule_content": "Generated rule content"
        }
        return mock_generator
    
    @pytest.fixture
    def use_case(self, repository, auto_rule_generator):
        """Create UpdateTask use case instance"""
        return UpdateTaskUseCase(repository, auto_rule_generator)
    
    @pytest.fixture
    def sample_task(self, repository):
        """Create and store a sample task for testing"""
        task = Task(
            title="Original Task",
            description="Original Description",
            priority=Priority.medium(),
            assignees=[AgentRole.CODING],
            labels=["original", "test"]
        )
        return repository.create(task)
    
    def test_execute_update_title(self, use_case, sample_task):
        """Test updating task title"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            title="Updated Title"
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.title == "Updated Title"
        assert result.task.description == "Original Description"  # Unchanged
        assert result.task.updated_at > sample_task.updated_at
    
    def test_execute_update_description(self, use_case, sample_task):
        """Test updating task description"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            description="Updated Description"
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.description == "Updated Description"
        assert result.task.title == "Original Task"  # Unchanged
    
    def test_execute_update_status(self, use_case, sample_task):
        """Test updating task status"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            status="in_progress"
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.status.value == TaskStatus.in_progress().value
    
    def test_execute_update_priority(self, use_case, sample_task):
        """Test updating task priority"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            priority="critical"
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.priority.value == Priority.critical().value
    
    def test_execute_update_details(self, use_case, sample_task):
        """Test updating task details"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            details="Updated detailed information"
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.details == "Updated detailed information"
    
    def test_execute_update_estimated_effort(self, use_case, sample_task):
        """Test updating task estimated effort"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            estimated_effort="large"
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.estimated_effort.value == "large"
    
    def test_execute_update_assignees(self, use_case, sample_task):
        """Test updating task assignees"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            assignees=["@test_agent", "@code_reviewer_agent"]
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        assert AgentRole.TEST_CASE_GENERATOR in result.task.assignees
        assert AgentRole.CODE_REVIEWER in result.task.assignees
        assert AgentRole.CODING not in result.task.assignees  # Replaced
    
    def test_execute_update_labels(self, use_case, sample_task):
        """Test updating task labels"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            labels=["updated", "feature", "backend"]
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        assert "updated" in result.task.labels
        assert "feature" in result.task.labels
        assert "backend" in result.task.labels
        assert "original" not in result.task.labels  # Replaced
    
    def test_execute_update_due_date(self, use_case, sample_task):
        """Test updating task due date"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            due_date="2025-12-31"
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.due_date is not None
    
    def test_execute_update_multiple_fields(self, use_case, sample_task):
        """Test updating multiple fields at once"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            title="Completely Updated Task",
            description="Completely updated description",
            status="done",
            priority="high",
            details="Updated details",
            estimated_effort="xlarge",
            assignees=["@test_agent", "@documentation_agent"],
            labels=["updated", "completed", "feature"],
            due_date="2025-06-30"
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.title == "Completely Updated Task"
        assert result.task.description == "Completely updated description"
        assert result.task.status.value == TaskStatus.done().value
        assert result.task.priority.value == Priority.high().value
        assert result.task.details == "Updated details"
        assert result.task.estimated_effort.value == "xlarge"
        assert AgentRole.TEST_CASE_GENERATOR in result.task.assignees
        assert AgentRole.DOCUMENTATION in result.task.assignees
        assert "updated" in result.task.labels
        assert "completed" in result.task.labels
        assert "feature" in result.task.labels
        assert result.task.due_date is not None
    
    def test_execute_update_nonexistent_task(self, use_case):
        """Test updating non-existent task"""
        request = UpdateTaskRequest(
            task_id="nonexistent_id",
            title="Updated Title"
        )
        
        result = use_case.execute(request)
        
        assert result.success is False
        assert "not found" in result.error_message.lower() or isinstance(result.error, TaskNotFoundError)
    
    def test_execute_update_with_empty_task_id(self, use_case):
        """Test updating with empty task ID"""
        request = UpdateTaskRequest(
            task_id="",
            title="Updated Title"
        )
        
        result = use_case.execute(request)
        
        assert result.success is False
    
    def test_execute_update_with_none_task_id(self, use_case):
        """Test updating with None task ID"""
        request = UpdateTaskRequest(
            task_id=None,
            title="Updated Title"
        )
        
        result = use_case.execute(request)
        
        assert result.success is False
    
    def test_execute_update_with_invalid_status(self, use_case, sample_task):
        """Test updating with invalid status"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            status="invalid_status"
        )
        
        result = use_case.execute(request)
        
        # Should handle gracefully - either succeed with default or fail gracefully
        assert result is not None
    
    def test_execute_update_with_invalid_priority(self, use_case, sample_task):
        """Test updating with invalid priority"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            priority="invalid_priority"
        )
        
        result = use_case.execute(request)
        
        # Should handle gracefully
        assert result is not None
    
    def test_execute_update_with_invalid_assignees(self, use_case, sample_task):
        """Test updating with invalid assignees"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            assignees=["@invalid_agent", "@another_invalid"]
        )
        
        result = use_case.execute(request)
        
        # Should handle gracefully
        assert result is not None
    
    def test_execute_update_with_invalid_estimated_effort(self, use_case, sample_task):
        """Test updating with invalid estimated effort"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            estimated_effort="invalid_effort"
        )
        
        result = use_case.execute(request)
        
        # Should handle gracefully
        assert result is not None
    
    def test_execute_update_with_invalid_due_date(self, use_case, sample_task):
        """Test updating with invalid due date"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            due_date="invalid_date"
        )
        
        result = use_case.execute(request)
        
        # Should handle gracefully
        assert result is not None
    
    def test_execute_update_with_empty_strings(self, use_case, sample_task):
        """Test updating with empty strings"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            title="",
            description="",
            details=""
        )
        
        result = use_case.execute(request)
        
        # Should handle appropriately (might allow empty strings or use defaults)
        assert result is not None
    
    def test_execute_update_with_none_values(self, use_case, sample_task):
        """Test updating with None values"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
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
        
        result = use_case.execute(request)
        
        # Should handle None values appropriately (no changes or defaults)
        assert result.success is True
        # Original values should be preserved when None is passed
        assert result.task.title == "Original Task"
        assert result.task.description == "Original Description"
    
    def test_execute_update_with_empty_lists(self, use_case, sample_task):
        """Test updating with empty lists"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            assignees=[],
            labels=[]
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.assignees == []
        assert result.task.labels == []
    
    def test_execute_auto_rule_generation_success(self, use_case, sample_task, auto_rule_generator):
        """Test successful auto rule generation during update"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            title="Updated Task",
            assignees=["@coding_agent"]
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        
        # Verify auto rule generator was called
        auto_rule_generator.generate_rule.assert_called_once()
        call_args = auto_rule_generator.generate_rule.call_args
        
        # Should be called with role and task context
        assert len(call_args[0]) >= 1
        if len(call_args[0]) > 1:
            task_context = call_args[0][1]
            assert isinstance(task_context, dict)
            assert "id" in task_context
            assert "title" in task_context
            assert task_context["title"] == "Updated Task"
    
    def test_execute_auto_rule_generation_failure(self, use_case, sample_task, auto_rule_generator):
        """Test handling auto rule generation failure"""
        auto_rule_generator.generate_rule.return_value = {
            "success": False,
            "error": "Generation failed"
        }
        
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            title="Updated Task"
        )
        
        result = use_case.execute(request)
        
        # Task update should still succeed even if rule generation fails
        assert result.success is True
        assert result.task.title == "Updated Task"
    
    def test_execute_auto_rule_generation_exception(self, use_case, sample_task, auto_rule_generator):
        """Test handling auto rule generation exception"""
        auto_rule_generator.generate_rule.side_effect = Exception("Generator error")
        
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            title="Updated Task"
        )
        
        result = use_case.execute(request)
        
        # Task update should still succeed even if rule generation raises exception
        assert result.success is True
        assert result.task.title == "Updated Task"
    
    def test_execute_repository_error(self, use_case, sample_task, repository):
        """Test handling repository error"""
        repository.update = Mock(side_effect=Exception("Repository error"))
        
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            title="Updated Task"
        )
        
        result = use_case.execute(request)
        
        assert result.success is False
        assert "error" in result.__dict__ or hasattr(result, 'error_message')
    
    def test_execute_preserves_unchanged_fields(self, use_case, sample_task):
        """Test that unchanged fields are preserved"""
        original_created_at = sample_task.created_at
        original_assignees = sample_task.assignees.copy()
        original_labels = sample_task.labels.copy()
        
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            title="Only Title Updated"
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.title == "Only Title Updated"
        assert result.task.description == "Original Description"
        assert result.task.priority.value == Priority.medium().value
        assert result.task.assignees == original_assignees
        assert result.task.labels == original_labels
        assert result.task.created_at == original_created_at
        assert result.task.updated_at > original_created_at
    
    def test_execute_multiple_updates_same_task(self, use_case, sample_task):
        """Test multiple updates to the same task"""
        # First update
        request1 = UpdateTaskRequest(
            task_id=sample_task.id,
            title="First Update"
        )
        result1 = use_case.execute(request1)
        assert result1.success is True
        
        # Second update
        request2 = UpdateTaskRequest(
            task_id=sample_task.id,
            description="Second Update Description"
        )
        result2 = use_case.execute(request2)
        assert result2.success is True
        
        # Third update
        request3 = UpdateTaskRequest(
            task_id=sample_task.id,
            status="in_progress",
            priority="high"
        )
        result3 = use_case.execute(request3)
        assert result3.success is True
        
        # Final state should have all updates
        assert result3.task.title == "First Update"
        assert result3.task.description == "Second Update Description"
        assert result3.task.status.value == TaskStatus.in_progress().value
        assert result3.task.priority.value == Priority.high().value
        
        # Timestamps should progress
        assert result1.task.updated_at <= result2.task.updated_at <= result3.task.updated_at
    
    def test_execute_update_with_special_characters(self, use_case, sample_task):
        """Test updating with special characters"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            title="Task with \"quotes\" and 'apostrophes'",
            description="Description with <tags> & symbols",
            details="Details with émojis 🚀 and ünïcödé"
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.title == "Task with \"quotes\" and 'apostrophes'"
        assert "émojis" in result.task.details
        assert "🚀" in result.task.details
    
    def test_execute_update_with_very_long_content(self, use_case, sample_task):
        """Test updating with very long content"""
        long_title = "Very long title " * 100
        long_description = "Very long description " * 1000
        long_details = "Very long details " * 500
        
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            title=long_title,
            description=long_description,
            details=long_details
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.title == long_title
        assert result.task.description == long_description
        assert result.task.details == long_details
    
    def test_execute_update_timestamp_precision(self, use_case, sample_task):
        """Test that update timestamp is precise"""
        original_updated_at = sample_task.updated_at
        
        # Small delay to ensure timestamp difference
        import time
        time.sleep(0.001)
        
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            title="Timestamp Test"
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.updated_at > original_updated_at
        # Should be very recent
        time_diff = datetime.now(timezone.utc) - result.task.updated_at
        assert time_diff.total_seconds() < 1.0
    
    def test_execute_concurrent_updates_simulation(self, use_case, repository):
        """Test simulated concurrent updates"""
        # Create a task for concurrent updates
        task = Task(title="Concurrent Task", description="For concurrent testing")
        created_task = repository.create(task)
        
        import threading
        results = []
        
        def update_task_worker(worker_id):
            request = UpdateTaskRequest(
                task_id=created_task.id,
                title=f"Updated by worker {worker_id}",
                details=f"Worker {worker_id} details"
            )
            result = use_case.execute(request)
            results.append((worker_id, result))
        
        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=update_task_worker, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # All updates should succeed (last one wins)
        assert len(results) == 3
        for worker_id, result in results:
            assert result.success is True
        
        # Final task should have one of the worker's updates
        final_task = repository.get_by_id(created_task.id)
        assert "Updated by worker" in final_task.title
    
    def test_execute_update_preserves_subtasks_and_dependencies(self, use_case, sample_task):
        """Test that update preserves subtasks and dependencies"""
        # Add subtasks and dependencies to the original task
        sample_task.add_subtask("Test subtask", "Subtask description")
        sample_task.add_dependency("dependency_task_id")
        
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            title="Updated Title"
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.title == "Updated Title"
        # Subtasks and dependencies should be preserved
        assert len(result.task.subtasks) == 1
        assert len(result.task.dependencies) == 1
        assert result.task.subtasks[0]["title"] == "Test subtask"
        assert "dependency_task_id" in result.task.dependencies


if __name__ == "__main__":
    pytest.main([__file__]) 