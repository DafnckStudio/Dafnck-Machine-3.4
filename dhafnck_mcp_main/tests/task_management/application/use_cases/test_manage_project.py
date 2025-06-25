"""
This is the canonical and only maintained test suite for the MCP project management tool interface.
All validation, edge-case, and integration tests should be added here.
Redundant or duplicate tests in other files have been removed.
"""

import pytest
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

from fastmcp.task_management.interface.consolidated_mcp_tools import ConsolidatedMCPTools

@pytest.fixture
def mcp_tools():
    """Fixture to provide an instance of ConsolidatedMCPTools."""
    tools = ConsolidatedMCPTools()
    # Ensure a clean state for project tests
    tools._project_manager._projects = {}
    tools._project_manager._save_projects()
    return tools

def test_create_project(mcp_tools):
    """Test creating a new project."""
    result = mcp_tools._project_manager.create_project(
        "test_project",
        "Test Project",
        "A project for testing"
    )
    assert result["success"]
    assert result["project"]["id"] == "test_project"
    assert result["project"]["name"] == "Test Project"

def test_get_project(mcp_tools):
    """Test getting an existing project."""
    # First, create a project
    mcp_tools._project_manager.create_project(
        "test_project_2",
        "Test Project 2",
        "Another project for testing"
    )

    # Now, get the project
    result = mcp_tools._project_manager.get_project("test_project_2")
    assert result["success"]
    assert result["project"]["id"] == "test_project_2"

def test_get_nonexistent_project(mcp_tools):
    """Test getting a project that does not exist."""
    result = mcp_tools._project_manager.get_project("nonexistent_project")
    assert not result["success"]
    assert "not found" in result["error"]

def test_list_projects(mcp_tools):
    """Test listing all projects."""
    # Create a couple of projects
    mcp_tools._project_manager.create_project(
        "proj1", "Project 1"
    )
    mcp_tools._project_manager.create_project(
        "proj2", "Project 2"
    )

    result = mcp_tools._project_manager.list_projects()
    assert result["success"]
    assert result["count"] == 2
    project_ids = [p["id"] for p in result["projects"]]
    assert "proj1" in project_ids
    assert "proj2" in project_ids 