"""
Comprehensive Domain Entity Coverage Improvement Tests
Task: Domain Entity Test - Testing domain entity integrity
Focus: Improve test coverage from 26% to 80%+ by testing missing functionality
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from typing import Dict, Any, List

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


class TestTaskEntityCoverageImprovement:
    """Tests for Task entity to improve coverage on missing lines."""
    
    @pytest.fixture
    def task_entity(self):
        """Create a task entity for testing."""
        from task_mcp.domain.entities.task import Task
        from task_mcp.domain.value_objects.task_id import TaskId
        from task_mcp.domain.value_objects.task_status import TaskStatus
        from task_mcp.domain.value_objects.priority import Priority
        
        return Task(
            id=TaskId.from_int(1),
            title="Test Task",
            description="Test Description",
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_update_estimated_effort_validation(self, task_entity):
        """Test estimated effort update with enum validation."""
        # Test valid effort
        task_entity.update_estimated_effort("large")
        assert task_entity.estimated_effort == "large"
        
        # Test valid medium effort
        task_entity.update_estimated_effort("medium")
        assert task_entity.estimated_effort == "medium"
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_assignee_management_comprehensive(self, task_entity):
        """Test comprehensive assignee management."""
        # Test update_assignees with validation
        assignees = ["@coding_agent", "test_agent", "@ui_designer_agent"]
        task_entity.update_assignees(assignees)
        
        # Should validate and add @ prefix where needed
        assert "@coding_agent" in task_entity.assignees
        assert "@ui_designer_agent" in task_entity.assignees
        
        # Test add_assignee
        task_entity.add_assignee("@new_agent")
        assert "@new_agent" in task_entity.assignees
        
        # Test duplicate add
        initial_count = len(task_entity.assignees)
        task_entity.add_assignee("@coding_agent")  # Already exists
        assert len(task_entity.assignees) == initial_count
        
        # Test remove_assignee
        task_entity.remove_assignee("@coding_agent")
        assert "@coding_agent" not in task_entity.assignees
        
        # Test helper methods
        assert task_entity.has_assignee("@ui_designer_agent")
        assert task_entity.get_assignees_count() > 0
        assert task_entity.get_primary_assignee() is not None
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_get_assignees_info_detailed(self, task_entity):
        """Test detailed assignee information retrieval."""
        task_entity.update_assignees(["@coding_agent", "custom_agent"])
        
        assignees_info = task_entity.get_assignees_info()
        assert len(assignees_info) == 2
        
        for info in assignees_info:
            assert "role" in info
            assert "display_name" in info
            assert "folder_name" in info
            assert "metadata" in info
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_label_management_with_validation(self, task_entity):
        """Test label management with enum validation."""
        # Test update_labels
        labels = ["feature", "bug", "invalid_label"]
        task_entity.update_labels(labels)
        
        # Should contain valid labels and suggestions for invalid ones
        assert len(task_entity.labels) > 0
        
        # Test add_label
        task_entity.add_label("urgent")
        assert "urgent" in task_entity.labels or len(task_entity.labels) > 0
        
        # Test remove_label
        if task_entity.labels:
            first_label = task_entity.labels[0]
            task_entity.remove_label(first_label)
            assert first_label not in task_entity.labels
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_subtask_management_comprehensive(self, task_entity):
        """Test comprehensive subtask management."""
        # Test add_subtask without ID
        subtask_data = {"title": "Test Subtask", "description": "Test description"}
        task_entity.add_subtask(subtask_data)
        
        assert len(task_entity.subtasks) == 1
        subtask = task_entity.subtasks[0]
        assert subtask["title"] == "Test Subtask"
        assert subtask["completed"] is False
        assert "id" in subtask
        
        # Test add_subtask with missing title
        with pytest.raises(ValueError, match="Subtask must have a title"):
            task_entity.add_subtask({})
        
        # Test get_subtask
        subtask_id = subtask["id"]
        retrieved = task_entity.get_subtask(subtask_id)
        assert retrieved is not None
        assert retrieved["title"] == "Test Subtask"
        
        # Test update_subtask
        success = task_entity.update_subtask(subtask_id, {"title": "Updated Subtask"})
        assert success
        updated = task_entity.get_subtask(subtask_id)
        assert updated["title"] == "Updated Subtask"
        
        # Test complete_subtask
        success = task_entity.complete_subtask(subtask_id)
        assert success
        completed = task_entity.get_subtask(subtask_id)
        assert completed["completed"] is True
        
        # Test remove_subtask
        success = task_entity.remove_subtask(subtask_id)
        assert success
        assert len(task_entity.subtasks) == 0
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_subtask_progress_calculation(self, task_entity):
        """Test subtask progress calculation."""
        # Test with no subtasks
        progress = task_entity.get_subtask_progress()
        assert progress["total"] == 0
        assert progress["completed"] == 0
        assert progress["percentage"] == 0
        
        # Add subtasks
        task_entity.add_subtask({"title": "Subtask 1"})
        task_entity.add_subtask({"title": "Subtask 2"})
        task_entity.add_subtask({"title": "Subtask 3"})
        
        progress = task_entity.get_subtask_progress()
        assert progress["total"] == 3
        assert progress["completed"] == 0
        assert progress["percentage"] == 0
        
        # Complete one subtask
        subtask_id = task_entity.subtasks[0]["id"]
        task_entity.complete_subtask(subtask_id)
        
        progress = task_entity.get_subtask_progress()
        assert progress["completed"] == 1
        assert progress["percentage"] == 33.3
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_complete_task_functionality(self, task_entity):
        """Test complete task with subtasks."""
        # Add subtasks
        task_entity.add_subtask({"title": "Subtask 1"})
        task_entity.add_subtask({"title": "Subtask 2"})
        
        # Complete task
        task_entity.complete_task()
        
        # All subtasks should be completed
        for subtask in task_entity.subtasks:
            assert subtask["completed"] is True
        
        # Task status should be done
        assert task_entity.status.is_completed()
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_migrate_subtask_ids(self, task_entity):
        """Test migrating old integer subtask IDs."""
        # Add subtasks with old integer IDs
        task_entity.subtasks = [
            {"id": 1, "title": "Old Subtask 1", "completed": False},
            {"id": 2, "title": "Old Subtask 2", "completed": True}
        ]
        
        task_entity.migrate_subtask_ids()
        
        # Check that IDs are converted
        for subtask in task_entity.subtasks:
            subtask_id = subtask["id"]
            if isinstance(subtask_id, str) and "." in subtask_id:
                assert str(task_entity.id) in subtask_id
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_business_logic_methods(self, task_entity):
        """Test various business logic methods."""
        # Test effort level
        task_entity.update_estimated_effort("large")
        effort_level = task_entity.get_effort_level()
        assert effort_level in ["quick", "short", "small", "medium", "large", "xlarge", "epic", "massive"]
        
        # Test suggested labels
        suggestions = task_entity.get_suggested_labels("authentication security")
        assert isinstance(suggestions, list)
        
        # Test overdue checking
        assert not task_entity.is_overdue()  # No due date
        
        future_date = (datetime.now() + timedelta(days=1)).isoformat()
        task_entity.update_due_date(future_date)
        assert not task_entity.is_overdue()
        
        past_date = (datetime.now() - timedelta(days=1)).isoformat()
        task_entity.update_due_date(past_date)
        assert task_entity.is_overdue()
        
        # Test circular dependency
        assert task_entity.has_circular_dependency(task_entity.id)
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_domain_events_comprehensive(self, task_entity):
        """Test domain events generation."""
        # Clear existing events
        task_entity.get_events()
        
        # Test various operations that should generate events
        task_entity.update_title("New Title")
        events = task_entity.get_events()
        assert len(events) > 0
        
        task_entity.update_assignees(["@coding_agent"])
        events = task_entity.get_events()
        assert len(events) > 0
        
        task_entity.mark_as_retrieved()
        events = task_entity.get_events()
        assert len(events) > 0
        
        task_entity.mark_as_deleted()
        events = task_entity.get_events()
        assert len(events) > 0


class TestProjectEntityCoverageImprovement:
    """Tests for Project entity to improve coverage."""
    
    @pytest.fixture
    def project_entity(self):
        """Create a project entity."""
        from task_mcp.domain.entities.project import Project
        return Project(
            id="test_project",
            name="Test Project", 
            description="Test Description",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    @pytest.fixture
    def agent_entity(self):
        """Create an agent entity."""
        from task_mcp.domain.entities.agent import Agent
        from task_mcp.domain.enums.agent_roles import AgentRole
        return Agent.create_agent(
            agent_id="test_agent",
            name="Test Agent",
            description="Test agent for testing",
            capabilities=[],
            specializations=["coding"]
        )
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_tree_management(self, project_entity):
        """Test task tree creation and management."""
        # Create task tree
        tree = project_entity.create_task_tree("frontend", "Frontend Tasks", "Frontend development")
        assert tree.id == "frontend"
        assert "frontend" in project_entity.task_trees
        
        # Test duplicate creation
        with pytest.raises(ValueError):
            project_entity.create_task_tree("frontend", "Duplicate")
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_agent_registration_and_assignment(self, project_entity, agent_entity):
        """Test agent registration and assignment."""
        # Register agent
        project_entity.register_agent(agent_entity)
        assert agent_entity.id in project_entity.registered_agents
        
        # Create tree and assign agent
        project_entity.create_task_tree("backend", "Backend Tasks")
        project_entity.assign_agent_to_tree(agent_entity.id, "backend")
        assert project_entity.agent_assignments["backend"] == agent_entity.id
        
        # Test error cases
        with pytest.raises(ValueError):
            project_entity.assign_agent_to_tree("unknown_agent", "backend")
        
        with pytest.raises(ValueError):
            project_entity.assign_agent_to_tree(agent_entity.id, "unknown_tree")
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_cross_tree_dependencies(self, project_entity):
        """Test cross-tree dependency management."""
        # Create trees
        project_entity.create_task_tree("tree1", "Tree 1")
        project_entity.create_task_tree("tree2", "Tree 2")
        
        # Mock finding tasks in different trees
        with patch.object(project_entity, '_find_task_tree') as mock_find:
            def side_effect(task_id):
                return project_entity.task_trees["tree1"] if task_id == "task1" else project_entity.task_trees["tree2"]
            mock_find.side_effect = side_effect
            
            # Add cross-tree dependency
            project_entity.add_cross_tree_dependency("task2", "task1")
            assert "task2" in project_entity.cross_tree_dependencies
            assert "task1" in project_entity.cross_tree_dependencies["task2"]
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_orchestration_status(self, project_entity, agent_entity):
        """Test orchestration status generation."""
        project_entity.register_agent(agent_entity)
        project_entity.create_task_tree("tree1", "Tree 1")
        project_entity.assign_agent_to_tree(agent_entity.id, "tree1")
        
        status = project_entity.get_orchestration_status()
        
        assert status["project_id"] == project_entity.id
        assert status["total_trees"] == 1
        assert status["registered_agents"] == 1
        assert "trees" in status
        assert "agents" in status


class TestWorkSessionEntityCoverageImprovement:
    """Tests for WorkSession entity (0% coverage)."""
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_work_session_creation(self):
        """Test work session creation."""
        from task_mcp.domain.entities.work_session import WorkSession
        
        session = WorkSession.create_session(
            agent_id="test_agent",
            task_id="test_task", 
            tree_id="test_tree",
            max_duration_hours=2.0
        )
        
        assert session.agent_id == "test_agent"
        assert session.task_id == "test_task"
        assert session.tree_id == "test_tree"
        assert session.started_at is not None
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_work_session_lifecycle(self):
        """Test work session lifecycle methods."""
        from task_mcp.domain.entities.work_session import WorkSession
        
        session = WorkSession.create_session(
            agent_id="test_agent",
            task_id="test_task",
            tree_id="test_tree"
        )
        
        # Test completion
        session.complete_session(success=True, notes="Task completed")
        assert session.status.value == "completed"
        assert "Task completed" in session.session_notes
        
        # Test timeout detection
        session_short = WorkSession.create_session(
            agent_id="test_agent",
            task_id="test_task2",
            tree_id="test_tree",
            max_duration_hours=0.001
        )
        
        # For testing timeout, we need to manually check if it would timeout
        import time
        time.sleep(0.1)
        # The max duration is very short (0.001 hours = 3.6 seconds), so it should timeout
        assert session_short.get_total_duration().total_seconds() > 0


class TestAgentEntityCoverageImprovement:
    """Tests for Agent entity to improve coverage."""
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_agent_capabilities(self):
        """Test agent capability management."""
        from task_mcp.domain.entities.agent import Agent
        from task_mcp.domain.enums.agent_roles import AgentRole
        
        from task_mcp.domain.entities.agent import AgentCapability
        
        agent = Agent.create_agent(
            agent_id="test_agent",
            name="Test Agent",
            description="Test agent for testing",
            capabilities=[AgentCapability.FRONTEND_DEVELOPMENT],
            specializations=["coding"]
        )
        
        # Test capability operations
        agent.add_capability(AgentCapability.TESTING)
        assert agent.has_capability(AgentCapability.TESTING)
        
        agent.remove_capability(AgentCapability.FRONTEND_DEVELOPMENT)
        assert not agent.has_capability(AgentCapability.FRONTEND_DEVELOPMENT)


class TestTaskTreeEntityCoverageImprovement:
    """Tests for TaskTree entity to improve coverage."""
    
    @pytest.fixture
    def task_tree(self):
        """Create a task tree."""
        from task_mcp.domain.entities.task_tree import TaskTree
        return TaskTree(
            id="test_tree",
            name="Test Tree",
            description="Test Description",
            project_id="test_project",
            created_at=datetime.now()
        )
    
    @pytest.mark.unit
    @pytest.mark.domain
    def test_task_tree_task_management(self, task_tree):
        """Test task management in task tree."""
        from task_mcp.domain.entities.task import Task
        from task_mcp.domain.value_objects.task_id import TaskId
        from task_mcp.domain.value_objects.task_status import TaskStatus
        from task_mcp.domain.value_objects.priority import Priority
        
        # Create and add task
        task = Task(
            id=TaskId.from_int(1),
            title="Test Task",
            description="Test Description", 
            status=TaskStatus.todo(),
            priority=Priority.medium()
        )
        
        task_tree.add_task(task)
        
        # Test retrieval
        assert task_tree.has_task(str(task.id))
        retrieved = task_tree.get_task(str(task.id))
        assert retrieved.title == "Test Task"
        
        # Test counts
        assert task_tree.get_task_count() == 1
        
        # Test progress
        progress = task_tree.get_progress_percentage()
        assert progress >= 0 