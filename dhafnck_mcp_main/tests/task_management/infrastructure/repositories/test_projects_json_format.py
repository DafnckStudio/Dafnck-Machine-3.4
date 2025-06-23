"""
Integration test to verify that the actual projects.json file uses simplified agent format.

This test validates that the real projects.json file in cursor_agent/.cursor/rules/brain/
contains only simplified agent registrations with id, name, and call_agent fields.
"""
import json
import os
import pytest


class TestProjectsJsonFormat:
    """Test that the actual projects.json file uses simplified agent format"""
    
    @pytest.fixture
    def projects_file_path(self):
        """Get the path to the actual projects.json file"""
        return "../cursor_agent/.cursor/rules/brain/projects.json"
    
    def test_projects_file_exists(self, projects_file_path):
        """Test that the projects.json file exists"""
        assert os.path.exists(projects_file_path), f"Projects file not found at {projects_file_path}"
    
    def test_projects_file_is_valid_json(self, projects_file_path):
        """Test that the projects.json file contains valid JSON"""
        try:
            with open(projects_file_path, 'r') as f:
                data = json.load(f)
            assert isinstance(data, dict), "Projects file should contain a JSON object"
        except json.JSONDecodeError as e:
            pytest.fail(f"Projects file contains invalid JSON: {e}")
    
    def test_all_agents_use_simplified_format(self, projects_file_path):
        """Test that all registered agents use the simplified format (id, name, call_agent only)"""
        with open(projects_file_path, 'r') as f:
            projects_data = json.load(f)
        
        expected_fields = {"id", "name", "call_agent"}
        unwanted_fields = {"description", "capabilities", "specializations", "preferred_languages", "max_concurrent_tasks"}
        
        agents_found = 0
        
        for project_id, project_data in projects_data.items():
            if "registered_agents" not in project_data:
                continue
            
            registered_agents = project_data["registered_agents"]
            
            for agent_id, agent_data in registered_agents.items():
                agents_found += 1
                
                # Check that only expected fields are present
                actual_fields = set(agent_data.keys())
                assert actual_fields == expected_fields, (
                    f"Project '{project_id}', Agent '{agent_id}' has unexpected fields. "
                    f"Expected: {expected_fields}, Got: {actual_fields}"
                )
                
                # Check that no unwanted fields are present
                for unwanted_field in unwanted_fields:
                    assert unwanted_field not in agent_data, (
                        f"Project '{project_id}', Agent '{agent_id}' contains unwanted field '{unwanted_field}'"
                    )
                
                # Validate field values
                assert isinstance(agent_data["id"], str), f"Agent {agent_id} id must be string"
                assert isinstance(agent_data["name"], str), f"Agent {agent_id} name must be string"
                assert isinstance(agent_data["call_agent"], str), f"Agent {agent_id} call_agent must be string"
                assert agent_data["call_agent"].startswith("@"), f"Agent {agent_id} call_agent must start with @"
                assert agent_data["id"] == agent_id, f"Agent {agent_id} id field must match dictionary key"
        
        # Ensure we actually tested some agents
        assert agents_found > 0, "No agents found in projects.json file"
        print(f"Successfully validated {agents_found} agents using simplified format")
    
    def test_specific_agent_examples(self, projects_file_path):
        """Test specific agents mentioned in the user's request"""
        with open(projects_file_path, 'r') as f:
            projects_data = json.load(f)
        
        # Check for mcp_architect agent in dhafnck_mcp_main project
        if "dhafnck_mcp_main" in projects_data:
            project = projects_data["dhafnck_mcp_main"]
            if "registered_agents" in project and "mcp_architect" in project["registered_agents"]:
                mcp_architect = project["registered_agents"]["mcp_architect"]
                
                # Verify the exact format the user requested
                expected_mcp_architect = {
                    "id": "mcp_architect",
                    "name": "MCP System Architect",
                    "call_agent": "@mcp_architect_agent"
                }
                
                assert mcp_architect == expected_mcp_architect, (
                    f"mcp_architect agent doesn't match expected format. "
                    f"Expected: {expected_mcp_architect}, Got: {mcp_architect}"
                )
    
    def test_no_legacy_complex_agents_remain(self, projects_file_path):
        """Test that no agents with complex format remain in the file"""
        with open(projects_file_path, 'r') as f:
            projects_data = json.load(f)
        
        complex_agents_found = []
        
        for project_id, project_data in projects_data.items():
            if "registered_agents" not in project_data:
                continue
            
            registered_agents = project_data["registered_agents"]
            
            for agent_id, agent_data in registered_agents.items():
                # Check if agent has more than 3 fields or any complex fields
                if (len(agent_data) > 3 or 
                    any(field in agent_data for field in 
                        ["description", "capabilities", "specializations", "preferred_languages", "max_concurrent_tasks"])):
                    complex_agents_found.append(f"{project_id}.{agent_id}")
        
        assert len(complex_agents_found) == 0, (
            f"Found {len(complex_agents_found)} agents still using complex format: {complex_agents_found}"
        )
    
    def test_call_agent_format_consistency(self, projects_file_path):
        """Test that all call_agent fields follow the expected format"""
        with open(projects_file_path, 'r') as f:
            projects_data = json.load(f)
        
        for project_id, project_data in projects_data.items():
            if "registered_agents" not in project_data:
                continue
            
            registered_agents = project_data["registered_agents"]
            
            for agent_id, agent_data in registered_agents.items():
                call_agent = agent_data["call_agent"]
                
                # Should start with @
                assert call_agent.startswith("@"), (
                    f"Agent {project_id}.{agent_id} call_agent '{call_agent}' should start with @"
                )
                
                # Should end with _agent
                assert call_agent.endswith("_agent"), (
                    f"Agent {project_id}.{agent_id} call_agent '{call_agent}' should end with _agent"
                )
                
                # Should not contain spaces
                assert " " not in call_agent, (
                    f"Agent {project_id}.{agent_id} call_agent '{call_agent}' should not contain spaces"
                ) 