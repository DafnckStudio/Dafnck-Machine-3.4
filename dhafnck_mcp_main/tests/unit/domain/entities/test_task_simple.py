"""Simple unit tests for Task domain entity"""

import pytest
from fastmcp.task_management.domain.entities.task import Task
from fastmcp.task_management.domain.value_objects import TaskId, TaskStatus, Priority


def test_create_task():
    """Test creating a basic task"""
    task_id = TaskId("20250101001")
    task = Task.create(task_id, "Test Task", "Test Description")
    
    assert task.id == task_id
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.status.is_todo()


def test_task_validation():
    """Test task validation"""
    with pytest.raises(ValueError, match="Task title cannot be empty"):
        Task.create(TaskId("20250101001"), "", "Description")
    
    with pytest.raises(ValueError, match="Task description cannot be empty"):
        Task.create(TaskId("20250101001"), "Title", "")


def test_update_status():
    """Test updating task status"""
    task = Task.create(TaskId("20250101001"), "Test", "Test")
    task.get_events()  # Clear creation events
    
    task.update_status(TaskStatus.in_progress())
    assert task.status.is_in_progress()
    
    events = task.get_events()
    assert len(events) == 1


def test_subtask_management():
    """Test basic subtask operations"""
    task = Task.create(TaskId("20250101001"), "Test", "Test")
    task.get_events()  # Clear creation events
    
    # Add subtask
    task.add_subtask({"title": "Subtask 1"})
    assert len(task.subtasks) == 1
    assert task.subtasks[0]["title"] == "Subtask 1"
    
    # Check progress
    progress = task.get_subtask_progress()
    assert progress["total"] == 1
    assert progress["completed"] == 0
    
    # Complete subtask
    subtask_id = task.subtasks[0]["id"]
    task.complete_subtask(subtask_id)
    assert task.subtasks[0]["completed"] is True
    
    progress = task.get_subtask_progress()
    assert progress["completed"] == 1
    assert progress["percentage"] == 100.0


def test_task_completion():
    """Test task completion"""
    task = Task.create(TaskId("20250101001"), "Test", "Test")
    task.update_status(TaskStatus.in_progress())
    task.add_subtask({"title": "Subtask 1"})
    task.get_events()  # Clear events
    
    task.complete_task()
    
    assert task.status.is_done()
    assert task.subtasks[0]["completed"] is True
