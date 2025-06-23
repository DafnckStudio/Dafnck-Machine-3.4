"""
Unit Test: Value Objects Testing
Task 2.1 - Domain Value Objects Validation
Duration: Part of 1.5 hours
"""

import pytest
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


class TestTaskId:
    """Test cases for TaskId value object."""
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_id_creation_with_integer(self):
        """Test TaskId creation with integer value."""
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        
        task_id = TaskId.from_int(1)
        assert task_id.value.endswith('001')  # YYYYMMDD001 format
        assert str(task_id).endswith('001')
        assert int(task_id) == 1  # Should return the sequence part
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_id_creation_with_string(self):
        """Test TaskId creation with string value (YYYYMMDDXXX format)."""
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        
        # Use valid YYYYMMDDXXX format
        task_id = TaskId("20250618001")
        assert task_id.value == "20250618001"
        assert str(task_id) == "20250618001"
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_id_validation_none_value(self):
        """Test TaskId validation fails with None value."""
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        
        with pytest.raises(ValueError, match="Task ID cannot be None"):
            TaskId(None)
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_id_validation_empty_string(self):
        """Test TaskId validation fails with empty string."""
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        
        with pytest.raises(ValueError, match="Task ID cannot be empty or whitespace"):
            TaskId("")
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_id_validation_negative_integer(self):
        """Test TaskId validation fails with negative integer."""
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        
        with pytest.raises(ValueError):
            TaskId.from_int(-1)
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_id_validation_zero_integer(self):
        """Test TaskId validation fails with zero integer."""
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        
        with pytest.raises(ValueError):
            TaskId.from_int(0)
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_id_validation_invalid_type(self):
        """Test TaskId validation fails with invalid type."""
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        
        with pytest.raises(ValueError):
            TaskId("invalid-format")
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_id_factory_methods(self):
        """Test TaskId factory methods."""
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        
        # From string (valid YYYYMMDDXXX format)
        task_id_str = TaskId.from_string("20250618042")
        assert task_id_str.value == "20250618042"
        
        # From int
        task_id_int = TaskId.from_int(42)
        assert task_id_int.value.endswith('042')
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_id_string_to_int_conversion(self):
        """Test TaskId string to int conversion."""
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        
        # Valid YYYYMMDDXXX format can be converted to sequence number
        task_id = TaskId("20250618123")
        assert int(task_id) == 123
        
        # Test from_int method
        task_id_from_int = TaskId.from_int(456)
        assert int(task_id_from_int) == 456

    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_id_properties(self):
        """Test TaskId properties for date, sequence, and subtask info."""
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        
        # Main task ID
        main_task = TaskId("20250618123")
        assert main_task.date_part == "20250618"
        assert main_task.sequence_part == "123"
        assert main_task.subtask_sequence is None
        assert not main_task.is_subtask
        
        # Subtask ID
        subtask = TaskId("20250618123.456")
        assert subtask.date_part == "20250618"
        assert subtask.sequence_part == "123"
        assert subtask.subtask_sequence == "456"
        assert subtask.is_subtask
        assert subtask.parent_task_id.value == "20250618123"

    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_id_subtask_conversion(self):
        """Test subtask ID conversion to integer."""
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        
        # Subtask should combine main and sub sequence numbers
        subtask = TaskId("20250618123.456")
        # 123 * 1000 + 456 = 123456
        assert int(subtask) == 123456

    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_id_parent_task_error(self):
        """Test error when getting parent task ID from main task."""
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        
        main_task = TaskId("20250618123")
        with pytest.raises(ValueError, match="Cannot get parent task ID for main task"):
            main_task.parent_task_id

    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_id_generate_new(self):
        """Test generating new task IDs."""
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        from datetime import datetime
        
        TaskId.reset_counter()

        # Generate new ID without existing IDs
        new_id = TaskId.generate_new()
        assert new_id.date_part == TaskId.from_int(1).date_part  # Same date
        assert not new_id.is_subtask
        # With a reset counter, the first ID should have sequence "001"
        assert new_id.sequence_part == "001"
        assert len(new_id.sequence_part) == 3  # Should be 3 digits
        
        # Generate new ID with existing IDs using current date
        current_date = datetime.now().strftime('%Y%m%d')
        existing_ids = [f"{current_date}001", f"{current_date}002"]
        new_id_2 = TaskId.generate_new(existing_ids)
        assert new_id_2.sequence_part == "003"

    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_id_generate_subtask(self):
        """Test generating subtask IDs."""
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        
        parent = TaskId("20250618123")
        
        # Generate new subtask without existing subtasks
        subtask = TaskId.generate_subtask(parent)
        assert subtask.value == "20250618123.001"
        assert subtask.is_subtask
        
        # Generate subtask with existing subtasks
        existing_subtasks = ["20250618123.001", "20250618123.002"]
        new_subtask = TaskId.generate_subtask(parent, existing_subtasks)
        assert new_subtask.value == "20250618123.003"

    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_id_generate_subtask_error(self):
        """Test error when creating subtask of subtask."""
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        
        subtask = TaskId("20250618123.001")
        with pytest.raises(ValueError, match="Cannot create subtask of a subtask"):
            TaskId.generate_subtask(subtask)

    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_id_validation_edge_cases(self):
        """Test TaskId validation edge cases."""
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        
        # Test invalid date in YYYYMMDDXXX format
        with pytest.raises(ValueError):
            TaskId("20251301001")  # Invalid month 13
        
        # Test invalid date in subtask format
        with pytest.raises(ValueError):
            TaskId("20251301001.001")  # Invalid month 13

    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_id_from_int_validation(self):
        """Test TaskId.from_int validation."""
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        
        # Test non-integer input
        with pytest.raises(ValueError, match="Value must be an integer"):
            TaskId.from_int("not_an_int")
        
        # Test sequence too large
        with pytest.raises(ValueError, match="Task ID sequence cannot exceed 999"):
            TaskId.from_int(1000)

    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_id_max_sequences(self):
        """Test maximum sequences per day and per task."""
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        from datetime import datetime
        
        TaskId.reset_counter()

        current_date = datetime.now().strftime('%Y%m%d')
        
        # Create 999 existing IDs (maximum)
        existing_ids = [f"{current_date}{i:03d}" for i in range(1, 1000)]
        
        # Should raise error when trying to generate 1000th ID
        with pytest.raises(ValueError, match="Maximum tasks per day \\(999\\) exceeded"):
            TaskId.generate_new(existing_ids)
        
        # Test maximum subtasks per task
        parent = TaskId(f"{current_date}001")
        existing_subtasks = [f"{current_date}001.{i:03d}" for i in range(1, 1000)]
        
        with pytest.raises(ValueError, match="Maximum subtasks per task \\(999\\) exceeded"):
            TaskId.generate_subtask(parent, existing_subtasks)


class TestTaskStatus:
    """Test cases for TaskStatus value object."""
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_status_creation_valid_values(self):
        """Test TaskStatus creation with valid values."""
        from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
        
        valid_statuses = ["todo", "in_progress", "blocked", "review", "testing", "done", "cancelled"]
        
        for status in valid_statuses:
            task_status = TaskStatus(status)
            assert task_status.value == status
            assert str(task_status) == status
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_status_validation_empty_value(self):
        """Test TaskStatus validation fails with empty value."""
        from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
        
        with pytest.raises(ValueError, match="Task status cannot be empty"):
            TaskStatus("")
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_status_validation_invalid_value(self):
        """Test TaskStatus validation fails with invalid value."""
        from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
        
        with pytest.raises(ValueError, match="Invalid task status"):
            TaskStatus("invalid_status")
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_status_factory_methods(self):
        """Test TaskStatus factory methods."""
        from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
        
        assert str(TaskStatus.todo()) == "todo"
        assert str(TaskStatus.in_progress()) == "in_progress"
        assert str(TaskStatus.blocked()) == "blocked"
        assert str(TaskStatus.review()) == "review"
        assert str(TaskStatus.testing()) == "testing"
        assert str(TaskStatus.done()) == "done"
        assert str(TaskStatus.cancelled()) == "cancelled"
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_status_state_checks(self):
        """Test TaskStatus state checking methods."""
        from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
        
        todo_status = TaskStatus.todo()
        assert todo_status.is_todo()
        assert not todo_status.is_in_progress()
        assert not todo_status.is_done()
        
        in_progress_status = TaskStatus.in_progress()
        assert not in_progress_status.is_todo()
        assert in_progress_status.is_in_progress()
        assert not in_progress_status.is_done()
        
        done_status = TaskStatus.done()
        assert not done_status.is_todo()
        assert not done_status.is_in_progress()
        assert done_status.is_done()
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_status_valid_transitions(self):
        """Test TaskStatus valid transitions."""
        from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
        
        todo_status = TaskStatus.todo()
        assert todo_status.can_transition_to("in_progress")
        assert todo_status.can_transition_to("cancelled")
        assert not todo_status.can_transition_to("done")  # Must go through in_progress
        
        in_progress_status = TaskStatus.in_progress()
        assert in_progress_status.can_transition_to("blocked")
        assert in_progress_status.can_transition_to("review")
        assert in_progress_status.can_transition_to("testing")
        assert in_progress_status.can_transition_to("cancelled")
        assert not in_progress_status.can_transition_to("todo")
        
        done_status = TaskStatus.done()
        assert not done_status.can_transition_to("todo")
        assert not done_status.can_transition_to("in_progress")
        # Done is terminal state
        
        cancelled_status = TaskStatus.cancelled()
        assert cancelled_status.can_transition_to("todo")  # Can reopen
        assert not cancelled_status.can_transition_to("done")


class TestPriority:
    """Test cases for Priority value object."""
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_priority_creation_valid_values(self):
        """Test Priority creation with valid values."""
        from fastmcp.task_management.domain.value_objects.priority import Priority
        
        valid_priorities = ["low", "medium", "high", "urgent", "critical"]
        
        for priority in valid_priorities:
            priority_obj = Priority(priority)
            assert priority_obj.value == priority
            assert str(priority_obj) == priority
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_priority_validation_empty_value(self):
        """Test Priority validation fails with empty value."""
        from fastmcp.task_management.domain.value_objects.priority import Priority
        
        with pytest.raises(ValueError, match="Priority cannot be empty"):
            Priority("")
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_priority_validation_invalid_value(self):
        """Test Priority validation fails with invalid value."""
        from fastmcp.task_management.domain.value_objects.priority import Priority
        
        with pytest.raises(ValueError, match="Invalid priority"):
            Priority("invalid_priority")
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_priority_factory_methods(self):
        """Test Priority factory methods."""
        from fastmcp.task_management.domain.value_objects.priority import Priority
        
        assert str(Priority.low()) == "low"
        assert str(Priority.medium()) == "medium"
        assert str(Priority.high()) == "high"
        assert str(Priority.urgent()) == "urgent"
        assert str(Priority.critical()) == "critical"
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_priority_ordering_comparison(self):
        """Test Priority ordering and comparison."""
        from fastmcp.task_management.domain.value_objects.priority import Priority
        
        low = Priority.low()
        medium = Priority.medium()
        high = Priority.high()
        urgent = Priority.urgent()
        critical = Priority.critical()
        
        # Test ordering
        assert low < medium < high < urgent < critical
        assert critical > urgent > high > medium > low
        
        # Test equality
        assert low <= Priority.low()
        assert medium >= Priority.medium()
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_priority_order_property(self):
        """Test Priority order property."""
        from fastmcp.task_management.domain.value_objects.priority import Priority
        
        assert Priority.low().order == 1
        assert Priority.medium().order == 2
        assert Priority.high().order == 3
        assert Priority.urgent().order == 4
        assert Priority.critical().order == 5
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_priority_state_checks(self):
        """Test Priority state checking methods."""
        from fastmcp.task_management.domain.value_objects.priority import Priority
        
        critical = Priority.critical()
        assert critical.is_critical()
        assert critical.is_high_or_critical()
        
        high = Priority.high()
        assert not high.is_critical()
        assert high.is_high_or_critical()
        
        medium = Priority.medium()
        assert not medium.is_critical()
        assert not medium.is_high_or_critical()


class TestDomainEvents:
    """Test cases for Domain Events."""
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_created_event(self):
        """Test TaskCreated domain event."""
        from fastmcp.task_management.domain.events.task_events import TaskCreated
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        from datetime import datetime
        
        task_id = TaskId.from_int(1)
        created_at = datetime.now()
        
        event = TaskCreated(
            task_id=task_id,
            title="Test Task",
            created_at=created_at
        )
        
        assert event.task_id == task_id
        assert event.title == "Test Task"
        assert event.created_at == created_at
        assert event.occurred_at is not None
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_updated_event(self):
        """Test TaskUpdated domain event."""
        from fastmcp.task_management.domain.events.task_events import TaskUpdated
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        from datetime import datetime
        
        task_id = TaskId.from_int(1)
        updated_at = datetime.now()
        
        event = TaskUpdated(
            task_id=task_id,
            field_name="title",
            old_value="Old Title",
            new_value="New Title",
            updated_at=updated_at
        )
        
        assert event.task_id == task_id
        assert event.field_name == "title"
        assert event.old_value == "Old Title"
        assert event.new_value == "New Title"
        assert event.updated_at == updated_at
        assert event.occurred_at is not None
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_retrieved_event(self):
        """Test TaskRetrieved domain event."""
        from fastmcp.task_management.domain.events.task_events import TaskRetrieved
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        from datetime import datetime
        
        task_id = TaskId.from_int(1)
        retrieved_at = datetime.now()
        task_data = {"id": 1, "title": "Test Task"}
        
        event = TaskRetrieved(
            task_id=task_id,
            task_data=task_data,
            retrieved_at=retrieved_at
        )
        
        assert event.task_id == task_id
        assert event.task_data == task_data
        assert event.retrieved_at == retrieved_at
        assert event.occurred_at is not None
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_deleted_event(self):
        """Test TaskDeleted domain event."""
        from fastmcp.task_management.domain.events.task_events import TaskDeleted
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        from datetime import datetime
        
        task_id = TaskId.from_int(1)
        deleted_at = datetime.now()
        
        event = TaskDeleted(
            task_id=task_id,
            title="Test Task",
            deleted_at=deleted_at
        )
        
        assert event.task_id == task_id
        assert event.title == "Test Task"
        assert event.deleted_at == deleted_at
        assert event.occurred_at is not None 