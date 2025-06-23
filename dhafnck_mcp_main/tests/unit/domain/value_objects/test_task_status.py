"""
This is the canonical and only maintained unit test suite for the TaskStatus value object.
All unit tests for TaskStatus should be added here.
Redundant or duplicate tests in other files have been removed.
"""

import pytest
from fastmcp.dhafnck_mcp.domain.value_objects.task_status import TaskStatus


def test_create_valid_status():
    """Test creating a valid task status"""
    status = TaskStatus("todo")
    assert status.value == "todo"
    assert str(status) == "todo"


def test_invalid_status_raises_error():
    """Test that invalid status raises ValueError"""
    with pytest.raises(ValueError, match="Invalid task status"):
        TaskStatus("invalid")


def test_status_factory_methods():
    """Test status factory methods"""
    assert TaskStatus.todo().value == "todo"
    assert TaskStatus.in_progress().value == "in_progress"
    assert TaskStatus.blocked().value == "blocked"
    assert TaskStatus.review().value == "review"
    assert TaskStatus.testing().value == "testing"
    assert TaskStatus.done().value == "done"
    assert TaskStatus.cancelled().value == "cancelled"


def test_status_check_methods():
    """Test status check methods"""
    todo = TaskStatus.todo()
    in_progress = TaskStatus.in_progress()
    done = TaskStatus.done()
    
    assert todo.is_todo() is True
    assert todo.is_in_progress() is False
    assert todo.is_done() is False
    
    assert in_progress.is_in_progress() is True
    assert in_progress.is_todo() is False
    
    assert done.is_done() is True
    assert done.is_completed() is True


def test_status_transitions():
    """Test status transition validation"""
    todo = TaskStatus.todo()
    in_progress = TaskStatus.in_progress()
    done = TaskStatus.done()
    
    # Valid transitions
    assert todo.can_transition_to("in_progress") is True
    assert todo.can_transition_to("cancelled") is True
    assert in_progress.can_transition_to("review") is True
    
    # Invalid transitions
    assert todo.can_transition_to("done") is False
    assert done.can_transition_to("in_progress") is False
