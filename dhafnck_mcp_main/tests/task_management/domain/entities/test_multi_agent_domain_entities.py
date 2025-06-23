#!/usr/bin/env python3
"""
Comprehensive tests for Multi-Agent Domain Entities
Tests Project, Agent, TaskTree, WorkSession entities
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from fastmcp.task_management.domain.entities.project import Project
from fastmcp.task_management.domain.entities.agent import Agent, AgentCapability, AgentStatus
from fastmcp.task_management.domain.entities.task_tree import TaskTree
from fastmcp.task_management.domain.entities.work_session import WorkSession, SessionStatus
from fastmcp.task_management.domain.entities.task import Task
from fastmcp.task_management.domain.value_objects.task_id import TaskId
from fastmcp.task_management.domain.value_objects.task_status import TaskStatus, TaskStatusEnum
from fastmcp.task_management.domain.value_objects.priority import Priority, PriorityLevel


class TestProjectEntity:
    """Test Project domain entity"""
    
    @pytest.fixture
    def sample_project(self):
        """Create a sample project for testing"""
        return Project(
            id="test_project",
            name="Test Project",
            description="A test project for multi-agent orchestration",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    @pytest.fixture
    def sample_agent(self):
        """Create a sample agent for testing"""
        return Agent.create_agent(
            agent_id="test_agent",
            name="Test Agent",
            description="Test agent for testing",
            capabilities=[AgentCapability.FRONTEND_DEVELOPMENT],
            specializations=["React"],
            preferred_languages=["javascript"]
        )
    
    def test_project_creation(self, sample_project):
        """Test project creation with basic properties"""
        assert sample_project.id == "test_project"
        assert sample_project.name == "Test Project"
        assert sample_project.description == "A test project for multi-agent orchestration"
        assert isinstance(sample_project.created_at, datetime)
        assert isinstance(sample_project.updated_at, datetime)
        
        # Test default collections are empty
        assert len(sample_project.task_trees) == 0
        assert len(sample_project.registered_agents) == 0
        assert len(sample_project.agent_assignments) == 0
        assert len(sample_project.cross_tree_dependencies) == 0
        assert len(sample_project.active_work_sessions) == 0
        assert len(sample_project.resource_locks) == 0
    
    def test_create_task_tree_success(self, sample_project):
        """Test successful task tree creation"""
        tree_id = "frontend_tree"
        name = "Frontend Development"
        description = "React frontend development"
        
        task_tree = sample_project.create_task_tree(tree_id, name, description)
        
        assert task_tree.id == tree_id
        assert task_tree.name == name
        assert task_tree.description == description
        assert task_tree.project_id == sample_project.id
        assert tree_id in sample_project.task_trees
        assert sample_project.task_trees[tree_id] == task_tree
    
    def test_create_task_tree_duplicate_fails(self, sample_project):
        """Test that creating duplicate task tree fails"""
        tree_id = "duplicate_tree"
        
        # Create first tree
        sample_project.create_task_tree(tree_id, "First Tree", "First description")
        
        # Try to create duplicate
        with pytest.raises(ValueError, match=f"Task tree {tree_id} already exists"):
            sample_project.create_task_tree(tree_id, "Duplicate Tree", "Duplicate description")
    
    def test_register_agent_success(self, sample_project, sample_agent):
        """Test successful agent registration"""
        agent_id = sample_agent.id
        
        sample_project.register_agent(sample_agent)
        
        assert agent_id in sample_project.registered_agents
        assert sample_project.registered_agents[agent_id] == sample_agent
    
    def test_assign_agent_to_tree_success(self, sample_project, sample_agent):
        """Test successful agent assignment to task tree"""
        tree_id = "test_tree"
        agent_id = sample_agent.id
        
        # Setup: register agent and create tree
        sample_project.register_agent(sample_agent)
        sample_project.create_task_tree(tree_id, "Test Tree", "Test description")
        
        # Assign agent to tree
        sample_project.assign_agent_to_tree(agent_id, tree_id)
        
        assert tree_id in sample_project.agent_assignments
        assert sample_project.agent_assignments[tree_id] == agent_id
    
    def test_assign_agent_to_tree_agent_not_registered(self, sample_project):
        """Test assigning non-registered agent fails"""
        tree_id = "test_tree"
        agent_id = "non_registered_agent"
        
        # Create tree but don't register agent
        sample_project.create_task_tree(tree_id, "Test Tree", "Test description")
        
        with pytest.raises(ValueError, match=f"Agent {agent_id} not registered"):
            sample_project.assign_agent_to_tree(agent_id, tree_id)
    
    def test_assign_agent_to_tree_tree_not_found(self, sample_project, sample_agent):
        """Test assigning agent to non-existent tree fails"""
        tree_id = "non_existent_tree"
        agent_id = sample_agent.id
        
        # Register agent but don't create tree
        sample_project.register_agent(sample_agent)
        
        with pytest.raises(ValueError, match=f"Task tree {tree_id} not found"):
            sample_project.assign_agent_to_tree(agent_id, tree_id)
    
    def test_assign_agent_to_tree_already_assigned_different_agent(self, sample_project):
        """Test reassigning tree to different agent fails"""
        tree_id = "test_tree"
        
        # Create two agents
        agent1 = Agent.create_agent("agent1", "Agent 1", "First agent", [AgentCapability.FRONTEND_DEVELOPMENT])
        agent2 = Agent.create_agent("agent2", "Agent 2", "Second agent", [AgentCapability.BACKEND_DEVELOPMENT])
        
        # Register both agents and create tree
        sample_project.register_agent(agent1)
        sample_project.register_agent(agent2)
        sample_project.create_task_tree(tree_id, "Test Tree", "Test description")
        
        # Assign first agent
        sample_project.assign_agent_to_tree("agent1", tree_id)
        
        # Try to assign second agent to same tree
        with pytest.raises(ValueError, match=f"Task tree {tree_id} already assigned to agent agent1"):
            sample_project.assign_agent_to_tree("agent2", tree_id)
    
    def test_add_cross_tree_dependency_success(self, sample_project):
        """Test adding cross-tree dependency"""
        # Create two trees
        sample_project.create_task_tree("frontend_tree", "Frontend", "Frontend development")
        sample_project.create_task_tree("backend_tree", "Backend", "Backend development")
        
        # Mock tasks in different trees
        with patch.object(sample_project, '_find_task_tree') as mock_find:
            frontend_tree = sample_project.task_trees["frontend_tree"]
            backend_tree = sample_project.task_trees["backend_tree"]
            
            # Mock finding tasks in different trees
            def mock_find_task(task_id):
                if task_id == "frontend_task":
                    return frontend_tree
                elif task_id == "backend_task":
                    return backend_tree
                return None
            
            mock_find.side_effect = mock_find_task
            
            # Add cross-tree dependency
            sample_project.add_cross_tree_dependency("frontend_task", "backend_task")
            
            assert "frontend_task" in sample_project.cross_tree_dependencies
            assert "backend_task" in sample_project.cross_tree_dependencies["frontend_task"]
    
    def test_add_cross_tree_dependency_same_tree_fails(self, sample_project):
        """Test adding dependency within same tree fails"""
        # Create one tree
        sample_project.create_task_tree("frontend_tree", "Frontend", "Frontend development")
        
        # Mock tasks in same tree
        with patch.object(sample_project, '_find_task_tree') as mock_find:
            frontend_tree = sample_project.task_trees["frontend_tree"]
            mock_find.return_value = frontend_tree
            
            with pytest.raises(ValueError, match="Use regular task dependencies for tasks within the same tree"):
                sample_project.add_cross_tree_dependency("task1", "task2")
    
    def test_get_orchestration_status(self, sample_project, sample_agent):
        """Test getting orchestration status"""
        # Setup project with agent, tree, and assignment
        tree_id = "test_tree"
        agent_id = sample_agent.id
        
        sample_project.register_agent(sample_agent)
        task_tree = sample_project.create_task_tree(tree_id, "Test Tree", "Test description")
        sample_project.assign_agent_to_tree(agent_id, tree_id)
        
        # Mock task tree methods
        with patch.object(task_tree, 'get_task_count', return_value=5), \
             patch.object(task_tree, 'get_completed_task_count', return_value=2), \
             patch.object(task_tree, 'get_progress_percentage', return_value=40.0):
            
            status = sample_project.get_orchestration_status()
            
            assert status["project_id"] == sample_project.id
            assert status["project_name"] == sample_project.name
            assert status["total_trees"] == 1
            assert status["registered_agents"] == 1
            assert status["active_assignments"] == 1
            assert status["active_sessions"] == 0
            assert status["cross_tree_dependencies"] == 0
            assert status["resource_locks"] == 0
            
            # Check tree details
            assert tree_id in status["trees"]
            tree_status = status["trees"][tree_id]
            assert tree_status["name"] == "Test Tree"
            assert tree_status["assigned_agent"] == agent_id
            assert tree_status["total_tasks"] == 5
            assert tree_status["completed_tasks"] == 2
            assert tree_status["progress"] == 40.0
            
            # Check agent details
            assert agent_id in status["agents"]
            agent_status = status["agents"][agent_id]
            assert agent_status["name"] == sample_agent.name
            assert tree_id in agent_status["assigned_trees"]


class TestAgentEntity:
    """Test Agent domain entity"""
    
    def test_agent_creation_with_create_agent(self):
        """Test agent creation using create_agent factory method"""
        agent_id = "test_agent"
        name = "Test Agent"
        description = "A test agent"
        capabilities = [AgentCapability.FRONTEND_DEVELOPMENT, AgentCapability.CODE_REVIEW]
        specializations = ["React", "TypeScript"]
        preferred_languages = ["javascript", "typescript"]
        
        agent = Agent.create_agent(
            agent_id=agent_id,
            name=name,
            description=description,
            capabilities=capabilities,
            specializations=specializations,
            preferred_languages=preferred_languages
        )
        
        assert agent.id == agent_id
        assert agent.name == name
        assert agent.description == description
        assert agent.capabilities == set(capabilities)
        assert agent.specializations == specializations
        assert agent.preferred_languages == preferred_languages
        assert agent.status == AgentStatus.AVAILABLE
        assert agent.max_concurrent_tasks == 1  # Default value
        assert len(agent.assigned_trees) == 0
        assert len(agent.active_tasks) == 0
    
    def test_agent_get_agent_profile(self):
        """Test getting agent profile"""
        agent = Agent.create_agent(
            agent_id="profile_agent",
            name="Profile Agent",
            description="Agent for profile testing",
            capabilities=[AgentCapability.BACKEND_DEVELOPMENT],
            specializations=["Node.js"],
            preferred_languages=["javascript"]
        )
        
        profile = agent.get_agent_profile()
        
        assert profile["id"] == "profile_agent"
        assert profile["name"] == "Profile Agent"
        assert profile["description"] == "Agent for profile testing"
        assert profile["status"] == AgentStatus.AVAILABLE.value
        assert profile["capabilities"] == [AgentCapability.BACKEND_DEVELOPMENT.value]
        assert profile["specializations"] == ["Node.js"]
        assert profile["preferred_languages"] == ["javascript"]
        assert isinstance(profile["workload"]["percentage"], (int, float))
    
    def test_agent_get_workload_percentage(self):
        """Test getting agent workload percentage"""
        agent = Agent.create_agent(
            agent_id="workload_agent",
            name="Workload Agent",
            description="Agent for workload testing",
            capabilities=[AgentCapability.FRONTEND_DEVELOPMENT]
        )
        
        # Initially no workload
        assert agent.get_workload_percentage() == 0.0
        
        # Add some active tasks and set current workload
        agent.active_tasks.add("task1")
        agent.active_tasks.add("task2")
        agent.current_workload = 2  # Set current workload to match active tasks
        agent.max_concurrent_tasks = 4
        
        # Should be 50% (2 out of 4)
        assert agent.get_workload_percentage() == 50.0


class TestTaskTreeEntity:
    """Test TaskTree domain entity"""
    
    @pytest.fixture
    def sample_task_tree(self):
        """Create a sample task tree for testing"""
        return TaskTree(
            id="test_tree",
            name="Test Tree",
            description="A test task tree",
            project_id="test_project",
            created_at=datetime.now()
        )
    
    def test_task_tree_creation(self, sample_task_tree):
        """Test task tree creation with basic properties"""
        assert sample_task_tree.id == "test_tree"
        assert sample_task_tree.name == "Test Tree"
        assert sample_task_tree.description == "A test task tree"
        assert sample_task_tree.project_id == "test_project"
        assert isinstance(sample_task_tree.created_at, datetime)
        assert sample_task_tree.assigned_agent_id is None
        assert sample_task_tree.status == "active"  # Default status
        assert len(sample_task_tree.all_tasks) == 0
    
    def test_task_tree_get_tree_status(self, sample_task_tree):
        """Test getting task tree status"""
        # Mock the methods that would be called
        with patch.object(sample_task_tree, 'get_task_count', return_value=10), \
             patch.object(sample_task_tree, 'get_completed_task_count', return_value=4), \
             patch.object(sample_task_tree, 'get_progress_percentage', return_value=40.0), \
             patch.object(sample_task_tree, 'get_available_tasks', return_value=[]):
            
            status = sample_task_tree.get_tree_status()
            
            assert status["tree_id"] == "test_tree"
            assert status["tree_name"] == "Test Tree"
            assert status["assigned_agent"] is None
            assert status["total_tasks"] == 10
            assert status["completed_tasks"] == 4
            assert status["progress_percentage"] == 40.0
            assert status["available_tasks"] == 0
    
    def test_task_tree_has_task(self, sample_task_tree):
        """Test checking if task tree has a specific task"""
        # Mock all_tasks
        sample_task_tree.all_tasks = {"task1": Mock(), "task2": Mock()}
        
        assert sample_task_tree.has_task("task1") is True
        assert sample_task_tree.has_task("task2") is True
        assert sample_task_tree.has_task("task3") is False
    
    def test_task_tree_get_task(self, sample_task_tree):
        """Test getting a specific task from tree"""
        mock_task = Mock()
        sample_task_tree.all_tasks = {"task1": mock_task}
        
        assert sample_task_tree.get_task("task1") == mock_task
        assert sample_task_tree.get_task("non_existent") is None


class TestWorkSessionEntity:
    """Test WorkSession domain entity"""
    
    @pytest.fixture
    def sample_work_session(self):
        """Create a sample work session for testing"""
        return WorkSession(
            id="session_1",
            agent_id="test_agent",
            task_id="test_task",
            tree_id="test_tree",
            started_at=datetime.now()
        )
    
    def test_work_session_creation(self, sample_work_session):
        """Test work session creation with basic properties"""
        assert sample_work_session.id == "session_1"
        assert sample_work_session.agent_id == "test_agent"
        assert sample_work_session.task_id == "test_task"
        assert sample_work_session.tree_id == "test_tree"
        assert isinstance(sample_work_session.started_at, datetime)
        assert sample_work_session.ended_at is None
        assert sample_work_session.max_duration is None
        assert sample_work_session.status == SessionStatus.ACTIVE  # Compare with enum
    
    def test_work_session_get_session_summary(self, sample_work_session):
        """Test getting work session summary"""
        summary = sample_work_session.get_session_summary()
        
        assert summary["session_id"] == "session_1"
        assert summary["agent_id"] == "test_agent"
        assert summary["task_id"] == "test_task"
        assert summary["tree_id"] == "test_tree"
        assert summary["status"] == SessionStatus.ACTIVE.value
        assert "timing" in summary
        assert summary["timing"]["started_at"] is not None
    
    def test_work_session_is_active(self, sample_work_session):
        """Test checking if work session is active"""
        assert sample_work_session.is_active() is True
        
        # End the session
        sample_work_session.ended_at = datetime.now()
        sample_work_session.status = "completed"
        
        assert sample_work_session.is_active() is False
    
    def test_work_session_is_expired(self, sample_work_session):
        """Test checking if work session is expired"""
        # No max duration set
        assert sample_work_session.is_timeout_due() is False
        
        # Set max duration to 1 hour
        sample_work_session.max_duration = timedelta(hours=1)
        
        # Session just started, not expired
        assert sample_work_session.is_timeout_due() is False
        
        # Mock started_at to be 2 hours ago
        sample_work_session.started_at = datetime.now() - timedelta(hours=2)
        
        # Should be expired now
        assert sample_work_session.is_timeout_due() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 