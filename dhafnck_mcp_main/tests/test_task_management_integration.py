"""End-to-End Tests for Task Management Integration"""

import pytest
import asyncio
import tempfile
import json
import os
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch


# Global fixtures available to all test classes
@pytest.fixture
def temp_project_dir():
    """Create temporary project directory for testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_fastmcp_server():
    """Mock FastMCP server for testing tool registration"""
    class MockFastMCP:
        def __init__(self):
            self.tools = {}
            self.name = "Test Server"
        
        def tool(self):
            def decorator(func):
                self.tools[func.__name__] = func
                return func
            return decorator
    
    return MockFastMCP()


@pytest.fixture
def dhafnck_mcp_tools(temp_project_dir):
    """Initialize ConsolidatedMCPToolsV2 with test configuration"""
    # Import the module first, before any mocking
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
    
    try:
        from fastmcp.task_management.interface.consolidated_mcp_tools_v2 import ConsolidatedMCPToolsV2
        from fastmcp.task_management.infrastructure import InMemoryTaskRepository, FileAutoRuleGenerator
        
        # Create test projects file
        projects_file = temp_project_dir / "projects.json"
        projects_file.write_text("{}")
        
        # Use InMemoryTaskRepository for test isolation
        task_repo = InMemoryTaskRepository()
        auto_rule_gen = FileAutoRuleGenerator()
        
        return ConsolidatedMCPToolsV2(
            task_repository=task_repo,
            auto_rule_generator=auto_rule_gen,
            projects_file_path=str(projects_file)
        )
    except ImportError as e:
        pytest.skip(f"Could not import ConsolidatedMCPToolsV2: {e}")


class TestTaskManagementIntegration:
    """Comprehensive end-to-end tests for task management MCP tools integration"""
    pass


class TestCoreTaskManagementTools:
    """Test core task management functionality"""
    
    def test_manage_task_tool_registration(self, mock_fastmcp_server, dhafnck_mcp_tools):
        """Test that manage_task tool is properly registered"""
        dhafnck_mcp_tools.register_tools(mock_fastmcp_server)
        
        assert "manage_task" in mock_fastmcp_server.tools
        assert callable(mock_fastmcp_server.tools["manage_task"])
    
    def test_manage_subtask_tool_registration(self, mock_fastmcp_server, dhafnck_mcp_tools):
        """Test that manage_subtask tool is properly registered"""
        dhafnck_mcp_tools.register_tools(mock_fastmcp_server)
        
        assert "manage_subtask" in mock_fastmcp_server.tools
        assert callable(mock_fastmcp_server.tools["manage_subtask"])
    
    def test_task_creation_workflow(self, mock_fastmcp_server, dhafnck_mcp_tools):
        """Test complete task creation workflow"""
        dhafnck_mcp_tools.register_tools(mock_fastmcp_server)
        
        # Test task creation
        create_result = mock_fastmcp_server.tools["manage_task"](
            action="create",
            title="Test Task",
            description="Test Description",
            priority="high",
            assignees=["@coding_agent"]
        )
        
        assert create_result["success"] is True
        assert "task" in create_result
        assert create_result["task"]["title"] == "Test Task"
        
        # Test task retrieval
        task_id = create_result["task"]["id"]
        get_result = mock_fastmcp_server.tools["manage_task"](
            action="get",
            task_id=task_id
        )
        
        assert get_result["success"] is True
        assert get_result["task"]["id"] == task_id
    
    def test_subdhafnck_mcp_workflow(self, mock_fastmcp_server, dhafnck_mcp_tools):
        """Test subtask creation and management"""
        dhafnck_mcp_tools.register_tools(mock_fastmcp_server)
        
        # Create parent task
        task_result = mock_fastmcp_server.tools["manage_task"](
            action="create",
            title="Parent Task",
            description="Parent task for subtask testing"
        )
        
        task_id = task_result["task"]["id"]
        
        # Add subtask
        subtask_result = mock_fastmcp_server.tools["manage_subtask"](
            action="add_subtask",
            task_id=task_id,
            subtask_data={"title": "Test Subtask", "description": "Test subtask description"}
        )
        
        assert subtask_result["success"] is True
        assert "result" in subtask_result
        assert "subtask" in subtask_result["result"]
        assert subtask_result["result"]["subtask"]["title"] == "Test Subtask"
        
        # List subtasks
        list_result = mock_fastmcp_server.tools["manage_subtask"](
            action="list_subtasks",
            task_id=task_id
        )
        
        assert list_result["success"] is True
        assert "result" in list_result
        assert len(list_result["result"]) == 1
        assert list_result["result"][0]["title"] == "Test Subtask"


class TestProjectManagementTools:
    """Test project management and orchestration functionality"""
    
    def test_manage_project_tool_registration(self, mock_fastmcp_server, dhafnck_mcp_tools):
        """Test that manage_project tool is properly registered"""
        dhafnck_mcp_tools.register_tools(mock_fastmcp_server)
        
        assert "manage_project" in mock_fastmcp_server.tools
        assert callable(mock_fastmcp_server.tools["manage_project"])
    
    def test_project_creation_workflow(self, mock_fastmcp_server, dhafnck_mcp_tools):
        """Test complete project creation and management workflow"""
        dhafnck_mcp_tools.register_tools(mock_fastmcp_server)
        
        # Create project
        create_result = mock_fastmcp_server.tools["manage_project"](
            action="create",
            project_id="test_project",
            name="Test Project",
            description="Test project description"
        )
        
        assert create_result["success"] is True
        assert create_result["project"]["id"] == "test_project"
        
        # Get project
        get_result = mock_fastmcp_server.tools["manage_project"](
            action="get",
            project_id="test_project"
        )
        
        assert get_result["success"] is True
        assert get_result["project"]["name"] == "Test Project"
        
        # List projects
        list_result = mock_fastmcp_server.tools["manage_project"](
            action="list"
        )
        
        assert list_result["success"] is True
        assert len(list_result["projects"]) >= 1
    
    def test_task_tree_management(self, mock_fastmcp_server, dhafnck_mcp_tools):
        """Test task tree creation and management"""
        dhafnck_mcp_tools.register_tools(mock_fastmcp_server)
        
        # Create project first
        mock_fastmcp_server.tools["manage_project"](
            action="create",
            project_id="tree_test_project",
            name="Tree Test Project"
        )
        
        # Create task tree
        tree_result = mock_fastmcp_server.tools["manage_project"](
            action="create_tree",
            project_id="tree_test_project",
            tree_id="feature_tree",
            tree_name="Feature Development Tree",
            tree_description="Tree for feature development tasks"
        )
        
        assert tree_result["success"] is True
        assert tree_result["tree"]["id"] == "feature_tree"
        
        # Get tree status
        status_result = mock_fastmcp_server.tools["manage_project"](
            action="get_tree_status",
            project_id="tree_test_project",
            tree_id="feature_tree"
        )
        
        assert status_result["success"] is True
        assert status_result["tree"]["id"] == "feature_tree"


class TestMultiAgentCoordinationTools:
    """Test multi-agent coordination functionality"""
    
    def test_manage_agent_tool_registration(self, mock_fastmcp_server, dhafnck_mcp_tools):
        """Test that manage_agent tool is properly registered"""
        dhafnck_mcp_tools.register_tools(mock_fastmcp_server)
        
        assert "manage_agent" in mock_fastmcp_server.tools
        assert callable(mock_fastmcp_server.tools["manage_agent"])
    
    def test_call_agent_tool_registration(self, mock_fastmcp_server, dhafnck_mcp_tools):
        """Test that call_agent tool is properly registered"""
        dhafnck_mcp_tools.register_tools(mock_fastmcp_server)
        
        assert "call_agent" in mock_fastmcp_server.tools
        assert callable(mock_fastmcp_server.tools["call_agent"])
    
    def test_agent_registration_workflow(self, mock_fastmcp_server, dhafnck_mcp_tools):
        """Test agent registration and assignment workflow"""
        dhafnck_mcp_tools.register_tools(mock_fastmcp_server)
        
        # Create project
        mock_fastmcp_server.tools["manage_project"](
            action="create",
            project_id="agent_test_project",
            name="Agent Test Project"
        )
        
        # Register agent
        register_result = mock_fastmcp_server.tools["manage_agent"](
            action="register",
            project_id="agent_test_project",
            agent_id="test_coding_agent",
            name="Test Coding Agent",
            call_agent="@coding_agent"
        )
        
        assert register_result["success"] is True
        
        # List agents
        list_result = mock_fastmcp_server.tools["manage_agent"](
            action="list",
            project_id="agent_test_project"
        )
        
        assert list_result["success"] is True
        assert len(list_result["agents"]) >= 1
        
        # Assign agent to tree
        assign_result = mock_fastmcp_server.tools["manage_agent"](
            action="assign",
            project_id="agent_test_project",
            agent_id="test_coding_agent",
            tree_id="main"
        )
        
        assert assign_result["success"] is True


class TestRulesAndContextManagementTools:
    """Test rules and context management functionality"""
    
    def test_cursor_rules_tools_registration(self, mock_fastmcp_server, dhafnck_mcp_tools):
        """Test that cursor rules tools are properly registered"""
        dhafnck_mcp_tools.register_tools(mock_fastmcp_server)
        
        expected_tools = [
            "update_auto_rule",
            "validate_rules", 
            "manage_cursor_rules",
            "regenerate_auto_rule",
            "validate_tasks_json"
        ]
        
        for tool_name in expected_tools:
            assert tool_name in mock_fastmcp_server.tools
            assert callable(mock_fastmcp_server.tools[tool_name])


class TestIntegrationWorkflows:
    """Test complete integration workflows"""
    
    def test_complete_task_workflow(self, mock_fastmcp_server, dhafnck_mcp_tools):
        """Test complete task management workflow from creation to completion"""
        dhafnck_mcp_tools.register_tools(mock_fastmcp_server)
        
        # Create task
        create_result = mock_fastmcp_server.tools["manage_task"](
            action="create",
            title="Integration Test Task",
            description="Complete workflow test",
            priority="medium",
            assignees=["@coding_agent"],
            labels=["integration", "test"]
        )
        
        task_id = create_result["task"]["id"]
        
        # Add subtasks
        subtask1 = mock_fastmcp_server.tools["manage_subtask"](
            action="add_subtask",
            task_id=task_id,
            subtask_data={"title": "Subtask 1", "description": "First subtask"}
        )
        
        subtask2 = mock_fastmcp_server.tools["manage_subtask"](
            action="add_subtask",
            task_id=task_id,
            subtask_data={"title": "Subtask 2", "description": "Second subtask"}
        )
        
        # Complete subtasks
        mock_fastmcp_server.tools["manage_subtask"](
            action="complete_subtask",
            task_id=task_id,
            subtask_data={"subtask_id": subtask1["result"]["subtask"]["id"]}
        )
    
        mock_fastmcp_server.tools["manage_subtask"](
            action="complete_subtask",
            task_id=task_id,
            subtask_data={"subtask_id": subtask2["result"]["subtask"]["id"]}
        )
        
        # Complete main task
        complete_result = mock_fastmcp_server.tools["manage_task"](
            action="complete",
            task_id=task_id
        )
        
        assert complete_result["success"] is True
        
        # Verify task is completed
        get_result = mock_fastmcp_server.tools["manage_task"](
            action="get",
            task_id=task_id
        )
        
        assert get_result["task"]["status"] == "done"
    
    def test_project_orchestration_workflow(self, mock_fastmcp_server, dhafnck_mcp_tools):
        """Test project orchestration and dashboard functionality"""
        dhafnck_mcp_tools.register_tools(mock_fastmcp_server)
        
        # Create project
        mock_fastmcp_server.tools["manage_project"](
            action="create",
            project_id="orchestration_test",
            name="Orchestration Test Project"
        )
        
        # Register agents
        mock_fastmcp_server.tools["manage_agent"](
            action="register",
            project_id="orchestration_test",
            agent_id="coding_agent",
            name="Coding Agent",
            call_agent="@coding_agent"
        )
        
        # Run orchestration
        orchestrate_result = mock_fastmcp_server.tools["manage_project"](
            action="orchestrate",
            project_id="orchestration_test"
        )
        
        assert orchestrate_result["success"] is True
        
        # Get dashboard
        dashboard_result = mock_fastmcp_server.tools["manage_project"](
            action="dashboard",
            project_id="orchestration_test"
        )
        
        assert dashboard_result["success"] is True
        assert "dashboard" in dashboard_result


class TestErrorHandlingAndEdgeCases:
    """Test error handling and edge cases"""
    
    def test_invalid_task_operations(self, mock_fastmcp_server, dhafnck_mcp_tools):
        """Test error handling for invalid task operations"""
        dhafnck_mcp_tools.register_tools(mock_fastmcp_server)
        
        # Try to get non-existent task
        get_result = mock_fastmcp_server.tools["manage_task"](
            action="get",
            task_id="non_existent_task"
        )
        
        assert get_result["success"] is False
        assert "error" in get_result
    
    def test_invalid_project_operations(self, mock_fastmcp_server, dhafnck_mcp_tools):
        """Test error handling for invalid project operations"""
        dhafnck_mcp_tools.register_tools(mock_fastmcp_server)
        
        # Try to get non-existent project
        get_result = mock_fastmcp_server.tools["manage_project"](
            action="get",
            project_id="non_existent_project"
        )
        
        assert get_result["success"] is False
        assert "error" in get_result
    
    def test_invalid_agent_operations(self, mock_fastmcp_server, dhafnck_mcp_tools):
        """Test error handling for invalid agent operations"""
        dhafnck_mcp_tools.register_tools(mock_fastmcp_server)
        
        # Try to register agent to non-existent project
        register_result = mock_fastmcp_server.tools["manage_agent"](
            action="register",
            project_id="non_existent_project",
            agent_id="test_agent",
            name="Test Agent"
        )
        
        assert register_result["success"] is False
        assert "error" in register_result


class TestPerformanceAndScalability:
    """Test performance and scalability aspects"""
    
    def test_bulk_task_operations(self, mock_fastmcp_server, dhafnck_mcp_tools):
        """Test performance with bulk task operations"""
        dhafnck_mcp_tools.register_tools(mock_fastmcp_server)
        
        # Create multiple tasks
        task_ids = []
        for i in range(10):
            result = mock_fastmcp_server.tools["manage_task"](
                action="create",
                title=f"Bulk Task {i}",
                description=f"Bulk task number {i}",
                priority="low"
            )
            task_ids.append(result["task"]["id"])
        
        # List all tasks
        list_result = mock_fastmcp_server.tools["manage_task"](
            action="list",
            limit=20
        )
        
        assert list_result["success"] is True
        assert len(list_result["tasks"]) >= 10
    
    def test_complex_project_structure(self, mock_fastmcp_server, dhafnck_mcp_tools):
        """Test complex project structures with multiple trees and agents"""
        dhafnck_mcp_tools.register_tools(mock_fastmcp_server)
        
        # Create project
        mock_fastmcp_server.tools["manage_project"](
            action="create",
            project_id="complex_project",
            name="Complex Project"
        )
        
        # Create multiple task trees
        tree_names = ["frontend", "backend", "testing", "deployment"]
        for tree_name in tree_names:
            mock_fastmcp_server.tools["manage_project"](
                action="create_tree",
                project_id="complex_project",
                tree_id=tree_name,
                tree_name=f"{tree_name.title()} Tree"
            )
        
        # Register multiple agents
        agent_types = ["coding_agent", "test_agent", "devops_agent"]
        for agent_type in agent_types:
            mock_fastmcp_server.tools["manage_agent"](
                action="register",
                project_id="complex_project",
                agent_id=agent_type,
                name=f"{agent_type.title()}",
                call_agent=f"@{agent_type}"
            )
        
        # Verify project structure
        get_result = mock_fastmcp_server.tools["manage_project"](
            action="get",
            project_id="complex_project"
        )
        
        assert get_result["success"] is True
        assert len(get_result["project"]["task_trees"]) >= 4


# Test fixtures and utilities
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"]) 