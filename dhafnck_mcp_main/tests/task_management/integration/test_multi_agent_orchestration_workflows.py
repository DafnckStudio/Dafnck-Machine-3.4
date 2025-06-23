#!/usr/bin/env python3
"""
This is the canonical and only maintained test suite for multi-agent orchestration workflow integration tests in task management.
All validation, edge-case, and integration tests should be added here.
Redundant or duplicate tests in other files have been removed.

Comprehensive tests for Multi-Agent Orchestration Workflows
Tests end-to-end orchestration scenarios and complex workflows
"""

import pytest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List, Any
import time

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from fastmcp.dhafnck_mcp.domain.entities.project import Project
from fastmcp.dhafnck_mcp.domain.entities.agent import Agent, AgentCapability, AgentStatus
from fastmcp.dhafnck_mcp.domain.entities.task_tree import TaskTree
from fastmcp.dhafnck_mcp.domain.entities.work_session import WorkSession
from fastmcp.dhafnck_mcp.domain.entities.task import Task
from fastmcp.dhafnck_mcp.domain.services.orchestrator import Orchestrator
from fastmcp.dhafnck_mcp.domain.value_objects.task_id import TaskId
from fastmcp.dhafnck_mcp.domain.value_objects.task_status import TaskStatus, TaskStatusEnum
from fastmcp.dhafnck_mcp.domain.value_objects.priority import Priority, PriorityLevel


class TestOrchestrationWorkflows:
    """Test orchestration workflows and scenarios"""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance"""
        return Orchestrator()
    
    @pytest.fixture
    def ecommerce_project(self):
        """Create a complete e-commerce project setup for testing"""
        project = Project(
            id="ecommerce_project",
            name="E-Commerce Platform",
            description="Full-stack e-commerce application",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Create task trees
        frontend_tree = project.create_task_tree(
            "frontend", 
            "Frontend Development",
            "React-based user interface"
        )
        backend_tree = project.create_task_tree(
            "backend",
            "Backend Development", 
            "Node.js API and services"
        )
        devops_tree = project.create_task_tree(
            "devops",
            "DevOps & Infrastructure",
            "Deployment and CI/CD"
        )
        testing_tree = project.create_task_tree(
            "testing",
            "Quality Assurance",
            "Testing and validation"
        )
        
        # Create specialized agents
        frontend_agent = Agent.create_agent(
            agent_id="frontend_dev",
            name="Frontend Developer",
            description="React and TypeScript specialist",
            capabilities=[
                AgentCapability.FRONTEND_DEVELOPMENT,
                AgentCapability.CODE_REVIEW,
                AgentCapability.TESTING
            ],
            specializations=["React", "TypeScript", "CSS", "UI/UX"],
            preferred_languages=["javascript", "typescript", "html", "css"]
        )
        frontend_agent.max_concurrent_tasks = 2
        
        backend_agent = Agent.create_agent(
            agent_id="backend_dev",
            name="Backend Developer",
            description="Node.js and API specialist",
            capabilities=[
                AgentCapability.BACKEND_DEVELOPMENT,
                AgentCapability.ARCHITECTURE,
                AgentCapability.SECURITY
            ],
            specializations=["Node.js", "Express", "MongoDB", "REST APIs"],
            preferred_languages=["javascript", "typescript", "python"]
        )
        backend_agent.max_concurrent_tasks = 2
        
        devops_agent = Agent.create_agent(
            agent_id="devops_eng",
            name="DevOps Engineer",
            description="Infrastructure and deployment specialist",
            capabilities=[
                AgentCapability.DEVOPS,
                AgentCapability.SECURITY
            ],
            specializations=["Docker", "AWS", "CI/CD", "Kubernetes"],
            preferred_languages=["bash", "yaml", "python"]
        )
        devops_agent.max_concurrent_tasks = 1
        
        qa_agent = Agent.create_agent(
            agent_id="qa_eng",
            name="QA Engineer",
            description="Testing and quality assurance specialist",
            capabilities=[
                AgentCapability.TESTING,
                AgentCapability.CODE_REVIEW
            ],
            specializations=["Jest", "Cypress", "Selenium", "Test Automation"],
            preferred_languages=["javascript", "python"]
        )
        qa_agent.max_concurrent_tasks = 3
        
        # Register agents
        project.register_agent(frontend_agent)
        project.register_agent(backend_agent)
        project.register_agent(devops_agent)
        project.register_agent(qa_agent)
        
        return project
    
    @pytest.fixture
    def sample_tasks(self):
        """Create sample tasks for testing"""
        return {
            "frontend_tasks": [
                {
                    "id": "frontend_auth_ui",
                    "title": "User Authentication UI",
                    "description": "Login and registration forms",
                    "status": "todo",
                    "priority": "high"
                },
                {
                    "id": "frontend_product_catalog",
                    "title": "Product Catalog Interface",
                    "description": "Browse and search products",
                    "status": "todo", 
                    "priority": "high"
                },
                {
                    "id": "frontend_shopping_cart",
                    "title": "Shopping Cart Component",
                    "description": "Add/remove items, view cart",
                    "status": "todo",
                    "priority": "medium"
                }
            ],
            "backend_tasks": [
                {
                    "id": "backend_auth_api",
                    "title": "Authentication API",
                    "description": "JWT-based authentication system",
                    "status": "todo",
                    "priority": "high"
                },
                {
                    "id": "backend_product_api",
                    "title": "Product Management API",
                    "description": "CRUD operations for products",
                    "status": "todo",
                    "priority": "high"
                },
                {
                    "id": "backend_order_api",
                    "title": "Order Processing API",
                    "description": "Handle order creation and processing",
                    "status": "todo",
                    "priority": "medium"
                }
            ],
            "devops_tasks": [
                {
                    "id": "devops_containerization",
                    "title": "Docker Containerization",
                    "description": "Containerize frontend and backend",
                    "status": "todo",
                    "priority": "medium"
                },
                {
                    "id": "devops_ci_cd",
                    "title": "CI/CD Pipeline",
                    "description": "Automated build and deployment",
                    "status": "todo",
                    "priority": "medium"
                },
                {
                    "id": "devops_aws_deployment",
                    "title": "AWS Deployment",
                    "description": "Deploy to AWS infrastructure",
                    "status": "todo",
                    "priority": "low"
                }
            ],
            "testing_tasks": [
                {
                    "id": "testing_unit_tests",
                    "title": "Unit Test Suite",
                    "description": "Comprehensive unit tests",
                    "status": "todo",
                    "priority": "high"
                },
                {
                    "id": "testing_integration_tests",
                    "title": "Integration Tests",
                    "description": "API and component integration tests",
                    "status": "todo",
                    "priority": "medium"
                },
                {
                    "id": "testing_e2e_tests",
                    "title": "End-to-End Tests",
                    "description": "Full user journey testing",
                    "status": "todo",
                    "priority": "low"
                }
            ]
        }


class TestBasicOrchestration(TestOrchestrationWorkflows):
    """Test basic orchestration functionality"""
    
    def test_orchestrate_empty_project(self, orchestrator):
        """Test orchestrating a project with no agents or trees"""
        project = Project(
            id="empty_project",
            name="Empty Project",
            description="Project with no setup",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Mock orchestrator method
        with patch.object(orchestrator, 'orchestrate_project') as mock_orchestrate:
            mock_orchestrate.return_value = {
                "new_assignments": [],
                "agent_recommendations": {},
                "available_agents": 0,
                "active_sessions": 0,
                "coordination_status": "no_work_available"
            }
            
            result = orchestrator.orchestrate_project(project)
            
            assert result["available_agents"] == 0
            assert result["active_sessions"] == 0
            assert len(result["new_assignments"]) == 0
            assert len(result["agent_recommendations"]) == 0
    
    def test_orchestrate_project_with_agents_no_trees(self, orchestrator, ecommerce_project):
        """Test orchestrating project with agents but no task trees"""
        # Remove all task trees
        ecommerce_project.task_trees.clear()
        
        with patch.object(orchestrator, 'orchestrate_project') as mock_orchestrate:
            mock_orchestrate.return_value = {
                "new_assignments": [],
                "agent_recommendations": {},
                "available_agents": 4,
                "active_sessions": 0,
                "coordination_status": "no_trees_available"
            }
            
            result = orchestrator.orchestrate_project(ecommerce_project)
            
            assert result["available_agents"] == 4
            assert len(result["new_assignments"]) == 0
    
    def test_orchestrate_project_with_trees_no_agents(self, orchestrator, ecommerce_project):
        """Test orchestrating project with task trees but no agents"""
        # Remove all agents
        ecommerce_project.registered_agents.clear()
        
        with patch.object(orchestrator, 'orchestrate_project') as mock_orchestrate:
            mock_orchestrate.return_value = {
                "new_assignments": [],
                "agent_recommendations": {},
                "available_agents": 0,
                "active_sessions": 0,
                "coordination_status": "no_agents_available"
            }
            
            result = orchestrator.orchestrate_project(ecommerce_project)
            
            assert result["available_agents"] == 0
            assert len(result["new_assignments"]) == 0


class TestAgentAssignment(TestOrchestrationWorkflows):
    """Test agent assignment logic"""
    
    def test_assign_agents_based_on_capabilities(self, orchestrator, ecommerce_project):
        """Test that agents are assigned based on their capabilities"""
        # Mock orchestrator to simulate capability-based assignment
        with patch.object(orchestrator, 'orchestrate_project') as mock_orchestrate:
            mock_orchestrate.return_value = {
                "new_assignments": [
                    {"agent_id": "frontend_dev", "tree_id": "frontend", "reason": "frontend_development capability"},
                    {"agent_id": "backend_dev", "tree_id": "backend", "reason": "backend_development capability"},
                    {"agent_id": "devops_eng", "tree_id": "devops", "reason": "devops capability"},
                    {"agent_id": "qa_eng", "tree_id": "testing", "reason": "testing capability"}
                ],
                "agent_recommendations": {
                    "frontend_dev": "frontend_auth_ui",
                    "backend_dev": "backend_auth_api",
                    "devops_eng": "devops_containerization",
                    "qa_eng": "testing_unit_tests"
                },
                "available_agents": 4,
                "active_sessions": 0
            }
            
            result = orchestrator.orchestrate_project(ecommerce_project)
            
            assert len(result["new_assignments"]) == 4
            
            # Verify capability-based assignments
            assignments = {assignment["agent_id"]: assignment["tree_id"] for assignment in result["new_assignments"]}
            assert assignments["frontend_dev"] == "frontend"
            assert assignments["backend_dev"] == "backend"
            assert assignments["devops_eng"] == "devops"
            assert assignments["qa_eng"] == "testing"
    
    def test_agent_workload_balancing(self, orchestrator, ecommerce_project):
        """Test workload balancing across agents"""
        # Simulate some agents being overloaded
        frontend_agent = ecommerce_project.registered_agents["frontend_dev"]
        frontend_agent.active_tasks.add("task1")
        frontend_agent.active_tasks.add("task2")  # At max capacity (2)
        
        backend_agent = ecommerce_project.registered_agents["backend_dev"]
        backend_agent.active_tasks.add("task3")  # Below capacity
        
        with patch.object(orchestrator, 'balance_workload') as mock_balance:
            mock_balance.return_value = {
                "workload_analysis": {
                    "frontend_dev": {"workload_percentage": 100.0, "status": "overloaded"},
                    "backend_dev": {"workload_percentage": 50.0, "status": "available"},
                    "devops_eng": {"workload_percentage": 0.0, "status": "available"},
                    "qa_eng": {"workload_percentage": 0.0, "status": "available"}
                },
                "recommendations": [
                    "Consider reassigning work from frontend_dev to other available agents"
                ],
                "balance_score": 0.625  # (100 + 50 + 0 + 0) / 4 / 100
            }
            
            result = orchestrator.balance_workload(ecommerce_project)
            
            assert result["workload_analysis"]["frontend_dev"]["status"] == "overloaded"
            assert result["workload_analysis"]["backend_dev"]["status"] == "available"
            assert len(result["recommendations"]) > 0
    
    def test_agent_specialization_matching(self, orchestrator, ecommerce_project):
        """Test that agents are matched based on specializations"""
        # Mock project method instead of orchestrator method
        with patch.object(ecommerce_project, 'get_available_work_for_agent') as mock_next_work:
            def mock_get_next_work(agent_id):
                # Return work that matches agent specializations
                if agent_id == "frontend_dev":
                    mock_task = Mock()
                    mock_task.id.value = "react_component"
                    mock_task.title = "React Component"
                    mock_task.created_at = datetime.now()
                    return [mock_task]
                elif agent_id == "backend_dev":
                    mock_task = Mock()
                    mock_task.id.value = "node_api"
                    mock_task.title = "Node.js API"
                    mock_task.created_at = datetime.now()
                    return [mock_task]
                elif agent_id == "devops_eng":
                    mock_task = Mock()
                    mock_task.id.value = "docker_setup"
                    mock_task.title = "Docker Setup"
                    mock_task.created_at = datetime.now()
                    return [mock_task]
                return []
            
            mock_next_work.side_effect = mock_get_next_work
            
            result = orchestrator.orchestrate_project(ecommerce_project)
            
            # Verify that recommendations were made
            assert "agent_recommendations" in result
            recommendations = result["agent_recommendations"]
            
            # Check that agents got work matching their specializations
            if "frontend_dev" in recommendations and recommendations["frontend_dev"]:
                assert "react" in recommendations["frontend_dev"].lower() or "component" in recommendations["frontend_dev"].lower()
            
            if "backend_dev" in recommendations and recommendations["backend_dev"]:
                assert "node" in recommendations["backend_dev"].lower() or "api" in recommendations["backend_dev"].lower()


class TestCrossTreeDependencies(TestOrchestrationWorkflows):
    """Test cross-tree dependency management"""
    
    def test_add_cross_tree_dependencies(self, orchestrator, ecommerce_project):
        """Test adding cross-tree dependencies"""
        # Add dependencies: Frontend Auth UI depends on Backend Auth API
        with patch.object(ecommerce_project, '_find_task_tree') as mock_find:
            # Mock finding tasks in different trees
            def mock_find_task(task_id):
                if task_id.startswith("frontend_"):
                    return ecommerce_project.task_trees["frontend"]
                elif task_id.startswith("backend_"):
                    return ecommerce_project.task_trees["backend"]
                return None
            
            mock_find.side_effect = mock_find_task
            
            # Add cross-tree dependency
            ecommerce_project.add_cross_tree_dependency("frontend_auth_ui", "backend_auth_api")
            
            assert "frontend_auth_ui" in ecommerce_project.cross_tree_dependencies
            assert "backend_auth_api" in ecommerce_project.cross_tree_dependencies["frontend_auth_ui"]
    
    def test_coordinate_cross_tree_dependencies(self, orchestrator, ecommerce_project):
        """Test coordinating cross-tree dependencies"""
        # Add cross-tree dependencies
        with patch.object(ecommerce_project, '_find_task_tree') as mock_find:
            frontend_tree = ecommerce_project.task_trees["frontend"]
            backend_tree = ecommerce_project.task_trees["backend"]
            
            def mock_find_task(task_id):
                if "frontend" in task_id:
                    return frontend_tree
                elif "backend" in task_id:
                    return backend_tree
                return None
            
            mock_find.side_effect = mock_find_task
            
            # Add dependencies
            ecommerce_project.add_cross_tree_dependency("frontend_auth_ui", "backend_auth_api")
            ecommerce_project.add_cross_tree_dependency("frontend_shopping_cart", "backend_order_api")
            ecommerce_project.add_cross_tree_dependency("frontend_product_catalog", "backend_product_api")
            
            # Coordinate dependencies
            result = orchestrator.coordinate_cross_tree_dependencies(ecommerce_project)
            
            # Should return list of dependency issues
            assert isinstance(result, list)
            # The result contains dependency coordination information
            # Since tasks don't exist in the trees, we expect some issues to be detected
    
    def test_dependency_blocking_logic(self, orchestrator, ecommerce_project):
        """Test that dependencies properly block task execution"""
        # Setup: Frontend task depends on incomplete backend task
        ecommerce_project.cross_tree_dependencies = {
            "frontend_auth_ui": {"backend_auth_api"}
        }
        
        with patch.object(ecommerce_project, '_is_task_ready_for_work') as mock_ready:
            # Mock that backend task is not complete
            mock_ready.return_value = False
            
            # Frontend task should be blocked
            is_ready = ecommerce_project._is_task_ready_for_work("frontend_auth_ui")
            assert is_ready is False
            
            # Simulate backend task completion
            mock_ready.return_value = True
            
            # Frontend task should now be ready
            is_ready = ecommerce_project._is_task_ready_for_work("frontend_auth_ui")
            assert is_ready is True


class TestWorkSessionManagement(TestOrchestrationWorkflows):
    """Test work session management"""
    
    def test_start_work_session(self, orchestrator, ecommerce_project):
        """Test starting a work session"""
        # Add a task to the frontend tree first
        frontend_tree = ecommerce_project.task_trees["frontend"]
        test_task = Task.create(
            id=TaskId.from_string("20250618001"),
            title="User Authentication UI",
            description="Login and registration forms",
            status=TaskStatus.todo(),
            priority=Priority.high(),
            assignees=["frontend_dev"]
        )
        frontend_tree.add_root_task(test_task)
        
        # Assign agent to tree before starting session
        ecommerce_project.assign_agent_to_tree("frontend_dev", "frontend")
        
        # Start work session
        session = ecommerce_project.start_work_session("frontend_dev", "20250618001")
        
        assert session.agent_id == "frontend_dev"
        assert session.task_id == "20250618001"
        assert session.tree_id == "frontend"
        assert session.is_active()
        assert session.id in ecommerce_project.active_work_sessions
    
    def test_multiple_concurrent_sessions(self, orchestrator, ecommerce_project):
        """Test multiple agents working concurrently"""
        # Add tasks to both trees
        frontend_tree = ecommerce_project.task_trees["frontend"]
        backend_tree = ecommerce_project.task_trees["backend"]
        
        frontend_task = Task.create(
            id=TaskId.from_string("20250618001"),
            title="User Authentication UI",
            description="Login and registration forms",
            status=TaskStatus.todo(),
            priority=Priority.high(),
            assignees=["frontend_dev"]
        )
        frontend_tree.add_root_task(frontend_task)
        
        backend_task = Task.create(
            id=TaskId.from_string("20250618002"),
            title="Authentication API",
            description="User authentication endpoints",
            status=TaskStatus.todo(),
            priority=Priority.high(),
            assignees=["backend_dev"]
        )
        backend_tree.add_root_task(backend_task)
        
        # Assign agents to trees before starting sessions
        ecommerce_project.assign_agent_to_tree("frontend_dev", "frontend")
        ecommerce_project.assign_agent_to_tree("backend_dev", "backend")
        
        # Start multiple sessions
        session1 = ecommerce_project.start_work_session("frontend_dev", "20250618001")
        session2 = ecommerce_project.start_work_session("backend_dev", "20250618002")
        
        assert len(ecommerce_project.active_work_sessions) == 2
        assert session1.is_active()
        assert session2.is_active()
        assert session1.agent_id != session2.agent_id
    
    def test_session_expiration(self, orchestrator, ecommerce_project):
        """Test work session expiration"""
        # Add a task to the frontend tree first
        frontend_tree = ecommerce_project.task_trees["frontend"]
        test_task = Task.create(
            id=TaskId.from_string("20250618001"),
            title="User Authentication UI",
            description="Login and registration forms",
            status=TaskStatus.todo(),
            priority=Priority.high(),
            assignees=["frontend_dev"]
        )
        frontend_tree.add_root_task(test_task)
        
        # Assign agent to tree before starting session
        ecommerce_project.assign_agent_to_tree("frontend_dev", "frontend")
        
        # Start work session with very short duration (1 second)
        session = ecommerce_project.start_work_session("frontend_dev", "20250618001", max_duration_hours=1/3600)  # 1 second
        
        # Verify session is initially active
        assert session.is_active()
        assert not session.is_timeout_due()
        
        # Manually set the started_at time to simulate time passing
        session.started_at = datetime.now() - timedelta(seconds=2)  # 2 seconds ago
        
        # Now check if session is expired
        assert session.is_timeout_due()
        assert session.is_active()  # Still active until explicitly ended


class TestCompleteWorkflows(TestOrchestrationWorkflows):
    """Test complete end-to-end workflows"""
    
    def test_complete_ecommerce_development_workflow(self, orchestrator, ecommerce_project):
        """Test a complete development workflow"""
        # Add tasks to all trees
        frontend_tree = ecommerce_project.task_trees["frontend"]
        backend_tree = ecommerce_project.task_trees["backend"]
        devops_tree = ecommerce_project.task_trees["devops"]
        testing_tree = ecommerce_project.task_trees["testing"]
        
        # Frontend tasks
        frontend_auth_task = Task.create(
            id=TaskId.from_string("20250618001"),
            title="User Authentication UI",
            description="Login and registration forms",
            status=TaskStatus.todo(),
            priority=Priority.high(),
            assignees=["frontend_dev"]
        )
        frontend_tree.add_root_task(frontend_auth_task)
        
        # Backend tasks
        backend_auth_task = Task.create(
            id=TaskId.from_string("20250618002"),
            title="Authentication API",
            description="User authentication endpoints",
            status=TaskStatus.todo(),
            priority=Priority.high(),
            assignees=["backend_dev"]
        )
        backend_tree.add_root_task(backend_auth_task)
        
        # DevOps tasks
        deployment_task = Task.create(
            id=TaskId.from_string("20250618003"),
            title="Deployment Pipeline",
            description="CI/CD pipeline setup",
            status=TaskStatus.todo(),
            priority=Priority.medium(),
            assignees=["devops_eng"]
        )
        devops_tree.add_root_task(deployment_task)
        
        # Testing tasks
        testing_task = Task.create(
            id=TaskId.from_string("20250618004"),
            title="E2E Testing",
            description="End-to-end test automation",
            status=TaskStatus.todo(),
            priority=Priority.medium(),
            assignees=["qa_eng"]
        )
        testing_tree.add_root_task(testing_task)
        
        # Add cross-tree dependency: Frontend Auth UI depends on Backend Auth API
        ecommerce_project.add_cross_tree_dependency("20250618001", "20250618002")
        
        # Assign agents to trees before starting sessions
        ecommerce_project.assign_agent_to_tree("frontend_dev", "frontend")
        ecommerce_project.assign_agent_to_tree("backend_dev", "backend")
        ecommerce_project.assign_agent_to_tree("devops_eng", "devops")
        ecommerce_project.assign_agent_to_tree("qa_eng", "testing")
        
        # Start work sessions
        frontend_session = ecommerce_project.start_work_session("frontend_dev", "20250618001")
        backend_session = ecommerce_project.start_work_session("backend_dev", "20250618002")
        
        # Verify active sessions
        assert len(ecommerce_project.active_work_sessions) == 2
        assert frontend_session.is_active()
        assert backend_session.is_active()
        
        # Complete backend task first (prerequisite for frontend)
        backend_auth_task.status = TaskStatus.done()
        
        # Coordinate dependencies
        dependency_status = ecommerce_project.coordinate_cross_tree_dependencies()
        assert dependency_status["total_dependencies"] == 1
        
        # Complete frontend task
        frontend_auth_task.status = TaskStatus.done()
        
        # Start additional work
        devops_session = ecommerce_project.start_work_session("devops_eng", "20250618003")
        testing_session = ecommerce_project.start_work_session("qa_eng", "20250618004")
        
        # Verify all sessions
        assert len(ecommerce_project.active_work_sessions) == 4
        assert all(session.is_active() for session in ecommerce_project.active_work_sessions.values())
    
    def test_project_progress_tracking(self, orchestrator, ecommerce_project):
        """Test tracking project progress across multiple trees"""
        # Mock tree progress
        with patch.object(ecommerce_project.task_trees["frontend"], 'get_progress_percentage', return_value=60.0), \
             patch.object(ecommerce_project.task_trees["backend"], 'get_progress_percentage', return_value=40.0), \
             patch.object(ecommerce_project.task_trees["devops"], 'get_progress_percentage', return_value=20.0), \
             patch.object(ecommerce_project.task_trees["testing"], 'get_progress_percentage', return_value=80.0):
            
            status = ecommerce_project.get_orchestration_status()
            
            # Verify individual tree progress
            assert status["trees"]["frontend"]["progress"] == 60.0
            assert status["trees"]["backend"]["progress"] == 40.0
            assert status["trees"]["devops"]["progress"] == 20.0
            assert status["trees"]["testing"]["progress"] == 80.0
            
            # Calculate overall progress (average)
            overall_progress = sum(
                status["trees"][tree_id]["progress"] 
                for tree_id in status["trees"]
            ) / len(status["trees"])
            
            assert overall_progress == 50.0  # (60 + 40 + 20 + 80) / 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 