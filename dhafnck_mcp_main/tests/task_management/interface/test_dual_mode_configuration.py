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
        """Test convenience functions"""
        # Test in stdio mode (default)
        assert get_runtime_mode() == "stdio"
        assert is_stdio_mode() is True
        assert is_http_mode() is False
        
        # Test directory functions
        rules_dir = get_rules_directory()
        data_dir = get_data_directory()
        assert isinstance(rules_dir, Path)
        assert isinstance(data_dir, Path)
        
        # Test path resolution
        resolved = resolve_path("test.txt", "project")
        assert isinstance(resolved, Path)


class TestCursorRulesToolsIntegration:
    """Test integration of CursorRulesTools with dual mode configuration"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.original_env = os.environ.copy()
        for env_var in ["CURSOR_RULES_DIR", "FASTMCP_TRANSPORT", "DOCUMENT_RULES_PATH"]:
            if env_var in os.environ:
                del os.environ[env_var]
    
    def teardown_method(self):
        """Cleanup after each test method"""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_rules_directory_resolution_stdio(self):
        """Test rules directory resolution in CursorRulesTools for stdio mode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            rules_dir = temp_path / "00_RULES"
            rules_dir.mkdir()
            
            with patch('pathlib.Path.cwd', return_value=temp_path):
                cursor_tools = CursorRulesTools()
                resolved_dir = cursor_tools._get_rules_directory_from_settings()
                
                # Should use the dual-mode configuration
                assert resolved_dir == rules_dir
    
    @patch('os.path.exists')
    def test_rules_directory_resolution_http(self, mock_exists):
        """Test rules directory resolution in CursorRulesTools for HTTP mode"""
        def mock_exists_side_effect(path):
            if path == "/.dockerenv":
                return True
            elif str(path) == "/data/rules":
                return True
            return False
        
        mock_exists.side_effect = mock_exists_side_effect
        
        cursor_tools = CursorRulesTools()
        resolved_dir = cursor_tools._get_rules_directory_from_settings()
        
        assert resolved_dir == Path("/data/rules")
    
    def test_settings_file_fallback_stdio(self):
        """Test fallback to settings files in stdio mode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create settings file
            settings_dir = temp_path / "00_RULES" / "core"
            settings_dir.mkdir(parents=True)
            settings_file = settings_dir / "settings.json"
            
            settings_content = {
                "runtime_constants": {
                    "DOCUMENT_RULES_PATH": "custom_rules"
                }
            }
            
            with open(settings_file, 'w') as f:
                json.dump(settings_content, f)
            
            with patch('pathlib.Path.cwd', return_value=temp_path):
                cursor_tools = CursorRulesTools()
                resolved_dir = cursor_tools._get_rules_directory_from_settings()
                
                assert resolved_dir == temp_path / "custom_rules"
    
    def test_cursor_settings_fallback_stdio(self):
        """Test fallback to .cursor/settings.json in stdio mode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create .cursor/settings.json
            cursor_dir = temp_path / ".cursor"
            cursor_dir.mkdir()
            settings_file = cursor_dir / "settings.json"
            
            settings_content = {
                "runtime_constants": {
                    "DOCUMENT_RULES_PATH": "/app/00_RULES"
                }
            }
            
            with open(settings_file, 'w') as f:
                json.dump(settings_content, f)
            
            with patch('pathlib.Path.cwd', return_value=temp_path):
                cursor_tools = CursorRulesTools()
                resolved_dir = cursor_tools._get_rules_directory_from_settings()
                
                assert resolved_dir == Path("/app/00_RULES")
    
    def test_environment_override_stdio(self):
        """Test environment variable override in stdio mode"""
        os.environ["DOCUMENT_RULES_PATH"] = "env_rules"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            with patch('pathlib.Path.cwd', return_value=temp_path):
                cursor_tools = CursorRulesTools()
                resolved_dir = cursor_tools._get_rules_directory_from_settings()
                
                assert resolved_dir == temp_path / "env_rules"
    
    @patch('os.path.exists')
    def test_no_settings_fallback_http(self, mock_exists):
        """Test fallback when no settings files exist in HTTP mode"""
        def mock_exists_side_effect(path):
            if path == "/.dockerenv":
                return True
            elif str(path) == "/data/rules":
                return False  # Rules directory doesn't exist
            return False
        
        mock_exists.side_effect = mock_exists_side_effect
        
        cursor_tools = CursorRulesTools()
        resolved_dir = cursor_tools._get_rules_directory_from_settings()
        
        # Should still return the expected path even if it doesn't exist
        assert resolved_dir == Path("/data/rules")


class TestRealWorldScenarios:
    """Test real-world usage scenarios"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.original_env = os.environ.copy()
    
    def teardown_method(self):
        """Cleanup after each test method"""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_docker_development_scenario(self):
        """Test typical Docker development scenario"""
        # Simulate Docker environment
        os.environ["FASTMCP_TRANSPORT"] = "streamable-http"
        os.environ["CURSOR_RULES_DIR"] = "/data/rules"
        
        with patch('os.path.exists', return_value=True):
            config = DualModeConfig()
            
            assert config.runtime_mode == "http"
            assert config.get_rules_directory() == Path("/data/rules")
            assert config.get_data_directory() == Path("/data")
            
            env_config = config.get_environment_config()
            assert env_config["transport"] == "streamable-http"
            assert env_config["container_mode"] is True
    
    def test_local_development_scenario(self):
        """Test typical local development scenario"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create project structure
            (temp_path / "pyproject.toml").touch()
            (temp_path / "src").mkdir()
            (temp_path / "00_RULES").mkdir()
            (temp_path / "data").mkdir()
            
            with patch('pathlib.Path.cwd', return_value=temp_path):
                config = DualModeConfig()
                
                assert config.runtime_mode == "stdio"
                assert config.get_rules_directory() == temp_path / "00_RULES"
                assert config.get_data_directory() == temp_path / "data"
                
                env_config = config.get_environment_config()
                assert env_config["transport"] == "stdio"
                assert env_config["container_mode"] is False
    
    def test_migration_compatibility(self):
        """Test compatibility with existing configurations"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create legacy .cursor/settings.json
            cursor_dir = temp_path / ".cursor"
            cursor_dir.mkdir()
            settings_file = cursor_dir / "settings.json"
            
            legacy_settings = {
                "runtime_constants": {
                    "DOCUMENT_RULES_PATH": "/app/00_RULES",
                    "projet_path_root": "/app"
                }
            }
            
            with open(settings_file, 'w') as f:
                json.dump(legacy_settings, f)
            
            with patch('pathlib.Path.cwd', return_value=temp_path):
                cursor_tools = CursorRulesTools()
                resolved_dir = cursor_tools._get_rules_directory_from_settings()
                
                # Should respect the legacy configuration
                assert resolved_dir == Path("/app/00_RULES")


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])