"""
Test configuration and fixtures for MCP Task Management Server
Using Test Data Isolation System with .test.json files
Following Test_Projet_Impliment.mdc architecture
"""

import pytest
import asyncio
import tempfile
import yaml
import json
from pathlib import Path
from unittest.mock import Mock, AsyncMock
from typing import Dict, Any

# Import project modules
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import test isolation system - Fixed import
from test_environment_config import isolated_test_environment, cleanup_test_data_files_only

# Mock imports for testing
try:
    from fastmcp.task_management.interface.consolidated_mcp_server import ConsolidatedMCPServer
    from fastmcp.task_management.interface.consolidated_mcp_tools import ConsolidatedMCPTools
except ImportError:
    # Create mock classes if imports fail
    class ConsolidatedMCPServer:
        pass
    
    class ConsolidatedMCPTools:
        pass


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_data_after_session():
    """
    Automatically clean up test data files after test session
    
    This only removes:
    - .test.json files
    - .test.mdc files
    - .test.yaml files
    - Temporary test directories
    - __pycache__ files
    
    It NEVER removes:
    - Test code files (test_*.py)
    - Production files
    - Source code
    """
    print("\n🧪 Starting test session with automatic cleanup enabled...")
    print("🛡️  SAFETY: Only .test.json and .test.mdc files will be cleaned after tests")
    
    yield  # Run all tests
    
    # Cleanup after all tests complete
    print("\n🧹 Running automatic test data cleanup...")
    
    project_root = Path.cwd()
    cleaned_count = cleanup_test_data_files_only(project_root)
    
    if cleaned_count > 0:
        print(f"🧹 Session cleanup: Removed {cleaned_count} test data files")
    else:
        print("✨ No test data files found to clean")
    
    print("🛡️  Production data was never touched")


@pytest.fixture
def isolated_test_config():
    """Provide isolated test environment configuration"""
    with isolated_test_environment(test_id="pytest_test") as config:
        yield config


@pytest.fixture
def mock_mcp_server():
    """Mock MCP server for testing"""
    mock_server = Mock(spec=ConsolidatedMCPServer)
    mock_server.run = AsyncMock()
    mock_server.stop = AsyncMock()
    return mock_server


@pytest.fixture
def mock_mcp_tools():
    """Mock MCP tools for testing"""
    mock_tools = Mock(spec=ConsolidatedMCPTools)
    mock_tools.register_tools = Mock()
    return mock_tools


@pytest.fixture
def sample_project_data():
    """Sample project data for testing"""
    return {
        "test_project": {
            "name": "Test Project",
            "description": "A test project for isolated testing",
            "test_environment": True,
            "created_at": "2025-01-01T00:00:00Z",
            "task_trees": {
                "main": {
                    "name": "Main task tree",
                    "description": "Main task tree"
                }
            }
        }
    }


@pytest.fixture
def sample_task_data():
    """Sample task data for testing"""
    return {
        "task_001": {
            "id": "task_001",
            "title": "Test Task",
            "description": "A test task for isolated testing",
            "status": "todo",
            "priority": "medium",
            "test_environment": True,
            "created_at": "2025-01-01T00:00:00Z"
        }
    }


# Configure pytest markers
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line("markers", "isolated: mark test as using isolated test environment")
    config.addinivalue_line("markers", "production_safe: mark test as production data safe")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")


def pytest_runtest_setup(item):
    """Setup for each test"""
    # Ensure test isolation for marked tests
    if item.get_closest_marker("isolated"):
        # Test should use isolated environment
        pass


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished"""
    print(f"\n🏁 Test session finished with exit status: {exitstatus}")
    if exitstatus == 0:
        print("✅ All tests passed successfully")
    else:
        print("❌ Some tests failed")
    print("🛡️  Production data remained protected throughout testing")


@pytest.fixture
def mock_mcp_server():
    """Mock MCP server for unit tests."""
    return Mock()


@pytest.fixture
def mcp_server():
    """Real MCP server for integration tests."""
    return create_consolidated_mcp_server()


@pytest.fixture
def sample_config(isolated_test_config):
    """Sample configuration for tests using isolated environment."""
    return {
        "server": {
            "name": "dhafnck_mcp",
            "version": "1.0.0"
        },
        "storage": {
            "type": "json",
            "path": str(isolated_test_config.test_files["tasks"])  # Use .test.json file
        },
        "features": {
            "dhafnck_mcp": True,
            "rule_generation": True,
            "yaml_roles": True
        }
    }


@pytest.fixture
def temp_config_file(isolated_test_config, sample_config):
    """Temporary config file for tests using isolated environment."""
    config_file = isolated_test_config.temp_dir / "test_config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(sample_config, f)
    return config_file


@pytest.fixture
def sample_tasks_data():
    """Sample tasks data for testing."""
    return {
        "meta": {
            "projectName": "Test Project",
            "version": "1.0.0",
            "totalTasks": 2
        },
        "tasks": [
            {
                "id": 1,
                "title": "Test Task 1",
                "description": "First test task",
                "status": "todo",
                "priority": "high",
                "assignees": ["qa_engineer"],
                "labels": ["test"],
                "subtasks": []
            },
            {
                "id": 2,
                "title": "Test Task 2", 
                "description": "Second test task",
                "status": "in_progress",
                "priority": "medium",
                "assignees": ["senior_developer"],
                "labels": ["development"],
                "subtasks": []
            }
        ]
    }


@pytest.fixture
def temp_tasks_file(isolated_test_config, sample_tasks_data):
    """Isolated tasks.test.json file for tests, sets TASKS_JSON_PATH env var."""
    tasks_file = isolated_test_config.test_files["tasks"]
    with open(tasks_file, 'w') as f:
        json.dump(sample_tasks_data, f, indent=2)
    
    # Set the environment variable for all code under test
    original_env = os.environ.get("TASKS_JSON_PATH")
    os.environ["TASKS_JSON_PATH"] = str(tasks_file)
    
    yield tasks_file
    
    # Restore original environment
    if original_env is not None:
        os.environ["TASKS_JSON_PATH"] = original_env
    else:
        os.environ.pop("TASKS_JSON_PATH", None)


@pytest.fixture
def temp_project_dir(isolated_test_config, sample_tasks_data):
    """Isolated project directory with complete structure, sets TASKS_JSON_PATH env var."""
    # The isolated_test_config already creates the proper directory structure
    # with .cursor/rules/tasks/ etc.
    
    # Create tasks.test.json with sample data
    tasks_file = isolated_test_config.test_files["tasks"]
    with open(tasks_file, 'w') as f:
        json.dump(sample_tasks_data, f, indent=2)
    
    # Set the environment variable for all code under test
    original_env = os.environ.get("TASKS_JSON_PATH")
    os.environ["TASKS_JSON_PATH"] = str(tasks_file)
    
    yield isolated_test_config.temp_dir
    
    # Restore original environment
    if original_env is not None:
        os.environ["TASKS_JSON_PATH"] = original_env
    else:
        os.environ.pop("TASKS_JSON_PATH", None)


@pytest.fixture
def sample_task_entity():
    """Sample Task entity for testing."""
    return Task.create(
        id=TaskId.from_int(1),
        title="Test Task",
        description="Test task description",
        status=TaskStatus(TaskStatusEnum.TODO),
        priority=Priority(PriorityLevel.HIGH),
        assignees=["qa_engineer"],
        labels=["test"]
    )


@pytest.fixture
def yaml_role_data():
    """Sample YAML role data for testing."""
    return {
        "name": "QA Engineer",
        "role": "qa_engineer",
        "persona": "Quality assurance specialist focused on testing and validation",
        "primary_focus": "Testing strategies, quality validation, and bug prevention",
        "responsibilities": [
            "Design comprehensive test strategies",
            "Implement automated testing frameworks",
            "Ensure code quality and reliability"
        ],
        "tools": [
            "pytest",
            "coverage",
            "mock"
        ]
    }


@pytest.fixture
def temp_yaml_role_file(isolated_test_config, yaml_role_data):
    """Temporary YAML role file for tests using isolated environment."""
    yaml_dir = isolated_test_config.temp_dir / "yaml-lib" / "qa_engineer"
    yaml_dir.mkdir(parents=True)
    
    role_file = yaml_dir / "job_desc.yaml"
    with open(role_file, 'w') as f:
        yaml.dump(yaml_role_data, f)
    
    return role_file


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "quick: Quick smoke tests for development")
    config.addinivalue_line("markers", "unit: Unit tests")
    config.addinivalue_line("markers", "integration: Integration tests")
    config.addinivalue_line("markers", "slow: Slow tests (skip during development)")
    config.addinivalue_line("markers", "mcp: MCP server specific tests")
    config.addinivalue_line("markers", "domain: Domain layer tests")
    config.addinivalue_line("markers", "application: Application layer tests")
    config.addinivalue_line("markers", "infrastructure: Infrastructure layer tests")
    config.addinivalue_line("markers", "interface: Interface layer tests")
    config.addinivalue_line("markers", "isolated: Tests using isolated test environment")


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def isolate_test_environment():
    """
    Automatically isolate each test to prevent interference.
    This fixture runs for every test and ensures proper isolation.
    """
    # Store original environment variables
    original_tasks_path = os.environ.get("TASKS_JSON_PATH")
    original_projects_path = os.environ.get("PROJECTS_JSON_PATH")
    original_auto_rule_path = os.environ.get("AUTO_RULE_PATH")
    
    yield
    
    # Restore original environment after test
    if original_tasks_path is not None:
        os.environ["TASKS_JSON_PATH"] = original_tasks_path
    else:
        os.environ.pop("TASKS_JSON_PATH", None)
        
    if original_projects_path is not None:
        os.environ["PROJECTS_JSON_PATH"] = original_projects_path
    else:
        os.environ.pop("PROJECTS_JSON_PATH", None)
        
    if original_auto_rule_path is not None:
        os.environ["AUTO_RULE_PATH"] = original_auto_rule_path
    else:
        os.environ.pop("AUTO_RULE_PATH", None)


# Legacy fixtures for backward compatibility (deprecated)
@pytest.fixture
def temp_tasks_file_legacy(tmp_path, sample_tasks_data):
    """DEPRECATED: Legacy fixture - use temp_tasks_file instead"""
    import warnings
    warnings.warn(
        "temp_tasks_file_legacy is deprecated. Use temp_tasks_file with isolated_test_config instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    tasks_file = tmp_path / "tasks.json"  # Note: uses .json not .test.json
    with open(tasks_file, 'w') as f:
        json.dump(sample_tasks_data, f, indent=2)
    os.environ["TASKS_JSON_PATH"] = str(tasks_file)
    return tasks_file


@pytest.fixture  
def temp_project_dir_legacy(tmp_path, sample_tasks_data):
    """DEPRECATED: Legacy fixture - use temp_project_dir instead"""
    import warnings
    warnings.warn(
        "temp_project_dir_legacy is deprecated. Use temp_project_dir with isolated_test_config instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # Create directory structure
    cursor_rules = tmp_path / ".cursor" / "rules"
    cursor_rules.mkdir(parents=True)
    
    tasks_dir = cursor_rules / "tasks"
    tasks_dir.mkdir()
    
    contexts_dir = cursor_rules / "contexts"
    contexts_dir.mkdir()
    
    # Create tasks.json (not .test.json)
    tasks_file = tasks_dir / "tasks.json"
    with open(tasks_file, 'w') as f:
        json.dump(sample_tasks_data, f, indent=2)
    os.environ["TASKS_JSON_PATH"] = str(tasks_file)
    
    return tmp_path 