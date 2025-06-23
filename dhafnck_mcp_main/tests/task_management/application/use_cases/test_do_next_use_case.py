"""
Comprehensive unit tests for DoNext Use Case
Tests task selection, prioritization, dependency resolution, and subtask management.
This is P0.2 from the coverage priority list - critical business logic.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from typing import List, Dict, Any
import sys
import os
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from fastmcp.dhafnck_mcp.application.use_cases.do_next import DoNextUseCase, DoNextResponse
from fastmcp.dhafnck_mcp.domain.entities.task import Task
from fastmcp.dhafnck_mcp.domain.value_objects.task_id import TaskId
from fastmcp.dhafnck_mcp.domain.value_objects.task_status import TaskStatus, TaskStatusEnum
from fastmcp.dhafnck_mcp.domain.value_objects.priority import Priority, PriorityLevel


class TestDoNextResponse:
    """Test the DoNextResponse dataclass."""
    
    def test_do_next_response_creation(self):
        """Test DoNextResponse creation with all fields."""
        response = DoNextResponse(
            has_next=True,
            next_item={"type": "task", "id": "123"},
            context={"progress": 50},
            message="Next task found"
        )
        
        assert response.has_next is True
        assert response.next_item == {"type": "task", "id": "123"}
        assert response.context == {"progress": 50}
        assert response.message == "Next task found"
    
    def test_do_next_response_defaults(self):
        """Test DoNextResponse with default values."""
        response = DoNextResponse(has_next=False)
        
        assert response.has_next is False
        assert response.next_item is None
        assert response.context is None
        assert response.message == ""


class TestDoNextUseCase:
    """Test the DoNextUseCase class."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.mock_repository = Mock()
        self.mock_auto_rule_generator = Mock()
        self.use_case = DoNextUseCase(self.mock_repository, self.mock_auto_rule_generator)
        
        # Patch datetime to control task ID generation
        self.patcher = patch('fastmcp.dhafnck_mcp.domain.value_objects.task_id.datetime')
        self.mock_datetime = self.patcher.start()
        self.mock_datetime.now.return_value = datetime(2025, 6, 20)

    def teardown_method(self):
        """Teardown for each test method."""
        self.patcher.stop()
    
    def create_task(self, task_id: int, title: str, status: TaskStatusEnum, 
                   priority: PriorityLevel, dependencies: List[int] = None, 
                   subtasks: List[Dict] = None) -> Task:
        """Helper method to create a task for testing."""
        task = Task(
            id=TaskId.from_int(task_id),
            title=title,
            description=f"Description for {title}",
            status=TaskStatus(status.value),
            priority=Priority(priority.label),
            assignees=["@coding_agent"],
            labels=["test"],
            subtasks=subtasks or []
        )
        
        # Add dependencies if provided
        if dependencies:
            task.dependencies = [TaskId.from_int(dep_id) for dep_id in dependencies]
        
        return task
    
    def test_execute_no_tasks(self):
        """Test execute when no tasks exist."""
        self.mock_repository.find_all.return_value = []
        
        result = self.use_case.execute()
        
        assert result.has_next is False
        assert result.next_item is None
        assert result.context is None
        assert result.message == "No tasks found. Create a task to get started!"
    
    def test_execute_all_tasks_completed(self):
        """Test execute when all tasks are completed."""
        tasks = [
            self.create_task(1, "Task 1", TaskStatusEnum.DONE, PriorityLevel.HIGH),
            self.create_task(2, "Task 2", TaskStatusEnum.DONE, PriorityLevel.MEDIUM)
        ]
        self.mock_repository.find_all.return_value = tasks
        
        result = self.use_case.execute()
        
        assert result.has_next is False
        assert result.next_item is None
        assert result.context is not None
        assert result.context["total_completed"] == 2
        assert result.context["completion_rate"] == 100.0
        assert result.message == "🎉 All tasks completed! Great job!"
    
    def test_execute_no_actionable_tasks(self):
        """Test execute when tasks exist but none are actionable."""
        tasks = [
            self.create_task(1, "Task 1", TaskStatusEnum.BLOCKED, PriorityLevel.HIGH),
            self.create_task(2, "Task 2", TaskStatusEnum.REVIEW, PriorityLevel.MEDIUM),
            self.create_task(3, "Task 3", TaskStatusEnum.TESTING, PriorityLevel.LOW)
        ]
        self.mock_repository.find_all.return_value = tasks
        
        result = self.use_case.execute()
        
        assert result.has_next is False
        assert result.next_item is None
        assert result.message == "No actionable tasks found."
    
    def test_execute_single_todo_task(self):
        """Test execute with a single todo task."""
        task = self.create_task(1, "Single Task", TaskStatusEnum.TODO, PriorityLevel.HIGH)
        self.mock_repository.find_all.return_value = [task]
        
        result = self.use_case.execute()
        
        assert result.has_next is True
        assert result.next_item["type"] == "task"
        assert result.next_item["task"]["id"] == "20250620001"
        assert result.message == "Next action: Work on task 'Single Task'"
    
    def test_execute_priority_ordering(self):
        """Test that tasks are selected by priority order."""
        tasks = [
            self.create_task(1, "Low Priority", TaskStatusEnum.TODO, PriorityLevel.LOW),
            self.create_task(2, "High Priority", TaskStatusEnum.TODO, PriorityLevel.HIGH),
            self.create_task(3, "Critical Priority", TaskStatusEnum.TODO, PriorityLevel.CRITICAL),
            self.create_task(4, "Medium Priority", TaskStatusEnum.TODO, PriorityLevel.MEDIUM)
        ]
        self.mock_repository.find_all.return_value = tasks
        
        result = self.use_case.execute()
        
        assert result.has_next is True
        assert result.next_item["task"]["title"] == "Critical Priority"
    
    def test_execute_status_ordering(self):
        """Test that todo tasks are preferred over in_progress tasks."""
        tasks = [
            self.create_task(1, "In Progress", TaskStatusEnum.IN_PROGRESS, PriorityLevel.HIGH),
            self.create_task(2, "Todo", TaskStatusEnum.TODO, PriorityLevel.HIGH)
        ]
        self.mock_repository.find_all.return_value = tasks
        
        result = self.use_case.execute()
        
        assert result.has_next is True
        assert result.next_item["task"]["title"] == "Todo"
    
    def test_execute_task_with_incomplete_subtasks(self):
        """Test execute when task has incomplete subtasks."""
        subtasks = [
            {"id": 1, "title": "Subtask 1", "completed": True, "assignees": ["@coding_agent"]},
            {"id": 2, "title": "Subtask 2", "completed": False, "assignees": ["@coding_agent"]},
            {"id": 3, "title": "Subtask 3", "completed": False, "assignees": ["@coding_agent"]}
        ]
        task = self.create_task(1, "Task with Subtasks", TaskStatusEnum.TODO, PriorityLevel.HIGH, None, subtasks)
        task.assignees = ["@coding_agent"]
        self.mock_repository.find_all.return_value = [task]
        with patch("fastmcp.dhafnck_mcp.application.use_cases.do_next.generate_docs_for_assignees") as mock_gen:
            result = self.use_case.execute()
            assert mock_gen.call_count > 0, f"generate_docs_for_assignees was not called. Calls: {mock_gen.call_args_list}"
        assert result.has_next is True
        assert result.next_item["type"] == "subtask"
        assert result.next_item["subtask"]["title"] == "Subtask 2"
        assert result.message == "Next action: Work on subtask 'Subtask 2' in task 'Task with Subtasks'"
    
    def test_execute_task_with_subtask_assignees(self):
        """Test execute when subtasks have their own assignees."""
        subtasks = [
            {"id": 1, "title": "Subtask 1", "completed": True, "assignees": ["@coding_agent"]},
            {"id": 2, "title": "Subtask 2", "completed": False, "assignees": ["@coding_agent"]}
        ]
        task = self.create_task(1, "Task with Subtasks", TaskStatusEnum.TODO, PriorityLevel.HIGH, None, subtasks)
        task.assignees = ["@coding_agent"]
        self.mock_repository.find_all.return_value = [task]
        with patch("fastmcp.dhafnck_mcp.application.use_cases.do_next.generate_docs_for_assignees") as mock_gen:
            result = self.use_case.execute()
            assert mock_gen.call_count > 0, f"generate_docs_for_assignees was not called. Calls: {mock_gen.call_args_list}"
        assert result.has_next is True
        assert result.next_item["type"] == "subtask"
        assert result.next_item["subtask"]["title"] == "Subtask 2"
        assert result.message == "Next action: Work on subtask 'Subtask 2' in task 'Task with Subtasks'"
    
    def test_execute_task_with_satisfied_dependencies(self):
        """Test execute when task dependencies are satisfied."""
        tasks = [
            self.create_task(1, "Dependency Task", TaskStatusEnum.DONE, PriorityLevel.LOW),
            self.create_task(2, "Dependent Task", TaskStatusEnum.TODO, PriorityLevel.HIGH, [1])
        ]
        self.mock_repository.find_all.return_value = tasks
        
        result = self.use_case.execute()
        
        assert result.has_next is True
        assert result.next_item["task"]["title"] == "Dependent Task"
    
    def test_execute_task_with_unsatisfied_dependencies(self):
        """Test execute when task dependencies are not satisfied."""
        tasks = [
            self.create_task(1, "Dependency Task", TaskStatusEnum.TODO, PriorityLevel.LOW),
            self.create_task(2, "Dependent Task", TaskStatusEnum.TODO, PriorityLevel.HIGH, [1])
        ]
        self.mock_repository.find_all.return_value = tasks
        
        result = self.use_case.execute()
        
        assert result.has_next is True
        assert result.next_item["task"]["title"] == "Dependency Task"
    
    def test_execute_all_tasks_blocked_by_dependencies(self):
        """Test execute when all tasks are blocked by dependencies."""
        tasks = [
            self.create_task(1, "Task 1", TaskStatusEnum.TODO, PriorityLevel.HIGH, [3]),
            self.create_task(2, "Task 2", TaskStatusEnum.TODO, PriorityLevel.MEDIUM, [3]),
            self.create_task(3, "Blocking Task", TaskStatusEnum.IN_PROGRESS, PriorityLevel.LOW)
        ]
        self.mock_repository.find_all.return_value = tasks
        
        result = self.use_case.execute()
        
        assert result.has_next is True # The blocking task should be returned
        assert result.next_item["task"]["title"] == "Blocking Task"


class TestDoNextPrivateMethods:
    """Test private methods of DoNextUseCase."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.mock_repository = Mock()
        self.mock_auto_rule_generator = Mock()
        self.use_case = DoNextUseCase(self.mock_repository, self.mock_auto_rule_generator)
        # Patch datetime to control task ID generation
        self.patcher = patch('fastmcp.dhafnck_mcp.domain.value_objects.task_id.datetime')
        self.mock_datetime = self.patcher.start()
        self.mock_datetime.now.return_value = datetime(2025, 6, 20)

    def teardown_method(self):
        """Teardown for each test method."""
        self.patcher.stop()

    def create_task(self, task_id: int, title: str, status: TaskStatusEnum, 
                   priority: PriorityLevel, dependencies: List[int] = None, 
                   subtasks: List[Dict] = None) -> Task:
        """Helper method to create a task for testing."""
        task = Task(
            id=TaskId.from_int(task_id),
            title=title,
            description=f"Description for {title}",
            status=TaskStatus(status.value),
            priority=Priority(priority.label),
            assignees=["@coding_agent"],
            labels=["test"],
            subtasks=subtasks or []
        )
        
        # Add dependencies if provided
        if dependencies:
            task.dependencies = [TaskId.from_int(dep_id) for dep_id in dependencies]
        
        return task
    
    def test_sort_tasks_by_priority_order(self):
        """Test _sort_tasks_by_priority by priority order."""
        tasks = [
            self.create_task(1, "Low", TaskStatusEnum.TODO, PriorityLevel.LOW),
            self.create_task(2, "High", TaskStatusEnum.TODO, PriorityLevel.HIGH),
            self.create_task(3, "Critical", TaskStatusEnum.TODO, PriorityLevel.CRITICAL),
            self.create_task(4, "Medium", TaskStatusEnum.TODO, PriorityLevel.MEDIUM)
        ]
        
        sorted_tasks = self.use_case._sort_tasks_by_priority(tasks)
        
        assert [task.title for task in sorted_tasks] == ["Critical", "High", "Medium", "Low"]
    
    def test_sort_tasks_by_status_order(self):
        """Test _sort_tasks_by_priority by status order (todo before in_progress)."""
        tasks = [
            self.create_task(1, "In Progress", TaskStatusEnum.IN_PROGRESS, PriorityLevel.HIGH),
            self.create_task(2, "Todo", TaskStatusEnum.TODO, PriorityLevel.HIGH)
        ]
        
        sorted_tasks = self.use_case._sort_tasks_by_priority(tasks)
        
        assert [task.title for task in sorted_tasks] == ["Todo", "In Progress"]
    
    def test_can_task_be_started_no_dependencies(self):
        """Test _can_task_be_started with no dependencies."""
        task = self.create_task(1, "No Deps", TaskStatusEnum.TODO, PriorityLevel.HIGH)
        all_tasks = [task]
        
        assert self.use_case._can_task_be_started(task, all_tasks) is True
    
    def test_can_task_be_started_dependencies_completed(self):
        """Test _can_task_be_started with completed dependencies."""
        dep_task = self.create_task(1, "Dep", TaskStatusEnum.DONE, PriorityLevel.LOW)
        task = self.create_task(2, "Has Deps", TaskStatusEnum.TODO, PriorityLevel.HIGH, [1])
        all_tasks = [dep_task, task]
        
        assert self.use_case._can_task_be_started(task, all_tasks) is True
    
    def test_can_task_be_started_dependencies_not_completed(self):
        """Test _can_task_be_started with incomplete dependencies."""
        dep_task = self.create_task(1, "Dep", TaskStatusEnum.TODO, PriorityLevel.LOW)
        task = self.create_task(2, "Has Deps", TaskStatusEnum.TODO, PriorityLevel.HIGH, [1])
        all_tasks = [dep_task, task]
        
        assert self.use_case._can_task_be_started(task, all_tasks) is False
    
    def test_find_next_subtask_no_subtasks(self):
        """Test _find_next_subtask when there are no subtasks."""
        task = self.create_task(1, "No Subtasks", TaskStatusEnum.TODO, PriorityLevel.HIGH)
        
        next_subtask = self.use_case._find_next_subtask(task)
        
        assert next_subtask is None
    
    def test_find_next_subtask_first_incomplete(self):
        """Test _find_next_subtask finds the first incomplete subtask."""
        subtasks = [
            {"id": 1, "title": "Subtask 1", "completed": True},
            {"id": 2, "title": "Subtask 2", "completed": False},
            {"id": 3, "title": "Subtask 3", "completed": False}
        ]
        task = self.create_task(1, "With Subtasks", TaskStatusEnum.IN_PROGRESS, PriorityLevel.MEDIUM, None, subtasks)
        
        result = self.use_case._find_next_subtask(task)
        
        assert result is not None
        assert result["title"] == "Subtask 2"

    def test_find_next_subtask_skip_completed(self):
        """Test finding next subtask skips completed ones."""
        subtasks = [
            {"id": 1, "title": "Subtask 1", "completed": True},
            {"id": 2, "title": "Subtask 2", "completed": False}
        ]
        task = self.create_task(1, "With Subtasks", TaskStatusEnum.IN_PROGRESS, PriorityLevel.MEDIUM, None, subtasks)
        
        result = self.use_case._find_next_subtask(task)
        
        assert result is not None
        assert result["title"] == "Subtask 2"
    
    def test_task_to_dict_without_subtasks(self):
        """Test converting task to dict without subtasks."""
        task = self.create_task(1, "Test Task", TaskStatusEnum.IN_PROGRESS, PriorityLevel.HIGH)
        
        result = self.use_case._task_to_dict(task)
        
        assert result["id"] == "20250620001"
        assert result["title"] == "Test Task"
    
    def test_task_to_dict_with_subtasks(self):
        """Test converting task to dict with subtasks."""
        subtasks = [
            {"id": "20250620001.001", "title": "Subtask 1", "completed": True},
            {"id": "20250620001.002", "title": "Subtask 2", "completed": False}
        ]
        task = self.create_task(1, "Test Task", TaskStatusEnum.IN_PROGRESS, PriorityLevel.HIGH, None, subtasks)
        
        # Mock the get_subtask_progress method
        task.get_subtask_progress = Mock(return_value={"completed": 1, "total": 2, "percentage": 50.0})
        
        result = self.use_case._task_to_dict(task)
        
        assert result["id"] == "20250620001"
        assert result["title"] == "Test Task"
        assert "subtask_progress" in result
        assert result["subtask_progress"]["percentage"] == 50.0
    
    def test_get_task_context_basic(self):
        """Test getting basic task context."""
        task = self.create_task(1, "Test Task", TaskStatusEnum.IN_PROGRESS, PriorityLevel.MEDIUM)
        all_tasks = [
            task,
            self.create_task(2, "Other Task", TaskStatusEnum.DONE, PriorityLevel.MEDIUM)
        ]
        
        result = self.use_case._get_task_context(task, all_tasks)
        
        assert result["task_id"] == "20250620001"
        assert result["can_start"] is True
        assert result["dependency_count"] == 0
        assert result["blocking_count"] == 0
        assert result["overall_progress"]["completed"] == 1
        assert result["overall_progress"]["total"] == 2
        assert result["overall_progress"]["percentage"] == 50.0
    
    def test_get_completion_context(self):
        """Test getting completion context."""
        tasks = [
            self.create_task(1, "Task 1", TaskStatusEnum.DONE, PriorityLevel.HIGH),
            self.create_task(2, "Task 2", TaskStatusEnum.DONE, PriorityLevel.MEDIUM)
        ]
        
        result = self.use_case._get_completion_context(tasks)
        
        assert result["total_completed"] == 2
        assert result["completion_rate"] == 100.0
        assert "priority_breakdown" in result
    
    def test_get_blocking_info(self):
        """Test getting blocking information for blocked tasks."""
        dep_task = self.create_task(1, "Dependency", TaskStatusEnum.IN_PROGRESS, PriorityLevel.LOW)
        blocked_task = self.create_task(2, "Blocked Task", TaskStatusEnum.TODO, PriorityLevel.HIGH, [1])
        all_tasks = [dep_task, blocked_task]
        
        result = self.use_case._get_blocking_info([blocked_task], all_tasks)
        
        assert len(result["blocked_tasks"]) == 1
        assert result["blocked_tasks"][0]["title"] == "Blocked Task"
        assert len(result["blocked_tasks"][0]["blocked_by"]) == 1
        assert result["blocked_tasks"][0]["blocked_by"][0]["title"] == "Dependency"
        
        assert len(result["required_completions"]) == 1
        assert result["required_completions"][0]["title"] == "Dependency"


# Pytest markers for test categorization
pytestmark = [
    pytest.mark.unit,
    pytest.mark.application,
    pytest.mark.mcp
] 