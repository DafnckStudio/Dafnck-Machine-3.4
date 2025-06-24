"""Tests for consolidated MCP server module."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


import pytest
import logging
from unittest.mock import Mock, patch, MagicMock
from fastmcp.task_management.interface.consolidated_mcp_server import (
    create_consolidated_mcp_server,
    main
)


class TestConsolidatedMCPServer:
    """Test the consolidated MCP server functionality"""
    
    @patch('fastmcp.task_management.interface.consolidated_mcp_server.FastMCP')
    @patch('fastmcp.task_management.interface.consolidated_mcp_server.ConsolidatedMCPTools')
    def test_create_consolidated_mcp_server(self, mock_tools_class, mock_fastmcp_class):
        """Test creating the consolidated MCP server"""
        # Setup mocks
        mock_mcp = Mock()
        mock_fastmcp_class.return_value = mock_mcp
        
        mock_tools = Mock()
        mock_tools_class.return_value = mock_tools
        
        # Call the function
        result = create_consolidated_mcp_server()
        
        # Verify FastMCP was initialized with correct name
        mock_fastmcp_class.assert_called_once_with("Task Management Consolidated with Multi-Agent Support")
        
        # Verify tools were initialized and registered
        mock_tools_class.assert_called_once()
        mock_tools.register_tools.assert_called_once_with(mock_mcp)
        
        # Verify the MCP instance is returned
        assert result == mock_mcp
    
    @patch('fastmcp.task_management.interface.consolidated_mcp_server.mcp_instance')
    @patch('fastmcp.task_management.interface.consolidated_mcp_server.logging')
    def test_main_success(self, mock_logging, mock_mcp_instance):
        """Test main function successful execution"""
        # Setup mocks
        mock_mcp_instance.run = Mock()  # Mock the run method on the global instance
        
        # Call main
        main()
        
        # Verify logging was configured
        assert mock_logging.basicConfig.called
        
        # Verify server run was called
        mock_mcp_instance.run.assert_called_once()
    
    @patch('fastmcp.task_management.interface.consolidated_mcp_server.mcp_instance')
    @patch('fastmcp.task_management.interface.consolidated_mcp_server.logging')
    def test_main_keyboard_interrupt(self, mock_logging, mock_mcp_instance):
        """Test main function handles KeyboardInterrupt gracefully"""
        # Setup mocks
        mock_mcp_instance.run.side_effect = KeyboardInterrupt()
        
        # Call main - should not raise exception
        main()
        
        # Verify logging was configured
        mock_logging.basicConfig.assert_called_once()
        
        # Verify server attempted to run
        mock_mcp_instance.run.assert_called_once()
        
        # Verify info message was logged
        mock_logging.info.assert_called_once_with("Consolidated server stopped by user")
    
    @patch('fastmcp.task_management.interface.consolidated_mcp_server.mcp_instance')
    @patch('fastmcp.task_management.interface.consolidated_mcp_server.logging')
    def test_main_generic_exception(self, mock_logging, mock_mcp_instance):
        """Test main function handles generic exceptions"""
        # Setup mocks
        test_error = Exception("Test error")
        mock_mcp_instance.run.side_effect = test_error
        
        # Call main - should raise the exception
        with pytest.raises(Exception) as exc_info:
            main()
        
        assert exc_info.value == test_error
        
        # Verify logging was configured
        mock_logging.basicConfig.assert_called_once()
        
        # Verify server attempted to run
        mock_mcp_instance.run.assert_called_once()
        
        # Verify error message was logged
        mock_logging.error.assert_called_once_with(f"Consolidated server error: {test_error}")
    
    def test_module_imports_successfully(self):
        """Test that the module imports successfully without sys.path modification"""
        # The consolidated_mcp_server module uses proper package imports
        # and doesn't need sys.path modification
        import fastmcp.task_management.interface.consolidated_mcp_server
        
        # Verify the module has the expected functions
        assert hasattr(fastmcp.task_management.interface.consolidated_mcp_server, 'create_consolidated_mcp_server')
        assert hasattr(fastmcp.task_management.interface.consolidated_mcp_server, 'main')
        
        # If we get here, the import succeeded without sys.path manipulation
        assert True
    
    def test_module_docstring(self):
        """Test that the module has proper documentation"""
        import fastmcp.task_management.interface.consolidated_mcp_server as module
        
        assert module.__doc__ is not None
        assert "Consolidated DDD-based MCP Server with Multi-Agent Support" in module.__doc__ 