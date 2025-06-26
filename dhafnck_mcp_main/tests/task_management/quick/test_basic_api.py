"""
This is the canonical and only maintained quick test suite for basic API validation in task management.
All validation, edge-case, and integration tests should be added here.
Redundant or duplicate tests in other files have been removed.
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))


@pytest.mark.quick
@pytest.mark.mcp
def test_basic_task_creation_structure():
    """Test basic task creation structure without persistence."""
    try:
        from fastmcp.task_management.domain.entities.task import Task
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        from fastmcp.task_management.domain.value_objects.task_status import TaskStatus, TaskStatusEnum
        from fastmcp.task_management.domain.value_objects.priority import Priority, PriorityLevel
        
        # Test creating a basic task structure using new TaskId format
        task_id = TaskId.from_int(999)
        task = Task(
            id=task_id,
            title="Quick Test Task",
            description="Test task for API validation",
            status=TaskStatus.todo(),
            priority=Priority.medium(),
            assignees=["qa_engineer"],
            labels=["quick-test"],
            subtasks=[]
        )
        
        # Validate task structure (TaskId is now in YYYYMMDDXXX format)
        assert task.id.value.endswith("999")  # Should end with 999
        assert task.title == "Quick Test Task"
        assert task.description == "Test task for API validation"
        assert task.status.value == "todo"
        assert task.priority.value == "medium"
        assert "qa_engineer" in task.assignees
        assert "quick-test" in task.labels
        assert len(task.subtasks) == 0
        
    except Exception as e:
        pytest.fail(f"Basic task creation structure test failed: {e}")


@pytest.mark.quick
@pytest.mark.mcp
def test_task_status_transitions():
    """Test basic task status transition validation."""
    try:
        from fastmcp.task_management.domain.value_objects.task_status import TaskStatus, TaskStatusEnum
        
        # Test all valid status values
        valid_statuses = [
            TaskStatusEnum.TODO,
            TaskStatusEnum.IN_PROGRESS,
            TaskStatusEnum.DONE,
            TaskStatusEnum.CANCELLED
        ]
        
        for status_enum in valid_statuses:
            status = TaskStatus(status_enum.value)
            assert status.value == status_enum.value
            assert str(status) == status_enum.value
            
    except Exception as e:
        pytest.fail(f"Task status transitions test failed: {e}")


@pytest.mark.quick
@pytest.mark.mcp
def test_priority_levels():
    """Test basic priority level validation."""
    try:
        from fastmcp.task_management.domain.value_objects.priority import Priority, PriorityLevel
        
        # Test all valid priority levels
        valid_priorities = [
            PriorityLevel.LOW,
            PriorityLevel.MEDIUM,
            PriorityLevel.HIGH,
            PriorityLevel.CRITICAL
        ]
        
        for priority_enum in valid_priorities:
            priority = Priority(priority_enum.label)
            assert priority.value == priority_enum.label
            assert str(priority) == priority_enum.label
            
    except Exception as e:
        pytest.fail(f"Priority levels test failed: {e}")


@pytest.mark.quick
@pytest.mark.mcp
def test_task_id_validation():
    """Test basic task ID validation with new format."""
    try:
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        
        # Test valid task IDs using from_int method for backward compatibility
        valid_int_ids = [1, 100, 999]
        
        for task_id_value in valid_int_ids:
            task_id = TaskId.from_int(task_id_value)
            assert task_id.value.endswith(f"{task_id_value:03d}")  # Should end with zero-padded number
            
        # Test valid YYYYMMDDXXX format task IDs
        valid_string_ids = ["20250618001", "20250618999"]
        
        for task_id_value in valid_string_ids:
            task_id = TaskId(task_id_value)
            assert task_id.value == task_id_value
            
    except Exception as e:
        pytest.fail(f"Task ID validation test failed: {e}")


@pytest.mark.quick
@pytest.mark.mcp
def test_use_case_instantiation():
    """Test that use cases can be instantiated with mock repository."""
    try:
        from fastmcp.task_management.application.use_cases.create_task import CreateTaskUseCase
        from fastmcp.task_management.application.use_cases.get_task import GetTaskUseCase
        from fastmcp.task_management.application.use_cases.list_tasks import ListTasksUseCase
        from fastmcp.task_management.application.use_cases.update_task import UpdateTaskUseCase
        from fastmcp.task_management.application.use_cases.delete_task import DeleteTaskUseCase
        from fastmcp.task_management.application.use_cases.search_tasks import SearchTasksUseCase
        from unittest.mock import Mock
        
        # Mock repository and auto rule generator for testing
        mock_repo = Mock()
        mock_auto_rule_gen = Mock()
        
        # Test use case instantiation
        use_cases = [
            CreateTaskUseCase(mock_repo),
            GetTaskUseCase(mock_repo, mock_auto_rule_gen),
            ListTasksUseCase(mock_repo),
            UpdateTaskUseCase(mock_repo),
            DeleteTaskUseCase(mock_repo),
            SearchTasksUseCase(mock_repo)
        ]
        
        for use_case in use_cases:
            assert use_case is not None
            assert hasattr(use_case, 'execute')
            
    except Exception as e:
        pytest.fail(f"Use case instantiation test failed: {e}")


@pytest.mark.quick
@pytest.mark.mcp
def test_dto_structure():
    """Test basic DTO structure validation."""
    try:
        from fastmcp.task_management.application.dtos.task_dto import CreateTaskRequest, UpdateTaskRequest, TaskResponse
        
        # Test CreateTaskRequest
        create_dto = CreateTaskRequest(
            title="Test Task",
            description="Test Description",
            project_id="test_project",
            priority="high",
            assignees=["qa_engineer"],  # This will be transformed to functional_tester_agent
            labels=["test"]
        )
        
        assert create_dto.title == "Test Task"
        assert create_dto.description == "Test Description"
        assert create_dto.priority == "high"
        assert "@functional_tester_agent" in create_dto.assignees  # Expect the transformed role
        assert "test" in create_dto.labels
        
        # Test UpdateTaskRequest
        update_dto = UpdateTaskRequest(
            task_id=1,
            title="Updated Task",
            status="in_progress"
        )
        
        assert update_dto.task_id == 1
        assert update_dto.title == "Updated Task"
        assert update_dto.status == "in_progress"
        
    except Exception as e:
        pytest.fail(f"DTO structure test failed: {e}")


@pytest.mark.quick
@pytest.mark.mcp
def test_domain_events_structure():
    """Test basic domain events structure."""
    try:
        from fastmcp.task_management.domain.events.task_events import TaskCreated, TaskUpdated, TaskRetrieved, TaskDeleted
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        from datetime import datetime
        
        task_id = TaskId.from_int(1)
        now = datetime.now()
        
        # Test event creation
        events = [
            TaskCreated(task_id, "Test Task", now),
            TaskUpdated(task_id, "status", "todo", "in_progress", now),
            TaskRetrieved(task_id, {"title": "Test"}, now),
            TaskDeleted(task_id, "Test Task", now)
        ]
        
        for event in events:
            assert event is not None
            assert hasattr(event, 'task_id')
            assert event.task_id == task_id
            
    except Exception as e:
        pytest.fail(f"Domain events structure test failed: {e}")


@pytest.mark.quick
def test_json_serialization_basic():
    """Test basic JSON serialization capabilities."""
    try:
        import json
        
        # Test basic task-like structure serialization
        task_data = {
            "id": 1,
            "title": "Test Task",
            "description": "Test Description",
            "status": "todo",
            "priority": "high",
            "assignees": ["qa_engineer"],
            "labels": ["test"],
            "subtasks": []
        }
        
        # Test serialization
        json_str = json.dumps(task_data)
        assert json_str is not None
        
        # Test deserialization
        parsed_data = json.loads(json_str)
        assert parsed_data == task_data
        
    except Exception as e:
        pytest.fail(f"JSON serialization test failed: {e}") 