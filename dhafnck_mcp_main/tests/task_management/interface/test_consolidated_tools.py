"""Tests for Consolidated MCP Tools"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


import pytest
import tempfile
import os
from unittest.mock import Mock, patch

# Updated import to use v2
from fastmcp.task_management.interface.consolidated_mcp_tools import ConsolidatedMCPTools


class TestConsolidatedMCPTools:
    """Test consolidated MCP tools functionality"""
    
    @pytest.fixture
    def temp_tasks_file(self):
        """Create a temporary tasks file"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.write('{"tasks": {}, "project_meta": {}}')
        temp_file.close()
        yield temp_file.name
        os.unlink(temp_file.name)
    
    @pytest.fixture
    def consolidated_tools(self, temp_tasks_file):
        """Create ConsolidatedMCPTools instance with mocked dependencies"""
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
            
            tools = ConsolidatedMCPTools()
            return tools
    
    def test_consolidated_tools_initialization(self, consolidated_tools):
        """Test that consolidated tools initialize correctly"""
        assert consolidated_tools is not None
        assert hasattr(consolidated_tools, '_task_repository')
        assert hasattr(consolidated_tools, '_auto_rule_generator')
        assert hasattr(consolidated_tools, '_task_app_service')
        assert hasattr(consolidated_tools, '_cursor_rules_tools')
        assert hasattr(consolidated_tools, '_multi_agent_tools')
    
    def test_register_tools_method_exists(self, consolidated_tools):
        """Test that register_tools method exists"""
        assert hasattr(consolidated_tools, 'register_tools')
        assert callable(getattr(consolidated_tools, 'register_tools'))
    
    def test_helper_methods_exist(self, consolidated_tools):
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
            assert hasattr(consolidated_tools, method_name)
            assert callable(getattr(consolidated_tools, method_name))
    
    def test_tool_registration_works(self, consolidated_tools):
        """Test that tools can be registered without errors"""
        mock_mcp = Mock()
        mock_mcp.tool = Mock(return_value=lambda f: f)  # Mock decorator
        
        # Should not raise an exception
        consolidated_tools.register_tools(mock_mcp)
        
        # Verify that tool decorator was called (indicating tools were registered)
        assert mock_mcp.tool.called
        # Should have at least 3 main tools (manage_project, manage_task, manage_agent)
        assert mock_mcp.tool.call_count >= 3


class TestConsolidatedToolsWithRealFiles:
    """Integration tests using real file system"""
    
    def test_real_file_integration(self):
        """Test that tools work with real file operations"""
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.write('{"tasks": {}, "project_meta": {}}')
        temp_file.close()
        
        try:
            # Test instantiation works with real files
            tools = ConsolidatedMCPTools()
            assert tools is not None
            
            # Verify components are initialized
            assert hasattr(tools, '_task_repository')
            assert hasattr(tools, '_multi_agent_tools')
            
        finally:
            # Clean up
            if os.path.exists(temp_file.name):
                os.unlink(temp_file.name)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 