"""
This is the canonical and only maintained test suite for Agent entity.
All CRUD, validation, and edge-case tests should be added here.
Redundant or duplicate tests in other files have been removed.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import time
from fastmcp.task_management.domain.entities.agent import (
    Agent,
    AgentStatus,
    AgentCapability
)


class TestAgentEntity:
    """Comprehensive tests for Agent entity"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.agent_id = "test-agent-001"
        self.agent_name = "Test Agent"
        self.agent_description = "A test agent for unit testing"
        self.created_at = datetime.now()
        
        self.agent = Agent(
            id=self.agent_id,
            name=self.agent_name,
            description=self.agent_description,
            created_at=self.created_at
        )
    
    def test_agent_initialization(self):
        """Test agent initialization with required fields"""
        assert self.agent.id == self.agent_id
        assert self.agent.name == self.agent_name
        assert self.agent.description == self.agent_description
        assert self.agent.created_at == self.created_at
        assert isinstance(self.agent.updated_at, datetime)
        assert self.agent.status == AgentStatus.AVAILABLE
        assert self.agent.max_concurrent_tasks == 1
        assert self.agent.current_workload == 0
        assert self.agent.completed_tasks == 0
        assert self.agent.success_rate == 100.0
        assert len(self.agent.capabilities) == 0
        assert len(self.agent.specializations) == 0
        assert len(self.agent.preferred_languages) == 0
        assert len(self.agent.preferred_frameworks) == 0
        assert len(self.agent.assigned_projects) == 0
        assert len(self.agent.assigned_trees) == 0
        assert len(self.agent.active_tasks) == 0
    
    def test_agent_initialization_with_optional_fields(self):
        """Test agent initialization with optional fields"""
        capabilities = {AgentCapability.FRONTEND_DEVELOPMENT, AgentCapability.TESTING}
        specializations = ["React", "Jest"]
        preferred_languages = ["TypeScript", "Python"]
        work_hours = {"start": "09:00", "end": "17:00"}
        
        agent = Agent(
            id="test-agent-002",
            name="Full Agent",
            description="Agent with all fields",
            created_at=datetime.now(),
            capabilities=capabilities,
            specializations=specializations,
            preferred_languages=preferred_languages,
            max_concurrent_tasks=3,
            work_hours=work_hours,
            timezone="EST",
            priority_preference="medium"
        )
        
        assert agent.capabilities == capabilities
        assert agent.specializations == specializations
        assert agent.preferred_languages == preferred_languages
        assert agent.max_concurrent_tasks == 3
        assert agent.work_hours == work_hours
        assert agent.timezone == "EST"
        assert agent.priority_preference == "medium"
    
    def test_add_capability(self):
        """Test adding capability to agent"""
        initial_updated = self.agent.updated_at
        time.sleep(0.001)
        
        # Add capability
        self.agent.add_capability(AgentCapability.FRONTEND_DEVELOPMENT)
        
        assert AgentCapability.FRONTEND_DEVELOPMENT in self.agent.capabilities
        assert self.agent.updated_at > initial_updated
    
    def test_remove_capability(self):
        """Test removing capability from agent"""
        # Add capability first
        self.agent.add_capability(AgentCapability.FRONTEND_DEVELOPMENT)
        self.agent.add_capability(AgentCapability.TESTING)
        
        initial_updated = self.agent.updated_at
        time.sleep(0.001)
        
        # Remove capability
        self.agent.remove_capability(AgentCapability.FRONTEND_DEVELOPMENT)
        
        assert AgentCapability.FRONTEND_DEVELOPMENT not in self.agent.capabilities
        assert AgentCapability.TESTING in self.agent.capabilities
        assert self.agent.updated_at > initial_updated
    
    def test_remove_nonexistent_capability(self):
        """Test removing capability that doesn't exist"""
        initial_capabilities = self.agent.capabilities.copy()
        
        # Remove non-existent capability
        self.agent.remove_capability(AgentCapability.FRONTEND_DEVELOPMENT)
        
        assert self.agent.capabilities == initial_capabilities
    
    def test_has_capability(self):
        """Test checking if agent has capability"""
        assert not self.agent.has_capability(AgentCapability.FRONTEND_DEVELOPMENT)
        
        self.agent.add_capability(AgentCapability.FRONTEND_DEVELOPMENT)
        assert self.agent.has_capability(AgentCapability.FRONTEND_DEVELOPMENT)
    
    def test_can_handle_task_with_capabilities(self):
        """Test task handling capability checking"""
        # Add capabilities
        self.agent.add_capability(AgentCapability.FRONTEND_DEVELOPMENT)
        self.agent.add_capability(AgentCapability.TESTING)
        
        # Task requiring frontend development
        task_requirements = {"capabilities": ["frontend_development"]}
        assert self.agent.can_handle_task(task_requirements)
        
        # Task requiring backend development (not available)
        task_requirements = {"capabilities": ["backend_development"]}
        assert not self.agent.can_handle_task(task_requirements)
        
        # Task requiring multiple capabilities
        task_requirements = {"capabilities": ["frontend_development", "testing"]}
        assert self.agent.can_handle_task(task_requirements)
        
        # Task requiring mix of available and unavailable
        task_requirements = {"capabilities": ["frontend_development", "backend_development"]}
        assert not self.agent.can_handle_task(task_requirements)
    
    def test_can_handle_task_with_languages(self):
        """Test task handling with programming languages"""
        self.agent.preferred_languages = ["Python", "JavaScript"]
        
        # Task requiring Python
        task_requirements = {"languages": ["Python"]}
        assert self.agent.can_handle_task(task_requirements)
        
        # Task requiring Java (not available)
        task_requirements = {"languages": ["Java"]}
        assert not self.agent.can_handle_task(task_requirements)
        
        # Task requiring multiple languages (one available)
        task_requirements = {"languages": ["Python", "Go"]}
        assert self.agent.can_handle_task(task_requirements)
    
    def test_can_handle_task_with_frameworks(self):
        """Test task handling with frameworks"""
        self.agent.preferred_frameworks = ["React", "FastAPI"]
        
        # Task requiring React
        task_requirements = {"frameworks": ["React"]}
        assert self.agent.can_handle_task(task_requirements)
        
        # Task requiring Django (not available)
        task_requirements = {"frameworks": ["Django"]}
        assert not self.agent.can_handle_task(task_requirements)
        
        # Task requiring multiple frameworks (one available)
        task_requirements = {"frameworks": ["React", "Vue"]}
        assert self.agent.can_handle_task(task_requirements)
    
    def test_can_handle_task_with_enum_capabilities(self):
        """Test task handling with AgentCapability enum objects"""
        self.agent.add_capability(AgentCapability.FRONTEND_DEVELOPMENT)
        
        # Task with enum capability
        task_requirements = {"capabilities": [AgentCapability.FRONTEND_DEVELOPMENT]}
        assert self.agent.can_handle_task(task_requirements)
        
        # Task with enum capability not available
        task_requirements = {"capabilities": [AgentCapability.BACKEND_DEVELOPMENT]}
        assert not self.agent.can_handle_task(task_requirements)
    
    def test_can_handle_task_with_invalid_capability_string(self):
        """Test task handling with invalid capability strings"""
        task_requirements = {"capabilities": ["invalid_capability"]}
        # Should not crash and should return True (since no valid capabilities to check)
        assert self.agent.can_handle_task(task_requirements)
    
    def test_is_available(self):
        """Test agent availability checking"""
        # Initially available
        assert self.agent.is_available()
        
        # Set to busy
        self.agent.status = AgentStatus.BUSY
        assert not self.agent.is_available()
        
        # Set back to available but at max workload
        self.agent.status = AgentStatus.AVAILABLE
        self.agent.current_workload = self.agent.max_concurrent_tasks
        assert not self.agent.is_available()
        
        # Available with room for more work
        self.agent.current_workload = 0
        assert self.agent.is_available()
    
    def test_assign_to_project(self):
        """Test assigning agent to project"""
        project_id = "project-123"
        initial_updated = self.agent.updated_at
        time.sleep(0.001)
        
        self.agent.assign_to_project(project_id)
        
        assert project_id in self.agent.assigned_projects
        assert self.agent.updated_at > initial_updated
    
    def test_assign_to_tree(self):
        """Test assigning agent to task tree"""
        tree_id = "tree-456"
        initial_updated = self.agent.updated_at
        time.sleep(0.001)
        
        self.agent.assign_to_tree(tree_id)
        
        assert tree_id in self.agent.assigned_trees
        assert self.agent.updated_at > initial_updated
    
    def test_start_task_success(self):
        """Test starting a task successfully"""
        task_id = "task-789"
        initial_updated = self.agent.updated_at
        time.sleep(0.001)
        
        self.agent.start_task(task_id)
        
        assert task_id in self.agent.active_tasks
        assert self.agent.current_workload == 1
        assert self.agent.status == AgentStatus.BUSY  # Since max_concurrent_tasks is 1
        assert self.agent.updated_at > initial_updated
    
    def test_start_task_not_available(self):
        """Test starting task when agent is not available"""
        self.agent.status = AgentStatus.OFFLINE
        
        with pytest.raises(ValueError, match="Agent test-agent-001 is not available for new tasks"):
            self.agent.start_task("task-123")
    
    def test_start_task_multiple_concurrent(self):
        """Test starting multiple tasks with higher concurrent limit"""
        self.agent.max_concurrent_tasks = 3
        
        # Start first task
        self.agent.start_task("task-1")
        assert self.agent.current_workload == 1
        assert self.agent.status == AgentStatus.AVAILABLE
        
        # Start second task
        self.agent.start_task("task-2")
        assert self.agent.current_workload == 2
        assert self.agent.status == AgentStatus.AVAILABLE
        
        # Start third task (at max capacity)
        self.agent.start_task("task-3")
        assert self.agent.current_workload == 3
        assert self.agent.status == AgentStatus.BUSY
    
    def test_complete_task_success(self):
        """Test completing task successfully"""
        task_id = "task-789"
        
        # Start task first
        self.agent.start_task(task_id)
        initial_completed = self.agent.completed_tasks
        initial_updated = self.agent.updated_at
        time.sleep(0.001)
        
        # Complete task
        self.agent.complete_task(task_id, success=True)
        
        assert task_id not in self.agent.active_tasks
        assert self.agent.current_workload == 0
        assert self.agent.completed_tasks == initial_completed + 1
        assert self.agent.status == AgentStatus.AVAILABLE
        assert self.agent.updated_at > initial_updated
        # Success rate should be updated (weighted average)
        assert self.agent.success_rate >= 99.0  # Should be close to 100
    
    def test_complete_task_failure(self):
        """Test completing task with failure"""
        task_id = "task-789"
        
        # Start task first
        self.agent.start_task(task_id)
        initial_success_rate = self.agent.success_rate
        initial_updated = self.agent.updated_at
        time.sleep(0.001)
        
        # Complete task with failure
        self.agent.complete_task(task_id, success=False)
        
        assert task_id not in self.agent.active_tasks
        assert self.agent.current_workload == 0
        assert self.agent.completed_tasks == 1
        assert self.agent.status == AgentStatus.AVAILABLE
        # Success rate should decrease
        assert self.agent.success_rate < initial_success_rate
        assert self.agent.updated_at > initial_updated
    
    def test_complete_task_not_assigned(self):
        """Test completing task that wasn't assigned"""
        with pytest.raises(ValueError, match="Task task-999 not assigned to agent test-agent-001"):
            self.agent.complete_task("task-999")
    
    def test_complete_task_with_remaining_workload(self):
        """Test completing task while still having other active tasks"""
        self.agent.max_concurrent_tasks = 3
        
        # Start multiple tasks
        self.agent.start_task("task-1")
        self.agent.start_task("task-2")
        
        # Complete one task
        self.agent.complete_task("task-1")
        
        assert "task-1" not in self.agent.active_tasks
        assert "task-2" in self.agent.active_tasks
        assert self.agent.current_workload == 1
        assert self.agent.status == AgentStatus.AVAILABLE  # Should be available again
    
    def test_pause_work(self):
        """Test pausing agent work"""
        initial_updated = self.agent.updated_at
        time.sleep(0.001)
        
        self.agent.pause_work()
        
        assert self.agent.status == AgentStatus.PAUSED
        assert self.agent.updated_at > initial_updated
    
    def test_resume_work_available(self):
        """Test resuming work when under capacity"""
        self.agent.pause_work()
        initial_updated = self.agent.updated_at
        time.sleep(0.001)
        
        self.agent.resume_work()
        
        assert self.agent.status == AgentStatus.AVAILABLE
        assert self.agent.updated_at > initial_updated
    
    def test_resume_work_busy(self):
        """Test resuming work when at capacity"""
        self.agent.start_task("task-1")  # This makes agent busy
        self.agent.pause_work()
        initial_updated = self.agent.updated_at
        time.sleep(0.001)
        
        self.agent.resume_work()
        
        assert self.agent.status == AgentStatus.BUSY
        assert self.agent.updated_at > initial_updated
    
    def test_go_offline(self):
        """Test setting agent offline"""
        initial_updated = self.agent.updated_at
        time.sleep(0.001)
        
        self.agent.go_offline()
        
        assert self.agent.status == AgentStatus.OFFLINE
        assert self.agent.updated_at > initial_updated
    
    def test_go_online(self):
        """Test setting agent online"""
        self.agent.go_offline()
        initial_updated = self.agent.updated_at
        time.sleep(0.001)
        
        self.agent.go_online()
        
        assert self.agent.status == AgentStatus.AVAILABLE
        assert self.agent.updated_at > initial_updated
    
    def test_get_workload_percentage(self):
        """Test workload percentage calculation"""
        # No workload
        assert self.agent.get_workload_percentage() == 0.0
        
        # Partial workload
        self.agent.max_concurrent_tasks = 4
        self.agent.current_workload = 2
        assert self.agent.get_workload_percentage() == 50.0
        
        # Full workload
        self.agent.current_workload = 4
        assert self.agent.get_workload_percentage() == 100.0
        
        # Edge case: zero max tasks
        self.agent.max_concurrent_tasks = 0
        assert self.agent.get_workload_percentage() == 100.0
    
    def test_get_agent_profile(self):
        """Test getting comprehensive agent profile"""
        # Set up agent with various data
        self.agent.add_capability(AgentCapability.FRONTEND_DEVELOPMENT)
        self.agent.specializations = ["React", "TypeScript"]
        self.agent.preferred_languages = ["JavaScript", "Python"]
        self.agent.preferred_frameworks = ["React", "FastAPI"]
        self.agent.work_hours = {"start": "09:00", "end": "17:00"}
        self.agent.timezone = "EST"
        self.agent.priority_preference = "high"
        self.agent.assign_to_project("project-1")
        self.agent.assign_to_tree("tree-1")
        self.agent.start_task("task-1")
        self.agent.completed_tasks = 5
        self.agent.success_rate = 95.0
        self.agent.average_task_duration = 2.5
        
        profile = self.agent.get_agent_profile()
        
        # Check all profile fields
        assert profile["id"] == self.agent.id
        assert profile["name"] == self.agent.name
        assert profile["description"] == self.agent.description
        assert profile["status"] == self.agent.status.value
        assert profile["capabilities"] == ["frontend_development"]
        assert profile["specializations"] == ["React", "TypeScript"]
        assert profile["preferred_languages"] == ["JavaScript", "Python"]
        assert profile["preferred_frameworks"] == ["React", "FastAPI"]
        
        # Check workload section
        workload = profile["workload"]
        assert workload["current"] == 1
        assert workload["max"] == 1
        assert workload["percentage"] == 100.0
        assert workload["available"] is False
        
        # Check performance section
        performance = profile["performance"]
        assert performance["completed_tasks"] == 5
        assert performance["success_rate"] == 95.0
        assert performance["average_duration"] == 2.5
        
        # Check assignments section
        assignments = profile["assignments"]
        assert assignments["projects"] == ["project-1"]
        assert assignments["trees"] == ["tree-1"]
        assert assignments["active_tasks"] == ["task-1"]
        
        # Check preferences section
        preferences = profile["preferences"]
        assert preferences["work_hours"] == {"start": "09:00", "end": "17:00"}
        assert preferences["timezone"] == "EST"
        assert preferences["priority_preference"] == "high"
        
        # Check timestamps
        assert "created_at" in profile
        assert "updated_at" in profile
    
    def test_calculate_task_suitability_score_cannot_handle(self):
        """Test suitability score when agent cannot handle task"""
        task_requirements = {"capabilities": ["backend_development"]}
        
        score = self.agent.calculate_task_suitability_score(task_requirements)
        
        assert score == 0.0
    
    def test_calculate_task_suitability_score_basic(self):
        """Test basic suitability score calculation"""
        self.agent.add_capability(AgentCapability.FRONTEND_DEVELOPMENT)
        task_requirements = {"capabilities": ["frontend_development"]}
        
        score = self.agent.calculate_task_suitability_score(task_requirements)
        
        # Base score (50) + availability (20) + low workload (10) + high success rate (10)
        assert score >= 90.0
    
    def test_calculate_task_suitability_score_not_available(self):
        """Test suitability score when agent is not available"""
        self.agent.add_capability(AgentCapability.FRONTEND_DEVELOPMENT)
        self.agent.status = AgentStatus.OFFLINE
        task_requirements = {"capabilities": ["frontend_development"]}
        
        score = self.agent.calculate_task_suitability_score(task_requirements)
        
        # Base score (50) + no availability bonus + low workload (10) + high success rate (10)
        assert score >= 70.0
        assert score < 90.0
    
    def test_calculate_task_suitability_score_high_workload(self):
        """Test suitability score with high workload"""
        self.agent.add_capability(AgentCapability.FRONTEND_DEVELOPMENT)
        self.agent.max_concurrent_tasks = 4
        self.agent.current_workload = 3  # 75% workload
        task_requirements = {"capabilities": ["frontend_development"]}
        
        score = self.agent.calculate_task_suitability_score(task_requirements)
        
        # Base score (50) + availability (20) + workload bonus (2.5) + success rate (10)
        assert score >= 80.0
        assert score < 85.0
    
    def test_calculate_task_suitability_score_low_success_rate(self):
        """Test suitability score with low success rate"""
        self.agent.add_capability(AgentCapability.FRONTEND_DEVELOPMENT)
        self.agent.success_rate = 60.0
        task_requirements = {"capabilities": ["frontend_development"]}
        
        score = self.agent.calculate_task_suitability_score(task_requirements)
        
        # Base score (50) + availability (20) + low workload (10) + success rate (6)
        assert score >= 86.0
        assert score < 90.0
    
    def test_calculate_task_suitability_score_matching_priority(self):
        """Test suitability score with matching priority preference"""
        self.agent.add_capability(AgentCapability.FRONTEND_DEVELOPMENT)
        self.agent.priority_preference = "high"
        task_requirements = {"capabilities": ["frontend_development"], "priority": "high"}
        
        score = self.agent.calculate_task_suitability_score(task_requirements)
        
        # Base score (50) + availability (20) + low workload (10) + success rate (10) + priority match (10)
        assert score == 100.0
    
    def test_calculate_task_suitability_score_non_matching_priority(self):
        """Test suitability score with non-matching priority preference"""
        self.agent.add_capability(AgentCapability.FRONTEND_DEVELOPMENT)
        self.agent.priority_preference = "high"
        task_requirements = {"capabilities": ["frontend_development"], "priority": "low"}
        
        score = self.agent.calculate_task_suitability_score(task_requirements)
        
        # Base score (50) + availability (20) + low workload (10) + success rate (10)
        assert score >= 90.0
        assert score < 100.0
    
    def test_create_agent_factory_method(self):
        """Test creating agent using factory method"""
        agent_id = "factory-agent"
        name = "Factory Agent"
        description = "Created via factory"
        capabilities = [AgentCapability.TESTING, AgentCapability.DOCUMENTATION]
        specializations = ["Pytest", "Sphinx"]
        preferred_languages = ["Python"]
        
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
        assert isinstance(agent.created_at, datetime)
    
    def test_create_agent_factory_method_minimal(self):
        """Test creating agent using factory method with minimal parameters"""
        agent = Agent.create_agent(
            agent_id="minimal-agent",
            name="Minimal Agent",
            description="Minimal setup"
        )
        
        assert agent.id == "minimal-agent"
        assert agent.name == "Minimal Agent"
        assert agent.description == "Minimal setup"
        assert len(agent.capabilities) == 0
        assert len(agent.specializations) == 0
        assert len(agent.preferred_languages) == 0 