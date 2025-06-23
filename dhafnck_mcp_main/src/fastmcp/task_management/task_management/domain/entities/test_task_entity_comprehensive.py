"""Comprehensive tests for Task domain entity"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from fastmcp.task_management.domain.entities.task import Task
from fastmcp.task_management.domain.value_objects import TaskId, TaskStatus, Priority
from fastmcp.task_management.domain.events.task_events import TaskCreated, TaskUpdated, TaskDeleted, TaskRetrieved
from fastmcp.task_management.application.use_cases.get_task import GetTaskUseCase


class TestTaskCreation:
    """Test Task creation and validation"""
    
    def test_create_valid_task(self):
        """Test creating a valid task"""
        task = Task.create(
            id=TaskId.from_int(1),
            title="Test Task",
            description="Test Description"
        )
        
        assert task.id.value.endswith('001')  # TaskId.from_int(1) creates YYYYMMDD001 format
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.status == TaskStatus.todo()
        assert task.priority == Priority.medium()
        assert task.created_at is not None
        assert task.updated_at is not None
        
        # Check domain event
        events = task.get_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskCreated)
        assert events[0].task_id == task.id
    
    def test_create_with_custom_status_priority(self):
        """Test creating task with custom status and priority"""
        task = Task.create(
            id=TaskId.from_int(1),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.in_progress(),
            priority=Priority.high()
        )
        
        assert task.status == TaskStatus.in_progress()
        assert task.priority == Priority.high()
    
    def test_create_with_additional_fields(self):
        """Test creating task with additional fields"""
        task = Task.create(
            id=TaskId.from_int(1),
            title="Test Task",
            description="Test Description",
            details="Additional details",
            assignees=["user1"],
            labels=["label1", "label2"],
            due_date="2023-12-31"
        )
        
        assert task.details == "Additional details"
        assert "user1" in task.assignees
        assert task.labels == ["label1", "label2"]
        assert task.due_date == "2023-12-31"
    
    def test_validation_empty_title(self):
        """Test validation fails for empty title"""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            Task.create(
                id=TaskId.from_int(1),
                title="",
                description="Test Description"
            )
        
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            Task.create(
                id=TaskId.from_int(1),
                title="   ",  # whitespace only
                description="Test Description"
            )
    
    def test_validation_empty_description(self):
        """Test validation fails for empty description"""
        with pytest.raises(ValueError, match="Task description cannot be empty"):
            Task.create(
                id=TaskId.from_int(1),
                title="Test Task",
                description=""
            )
        
        with pytest.raises(ValueError, match="Task description cannot be empty"):
            Task.create(
                id=TaskId.from_int(1),
                title="Test Task",
                description="   "  # whitespace only
            )
    
    def test_validation_title_too_long(self):
        """Test validation fails for title too long"""
        long_title = "x" * 201  # 201 characters
        with pytest.raises(ValueError, match="Task title cannot exceed 200 characters"):
            Task.create(
                id=TaskId.from_int(1),
                title=long_title,
                description="Test Description"
            )
    
    def test_validation_description_too_long(self):
        """Test validation fails for description too long"""
        long_description = "x" * 1001  # 1001 characters
        with pytest.raises(ValueError, match="Task description cannot exceed 1000 characters"):
            Task.create(
                id=TaskId.from_int(1),
                title="Test Task",
                description=long_description
            )


class TestTaskUpdates:
    """Test Task update methods"""
    
    def setup_method(self):
        """Setup test task"""
        self.task = Task.create(
            id=TaskId.from_int(1),
            title="Original Title",
            description="Original Description",
            status=TaskStatus.todo(),
            priority=Priority.medium(),
            details="Original details",
            assignees=["original_user"],
            labels=["original"],
            due_date="2023-01-01"
        )
        # Clear creation events
        self.task.get_events()
    
    def test_update_status_valid_transition(self):
        """Test updating status with valid transition"""
        old_status = self.task.status
        new_status = TaskStatus.in_progress()
        
        self.task.update_status(new_status)
        
        assert self.task.status == new_status
        assert self.task.updated_at is not None
        
        # Check domain event
        events = self.task.get_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskUpdated)
        assert events[0].field_name == "status"
        assert events[0].old_value == str(old_status)
        assert events[0].new_value == str(new_status)
    
    def test_update_status_invalid_transition(self):
        """Test updating status with invalid transition"""
        # Try to go from todo directly to completed (might be invalid depending on business rules)
        # This test assumes the status validation logic exists
        with pytest.raises(ValueError):
            # This will raise ValueError during TaskStatus construction for invalid status
            self.task.update_status(TaskStatus("invalid_status"))
    
    def test_update_priority(self):
        """Test updating priority"""
        old_priority = self.task.priority
        new_priority = Priority.high()
        
        self.task.update_priority(new_priority)
        
        assert self.task.priority == new_priority
        
        # Check domain event
        events = self.task.get_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskUpdated)
        assert events[0].field_name == "priority"
        assert events[0].old_value == str(old_priority)
        assert events[0].new_value == str(new_priority)
    
    def test_update_title_valid(self):
        """Test updating title with valid value"""
        new_title = "New Title"
        
        self.task.update_title(new_title)
        
        assert self.task.title == new_title
        
        # Check domain event
        events = self.task.get_events()
        assert len(events) == 1
        assert events[0].field_name == "title"
        assert events[0].new_value == new_title
    
    def test_update_title_empty(self):
        """Test updating title with empty value fails"""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            self.task.update_title("")
        
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            self.task.update_title("   ")
    
    def test_update_description_valid(self):
        """Test updating description with valid value"""
        new_description = "New Description"
        
        self.task.update_description(new_description)
        
        assert self.task.description == new_description
        
        # Check domain event
        events = self.task.get_events()
        assert len(events) == 1
        assert events[0].field_name == "description"
        assert events[0].new_value == new_description
    
    def test_update_description_empty(self):
        """Test updating description with empty value fails"""
        with pytest.raises(ValueError, match="Task description cannot be empty"):
            self.task.update_description("")
        
        with pytest.raises(ValueError, match="Task description cannot be empty"):
            self.task.update_description("   ")
    
    def test_update_details(self):
        """Test updating details"""
        new_details = "New details"
        
        self.task.update_details(new_details)
        
        assert self.task.details == new_details
        
        # Check domain event
        events = self.task.get_events()
        assert len(events) == 1
        assert events[0].field_name == "details"
        assert events[0].new_value == new_details
    
    def test_update_estimated_effort(self):
        """Test updating estimated effort"""
        new_effort = "4 hours"
        
        self.task.update_estimated_effort(new_effort)
        
        assert self.task.estimated_effort == new_effort
        
        # Check domain event
        events = self.task.get_events()
        assert len(events) == 1
        assert events[0].field_name == "estimated_effort"
        assert events[0].new_value == new_effort
    
    def test_update_assignee(self):
        """Test updating assignees"""
        new_assignee = "new_user"
        
        self.task.update_assignees([new_assignee])
        
        assert new_assignee in self.task.assignees
        
        # Check domain event
        events = self.task.get_events()
        assert len(events) == 1
        assert events[0].field_name == "assignees"
        assert events[0].new_value == [new_assignee]
    
    # NOTE: assigned_role functionality has been removed from Task entity
    # Tasks now use assignees list instead of assigned_role field
    
    def test_update_labels(self):
        """Test updating labels"""
        new_labels = ["label1", "label2", "label3"]
        
        self.task.update_labels(new_labels)
        
        assert self.task.labels == new_labels
        
        # Check domain event
        events = self.task.get_events()
        assert len(events) == 1
        assert events[0].field_name == "labels"
        assert events[0].new_value == new_labels
    
    def test_update_due_date(self):
        """Test updating due date"""
        new_due_date = "2023-12-31"
        
        self.task.update_due_date(new_due_date)
        
        assert self.task.due_date == new_due_date
        
        # Check domain event
        events = self.task.get_events()
        assert len(events) == 1
        assert events[0].field_name == "due_date"
        assert events[0].new_value == new_due_date
    
    def test_update_details_legacy_all_fields(self):
        """Test legacy update method with all fields"""
        self.task.update_details_legacy(
            title="New Title",
            description="New Description", 
            details="New Details",
            assignees=["new_user"]
        )
        
        assert self.task.title == "New Title"
        assert self.task.description == "New Description"
        assert self.task.details == "New Details"
        assert "new_user" in self.task.assignees
        
        # Should generate events for each changed field
        events = self.task.get_events()
        assert len(events) == 4
        field_names = [event.field_name for event in events]
        assert "title" in field_names
        assert "description" in field_names
        assert "details" in field_names
        assert "assignees" in field_names
    
    def test_update_details_legacy_no_changes(self):
        """Test legacy update method with no changes"""
        self.task.update_details_legacy(
            title=self.task.title,
            description=self.task.description
        )
        
        # No events should be generated
        events = self.task.get_events()
        assert len(events) == 0
    
    def test_update_details_legacy_empty_title(self):
        """Test legacy update method with empty title fails"""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            self.task.update_details_legacy(title="")
    
    def test_update_details_legacy_empty_description(self):
        """Test legacy update method with empty description fails"""
        with pytest.raises(ValueError, match="Task description cannot be empty"):
            self.task.update_details_legacy(description="")


class TestTaskDependencies:
    """Test Task dependency management"""
    
    def setup_method(self):
        """Setup test task"""
        self.task = Task.create(
            id=TaskId.from_int(1),
            title="Test Task",
            description="Test Description"
        )
        self.dep_id = TaskId.from_int(2)
        # Clear creation events
        self.task.get_events()
    
    def test_add_dependency(self):
        """Test adding a dependency"""
        self.task.add_dependency(self.dep_id)
        
        assert self.dep_id in self.task.dependencies
        assert self.task.has_dependency(self.dep_id)
    
    def test_add_dependency_self_reference(self):
        """Test adding self as dependency fails"""
        with pytest.raises(ValueError, match="Task cannot depend on itself"):
            self.task.add_dependency(self.task.id)
    
    def test_add_dependency_duplicate(self):
        """Test adding duplicate dependency"""
        self.task.add_dependency(self.dep_id)
        initial_count = len(self.task.dependencies)
        
        # Add same dependency again
        self.task.add_dependency(self.dep_id)
        
        # Should not add duplicate
        assert len(self.task.dependencies) == initial_count
    
    def test_remove_dependency(self):
        """Test removing a dependency"""
        self.task.add_dependency(self.dep_id)
        assert self.task.has_dependency(self.dep_id)
        
        self.task.remove_dependency(self.dep_id)
        assert not self.task.has_dependency(self.dep_id)
    
    def test_remove_nonexistent_dependency(self):
        """Test removing non-existent dependency"""
        # Should not raise error
        self.task.remove_dependency(self.dep_id)
        assert not self.task.has_dependency(self.dep_id)
    
    def test_get_dependency_ids(self):
        """Test getting dependency IDs as strings"""
        dep1 = TaskId.from_int(2)
        dep2 = TaskId.from_int(3)
        
        self.task.add_dependency(dep1)
        self.task.add_dependency(dep2)
        
        dep_ids = self.task.get_dependency_ids()
        assert isinstance(dep_ids, list)
        assert str(dep1.value) in dep_ids
        assert str(dep2.value) in dep_ids
    
    def test_clear_dependencies(self):
        """Test clearing all dependencies"""
        dep1 = TaskId.from_int(2)
        dep2 = TaskId.from_int(3)
        
        self.task.add_dependency(dep1)
        self.task.add_dependency(dep2)
        assert len(self.task.dependencies) == 2
        
        self.task.clear_dependencies()
        assert len(self.task.dependencies) == 0
    
    def test_clear_dependencies_empty(self):
        """Test clearing dependencies when none exist"""
        # Should not raise error
        self.task.clear_dependencies()
        assert len(self.task.dependencies) == 0
    
    def test_has_circular_dependency(self):
        """Test checking for circular dependencies"""
        # Simple check - task depending on itself
        assert self.task.has_circular_dependency(self.task.id)
        assert not self.task.has_circular_dependency(self.dep_id)


class TestTaskLabels:
    """Test Task label management"""
    
    def setup_method(self):
        """Setup test task"""
        self.task = Task.create(
            id=TaskId.from_int(1),
            title="Test Task",
            description="Test Description"
        )
        # Clear creation events
        self.task.get_events()
    
    def test_add_label(self):
        """Test adding a label"""
        self.task.add_label("test-label")
        
        assert "test-label" in self.task.labels
    
    def test_add_duplicate_label(self):
        """Test adding duplicate label"""
        self.task.add_label("test-label")
        initial_count = len(self.task.labels)
        
        self.task.add_label("test-label")
        
        # Should not add duplicate
        assert len(self.task.labels) == initial_count
    
    def test_add_empty_label(self):
        """Test adding empty label"""
        self.task.add_label("")
        
        # Should not add empty label
        assert "" not in self.task.labels
    
    def test_remove_label(self):
        """Test removing a label"""
        self.task.add_label("test-label")
        assert "test-label" in self.task.labels
        
        self.task.remove_label("test-label")
        assert "test-label" not in self.task.labels
    
    def test_remove_nonexistent_label(self):
        """Test removing non-existent label"""
        # Should not raise error
        self.task.remove_label("nonexistent")


class TestTaskSubtasks:
    """Test Task subtask management"""
    
    def setup_method(self):
        """Setup test task"""
        self.task = Task.create(
            id=TaskId.from_int(1),
            title="Test Task",
            description="Test Description"
        )
        # Clear creation events
        self.task.get_events()
    
    def test_add_subtask_minimal(self):
        """Test adding subtask with minimal data"""
        result = self.task.add_subtask(title="Test Subtask")
        
        assert result["title"] == "Test Subtask"
        assert len(self.task.subtasks) == 1
        added_subtask = self.task.subtasks[0]
        assert added_subtask["title"] == "Test Subtask"
        assert "id" in added_subtask
        assert added_subtask["completed"] is False
        assert added_subtask["description"] == ""
        assert added_subtask["assignees"] == []
        
        # Check domain event
        events = self.task.get_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskUpdated)
        assert events[0].field_name == "subtasks"
    
    def test_add_subtask_with_id(self):
        """Test adding subtask with existing ID"""
        result = self.task.add_subtask(title="Test Subtask", id="custom-id")
        
        assert result["title"] == "Test Subtask"
        added_subtask = self.task.subtasks[0]
        assert added_subtask["id"] == "custom-id"
    
    def test_add_subtask_no_title(self):
        """Test adding subtask without title fails"""
        with pytest.raises(ValueError, match="Either subtask_title or title must be provided"):
            self.task.add_subtask()
        
        with pytest.raises(ValueError, match="Subtask must have a title"):
            self.task.add_subtask(title="")
    
    def test_add_multiple_subtasks_auto_id(self):
        """Test adding multiple subtasks with auto-generated IDs"""
        self.task.add_subtask(title="Subtask 1")
        self.task.add_subtask(title="Subtask 2")
        
        assert len(self.task.subtasks) == 2
        
        # IDs should be different
        id1 = self.task.subtasks[0]["id"]
        id2 = self.task.subtasks[1]["id"]
        assert id1 != id2
    
    def test_remove_subtask_by_string_id(self):
        """Test removing subtask by string ID"""
        self.task.add_subtask(title="Test Subtask", id="test-id")
        
        result = self.task.remove_subtask("test-id")
        
        assert result is True
        assert len(self.task.subtasks) == 0
        
        # Check domain event
        events = self.task.get_events()
        # Should have add event and remove event
        assert len(events) == 2
        assert events[1].field_name == "subtasks"
        assert events[1].old_value == "subtask_removed"
    
    def test_remove_subtask_by_int_id(self):
        """Test removing subtask by integer ID"""
        subtask = {"id": 1, "title": "Test Subtask"}
        self.task.add_subtask(subtask)
        
        result = self.task.remove_subtask(1)
        
        assert result is True
        assert len(self.task.subtasks) == 0
    
    def test_remove_nonexistent_subtask(self):
        """Test removing non-existent subtask"""
        result = self.task.remove_subtask("nonexistent")
        
        assert result is False
    
    def test_update_subtask(self):
        """Test updating a subtask"""
        subtask = {"id": "test-id", "title": "Original Title"}
        self.task.add_subtask(subtask)
        
        updates = {"title": "Updated Title", "completed": True}
        result = self.task.update_subtask("test-id", updates)
        
        assert result is True
        updated_subtask = self.task.subtasks[0]
        assert updated_subtask["title"] == "Updated Title"
        assert updated_subtask["completed"] is True
    
    def test_update_nonexistent_subtask(self):
        """Test updating non-existent subtask"""
        result = self.task.update_subtask("nonexistent", {"title": "New Title"})
        
        assert result is False
    
    def test_complete_subtask(self):
        """Test completing a subtask"""
        subtask = {"id": "test-id", "title": "Test Subtask"}
        self.task.add_subtask(subtask)
        
        result = self.task.complete_subtask("test-id")
        
        assert result is True
        assert self.task.subtasks[0]["completed"] is True
    
    def test_get_subtask(self):
        """Test getting a subtask by ID"""
        subtask = {"id": "test-id", "title": "Test Subtask"}
        self.task.add_subtask(subtask)
        
        found_subtask = self.task.get_subtask("test-id")
        
        assert found_subtask is not None
        assert found_subtask["title"] == "Test Subtask"
        
        # Non-existent subtask
        assert self.task.get_subtask("nonexistent") is None
    
    def test_subtask_ids_match_string_comparison(self):
        """Test subtask ID matching with string comparison"""
        assert self.task._subtask_ids_match("test-id", "test-id")
        assert not self.task._subtask_ids_match("test-id", "other-id")
    
    def test_subtask_ids_match_int_comparison(self):
        """Test subtask ID matching with integer comparison"""
        assert self.task._subtask_ids_match(1, 1)
        assert self.task._subtask_ids_match("1", 1)
        assert self.task._subtask_ids_match(1, "1")
        assert not self.task._subtask_ids_match(1, 2)
    
    def test_subtask_ids_match_invalid_comparison(self):
        """Test subtask ID matching with invalid values"""
        assert not self.task._subtask_ids_match("invalid", None)
        assert not self.task._subtask_ids_match(None, "invalid")
    
    def test_get_subtask_progress_empty(self):
        """Test getting subtask progress with no subtasks"""
        progress = self.task.get_subtask_progress()
        
        assert progress["total"] == 0
        assert progress["completed"] == 0
        assert progress["percentage"] == 0
    
    def test_get_subtask_progress_with_subtasks(self):
        """Test getting subtask progress with subtasks"""
        self.task.add_subtask({"title": "Subtask 1"})
        self.task.add_subtask({"title": "Subtask 2", "completed": True})
        self.task.add_subtask({"title": "Subtask 3", "completed": True})
        
        progress = self.task.get_subtask_progress()
        
        assert progress["total"] == 3
        assert progress["completed"] == 2
        assert progress["percentage"] == 66.7
    
    def test_migrate_subtask_ids(self):
        """Test migrating old integer subtask IDs to hierarchical format"""
        # Add subtasks with old integer IDs
        self.task.subtasks = [
            {"id": 1, "title": "Subtask 1"},
            {"id": 2, "title": "Subtask 2"}
        ]
        
        self.task.migrate_subtask_ids()
        
        # IDs should be converted to hierarchical format
        for subtask in self.task.subtasks:
            assert isinstance(subtask["id"], str)
            assert "." in subtask["id"]  # Hierarchical format


class TestTaskUtilityMethods:
    """Test Task utility methods"""
    
    def setup_method(self):
        """Setup test task"""
        self.task = Task.create(
            id=TaskId.from_int(1),
            title="Test Task",
            description="Test Description",
            due_date="2023-12-31T23:59:59"
        )
        # Clear creation events
        self.task.get_events()
    
    def test_is_overdue_with_due_date_future(self):
        """Test is_overdue with future due date"""
        future_date = "2099-12-31T23:59:59"
        self.task.update_due_date(future_date)
        
        assert not self.task.is_overdue()
    
    def test_is_overdue_with_due_date_past(self):
        """Test is_overdue with past due date"""
        past_date = "2020-01-01T00:00:00"
        self.task.update_due_date(past_date)
        
        assert self.task.is_overdue()
    
    def test_is_overdue_completed_task(self):
        """Test is_overdue with completed task"""
        past_date = "2020-01-01T00:00:00"
        self.task.update_due_date(past_date)
        # Valid transition: todo -> in_progress -> testing -> done
        self.task.update_status(TaskStatus.in_progress())
        self.task.update_status(TaskStatus.testing())
        self.task.update_status(TaskStatus.done())
        
        # Completed tasks should not be overdue
        assert not self.task.is_overdue()
    
    def test_is_overdue_no_due_date(self):
        """Test is_overdue with no due date"""
        self.task.update_due_date(None)
        
        assert not self.task.is_overdue()
    
    def test_is_overdue_invalid_date_format(self):
        """Test is_overdue with invalid date format"""
        with pytest.raises(ValueError, match="Invalid due date format"):
            self.task.update_due_date("invalid-date")
    
    def test_can_be_started_todo_status(self):
        """Test can_be_started with todo status"""
        assert self.task.can_be_started()
    
    def test_can_be_started_non_todo_status(self):
        """Test can_be_started with non-todo status"""
        self.task.update_status(TaskStatus.in_progress())
        
        assert not self.task.can_be_started()
    
    def test_mark_as_deleted(self):
        """Test marking task as deleted"""
        self.task.mark_as_deleted()
        
        events = self.task.get_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskDeleted)
        assert events[0].task_id == self.task.id
        assert events[0].title == self.task.title
    
    def test_mark_as_retrieved(self):
        """Test marking task as retrieved"""
        self.task.mark_as_retrieved()
        
        events = self.task.get_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskRetrieved)
        assert events[0].task_id == self.task.id
        assert events[0].task_data == self.task.to_dict()
    
    def test_to_dict(self):
        """Test converting task to dictionary"""
        task_dict = self.task.to_dict()
        
        assert task_dict["id"] == str(self.task.id)
        assert task_dict["title"] == self.task.title
        assert task_dict["description"] == self.task.description
        assert task_dict["status"] == str(self.task.status)
        assert task_dict["priority"] == str(self.task.priority)
        assert task_dict["details"] == self.task.details
        assert task_dict["estimatedEffort"] == self.task.estimated_effort
        assert task_dict["assignees"] == self.task.assignees
        # NOTE: assignedRole field has been removed from Task entity
        assert task_dict["labels"] == self.task.labels
        assert task_dict["dependencies"] == [str(dep) for dep in self.task.dependencies]
        assert task_dict["subtasks"] == self.task.subtasks
        assert task_dict["dueDate"] == self.task.due_date
        assert task_dict["created_at"] is not None
        assert task_dict["updated_at"] is not None
    
    def test_get_events_clears_events(self):
        """Test that get_events clears the events list"""
        self.task.update_title("New Title")
        
        events = self.task.get_events()
        assert len(events) == 1
        
        # Get events again - should be empty
        events2 = self.task.get_events()
        assert len(events2) == 0


class TestTaskComplexScenarios:
    """Test complex Task scenarios"""
    
    def test_task_with_subtasks_and_dependencies(self):
        """Test task with both subtasks and dependencies"""
        task = Task.create(
            id=TaskId.from_int(1),
            title="Complex Task",
            description="Task with subtasks and dependencies"
        )
        
        # Add dependencies
        dep1 = TaskId.from_int(2)
        dep2 = TaskId.from_int(3)
        task.add_dependency(dep1)
        task.add_dependency(dep2)
        
        # Add subtasks
        task.add_subtask({"title": "Subtask 1"})
        task.add_subtask({"title": "Subtask 2"})
        
        # Verify state
        assert len(task.dependencies) == 2
        assert len(task.subtasks) == 2
        
        # Test progress
        progress = task.get_subtask_progress()
        assert progress["total"] == 2
        assert progress["completed"] == 0
        
        # Complete one subtask
        subtask_id = task.subtasks[0]["id"]
        task.complete_subtask(subtask_id)
        
        progress = task.get_subtask_progress()
        assert progress["completed"] == 1
        assert progress["percentage"] == 50.0
    
    def test_task_full_lifecycle(self):
        """Test complete task lifecycle"""
        task = Task.create(
            id=TaskId.from_int(1),
            title="Lifecycle Task",
            description="Task for testing full lifecycle"
        )
        
        # Clear creation events
        task.get_events()
        
        # Add details
        task.update_details("Detailed information")
        task.update_assignees(["developer"])
        task.add_label("feature")
        task.add_label("high-priority")
        
        # Add subtasks
        task.add_subtask({"title": "Design"})
        task.add_subtask({"title": "Implementation"})
        task.add_subtask({"title": "Testing"})
        
        # Start work
        task.update_status(TaskStatus.in_progress())
        
        # Complete subtasks
        for subtask in task.subtasks:
            task.complete_subtask(subtask["id"])
        
        # Verify all subtasks completed
        progress = task.get_subtask_progress()
        assert progress["percentage"] == 100.0
        
        # Complete task with valid transition
        task.update_status(TaskStatus.testing())
        task.update_status(TaskStatus.done())
        
        # Mark as retrieved (for auto-rule generation)
        task.mark_as_retrieved()
        
        # Verify final state
        assert task.status == TaskStatus.done()
        assert len(task.labels) == 2
        assert all(st["completed"] for st in task.subtasks)
        
        # Check that events were generated throughout lifecycle
        events = task.get_events()
        assert len(events) > 0  # Should have events from the lifecycle 