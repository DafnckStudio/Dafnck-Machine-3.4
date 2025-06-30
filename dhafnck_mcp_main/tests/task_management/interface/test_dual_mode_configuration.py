"""
Comprehensive Test Suite for Dual Mode Configuration System
Tests both stdio (local Python) and HTTP (Docker) modes
"""

import os
import sys
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import json

# Add project src to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from fastmcp.dual_mode_config import (
    DualModeConfig,
    dual_mode_config,
    get_runtime_mode,
    get_rules_directory,
    get_data_directory,
    resolve_path,
    is_http_mode,
    is_stdio_mode
)
from fastmcp.task_management.interface.cursor_rules_tools import CursorRulesTools


class TestDualModeConfig:
    """Test the dual mode configuration system"""
    
    def setup_method(self):
        """Setup for each test method"""
        # Clear environment variables that might affect detection
        self.original_env = os.environ.copy()
        for env_var in ["CURSOR_RULES_DIR", "FASTMCP_TRANSPORT", "DOCUMENT_RULES_PATH"]:
            if env_var in os.environ:
                del os.environ[env_var]
    
    def teardown_method(self):
        """Cleanup after each test method"""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_stdio_mode_detection(self):
        """Test detection of stdio mode (default)"""
        config = DualModeConfig()
        assert config.runtime_mode == "stdio"
        assert config._detect_runtime_mode() == "stdio"
    
    @patch('os.path.exists')
    def test_http_mode_detection_dockerenv(self, mock_exists):
        """Test detection of HTTP mode via .dockerenv"""
        def mock_exists_side_effect(path):
            return path == "/.dockerenv"
        
        mock_exists.side_effect = mock_exists_side_effect
        
        config = DualModeConfig()
        assert config.runtime_mode == "http"
    
    def test_http_mode_detection_env_var(self):
        """Test detection of HTTP mode via environment variable"""
        os.environ["FASTMCP_TRANSPORT"] = "streamable-http"
        
        config = DualModeConfig()
        assert config.runtime_mode == "http"
    
    def test_http_mode_detection_cursor_rules_dir(self):
        """Test detection of HTTP mode via CURSOR_RULES_DIR"""
        os.environ["CURSOR_RULES_DIR"] = "/data/rules"
        
        config = DualModeConfig()
        assert config.runtime_mode == "http"
    
    @patch('os.path.exists')
    def test_http_mode_detection_app_structure(self, mock_exists):
        """Test detection of HTTP mode via Docker file structure"""
        def mock_exists_side_effect(path):
            if path == "/app":
                return True
            elif path == "/home":
                return False
            elif path == "/.dockerenv":
                return False
            return False
        
        mock_exists.side_effect = mock_exists_side_effect
        
        config = DualModeConfig()
        assert config.runtime_mode == "http"
    
    def test_project_root_detection_stdio(self):
        """Test project root detection in stdio mode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create project indicators
            (temp_path / "pyproject.toml").touch()
            (temp_path / "src").mkdir()
            
            with patch('pathlib.Path.cwd', return_value=temp_path):
                config = DualModeConfig()
                assert config.project_root == temp_path
    
    @patch('os.path.exists')
    def test_project_root_detection_http(self, mock_exists):
        """Test project root detection in HTTP mode"""
        mock_exists.return_value = True  # Simulate /.dockerenv exists
        
        config = DualModeConfig()
        assert config.project_root == Path("/app")
    
    def test_rules_directory_stdio_mode(self):
        """Test rules directory resolution in stdio mode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            with patch('pathlib.Path.cwd', return_value=temp_path):
                config = DualModeConfig()
                rules_dir = config.get_rules_directory()
                assert rules_dir == temp_path / "00_RULES"
    
    @patch('os.path.exists')
    def test_rules_directory_http_mode(self, mock_exists):
        """Test rules directory resolution in HTTP mode"""
        mock_exists.return_value = True  # Simulate /.dockerenv exists
        
        config = DualModeConfig()
        rules_dir = config.get_rules_directory()
        assert rules_dir == Path("/data/rules")
    
    def test_data_directory_stdio_mode(self):
        """Test data directory resolution in stdio mode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            with patch('pathlib.Path.cwd', return_value=temp_path):
                config = DualModeConfig()
                data_dir = config.get_data_directory()
                assert data_dir == temp_path / "data"
    
    @patch('os.path.exists')
    def test_data_directory_http_mode(self, mock_exists):
        """Test data directory resolution in HTTP mode"""
        mock_exists.return_value = True  # Simulate /.dockerenv exists
        
        config = DualModeConfig()
        data_dir = config.get_data_directory()
        assert data_dir == Path("/data")
    
    def test_path_resolution_absolute(self):
        """Test resolution of absolute paths"""
        config = DualModeConfig()
        absolute_path = "/absolute/path/file.txt"
        resolved = config.resolve_path(absolute_path)
        assert resolved == Path(absolute_path)
    
    def test_path_resolution_relative_stdio(self):
        """Test resolution of relative paths in stdio mode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            with patch('pathlib.Path.cwd', return_value=temp_path):
                config = DualModeConfig()
                resolved = config.resolve_path("relative/path.txt", "project")
                assert resolved == temp_path / "relative/path.txt"
    
    def test_environment_config_stdio(self):
        """Test environment configuration in stdio mode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            with patch('pathlib.Path.cwd', return_value=temp_path):
                config = DualModeConfig()
                env_config = config.get_environment_config()
                
                assert env_config["runtime_mode"] == "stdio"
                assert env_config["transport"] == "stdio"
                assert env_config["container_mode"] is False
                assert env_config["auth_enabled"] is False
    
    @patch('os.path.exists')
    def test_environment_config_http(self, mock_exists):
        """Test environment configuration in HTTP mode"""
        mock_exists.return_value = True  # Simulate /.dockerenv exists
        
        config = DualModeConfig()
        env_config = config.get_environment_config()
        
        assert env_config["runtime_mode"] == "http"
        assert env_config["transport"] == "streamable-http"
        assert env_config["container_mode"] is True
        assert env_config["host"] == "0.0.0.0"
        assert env_config["port"] == 8000
    
    def test_convenience_functions(self):
        """Test convenience functions work correctly"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create a real DualModeConfig instance with mocked detection
            with patch('fastmcp.dual_mode_config.DualModeConfig._detect_runtime_mode', return_value="stdio"), \
                 patch('fastmcp.dual_mode_config.DualModeConfig._get_project_root', return_value=temp_path):
                
                # Create a new config instance for testing
                test_config = DualModeConfig()
                
                # Patch the global instance
                with patch('fastmcp.dual_mode_config.dual_mode_config', test_config):
                    mode = get_runtime_mode()
                    rules_dir = get_rules_directory()
                    data_dir = get_data_directory()
                    http_mode = is_http_mode()
                    stdio_mode = is_stdio_mode()
                    
                    assert mode == "stdio"
                    assert rules_dir == temp_path / "00_RULES"
                    assert data_dir == temp_path / "data"
                    assert http_mode is False
                    assert stdio_mode is True
                    
                    # Test path resolution
                    resolved = resolve_path("test.txt", "project")
                    assert resolved == temp_path / "test.txt"


class TestCursorRulesToolsIntegration:
    """Test CursorRulesTools integration with dual mode configuration"""
    
    def test_rules_directory_resolution_stdio(self):
        """Test rules directory resolution in stdio mode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Patch the functions in the cursor_rules_tools module where they're imported
            with patch('fastmcp.task_management.interface.cursor_rules_tools.get_rules_directory') as mock_get_rules, \
                 patch('fastmcp.task_management.interface.cursor_rules_tools.is_http_mode') as mock_is_http, \
                 patch('fastmcp.task_management.interface.cursor_rules_tools.find_project_root') as mock_find_root:
                
                # Set up mocks
                expected_path = temp_path / "rules"
                mock_get_rules.return_value = expected_path
                mock_is_http.return_value = False
                mock_find_root.return_value = temp_path
                
                # Create the expected directory
                expected_path.mkdir(parents=True, exist_ok=True)
                
                # Create CursorRulesTools instance
                tools = CursorRulesTools()
                
                # Test the method
                result = tools._get_rules_directory_from_settings()
                
                # Verify result
                assert result == expected_path
                print("✅ STDIO rules directory resolution test passed")
    
    def test_rules_directory_resolution_http(self):
        """Test rules directory resolution in HTTP mode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Patch the functions in the cursor_rules_tools module where they're imported
            with patch('fastmcp.task_management.interface.cursor_rules_tools.get_rules_directory') as mock_get_rules, \
                 patch('fastmcp.task_management.interface.cursor_rules_tools.is_http_mode') as mock_is_http, \
                 patch('fastmcp.task_management.interface.cursor_rules_tools.find_project_root') as mock_find_root:
                
                # Set up mocks
                expected_path = temp_path / "app_rules"
                mock_get_rules.return_value = expected_path
                mock_is_http.return_value = True
                mock_find_root.return_value = temp_path
                
                # Create the expected directory
                expected_path.mkdir(parents=True, exist_ok=True)
                
                # Create CursorRulesTools instance
                tools = CursorRulesTools()
                
                # Test the method
                result = tools._get_rules_directory_from_settings()
                
                # Verify result
                assert result == expected_path
                print("✅ HTTP rules directory resolution test passed")
    
    def test_settings_file_fallback_stdio(self):
        """Test fallback to settings file in stdio mode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Patch the functions in the cursor_rules_tools module where they're imported
            with patch('fastmcp.task_management.interface.cursor_rules_tools.get_rules_directory') as mock_get_rules, \
                 patch('fastmcp.task_management.interface.cursor_rules_tools.is_http_mode') as mock_is_http, \
                 patch('fastmcp.task_management.interface.cursor_rules_tools.find_project_root') as mock_find_root:
                
                # Set up mocks - simulate non-existent rules directory
                non_existent_path = temp_path / "non_existent"
                mock_get_rules.return_value = non_existent_path
                mock_is_http.return_value = False
                mock_find_root.return_value = temp_path
                
                # Create settings file with custom rules path
                settings_dir = temp_path / "00_RULES" / "core"
                settings_dir.mkdir(parents=True, exist_ok=True)
                settings_file = settings_dir / "settings.json"
                
                custom_rules_path = temp_path / "custom_rules"
                custom_rules_path.mkdir(parents=True, exist_ok=True)
                
                settings_content = {
                    "runtime_constants": {
                        "DOCUMENT_RULES_PATH": str(custom_rules_path)
                    }
                }
                
                with open(settings_file, 'w') as f:
                    json.dump(settings_content, f)
                
                # Create CursorRulesTools instance
                tools = CursorRulesTools()
                
                # Test the method
                result = tools._get_rules_directory_from_settings()
                
                # Verify result uses the settings file path
                assert result == custom_rules_path
                print("✅ Settings file fallback test passed")
    
    def test_cursor_settings_fallback_stdio(self):
        """Test fallback to .cursor/settings.json in stdio mode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Patch the functions in the cursor_rules_tools module where they're imported
            with patch('fastmcp.task_management.interface.cursor_rules_tools.get_rules_directory') as mock_get_rules, \
                 patch('fastmcp.task_management.interface.cursor_rules_tools.is_http_mode') as mock_is_http, \
                 patch('fastmcp.task_management.interface.cursor_rules_tools.find_project_root') as mock_find_root:
                
                # Set up mocks - simulate non-existent rules directory
                non_existent_path = temp_path / "non_existent"
                mock_get_rules.return_value = non_existent_path
                mock_is_http.return_value = False
                mock_find_root.return_value = temp_path
                
                # Create .cursor/settings.json with custom rules path
                cursor_dir = temp_path / ".cursor"
                cursor_dir.mkdir(parents=True, exist_ok=True)
                settings_file = cursor_dir / "settings.json"
                
                custom_rules_path = temp_path / "cursor_rules"
                custom_rules_path.mkdir(parents=True, exist_ok=True)
                
                settings_content = {
                    "runtime_constants": {
                        "DOCUMENT_RULES_PATH": str(custom_rules_path)
                    }
                }
                
                with open(settings_file, 'w') as f:
                    json.dump(settings_content, f)
                
                # Create CursorRulesTools instance
                tools = CursorRulesTools()
                
                # Test the method
                result = tools._get_rules_directory_from_settings()
                
                # Verify result uses the .cursor settings file path
                assert result == custom_rules_path
                print("✅ Cursor settings fallback test passed")
    
    def test_environment_override_stdio(self):
        """Test environment variable override in stdio mode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Patch the functions in the cursor_rules_tools module where they're imported
            with patch('fastmcp.task_management.interface.cursor_rules_tools.get_rules_directory') as mock_get_rules, \
                 patch('fastmcp.task_management.interface.cursor_rules_tools.is_http_mode') as mock_is_http, \
                 patch('fastmcp.task_management.interface.cursor_rules_tools.find_project_root') as mock_find_root:
                
                # Set up mocks - simulate non-existent rules directory
                non_existent_path = temp_path / "non_existent"
                mock_get_rules.return_value = non_existent_path
                mock_is_http.return_value = False
                mock_find_root.return_value = temp_path
                
                # Set environment variable
                env_rules_path = temp_path / "env_rules"
                env_rules_path.mkdir(parents=True, exist_ok=True)
                
                with patch.dict(os.environ, {'DOCUMENT_RULES_PATH': str(env_rules_path)}):
                    # Create CursorRulesTools instance
                    tools = CursorRulesTools()
                    
                    # Test the method
                    result = tools._get_rules_directory_from_settings()
                    
                    # Verify result uses the environment variable path
                    assert result == env_rules_path
                    print("✅ Environment override test passed")
    
    def test_no_settings_fallback_http(self):
        """Test fallback behavior when no settings files exist in HTTP mode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Patch the functions in the cursor_rules_tools module where they're imported
            with patch('fastmcp.task_management.interface.cursor_rules_tools.get_rules_directory') as mock_get_rules, \
                 patch('fastmcp.task_management.interface.cursor_rules_tools.is_http_mode') as mock_is_http, \
                 patch('fastmcp.task_management.interface.cursor_rules_tools.find_project_root') as mock_find_root:
                
                # Set up mocks
                expected_path = temp_path / "default_rules"
                mock_get_rules.return_value = expected_path
                mock_is_http.return_value = True
                mock_find_root.return_value = temp_path
                
                # Create CursorRulesTools instance
                tools = CursorRulesTools()
                
                # Test the method
                result = tools._get_rules_directory_from_settings()
                
                # Verify result falls back to dual-mode config
                assert result == expected_path
                print("✅ HTTP no settings fallback test passed")


class TestRealWorldScenarios:
    """Test real-world usage scenarios"""
    
    def test_migration_compatibility(self):
        """Test compatibility with legacy project structures"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Patch the functions in the cursor_rules_tools module where they're imported
            with patch('fastmcp.task_management.interface.cursor_rules_tools.get_rules_directory') as mock_get_rules, \
                 patch('fastmcp.task_management.interface.cursor_rules_tools.is_http_mode') as mock_is_http, \
                 patch('fastmcp.task_management.interface.cursor_rules_tools.find_project_root') as mock_find_root:
                
                # Set up mocks to simulate legacy structure
                legacy_path = temp_path / "legacy_rules"
                mock_get_rules.return_value = legacy_path
                mock_is_http.return_value = False
                mock_find_root.return_value = temp_path
                
                # Create legacy directory structure
                legacy_path.mkdir(parents=True, exist_ok=True)
                
                # Create CursorRulesTools instance
                tools = CursorRulesTools()
                
                # Test the method
                result = tools._get_rules_directory_from_settings()
                
                # Verify result
                assert result == legacy_path
                print("✅ Migration compatibility test passed")


def test_basic_dual_mode_functionality():
    """Test basic dual mode configuration functionality"""
    # Test that we can create DualModeConfig instances
    config = DualModeConfig()
    assert config is not None
    
    # Test mode detection functions
    assert callable(get_runtime_mode)
    assert callable(is_http_mode)
    assert callable(is_stdio_mode)
    
    print("✅ Basic dual mode functionality test passed")


if __name__ == "__main__":
    # Run tests manually for debugging
    test_basic_dual_mode_functionality()
    
    test_instance = TestCursorRulesToolsIntegration()
    test_instance.test_rules_directory_resolution_stdio()
    test_instance.test_rules_directory_resolution_http()
    test_instance.test_settings_file_fallback_stdio()
    test_instance.test_cursor_settings_fallback_stdio()
    test_instance.test_environment_override_stdio()
    test_instance.test_no_settings_fallback_http()
    
    real_world_test = TestRealWorldScenarios()
    real_world_test.test_migration_compatibility()
    
    print("🎉 All tests passed!")