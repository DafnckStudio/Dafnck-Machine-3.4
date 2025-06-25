"""
Comprehensive tests for the Orchestrator domain service.
Tests multi-agent coordination, task assignment, and orchestration strategies.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from fastmcp.task_management.domain.services.orchestrator import (
    OrchestrationStrategy, 
    CapabilityBasedStrategy
)
from fastmcp.task_management.domain.entities.project import Project
from fastmcp.task_management.domain.entities.agent import Agent, AgentCapability, AgentStatus
from fastmcp.task_management.domain.entities.task_tree import TaskTree
from fastmcp.task_management.domain.entities.task import Task
from fastmcp.task_management.domain.entities.work_session import WorkSession
from fastmcp.task_management.domain.value_objects.task_id import TaskId
from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
from fastmcp.task_management.domain.value_objects.priority import Priority


class TestCapabilityBasedStrategy:
    """Test capability-based orchestration strategy"""
    
    @pytest.fixture
    def strategy(self):
        """Create capability-based strategy instance"""
        return CapabilityBasedStrategy()
    
    @pytest.fixture
    def sample_project(self):
        """Create sample project with task trees"""
        now = datetime.now()
        project = Project(
            id="test_project",
            name="Test Project",
            description="Test project for orchestrator",
            created_at=now,
            updated_at=now
        )
        
        # Create frontend task tree
        frontend_tree = TaskTree(
            id="frontend_tree",
            name="Frontend Tasks",
            description="UI development tasks",
            project_id="test_project",
            created_at=now
        )
        
        # Add frontend tasks
        frontend_task = Task.create(
            id=TaskId.from_string("20250625001"),
            title="Implement React Components",
            description="Create responsive UI components using React",
            status=TaskStatus("todo"),
            priority=Priority("high")
        )
        frontend_tree.add_root_task(frontend_task)
        
        # Create backend task tree
        backend_tree = TaskTree(
            id="backend_tree", 
            name="Backend Tasks",
            description="API development tasks",
            project_id="test_project",
            created_at=now
        )
        
        # Add backend tasks
        backend_task = Task.create(
            id=TaskId.from_string("20250625002"),
            title="Implement REST API",
            description="Create Python FastAPI endpoints for backend",
            status=TaskStatus("todo"),
            priority=Priority("medium")
        )
        backend_tree.add_root_task(backend_task)
        
        project.task_trees["frontend_tree"] = frontend_tree
        project.task_trees["backend_tree"] = backend_tree
        
        return project
    
    @pytest.fixture
    def sample_agents(self):
        """Create sample agents with different capabilities"""
        # Frontend specialist agent
        frontend_agent = Agent(
            id="frontend_agent",
            name="Frontend Developer",
            description="Frontend development specialist",
            capabilities={AgentCapability.FRONTEND_DEVELOPMENT},
            preferred_languages=["javascript", "typescript", "html", "css"],
            status=AgentStatus.AVAILABLE,
            max_concurrent_tasks=3,
            current_workload=0
        )
        
        # Backend specialist agent
        backend_agent = Agent(
            id="backend_agent", 
            name="Backend Developer",
            description="Backend development specialist",
            capabilities={AgentCapability.BACKEND_DEVELOPMENT},
            preferred_languages=["python", "java", "sql"],
            status=AgentStatus.AVAILABLE,
            max_concurrent_tasks=2,
            current_workload=1
        )
        
        # Full-stack agent
        fullstack_agent = Agent(
            id="fullstack_agent",
            name="Full Stack Developer",
            description="Full-stack development specialist",
            capabilities={
                AgentCapability.FRONTEND_DEVELOPMENT,
                AgentCapability.BACKEND_DEVELOPMENT
            },
            preferred_languages=["javascript", "python", "typescript"],
            status=AgentStatus.AVAILABLE,
            max_concurrent_tasks=4,
            current_workload=2
        )
        
        return [frontend_agent, backend_agent, fullstack_agent]
    
    def test_assign_work_matches_capabilities(self, strategy, sample_project, sample_agents):
        """Test that work assignment matches agent capabilities"""
        assignments = strategy.assign_work(sample_project, sample_agents)
        
        assert "frontend_tree" in assignments
        assert "backend_tree" in assignments
        
        # Frontend tree should be assigned to frontend specialist or fullstack
        frontend_assignee = assignments["frontend_tree"]
        assert frontend_assignee in ["frontend_agent", "fullstack_agent"]
        
        # Backend tree should be assigned to backend specialist or fullstack
        backend_assignee = assignments["backend_tree"]
        assert backend_assignee in ["backend_agent", "fullstack_agent"]
    
    def test_assign_work_no_available_agents(self, strategy, sample_project):
        """Test work assignment when no agents are available"""
        busy_agents = []
        for i in range(3):
            agent = Agent(
                id=f"busy_agent_{i}",
                name=f"Busy Agent {i}",
                description=f"Busy test agent {i}",
                capabilities={AgentCapability.FRONTEND_DEVELOPMENT},
                status=AgentStatus.BUSY,
                max_concurrent_tasks=1,
                current_workload=1
            )
            busy_agents.append(agent)
        
        assignments = strategy.assign_work(sample_project, busy_agents)
        assert assignments == {}
    
    def test_assign_work_skips_already_assigned(self, strategy, sample_project, sample_agents):
        """Test that already assigned trees are skipped"""
        # Pre-assign frontend tree
        sample_project.agent_assignments["frontend_tree"] = "existing_agent"
        
        assignments = strategy.assign_work(sample_project, sample_agents)
        
        # Should not reassign frontend tree
        assert "frontend_tree" not in assignments
        assert "backend_tree" in assignments
    
    def test_calculate_agent_tree_score_capability_match(self, strategy):
        """Test agent scoring based on capability match"""
        # Create agent with frontend capabilities
        agent = Agent(
            id="test_agent",
            name="Test Agent",
            description="Test agent",
            capabilities={AgentCapability.FRONTEND_DEVELOPMENT},
            preferred_languages=["javascript"],
            status=AgentStatus.AVAILABLE,
            max_concurrent_tasks=3,
            current_workload=0
        )
        
        # Create tree requiring frontend work
        tree = TaskTree(
            id="test_tree", 
            name="Test Tree", 
            description="Test",
            project_id="test_project",
            created_at=datetime.now()
        )
        frontend_task = Task.create(
            id=TaskId.from_string("20250625003"),
            title="React component development",
            description="Build UI components with React",
            status=TaskStatus("todo"),
            priority=Priority("high")
        )
        tree.add_root_task(frontend_task)
        
        score = strategy._calculate_agent_tree_score(agent, tree)
        
        # Should have high score due to capability match
        assert score > 70.0  # Base 50 + capability bonus + workload bonus
    
    def test_calculate_agent_tree_score_no_match(self, strategy):
        """Test agent scoring with no capability match"""
        # Create agent with only backend capabilities
        agent = Agent(
            id="test_agent",
            name="Test Agent",
            description="Test agent", 
            capabilities={AgentCapability.BACKEND_DEVELOPMENT},
            preferred_languages=["python"],
            status=AgentStatus.AVAILABLE,
            max_concurrent_tasks=2,
            current_workload=1
        )
        
        # Create tree requiring frontend work
        tree = TaskTree(
            id="test_tree", 
            name="Test Tree", 
            description="Test",
            project_id="test_project",
            created_at=datetime.now()
        )
        frontend_task = Task.create(
            id=TaskId.from_string("20250625004"),
            title="React UI development",
            description="Create responsive frontend with React",
            status=TaskStatus("todo"),
            priority=Priority("medium")
        )
        tree.add_root_task(frontend_task)
        
        score = strategy._calculate_agent_tree_score(agent, tree)
        
        # Should have lower score due to capability mismatch
        assert score <= 65.0  # Mainly base score with reduced workload bonus
    
    def test_analyze_tree_requirements_frontend(self, strategy):
        """Test tree requirements analysis for frontend tasks"""
        tree = TaskTree(
            id="test_tree", 
            name="Frontend Tree", 
            description="UI tasks",
            project_id="test_project",
            created_at=datetime.now()
        )
        
        # Add frontend tasks
        tasks = [
            Task.create(
                id=TaskId.from_string(f"2025062500{i+5}"),
                title=f"React component {i}",
                description="Build UI components using React and TypeScript",
                status=TaskStatus("todo"),
                priority=Priority("high")
            )
            for i in range(3)
        ]
        
        for task in tasks:
            tree.add_root_task(task)
        
        requirements = strategy._analyze_tree_requirements(tree)
        
        assert AgentCapability.FRONTEND_DEVELOPMENT in requirements["capabilities"]
        assert "javascript" in requirements["languages"]
        assert "typescript" in requirements["languages"]
    
    def test_analyze_tree_requirements_backend(self, strategy):
        """Test tree requirements analysis for backend tasks"""
        tree = TaskTree(
            id="test_tree", 
            name="Backend Tree", 
            description="API tasks",
            project_id="test_project",
            created_at=datetime.now()
        )
        
        # Add backend tasks
        backend_task = Task.create(
            id=TaskId.from_string("20250625008"),
            title="Python API development",
            description="Create REST API endpoints using Python and database",
            status=TaskStatus("todo"),
            priority=Priority("high")
        )
        tree.add_root_task(backend_task)
        
        requirements = strategy._analyze_tree_requirements(tree)
        
        assert AgentCapability.BACKEND_DEVELOPMENT in requirements["capabilities"]
        assert "python" in requirements["languages"]
    
    def test_analyze_tree_requirements_mixed(self, strategy):
        """Test tree requirements analysis for mixed task types"""
        tree = TaskTree(
            id="test_tree", 
            name="Mixed Tree", 
            description="Full-stack tasks",
            project_id="test_project",
            created_at=datetime.now()
        )
        
        # Add mixed tasks
        frontend_task = Task.create(
            id=TaskId.from_string("20250625009"),
            title="React frontend",
            description="Build UI with React",
            status=TaskStatus("todo"),
            priority=Priority("high")
        )
        
        backend_task = Task.create(
            id=TaskId.from_string("20250625010"),
            title="API server",
            description="Create backend API",
            status=TaskStatus("todo"),
            priority=Priority("high")
        )
        
        devops_task = Task.create(
            id=TaskId.from_string("20250625011"),
            title="Docker deployment",
            description="Containerize application for deployment",
            status=TaskStatus("todo"),
            priority=Priority("medium")
        )
        
        tree.add_root_task(frontend_task)
        tree.add_root_task(backend_task) 
        tree.add_root_task(devops_task)
        
        requirements = strategy._analyze_tree_requirements(tree)
        
        # Should detect multiple capability requirements
        capabilities = requirements["capabilities"]
        assert AgentCapability.FRONTEND_DEVELOPMENT in capabilities
        assert AgentCapability.BACKEND_DEVELOPMENT in capabilities
        # Note: DEVOPS capability detection needs to be implemented in the strategy


# Additional test classes would go here for other orchestration strategies
# when they are implemented in the domain service


if __name__ == "__main__":
    pytest.main([__file__])