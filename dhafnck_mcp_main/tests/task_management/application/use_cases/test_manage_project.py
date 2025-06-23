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

from fastmcp.dhafnck_mcp.interface.consolidated_mcp_tools_v2 import ConsolidatedMCPToolsV2

@pytest.fixture
def mcp_tools():
    """Fixture to provide an instance of ConsolidatedMCPToolsV2."""
    tools = ConsolidatedMCPToolsV2()
    # Ensure a clean state for project tests
    tools._multi_agent_tools._projects = {}
    tools._multi_agent_tools._save_projects()
    return tools

def test_create_project(mcp_tools):
    """Test creating a new project."""
    result = mcp_tools._multi_agent_tools.create_project(
        project_id="test_project",
        name="Test Project",
        description="A project for testing"
    )
    assert result["success"]
    assert result["project"]["id"] == "test_project"
    assert result["project"]["name"] == "Test Project"

def test_get_project(mcp_tools):
    """Test getting an existing project."""
    # First, create a project
    mcp_tools._multi_agent_tools.create_project(
        project_id="test_project_2",
        name="Test Project 2",
        description="Another project for testing"
    )

    # Now, get the project
    result = mcp_tools._multi_agent_tools.get_project(project_id="test_project_2")
    assert result["success"]
    assert result["project"]["id"] == "test_project_2"

def test_get_nonexistent_project(mcp_tools):
    """Test getting a project that does not exist."""
    result = mcp_tools._multi_agent_tools.get_project(project_id="nonexistent_project")
    assert not result["success"]
    assert "not found" in result["error"]

def test_list_projects(mcp_tools):
    """Test listing all projects."""
    # Create a couple of projects
    mcp_tools._multi_agent_tools.create_project(
        project_id="proj1", name="Project 1"
    )
    mcp_tools._multi_agent_tools.create_project(
        project_id="proj2", name="Project 2"
    )

    result = mcp_tools._multi_agent_tools.list_projects()
    assert result["success"]
    assert result["count"] == 2
    project_ids = [p["id"] for p in result["projects"]]
    assert "proj1" in project_ids
    assert "proj2" in project_ids 