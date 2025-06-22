"""Unit tests for Task domain entity"""

import pytest
from datetime import datetime

from fastmcp.task_management.domain.entities.task import Task
from fastmcp.task_management.domain.value_objects import TaskId, TaskStatus, Priority
from fastmcp.task_management.domain.events.task_events import TaskCreated, TaskUpdated


class TestTaskCreation:
    """Test task creation and initialization"""
    
    def test_create_task_with_valid_data(self):
        """Test creating a task with valid data"""
        task_id = TaskId("20250101001")
        title = "Test Task"
        description = "Test Description"
        
        task = Task.create(task_id, title, description)
        
        assert task.id == task_id
        assert task.title == title
        assert task.description == description
        assert task.status.is_todo()
        assert task.priority.value == "medium"
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)
    
    def test_task_creation_raises_domain_event(self):
        """Test that task creation raises TaskCreated event"""
        task_id = TaskId("20250101003")
        task = Task.create(task_id, "Test Task", "Test Description")
        
        events = task.get_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskCreated)


class TestTaskValidation:
    """Test task validation rules"""
    
    def test_empty_title_raises_error(self):
        """Test that empty title raises ValueError"""
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            Task.create(TaskId("20250101001"), "", "Description")
    
    def test_empty_description_raises_error(self):
        """Test that empty description raises ValueError"""
        with pytest.raises(ValueError, match="Task description cannot be empty"):
            Task.create(TaskId("20250101001"), "Title", "")


class TestTaskSubtasks:
    """Test task subtask management"""
    
    def setup_method(self):
        """Set up test data"""
        self.task = Task.create(
            TaskId("20250101001"),
            "Test Task",
            "Test Description"
        )
        self.task.get_events()  # Clear creation events
    
    def test_add_subtask(self):
        """Test adding a subtask"""
        subtask = {"title": "Test Subtask"}
        self.task.add_subtask(subtask)
        
        assert len(self.task.subtasks) == 1
        assert self.task.subtasks[0]["title"] == "Test Subtask"
        assert "id" in self.task.subtasks[0]
        assert self.task.subtasks[0]["completed"] is False
    
    def test_get_subtask_progress(self):
        """Test getting subtask progress"""
        # No subtasks
        progress = self.task.get_subtask_progress()
        assert progress["total"] == 0
        assert progress["completed"] == 0
        assert progress["percentage"] == 0
        
        # Add subtasks
        self.task.add_subtask({"title": "Subtask 1"})
        self.task.add_subtask({"title": "Subtask 2"})
        
        progress = self.task.get_subtask_progress()
        assert progress["total"] == 2
        assert progress["completed"] == 0
        assert progress["percentage"] == 0
