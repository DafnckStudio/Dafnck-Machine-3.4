#!/usr/bin/env python3
"""
Integration tests for YAML role system integration with task management.
Tests role assignment, persona generation, and integration with auto rule generation.
"""

import pytest
import json
from pathlib import Path
from typing import Dict, List, Any

import sys
import os

# Add the source directory to the path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent.parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

from fastmcp.task_management.infrastructure.services.legacy.role_manager import RoleManager
from fastmcp.task_management.infrastructure.services.legacy.models import AgentRole


class TestRoleIntegration:
    """Integration tests for role system with task management"""
    
    @pytest.fixture
    def project_lib_dir(self):
        """Get the actual project library directory"""
        project_root = Path(__file__).parent.parent.parent.parent
        lib_dir = project_root / "yaml-lib"
        return lib_dir
    
    @pytest.fixture
    def role_manager(self, project_lib_dir):
        """Create a role manager with actual project structure"""
        return RoleManager(project_lib_dir)
    
    def test_role_assignment_from_assignee(self, role_manager):
        """Test role assignment based on task assignee"""
        # Test various assignee mappings
        test_cases = [
            ("qa_engineer", "qa_engineer"),
            ("QA Engineer", "qa_engineer"),
            ("senior_developer", "senior_developer"),
            ("Lead Developer", "senior_developer"),
            ("task_planner", "task_planner"),
            ("Task Planner", "task_planner"),
            ("code_reviewer", "code_reviewer"),
            ("Code Reviewer", "code_reviewer")
        ]
        
        for assignee, expected_role in test_cases:
            actual_role = role_manager.get_role_from_assignee(assignee)
            assert actual_role == expected_role, f"Expected {expected_role} for {assignee}, got {actual_role}"
    
    def test_role_loading_for_task_assignees(self, role_manager):
        """Test loading roles for common task assignees"""
        common_assignees = ["qa_engineer", "senior_developer", "task_planner", "code_reviewer"]
        
        loaded_roles = role_manager.load_specific_roles(common_assignees)
        
        assert len(loaded_roles) == len(common_assignees)
        
        for assignee in common_assignees:
            assert assignee in loaded_roles
            role = loaded_roles[assignee]
            assert isinstance(role, AgentRole)
            assert role.name is not None
            assert role.persona is not None
            assert role.primary_focus is not None
    
    def test_persona_generation_from_yaml(self, role_manager):
        """Test persona generation from YAML role definitions"""
        if not role_manager.lib_dir.exists():
            pytest.skip("Project yaml-lib directory not found")
        
        # Load specific roles and test their personas
        roles_to_test = ["task_planner", "senior_developer", "qa_engineer"]
        loaded_roles = role_manager.load_specific_roles(roles_to_test)
        
        # Test task_planner persona
        if "task_planner" in loaded_roles:
            task_planner = loaded_roles["task_planner"]
            assert "Expert 📅 Task Planning Agent" in task_planner.persona
            assert "decomposing complex project requirements" in task_planner.primary_focus
        
        # Test senior_developer persona  
        if "senior_developer" in loaded_roles:
            senior_dev = loaded_roles["senior_developer"]
            assert "Expert 💻 Coding Agent (Feature Implementation)" in senior_dev.persona
            assert "transforms detailed specifications and algorithmic designs" in senior_dev.primary_focus
        
        # Test qa_engineer persona
        if "qa_engineer" in loaded_roles:
            qa_engineer = loaded_roles["qa_engineer"]
            assert "Expert ⚙️ Functional Tester Agent" in qa_engineer.persona
            assert "Executes functional tests on software features" in qa_engineer.primary_focus
    
    def test_all_project_roles_loadable(self, role_manager):
        """Test that all project roles can be loaded successfully"""
        if not role_manager.lib_dir.exists():
            pytest.skip("Project yaml-lib directory not found")
        
        available_roles = role_manager.get_available_roles()
        
        # Should have all expected roles
        expected_roles = [
            'cache_engineer', 'cli_engineer', 'code_reviewer', 'context_engineer',
            'devops_engineer', 'metrics_engineer', 'platform_engineer', 'qa_engineer',
            'security_engineer', 'senior_developer', 'task_planner', 'technical_writer'
        ]
        
        for expected_role in expected_roles:
            assert expected_role in available_roles, f"Expected role {expected_role} not found"
        
        # Try to load all roles
        loaded_roles = role_manager.load_specific_roles(available_roles)
        
        assert len(loaded_roles) == len(available_roles)
        
        # Verify each role loaded correctly
        for role_name in available_roles:
            assert role_name in loaded_roles
            role = loaded_roles[role_name]
            assert isinstance(role, AgentRole)
            assert role.name is not None
            assert role.persona is not None
            assert role.primary_focus is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
