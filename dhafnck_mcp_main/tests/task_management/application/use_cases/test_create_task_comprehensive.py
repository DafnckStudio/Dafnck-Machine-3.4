"""Comprehensive tests for CreateTask use case"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone

from fastmcp.task_management.application.use_cases.create_task import CreateTaskUseCase
from fastmcp.task_management.application.dtos.task_dto import CreateTaskRequest
from fastmcp.task_management.infrastructure import InMemoryTaskRepository
from fastmcp.task_management.domain.entities.task import Task
from fastmcp.task_management.domain.value_objects.task_status import TaskStatus, TaskStatusEnum
from fastmcp.task_management.domain.value_objects.priority import Priority, PriorityLevel
from fastmcp.task_management.domain.enums import AgentRole
from fastmcp.task_management.domain.exceptions import TaskNotFoundError


class TestCreateTaskUseCase:
    """Test CreateTask use case functionality"""
    
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
        """Create CreateTask use case instance"""
        return CreateTaskUseCase(repository, auto_rule_generator)
    
    @pytest.fixture
    def basic_request(self):
        """Create basic create task request"""
        return CreateTaskRequest(
            title="Test Task",
            description="Test Description"
        )
    
    @pytest.fixture
    def detailed_request(self):
        """Create detailed create task request"""
        return CreateTaskRequest(
            title="Detailed Task",
            description="Detailed Description",
            priority="high",
            details="Detailed information",
            estimated_effort="medium",
            assignees=["@coding_agent", "@test_agent"],
            labels=["feature", "backend"],
            due_date="2025-12-31"
        )
    
    def test_execute_basic_task_creation(self, use_case, basic_request):
        """Test creating basic task"""
        result = use_case.execute(basic_request)
        
        assert result.success is True
        assert result.task is not None
        assert result.task.title == "Test Task"
        assert result.task.description == "Test Description"
        assert result.task.id is not None
        assert result.task.status == "todo"
        assert result.task.priority is not None
        assert result.task.created_at is not None
        assert result.task.updated_at is not None
    
    def test_execute_detailed_task_creation(self, use_case, detailed_request):
        """Test creating detailed task with all fields"""
        result = use_case.execute(detailed_request)
        
        assert result.success is True
        assert result.task is not None
        assert result.task.title == "Detailed Task"
        assert result.task.description == "Detailed Description"
        assert result.task.priority == "high"
        assert result.task.details == "Detailed information"
        assert result.task.estimated_effort == "medium"
        assert "@coding_agent" in result.task.assignees
        assert "@test_agent" in result.task.assignees
        assert "feature" in result.task.labels
        assert "backend" in result.task.labels
        assert result.task.due_date is not None
    
    def test_execute_with_invalid_priority(self, use_case):
        """Test creating task with invalid priority"""
        request = CreateTaskRequest(
            title="Test Task",
            description="Test Description",
            priority="invalid_priority"
        )
        
        with pytest.raises(ValueError, match="Invalid priority: invalid_priority"):
            use_case.execute(request)
    
    def test_execute_with_invalid_estimated_effort(self, use_case):
        """Test creating task with invalid estimated effort"""
        request = CreateTaskRequest(
            title="Test Task",
            description="Test Description",
            estimated_effort="invalid_effort"
        )
        
        result = use_case.execute(request)
        
        # Should handle gracefully
        assert result.success is True
        assert result.task.estimated_effort is not None
    
    def test_execute_with_invalid_assignees(self, use_case):
        """Test creating task with invalid assignees"""
        request = CreateTaskRequest(
            title="Test Task",
            description="Test Description",
            assignees=["@invalid_agent", "@another_invalid"]
        )
        
        result = use_case.execute(request)
        
        # Should handle gracefully
        assert result.success is True
        assert result.task.assignees is not None
    
    def test_execute_with_invalid_due_date(self, use_case):
        """Test creating task with invalid due date"""
        request = CreateTaskRequest(
            title="Test Task",
            description="Test Description",
            due_date="invalid_date"
        )
        
        result = use_case.execute(request)
        
        # Should handle gracefully
        assert result.success is True
        # due_date should be None or handled appropriately
    
    def test_execute_with_empty_title(self, use_case):
        """Test creating task with empty title"""
        request = CreateTaskRequest(
            title="",
            description="Test Description"
        )
        
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            use_case.execute(request)
    
    def test_execute_with_empty_description(self, use_case):
        """Test creating task with empty description"""
        request = CreateTaskRequest(
            title="Test Task",
            description=""
        )
        
        with pytest.raises(ValueError, match="Task description cannot be empty"):
            use_case.execute(request)
    
    def test_execute_with_none_values(self, use_case):
        """Test creating task with None values"""
        request = CreateTaskRequest(
            title="Test Task",
            description="Test Description",
            priority=None,
            details=None,
            estimated_effort=None,
            assignees=None,
            labels=None,
            due_date=None
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task is not None
        assert result.task.title == "Test Task"
    
    def test_execute_with_empty_lists(self, use_case):
        """Test creating task with empty lists"""
        request = CreateTaskRequest(
            title="Test Task",
            description="Test Description",
            assignees=[],
            labels=[]
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task is not None
        assert result.task.assignees == []
        assert result.task.labels == []
    
    def test_execute_auto_rule_generation_success(self, use_case, basic_request, auto_rule_generator):
        """Test successful auto rule generation"""
        result = use_case.execute(basic_request)
        
        assert result.success is True
        
        # Verify auto rule generator was called
        auto_rule_generator.generate_rule.assert_called_once()
        
        # Verify that context was passed correctly
        call_args, call_kwargs = auto_rule_generator.generate_rule.call_args
        assert "task" in call_kwargs
        task_context = call_kwargs["task"]
        assert isinstance(task_context, Task)
        assert task_context.title == "Test Task"
    
    def test_execute_auto_rule_generation_failure(self, use_case, basic_request, auto_rule_generator):
        """Test handling auto rule generation failure"""
        auto_rule_generator.generate_rule.return_value = {
            "success": False,
            "error": "Generation failed"
        }
        
        result = use_case.execute(basic_request)
        
        # Task creation should still succeed even if rule generation fails
        assert result.success is True
        assert result.task is not None
    
    def test_execute_auto_rule_generation_exception(self, use_case, basic_request, auto_rule_generator):
        """Test handling auto rule generation exception"""
        auto_rule_generator.generate_rule.side_effect = Exception("Generator error")
        
        result = use_case.execute(basic_request)
        
        # Task creation should still succeed even if rule generation raises exception
        assert result.success is True
        assert result.task is not None
    
    def test_execute_repository_error(self, use_case, basic_request, repository):
        """Test handling repository error"""
        repository.save = Mock(side_effect=Exception("Repository error"))
        
        result = use_case.execute(basic_request)
        
        assert result.success is False
        assert "error" in result.message or "Repository error" in result.message
    
    def test_execute_multiple_tasks(self, use_case):
        """Test creating multiple tasks"""
        requests = [
            CreateTaskRequest(title=f"Task {i}", description=f"Description {i}")
            for i in range(5)
        ]
        
        results = []
        for request in requests:
            result = use_case.execute(request)
            results.append(result)
        
        # All should succeed
        assert all(r.success for r in results)
        
        # All should have unique IDs
        task_ids = [r.task.id for r in results]
        assert len(set(task_ids)) == 5
    
    def test_execute_with_special_characters(self, use_case):
        """Test creating task with special characters"""
        request = CreateTaskRequest(
            title="Task with \"quotes\" and 'apostrophes'",
            description="Description with <tags> & symbols",
            details="Details with émojis 🚀 and ünïcödé"
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.title == "Task with \"quotes\" and 'apostrophes'"
        assert "émojis" in result.task.details
        assert "🚀" in result.task.details
    
    def test_execute_with_very_long_content(self, use_case):
        """Test creating task with very long content"""
        long_title = "Very long title " * 100
        long_description = "Very long description " * 1000
        long_details = "Very long details " * 500
        
        request = CreateTaskRequest(
            title=long_title,
            description=long_description,
            details=long_details
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        # Title should be truncated to 200 characters
        assert len(result.task.title) <= 200
        assert result.task.title.startswith("Very long title")
        # Description should be truncated to 1000 characters  
        assert len(result.task.description) <= 1000
        assert result.task.description.startswith("Very long description")
        # Details should be preserved as-is (no length limit in use case)
        assert result.task.details == long_details
    
    def test_execute_with_all_assignee_roles(self, use_case):
        """Test creating task with all valid assignee roles"""
        all_roles = [role.value for role in AgentRole]
        
        request = CreateTaskRequest(
            title="Task with all roles",
            description="Test all assignee roles",
            assignees=all_roles
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        assert len(result.task.assignees) > 0  # Should have valid assignees
    
    def test_execute_with_many_labels(self, use_case):
        """Test creating task with many labels"""
        many_labels = [f"label_{i}" for i in range(50)]
        
        request = CreateTaskRequest(
            title="Task with many labels",
            description="Test many labels",
            labels=many_labels
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        assert len(result.task.labels) == 50
        assert "label_0" in result.task.labels
        assert "label_49" in result.task.labels
    
    def test_execute_with_project_id(self, use_case):
        """Test creating task with project ID"""
        request = CreateTaskRequest(
            title="Project Task",
            description="Task for specific project",
            project_id="test_project"
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        assert result.task.project_id == "test_project"
    
    def test_execute_preserves_task_order(self, use_case, repository):
        """Test that task creation preserves order in repository"""
        tasks = []
        for i in range(3):
            request = CreateTaskRequest(
                title=f"Task {i}",
                description=f"Description {i}"
            )
            result = use_case.execute(request)
            tasks.append(result.task)
        
        # Check repository has all tasks
        all_tasks = repository.find_all()
        assert len(all_tasks) == 3
        
        # Tasks should be in creation order
        for i, task in enumerate(all_tasks):
            assert task.title == f"Task {i}"
    
    def test_execute_task_timestamps(self, use_case, basic_request):
        """Test that task timestamps are set correctly"""
        before_creation = datetime.now(timezone.utc)
        result = use_case.execute(basic_request)
        after_creation = datetime.now(timezone.utc)
        
        assert result.success is True
        assert before_creation <= result.task.created_at <= after_creation
        assert result.task.created_at == result.task.updated_at
    
    def test_execute_task_id_format(self, use_case, basic_request):
        """Test that task ID has correct format"""
        result = use_case.execute(basic_request)
        
        assert result.success is True
        assert result.task.id is not None
        assert isinstance(result.task.id, str)
        assert len(result.task.id) > 0
        # Task ID should follow expected format (e.g., date-based)
        assert result.task.id.isalnum() or any(c in result.task.id for c in ['-', '_'])
    
    def test_execute_concurrent_creation_simulation(self, use_case):
        """Test simulated concurrent task creation"""
        import threading
        
        results = []
        
        def create_task_worker(worker_id):
            request = CreateTaskRequest(
                title=f"Concurrent Task {worker_id}",
                description=f"Created by worker {worker_id}"
            )
            result = use_case.execute(request)
            results.append((worker_id, result))
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_task_worker, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        # Verify all creations succeeded
        assert len(results) == 5
        for worker_id, result in results:
            assert result.success is True
            assert f"Concurrent Task {worker_id}" in result.task.title
        
        # Verify all tasks have unique IDs
        task_ids = [result.task.id for _, result in results]
        assert len(set(task_ids)) == 5
    
    def test_execute_with_due_date_formats(self, use_case):
        """Test creating task with various due date formats"""
        date_formats = [
            "2025-12-31",
            "2025-12-31T23:59:59",
            "2025-12-31T23:59:59Z",
            "2025-12-31T23:59:59+00:00"
        ]
        
        for date_str in date_formats:
            request = CreateTaskRequest(
                title=f"Task with date {date_str}",
                description="Test date format",
                due_date=date_str
            )
            
            result = use_case.execute(request)
            assert result.success is True
    
    def test_execute_auto_rule_generation_with_assignee(self, use_case, auto_rule_generator):
        """Test auto rule generation extracts role from assignee"""
        request = CreateTaskRequest(
            title="Test Task",
            description="Test Description",
            assignees=["@coding_agent"]
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        auto_rule_generator.generate_rule.assert_called_once()
        
        # Should extract role from assignee
        _, call_kwargs = auto_rule_generator.generate_rule.call_args
        assert "role" in call_kwargs
        assert call_kwargs["role"] == "coding_agent"
        assert "task" in call_kwargs
    
    def test_execute_auto_rule_generation_no_assignee(self, use_case, auto_rule_generator):
        """Test auto rule generation with no assignee"""
        request = CreateTaskRequest(
            title="Test Task",
            description="Test Description"
        )
        
        result = use_case.execute(request)
        
        assert result.success is True
        auto_rule_generator.generate_rule.assert_called_once()
        
        # Role should be None if no assignees
        _, call_kwargs = auto_rule_generator.generate_rule.call_args
        assert call_kwargs["role"] is None
        assert "task" in call_kwargs


if __name__ == "__main__":
    pytest.main([__file__]) 