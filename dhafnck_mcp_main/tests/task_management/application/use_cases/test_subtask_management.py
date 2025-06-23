"""Unit Tests for Subtask Management"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


import pytest
from datetime import datetime
from fastmcp.dhafnck_mcp.domain import Task, TaskId, TaskStatus, Priority
from fastmcp.dhafnck_mcp.application.use_cases.manage_subtasks import (
    ManageSubtasksUseCase, 
    AddSubtaskRequest, 
    UpdateSubtaskRequest
)
from fastmcp.dhafnck_mcp.infrastructure.repositories.json_task_repository import InMemoryTaskRepository
from fastmcp.dhafnck_mcp.domain.exceptions import TaskNotFoundError


class TestSubtaskManagement:
    """Test subtask management functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.repository = InMemoryTaskRepository()
        self.use_case = ManageSubtasksUseCase(self.repository)
        
        # Create a test task
        self.test_task = Task(
            id=TaskId.from_int(1),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        self.repository.save(self.test_task)
    
    def test_add_subtask_success(self):
        """Test adding a subtask successfully"""
        request = AddSubtaskRequest(
            task_id=1,
            title="Test Subtask",
            description="Test subtask description"
        )
        
        response = self.use_case.add_subtask(request)
        
        assert response.task_id == "1"
        assert response.subtask["title"] == "Test Subtask"
        assert response.subtask["description"] == "Test subtask description"
        assert response.subtask["completed"] is False
        assert "id" in response.subtask
        assert response.progress["total"] == 1
        assert response.progress["completed"] == 0
        assert response.progress["percentage"] == 0
    
    def test_add_subtask_task_not_found(self):
        """Test adding subtask to non-existent task"""
        request = AddSubtaskRequest(
            task_id=999,
            title="Test Subtask"
        )
        
        with pytest.raises(TaskNotFoundError):
            self.use_case.add_subtask(request)
    
    def test_add_multiple_subtasks(self):
        """Test adding multiple subtasks"""
        # Add first subtask
        request1 = AddSubtaskRequest(task_id=1, title="Subtask 1")
        response1 = self.use_case.add_subtask(request1)
        
        # Add second subtask
        request2 = AddSubtaskRequest(task_id=1, title="Subtask 2")
        response2 = self.use_case.add_subtask(request2)
        
        assert response1.subtask["id"] != response2.subtask["id"]
        assert response2.progress["total"] == 2
    
    def test_remove_subtask_success(self):
        """Test removing a subtask successfully"""
        # Add a subtask first
        request = AddSubtaskRequest(task_id=1, title="Test Subtask")
        add_response = self.use_case.add_subtask(request)
        subtask_id = add_response.subtask["id"]
        
        # Remove the subtask
        response = self.use_case.remove_subtask(1, subtask_id)
        
        assert response["success"] is True
        assert response["task_id"] == "1"
        assert response["subtask_id"] == subtask_id
        assert response["progress"]["total"] == 0
    
    def test_remove_subtask_not_found(self):
        """Test removing non-existent subtask"""
        response = self.use_case.remove_subtask(1, 999)
        
        assert response["success"] is False
        assert response["task_id"] == "1"
        assert response["subtask_id"] == "999"
    
    def test_update_subtask_success(self):
        """Test updating a subtask successfully"""
        # Add a subtask first
        add_request = AddSubtaskRequest(task_id=1, title="Original Title")
        add_response = self.use_case.add_subtask(add_request)
        subtask_id = add_response.subtask["id"]
        
        # Update the subtask
        update_request = UpdateSubtaskRequest(
            task_id=1,
            subtask_id=subtask_id,
            title="Updated Title",
            description="Updated description",
            completed=True
        )
        response = self.use_case.update_subtask(update_request)
        
        assert response.subtask["title"] == "Updated Title"
        assert response.subtask["description"] == "Updated description"
        assert response.subtask["completed"] is True
        assert response.progress["completed"] == 1
        assert response.progress["percentage"] == 100.0
    
    def test_update_subtask_partial(self):
        """Test updating only some fields of a subtask"""
        # Add a subtask first
        add_request = AddSubtaskRequest(task_id=1, title="Original Title", description="Original desc")
        add_response = self.use_case.add_subtask(add_request)
        subtask_id = add_response.subtask["id"]
        
        # Update only the title
        update_request = UpdateSubtaskRequest(
            task_id=1,
            subtask_id=subtask_id,
            title="New Title"
        )
        response = self.use_case.update_subtask(update_request)
        
        assert response.subtask["title"] == "New Title"
        assert response.subtask["description"] == "Original desc"  # Should remain unchanged
        assert response.subtask["completed"] is False  # Should remain unchanged
    
    def test_complete_subtask(self):
        """Test marking a subtask as completed"""
        # Add a subtask first
        add_request = AddSubtaskRequest(task_id=1, title="Test Subtask")
        add_response = self.use_case.add_subtask(add_request)
        subtask_id = add_response.subtask["id"]
        
        # Complete the subtask
        response = self.use_case.complete_subtask(1, subtask_id)
        
        assert response["success"] is True
        assert response["progress"]["completed"] == 1
        assert response["progress"]["percentage"] == 100.0
    
    def test_get_subtasks(self):
        """Test getting all subtasks for a task"""
        # Add multiple subtasks
        request1 = AddSubtaskRequest(task_id=1, title="Subtask 1")
        request2 = AddSubtaskRequest(task_id=1, title="Subtask 2")
        self.use_case.add_subtask(request1)
        self.use_case.add_subtask(request2)
        
        # Get all subtasks
        response = self.use_case.get_subtasks(1)
        
        assert response["task_id"] == "1"
        assert len(response["subtasks"]) == 2
        assert response["progress"]["total"] == 2
        assert response["progress"]["completed"] == 0
    
    def test_subtask_progress_calculation(self):
        """Test subtask progress calculation with mixed completion states"""
        # Add 3 subtasks
        for i in range(3):
            request = AddSubtaskRequest(task_id=1, title=f"Subtask {i+1}")
            self.use_case.add_subtask(request)
        
        # Complete 2 out of 3 subtasks
        response = self.use_case.get_subtasks(1)
        subtasks = response["subtasks"]
        
        self.use_case.complete_subtask(1, subtasks[0]["id"])
        self.use_case.complete_subtask(1, subtasks[1]["id"])
        
        # Check progress
        final_response = self.use_case.get_subtasks(1)
        progress = final_response["progress"]
        
        assert progress["total"] == 3
        assert progress["completed"] == 2
        assert progress["percentage"] == 66.7
    
    def test_subtask_id_generation(self):
        """Test that subtask IDs are generated correctly"""
        # Add subtasks and verify unique IDs
        request1 = AddSubtaskRequest(task_id=1, title="Subtask 1")
        request2 = AddSubtaskRequest(task_id=1, title="Subtask 2")
        
        response1 = self.use_case.add_subtask(request1)
        response2 = self.use_case.add_subtask(request2)
        
        id1 = response1.subtask["id"]
        id2 = response2.subtask["id"]
        
        assert id1 != id2
        # IDs can be either integers or strings (hierarchical format)
        assert id1 is not None
        assert id2 is not None
        # Ensure IDs are different and valid
        assert str(id1) != str(id2) 