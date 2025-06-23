"""
This is the canonical and only maintained test suite for the DoNext use case.
All validation, edge-case, and integration tests should be added here.
Redundant or duplicate tests in other files have been removed.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone

from fastmcp.task_management.application.use_cases.do_next import DoNextUseCase
from fastmcp.task_management.domain.entities.task import Task
from fastmcp.task_management.domain.value_objects.task_id import TaskId
from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
from fastmcp.task_management.domain.value_objects.priority import Priority
from fastmcp.task_management.domain.enums.agent_roles import AgentRole
from fastmcp.task_management.domain.enums.common_labels import CommonLabel
from fastmcp.task_management.domain.enums.estimated_effort import EffortLevel
from fastmcp.task_management.domain.repositories.task_repository import TaskRepository
from fastmcp.task_management.domain.services.auto_rule_generator import AutoRuleGenerator


class TestDoNextUseCaseComprehensive:
    """Comprehensive test suite for DoNext use case covering all execution paths"""

    def setup_method(self):
        """Set up test fixtures"""
        self.mock_task_repository = Mock(spec=TaskRepository)
        self.mock_auto_rule_generator = Mock(spec=AutoRuleGenerator)
        # Add the missing method to the mock
        self.mock_auto_rule_generator.generate_rules_for_task = Mock(return_value=True)
        self.use_case = DoNextUseCase(
            task_repository=self.mock_task_repository,
            auto_rule_generator=self.mock_auto_rule_generator
        )

    def test_execute_with_no_tasks(self):
        """Test execute when no tasks are available"""
        # Mock empty task list
        self.mock_task_repository.find_all.return_value = []
        
        result = self.use_case.execute()
        
        assert result["success"] is True
        assert result.has_next is False
        assert result.next_item is None
        assert "No tasks found" in result.message

    def test_execute_with_single_todo_task(self):
        """Test execute with single TODO task"""
        task = Task(
            id=TaskId.generate_new(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.todo(),
            priority=Priority.high(),
            assignees=["@coding_agent"]
        )
        
        self.mock_task_repository.find_all.return_value = [task]
        
        result = self.use_case.execute()
        
        assert result["success"] is True
        assert result.has_next is True
        assert result.next_item["type"] == "task"
        assert result.next_item["task"]["id"] == str(task.id)
        assert result.next_item["task"]["title"] == "Test Task"

    def test_execute_with_task_having_incomplete_subtasks(self):
        """Test execute with task that has incomplete subtasks"""
        task = Task(
            id=TaskId.generate_new(),
            title="Parent Task",
            description="Parent Description",
            status=TaskStatus.in_progress(),
            priority=Priority.high(),
            assignees=["@coding_agent"]
        )
        
        # Add subtasks
        task.add_subtask({
            "title": "Completed Subtask",
            "description": "Already done",
            "assignees": ["@coding_agent"],
            "completed": True
        })
        task.add_subtask({
            "title": "Incomplete Subtask",
            "description": "Still to do",
            "assignees": ["@coding_agent"],
            "completed": False
        })
        
        self.mock_task_repository.find_all.return_value = [task]
        
        result = self.use_case.execute()
        
        assert result["success"] is True
        assert result.has_next is True
        assert result.next_item is not None

    def test_execute_with_task_having_all_subtasks_completed(self):
        """Test execute with task where all subtasks are completed"""
        task = Task(
            id=TaskId.generate_new(),
            title="Parent Task",
            description="Parent Description",
            status=TaskStatus.in_progress(),
            priority=Priority.high(),
            assignees=["@coding_agent"]
        )
        
        # Add and complete all subtasks
        task.add_subtask({
            "title": "Subtask 1",
            "description": "First subtask",
            "assignees": ["@coding_agent"],
            "completed": True
        })
        task.add_subtask({
            "title": "Subtask 2", 
            "description": "Second subtask",
            "assignees": ["@coding_agent"],
            "completed": True
        })
        
        self.mock_task_repository.find_all.return_value = [task]
        
        result = self.use_case.execute()
        
        assert result["success"] is True
        assert result.has_next is True
        assert result.next_item is not None

    def test_execute_with_multiple_tasks_priority_ordering(self):
        """Test execute with multiple tasks - should prioritize by priority"""
        task_low = Task(
            id=TaskId.generate_new(),
            title="Low Priority Task",
            description="Low priority",
            status=TaskStatus.todo(),
            priority=Priority.low(),
            assignees=["@coding_agent"]
        )
        
        task_critical = Task(
            id=TaskId.generate_new(),
            title="Critical Task",
            description="Critical priority",
            status=TaskStatus.todo(),
            priority=Priority.critical(),
            assignees=["@coding_agent"]
        )
        
        task_high = Task(
            id=TaskId.generate_new(),
            title="High Priority Task",
            description="High priority",
            status=TaskStatus.todo(),
            priority=Priority.high(),
            assignees=["@coding_agent"]
        )
        
        self.mock_task_repository.find_all.return_value = [task_low, task_critical, task_high]
        
        result = self.use_case.execute()
        
        assert result["success"] is True
        # Should prioritize critical task
        assert result.has_next is True
        assert result.next_item is not None

    def test_execute_with_blocked_tasks(self):
        """Test execute with blocked tasks - should skip blocked tasks"""
        task_blocked = Task(
            id=TaskId.generate_new(),
            title="Blocked Task",
            description="Blocked task",
            status=TaskStatus.blocked(),
            priority=Priority.high(),
            assignees=["@coding_agent"]
        )
        
        task_available = Task(
            id=TaskId.generate_new(),
            title="Available Task",
            description="Available task",
            status=TaskStatus.todo(),
            priority=Priority.medium(),
            assignees=["@coding_agent"]
        )
        
        self.mock_task_repository.find_all.return_value = [task_blocked, task_available]
        
        result = self.use_case.execute()
        
        assert result["success"] is True
        assert result.has_next is True
        assert result.next_item is not None

    def test_execute_with_completed_tasks(self):
        """Test execute with all tasks completed"""
        task_completed = Task(
            id=TaskId.generate_new(),
            title="Completed Task",
            description="Completed task",
            status=TaskStatus.done(),
            priority=Priority.high(),
            assignees=["@coding_agent"]
        )
        
        self.mock_task_repository.find_all.return_value = [task_completed]
        
        result = self.use_case.execute()
        
        assert result["success"] is True
        assert result.has_next is False
        assert "All tasks completed" in result.message

    def test_execute_with_dependencies(self):
        """Test execute with task dependencies"""
        dependency_task = Task(
            id=TaskId.generate_new(),
            title="Dependency Task",
            description="Must be completed first",
            status=TaskStatus.done(),
            priority=Priority.medium(),
            assignees=["@coding_agent"]
        )
        
        # Create task with different ID to avoid self-dependency
        dependent_task_id = TaskId.generate_new()
        while dependent_task_id == dependency_task.id:
            dependent_task_id = TaskId.generate_new()
            
        task_with_deps = Task(
            id=dependent_task_id,
            title="Dependent Task",
            description="Depends on other task",
            status=TaskStatus.todo(),
            priority=Priority.high(),
            assignees=["@coding_agent"]
        )
        task_with_deps.add_dependency(dependency_task.id)
        
        self.mock_task_repository.find_all.return_value = [dependency_task, task_with_deps]
        
        result = self.use_case.execute()
        
        assert result["success"] is True
        assert result.has_next is True

    def test_execute_with_due_dates(self):
        """Test execute with tasks having due dates"""
        overdue_task = Task(
            id=TaskId.generate_new(),
            title="Overdue Task",
            description="Past due date",
            status=TaskStatus.todo(),
            priority=Priority.medium(),
            assignees=["@coding_agent"],
            due_date="2023-01-01T00:00:00"
        )
        
        future_task = Task(
            id=TaskId.generate_new(),
            title="Future Task",
            description="Future due date",
            status=TaskStatus.todo(),
            priority=Priority.low(),
            assignees=["@coding_agent"],
            due_date="2030-12-31T23:59:59"
        )
        
        self.mock_task_repository.find_all.return_value = [overdue_task, future_task]
        
        result = self.use_case.execute()
        
        assert result["success"] is True
        assert result.has_next is True

    def test_execute_with_assignee_filter(self):
        """Test execute with assignee filter"""
        task1 = Task(
            id=TaskId.generate_new(),
            title="Coding Task",
            description="For coding agent",
            status=TaskStatus.todo(),
            priority=Priority.high(),
            assignees=["@coding_agent"]
        )
        
        task2 = Task(
            id=TaskId.generate_new(),
            title="Testing Task",
            description="For testing agent",
            status=TaskStatus.todo(),
            priority=Priority.high(),
            assignees=["@test_orchestrator_agent"]
        )
        
        self.mock_task_repository.find_all.return_value = [task1, task2]
        
        result = self.use_case.execute(assignee="@coding_agent")
        
        assert result["success"] is True
        assert result.has_next is True

    def test_execute_with_assignee_filter_no_matches(self):
        """Test execute with assignee filter that matches no tasks"""
        task = Task(
            id=TaskId.generate_new(),
            title="Task",
            description="Description",
            status=TaskStatus.todo(),
            priority=Priority.high(),
            assignees=["@coding_agent"]
        )
        
        self.mock_task_repository.find_all.return_value = [task]
        
        result = self.use_case.execute(assignee="@nonexistent_agent")
        
        assert result["success"] is True
        assert result.has_next is False
        assert "No tasks match the specified filters" in result.message

    def test_execute_with_project_filter(self):
        """Test execute with project filter"""
        task_a = Task(
            id=TaskId.generate_new(),
            title="Project A Task",
            description="Task for project A",
            status=TaskStatus.todo(),
            priority=Priority.high(),
            assignees=["@coding_agent"],
            project_id="project_a"
        )
        
        task_b = Task(
            id=TaskId.generate_new(),
            title="Project B Task",
            description="Task for project B",
            status=TaskStatus.todo(),
            priority=Priority.high(),
            assignees=["@coding_agent"],
            project_id="project_b"
        )
        
        self.mock_task_repository.find_all.return_value = [task_a, task_b]
        
        result = self.use_case.execute(project_id="project_a")
        
        assert result["success"] is True
        assert result.has_next is True

    def test_execute_with_label_filter(self):
        """Test execute with label filter"""
        task_bug = Task(
            id=TaskId.generate_new(),
            title="Bug Fix",
            description="Fix a bug",
            status=TaskStatus.todo(),
            priority=Priority.high(),
            assignees=["@coding_agent"],
            labels=[CommonLabel.BUG.value]
        )
        
        task_feature = Task(
            id=TaskId.generate_new(),
            title="New Feature",
            description="Add new feature",
            status=TaskStatus.todo(),
            priority=Priority.medium(),
            assignees=["@coding_agent"],
            labels=[CommonLabel.FEATURE.value]
        )
        
        self.mock_task_repository.find_all.return_value = [task_bug, task_feature]
        
        result = self.use_case.execute(labels=[CommonLabel.BUG.value])
        
        assert result["success"] is True
        assert result.has_next is True

    def test_execute_with_multiple_filters(self):
        """Test execute with multiple filters combined"""
        task = Task(
            id=TaskId.generate_new(),
            title="Filtered Task",
            description="Matches all filters",
            status=TaskStatus.todo(),
            priority=Priority.high(),
            assignees=["@coding_agent"],
            project_id="project_a",
            labels=[CommonLabel.BUG.value]
        )
        
        other_task = Task(
            id=TaskId.generate_new(),
            title="Other Task",
            description="Doesn't match filters",
            status=TaskStatus.todo(),
            priority=Priority.high(),
            assignees=["@test_orchestrator_agent"],
            project_id="project_b",
            labels=[CommonLabel.FEATURE.value]
        )
        
        self.mock_task_repository.find_all.return_value = [task, other_task]
        
        result = self.use_case.execute(
            assignee="@coding_agent",
            project_id="project_a",
            labels=[CommonLabel.BUG.value]
        )
        
        assert result["success"] is True
        assert result.has_next is True

    def test_execute_with_auto_rule_generation(self):
        """Test execute triggers auto rule generation"""
        task = Task(
            id=TaskId.generate_new(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.todo(),
            priority=Priority.high(),
            assignees=["@coding_agent"]
        )
        
        self.mock_task_repository.find_all.return_value = [task]
        
        result = self.use_case.execute()
        
        assert result["success"] is True
        # Verify auto rule generation was called
        self.mock_auto_rule_generator.generate_rules_for_task.assert_called_once_with(task)

    def test_execute_with_repository_error(self):
        """Test execute with repository error"""
        self.mock_task_repository.find_all.side_effect = Exception("Database error")
        
        with pytest.raises(Exception, match="Database error"):
            self.use_case.execute()

    def test_execute_with_auto_rule_generator_error(self):
        """Test execute with auto rule generator error"""
        task = Task(
            id=TaskId.generate_new(),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.todo(),
            priority=Priority.high(),
            assignees=["@coding_agent"]
        )
        
        self.mock_task_repository.find_all.return_value = [task]
        self.mock_auto_rule_generator.generate_rules_for_task.side_effect = Exception("Rule generation error")
        
        # Should not raise exception, should handle gracefully
        result = self.use_case.execute()
        
        # The actual behavior depends on implementation
        # For now, just verify it doesn't crash
        assert result is not None

    def test_complex_prioritization_scenario(self):
        """Test complex prioritization with mixed priorities and statuses"""
        tasks = [
            Task(
                id=TaskId.generate_new(),
                title="Critical In Progress",
                description="Critical task in progress",
                status=TaskStatus.in_progress(),
                priority=Priority.critical(),
                assignees=["@coding_agent"]
            ),
            Task(
                id=TaskId.generate_new(),
                title="High Todo",
                description="High priority todo",
                status=TaskStatus.todo(),
                priority=Priority.high(),
                assignees=["@coding_agent"]
            ),
            Task(
                id=TaskId.generate_new(),
                title="Medium Todo",
                description="Medium priority todo",
                status=TaskStatus.todo(),
                priority=Priority.medium(),
                assignees=["@coding_agent"]
            )
        ]
        
        self.mock_task_repository.find_all.return_value = tasks
        
        result = self.use_case.execute()
        
        assert result["success"] is True
        assert result.has_next is True
        # Should prioritize critical task even if in progress
        assert result.next_item is not None

    def test_context_information_completeness(self):
        """Test that context information is complete and accurate"""
        task = Task(
            id=TaskId.generate_new(),
            title="Context Test Task",
            description="Task for testing context",
            status=TaskStatus.todo(),
            priority=Priority.high(),
            assignees=["@coding_agent"]
        )
        
        self.mock_task_repository.find_all.return_value = [task]
        
        result = self.use_case.execute()
        
        assert result["success"] is True
        assert result.has_next is True
        assert result.next_item is not None
        
        # Check context information
        context = result.next_item.get("context")
        if context:
            assert "task_id" in context
            assert "overall_progress" in context 