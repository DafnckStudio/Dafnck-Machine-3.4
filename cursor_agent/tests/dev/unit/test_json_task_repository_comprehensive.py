"""Comprehensive tests for JsonTaskRepository"""

import pytest
import json
import os
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, mock_open

from src.task_mcp.infrastructure.repositories.json_task_repository import JsonTaskRepository, InMemoryTaskRepository
from src.task_mcp.domain import Task, TaskId, TaskStatus, Priority
from src.task_mcp.domain.exceptions import TaskNotFoundError


class TestInMemoryTaskRepository:
    """Test InMemoryTaskRepository implementation"""
    
    def setup_method(self):
        """Setup test data"""
        self.repo = InMemoryTaskRepository()
        self.task1 = Task.create(
            id=TaskId.from_int(1),
            title="Test Task 1",
            description="Description 1",
            priority=Priority.high(),
            assignees=["user1"],
            labels=["label1", "label2"]
        )
        self.task2 = Task.create(
            id=TaskId.from_int(2),
            title="Test Task 2",
            description="Description 2",
            status=TaskStatus.in_progress(),
            priority=Priority.low(),
            assignees=["user2"]
        )
    
    def test_save_and_find_by_id(self):
        """Test saving and finding tasks by ID"""
        # Save task
        self.repo.save(self.task1)
        
        # Find by ID
        found_task = self.repo.find_by_id(self.task1.id)
        assert found_task is not None
        assert found_task.id == self.task1.id
        assert found_task.title == self.task1.title
        
        # Find non-existent task
        non_existent_id = TaskId.from_int(999)
        assert self.repo.find_by_id(non_existent_id) is None
    
    def test_find_all(self):
        """Test finding all tasks"""
        # Empty repository
        assert self.repo.find_all() == []
        
        # Add tasks
        self.repo.save(self.task1)
        self.repo.save(self.task2)
        
        all_tasks = self.repo.find_all()
        assert len(all_tasks) == 2
        assert self.task1 in all_tasks
        assert self.task2 in all_tasks
    
    def test_find_by_criteria_status(self):
        """Test finding tasks by status criteria"""
        self.repo.save(self.task1)  # todo status
        self.repo.save(self.task2)  # in_progress status
        
        # Find by status
        todo_tasks = self.repo.find_by_criteria({"status": TaskStatus.todo()})
        assert len(todo_tasks) == 1
        assert todo_tasks[0].id == self.task1.id
        
        in_progress_tasks = self.repo.find_by_criteria({"status": TaskStatus.in_progress()})
        assert len(in_progress_tasks) == 1
        assert in_progress_tasks[0].id == self.task2.id
    
    def test_find_by_criteria_priority(self):
        """Test finding tasks by priority criteria"""
        self.repo.save(self.task1)  # high priority
        self.repo.save(self.task2)  # low priority
        
        high_priority_tasks = self.repo.find_by_criteria({"priority": Priority.high()})
        assert len(high_priority_tasks) == 1
        assert high_priority_tasks[0].id == self.task1.id
    
    def test_find_by_criteria_assignee(self):
        """Test finding tasks by assignee criteria"""
        self.repo.save(self.task1)  # user1
        self.repo.save(self.task2)  # user2
        
        user1_tasks = self.repo.find_by_criteria({"assignees": ["user1"]})
        assert len(user1_tasks) == 1
        assert user1_tasks[0].id == self.task1.id
    
    def test_find_by_criteria_labels(self):
        """Test finding tasks by labels criteria"""
        self.repo.save(self.task1)  # has labels
        self.repo.save(self.task2)  # no labels
        
        labeled_tasks = self.repo.find_by_criteria({"labels": ["label1"]})
        assert len(labeled_tasks) == 1
        assert labeled_tasks[0].id == self.task1.id
        
        # Multiple labels
        multi_labeled_tasks = self.repo.find_by_criteria({"labels": ["label1", "label2"]})
        assert len(multi_labeled_tasks) == 1
        assert multi_labeled_tasks[0].id == self.task1.id
        
        # Non-matching labels
        no_match_tasks = self.repo.find_by_criteria({"labels": ["nonexistent"]})
        assert len(no_match_tasks) == 0
    
    def test_find_by_criteria_with_limit(self):
        """Test finding tasks with limit"""
        # Add multiple tasks
        for i in range(5):
            task = Task.create(
                id=TaskId.from_int(i + 10),
                title=f"Task {i}",
                description=f"Description {i}",
                priority=Priority.medium()
            )
            self.repo.save(task)
        
        # Find with limit
        limited_tasks = self.repo.find_by_criteria({"priority": Priority.medium()}, limit=3)
        assert len(limited_tasks) == 3
    
    def test_search(self):
        """Test searching tasks"""
        self.repo.save(self.task1)
        self.repo.save(self.task2)
        
        # Search in title
        results = self.repo.search("Test Task 1")
        assert len(results) == 1
        assert results[0].id == self.task1.id
        
        # Search in description
        results = self.repo.search("Description 2")
        assert len(results) == 1
        assert results[0].id == self.task2.id
        
        # Case insensitive search
        results = self.repo.search("test task")
        assert len(results) == 2
        
        # No matches
        results = self.repo.search("nonexistent")
        assert len(results) == 0
    
    def test_search_with_limit(self):
        """Test searching with limit"""
        # Add multiple matching tasks
        for i in range(5):
            task = Task.create(
                id=TaskId.from_int(i + 20),
                title=f"Matching Task {i}",
                description="Common description"
            )
            self.repo.save(task)
        
        results = self.repo.search("Matching", limit=3)
        assert len(results) == 3
    
    def test_delete(self):
        """Test deleting tasks"""
        self.repo.save(self.task1)
        assert self.repo.exists(self.task1.id)
        
        # Delete existing task
        result = self.repo.delete(self.task1.id)
        assert result is True
        assert not self.repo.exists(self.task1.id)
        
        # Delete non-existent task
        result = self.repo.delete(TaskId.from_int(999))
        assert result is False
    
    def test_get_next_id(self):
        """Test getting next ID"""
        id1 = self.repo.get_next_id()
        id2 = self.repo.get_next_id()
        
        # IDs should be different and follow expected format
        assert id1 != id2
        assert isinstance(id1, TaskId)
        assert isinstance(id2, TaskId)
    
    def test_find_by_status(self):
        """Test finding tasks by status"""
        self.repo.save(self.task1)  # todo
        self.repo.save(self.task2)  # in_progress
        
        todo_tasks = self.repo.find_by_status(TaskStatus.todo())
        assert len(todo_tasks) == 1
        assert todo_tasks[0].id == self.task1.id
    
    def test_find_by_priority(self):
        """Test finding tasks by priority"""
        self.repo.save(self.task1)  # high
        self.repo.save(self.task2)  # low
        
        high_tasks = self.repo.find_by_priority(Priority.high())
        assert len(high_tasks) == 1
        assert high_tasks[0].id == self.task1.id
    
    def test_find_by_assignee(self):
        """Test finding tasks by assignee"""
        self.repo.save(self.task1)  # user1
        self.repo.save(self.task2)  # user2
        
        user1_tasks = self.repo.find_by_assignee("user1")
        assert len(user1_tasks) == 1
        assert user1_tasks[0].id == self.task1.id
    
    def test_find_by_labels(self):
        """Test finding tasks by labels"""
        self.repo.save(self.task1)  # has labels
        self.repo.save(self.task2)  # no labels
        
        labeled_tasks = self.repo.find_by_labels(["label1"])
        assert len(labeled_tasks) == 1
        assert labeled_tasks[0].id == self.task1.id
    
    def test_exists(self):
        """Test checking if task exists"""
        assert not self.repo.exists(self.task1.id)
        
        self.repo.save(self.task1)
        assert self.repo.exists(self.task1.id)
    
    def test_count(self):
        """Test counting tasks"""
        assert self.repo.count() == 0
        
        self.repo.save(self.task1)
        assert self.repo.count() == 1
        
        self.repo.save(self.task2)
        assert self.repo.count() == 2
    
    def test_get_statistics(self):
        """Test getting repository statistics"""
        self.repo.save(self.task1)
        self.repo.save(self.task2)
        
        stats = self.repo.get_statistics()
        
        assert stats["total_tasks"] == 2
        assert stats["status_distribution"] == {"todo": 1, "in_progress": 1}
        assert stats["priority_distribution"] == {"high": 1, "low": 1}


class TestJsonTaskRepository:
    """Comprehensive test suite for JsonTaskRepository"""

    def setup_method(self):
        """Setup for each test method"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test_tasks.json")
        self.repo = JsonTaskRepository(self.test_file)
        self.task1 = Task.create(
            id=TaskId.from_string("20250101001"),
            title="Test Task 1",
            description="Description 1",
            priority=Priority.high()
        )

    def teardown_method(self):
        """Teardown after each test method"""
        shutil.rmtree(self.temp_dir)

    def test_init_creates_file(self):
        """Test that repository initialization creates the file if it doesn't exist"""
        file_path = os.path.join(self.temp_dir, "new_tasks.json")
        assert not os.path.exists(file_path)
        
        repo = JsonTaskRepository(file_path=file_path)
        
        assert os.path.exists(file_path)
        with open(file_path, 'r') as f:
            data = json.load(f)
            assert data == {"tasks": []}

    def test_init_with_relative_path(self):
        """Test repository initialization with a relative path"""
        relative_path = "test_tasks.json"
        
        # Ensure we are in a temporary directory so we don't pollute the project
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                repo = JsonTaskRepository(file_path=relative_path)
                assert repo._file_path == str(Path(relative_path).resolve())
            finally:
                os.chdir(original_cwd)

    def test_init_with_absolute_path(self):
        """Test repository initialization with an absolute path"""
        abs_path = os.path.join(self.temp_dir, "absolute_tasks.json")
        repo = JsonTaskRepository(abs_path)
        assert repo._file_path == abs_path
    
    def test_ensure_file_exists_creates_directory(self):
        """Test that _ensure_file_exists creates parent directory"""
        nested_path = os.path.join(self.temp_dir, "nested", "dir", "tasks.json")
        repo = JsonTaskRepository(file_path=nested_path)
        assert os.path.exists(os.path.dirname(nested_path))
        assert os.path.exists(nested_path)

    def test_load_data_file_not_found(self):
        """Test loading data from a non-existent file"""
        non_existent_file = os.path.join(self.temp_dir, "non_existent.json")
        repo = JsonTaskRepository(non_existent_file)
        data = repo._load_data()
        assert data == {"tasks": []}

    def test_load_data_json_decode_error(self):
        """Test loading data from a malformed JSON file"""
        with open(self.test_file, 'w') as f:
            f.write("{malformed}")
        
        repo = JsonTaskRepository(self.test_file)
        data = repo._load_data()
        assert data == {"tasks": []}

    def test_save_data(self):
        """Test saving data to file"""
        test_data = {"tasks": [{"id": "1", "title": "Test"}], "test": "data"}
        self.repo._save_data(test_data)
        
        with open(self.test_file, 'r') as f:
            loaded_data = json.load(f)
        assert loaded_data == test_data
        assert loaded_data["test"] == "data"

    def test_task_dict_to_domain_numeric_id(self):
        """Test converting task dict with numeric ID to domain entity"""
        task_dict = {
            "id": 1, 
            "title": "Test Task",
            "description": "Test Description",
            "status": "todo",
            "priority": "medium",
            "details": "",
            "estimatedEffort": "",
            "assignees": [],
            "labels": [],
            "dependencies": [],
            "subtasks": [],
            "dueDate": None,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        
        task = self.repo._task_dict_to_domain(task_dict)
        assert isinstance(task, Task)
        assert task.title == "Test Task"
        assert task.description == "Test Description"

    def test_task_dict_to_domain_string_id(self):
        """Test converting task dict with string ID to domain entity"""
        task_dict = {
            "id": "20250618001",
            "title": "Test Task",
            "description": "Test Description",
            "status": "todo",
            "priority": "medium",
            "details": "",
            "estimatedEffort": "",
            "assignees": [],
            "labels": [],
            "dependencies": [],
            "subtasks": [],
            "dueDate": None,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        
        task = self.repo._task_dict_to_domain(task_dict)
        assert isinstance(task, Task)
        assert str(task.id) == "20250618001"
    
    def test_task_dict_to_domain_legacy_status(self):
        """Test converting task dict with legacy status values"""
        task_dict = {
            "id": 1,
            "title": "Test Task",
            "description": "Test Description",
            "status": "done",  # legacy status
            "priority": "medium",
            "details": "",
            "estimatedEffort": "",
            "assignees": [],
            "labels": [],
            "dependencies": [],
            "subtasks": [],
            "dueDate": None,
            "created_at": "2023-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00"
        }
        
        task = self.repo._task_dict_to_domain(task_dict)
        # 'done' is the correct status value, no conversion needed
        assert task.status.value == "done"

    def test_domain_to_task_dict(self):
        """Test converting domain entity to task dict"""
        task_dict = self.repo._domain_to_task_dict(self.task1)
        
        assert task_dict["id"] == str(self.task1.id)
        assert task_dict["title"] == self.task1.title
        assert task_dict["description"] == self.task1.description
        assert task_dict["status"] == str(self.task1.status)
        assert task_dict["priority"] == str(self.task1.priority)

    def test_save_and_find_by_id(self):
        """Test saving and finding tasks"""
        self.repo.save(self.task1)
        
        found_task = self.repo.find_by_id(self.task1.id)
        assert found_task is not None
        assert found_task.id == self.task1.id
        assert found_task.title == self.task1.title

    def test_find_all(self):
        """Test finding all tasks"""
        assert self.repo.find_all() == []
        
        self.repo.save(self.task1)
        all_tasks = self.repo.find_all()
        assert len( all_tasks) == 1
        assert all_tasks[0].id == self.task1.id

    def test_delete(self):
        """Test deleting tasks"""
        self.repo.save(self.task1)
        assert self.repo.exists(self.task1.id)
        
        result = self.repo.delete(self.task1.id)
        assert result is True
        assert not self.repo.exists(self.task1.id)
        
        # Delete non-existent task
        result = self.repo.delete(TaskId.from_int(999))
        assert result is False

    def test_get_next_id(self):
        """Test getting next ID"""
        # Save a task first
        self.repo.save(self.task1)
        
        next_id = self.repo.get_next_id()
        assert isinstance(next_id, TaskId)
        
        # Next ID should be different from existing
        assert next_id != self.task1.id

    def test_search(self):
        """Test searching tasks"""
        self.repo.save(self.task1)
        
        results = self.repo.search("Test Task")
        assert len(results) == 1
        assert results[0].id == self.task1.id
        
        results = self.repo.search("nonexistent")
        assert len(results) == 0

    def test_find_by_criteria(self):
        """Test finding by criteria"""
        self.repo.save(self.task1)
        
        results = self.repo.find_by_criteria({"priority": Priority.high()})
        assert len(results) == 1
        assert results[0].id == self.task1.id

    def test_exists(self):
        """Test checking existence"""
        assert not self.repo.exists(self.task1.id)
        
        self.repo.save(self.task1)
        assert self.repo.exists(self.task1.id)

    def test_count(self):
        """Test counting tasks"""
        assert self.repo.count() == 0
        
        self.repo.save(self.task1)
        assert self.repo.count() == 1

    def test_get_statistics(self):
        """Test getting statistics"""
        stats = self.repo.get_statistics()
        assert stats["total_tasks"] == 0
        
        self.repo.save(self.task1)
        stats = self.repo.get_statistics()
        assert stats["total_tasks"] == 1
        assert stats["priority_distribution"]["high"] == 1

    def test_find_by_status(self):
        """Test finding by status"""
        self.repo.save(self.task1)
        
        results = self.repo.find_by_status(TaskStatus.todo())
        assert len(results) == 1
        assert results[0].id == self.task1.id

    def test_find_by_priority(self):
        """Test finding by priority"""
        self.repo.save(self.task1)
        
        results = self.repo.find_by_priority(Priority.high())
        assert len(results) == 1
        assert results[0].id == self.task1.id

    def test_find_by_assignee(self):
        """Test finding by assignee"""
        task_with_assignee = Task.create(
            id=TaskId.from_int(2),
            title="Assigned Task",
            description="Test",
            assignees=["user1"]
        )
        self.repo.save(task_with_assignee)
        
        results = self.repo.find_by_assignee("user1")
        assert len(results) == 1
        assert results[0].id == task_with_assignee.id

    def test_find_by_labels(self):
        """Test finding by labels"""
        task_with_labels = Task.create(
            id=TaskId.from_int(2),
            title="Labeled Task",
            description="Test",
            labels=["test", "label"]
        )
        self.repo.save(task_with_labels)
        
        results = self.repo.find_by_labels(["test"])
        assert len(results) == 1
        assert results[0].id == task_with_labels.id


if __name__ == "__main__":
    pytest.main(['-s', __file__]) 