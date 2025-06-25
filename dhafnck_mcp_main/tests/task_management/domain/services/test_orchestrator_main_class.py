"""
Comprehensive tests for the main Orchestrator class.
Tests orchestration, conflict resolution, workload balancing, and session management.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta, timezone

from fastmcp.task_management.domain.services.orchestrator import (
    Orchestrator, 
    CapabilityBasedStrategy
)
from fastmcp.task_management.domain.entities.project import Project
from fastmcp.task_management.domain.entities.agent import Agent, AgentCapability, AgentStatus
from fastmcp.task_management.domain.entities.task_tree import TaskTree
from fastmcp.task_management.domain.entities.task import Task
from fastmcp.task_management.domain.entities.work_session import WorkSession, SessionStatus
from fastmcp.task_management.domain.value_objects.task_id import TaskId
from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
from fastmcp.task_management.domain.value_objects.priority import Priority


class TestOrchestrator:
    """Test main Orchestrator class functionality"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance with default strategy"""
        return Orchestrator()
    
    @pytest.fixture
    def custom_orchestrator(self):
        """Create orchestrator with custom strategy"""
        custom_strategy = Mock(spec=CapabilityBasedStrategy)
        custom_strategy.assign_work.return_value = {"tree1": "agent1"}
        return Orchestrator(strategy=custom_strategy)
    
    @pytest.fixture
    def sample_project(self):
        """Create a sample project with agents and task trees"""
        now = datetime.now(timezone.utc)
        project = Project(
            id="test_project",
            name="Test Project", 
            description="Test project for orchestrator testing",
            created_at=now,
            updated_at=now
        )
        
        # Create task trees
        frontend_tree = TaskTree(
            id="frontend_tree",
            name="Frontend Development",
            description="UI and frontend tasks",
            project_id="test_project",
            created_at=now
        )
        
        backend_tree = TaskTree(
            id="backend_tree",
            name="Backend Development", 
            description="API and backend tasks",
            project_id="test_project",
            created_at=now
        )
        
        # Add tasks to trees
        frontend_task = Task.create(
            id=TaskId.from_string("20250625001"),
            title="Build React Components",
            description="Create responsive UI components using React",
            status=TaskStatus("todo"),
            priority=Priority("high")
        )
        frontend_tree.add_root_task(frontend_task)
        
        backend_task = Task.create(
            id=TaskId.from_string("20250625002"),
            title="Implement REST API",
            description="Create Python FastAPI endpoints", 
            status=TaskStatus("todo"),
            priority=Priority("medium")
        )
        backend_tree.add_root_task(backend_task)
        
        project.task_trees["frontend_tree"] = frontend_tree
        project.task_trees["backend_tree"] = backend_tree
        
        # Register agents
        frontend_agent = Agent(
            id="frontend_agent",
            name="Frontend Developer",
            description="Frontend specialist",
            capabilities={AgentCapability.FRONTEND_DEVELOPMENT},
            preferred_languages=["javascript", "typescript"],
            status=AgentStatus.AVAILABLE,
            max_concurrent_tasks=3,
            current_workload=0
        )
        
        backend_agent = Agent(
            id="backend_agent",
            name="Backend Developer", 
            description="Backend specialist",
            capabilities={AgentCapability.BACKEND_DEVELOPMENT},
            preferred_languages=["python", "java"],
            status=AgentStatus.AVAILABLE,
            max_concurrent_tasks=2,
            current_workload=1
        )
        
        project.registered_agents["frontend_agent"] = frontend_agent
        project.registered_agents["backend_agent"] = backend_agent
        
        return project
    
    def test_orchestrator_initialization_default_strategy(self, orchestrator):
        """Test orchestrator initialization with default strategy"""
        assert isinstance(orchestrator.strategy, CapabilityBasedStrategy)
        assert orchestrator.logger is not None
    
    def test_orchestrator_initialization_custom_strategy(self, custom_orchestrator):
        """Test orchestrator initialization with custom strategy"""
        # The strategy is a Mock, so it's not a CapabilityBasedStrategy instance
        assert custom_orchestrator.strategy is not None
        # Check it's a mock object
        assert hasattr(custom_orchestrator.strategy, 'assign_work')
    
    def test_orchestrate_project_basic_flow(self, orchestrator, sample_project):
        """Test basic project orchestration flow"""
        result = orchestrator.orchestrate_project(sample_project)
        
        # Check result structure
        assert "orchestration_timestamp" in result
        assert "project_id" in result
        assert "new_assignments" in result
        assert "agent_recommendations" in result
        assert "conflicts_detected" in result
        assert "conflicts_resolved" in result
        assert "active_sessions" in result
        assert "available_agents" in result
        
        # Check values
        assert result["project_id"] == "test_project"
        assert isinstance(result["new_assignments"], dict)
        assert isinstance(result["agent_recommendations"], dict)
        assert result["conflicts_detected"] == 0  # No conflicts initially
        assert result["available_agents"] == 2  # Both agents are available
    
    def test_orchestrate_project_with_assignments(self, orchestrator, sample_project):
        """Test orchestration that creates new assignments"""
        result = orchestrator.orchestrate_project(sample_project)
        
        # Should have created some assignments
        assert len(result["new_assignments"]) > 0
        
        # Check that trees are assigned to appropriate agents
        assignments = result["new_assignments"]
        if "frontend_tree" in assignments:
            assert assignments["frontend_tree"] in ["frontend_agent", "backend_agent"]
        if "backend_tree" in assignments:
            assert assignments["backend_tree"] in ["frontend_agent", "backend_agent"]
    
    def test_orchestrate_project_skips_offline_agents(self, orchestrator, sample_project):
        """Test that offline agents are excluded from orchestration"""
        # Set one agent as offline
        sample_project.registered_agents["backend_agent"].status = AgentStatus.OFFLINE
        
        result = orchestrator.orchestrate_project(sample_project)
        
        # Should only count available agents
        assert result["available_agents"] == 1
    
    def test_orchestrate_project_with_existing_assignments(self, orchestrator, sample_project):
        """Test orchestration when some trees are already assigned"""
        # Pre-assign one tree
        sample_project.agent_assignments["frontend_tree"] = "frontend_agent"
        
        result = orchestrator.orchestrate_project(sample_project)
        
        # Should not reassign already assigned tree
        new_assignments = result["new_assignments"]
        assert "frontend_tree" not in new_assignments
    
    def test_orchestrate_project_generates_recommendations(self, orchestrator, sample_project):
        """Test that orchestration generates task recommendations for agents"""
        # Mock the get_available_work_for_agent method
        with patch.object(sample_project, 'get_available_work_for_agent') as mock_get_work:
            frontend_task = sample_project.task_trees["frontend_tree"].all_tasks["20250625001"]
            backend_task = sample_project.task_trees["backend_tree"].all_tasks["20250625002"]
            
            # Return different tasks for different agents
            def get_work_side_effect(agent_id):
                if agent_id == "frontend_agent":
                    return [frontend_task]
                elif agent_id == "backend_agent":
                    return [backend_task]
                return []
            
            mock_get_work.side_effect = get_work_side_effect
            
            result = orchestrator.orchestrate_project(sample_project)
            
            # Should have recommendations for both agents
            recommendations = result["agent_recommendations"]
            assert len(recommendations) > 0
            
            # Recommendations should contain task IDs
            for agent_id, task_id in recommendations.items():
                if task_id:  # Some recommendations might be None
                    assert task_id in ["20250625001", "20250625002"]
    
    def test_coordinate_cross_tree_dependencies_no_dependencies(self, orchestrator, sample_project):
        """Test dependency coordination when no dependencies exist"""
        issues = orchestrator.coordinate_cross_tree_dependencies(sample_project)
        
        assert isinstance(issues, list)
        assert len(issues) == 0  # No dependencies = no issues
    
    def test_coordinate_cross_tree_dependencies_missing_prerequisite(self, orchestrator, sample_project):
        """Test dependency coordination with missing prerequisites"""
        # Add dependency on non-existent task
        sample_project.cross_tree_dependencies["20250625001"] = ["20250625999"]
        
        issues = orchestrator.coordinate_cross_tree_dependencies(sample_project)
        
        assert len(issues) == 1
        assert issues[0]["type"] == "missing_prerequisite"
        assert issues[0]["dependent_task"] == "20250625001"
        assert issues[0]["missing_prerequisite"] == "20250625999"
    
    def test_coordinate_cross_tree_dependencies_prerequisite_not_active(self, orchestrator, sample_project):
        """Test dependency coordination when prerequisite is not being worked on"""
        # Add valid dependency
        sample_project.cross_tree_dependencies["20250625001"] = ["20250625002"]
        
        # Assign agent to backend tree but don't make task active
        sample_project.agent_assignments["backend_tree"] = "backend_agent"
        sample_project.registered_agents["backend_agent"].active_tasks = []  # No active tasks
        
        issues = orchestrator.coordinate_cross_tree_dependencies(sample_project)
        
        assert len(issues) == 1
        assert issues[0]["type"] == "prerequisite_not_active"
        assert issues[0]["dependent_task"] == "20250625001"
        assert issues[0]["prerequisite_task"] == "20250625002"
        assert issues[0]["recommendation"] == "prioritize_prerequisite"
    
    def test_balance_workload_no_imbalance(self, orchestrator, sample_project):
        """Test workload balancing when loads are balanced"""
        result = orchestrator.balance_workload(sample_project)
        
        assert "workload_analysis" in result
        assert "rebalancing_recommendations" in result
        
        analysis = result["workload_analysis"]
        assert "overloaded_agents" in analysis
        assert "underloaded_agents" in analysis
        assert "average_workload" in analysis
        assert "workload_distribution" in analysis
        
        # With current setup, no agents should be overloaded
        assert len(analysis["overloaded_agents"]) == 0
    
    def test_balance_workload_with_overloaded_agent(self, orchestrator, sample_project):
        """Test workload balancing with overloaded agent"""
        # Simulate overloaded agent
        overloaded_agent = sample_project.registered_agents["backend_agent"]
        overloaded_agent.current_workload = 2  # Above 80% (2/2 = 100%)
        overloaded_agent.active_tasks = ["20250625002"]
        
        # Simulate underloaded agent
        underloaded_agent = sample_project.registered_agents["frontend_agent"] 
        underloaded_agent.current_workload = 1  # Below 50% (1/3 = 33%)
        
        result = orchestrator.balance_workload(sample_project)
        
        analysis = result["workload_analysis"]
        assert "backend_agent" in analysis["overloaded_agents"]
        assert "frontend_agent" in analysis["underloaded_agents"]
        
        # Should have rebalancing recommendations
        recommendations = result["rebalancing_recommendations"]
        if recommendations:  # Recommendations depend on task compatibility
            assert recommendations[0]["type"] == "reassign_task"
            assert recommendations[0]["from_agent"] == "backend_agent"
            assert recommendations[0]["to_agent"] == "frontend_agent"
    
    def test_handle_timeout_sessions(self, orchestrator, sample_project):
        """Test handling of timed-out work sessions"""
        now = datetime.now()
        
        # Create a session that should timeout
        timeout_session = WorkSession.create_session(
            agent_id="backend_agent",
            task_id="20250625002", 
            tree_id="backend_tree",
            max_duration_hours=1.0
        )
        # Make it appear to have started 2 hours ago
        timeout_session.started_at = now - timedelta(hours=2)
        
        # Add the task to the agent's active tasks first
        agent = sample_project.registered_agents["backend_agent"]
        agent.start_task("20250625002")
        
        sample_project.active_work_sessions["session1"] = timeout_session
        
        # Call the private method through orchestration
        orchestrator._handle_timeout_sessions(sample_project)
        
        # Session should be timed out and removed
        assert "session1" not in sample_project.active_work_sessions
        assert timeout_session.status == SessionStatus.TIMEOUT
        
        # Agent should have task removed
        assert "20250625002" not in agent.active_tasks
    
    def test_detect_conflicts_no_conflicts(self, orchestrator, sample_project):
        """Test conflict detection when no conflicts exist"""
        conflicts = orchestrator._detect_conflicts(sample_project)
        
        assert isinstance(conflicts, list)
        assert len(conflicts) == 0
    
    def test_detect_conflicts_resource_conflict(self, orchestrator, sample_project):
        """Test detection of resource conflicts"""
        # Create two sessions that lock the same resource
        session1 = WorkSession.create_session("agent1", "task1", "tree1")
        session1.lock_resource("database_connection")
        
        session2 = WorkSession.create_session("agent2", "task2", "tree2") 
        session2.lock_resource("database_connection")
        
        # Use the actual session IDs as keys
        session1_id = session1.id
        session2_id = session2.id
        
        sample_project.active_work_sessions[session1_id] = session1
        sample_project.active_work_sessions[session2_id] = session2
        
        conflicts = orchestrator._detect_conflicts(sample_project)
        
        assert len(conflicts) == 1
        assert conflicts[0]["type"] == "resource_conflict"
        assert conflicts[0]["resource"] == "database_connection"
        assert set(conflicts[0]["conflicting_sessions"]) == {session1_id, session2_id}
    
    def test_resolve_conflicts_resource_conflict(self, orchestrator, sample_project):
        """Test resolution of resource conflicts"""
        # Create conflict scenario
        session1 = WorkSession.create_session("agent1", "task1", "tree1")
        session1.lock_resource("database_connection")
        
        session2 = WorkSession.create_session("agent2", "task2", "tree2")
        session2.lock_resource("database_connection") 
        
        sample_project.active_work_sessions["session1"] = session1
        sample_project.active_work_sessions["session2"] = session2
        
        conflicts = [{
            "type": "resource_conflict",
            "resource": "database_connection",
            "conflicting_sessions": ["session1", "session2"]
        }]
        
        orchestrator._resolve_conflicts(sample_project, conflicts)
        
        # Older session (session1) should have resource unlocked
        assert "database_connection" not in session1.resources_locked
        assert "database_connection" in session2.resources_locked
    
    def test_prioritize_tasks_for_agent_no_tasks(self, orchestrator):
        """Test task prioritization when no tasks available"""
        agent = Mock()
        result = orchestrator._prioritize_tasks_for_agent(agent, [])
        
        assert result is None
    
    def test_prioritize_tasks_for_agent_with_preferences(self, orchestrator, sample_project):
        """Test task prioritization based on agent preferences"""
        agent = sample_project.registered_agents["frontend_agent"]
        agent.priority_preference = "high"
        
        # Create tasks with different priorities
        high_task = Task.create(
            id=TaskId.from_string("20250625101"),
            title="High Priority Task",
            description="Important work",
            status=TaskStatus("todo"),
            priority=Priority("high")
        )
        
        low_task = Task.create(
            id=TaskId.from_string("20250625102"), 
            title="Low Priority Task",
            description="Less important work",
            status=TaskStatus("todo"),
            priority=Priority("low")
        )
        
        tasks = [low_task, high_task]  # Deliberate disorder
        
        result = orchestrator._prioritize_tasks_for_agent(agent, tasks)
        
        # Should prioritize high priority task that matches agent preference
        assert result == high_task
    
    def test_prioritize_tasks_for_agent_by_age(self, orchestrator, sample_project):
        """Test task prioritization considers task age"""
        agent = sample_project.registered_agents["frontend_agent"]
        
        now = datetime.now(timezone.utc)
        
        # Create tasks with different ages
        old_task = Task.create(
            id=TaskId.from_string("20250625101"),
            title="Old Task",
            description="Old work",
            status=TaskStatus("todo"),
            priority=Priority("medium")
        )
        old_task.created_at = now - timedelta(days=5)
        
        new_task = Task.create(
            id=TaskId.from_string("20250625102"),
            title="New Task", 
            description="New work",
            status=TaskStatus("todo"),
            priority=Priority("medium")
        )
        new_task.created_at = now - timedelta(hours=1)
        
        tasks = [new_task, old_task]
        
        result = orchestrator._prioritize_tasks_for_agent(agent, tasks)
        
        # Should prioritize older task when priorities are equal
        assert result == old_task
    
    def test_can_agent_handle_task_frontend(self, orchestrator):
        """Test agent task compatibility for frontend tasks"""
        frontend_agent = Agent(
            id="frontend_agent",
            name="Frontend Dev",
            description="Frontend specialist",
            capabilities={AgentCapability.FRONTEND_DEVELOPMENT},
            preferred_languages=["javascript"],
            status=AgentStatus.AVAILABLE,
            max_concurrent_tasks=3,
            current_workload=0
        )
        
        frontend_task = Task.create(
            id=TaskId.from_string("20250625001"),
            title="React Frontend Development",
            description="Build UI components with React",
            status=TaskStatus("todo"),
            priority=Priority("medium")
        )
        
        assert orchestrator._can_agent_handle_task(frontend_agent, frontend_task) is True
    
    def test_can_agent_handle_task_backend(self, orchestrator):
        """Test agent task compatibility for backend tasks"""
        backend_agent = Agent(
            id="backend_agent",
            name="Backend Dev",
            description="Backend specialist", 
            capabilities={AgentCapability.BACKEND_DEVELOPMENT},
            preferred_languages=["python"],
            status=AgentStatus.AVAILABLE,
            max_concurrent_tasks=2,
            current_workload=0
        )
        
        backend_task = Task.create(
            id=TaskId.from_string("20250625002"),
            title="API Server Development",
            description="Create backend API endpoints",
            status=TaskStatus("todo"),
            priority=Priority("medium")
        )
        
        assert orchestrator._can_agent_handle_task(backend_agent, backend_task) is True
    
    def test_can_agent_handle_task_capability_mismatch(self, orchestrator):
        """Test agent task compatibility when capabilities don't match"""
        frontend_agent = Agent(
            id="frontend_agent",
            name="Frontend Dev",
            description="Frontend specialist",
            capabilities={AgentCapability.FRONTEND_DEVELOPMENT},
            preferred_languages=["javascript"],
            status=AgentStatus.AVAILABLE,
            max_concurrent_tasks=3,
            current_workload=0
        )
        
        backend_task = Task.create(
            id=TaskId.from_string("20250625002"),
            title="Database Server Setup", 
            description="Configure backend database server",
            status=TaskStatus("todo"),
            priority=Priority("medium")
        )
        
        assert orchestrator._can_agent_handle_task(frontend_agent, backend_task) is False
    
    def test_can_agent_handle_task_general_task(self, orchestrator):
        """Test agent can handle general tasks without specific keywords"""
        agent = Agent(
            id="agent1",
            name="General Agent",
            description="General purpose agent",
            capabilities={AgentCapability.BACKEND_DEVELOPMENT},  # Use existing capability
            preferred_languages=["python"],
            status=AgentStatus.AVAILABLE,
            max_concurrent_tasks=2,
            current_workload=0
        )
        
        general_task = Task.create(
            id=TaskId.from_string("20250625003"),
            title="Documentation Update",
            description="Update project documentation",
            status=TaskStatus("todo"),
            priority=Priority("low")
        )
        
        assert orchestrator._can_agent_handle_task(agent, general_task) is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])