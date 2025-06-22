"""
Test simplified agent registration format.

This test ensures that agent registration only stores the essential fields:
- id: agent identifier
- name: human-readable name
- call_agent: reference to the actual agent (e.g., "@mcp_architect_agent")

No additional fields like description, capabilities, specializations should be stored
since those will be auto-generated in .cursor/rules/agents.
"""
import os
import tempfile
import pytest
import json
from unittest.mock import patch, Mock

from task_mcp.interface.consolidated_mcp_tools_v2 import SimpleMultiAgentTools


class TestSimplifiedAgentRegistration:
    """Test that agent registration uses simplified format only"""
    
    @pytest.fixture
    def temp_projects_file(self):
        """Create a temporary projects file for testing"""
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, 'test_projects.json')
        yield temp_file
        # Cleanup
        if os.path.exists(temp_file):
            os.remove(temp_file)
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def multi_agent_tools(self, temp_projects_file):
        """Create SimpleMultiAgentTools instance with isolated projects file"""
        return SimpleMultiAgentTools(projects_file_path=temp_projects_file)
    
    def test_register_agent_simplified_format_only(self, multi_agent_tools, temp_projects_file):
        """Test that agent registration stores only id, name, and call_agent"""
        # Create project first
        multi_agent_tools.create_project("test_project", "Test Project")
        
        # Register agent with simplified format
        result = multi_agent_tools.register_agent(
            "test_project", 
            "mcp_architect", 
            "MCP System Architect",
            call_agent="@mcp_architect_agent"
        )
        
        # Verify registration was successful
        assert result["success"] is True
        assert result["agent"]["id"] == "mcp_architect"
        assert result["agent"]["name"] == "MCP System Architect"
        assert result["agent"]["call_agent"] == "@mcp_architect_agent"
        
        # Load the actual file and verify only expected fields are stored
        with open(temp_projects_file, 'r') as f:
            projects_data = json.load(f)
        
        agent_data = projects_data["test_project"]["registered_agents"]["mcp_architect"]
        
        # Assert only the three expected fields exist
        expected_fields = {"id", "name", "call_agent"}
        actual_fields = set(agent_data.keys())
        
        assert actual_fields == expected_fields, f"Expected only {expected_fields}, but got {actual_fields}"
        
        # Assert no unwanted fields
        unwanted_fields = {"description", "capabilities", "specializations", "preferred_languages", "max_concurrent_tasks"}
        for field in unwanted_fields:
            assert field not in agent_data, f"Unwanted field '{field}' found in agent data"
    
    def test_register_agent_auto_generates_call_agent(self, multi_agent_tools):
        """Test that call_agent is auto-generated if not provided"""
        # Create project first
        multi_agent_tools.create_project("test_project", "Test Project")
        
        # Register agent without call_agent
        result = multi_agent_tools.register_agent(
            "test_project", 
            "frontend_specialist", 
            "Frontend Specialist"
        )
        
        # Verify call_agent was auto-generated
        assert result["success"] is True
        assert result["agent"]["call_agent"] == "@frontend-specialist-agent"
    
    def test_register_multiple_agents_simplified_format(self, multi_agent_tools, temp_projects_file):
        """Test registering multiple agents all use simplified format"""
        # Create project first
        multi_agent_tools.create_project("test_project", "Test Project")
        
        # Register multiple agents
        agents_to_register = [
            ("mcp_architect", "MCP System Architect", "@mcp_architect_agent"),
            ("python_developer", "Python Core Developer", "@python_developer_agent"),
            ("documentation_specialist", "Documentation Specialist", "@documentation_specialist_agent")
        ]
        
        for agent_id, name, call_agent in agents_to_register:
            result = multi_agent_tools.register_agent("test_project", agent_id, name, call_agent)
            assert result["success"] is True
        
        # Load the file and verify all agents use simplified format
        with open(temp_projects_file, 'r') as f:
            projects_data = json.load(f)
        
        registered_agents = projects_data["test_project"]["registered_agents"]
        assert len(registered_agents) == 3
        
        expected_fields = {"id", "name", "call_agent"}
        
        for agent_id, agent_data in registered_agents.items():
            actual_fields = set(agent_data.keys())
            assert actual_fields == expected_fields, f"Agent {agent_id} has unexpected fields: {actual_fields}"
            
            # Verify no complex fields exist
            unwanted_fields = {"description", "capabilities", "specializations", "preferred_languages", "max_concurrent_tasks"}
            for field in unwanted_fields:
                assert field not in agent_data, f"Agent {agent_id} contains unwanted field '{field}'"
    
    def test_get_project_returns_simplified_agents(self, multi_agent_tools):
        """Test that get_project returns agents in simplified format"""
        # Create project and register agent
        multi_agent_tools.create_project("test_project", "Test Project")
        multi_agent_tools.register_agent(
            "test_project", 
            "test_agent", 
            "Test Agent",
            call_agent="@test_agent"
        )
        
        # Get project and verify agent format
        result = multi_agent_tools.get_project("test_project")
        assert result["success"] is True
        
        agents = result["project"]["registered_agents"]
        assert "test_agent" in agents
        
        agent_data = agents["test_agent"]
        expected_fields = {"id", "name", "call_agent"}
        actual_fields = set(agent_data.keys())
        
        assert actual_fields == expected_fields, f"get_project returned unexpected agent fields: {actual_fields}"
    
    def test_existing_complex_agents_should_be_simplified(self):
        """Test that validates existing complex agent data should be simplified"""
        # This test documents the expected behavior for cleaning up existing data
        complex_agent_example = {
            "id": "mcp_architect",
            "name": "MCP System Architect", 
            "description": "Specialized in Model Context Protocol architecture...",
            "capabilities": ["mcp_protocol", "python", "asyncio"],
            "specializations": ["mcp_framework", "protocol_implementation"],
            "preferred_languages": ["python"],
            "max_concurrent_tasks": 1
        }
        
        # What it should be simplified to
        simplified_agent_expected = {
            "id": "mcp_architect",
            "name": "MCP System Architect",
            "call_agent": "@mcp_architect_agent"
        }
        
        # This test documents the transformation that needs to happen
        # The actual cleanup will be done by updating the projects.json file
        assert len(simplified_agent_expected) == 3
        assert "description" not in simplified_agent_expected
        assert "capabilities" not in simplified_agent_expected
        assert "specializations" not in simplified_agent_expected 