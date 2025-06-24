"""Tests for Consolidated MCP Tools v2 (Updated from old MCPTaskTools)"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


import pytest
import tempfile
import os
import shutil
from unittest.mock import Mock, patch

# Updated import to use consolidated v2 tools
from fastmcp.task_management.interface.consolidated_mcp_tools import ConsolidatedMCPTools


class TestConsolidatedMCPTools:
    """Test consolidated MCP tools v2 functionality (migrated from old MCPTaskTools tests)"""
    
    @pytest.fixture
    def temp_projects_file(self):
        """Create a temporary projects file for testing"""
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, 'test_mcp_tools_projects.json')
        
        yield temp_file
        
        # Cleanup after test
        if os.path.exists(temp_file):
            os.remove(temp_file)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mcp_tools(self, temp_projects_file):
        """Create ConsolidatedMCPTools instance with mocked dependencies and isolated files"""
        with patch('fastmcp.task_management.interface.consolidated_mcp_tools.JsonTaskRepository') as mock_repo_class, \
             patch('fastmcp.task_management.interface.consolidated_mcp_tools.FileAutoRuleGenerator') as mock_generator_class, \
             patch('fastmcp.task_management.interface.consolidated_mcp_tools.TaskApplicationService') as mock_service_class, \
             patch('fastmcp.task_management.interface.consolidated_mcp_tools.CursorRulesTools') as mock_cursor_class:
            
            # Configure mock instances
            mock_repo = Mock()
            mock_generator = Mock()
            mock_service = Mock()
            mock_cursor = Mock()
            
            mock_repo_class.return_value = mock_repo
            mock_generator_class.return_value = mock_generator
            mock_service_class.return_value = mock_service
            mock_cursor_class.return_value = mock_cursor
            
            # Create tools with isolated projects file
            return ConsolidatedMCPTools(projects_file_path=temp_projects_file)
    
    def test_mcp_tools_initialization(self, mcp_tools):
        """Test MCP tools initialization"""
        assert mcp_tools is not None
        
        # Verify all required components exist
        assert hasattr(mcp_tools, '_task_repository')
        assert hasattr(mcp_tools, '_auto_rule_generator')
        assert hasattr(mcp_tools, '_task_app_service')
        assert hasattr(mcp_tools, 'register_tools')
    
    def test_task_service_functionality(self, mcp_tools):
        """Test task service functionality"""
        # Verify task service exists and has required methods
        assert hasattr(mcp_tools, '_task_app_service')
        
        # Test service is properly connected
        assert mcp_tools._task_app_service is not None
    
    def test_repository_functionality(self, mcp_tools):
        """Test repository functionality"""
        repository = mcp_tools._task_repository
        
        # Verify repository exists
        assert repository is not None
    
    def test_auto_rule_generator_functionality(self, mcp_tools):
        """Test auto rule generator functionality"""
        generator = mcp_tools._auto_rule_generator
        
        # Verify generator exists
        assert generator is not None
    
    def test_register_tools_method(self, mcp_tools):
        """Test that register_tools method works"""
        # Create mock FastMCP instance
        mock_mcp = Mock()
        mock_mcp.tool = Mock(return_value=lambda f: f)  # Mock the decorator
        
        # Should not raise an exception
        mcp_tools.register_tools(mock_mcp)
        
        # Verify tools were registered
        assert mock_mcp.tool.called
        # Should have registered at least 3 main tools
        assert mock_mcp.tool.call_count >= 3
    
    def test_application_service_integration(self, mcp_tools):
        """Test application service integration"""
        service = mcp_tools._task_app_service
        
        # Verify service exists and is connected to dependencies
        assert service is not None
    
    def test_multi_agent_tools_integration_isolated(self, mcp_tools, temp_projects_file):
        """Test multi-agent tools integration with proper isolation"""
        # Verify multi-agent tools exist
        assert hasattr(mcp_tools, '_multi_agent_tools')
        assert mcp_tools._multi_agent_tools is not None
        
        # Test basic multi-agent functionality with isolated data
        result = mcp_tools._multi_agent_tools.create_project("test_isolated_mcp", "Test Isolated MCP Project")
        assert result["success"] is True
        
        # Verify the test data is in the temporary file, not production
        assert os.path.exists(temp_projects_file)
        
        # Verify production file is not affected
        production_file = os.path.join(os.path.dirname(__file__), '../../../.cursor/rules/brain/projects.json')
        if os.path.exists(production_file):
            import json
            with open(production_file, 'r') as f:
                prod_data = json.load(f)
            assert "test_isolated_mcp" not in prod_data, "Test data leaked into production file!"
    
    def test_cursor_rules_integration(self, mcp_tools):
        """Test cursor rules tools integration"""
        # Verify cursor rules tools exist
        assert hasattr(mcp_tools, '_cursor_rules_tools')
        assert mcp_tools._cursor_rules_tools is not None
    
    def test_helper_methods_exist(self, mcp_tools):
        """Test that all helper methods exist"""
        helper_methods = [
            '_handle_core_task_operations',
            '_handle_complete_task',
            '_handle_list_tasks',
            '_handle_search_tasks',
            '_handle_do_next',
            '_handle_subtask_operations',
            '_handle_dependency_operations'
        ]
        
        for method_name in helper_methods:
            assert hasattr(mcp_tools, method_name)
            assert callable(getattr(mcp_tools, method_name)) 