"""
Unit Test: MCP Tools Functionality (Simplified) - MIGRATED
Task 1.2 - MCP Tools Registration Testing
Duration: 1-2 minutes
"""

import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

# Use the new consolidated tools
from fastmcp.task_management.interface.consolidated_mcp_tools_v2 import ConsolidatedMCPToolsV2

class TestMCPToolsSimple:
    """Simplified test cases for MCP Tools functionality."""
    
    @pytest.fixture
    def tools(self):
        """Fixture to create a mocked instance of ConsolidatedMCPToolsV2"""
        with patch('task_mcp.interface.consolidated_mcp_tools_v2.JsonTaskRepository'), \
             patch('task_mcp.interface.consolidated_mcp_tools_v2.FileAutoRuleGenerator'), \
             patch('task_mcp.interface.consolidated_mcp_tools_v2.TaskApplicationService'), \
             patch('task_mcp.interface.consolidated_mcp_tools_v2.CursorRulesTools'):
            
            yield ConsolidatedMCPToolsV2()

    @pytest.mark.unit
    @pytest.mark.mcp
    def test_mcp_tools_can_be_instantiated(self, tools):
        """Test that ConsolidatedMCPToolsV2 can be instantiated."""
        assert tools is not None
        assert hasattr(tools, 'register_tools')
        assert hasattr(tools, '_task_app_service')
        assert hasattr(tools, '_task_repository')
        assert hasattr(tools, '_auto_rule_generator')
    
    @pytest.mark.unit
    @pytest.mark.mcp
    def test_mcp_tools_has_required_dependencies(self, tools):
        """Test that ConsolidatedMCPToolsV2 has all required dependencies."""
        # Check that internal services are properly initialized
        assert tools._task_repository is not None
        assert tools._auto_rule_generator is not None
        assert tools._task_app_service is not None
        
        # Check that task service has required methods (mocked)
        assert hasattr(tools._task_app_service, 'create_task')
        assert hasattr(tools._task_app_service, 'get_task')
        assert hasattr(tools._task_app_service, 'list_tasks')
        assert hasattr(tools._task_app_service, 'update_task')
        assert hasattr(tools._task_app_service, 'delete_task')
        assert hasattr(tools._task_app_service, 'search_tasks')
    
    @pytest.mark.unit
    @pytest.mark.mcp
    def test_mcp_tools_registration_process(self, tools):
        """Test that MCP tools can register with a FastMCP server."""
        # Create mock FastMCP server
        mock_server = Mock()
        mock_server.tool = Mock(return_value=lambda f: f) # Mock decorator
        
        # Test registration (should not raise exceptions)
        tools.register_tools(mock_server)
        
        # Verify that tool decorator was called
        assert mock_server.tool.called
    
    @pytest.mark.unit
    @pytest.mark.mcp
    def test_task_service_basic_functionality(self, tools):
        """Test that the task service has basic functionality."""
        from fastmcp.task_management.application.dtos.task_dto import CreateTaskRequest
        
        # Test that we can create a task request
        request = CreateTaskRequest(
            title="Test Task",
            description="Test Description",
            priority="medium",
            assignees=["qa_engineer"]
        )
        
        assert request is not None
        assert request.title == "Test Task"
        assert request.description == "Test Description"
        assert request.priority == "medium"
        # The logic for adding functional_tester_agent is inside the use case, not the DTO
        assert "@functional_tester_agent" in request.assignees
    
    @pytest.mark.unit
    @pytest.mark.mcp
    def test_repository_basic_functionality(self, tools):
        """Test that the repository has basic functionality."""
        repository = tools._task_repository
        
        # Test that repository has required methods (mocked)
        assert hasattr(repository, 'find_by_id')
        assert hasattr(repository, 'find_all')
        assert hasattr(repository, 'save')
        assert hasattr(repository, 'delete')
        assert hasattr(repository, 'search')
        assert hasattr(repository, 'get_next_id')
        
    @pytest.mark.unit
    @pytest.mark.mcp
    def test_auto_rule_generator_basic_functionality(self, tools):
        """Test that the auto rule generator has basic functionality."""
        auto_rule_gen = tools._auto_rule_generator
        
        # Test that auto rule generator has required methods
        assert hasattr(auto_rule_gen, 'generate_rules_for_task')
        
        # Auto rule generator should be callable
        assert auto_rule_gen is not None
 