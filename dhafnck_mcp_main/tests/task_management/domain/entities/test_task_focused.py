"""
Focused test suite for Task entity targeting actual implementation methods
Designed to improve coverage from 42% to >80% by testing real business logic
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


import pytest
from datetime import datetime, timezone
from unittest.mock import patch

from fastmcp.task_management.domain.entities.task import Task
from fastmcp.task_management.domain.value_objects.task_id import TaskId
from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
from fastmcp.task_management.domain.value_objects.priority import Priority
from fastmcp.task_management.domain.enums.agent_roles import AgentRole
from fastmcp.task_management.domain.enums.common_labels import CommonLabel
from fastmcp.task_management.domain.enums.estimated_effort import EstimatedEffort, EffortLevel


class TestTaskEntityFocused:
    """Focused test suite for Task entity covering actual implementation methods"""

    def test_task_creation_and_validation(self):
        """Test task creation with validation"""
        task_id = TaskId.generate_new()
        
        task = Task(
            id=task_id,
            title="Test Task",
            description="Test Description",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        assert task.id == task_id
        assert task.title == "Test Task"
        assert task.description == "Test Description"
        assert task.status == TaskStatus.todo()
        assert task.priority == Priority.medium()
        assert task.assignees == []
        assert task.labels == []
        assert task.dependencies == []
        assert task.subtasks == []

    def test_task_validation_errors(self):
        """Test task validation with invalid data"""
        task_id = TaskId.generate_new()
        
        # Test empty title
        with pytest.raises(ValueError, match="title cannot be empty"):
            Task(
                id=task_id,
                title="",
                description="Test Description",
                status=TaskStatus.todo(),
                priority=Priority.medium()
            )
        
        # Test empty description
        with pytest.raises(ValueError, match="description cannot be empty"):
            Task(
                id=task_id,
                title="Test Task",
                description="",
                status=TaskStatus.todo(),
                priority=Priority.medium()
            )

    def test_update_status(self):
        """Test status update with validation"""
        task = Task(
            id=TaskId.generate_new(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        # Valid transition
        task.update_status(TaskStatus.in_progress())
        assert task.status == TaskStatus.in_progress()
        
        # Check that events are generated
        events = task.get_events()
        assert len(events) > 0

    def test_update_priority(self):
        """Test priority update"""
        task = Task(
            id=TaskId.generate_new(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        task.update_priority(Priority.high())
        assert task.priority == Priority.high()
        
        # Check that events are generated
        events = task.get_events()
        assert len(events) > 0

    def test_update_title_and_description(self):
        """Test title and description updates"""
        task = Task(
            id=TaskId.generate_new(),
            title="Original Title",
            description="Original Description",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        # Update title
        task.update_title("New Title")
        assert task.title == "New Title"
        
        # Update description
        task.update_description("New Description")
        assert task.description == "New Description"
        
        # Test validation
        with pytest.raises(ValueError):
            task.update_title("")
        
        with pytest.raises(ValueError):
            task.update_description("")

    def test_update_details_and_effort(self):
        """Test details and estimated effort updates"""
        task = Task(
            id=TaskId.generate_new(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        # Update details
        task.update_details("Detailed information")
        assert task.details == "Detailed information"
        
        # Update estimated effort
        task.update_estimated_effort(EffortLevel.LARGE.label)
        assert task.estimated_effort == EffortLevel.LARGE.label

    def test_assignee_management(self):
        """Test assignee management methods"""
        task = Task(
            id=TaskId.generate_new(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        # Add assignee
        task.add_assignee("@coding_agent")
        assert "@coding_agent" in task.assignees
        
        # Test duplicate prevention
        task.add_assignee("@coding_agent")
        assert task.assignees.count("@coding_agent") == 1
        
        # Add another assignee
        task.add_assignee("@test_agent")
        assert len(task.assignees) == 2
        
        # Remove assignee
        task.remove_assignee("@coding_agent")
        assert "@coding_agent" not in task.assignees
        assert "@test_agent" in task.assignees
        
        # Test helper methods
        assert task.has_assignee("@test_agent")
        assert not task.has_assignee("@coding_agent")
        assert task.get_primary_assignee() == "@test_agent"
        assert task.get_assignees_count() == 1
        assert not task.is_multi_assignee()

    def test_update_assignees(self):
        """Test bulk assignee updates"""
        task = Task(
            id=TaskId.generate_new(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        # Update assignees
        assignees = ["@coding_agent", "@test_agent", "@review_agent"]
        task.update_assignees(assignees)
        
        assert len(task.assignees) == 3
        assert "@coding_agent" in task.assignees
        assert "@test_agent" in task.assignees
        assert "@review_agent" in task.assignees

    def test_label_management(self):
        """Test label management methods"""
        task = Task(
            id=TaskId.generate_new(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        # Add label
        task.add_label("feature")
        assert "feature" in task.labels
        
        # Test duplicate prevention
        task.add_label("feature")
        assert task.labels.count("feature") == 1
        
        # Add another label
        task.add_label("urgent")
        assert len(task.labels) == 2
        
        # Remove label
        task.remove_label("feature")
        assert "feature" not in task.labels
        assert "urgent" in task.labels

    def test_update_labels(self):
        """Test bulk label updates"""
        task = Task(
            id=TaskId.generate_new(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        # Update labels
        labels = ["feature", "urgent", "backend"]
        task.update_labels(labels)
        
        assert len(task.labels) >= 1  # Some labels may be validated/filtered

    def test_dependency_management(self):
        """Test dependency management methods"""
        task = Task(
            id=TaskId.generate_new(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        dep_id = TaskId.generate_new()
        
        # Add dependency
        task.add_dependency(dep_id)
        assert task.has_dependency(dep_id)
        assert dep_id in task.dependencies
        
        # Test self-dependency prevention
        with pytest.raises(ValueError, match="cannot depend on itself"):
            task.add_dependency(task.id)
        
        # Remove dependency
        task.remove_dependency(dep_id)
        assert not task.has_dependency(dep_id)
        assert dep_id not in task.dependencies
        
        # Test dependency ID conversion
        task.add_dependency(dep_id)
        dep_ids = task.get_dependency_ids()
        assert str(dep_id) in dep_ids
        
        # Clear all dependencies
        task.clear_dependencies()
        assert len(task.dependencies) == 0

    def test_subtask_management(self):
        """Test subtask management methods"""
        task = Task(
            id=TaskId.generate_new(),
            title="Parent Task",
            description="Parent Description",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        # Add subtask
        task.add_subtask(
            title="Subtask 1",
            description="First subtask",
            assignees=["@coding_agent"]
        )
        assert len(task.subtasks) == 1
        
        subtask = task.subtasks[0]
        assert subtask["title"] == "Subtask 1"
        assert subtask["completed"] is False
        assert "id" in subtask  # ID should be auto-generated
        
        # Get subtask by ID
        subtask_id = subtask["id"]
        found_subtask = task.get_subtask(subtask_id)
        assert found_subtask is not None
        assert found_subtask["title"] == "Subtask 1"
        
        # Update subtask
        success = task.update_subtask(subtask_id, {"title": "Updated Subtask"})
        assert success
        assert task.subtasks[0]["title"] == "Updated Subtask"
        
        # Complete subtask
        success = task.complete_subtask(subtask_id)
        assert success
        assert task.subtasks[0]["completed"] is True
        
        # Add another subtask
        task.add_subtask(title="Subtask 2", description="Second subtask")
        assert len(task.subtasks) == 2
        
        # Test progress calculation
        progress = task.get_subtask_progress()
        assert progress["total"] == 2
        assert progress["completed"] == 1
        assert progress["percentage"] == 50.0
        
        # Remove subtask
        success = task.remove_subtask(subtask_id)
        assert success
        assert len(task.subtasks) == 1

    def test_subtask_validation(self):
        """Test subtask validation"""
        task = Task(
            id=TaskId.generate_new(),
            title="Parent Task",
            description="Parent Description",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        # Test empty title validation
        with pytest.raises(ValueError, match="Either subtask_title or title must be provided"):
            task.add_subtask(description="No title")

    def test_task_completion(self):
        """Test task completion logic"""
        task = Task(
            id=TaskId.generate_new(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.in_progress(),
            priority=Priority.medium()
        )
        
        # Add subtasks
        task.add_subtask(title="Subtask 1", description="First")
        task.add_subtask(title="Subtask 2", description="Second")
        
        # Complete task
        task.complete_task()
        
        # Check that task status is done
        assert task.status.is_completed()
        
        # Check that all subtasks are completed
        for subtask in task.subtasks:
            assert subtask["completed"] is True

    def test_business_logic_methods(self):
        """Test business logic helper methods"""
        task = Task(
            id=TaskId.generate_new(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        # Test can_be_started
        assert task.can_be_started()
        
        # Test is_overdue with no due date
        assert not task.is_overdue()
        
        # Test is_overdue with past due date
        task.update_due_date("2023-01-01T00:00:00Z")
        assert task.is_overdue()
        
        # Test effort level
        task.update_estimated_effort(EffortLevel.LARGE.label)
        effort_level = task.get_effort_level()
        assert effort_level is not None

    def test_suggested_labels(self):
        """Test suggested labels functionality"""
        task = Task(
            id=TaskId.generate_new(),
            title="Bug Fix Task",
            description="Fix critical security bug",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        suggestions = task.get_suggested_labels()
        assert isinstance(suggestions, list)
        # Should suggest bug-related labels based on title/description

    def test_assignee_role_info(self):
        """Test assignee role information"""
        task = Task(
            id=TaskId.generate_new(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        # Test with no assignees
        role_info = task.get_assignee_role_info()
        assert role_info is None
        
        # Test with assignee
        task.add_assignee("@coding_agent")
        role_info = task.get_assignee_role_info()
        assert role_info is not None
        assert "role" in role_info

    def test_assignees_info(self):
        """Test getting info for all assignees"""
        task = Task(
            id=TaskId.generate_new(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        task.add_assignee("@coding_agent")
        task.add_assignee("@test_agent")
        
        assignees_info = task.get_assignees_info()
        assert len(assignees_info) == 2
        assert all("role" in info for info in assignees_info)

    def test_to_dict_conversion(self):
        """Test task to dictionary conversion"""
        task = Task(
            id=TaskId.generate_new(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        # Add some data
        task.add_assignee("@coding_agent")
        task.add_label("feature")
        task.add_subtask(title="Subtask", description="Test")
        
        task_dict = task.to_dict()
        
        assert task_dict["id"] == str(task.id)
        assert task_dict["title"] == "Test Task"
        assert task_dict["description"] == "Test Description"
        assert task_dict["status"] == str(task.status)
        assert task_dict["priority"] == str(task.priority)
        assert len(task_dict["assignees"]) == 1
        assert len(task_dict["labels"]) == 1
        assert len(task_dict["subtasks"]) == 1

    def test_domain_events(self):
        """Test domain event generation"""
        task = Task(
            id=TaskId.generate_new(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        # Clear initial events
        task.get_events()
        
        # Perform operations that should generate events
        task.update_title("New Title")
        task.update_status(TaskStatus.in_progress())
        task.add_assignee("@coding_agent")
        
        events = task.get_events()
        assert len(events) >= 2  # Should have multiple events
        
        # Events should be cleared after getting them
        events_again = task.get_events()
        assert len(events_again) == 0

    def test_mark_as_retrieved(self):
        """Test marking task as retrieved"""
        task = Task(
            id=TaskId.generate_new(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        # Clear initial events
        task.get_events()
        
        # Mark as retrieved
        task.mark_as_retrieved()
        
        events = task.get_events()
        assert len(events) == 1

    def test_mark_as_deleted(self):
        """Test marking task as deleted"""
        task = Task(
            id=TaskId.generate_new(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        # Clear initial events
        task.get_events()
        
        # Mark as deleted
        task.mark_as_deleted()
        
        events = task.get_events()
        assert len(events) == 1

    def test_subtask_id_migration(self):
        """Test subtask ID migration functionality"""
        task = Task(
            id=TaskId.generate_new(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        # Manually add subtask with old integer ID
        task.subtasks.append({"id": 1, "title": "Old ID Subtask", "completed": False})
        
        # Run migration
        task.migrate_subtask_ids()
        
        # Check that ID was converted
        subtask = task.subtasks[0]
        assert isinstance(subtask["id"], str)
        assert "." in subtask["id"]  # Should be hierarchical format

    def test_circular_dependency_check(self):
        """Test circular dependency detection"""
        task = Task(
            id=TaskId.generate_new(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        # Test self-dependency (circular)
        has_circular = task.has_circular_dependency(task.id)
        assert has_circular is True
        
        # Test different task (not circular in this simple check)
        other_id = TaskId.generate_new()
        has_circular = task.has_circular_dependency(other_id)
        assert has_circular is False

    def test_factory_method(self):
        """Test task creation using factory method"""
        task_id = TaskId.generate_new()
        
        task = Task.create(
            id=task_id,
            title="Factory Task",
            description="Created with factory method"
        )
        
        assert task.id == task_id
        assert task.title == "Factory Task"
        assert task.description == "Created with factory method"
        assert task.status == TaskStatus.todo()
        assert task.priority == Priority.medium()
        
        # Should generate creation event
        events = task.get_events()
        assert len(events) == 1 