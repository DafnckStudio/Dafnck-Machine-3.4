"""Unit Tests for Dependency Management"""

import pytest
from datetime import datetime
from task_mcp.domain import Task, TaskId, TaskStatus, Priority
from task_mcp.application.use_cases.manage_dependencies import (
    ManageDependenciesUseCase, 
    AddDependencyRequest
)
from task_mcp.infrastructure.repositories.json_task_repository import InMemoryTaskRepository
from task_mcp.domain.exceptions import TaskNotFoundError


class TestDependencyManagement:
    """Test dependency management functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.repository = InMemoryTaskRepository()
        self.use_case = ManageDependenciesUseCase(self.repository)
        
        # Create test tasks
        self.task1 = Task(
            id=TaskId.from_int(1),
            title="Task 1",
            description="First task",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        self.task2 = Task(
            id=TaskId.from_int(2),
            title="Task 2", 
            description="Second task",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        self.task3 = Task(
            id=TaskId.from_int(3),
            title="Task 3",
            description="Third task",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        self.repository.save(self.task1)
        self.repository.save(self.task2)
        self.repository.save(self.task3)
    
    def test_add_dependency_success(self):
        """Test adding a dependency successfully"""
        request = AddDependencyRequest(task_id=1, dependency_id=2)
        response = self.use_case.add_dependency(request)
        
        assert response.success is True
        assert response.task_id.endswith("1")  # TaskId format: 20250618001
        assert any(dep.endswith("2") for dep in response.dependencies)  # TaskId format: 20250618002
        assert "added successfully" in response.message
    
    def test_add_dependency_task_not_found(self):
        """Test adding dependency when main task doesn't exist"""
        request = AddDependencyRequest(task_id=999, dependency_id=2)
        
        with pytest.raises(TaskNotFoundError):
            self.use_case.add_dependency(request)
    
    def test_add_dependency_dependency_task_not_found(self):
        """Test adding dependency when dependency task doesn't exist"""
        request = AddDependencyRequest(task_id=1, dependency_id=999)
        
        with pytest.raises(TaskNotFoundError):
            self.use_case.add_dependency(request)
    
    def test_add_circular_dependency(self):
        """Test preventing circular dependencies"""
        request = AddDependencyRequest(task_id=1, dependency_id=1)
        response = self.use_case.add_dependency(request)
        
        assert response.success is False
        assert "circular reference" in response.message
    
    def test_add_duplicate_dependency(self):
        """Test adding duplicate dependency"""
        # Add dependency first time
        request = AddDependencyRequest(task_id=1, dependency_id=2)
        response1 = self.use_case.add_dependency(request)
        assert response1.success is True
        
        # Try to add same dependency again
        response2 = self.use_case.add_dependency(request)
        assert response2.success is False
        assert "already exists" in response2.message
    
    def test_remove_dependency_success(self):
        """Test removing a dependency successfully"""
        # Add dependency first
        request = AddDependencyRequest(task_id=1, dependency_id=2)
        self.use_case.add_dependency(request)
        
        # Remove the dependency
        response = self.use_case.remove_dependency(1, 2)
        
        assert response.success is True
        assert response.task_id.endswith("1")  # TaskId format: 20250618001
        assert not any(dep.endswith("2") for dep in response.dependencies)  # Should not contain TaskId ending with 2
        assert "removed successfully" in response.message
    
    def test_remove_dependency_not_found(self):
        """Test removing non-existent dependency"""
        response = self.use_case.remove_dependency(1, 2)
        
        assert response.success is False
        assert "does not exist" in response.message
    
    def test_remove_dependency_task_not_found(self):
        """Test removing dependency from non-existent task"""
        with pytest.raises(TaskNotFoundError):
            self.use_case.remove_dependency(999, 2)
    
    def test_get_dependencies_success(self):
        """Test getting dependencies for a task"""
        # Add multiple dependencies
        request1 = AddDependencyRequest(task_id=1, dependency_id=2)
        request2 = AddDependencyRequest(task_id=1, dependency_id=3)
        self.use_case.add_dependency(request1)
        self.use_case.add_dependency(request2)
        
        # Get dependencies
        response = self.use_case.get_dependencies(1)
        
        assert response["task_id"].endswith("1")  # TaskId format: 20250618001
        assert any(dep_id.endswith("2") for dep_id in response["dependency_ids"])  # TaskId ending with 2
        assert any(dep_id.endswith("3") for dep_id in response["dependency_ids"])  # TaskId ending with 3
        assert len(response["dependencies"]) == 2
        
        # Check detailed dependency info
        dep_details = response["dependencies"]
        dep_ids = [dep["id"] for dep in dep_details]
        assert any(dep_id.endswith("2") for dep_id in dep_ids)
        assert any(dep_id.endswith("3") for dep_id in dep_ids)
        
        # Check dependency details
        task2_detail = next(dep for dep in dep_details if str(dep["id"]).endswith("2"))
        assert task2_detail["title"] == "Task 2"
        assert task2_detail["status"] == "todo"
        assert task2_detail["priority"] == "medium"
    
    def test_get_dependencies_empty(self):
        """Test getting dependencies for task with no dependencies"""
        response = self.use_case.get_dependencies(1)
        
        assert response["task_id"].endswith("1")  # TaskId format: 20250618001
        assert response["dependency_ids"] == []
        assert response["dependencies"] == []
        assert response["can_start"] is True
    
    def test_clear_dependencies(self):
        """Test clearing all dependencies from a task"""
        # Add multiple dependencies
        request1 = AddDependencyRequest(task_id=1, dependency_id=2)
        request2 = AddDependencyRequest(task_id=1, dependency_id=3)
        self.use_case.add_dependency(request1)
        self.use_case.add_dependency(request2)
        
        # Clear all dependencies
        response = self.use_case.clear_dependencies(1)
        
        assert response.success is True
        assert response.task_id.endswith("1")  # TaskId format: 20250618001
        assert response.dependencies == []
        assert "Cleared 2 dependencies" in response.message
    
    def test_clear_dependencies_empty(self):
        """Test clearing dependencies from task with no dependencies"""
        response = self.use_case.clear_dependencies(1)
        
        assert response.success is True
        assert "Cleared 0 dependencies" in response.message
    
    def test_get_blocking_tasks(self):
        """Test getting tasks blocked by this task"""
        # Make task 2 and task 3 depend on task 1
        request1 = AddDependencyRequest(task_id=2, dependency_id=1)
        request2 = AddDependencyRequest(task_id=3, dependency_id=1)
        self.use_case.add_dependency(request1)
        self.use_case.add_dependency(request2)
        
        # Get tasks blocked by task 1
        response = self.use_case.get_blocking_tasks(1)
        
        assert response["task_id"].endswith("1")  # TaskId format: 20250618001
        assert response["blocking_count"] == 2
        
        blocking_ids = [task["id"] for task in response["blocking_tasks"]]
        assert any(str(task_id).endswith("2") for task_id in blocking_ids)
        assert any(str(task_id).endswith("3") for task_id in blocking_ids)
        
        # Check blocking task details
        task2_detail = next(task for task in response["blocking_tasks"] if str(task["id"]).endswith("2"))
        assert task2_detail["title"] == "Task 2"
        assert task2_detail["status"] == "todo"
    
    def test_get_blocking_tasks_none(self):
        """Test getting blocking tasks when none exist"""
        response = self.use_case.get_blocking_tasks(1)
        
        assert response["task_id"].endswith("1")  # TaskId format: 20250618001
        assert response["blocking_count"] == 0
        assert response["blocking_tasks"] == []
    
    def test_multiple_dependencies_chain(self):
        """Test complex dependency chain"""
        # Create chain: Task 1 -> Task 2 -> Task 3
        request1 = AddDependencyRequest(task_id=2, dependency_id=1)
        request2 = AddDependencyRequest(task_id=3, dependency_id=2)
        
        self.use_case.add_dependency(request1)
        self.use_case.add_dependency(request2)
        
        # Check task 2 dependencies
        task2_deps = self.use_case.get_dependencies(2)
        assert any(dep_id.endswith("1") for dep_id in task2_deps["dependency_ids"])
        
        # Check task 3 dependencies
        task3_deps = self.use_case.get_dependencies(3)
        assert any(dep_id.endswith("2") for dep_id in task3_deps["dependency_ids"])
        
        # Check blocking relationships
        task1_blocking = self.use_case.get_blocking_tasks(1)
        assert any(str(t["id"]).endswith("2") for t in task1_blocking["blocking_tasks"])
        
        task2_blocking = self.use_case.get_blocking_tasks(2)
        assert any(str(t["id"]).endswith("3") for t in task2_blocking["blocking_tasks"])
    
    def test_dependency_persistence(self):
        """Test that dependencies persist across repository operations"""
        # Add dependency
        request = AddDependencyRequest(task_id=1, dependency_id=2)
        self.use_case.add_dependency(request)
        
        # Reload task from repository
        reloaded_task = self.repository.find_by_id(TaskId.from_int(1))
        
        assert len(reloaded_task.dependencies) == 1
        assert any(dep_id.endswith("2") for dep_id in reloaded_task.get_dependency_ids())
    
    def test_can_start_with_dependencies(self):
        """Test can_start logic with dependencies"""
        # Task without dependencies can start
        response = self.use_case.get_dependencies(1)
        assert response["can_start"] is True
        
        # Add dependency - should still be able to start (simplified logic)
        request = AddDependencyRequest(task_id=1, dependency_id=2)
        self.use_case.add_dependency(request)
        
        response = self.use_case.get_dependencies(1)
        # Note: The current implementation uses task.can_be_started() which only checks if status is todo
        # In a more complex implementation, this would check if dependencies are completed
        assert response["can_start"] is True  # Because task is still in todo status 