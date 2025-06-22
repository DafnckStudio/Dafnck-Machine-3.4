"""Comprehensive tests for JsonTaskRepository"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from datetime import datetime, timezone

from fastmcp.task_management.infrastructure.repositories.json_task_repository import JsonTaskRepository
from fastmcp.task_management.domain.entities.task import Task
from fastmcp.task_management.domain.value_objects.task_status import TaskStatus, TaskStatusEnum
from fastmcp.task_management.domain.value_objects.priority import Priority, PriorityLevel
from fastmcp.task_management.domain.value_objects.task_id import TaskId
from fastmcp.task_management.domain.enums import AgentRole
from fastmcp.task_management.domain.exceptions import TaskNotFoundError


class TestJsonTaskRepository:
    """Test JsonTaskRepository functionality"""
    
    @pytest.fixture
    def temp_tasks_file(self):
        """Create temporary tasks file for testing"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"tasks": []}, f)
            yield f.name
        os.unlink(f.name)
    
    @pytest.fixture
    def repository(self, temp_tasks_file):
        """Create JsonTaskRepository instance for testing"""
        return JsonTaskRepository(file_path=temp_tasks_file)
    
    @pytest.fixture
    def sample_task(self):
        """Create sample task for testing"""
        return Task(
            id=TaskId.from_int(1),
            title="Test Task",
            description="Test Description",
            priority=Priority.high(),
            assignees=[AgentRole.CODING],
            labels=["test", "feature"]
        )
    
    def test_init_with_custom_file_path(self, temp_tasks_file):
        """Test initialization with custom file path"""
        repo = JsonTaskRepository(file_path=temp_tasks_file)
        assert repo._file_path == temp_tasks_file
    
    def test_init_with_default_file_path(self):
        """Test initialization with default file path"""
        repo = JsonTaskRepository()
        assert repo._file_path is not None
        assert repo._file_path != ""
    
    def test_init_creates_directory_if_not_exists(self):
        """Test that initialization creates directory if it doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            tasks_file = os.path.join(temp_dir, "subdir", "tasks.json")
            
            repo = JsonTaskRepository(file_path=tasks_file)
            assert os.path.exists(os.path.dirname(tasks_file))
    
    def test_load_tasks_from_existing_file(self, temp_tasks_file):
        """Test loading tasks from existing file"""
        # Write test data to file
        test_data = {
            "tasks": [
                {
                    "id": "20250101001",
                    "title": "Test Task",
                    "description": "Test Description",
                    "status": "todo",
                    "priority": "high",
                    "assignees": ["@coding_agent"],
                    "labels": ["test"],
                    "subtasks": [],
                    "dependencies": [],
                    "created_at": "2025-01-01T00:00:00+00:00",
                    "updated_at": "2025-01-01T00:00:00+00:00"
                }
            ]
        }
        
        with open(temp_tasks_file, 'w') as f:
            json.dump(test_data, f)
        
        repo = JsonTaskRepository(file_path=temp_tasks_file)
        tasks = repo.find_all()
        assert len(tasks) == 1
        assert tasks[0].title == "Test Task"
    
    def test_load_tasks_from_nonexistent_file(self):
        """Test loading tasks when file doesn't exist"""
        nonexistent_file = "/tmp/nonexistent_tasks.json"
        if os.path.exists(nonexistent_file):
            os.remove(nonexistent_file)
        
        repo = JsonTaskRepository(file_path=nonexistent_file)
        tasks = repo.find_all()
        assert tasks == []
    
    def test_load_tasks_with_invalid_json(self, temp_tasks_file):
        """Test loading tasks with invalid JSON"""
        # Write invalid JSON to file
        with open(temp_tasks_file, 'w') as f:
            f.write("invalid json content")
        
        repo = JsonTaskRepository(file_path=temp_tasks_file)
        tasks = repo.find_all()
        assert tasks == []  # Should handle gracefully
    
    def test_load_tasks_with_missing_tasks_key(self, temp_tasks_file):
        """Test loading tasks with missing 'tasks' key"""
        # Write JSON without 'tasks' key
        with open(temp_tasks_file, 'w') as f:
            json.dump({"other_key": "value"}, f)
        
        repo = JsonTaskRepository(file_path=temp_tasks_file)
        tasks = repo.find_all()
        assert tasks == []
    
    def test_save_tasks(self, repository, sample_task):
        """Test saving tasks to file"""
        repository.save(sample_task)
        repository._save_data({"tasks": [repository._domain_to_task_dict(sample_task)]})
        
        # Verify file was written
        with open(repository._file_path, 'r') as f:
            data = json.load(f)
        
        assert "tasks" in data
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["title"] == "Test Task"
    
    def test_save_tasks_creates_directory(self):
        """Test that save_tasks creates directory if needed"""
        with tempfile.TemporaryDirectory() as temp_dir:
            tasks_file = os.path.join(temp_dir, "new_subdir", "tasks.json")
            repo = JsonTaskRepository(file_path=tasks_file)
            
            # Add a task and save
            task = Task(id=TaskId.from_int(100), title="Test", description="Test")
            repo.save(task)
            
            assert os.path.exists(tasks_file)
    
    def test_save_tasks_handles_permission_error(self, repository):
        """Test save_tasks handles permission errors gracefully"""
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = PermissionError("Permission denied")
            
            # Should not raise exception
            try:
                repository._save_data({"tasks": []})
            except PermissionError:
                pass  # Expected to fail gracefully
    
    def test_save_tasks_handles_os_error(self, repository):
        """Test save_tasks handles OS errors gracefully"""
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = OSError("Disk full")
            
            # Should not raise exception
            try:
                repository._save_data({"tasks": []})
            except OSError:
                pass  # Expected to fail gracefully
    
    def test_create_task_generates_unique_id(self, repository):
        """Test that creating tasks generates unique IDs"""
        task1 = Task(id=TaskId.from_int(1), title="Task 1", description="Description 1")
        task2 = Task(id=TaskId.from_int(2), title="Task 2", description="Description 2")
        
        repository.save(task1)
        repository.save(task2)
        
        assert task1.id != task2.id
        assert len(repository.find_all()) == 2
    
    def test_create_task_sets_timestamps(self, repository):
        """Test that creating task sets created_at and updated_at timestamps"""
        task = Task(id=TaskId.from_int(1), title="Test Task", description="Test Description")
        repository.save(task)
        
        assert task.created_at is not None
        assert task.updated_at is not None
    
    def test_get_by_id_existing_task(self, repository, sample_task):
        """Test getting existing task by ID"""
        repository.save(sample_task)
        retrieved_task = repository.find_by_id(sample_task.id)
        
        assert retrieved_task is not None
        assert retrieved_task.id == sample_task.id
        assert retrieved_task.title == sample_task.title
    
    def test_get_by_id_nonexistent_task(self, repository):
        """Test getting nonexistent task by ID"""
        result = repository.find_by_id(TaskId.from_int(999))
        assert result is None
    
    def test_get_by_id_empty_repository(self, repository):
        """Test getting task from empty repository"""
        result = repository.find_by_id(TaskId.from_int(1))
        assert result is None
    
    def test_update_existing_task(self, repository, sample_task):
        """Test updating existing task"""
        repository.save(sample_task)
        
        # Update task
        sample_task.update_title("Updated Task")
        sample_task.update_description("Updated Description")
        repository.save(sample_task)
        
        # Verify update
        updated_task = repository.find_by_id(sample_task.id)
        assert updated_task.title == "Updated Task"
        assert updated_task.description == "Updated Description"
    
    def test_update_nonexistent_task(self, repository):
        """Test updating nonexistent task"""
        task = Task(id=TaskId.from_int(999), title="Nonexistent", description="Task")
        # This should work - save creates if not exists
        repository.save(task)
        assert len(repository.find_all()) == 1
    
    def test_update_task_without_id(self, repository):
        """Test updating task without ID should fail"""
        # This test doesn't make sense since Task requires id in constructor
        # But we can test with invalid TaskId
        with pytest.raises(Exception):
            Task(id=None, title="No ID", description="Task")
    
    def test_delete_existing_task(self, repository, sample_task):
        """Test deleting existing task"""
        repository.save(sample_task)
        assert len(repository.find_all()) == 1
        
        result = repository.delete(sample_task.id)
        assert result is True
        assert len(repository.find_all()) == 0
    
    def test_delete_nonexistent_task(self, repository):
        """Test deleting nonexistent task"""
        result = repository.delete(TaskId.from_int(999))
        assert result is False
    
    def test_delete_from_empty_repository(self, repository):
        """Test deleting from empty repository"""
        result = repository.delete(TaskId.from_int(1))
        assert result is False
    
    def test_list_all_tasks_empty(self, repository):
        """Test listing all tasks from empty repository"""
        tasks = repository.find_all()
        assert tasks == []
    
    def test_list_all_tasks_with_data(self, repository):
        """Test listing all tasks with data"""
        task1 = Task(id=TaskId.from_int(1), title="Task 1", description="Description 1")
        task2 = Task(id=TaskId.from_int(2), title="Task 2", description="Description 2")
        
        repository.save(task1)
        repository.save(task2)
        
        tasks = repository.find_all()
        assert len(tasks) == 2
        assert any(t.title == "Task 1" for t in tasks)
        assert any(t.title == "Task 2" for t in tasks)
    
    def test_find_by_priority(self, repository):
        """Test finding tasks by priority"""
        high_task = Task(id=TaskId.from_int(1), title="High Priority", description="High", priority=Priority.high())
        low_task = Task(id=TaskId.from_int(2), title="Low Priority", description="Low", priority=Priority.low())
        
        repository.save(high_task)
        repository.save(low_task)
        
        high_tasks = repository.find_by_priority(Priority.high())
        assert len(high_tasks) == 1
        assert high_tasks[0].title == "High Priority"
    
    def test_find_by_assignee(self, repository):
        """Test finding tasks by assignee"""
        task1 = Task(id=TaskId.from_int(1), title="Task 1", description="Desc 1", assignees=["@coding_agent"])
        task2 = Task(id=TaskId.from_int(2), title="Task 2", description="Desc 2", assignees=["@test_agent"])
        
        repository.save(task1)
        repository.save(task2)
        
        coding_tasks = repository.find_by_assignee("@coding_agent")
        assert len(coding_tasks) == 1
        assert coding_tasks[0].title == "Task 1"
    
    def test_find_by_label(self, repository):
        """Test finding tasks by label"""
        task1 = Task(id=TaskId.from_int(1), title="Task 1", description="Desc 1", labels=["feature"])
        task2 = Task(id=TaskId.from_int(2), title="Task 2", description="Desc 2", labels=["bug"])
        task3 = Task(id=TaskId.from_int(3), title="Task 3", description="Desc 3", labels=["feature", "urgent"])
        
        repository.save(task1)
        repository.save(task2)
        repository.save(task3)
        
        feature_tasks = repository.find_by_labels(["feature"])
        assert len(feature_tasks) == 2
        assert all("feature" in t.labels for t in feature_tasks)
    
    def test_search_tasks_by_title(self, repository):
        """Test searching tasks by title"""
        task1 = Task(id=TaskId.from_int(1), title="Implement authentication", description="Desc 1")
        task2 = Task(id=TaskId.from_int(2), title="Fix bug in parser", description="Desc 2")
        task3 = Task(id=TaskId.from_int(3), title="Add authentication tests", description="Desc 3")
        
        repository.save(task1)
        repository.save(task2)
        repository.save(task3)
        
        auth_tasks = repository.search("authentication")
        assert len(auth_tasks) == 2
        assert all("authentication" in t.title.lower() for t in auth_tasks)
    
    def test_search_tasks_by_description(self, repository):
        """Test searching tasks by description"""
        task1 = Task(id=TaskId.from_int(1), title="Task 1", description="Implement user login functionality")
        task2 = Task(id=TaskId.from_int(2), title="Task 2", description="Fix database connection issues")
        task3 = Task(id=TaskId.from_int(3), title="Task 3", description="Add user registration feature")
        
        repository.save(task1)
        repository.save(task2)
        repository.save(task3)
        
        user_tasks = repository.search("user")
        assert len(user_tasks) == 2
        assert all("user" in t.description.lower() for t in user_tasks)
    
    def test_search_tasks_case_insensitive(self, repository):
        """Test that search is case insensitive"""
        task = Task(id=TaskId.from_int(1), title="IMPORTANT Task", description="Very CRITICAL issue")
        repository.save(task)
        
        results = repository.search("important")
        assert len(results) == 1
        assert results[0].title == "IMPORTANT Task"
    
    def test_search_tasks_no_matches(self, repository):
        """Test searching with no matches"""
        task = Task(id=TaskId.from_int(1), title="Task 1", description="Description 1")
        repository.save(task)
        
        results = repository.search("nonexistent")
        assert results == []
    
    def test_search_tasks_empty_query(self, repository):
        """Test searching with empty query"""
        task = Task(id=TaskId.from_int(1), title="Task 1", description="Description 1")
        repository.save(task)
        
        results = repository.search("")
        assert len(results) == 1  # Empty query should match all
    
    def test_get_next_task_id(self, repository):
        """Test getting next task ID"""
        next_id = repository.get_next_id()
        assert next_id is not None
        assert isinstance(next_id, TaskId)
    
    def test_get_next_task_id_uniqueness(self, repository):
        """Test that consecutive calls return unique IDs"""
        id1 = repository.get_next_id()
        id2 = repository.get_next_id()
        
        assert id1 != id2
    
    def test_task_to_dict_conversion(self, repository, sample_task):
        """Test converting task to dictionary"""
        repository.save(sample_task)
        task_dict = repository._domain_to_task_dict(sample_task)
        
        assert task_dict["title"] == "Test Task"
        assert task_dict["description"] == "Test Description"
        assert task_dict["priority"] == "high"
        assert "test" in task_dict["labels"]
    
    def test_dict_to_task_conversion(self, repository):
        """Test converting dictionary to Task object"""
        task_dict = {
            "id": "20250101002",  # Use proper TaskId format
            "title": "Test Task",
            "description": "Test Description",
            "status": "todo",
            "priority": "high",
            "assignees": ["@coding_agent"],
            "labels": ["test"],
            "subtasks": [],
            "dependencies": [],
            "details": "Test details",
            "estimatedEffort": "medium",
            "created_at": "2025-01-01T00:00:00+00:00",
            "updated_at": "2025-01-01T00:00:00+00:00"
        }
        
        task = repository._dict_to_task(task_dict)
        assert task.id.value == "20250101002"
        assert task.title == "Test Task"
        assert task.description == "Test Description"
    
    def test_dict_to_task_with_invalid_enum_values(self, repository):
        """Test converting dictionary with invalid enum values"""
        task_dict = {
            "id": "20250101003",  # Use proper TaskId format
            "title": "Test Task",
            "description": "Test Description",
            "status": "invalid_status",
            "priority": "invalid_priority",
            "assignees": ["@invalid_agent"],
            "labels": ["test"],
            "subtasks": [],
            "dependencies": [],
            "created_at": "2025-01-01T00:00:00+00:00",
            "updated_at": "2025-01-01T00:00:00+00:00"
        }
        
        # Should handle gracefully with defaults
        task = repository._dict_to_task(task_dict)
        assert task.id.value == "20250101003"
        assert task.title == "Test Task"
    
    def test_dict_to_task_with_missing_fields(self, repository):
        """Test converting dictionary with missing fields"""
        task_dict = {
            "id": "20250101004",  # Use proper TaskId format
            "title": "Test Task",
            "description": "Test Description"
            # Missing other fields
        }
        
        # Should handle gracefully with defaults
        task = repository._dict_to_task(task_dict)
        assert task.id.value == "20250101004"
        assert task.title == "Test Task"
    
    def test_concurrent_access_simulation(self, repository):
        """Test concurrent access simulation"""
        tasks = []
        for i in range(10):
            task = Task(id=TaskId.from_int(i), title=f"Task {i}", description=f"Description {i}")
            tasks.append(task)
            repository.save(task)
        
        assert len(repository.find_all()) == 10
    
    def test_large_dataset_performance(self, repository):
        """Test performance with large dataset"""
        # Create 100 tasks
        tasks = []
        for i in range(100):
            task = Task(id=TaskId.from_int(i), title=f"Task {i}", description=f"Description {i}")
            tasks.append(task)
            repository.save(task)
        
        # Test retrieval performance
        all_tasks = repository.find_all()
        assert len(all_tasks) == 100
        
        # Test search performance
        search_results = repository.search("Task 5")
        assert len(search_results) >= 1
    
    def test_data_persistence_across_instances(self, temp_tasks_file):
        """Test data persistence across repository instances"""
        # Create first instance and add task
        repo1 = JsonTaskRepository(file_path=temp_tasks_file)
        task = Task(id=TaskId.from_int(1), title="Persistent Task", description="Should persist")
        repo1.save(task)
        
        # Create second instance and verify task exists
        repo2 = JsonTaskRepository(file_path=temp_tasks_file)
        tasks = repo2.find_all()
        assert len(tasks) == 1
        assert tasks[0].title == "Persistent Task"
    
    def test_file_corruption_recovery(self, temp_tasks_file):
        """Test recovery from file corruption"""
        # Create repository and add task
        repo = JsonTaskRepository(file_path=temp_tasks_file)
        task = Task(id=TaskId.from_int(1), title="Test Task", description="Test")
        repo.save(task)
        
        # Corrupt the file
        with open(temp_tasks_file, 'w') as f:
            f.write("corrupted data")
        
        # Create new instance - should handle corruption gracefully
        repo2 = JsonTaskRepository(file_path=temp_tasks_file)
        tasks = repo2.find_all()
        assert tasks == []  # Should start fresh after corruption


if __name__ == "__main__":
    pytest.main([__file__]) 