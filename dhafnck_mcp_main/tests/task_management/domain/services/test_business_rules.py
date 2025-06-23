"""
This is the canonical and only maintained test suite for all domain business rules/services.
All business rule, invariant, and edge-case tests should be added here.
Redundant or duplicate tests in other files have been removed.
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


class TestTaskBusinessRules:
    """Test cases for Task business rules and domain invariants."""
    
    @pytest.fixture
    def valid_task(self):
        """Create a valid task for testing."""
        from fastmcp.task_management.domain.entities.task import Task
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
        from fastmcp.task_management.domain.value_objects.priority import Priority
        
        return Task.create(
            id=TaskId.from_int(1),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
    
    @pytest.mark.unit
    @pytest.mark.business_rules
    def test_task_status_transition_rules(self, valid_task):
        """Test task status transition business rules."""
        from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
        
        # Rule: TODO can transition to IN_PROGRESS or CANCELLED
        assert valid_task.status.can_transition_to("in_progress")
        assert valid_task.status.can_transition_to("cancelled")
        assert not valid_task.status.can_transition_to("done")
        assert not valid_task.status.can_transition_to("review")
        
        # Move to IN_PROGRESS
        valid_task.update_status(TaskStatus.in_progress())
        
        # Rule: IN_PROGRESS can transition to BLOCKED, REVIEW, TESTING, or CANCELLED
        assert valid_task.status.can_transition_to("blocked")
        assert valid_task.status.can_transition_to("review")
        assert valid_task.status.can_transition_to("testing")
        assert valid_task.status.can_transition_to("cancelled")
        assert not valid_task.status.can_transition_to("todo")
        
        # Move to REVIEW
        valid_task.update_status(TaskStatus.review())
        
        # Rule: REVIEW can transition to IN_PROGRESS, TESTING, DONE, or CANCELLED
        assert valid_task.status.can_transition_to("in_progress")
        assert valid_task.status.can_transition_to("testing")
        assert valid_task.status.can_transition_to("done")
        assert valid_task.status.can_transition_to("cancelled")
        
        # Move to DONE
        valid_task.update_status(TaskStatus.done())
        
        # Rule: DONE is terminal state - no transitions allowed
        assert not valid_task.status.can_transition_to("todo")
        assert not valid_task.status.can_transition_to("in_progress")
        assert not valid_task.status.can_transition_to("review")
        assert not valid_task.status.can_transition_to("cancelled")
    
    @pytest.mark.unit
    @pytest.mark.business_rules
    def test_task_cancelled_state_rules(self, valid_task):
        """Test cancelled task business rules."""
        from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
        
        # Move to CANCELLED
        valid_task.update_status(TaskStatus.cancelled())
        
        # Rule: CANCELLED can only transition back to TODO (reopen)
        assert valid_task.status.can_transition_to("todo")
        assert not valid_task.status.can_transition_to("in_progress")
        assert not valid_task.status.can_transition_to("done")
        
        # Reopen task
        valid_task.update_status(TaskStatus.todo())
        assert str(valid_task.status) == "todo"
    
    @pytest.mark.unit
    @pytest.mark.business_rules
    def test_task_blocked_state_rules(self, valid_task):
        """Test blocked task business rules."""
        from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
        
        # Move to IN_PROGRESS first
        valid_task.update_status(TaskStatus.in_progress())
        
        # Move to BLOCKED
        valid_task.update_status(TaskStatus.blocked())
        
        # Rule: BLOCKED can transition to IN_PROGRESS or CANCELLED
        assert valid_task.status.can_transition_to("in_progress")
        assert valid_task.status.can_transition_to("cancelled")
        assert not valid_task.status.can_transition_to("done")
        assert not valid_task.status.can_transition_to("review")
    
    @pytest.mark.unit
    @pytest.mark.business_rules
    def test_task_title_validation_rules(self, valid_task):
        """Test task title validation business rules."""
        # Rule: Title cannot be empty
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            valid_task.update_title("")
        
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            valid_task.update_title("   ")  # Only whitespace
        
        # Rule: Title cannot exceed 200 characters
        long_title = "x" * 201
        with pytest.raises(ValueError, match="Task title cannot exceed 200 characters"):
            from fastmcp.task_management.domain.entities.task import Task
            from fastmcp.task_management.domain.value_objects.task_id import TaskId
            from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
            from fastmcp.task_management.domain.value_objects.priority import Priority
            
            Task(
                id=TaskId.from_int(2),
                title=long_title,
                description="Test",
                status=TaskStatus.todo(),
                priority=Priority.medium()
            )
    
    @pytest.mark.unit
    @pytest.mark.business_rules
    def test_task_description_validation_rules(self, valid_task):
        """Test task description validation business rules."""
        # Rule: Description cannot be empty
        with pytest.raises(ValueError, match="Task description cannot be empty"):
            valid_task.update_description("")
        
        with pytest.raises(ValueError, match="Task description cannot be empty"):
            valid_task.update_description("   ")  # Only whitespace
        
        # Rule: Description cannot exceed 1000 characters
        long_description = "x" * 1001
        with pytest.raises(ValueError, match="Task description cannot exceed 1000 characters"):
            from fastmcp.task_management.domain.entities.task import Task
            from fastmcp.task_management.domain.value_objects.task_id import TaskId
            from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
            from fastmcp.task_management.domain.value_objects.priority import Priority
            
            Task(
                id=TaskId.from_int(2),
                title="Test",
                description=long_description,
                status=TaskStatus.todo(),
                priority=Priority.medium()
            )
    
    @pytest.mark.unit
    @pytest.mark.business_rules
    def test_task_dependency_rules(self, valid_task):
        """Test task dependency business rules."""
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        
        # Rule: Task cannot depend on itself
        with pytest.raises(ValueError, match="Task cannot depend on itself"):
            valid_task.add_dependency(valid_task.id)
        
        # Rule: Dependencies can be added and removed
        dep_id = TaskId.from_int(2)
        valid_task.add_dependency(dep_id)
        assert dep_id in valid_task.dependencies
        
        # Rule: Adding same dependency twice should not duplicate
        valid_task.add_dependency(dep_id)
        dependency_count = sum(1 for dep in valid_task.dependencies if dep == dep_id)
        assert dependency_count == 1
        
        # Rule: Dependencies can be removed
        valid_task.remove_dependency(dep_id)
        assert dep_id not in valid_task.dependencies
    
    @pytest.mark.unit
    @pytest.mark.business_rules
    def test_task_label_management_rules(self, valid_task):
        """Test task label management business rules."""
        # Rule: Labels can be added
        valid_task.add_label("urgent")
        assert "urgent" in valid_task.labels
        
        # Rule: Duplicate labels should not be added
        valid_task.add_label("urgent")
        label_count = sum(1 for label in valid_task.labels if label == "urgent")
        assert label_count == 1
        
        # Rule: Empty labels should not be added
        valid_task.add_label("")
        assert "" not in valid_task.labels
        
        # Rule: Labels can be removed
        valid_task.remove_label("urgent")
        assert "urgent" not in valid_task.labels
    
    @pytest.mark.unit
    @pytest.mark.business_rules
    def test_task_overdue_calculation_rules(self, valid_task):
        """Test task overdue calculation business rules."""
        # Rule: Task without due date is never overdue
        assert not valid_task.is_overdue()
        
        # Rule: Task with future due date is not overdue
        future_date = (datetime.now() + timedelta(days=1)).isoformat()
        valid_task.due_date = future_date
        assert not valid_task.is_overdue()
        
        # Rule: Task with past due date is overdue (if not done)
        past_date = (datetime.now() - timedelta(days=1)).isoformat()
        valid_task.due_date = past_date
        assert valid_task.is_overdue()
        
        # Rule: Completed task is never overdue regardless of due date
        from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
        valid_task.update_status(TaskStatus.in_progress())
        valid_task.update_status(TaskStatus.review())
        valid_task.update_status(TaskStatus.done())
        assert not valid_task.is_overdue()
    
    @pytest.mark.unit
    @pytest.mark.business_rules
    def test_task_can_be_started_rules(self, valid_task):
        """Test task can be started business rules."""
        from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
        
        # Rule: TODO tasks can be started
        assert valid_task.can_be_started()
        
        # Rule: IN_PROGRESS tasks cannot be started (already started)
        valid_task.update_status(TaskStatus.in_progress())
        assert not valid_task.can_be_started()
        
        # Rule: DONE tasks cannot be started
        valid_task.update_status(TaskStatus.review())
        valid_task.update_status(TaskStatus.done())
        assert not valid_task.can_be_started()
        
        # Rule: CANCELLED tasks cannot be started (must be reopened first)
        from fastmcp.task_management.domain.entities.task import Task
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        from fastmcp.task_management.domain.value_objects.priority import Priority
        
        cancelled_task = Task(
            id=TaskId.from_int(2),
            title="Cancelled Task",
            description="Test",
            status=TaskStatus.cancelled(),
            priority=Priority.medium()
        )
        assert not cancelled_task.can_be_started()
    
    @pytest.mark.unit
    @pytest.mark.business_rules
    def test_priority_ordering_rules(self):
        """Test priority ordering business rules."""
        from fastmcp.task_management.domain.value_objects.priority import Priority
        
        # Rule: Priority ordering follows business importance
        low = Priority.low()
        medium = Priority.medium()
        high = Priority.high()
        urgent = Priority.urgent()
        critical = Priority.critical()
        
        # Verify ordering
        priorities = [low, medium, high, urgent, critical]
        sorted_priorities = sorted(priorities)
        assert sorted_priorities == priorities
        
        # Rule: Critical priority is highest
        assert critical.is_critical()
        assert critical > urgent
        assert critical > high
        
        # Rule: High and critical are considered high priority
        assert high.is_high_or_critical()
        assert critical.is_high_or_critical()
        assert not medium.is_high_or_critical()
    
    @pytest.mark.unit
    @pytest.mark.business_rules
    def test_task_update_timestamp_rules(self, valid_task):
        """Test task update timestamp business rules."""
        original_updated_at = valid_task.updated_at
        
        # Rule: Any update should change updated_at timestamp
        valid_task.update_title("New Title")
        assert valid_task.updated_at > original_updated_at
        
        # Rule: Multiple updates should continue updating timestamp
        second_update_time = valid_task.updated_at
        valid_task.update_description("New Description")
        assert valid_task.updated_at > second_update_time
    
    @pytest.mark.unit
    @pytest.mark.business_rules
    def test_domain_event_generation_rules(self, valid_task):
        """Test domain event generation business rules."""
        from fastmcp.task_management.domain.events.task_events import TaskUpdated, TaskRetrieved, TaskDeleted
        
        # Clear any existing events
        valid_task.get_events()
        
        # Rule: Updates should generate domain events
        valid_task.update_title("New Title")
        events = valid_task.get_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskUpdated)
        assert events[0].field_name == "title"
        
        # Rule: Retrieval should generate domain event
        valid_task.mark_as_retrieved()
        events = valid_task.get_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskRetrieved)
        
        # Rule: Deletion should generate domain event
        valid_task.mark_as_deleted()
        events = valid_task.get_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskDeleted)
    
    @pytest.mark.unit
    @pytest.mark.business_rules
    def test_task_creation_defaults_rules(self):
        """Test task creation default values business rules."""
        from fastmcp.task_management.domain.entities.task import Task
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        
        # Rule: Factory method should set default status and priority
        task = Task.create(
            id=TaskId.from_int(1),
            title="Test Task",
            description="Test Description"
        )
        
        assert str(task.status) == "todo"
        assert str(task.priority) == "medium"
        assert task.created_at is not None
        assert task.updated_at is not None
    
    @pytest.mark.unit
    @pytest.mark.business_rules
    def test_value_object_immutability_rules(self):
        """Test value object immutability business rules."""
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
        from fastmcp.task_management.domain.value_objects.priority import Priority
        
        # Rule: Value objects should be immutable (frozen dataclasses)
        task_id = TaskId.from_int(1)
        with pytest.raises(AttributeError):
            task_id.value = "2"
        
        task_status = TaskStatus.todo()
        with pytest.raises(AttributeError):
            task_status.value = "done"
        
        priority = Priority.high()
        with pytest.raises(AttributeError):
            priority.value = "low"
    
    @pytest.mark.unit
    @pytest.mark.business_rules
    def test_task_id_validation_rules(self):
        """Test TaskId validation business rules."""
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        
        # Rule: TaskId must follow YYYYMMDDXXX format
        valid_id = "20250618001"
        task_id = TaskId(valid_id)
        assert task_id.value == valid_id
        
        # Rule: TaskId can be created from integers using from_int
        task_id_from_int = TaskId.from_int(123)
        assert task_id_from_int.value.endswith("123")
        
        # Rule: Invalid TaskId values should raise errors
        invalid_ids = [None, "", "   ", "123", "invalid", "2025061800000"]  # Too long
        for invalid_id in invalid_ids:
            with pytest.raises(ValueError):
                TaskId(invalid_id) 