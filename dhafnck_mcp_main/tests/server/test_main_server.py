import pytest
from unittest.mock import patch, Mock
import logging

# Import server creation and main functions from both server implementations
from fastmcp.task_management.interface.ddd_mcp_server import main as ddd_main, create_mcp_server as create_ddd_server
from fastmcp.server.main_server import main as main_server_main, create_main_server
from fastmcp import FastMCP

@pytest.mark.server
class TestMCPServers:
    """Consolidated tests for MCP server main functions"""

    @pytest.mark.unit
    @pytest.mark.interface
    def test_create_ddd_mcp_server(self):
        """Test that the DDD-based MCP server is created correctly."""
        server = create_ddd_server()
        assert isinstance(server, FastMCP)
        assert hasattr(server, "run")
        assert server.name == "Task Management DDD"

    @pytest.mark.unit
    @pytest.mark.interface
    def test_ddd_mcp_server_main_function_error_handling(self):
        """Test that ddd_mcp_server.main handles runtime errors gracefully."""
        mock_mcp_instance = Mock()
        mock_mcp_instance.run.side_effect = Exception("Test server crash")

        with patch('fastmcp.task_management.interface.ddd_mcp_server.create_mcp_server', return_value=mock_mcp_instance), \
             patch('logging.error') as mock_log_error:
            
            with pytest.raises(Exception, match="Test server crash"):
                ddd_main()
            
            mock_log_error.assert_called_once()
            # The logger formats the message as "Server error: {e}"
            assert "Server error: Test server crash" in mock_log_error.call_args[0][0]

    @pytest.mark.unit
    def test_create_main_server(self):
        """Test that the main FastMCP server is created correctly."""
        server = create_main_server()
        assert isinstance(server, FastMCP)
        assert server.name == "FastMCP Server with Task Management"

    @pytest.mark.unit
    def test_main_server_main_function_error_handling(self):
        """Test that main_server.main handles runtime errors gracefully."""
        mock_mcp_instance = Mock()
        mock_mcp_instance.run.side_effect = Exception("Test server crash")
        
        with patch('fastmcp.server.main_server.create_main_server', return_value=mock_mcp_instance), \
             patch('logging.error') as mock_log_error:
            
            with pytest.raises(Exception, match="Test server crash"):
                main_server_main()
            
            mock_log_error.assert_called_once()
            assert "Server error: Test server crash" in mock_log_error.call_args[0][0]

    @pytest.mark.unit
    @pytest.mark.interface
    def test_ddd_main_keyboard_interrupt(self):
        """Test that ddd_mcp_server.main handles KeyboardInterrupt."""
        mock_mcp_instance = Mock()
        mock_mcp_instance.run.side_effect = KeyboardInterrupt()

        with patch('fastmcp.task_management.interface.ddd_mcp_server.create_mcp_server', return_value=mock_mcp_instance), \
             patch('logging.info') as mock_log_info:
            
            # main should catch KeyboardInterrupt and exit gracefully
            ddd_main()
            
            # Check for the specific log message
            mock_log_info.assert_any_call("Server stopped by user")

    @pytest.mark.unit
    def test_main_server_keyboard_interrupt(self):
        """Test that main_server.main handles KeyboardInterrupt."""
        mock_mcp_instance = Mock()
        mock_mcp_instance.run.side_effect = KeyboardInterrupt()
        
        with patch('fastmcp.server.main_server.create_main_server', return_value=mock_mcp_instance), \
             patch('logging.info') as mock_log_info:
            
            main_server_main()
            
            mock_log_info.assert_any_call("Server stopped by user") 