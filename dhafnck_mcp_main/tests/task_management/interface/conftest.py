"""
Configuration for interface layer tests
Includes fixtures and setup for dual-mode testing
"""

import os
import sys
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch

# Add project src to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))


@pytest.fixture
def temp_project_dir():
    """Create a temporary project directory with basic structure"""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create project structure
        (temp_path / "pyproject.toml").touch()
        (temp_path / "src").mkdir()
        (temp_path / "00_RULES").mkdir()
        (temp_path / "data").mkdir()
        (temp_path / "config").mkdir()
        (temp_path / "logs").mkdir()
        
        yield temp_path


@pytest.fixture
def temp_rules_dir():
    """Create a temporary rules directory with test files"""
    with tempfile.TemporaryDirectory() as temp_dir:
        rules_dir = Path(temp_dir)
        
        # Create test rule files
        (rules_dir / "auto_rule.mdc").write_text("# Auto Rule\nTest content")
        (rules_dir / "test_rule.mdc").write_text("# Test Rule\nTest content")
        
        # Create settings file
        settings_content = {
            "protect": True,
            "rules": ["Test rules"],
            "runtime_constants": {
                "project_path": str(rules_dir.parent),
                "username": "test_user"
            }
        }
        
        import json
        (rules_dir / "settings.json").write_text(json.dumps(settings_content, indent=2))
        
        yield rules_dir


@pytest.fixture
def clean_env():
    """Clean environment fixture that restores original state"""
    original_env = os.environ.copy()
    
    # Clear dual-mode related environment variables
    for env_var in ["CURSOR_RULES_DIR", "FASTMCP_TRANSPORT", "DOCUMENT_RULES_PATH"]:
        if env_var in os.environ:
            del os.environ[env_var]
    
    yield
    
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def stdio_mode_env(clean_env):
    """Set up environment for stdio mode testing"""
    # stdio mode doesn't need special environment variables
    # just ensure HTTP mode variables are not set
    return "stdio"


@pytest.fixture
def http_mode_env(clean_env):
    """Set up environment for HTTP mode testing"""
    os.environ["FASTMCP_TRANSPORT"] = "streamable-http"
    os.environ["CURSOR_RULES_DIR"] = "/data/rules"
    return "http"


@pytest.fixture
def mock_docker_env():
    """Mock Docker environment detection"""
    with patch('os.path.exists') as mock_exists:
        def mock_exists_side_effect(path):
            if path == "/.dockerenv":
                return True
            elif str(path) == "/data/rules":
                return True
            return False
        
        mock_exists.side_effect = mock_exists_side_effect
        yield mock_exists


@pytest.fixture
def mock_mcp_server():
    """Create a mock MCP server for testing tool registration"""
    class MockMCP:
        def __init__(self):
            self.tools = {}
        
        def tool(self):
            def decorator(func):
                self.tools[func.__name__] = func
                return func
            return decorator
    
    return MockMCP()


@pytest.fixture(scope="session")
def project_paths():
    """Provide project paths for testing"""
    return {
        "project_root": project_root,
        "src_dir": project_root / "src",
        "tests_dir": project_root / "tests",
        "docs_dir": project_root / "docs"
    }


# Pytest configuration
def pytest_configure(config):
    """Pytest configuration"""
    # Add custom markers
    config.addinivalue_line(
        "markers", "stdio_mode: mark test as stdio mode specific"
    )
    config.addinivalue_line(
        "markers", "http_mode: mark test as HTTP mode specific"
    )
    config.addinivalue_line(
        "markers", "dual_mode: mark test as dual mode compatible"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically"""
    for item in items:
        # Add integration marker to integration tests
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        
        # Add dual_mode marker to dual mode tests
        if "dual_mode" in item.nodeid:
            item.add_marker(pytest.mark.dual_mode)


# Custom assertions for dual mode testing
def assert_valid_path(path, should_exist=None):
    """Assert that a path is valid and optionally exists"""
    assert isinstance(path, Path), f"Expected Path object, got {type(path)}"
    assert path.is_absolute() or str(path).startswith("."), f"Path should be absolute or relative: {path}"
    
    if should_exist is not None:
        if should_exist:
            assert path.exists(), f"Path should exist: {path}"
        else:
            assert not path.exists(), f"Path should not exist: {path}"


def assert_mode_consistency(config, expected_mode):
    """Assert that configuration is consistent with expected mode"""
    assert config.runtime_mode == expected_mode
    
    if expected_mode == "http":
        assert str(config.get_rules_directory()).startswith("/data") or str(config.get_rules_directory()).startswith("/app")
        assert config.get_data_directory() == Path("/data")
    else:
        assert not str(config.get_rules_directory()).startswith("/data")
        assert not str(config.get_data_directory()).startswith("/data")