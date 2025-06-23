"""
This is the canonical and only maintained test suite for the UpdateTask use case.
All validation, edge-case, and integration tests should be added here.
Redundant or duplicate tests in other files have been removed.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
import time

from fastmcp.dhafnck_mcp.application.use_cases.update_task import UpdateTaskUseCase
from fastmcp.dhafnck_mcp.application.dtos.task_dto import UpdateTaskRequest
from fastmcp.dhafnck_mcp.infrastructure import InMemoryTaskRepository
from fastmcp.dhafnck_mcp.domain.entities.task import Task
from fastmcp.dhafnck_mcp.domain.value_objects.task_id import TaskId
from fastmcp.dhafnck_mcp.domain.value_objects.task_status import TaskStatus, TaskStatusEnum
from fastmcp.dhafnck_mcp.domain.value_objects.priority import Priority, PriorityLevel
from fastmcp.dhafnck_mcp.domain.enums import AgentRole
from fastmcp.dhafnck_mcp.domain.exceptions import TaskNotFoundError


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
        mock_generator.generate_rules_for_task.return_value = {
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
            assignees=[f"@{AgentRole.CODING.value}"],
            labels=["original", "test"]
        )
        return repository.create(task)
    
    def test_execute_update_title(self, use_case, sample_task):
        """Test updating task title"""
        original_updated_at = sample_task.updated_at
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            title="Updated Title"
        )
        
        time.sleep(0.001)
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.title == "Updated Title"
        assert result.task.description == "Original Description"  # Unchanged
        assert result.task.updated_at > original_updated_at
    
    def test_execute_update_description(self, use_case, sample_task):
        """Test updating task description"""
        original_updated_at = sample_task.updated_at
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            description="Updated Description"
        )
        
        time.sleep(0.001)
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.description == "Updated Description"
        assert result.task.title == "Original Task"  # Unchanged
        assert result.task.updated_at > original_updated_at
    
    def test_execute_update_status(self, use_case, sample_task):
        """Test updating task status"""
        original_updated_at = sample_task.updated_at
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            status="in_progress"
        )
        
        time.sleep(0.001)
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.status == "in_progress"
        assert result.task.updated_at > original_updated_at
    
    def test_execute_update_priority(self, use_case, sample_task):
        """Test updating task priority"""
        original_updated_at = sample_task.updated_at
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            priority="critical"
        )
        
        time.sleep(0.001)
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.priority == "critical"
        assert result.task.updated_at > original_updated_at
    
    def test_execute_update_details(self, use_case, sample_task):
        """Test updating task details"""
        original_updated_at = sample_task.updated_at
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            details="Updated detailed information"
        )
        
        time.sleep(0.001)
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.details == "Updated detailed information"
        assert result.task.updated_at > original_updated_at
    
    def test_execute_update_estimated_effort(self, use_case, sample_task):
        """Test updating task estimated effort"""
        original_updated_at = sample_task.updated_at
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            estimated_effort="large"
        )
        
        time.sleep(0.001)
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.estimated_effort == "large"
        assert result.task.updated_at > original_updated_at
    
    def test_execute_update_assignees(self, use_case, sample_task):
        """Test updating task assignees"""
        original_updated_at = sample_task.updated_at
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            assignees=["@test_agent", "@code_reviewer_agent"]
        )
        
        time.sleep(0.001)
        result = use_case.execute(request)
        
        assert result.success is True
        assert "@test_agent" in result.task.assignees
        assert "@code_reviewer_agent" in result.task.assignees
        assert f"@{AgentRole.CODING.value}" not in result.task.assignees  # Replaced
        assert result.task.updated_at > original_updated_at
    
    def test_execute_update_labels(self, use_case, sample_task):
        """Test updating task labels"""
        original_updated_at = sample_task.updated_at
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            labels=["updated", "feature", "backend"]
        )
        
        time.sleep(0.001)
        result = use_case.execute(request)
        
        assert result.success is True
        assert "updated" in result.task.labels
        assert "feature" in result.task.labels
        assert "backend" in result.task.labels
        assert "original" not in result.task.labels  # Replaced
        assert result.task.updated_at > original_updated_at
    
    def test_execute_update_due_date(self, use_case, sample_task):
        """Test updating task due date"""
        original_updated_at = sample_task.updated_at
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            due_date="2025-12-31"
        )
        
        time.sleep(0.001)
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.due_date is not None
        assert result.task.updated_at > original_updated_at
    
    def test_execute_update_multiple_fields(self, use_case, sample_task):
        """Test updating multiple fields at once"""
        original_updated_at = sample_task.updated_at
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            title="Completely Updated Task",
            description="Completely updated description",
            status="in_progress",
            priority="high",
            details="Updated details",
            estimated_effort="xlarge",
            assignees=["@test_agent", "@documentation_agent"],
            labels=["updated", "completed", "feature"],
            due_date="2025-06-30"
        )
        
        time.sleep(0.001)
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.title == "Completely Updated Task"
        assert result.task.description == "Completely updated description"
        assert result.task.status == "in_progress"
        assert result.task.priority == "high"
        assert result.task.details == "Updated details"
        assert result.task.estimated_effort == "xlarge"
        assert "@test_agent" in result.task.assignees
        assert "@documentation_agent" in result.task.assignees
        assert "updated" in result.task.labels
        assert "completed" in result.task.labels
        assert "feature" in result.task.labels
        assert result.task.due_date is not None
        assert result.task.updated_at > original_updated_at
    
    def test_execute_update_nonexistent_task(self, use_case):
        """Test updating non-existent task"""
        request = UpdateTaskRequest(
            task_id="20250101999",  # Valid format, but non-existent
            title="Updated Title"
        )
        
        with pytest.raises(TaskNotFoundError):
            use_case.execute(request)
    
    def test_execute_update_with_empty_task_id(self, use_case):
        """Test updating with empty task ID"""
        request = UpdateTaskRequest(
            task_id="",
            title="Updated Title"
        )
        with pytest.raises(ValueError):
            use_case.execute(request)
    
    def test_execute_update_with_none_task_id(self, use_case):
        """Test updating with None task ID"""
        request = UpdateTaskRequest(
            task_id=None,
            title="Updated Title"
        )
        with pytest.raises(ValueError):
            use_case.execute(request)
    
    def test_execute_update_with_invalid_status(self, use_case, sample_task):
        """Test updating with invalid status"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            status="invalid_status"
        )
        with pytest.raises(ValueError):
            use_case.execute(request)
    
    def test_execute_update_with_invalid_priority(self, use_case, sample_task):
        """Test updating with invalid priority"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            priority="invalid_priority"
        )
        with pytest.raises(ValueError):
            use_case.execute(request)
    
    def test_execute_update_with_invalid_assignees(self, use_case, sample_task):
        """Test updating with invalid assignees (e.g., empty string)"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            assignees=[""]
        )
        
        time.sleep(0.001)
        result = use_case.execute(request)

        assert result.success is True
        assert not result.task.assignees
    
    def test_execute_update_with_invalid_estimated_effort(self, use_case, sample_task):
        """Test updating with invalid estimated effort"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            estimated_effort="invalid_effort"
        )
        # This should not raise an error, but default to a value.
        time.sleep(0.001)
        result = use_case.execute(request)
        assert result.success is True
        assert result.task.estimated_effort == "medium"
    
    def test_execute_update_with_invalid_due_date(self, use_case, sample_task):
        """Test updating with invalid due date format"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            due_date="invalid_date"
        )
        with pytest.raises(ValueError):
            use_case.execute(request)
    
    def test_execute_update_with_empty_strings(self, use_case, sample_task):
        """Test updating with empty strings for optional fields"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            description="",
            details=""
        )
        with pytest.raises(ValueError):
             use_case.execute(request)
    
    def test_execute_update_with_none_values(self, use_case, sample_task):
        """Test that None values for fields do not cause updates"""
        original_title = sample_task.title
        original_description = sample_task.description
        
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            title=None,
            description=None
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.title == original_title
        assert result.task.description == original_description
    
    def test_execute_update_with_empty_lists(self, use_case, sample_task):
        """Test updating with empty lists for assignees and labels"""
        original_updated_at = sample_task.updated_at
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            assignees=[],
            labels=[]
        )
        
        time.sleep(0.001)
        result = use_case.execute(request)
        
        assert result.success is True
        assert not result.task.assignees
        assert not result.task.labels
        assert result.task.updated_at > original_updated_at
    
    def test_execute_auto_rule_generation_success(self, use_case, sample_task, auto_rule_generator):
        """Test successful auto rule generation on update"""
        original_updated_at = sample_task.updated_at
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            title="Updated Task"
        )

        time.sleep(0.001)
        result = use_case.execute(request)

        assert result.success is True
        auto_rule_generator.generate_rules_for_task.assert_called_once()
        assert result.task.updated_at > original_updated_at

    def test_execute_auto_rule_generation_failure(self, use_case, sample_task, auto_rule_generator):
        """Test auto rule generation failure is handled gracefully"""
        auto_rule_generator.generate_rules_for_task.return_value = {
            "success": False,
            "error": "Generation failed"
        }
        
        original_updated_at = sample_task.updated_at
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            title="Updated Task"
        )
        time.sleep(0.001)
        result = use_case.execute(request)

        assert result.success is True  # Task update should still succeed
        auto_rule_generator.generate_rules_for_task.assert_called_once()
        assert result.task.updated_at > original_updated_at

    def test_execute_auto_rule_generation_exception(self, use_case, sample_task, auto_rule_generator):
        """Test auto rule generation raises an exception"""
        auto_rule_generator.generate_rules_for_task.side_effect = Exception("Test exception")
        
        original_updated_at = sample_task.updated_at
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            title="Updated Task"
        )
        time.sleep(0.001)
        result = use_case.execute(request)

        assert result.success is True  # Task update should still succeed
        auto_rule_generator.generate_rules_for_task.assert_called_once()
        assert result.task.updated_at > original_updated_at

    def test_execute_repository_error(self, use_case, sample_task, repository):
        """Test handling of repository errors during update"""
        repository.save = Mock(side_effect=Exception("Database connection failed"))
        
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            title="Update that will fail"
        )
        
        with pytest.raises(Exception, match="Database connection failed"):
            use_case.execute(request)
    
    def test_execute_preserves_unchanged_fields(self, use_case, sample_task):
        """Test that fields not included in the request are preserved"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            title="New Title",
            status = "in_progress"
        )

        original_description = sample_task.description
        original_priority = sample_task.priority.value
        original_labels = sample_task.labels.copy()
        original_updated_at = sample_task.updated_at

        time.sleep(0.001)
        result = use_case.execute(request)

        assert result.success is True
        assert result.task.title == "New Title"
        assert result.task.status == "in_progress"
        assert result.task.description == original_description
        assert result.task.priority == original_priority
        assert result.task.labels == original_labels
        assert result.task.updated_at > original_updated_at

    def test_execute_multiple_updates_same_task(self, use_case, sample_task):
        """Test that multiple updates to the same task work correctly"""
        first_request = UpdateTaskRequest(
            task_id=sample_task.id,
            title="First Update",
            status="in_progress"
        )
    
        time.sleep(0.001)
        first_result = use_case.execute(first_request)
    
        assert first_result.success is True
        assert first_result.task.title == "First Update"
        assert first_result.task.status == "in_progress"
    
        second_request = UpdateTaskRequest(
            task_id=sample_task.id,
            description="Second Update Description"
        )
    
        time.sleep(0.001)
        second_result = use_case.execute(second_request)
    
        assert second_result.success is True
        assert second_result.task.title == "First Update"  # Preserved
        assert second_result.task.description == "Second Update Description"
        assert second_result.task.updated_at > first_result.task.updated_at
    
        third_request = UpdateTaskRequest(
            task_id=sample_task.id,
            status="done",
            priority="low"
        )
    
        time.sleep(0.001)
        third_result = use_case.execute(third_request)

        assert third_result.success is True
        assert third_result.task.status == "done"
        assert third_result.task.priority == "low"
        assert third_result.task.updated_at > second_result.task.updated_at

    def test_execute_update_with_special_characters(self, use_case, sample_task):
        """Test updating with various special characters"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            title="Task with special characters: éàçüö",
            details="Details with special characters: !@#$%^&*()_+{}|:\"<>?`~[]\\;',./"
        )
        
        original_updated_at = sample_task.updated_at
        time.sleep(0.001)
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.title == "Task with special characters: éàçüö"
        assert result.task.details == "Details with special characters: !@#$%^&*()_+{}|:\"<>?`~[]\\;',./"
        assert result.task.updated_at > original_updated_at

    def test_execute_update_with_very_long_content(self, use_case, sample_task):
        """Test updating with very long strings"""
        long_title = "a" * 200
        long_description = "b" * 1000
        
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            title=long_title,
            description=long_description
        )
        
        original_updated_at = sample_task.updated_at
        time.sleep(0.001)
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.title == long_title
        assert result.task.description == long_description
        assert result.task.updated_at > original_updated_at

    def test_execute_update_timestamp_precision(self, use_case, sample_task):
        """Test timestamp precision and timezone awareness"""
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            title="Timestamp Test"
        )
        
        original_updated_at = sample_task.updated_at
        time.sleep(0.001)
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.updated_at > original_updated_at
        
        assert result.task.created_at.tzinfo is not None
        assert result.task.updated_at.tzinfo is not None
        assert result.task.created_at.utcoffset().total_seconds() == 0
        assert result.task.updated_at.utcoffset().total_seconds() == 0
        
        assert result.task.updated_at.microsecond != original_updated_at.microsecond

    def test_execute_update_preserves_subtasks_and_dependencies(self, use_case, sample_task, repository):
        """Test that updating a task does not affect its subtasks or dependencies"""
        sample_task.add_subtask(title="Subtask 1")
        sample_task.add_dependency(TaskId("20250101998"))
        repository.save(sample_task)
        
        request = UpdateTaskRequest(
            task_id=sample_task.id,
            title="Updated without touching subtasks/deps"
        )
        
        original_updated_at = sample_task.updated_at
        time.sleep(0.001)
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.title == "Updated without touching subtasks/deps"
        assert len(result.task.subtasks) == 1
        assert result.task.subtasks[0]["title"] == "Subtask 1"
        assert len(result.task.dependencies) == 1
        assert result.task.dependencies[0] == "20250101998"
        assert result.task.updated_at > original_updated_at


if __name__ == "__main__":
    pytest.main([__file__]) 