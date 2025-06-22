"""Comprehensive tests for TaskTree domain entity to improve coverage."""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from fastmcp.task_management.domain.entities.task_tree import TaskTree
from fastmcp.task_management.domain.entities.task import Task
from fastmcp.task_management.domain.value_objects.task_id import TaskId
from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
from fastmcp.task_management.domain.value_objects.priority import Priority


class TestTaskTreeEntity:
    """Comprehensive tests for TaskTree entity"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.tree_id = "tree-001"
        self.tree_name = "Test Tree"
        self.tree_description = "A test task tree"
        self.project_id = "project-123"
        self.created_at = datetime.now()
        
        self.task_tree = TaskTree(
            id=self.tree_id,
            name=self.tree_name,
            description=self.tree_description,
            project_id=self.project_id,
            created_at=self.created_at
        )
    
    def create_mock_task(self, task_id: str, title: str = "Test Task", status: str = "todo", priority: str = "medium"):
        """Helper method to create a mock task"""
        task = Mock(spec=Task)
        task.id = Mock()
        task.id.value = task_id
        task.title = title
        task.description = f"Description for {title}"
        task.status = Mock()
        task.status.is_done.return_value = (status == "done")
        task.status.value = status
        task.priority = Mock()
        task.priority.value = priority
        task.assignees = []
        task.dependencies = []
        task.subtasks = []
        task.created_at = datetime.now()
        task.add_subtask = Mock()
        return task
    
    def test_task_tree_initialization(self):
        """Test task tree initialization with required fields"""
        assert self.task_tree.id == self.tree_id
        assert self.task_tree.name == self.tree_name
        assert self.task_tree.description == self.tree_description
        assert self.task_tree.project_id == self.project_id
        assert self.task_tree.created_at == self.created_at
        assert isinstance(self.task_tree.updated_at, datetime)
        assert len(self.task_tree.root_tasks) == 0
        assert len(self.task_tree.all_tasks) == 0
        assert self.task_tree.assigned_agent_id is None
        assert self.task_tree.priority == "medium"
        assert self.task_tree.status == "active"
    
    def test_add_root_task(self):
        """Test adding a root task to the tree"""
        task = self.create_mock_task("task-001", "Root Task")
        initial_updated = self.task_tree.updated_at
        
        self.task_tree.add_root_task(task)
        
        assert "task-001" in self.task_tree.root_tasks
        assert "task-001" in self.task_tree.all_tasks
        assert self.task_tree.root_tasks["task-001"] == task
        assert self.task_tree.all_tasks["task-001"] == task
        assert self.task_tree.updated_at > initial_updated
    
    def test_add_task_as_root(self):
        """Test adding a task as root (no parent)"""
        task = self.create_mock_task("task-002", "Another Root Task")
        initial_updated = self.task_tree.updated_at
        
        self.task_tree.add_task(task)
        
        assert "task-002" in self.task_tree.root_tasks
        assert "task-002" in self.task_tree.all_tasks
        assert self.task_tree.updated_at > initial_updated
    
    def test_add_task_as_subtask(self):
        """Test adding a task as a subtask of another task"""
        # Add parent task first
        parent_task = self.create_mock_task("parent-001", "Parent Task")
        self.task_tree.add_root_task(parent_task)
        
        # Add child task
        child_task = self.create_mock_task("child-001", "Child Task")
        
        self.task_tree.add_task(child_task, parent_task_id="parent-001")
        
        # Verify child task was added to all_tasks
        assert "child-001" in self.task_tree.all_tasks
        assert self.task_tree.all_tasks["child-001"] == child_task
        
        # Verify parent's add_subtask was called
        parent_task.add_subtask.assert_called_once()
        call_args = parent_task.add_subtask.call_args[0][0]
        assert call_args["id"] == "child-001"
        assert call_args["title"] == "Child Task"
        assert call_args["description"] == "Description for Child Task"
        assert call_args["completed"] is False
        assert call_args["assignees"] == []
    
    def test_add_task_with_nonexistent_parent(self):
        """Test adding task with non-existent parent raises error"""
        task = self.create_mock_task("task-003", "Orphan Task")
        
        with pytest.raises(ValueError, match="Parent task nonexistent-parent not found in tree"):
            self.task_tree.add_task(task, parent_task_id="nonexistent-parent")
    
    def test_get_task(self):
        """Test getting a specific task from the tree"""
        task = self.create_mock_task("task-004", "Findable Task")
        self.task_tree.add_root_task(task)
        
        retrieved_task = self.task_tree.get_task("task-004")
        assert retrieved_task == task
        
        # Test getting non-existent task
        assert self.task_tree.get_task("nonexistent") is None
    
    def test_has_task(self):
        """Test checking if a task exists in the tree"""
        task = self.create_mock_task("task-005", "Existing Task")
        self.task_tree.add_root_task(task)
        
        assert self.task_tree.has_task("task-005")
        assert not self.task_tree.has_task("nonexistent")
    
    def test_get_available_tasks(self):
        """Test getting tasks that are ready for work"""
        # Add completed task (should not be available)
        completed_task = self.create_mock_task("completed-001", "Completed Task", status="done")
        self.task_tree.add_root_task(completed_task)
        
        # Add available task
        available_task = self.create_mock_task("available-001", "Available Task", status="todo")
        self.task_tree.add_root_task(available_task)
        
        # Add task with unfulfilled dependency
        blocked_task = self.create_mock_task("blocked-001", "Blocked Task", status="todo")
        dep_mock = Mock()
        dep_mock.value = "dependency-001"
        blocked_task.dependencies = [dep_mock]
        self.task_tree.add_root_task(blocked_task)
        
        # Add the dependency task (not completed)
        dep_task = self.create_mock_task("dependency-001", "Dependency Task", status="todo")
        self.task_tree.add_root_task(dep_task)
        
        available_tasks = self.task_tree.get_available_tasks()
        
        # Should only include the available task and dependency task
        available_task_ids = [task.id.value for task in available_tasks]
        assert "available-001" in available_task_ids
        assert "dependency-001" in available_task_ids
        assert "completed-001" not in available_task_ids
        assert "blocked-001" not in available_task_ids
    
    def test_get_next_task(self):
        """Test getting the next highest priority task"""
        # Add tasks with different priorities
        low_task = self.create_mock_task("low-001", "Low Priority Task", priority="low")
        high_task = self.create_mock_task("high-001", "High Priority Task", priority="high")
        medium_task = self.create_mock_task("medium-001", "Medium Priority Task", priority="medium")
        
        self.task_tree.add_root_task(low_task)
        self.task_tree.add_root_task(high_task)
        self.task_tree.add_root_task(medium_task)
        
        next_task = self.task_tree.get_next_task()
        
        # Should return the high priority task
        assert next_task.id.value == "high-001"
    
    def test_get_next_task_no_available_tasks(self):
        """Test getting next task when no tasks are available"""
        # Add only completed tasks
        completed_task = self.create_mock_task("completed-001", "Completed Task", status="done")
        self.task_tree.add_root_task(completed_task)
        
        next_task = self.task_tree.get_next_task()
        assert next_task is None
    
    def test_get_task_count(self):
        """Test getting total number of tasks in the tree"""
        assert self.task_tree.get_task_count() == 0
        
        task1 = self.create_mock_task("task-001", "Task 1")
        task2 = self.create_mock_task("task-002", "Task 2")
        
        self.task_tree.add_root_task(task1)
        assert self.task_tree.get_task_count() == 1
        
        self.task_tree.add_root_task(task2)
        assert self.task_tree.get_task_count() == 2
    
    def test_get_completed_task_count(self):
        """Test getting number of completed tasks"""
        assert self.task_tree.get_completed_task_count() == 0
        
        todo_task = self.create_mock_task("todo-001", "Todo Task", status="todo")
        done_task = self.create_mock_task("done-001", "Done Task", status="done")
        
        self.task_tree.add_root_task(todo_task)
        assert self.task_tree.get_completed_task_count() == 0
        
        self.task_tree.add_root_task(done_task)
        assert self.task_tree.get_completed_task_count() == 1
    
    def test_get_progress_percentage(self):
        """Test getting completion percentage for the tree"""
        # Empty tree
        assert self.task_tree.get_progress_percentage() == 0.0
        
        # Add tasks
        task1 = self.create_mock_task("task-001", "Task 1", status="todo")
        task2 = self.create_mock_task("task-002", "Task 2", status="done")
        task3 = self.create_mock_task("task-003", "Task 3", status="done")
        
        self.task_tree.add_root_task(task1)
        self.task_tree.add_root_task(task2)
        self.task_tree.add_root_task(task3)
        
        # 2 out of 3 tasks completed = 66.67%
        progress = self.task_tree.get_progress_percentage()
        assert abs(progress - 66.66666666666667) < 0.001
    
    def test_get_tree_status(self):
        """Test getting comprehensive status of the task tree"""
        # Add tasks with different statuses and priorities
        task1 = self.create_mock_task("task-001", "Task 1", status="todo", priority="high")
        task2 = self.create_mock_task("task-002", "Task 2", status="done", priority="medium")
        task3 = self.create_mock_task("task-003", "Task 3", status="in_progress", priority="high")
        
        self.task_tree.add_root_task(task1)
        self.task_tree.add_root_task(task2)
        self.task_tree.add_root_task(task3)
        
        status = self.task_tree.get_tree_status()
        
        assert status["tree_id"] == self.tree_id
        assert status["tree_name"] == self.tree_name
        assert status["assigned_agent"] is None
        assert status["status"] == "active"
        assert status["priority"] == "medium"
        assert status["total_tasks"] == 3
        assert status["completed_tasks"] == 1
        assert abs(status["progress_percentage"] - 33.33333333333333) < 0.001
        assert status["status_breakdown"]["todo"] == 1
        assert status["status_breakdown"]["done"] == 1
        assert status["status_breakdown"]["in_progress"] == 1
        assert status["priority_breakdown"]["high"] == 2
        assert status["priority_breakdown"]["medium"] == 1
        assert status["available_tasks"] == 2  # todo and in_progress tasks
        assert "created_at" in status
        assert "updated_at" in status
    
    def test_mark_as_completed(self):
        """Test marking the entire tree as completed"""
        initial_updated = self.task_tree.updated_at
        
        self.task_tree.mark_as_completed()
        
        assert self.task_tree.status == "completed"
        assert self.task_tree.updated_at > initial_updated
    
    def test_pause_tree(self):
        """Test pausing work on the tree"""
        initial_updated = self.task_tree.updated_at
        
        self.task_tree.pause_tree()
        
        assert self.task_tree.status == "paused"
        assert self.task_tree.updated_at > initial_updated
    
    def test_resume_tree(self):
        """Test resuming work on the tree"""
        self.task_tree.pause_tree()
        initial_updated = self.task_tree.updated_at
        
        self.task_tree.resume_tree()
        
        assert self.task_tree.status == "active"
        assert self.task_tree.updated_at > initial_updated
    
    def test_archive_tree(self):
        """Test archiving the tree"""
        initial_updated = self.task_tree.updated_at
        
        self.task_tree.archive_tree()
        
        assert self.task_tree.status == "archived"
        assert self.task_tree.updated_at > initial_updated
    
    def test_add_subtasks_to_index(self):
        """Test adding subtasks to the flattened index"""
        # Create a task with subtasks
        parent_task = self.create_mock_task("parent-001", "Parent Task")
        parent_task.subtasks = [
            {
                "id": "20240620001",
                "title": "Subtask 1",
                "description": "First subtask",
                "completed": False,
                "assignees": ["agent1"]
            },
            {
                "id": "20240620002",
                "title": "Subtask 2",
                "description": "Second subtask",
                "completed": True,
                "assignees": []
            }
        ]
        
        with patch('src.task_mcp.domain.entities.task_tree.Task') as mock_task_class:
            # Mock the Task.create method
            mock_subtask1 = Mock()
            mock_subtask2 = Mock()
            mock_task_class.create.side_effect = [mock_subtask1, mock_subtask2]
            
            self.task_tree.add_root_task(parent_task)
            
            # Verify subtasks were added to all_tasks
            assert "20240620001" in self.task_tree.all_tasks
            assert "20240620002" in self.task_tree.all_tasks
            assert self.task_tree.all_tasks["20240620001"] == mock_subtask1
            assert self.task_tree.all_tasks["20240620002"] == mock_subtask2
    
    def test_is_task_available_for_work(self):
        """Test checking if a task is available for work"""
        # Test completed task (not available)
        completed_task = self.create_mock_task("completed-001", "Completed Task", status="done")
        assert not self.task_tree._is_task_available_for_work(completed_task)
        
        # Test task with no dependencies (available)
        available_task = self.create_mock_task("available-001", "Available Task", status="todo")
        assert self.task_tree._is_task_available_for_work(available_task)
        
        # Test task with completed dependency (available)
        task_with_completed_dep = self.create_mock_task("task-with-dep", "Task with Dependency", status="todo")
        dep_mock = Mock()
        dep_mock.value = "completed-dep"
        task_with_completed_dep.dependencies = [dep_mock]
        
        # Add completed dependency to tree
        completed_dep = self.create_mock_task("completed-dep", "Completed Dependency", status="done")
        self.task_tree.add_root_task(completed_dep)
        self.task_tree.add_root_task(task_with_completed_dep)
        
        assert self.task_tree._is_task_available_for_work(task_with_completed_dep)
        
        # Test task with incomplete dependency (not available)
        task_with_incomplete_dep = self.create_mock_task("task-with-incomplete-dep", "Task with Incomplete Dependency", status="todo")
        incomplete_dep_mock = Mock()
        incomplete_dep_mock.value = "incomplete-dep"
        task_with_incomplete_dep.dependencies = [incomplete_dep_mock]
        
        # Add incomplete dependency to tree
        incomplete_dep = self.create_mock_task("incomplete-dep", "Incomplete Dependency", status="todo")
        self.task_tree.add_root_task(incomplete_dep)
        self.task_tree.add_root_task(task_with_incomplete_dep)
        
        assert not self.task_tree._is_task_available_for_work(task_with_incomplete_dep)
    
    def test_get_dependency_graph(self):
        """Test getting dependency graph representation"""
        # Create tasks with dependencies
        task1 = self.create_mock_task("task-001", "Task 1", status="todo")
        task2 = self.create_mock_task("task-002", "Task 2", status="todo")
        task3 = self.create_mock_task("task-003", "Task 3", status="todo")
        
        # Task 2 depends on Task 1
        dep_mock = Mock()
        dep_mock.value = "task-001"
        task2.dependencies = [dep_mock]
        
        # Task 3 depends on Task 2
        dep_mock2 = Mock()
        dep_mock2.value = "task-002"
        task3.dependencies = [dep_mock2]
        
        self.task_tree.add_root_task(task1)
        self.task_tree.add_root_task(task2)
        self.task_tree.add_root_task(task3)
        
        graph = self.task_tree.get_dependency_graph()
        
        # Verify graph structure
        assert "task-001" in graph
        assert "task-002" in graph
        assert "task-003" in graph
        
        # Check task 1 (no dependencies, blocks task 2)
        assert graph["task-001"]["title"] == "Task 1"
        assert graph["task-001"]["dependencies"] == []
        assert graph["task-001"]["blocks"] == ["task-002"]
        
        # Check task 2 (depends on task 1, blocks task 3)
        assert graph["task-002"]["title"] == "Task 2"
        assert graph["task-002"]["dependencies"] == ["task-001"]
        assert graph["task-002"]["blocks"] == ["task-003"]
        
        # Check task 3 (depends on task 2, blocks nothing)
        assert graph["task-003"]["title"] == "Task 3"
        assert graph["task-003"]["dependencies"] == ["task-002"]
        assert graph["task-003"]["blocks"] == [] 