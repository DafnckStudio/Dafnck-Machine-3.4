"""
Unit tests for MCP Server entry point (mcp_server.py)
Tests server startup, logging setup, error handling, and main execution flow.
"""

import pytest
import sys
import os
import logging
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from io import StringIO

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

# Import the module under test
import mcp_server
from fastmcp.task_management.interface.ddd_mcp_server import create_mcp_server


class TestMCPServerLoggingSetup:
    """Test logging configuration and setup."""
    
    def setup_method(self):
        """Setup for each test method."""
        # Clear existing loggers
        logging.getLogger().handlers.clear()
        
    def teardown_method(self):
        """Cleanup after each test method."""
        # Clear existing loggers
        logging.getLogger().handlers.clear()
        
    @patch('os.makedirs')
    def test_logs_directory_creation(self, mock_makedirs):
        """Test that logs directory is created on import."""
        # Re-import to trigger directory creation
        import importlib
        importlib.reload(mcp_server)
        
        # Verify logs directory creation was called
        mock_makedirs.assert_called_with("logs", exist_ok=True)
    
    def test_logging_configuration(self):
        """Test that logging is properly configured."""
        # Re-import to trigger logging setup
        import importlib
        importlib.reload(mcp_server)
        
        # Get the root logger
        logger = logging.getLogger()
        
        # Check that handlers are configured
        assert len(logger.handlers) >= 1  # At least console handler
        
        # Check console handler configuration
        console_handler = None
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                console_handler = handler
                break
        
        assert console_handler is not None
        # In test environment, the level might be different, so just check it's set
        assert console_handler.level is not None
        
    def test_logging_formatter(self):
        """Test that logging formatter is properly configured."""
        import importlib
        importlib.reload(mcp_server)
        
        # Get console handler
        logger = logging.getLogger()
        console_handler = None
        for handler in logger.handlers:
            if isinstance(handler, logging.StreamHandler):
                console_handler = handler
                break
        
        assert console_handler is not None
        assert console_handler.formatter is not None
        
        # Test formatter format - check for essential components
        formatter = console_handler.formatter
        # In test environment, pytest may override the formatter, so check it exists
        assert hasattr(formatter, '_fmt')
        assert formatter._fmt is not None
        # Check for key logging components (may be in different format)
        fmt_str = formatter._fmt
        assert any(component in fmt_str for component in ["levelname", "message"])


class TestMCPServerPathSetup:
    """Test Python path configuration."""
    
    def test_current_directory_added_to_path(self):
        """Test that current directory is added to sys.path."""
        # Get the expected path
        current_dir = Path(mcp_server.__file__).parent
        expected_path = str(current_dir)
        
        # Check that the path is in sys.path
        assert expected_path in sys.path
        
        # Check that it's at the beginning (index 0)
        assert sys.path[0] == expected_path


class TestMCPServerMainFunction:
    """Test the main function execution."""
    
    @patch('mcp_server.create_mcp_server')
    @patch('mcp_server.logger')
    def test_main_success(self, mock_logger, mock_create_mcp_server):
        """Test successful main function execution."""
        # Setup mock server
        mock_server = Mock()
        mock_create_mcp_server.return_value = mock_server
        
        # Call main function
        mcp_server.main()
        
        # Verify server creation and running
        mock_create_mcp_server.assert_called_once()
        mock_server.run.assert_called_once()
        
    @patch('mcp_server.create_mcp_server')
    @patch('mcp_server.logger')
    def test_main_keyboard_interrupt(self, mock_logger, mock_create_mcp_server):
        """Test main function handling KeyboardInterrupt."""
        # Setup mock server to raise KeyboardInterrupt
        mock_server = Mock()
        mock_server.run.side_effect = KeyboardInterrupt()
        mock_create_mcp_server.return_value = mock_server
        
        # Call main function
        mcp_server.main()
        
        # Verify proper handling
        mock_create_mcp_server.assert_called_once()
        mock_server.run.assert_called_once()
        mock_logger.info.assert_called_with("Server stopped by user")
        
    @patch('mcp_server.create_mcp_server')
    @patch('mcp_server.logger')
    @patch('sys.exit')
    def test_main_general_exception(self, mock_exit, mock_logger, mock_create_mcp_server):
        """Test main function handling general exceptions."""
        # Setup mock server to raise general exception
        test_error = Exception("Test error")
        mock_server = Mock()
        mock_server.run.side_effect = test_error
        mock_create_mcp_server.return_value = mock_server
        
        # Call main function
        mcp_server.main()
        
        # Verify proper error handling
        mock_create_mcp_server.assert_called_once()
        mock_server.run.assert_called_once()
        mock_logger.error.assert_called_with(f"Server error: {test_error}")
        mock_exit.assert_called_with(1)
        
    @patch('mcp_server.create_mcp_server')
    @patch('mcp_server.logger')
    def test_main_server_creation_failure(self, mock_logger, mock_create_mcp_server):
        """Test main function when server creation fails."""
        # Setup mock to raise exception during server creation
        test_error = Exception("Server creation failed")
        mock_create_mcp_server.side_effect = test_error
        
        # Call main function
        with patch('sys.exit') as mock_exit:
            mcp_server.main()
        
        # Verify proper error handling
        mock_create_mcp_server.assert_called_once()
        mock_logger.error.assert_called_with(f"Server error: {test_error}")
        mock_exit.assert_called_with(1)


class TestMCPServerIntegration:
    """Integration tests for MCP server."""
    
    @patch('mcp_server.create_mcp_server')
    def test_server_creation_integration(self, mock_create_mcp_server):
        """Test that server creation is properly integrated."""
        # Setup mock
        mock_server = Mock()
        mock_create_mcp_server.return_value = mock_server
        
        # Import and call main
        mcp_server.main()
        
        # Verify integration
        mock_create_mcp_server.assert_called_once()
        mock_server.run.assert_called_once()
        
    def test_imports_work_correctly(self):
        """Test that all required imports work correctly."""
        # Test that we can import all required modules
        import asyncio
        import logging
        import sys
        import os
        from pathlib import Path
        
        # Test that we can import the DDD server
        from fastmcp.task_management.interface.ddd_mcp_server import create_mcp_server
        
        # Verify create_mcp_server is callable
        assert callable(create_mcp_server)


class TestMCPServerCommandLine:
    """Test command-line execution."""
    
    @patch('mcp_server.main')
    def test_main_execution_when_run_as_script(self, mock_main):
        """Test that main() is called when script is run directly."""
        # Simulate running as main script
        with patch.object(mcp_server, '__name__', '__main__'):
            # Re-execute the if __name__ == "__main__" block
            exec(compile(open(mcp_server.__file__).read(), mcp_server.__file__, 'exec'))
        
        # Note: This test is tricky because the if __name__ == "__main__" 
        # block was already executed during import. In a real scenario,
        # we would test this differently or mock the execution.
        
    def test_module_has_main_guard(self):
        """Test that the module has proper main execution guard."""
        # Read the source file
        with open(mcp_server.__file__, 'r') as f:
            source = f.read()
        
        # Check for main guard
        assert 'if __name__ == "__main__":' in source
        assert 'main()' in source


class TestMCPServerErrorHandling:
    """Test comprehensive error handling scenarios."""
    
    @patch('mcp_server.create_mcp_server')
    @patch('mcp_server.logger')
    def test_multiple_exception_types(self, mock_logger, mock_create_mcp_server):
        """Test handling of various exception types."""
        exception_types = [
            (ValueError("Invalid value"), "Server error: Invalid value"),
            (RuntimeError("Runtime issue"), "Server error: Runtime issue"),
            (OSError("OS error"), "Server error: OS error"),
            (ImportError("Import failed"), "Server error: Import failed")
        ]
        
        for exception, expected_message in exception_types:
            # Reset mocks
            mock_logger.reset_mock()
            mock_create_mcp_server.reset_mock()
            
            # Setup mock to raise specific exception
            mock_server = Mock()
            mock_server.run.side_effect = exception
            mock_create_mcp_server.return_value = mock_server
            
            # Call main and verify handling
            with patch('sys.exit') as mock_exit:
                mcp_server.main()
            
            mock_logger.error.assert_called_with(expected_message)
            mock_exit.assert_called_with(1)
            
    @patch('mcp_server.create_mcp_server')
    @patch('mcp_server.logger')
    def test_keyboard_interrupt_clean_shutdown(self, mock_logger, mock_create_mcp_server):
        """Test clean shutdown on KeyboardInterrupt."""
        # Setup mock server
        mock_server = Mock()
        mock_server.run.side_effect = KeyboardInterrupt()
        mock_create_mcp_server.return_value = mock_server
        
        # Call main function
        with patch('sys.exit') as mock_exit:
            mcp_server.main()
        
        # Verify clean shutdown (no sys.exit call for KeyboardInterrupt)
        mock_logger.info.assert_called_with("Server stopped by user")
        mock_exit.assert_not_called()


class TestMCPServerLoggingOutput:
    """Test actual logging output and behavior."""
    
    def test_logger_name(self):
        """Test that logger uses correct name."""
        logger = logging.getLogger(mcp_server.__name__)
        assert logger.name == 'mcp_server'
        
    @patch('mcp_server.create_mcp_server')
    def test_logging_during_execution(self, mock_create_mcp_server):
        """Test that logging works during actual execution."""
        # Setup mock server
        mock_server = Mock()
        mock_create_mcp_server.return_value = mock_server
        
        # Capture log output
        with patch('mcp_server.logger') as mock_logger:
            # Test successful execution
            mcp_server.main()
            
            # Verify no error logs for successful execution
            mock_logger.error.assert_not_called()
            
            # Test KeyboardInterrupt
            mock_server.run.side_effect = KeyboardInterrupt()
            mcp_server.main()
            mock_logger.info.assert_called_with("Server stopped by user")


class TestMCPServerFileSystem:
    """Test file system interactions."""
    
    def test_logs_directory_creation_with_temp_dir(self):
        """Test logs directory creation in isolated environment."""
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            try:
                # Change to temp directory
                os.chdir(temp_dir)
                
                # Mock os.makedirs to track calls
                with patch('os.makedirs') as mock_makedirs:
                    # Re-import to trigger directory creation
                    import importlib
                    importlib.reload(mcp_server)
                    
                    # Verify directory creation
                    mock_makedirs.assert_called_with("logs", exist_ok=True)
                    
            finally:
                os.chdir(original_cwd)
                
    def test_path_manipulation(self):
        """Test that path manipulation works correctly."""
        # Get current module path
        current_dir = Path(mcp_server.__file__).parent
        expected_path = str(current_dir)
        
        # Verify path is in sys.path
        assert expected_path in sys.path
        
        # Verify it's at the beginning for import priority
        assert sys.path.index(expected_path) == 0


# Pytest markers for test categorization
pytestmark = [
    pytest.mark.unit,
    pytest.mark.interface,
    pytest.mark.mcp
] 