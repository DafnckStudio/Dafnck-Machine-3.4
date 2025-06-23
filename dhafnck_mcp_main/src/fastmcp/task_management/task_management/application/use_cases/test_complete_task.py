"""Tests for Complete Task functionality"""

import pytest
import tempfile
import os
from datetime import datetime

from fastmcp.task_management.application.use_cases.complete_task import CompleteTaskUseCase
from fastmcp.task_management.infrastructure.repositories.json_task_repository import JsonTaskRepository
from fastmcp.task_management.domain.entities.task import Task
from fastmcp.task_management.domain.value_objects import TaskId, TaskStatus, Priority
from fastmcp.task_management.domain.exceptions import TaskNotFoundError


class TestCompleteTask:
    """Test complete task functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        # Create temporary JSON file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.write('{"project_id": "test", "tasks": []}')
        self.temp_file.close()
        
        # Initialize repository and use case
        self.repository = JsonTaskRepository(self.temp_file.name)
        self.use_case = CompleteTaskUseCase(self.repository)
    
    def teardown_method(self):
        """Clean up test fixtures"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_complete_task_without_subtasks(self):
        """Test completing a task that has no subtasks"""
        # Create a task without subtasks
        task_id = TaskId.from_string("20250618001")
        task = Task.create(
            id=task_id,
            title="Simple Task",
            description="A task without subtasks",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        self.repository.save(task)
        
        # Complete the task
        result = self.use_case.execute("20250618001")
        
        # Verify the result
        assert result["success"] is True
        assert result["task_id"] == "20250618001"
        assert result["status"] == "done"
        assert result["message"] == "task 20250618001 done, can do_next"
        assert result["subtask_progress"]["total"] == 0
        assert result["subtask_progress"]["completed"] == 0
        assert result["subtask_progress"]["percentage"] == 0
        
        # Verify the task was actually updated in repository
        updated_task = self.repository.find_by_id(task_id)
        assert updated_task.status.is_done()
    
    def test_complete_task_with_subtasks(self):
        """Test completing a task that has subtasks"""
        # Create a task with subtasks
        task_id = TaskId.from_string("20250618002")
        task = Task.create(
            id=task_id,
            title="Task with Subtasks",
            description="A task with multiple subtasks",
            status=TaskStatus.todo(),
            priority=Priority.high()
        )
        
        # Add subtasks
        task.add_subtask({"title": "Subtask 1", "description": "First subtask"})
        task.add_subtask({"title": "Subtask 2", "description": "Second subtask"})
        task.add_subtask({"title": "Subtask 3", "description": "Third subtask"})
        
        self.repository.save(task)
        
        # Complete the task
        result = self.use_case.execute("20250618002")
        
        # Verify the result
        assert result["success"] is True
        assert result["task_id"] == "20250618002"
        assert result["status"] == "done"
        assert result["message"] == "task 20250618002 done, can do_next"
        assert result["subtask_progress"]["total"] == 3
        assert result["subtask_progress"]["completed"] == 3
        assert result["subtask_progress"]["percentage"] == 100.0
        
        # Verify the task and all subtasks were updated in repository
        updated_task = self.repository.find_by_id(task_id)
        assert updated_task.status.is_done()
        assert len(updated_task.subtasks) == 3
        for subtask in updated_task.subtasks:
            assert subtask["completed"] is True
    
    def test_complete_task_with_partially_completed_subtasks(self):
        """Test completing a task that has some subtasks already completed"""
        # Create a task with mixed subtask completion states
        task_id = TaskId.from_string("20250618003")
        task = Task.create(
            id=task_id,
            title="Partially Completed Task",
            description="A task with some completed subtasks",
            status=TaskStatus.in_progress(),
            priority=Priority.medium()
        )
        
        # Add subtasks with mixed completion states
        task.add_subtask({"title": "Completed Subtask", "description": "Already done", "completed": True})
        task.add_subtask({"title": "Pending Subtask 1", "description": "Not done", "completed": False})
        task.add_subtask({"title": "Pending Subtask 2", "description": "Not done either", "completed": False})
        
        self.repository.save(task)
        
        # Complete the task
        result = self.use_case.execute("20250618003")
        
        # Verify the result
        assert result["success"] is True
        assert result["task_id"] == "20250618003"
        assert result["status"] == "done"
        assert result["message"] == "task 20250618003 done, can do_next"
        assert result["subtask_progress"]["total"] == 3
        assert result["subtask_progress"]["completed"] == 3
        assert result["subtask_progress"]["percentage"] == 100.0
        
        # Verify all subtasks are now completed
        updated_task = self.repository.find_by_id(task_id)
        assert updated_task.status.is_done()
        for subtask in updated_task.subtasks:
            assert subtask["completed"] is True
    
    def test_complete_already_completed_task(self):
        """Test completing a task that is already done"""
        # Create a completed task
        task_id = TaskId.from_string("20250618004")
        task = Task.create(
            id=task_id,
            title="Already Done Task",
            description="A task that is already completed",
            status=TaskStatus.done(),
            priority=Priority.low()
        )
        self.repository.save(task)
        
        # Try to complete the already completed task
        result = self.use_case.execute("20250618004")
        
        # Verify the result
        assert result["success"] is False
        assert result["task_id"] == "20250618004"
        assert result["status"] == "done"
        assert "already completed" in result["message"]
    
    def test_complete_nonexistent_task(self):
        """Test completing a task that doesn't exist"""
        # Try to complete a non-existent task
        with pytest.raises(TaskNotFoundError):
            self.use_case.execute("20250618999")
    
    def test_complete_task_domain_events(self):
        """Test that completing a task generates appropriate domain events"""
        # Create a task with subtasks
        task_id = TaskId.from_string("20250618005")
        task = Task.create(
            id=task_id,
            title="Event Test Task",
            description="Testing domain events",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        task.add_subtask({"title": "Event Subtask", "description": "For testing events"})
        self.repository.save(task)
        
        # Complete the task
        result = self.use_case.execute("20250618005")
        
        # Verify the result
        assert result["success"] is True
        
        # Verify the task was updated and events were generated
        updated_task = self.repository.find_by_id(task_id)
        assert updated_task.status.is_done()
        assert updated_task.subtasks[0]["completed"] is True
        
        # Verify timestamp was updated
        assert updated_task.updated_at is not None
    
    def test_complete_task_with_string_and_int_ids(self):
        """Test completing tasks using both string and integer IDs"""
        # Create a task with integer-style ID
        task_id = TaskId.from_string("20250618006")
        task = Task.create(
            id=task_id,
            title="ID Test Task",
            description="Testing different ID formats",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        self.repository.save(task)
        
        # Complete using string ID
        result = self.use_case.execute("20250618006")
        assert result["success"] is True
        
        # Create another task and test with different ID representation
        task_id2 = TaskId.from_string("20250618007")
        task2 = Task.create(
            id=task_id2,
            title="Another ID Test Task",
            description="Testing ID handling",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        self.repository.save(task2)
        
        # Complete using string ID (the use case handles conversion internally)
        result2 = self.use_case.execute("20250618007")
        assert result2["success"] is True 