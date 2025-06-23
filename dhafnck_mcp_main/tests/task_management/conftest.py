"""
Test configuration and fixtures for MCP Task Management Server
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

from fastmcp.task_management.interface.ddd_mcp_server import create_mcp_server
from fastmcp.task_management.interface.mcp_tools import MCPTaskTools
from fastmcp.task_management.domain.entities.task import Task
from fastmcp.task_management.domain.value_objects.task_id import TaskId
from fastmcp.task_management.domain.value_objects.task_status import TaskStatus, TaskStatusEnum
from fastmcp.task_management.domain.value_objects.priority import Priority, PriorityLevel


@pytest.fixture
def mock_mcp_server():
    """Mock MCP server for unit tests."""
    return Mock()


@pytest.fixture
def mcp_server():
    """Real MCP server for integration tests."""
    return create_mcp_server()


@pytest.fixture
def sample_config():
    """Sample configuration for tests."""
    return {
        "server": {
            "name": "task_management",
            "version": "1.0.0"
        },
        "storage": {
            "type": "json",
            "path": ".cursor/rules/tasks/tasks.json"
        },
        "features": {
            "task_management": True,
            "rule_generation": True,
            "yaml_roles": True
        }
    }


@pytest.fixture
def temp_config_file(tmp_path, sample_config):
    """Temporary config file for tests."""
    config_file = tmp_path / "test_config.yaml"
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
def temp_tasks_file(tmp_path, sample_tasks_data):
    """Temporary tasks.json file for tests, sets TASK_MANAGEMENT_TASKS_PATH env var."""
    tasks_file = tmp_path / "tasks.json"
    with open(tasks_file, 'w') as f:
        json.dump(sample_tasks_data, f, indent=2)
    # Set the environment variable for all code under test
    os.environ["TASK_MANAGEMENT_TASKS_PATH"] = str(tasks_file)
    return tasks_file


@pytest.fixture
def temp_project_dir(tmp_path, sample_tasks_data):
    """Temporary project directory with complete structure, sets TASK_MANAGEMENT_TASKS_PATH env var."""
    # Create directory structure
    cursor_rules = tmp_path / ".cursor" / "rules"
    cursor_rules.mkdir(parents=True)
    
    tasks_dir = cursor_rules / "tasks"
    tasks_dir.mkdir()
    
    contexts_dir = cursor_rules / "contexts"
    contexts_dir.mkdir()
    
    # Create tasks.json
    tasks_file = tasks_dir / "tasks.json"
    with open(tasks_file, 'w') as f:
        json.dump(sample_tasks_data, f, indent=2)
    # Set the environment variable for all code under test
    os.environ["TASK_MANAGEMENT_TASKS_PATH"] = str(tasks_file)
    
    return tmp_path


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
def temp_yaml_role_file(tmp_path, yaml_role_data):
    """Temporary YAML role file for tests."""
    yaml_dir = tmp_path / "yaml-lib" / "qa_engineer"
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


# Event loop fixture for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close() 