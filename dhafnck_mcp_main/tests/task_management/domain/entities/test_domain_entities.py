"""
Unit Test: Domain Entities Testing
Task 2.1 - Domain Entities Validation
Duration: 1.5 hours
"""

import pytest
import sys
import os
from datetime import datetime
from unittest.mock import Mock

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


class TestTaskEntity:
    """Test cases for Task domain entity."""
    
    @pytest.fixture
    def valid_task_data(self):
        """Valid task data for testing."""
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
        from fastmcp.task_management.domain.value_objects.priority import Priority
        
        return {
            'id': TaskId.from_int(1),
            'title': 'Test Task',
            'description': 'Test Description',
            'status': TaskStatus.todo(),
            'priority': Priority.medium()
        }
    
    @pytest.fixture
    def task_entity(self, valid_task_data):
        """Task entity instance for testing."""
        from fastmcp.task_management.domain.entities.task import Task
        return Task(**valid_task_data)
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_creation_with_valid_data(self, valid_task_data):
        """Test task creation with valid data."""
        from fastmcp.task_management.domain.entities.task import Task
        
        task = Task(**valid_task_data)
        
        assert task.id.value.endswith("1")  # TaskId format: 20250618001
        assert task.title == 'Test Task'
        assert task.description == 'Test Description'
        assert str(task.status) == 'todo'
        assert str(task.priority) == 'medium'
        assert task.created_at is not None
        assert task.updated_at is not None
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_validation_empty_title(self, valid_task_data):
        """Test task validation fails with empty title."""
        from fastmcp.task_management.domain.entities.task import Task
        
        valid_task_data['title'] = ''
        
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            Task(**valid_task_data)
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_validation_empty_description(self, valid_task_data):
        """Test task validation fails with empty description."""
        from fastmcp.task_management.domain.entities.task import Task
        
        valid_task_data['description'] = ''
        
        with pytest.raises(ValueError, match="Task description cannot be empty"):
            Task(**valid_task_data)
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_validation_title_too_long(self, valid_task_data):
        """Test task validation fails with title too long."""
        from fastmcp.task_management.domain.entities.task import Task
        
        valid_task_data['title'] = 'x' * 201  # Exceeds 200 character limit
        
        with pytest.raises(ValueError, match="Task title cannot exceed 200 characters"):
            Task(**valid_task_data)
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_validation_description_too_long(self, valid_task_data):
        """Test task validation fails with description too long."""
        from fastmcp.task_management.domain.entities.task import Task
        
        valid_task_data['description'] = 'x' * 1001  # Exceeds 1000 character limit
        
        with pytest.raises(ValueError, match="Task description cannot exceed 1000 characters"):
            Task(**valid_task_data)
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_update_status_valid_transition(self, task_entity):
        """Test task status update with valid transition."""
        from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
        
        # TODO -> IN_PROGRESS is valid
        new_status = TaskStatus.in_progress()
        task_entity.update_status(new_status)
        
        assert str(task_entity.status) == 'in_progress'
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_update_status_invalid_transition(self, task_entity):
        """Test task status update with invalid transition."""
        from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
        
        # TODO -> DONE is invalid (must go through in_progress)
        new_status = TaskStatus.done()
        
        with pytest.raises(ValueError, match="Cannot transition from"):
            task_entity.update_status(new_status)
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_update_priority(self, task_entity):
        """Test task priority update."""
        from fastmcp.task_management.domain.value_objects.priority import Priority
        
        new_priority = Priority.high()
        task_entity.update_priority(new_priority)
        
        assert str(task_entity.priority) == 'high'
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_update_title_valid(self, task_entity):
        """Test task title update with valid data."""
        new_title = "Updated Task Title"
        task_entity.update_title(new_title)
        
        assert task_entity.title == new_title
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_update_title_empty(self, task_entity):
        """Test task title update with empty title fails."""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            task_entity.update_title("")
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_update_description_valid(self, task_entity):
        """Test task description update with valid data."""
        new_description = "Updated Task Description"
        task_entity.update_description(new_description)
        
        assert task_entity.description == new_description
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_update_description_empty(self, task_entity):
        """Test task description update with empty description fails."""
        with pytest.raises(ValueError, match="Task description cannot be empty"):
            task_entity.update_description("")
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_dependency_management(self, task_entity):
        """Test task dependency management."""
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        
        dep_id = TaskId.from_int(2)
        
        # Add dependency
        task_entity.add_dependency(dep_id)
        assert dep_id in task_entity.dependencies
        
        # Remove dependency
        task_entity.remove_dependency(dep_id)
        assert dep_id not in task_entity.dependencies
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_self_dependency_prevention(self, task_entity):
        """Test task cannot depend on itself."""
        with pytest.raises(ValueError, match="Task cannot depend on itself"):
            task_entity.add_dependency(task_entity.id)
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_label_management(self, task_entity):
        """Test task label management."""
        # Add label
        task_entity.add_label("urgent")
        assert "urgent" in task_entity.labels
        
        # Remove label
        task_entity.remove_label("urgent")
        assert "urgent" not in task_entity.labels
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_overdue_check(self, task_entity):
        """Test task overdue checking."""
        from datetime import datetime, timedelta
        
        # Not overdue without due date
        assert not task_entity.is_overdue()
        
        # Set past due date
        past_date = (datetime.now() - timedelta(days=1)).isoformat()
        task_entity.due_date = past_date
        assert task_entity.is_overdue()
        
        # Set future due date
        future_date = (datetime.now() + timedelta(days=1)).isoformat()
        task_entity.due_date = future_date
        assert not task_entity.is_overdue()
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_can_be_started(self, task_entity):
        """Test task can be started logic."""
        # TODO status can be started
        assert task_entity.can_be_started()
        
        # IN_PROGRESS status cannot be started
        from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
        task_entity.status = TaskStatus.in_progress()
        assert not task_entity.can_be_started()
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_to_dict_conversion(self, task_entity):
        """Test task to dictionary conversion."""
        task_dict = task_entity.to_dict()
        
        assert task_dict['id'].endswith('001')  # TaskId format: YYYYMMDD001
        assert task_dict['title'] == 'Test Task'
        assert task_dict['description'] == 'Test Description'
        assert task_dict['status'] == 'todo'
        assert task_dict['priority'] == 'medium'
        assert 'created_at' in task_dict
        assert 'updated_at' in task_dict
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_factory_method(self):
        """Test task factory method."""
        from fastmcp.task_management.domain.entities.task import Task
        from fastmcp.task_management.domain.value_objects.task_id import TaskId
        
        task = Task.create(
            id=TaskId.from_int(1),
            title="Factory Task",
            description="Created via factory"
        )
        
        assert task.title == "Factory Task"
        assert str(task.status) == "todo"
        assert str(task.priority) == "medium"
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_domain_events_generation(self, task_entity):
        """Test that task operations generate domain events."""
        # Clear any existing events
        task_entity.get_events()
        
        # Update status should generate event
        from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
        task_entity.update_status(TaskStatus.in_progress())
        
        events = task_entity.get_events()
        assert len(events) > 0
        
        # Check event type
        from fastmcp.task_management.domain.events.task_events import TaskUpdated
        assert isinstance(events[0], TaskUpdated)
        assert events[0].field_name == "status"
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_mark_as_retrieved_event(self, task_entity):
        """Test task mark as retrieved generates event."""
        # Clear any existing events
        task_entity.get_events()
        
        task_entity.mark_as_retrieved()
        
        events = task_entity.get_events()
        assert len(events) > 0
        
        from fastmcp.task_management.domain.events.task_events import TaskRetrieved
        assert isinstance(events[0], TaskRetrieved)
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_mark_as_deleted_event(self, task_entity):
        """Test task mark as deleted generates event."""
        # Clear any existing events
        task_entity.get_events()
        
        task_entity.mark_as_deleted()
        
        events = task_entity.get_events()
        assert len(events) > 0
        
        from fastmcp.task_management.domain.events.task_events import TaskDeleted
        assert isinstance(events[0], TaskDeleted) 