#!/usr/bin/env python3
"""
Comprehensive unit tests for YAML role system loading and integration.
Tests the RoleManager class and its YAML loading capabilities.
"""

import pytest
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from typing import Dict, List, Any

import sys
import os

# Add the source directory to the path
current_file = Path(__file__).resolve()
project_root = current_file.parent.parent.parent.parent
src_dir = project_root / "src"
sys.path.insert(0, str(src_dir))

from fastmcp.dhafnck_mcp.infrastructure.services.legacy.role_manager import RoleManager
from fastmcp.dhafnck_mcp.infrastructure.services.legacy.models import AgentRole


class TestYAMLRoleSystem:
    """Test suite for YAML role system functionality"""
    
    @pytest.fixture
    def mock_lib_dir(self, tmp_path):
        """Create a mock library directory structure"""
        lib_dir = tmp_path / "yaml-lib"
        lib_dir.mkdir()
        return lib_dir
    
    @pytest.fixture
    def sample_job_desc_data(self):
        """Sample job description YAML data"""
        return {
            'name': 'Test Role',
            'role': 'test_role',
            'persona': 'Expert test persona',
            'primary_focus': 'Testing and validation',
            'description': 'Test role description',
            'responsibilities': ['test responsibility 1', 'test responsibility 2'],
            'globs': ['**/*.py', '**/*.test.py'],
            'alwaysApply': False
        }
    
    @pytest.fixture
    def sample_rules_data(self):
        """Sample rules YAML data"""
        return {
            'rules': [
                'Follow test-driven development',
                'Write comprehensive tests',
                'Ensure code coverage'
            ]
        }
    
    @pytest.fixture
    def sample_context_data(self):
        """Sample context YAML data"""
        return {
            'instructions': [
                'Analyze test requirements',
                'Create test strategies',
                'Validate test coverage'
            ]
        }
    
    @pytest.fixture
    def sample_tools_data(self):
        """Sample tools YAML data"""
        return {
            'tools': [
                'Use pytest for testing',
                'Implement mocking where needed',
                'Create test fixtures'
            ]
        }
    
    def test_role_manager_initialization(self, mock_lib_dir):
        """Test RoleManager initialization"""
        role_manager = RoleManager(mock_lib_dir)
        
        assert role_manager.lib_dir == mock_lib_dir
        assert isinstance(role_manager.roles, dict)
        assert hasattr(role_manager, 'assignee_to_role_mapping')
    
    def test_get_available_roles_with_valid_directory(self, mock_lib_dir, sample_job_desc_data):
        """Test getting available roles from valid directory structure"""
        # Create role directories with job_desc.yaml files
        role_dirs = ['task_planner', 'senior_developer', 'qa_engineer']
        
        for role_dir in role_dirs:
            role_path = mock_lib_dir / role_dir
            role_path.mkdir()
            
            job_desc_file = role_path / "job_desc.yaml"
            with open(job_desc_file, 'w') as f:
                yaml.dump(sample_job_desc_data, f)
        
        role_manager = RoleManager(mock_lib_dir)
        available_roles = role_manager.get_available_roles()
        
        assert len(available_roles) == 3
        assert 'qa_engineer' in available_roles
        assert 'senior_developer' in available_roles
        assert 'task_planner' in available_roles
        assert available_roles == sorted(available_roles)  # Should be sorted
    
    def test_get_available_roles_with_missing_directory(self, tmp_path):
        """Test getting available roles when library directory doesn't exist"""
        non_existent_dir = tmp_path / "non_existent"
        role_manager = RoleManager(non_existent_dir)
        
        available_roles = role_manager.get_available_roles()
        
        # Should return fallback roles
        expected_fallback = ["senior_developer", "task_planner", "qa_engineer", "code_reviewer"]
        assert available_roles == expected_fallback
    
    def test_read_yaml_file_success(self, mock_lib_dir, sample_job_desc_data):
        """Test successful YAML file reading"""
        yaml_file = mock_lib_dir / "test.yaml"
        with open(yaml_file, 'w') as f:
            yaml.dump(sample_job_desc_data, f)
        
        role_manager = RoleManager(mock_lib_dir)
        result = role_manager._read_yaml_file(yaml_file)
        
        assert result == sample_job_desc_data
        assert result['name'] == 'Test Role'
        assert result['role'] == 'test_role'
    
    def test_read_yaml_file_failure(self, mock_lib_dir, capsys):
        """Test YAML file reading with invalid file"""
        non_existent_file = mock_lib_dir / "non_existent.yaml"
        
        role_manager = RoleManager(mock_lib_dir)
        result = role_manager._read_yaml_file(non_existent_file)
        
        assert result == {}
        
        # Check warning message was printed
        captured = capsys.readouterr()
        assert "Failed to read YAML file" in captured.out
    
    def test_read_yaml_file_malformed(self, mock_lib_dir, capsys):
        """Test YAML file reading with malformed YAML"""
        yaml_file = mock_lib_dir / "malformed.yaml"
        with open(yaml_file, 'w') as f:
            f.write("invalid: yaml: content: [unclosed")
        
        role_manager = RoleManager(mock_lib_dir)
        result = role_manager._read_yaml_file(yaml_file)
        
        assert result == {}
        
        # Check warning message was printed
        captured = capsys.readouterr()
        assert "Failed to read YAML file" in captured.out
    
    def test_load_rules_from_yaml_directory(self, mock_lib_dir, sample_rules_data):
        """Test loading rules from YAML directory"""
        rules_dir = mock_lib_dir / "rules"
        rules_dir.mkdir()
        
        # Create multiple rule files
        rule_file1 = rules_dir / "001_basic_rules.yaml"
        with open(rule_file1, 'w') as f:
            yaml.dump(sample_rules_data, f)
        
        rule_file2 = rules_dir / "002_advanced_rules.yaml"
        advanced_rules = {'rules': ['Advanced rule 1', 'Advanced rule 2']}
        with open(rule_file2, 'w') as f:
            yaml.dump(advanced_rules, f)
        
        role_manager = RoleManager(mock_lib_dir)
        rules = role_manager._load_rules_from_yaml_directory(rules_dir)
        
        assert len(rules) == 5  # 3 from basic + 2 from advanced
        assert 'Follow test-driven development' in rules
        assert 'Advanced rule 1' in rules
        assert 'Advanced rule 2' in rules
    
    def test_load_rules_from_nonexistent_directory(self, mock_lib_dir):
        """Test loading rules from non-existent directory"""
        non_existent_dir = mock_lib_dir / "non_existent"
        
        role_manager = RoleManager(mock_lib_dir)
        rules = role_manager._load_rules_from_yaml_directory(non_existent_dir)
        
        assert rules == []
    
    def test_load_context_instructions_from_yaml_directory(self, mock_lib_dir, sample_context_data):
        """Test loading context instructions from YAML directory"""
        contexts_dir = mock_lib_dir / "contexts"
        contexts_dir.mkdir()
        
        context_file = contexts_dir / "001_context.yaml"
        with open(context_file, 'w') as f:
            yaml.dump(sample_context_data, f)
        
        role_manager = RoleManager(mock_lib_dir)
        instructions = role_manager._load_context_instructions_from_yaml_directory(contexts_dir)
        
        assert len(instructions) == 3
        assert 'Analyze test requirements' in instructions
        assert 'Create test strategies' in instructions
        assert 'Validate test coverage' in instructions
    
    def test_load_tools_guidance_from_yaml_directory(self, mock_lib_dir, sample_tools_data):
        """Test loading tools guidance from YAML directory"""
        tools_dir = mock_lib_dir / "tools"
        tools_dir.mkdir()
        
        tools_file = tools_dir / "001_tools.yaml"
        with open(tools_file, 'w') as f:
            yaml.dump(sample_tools_data, f)
        
        role_manager = RoleManager(mock_lib_dir)
        guidance = role_manager._load_tools_guidance_from_yaml_directory(tools_dir)
        
        assert len(guidance) == 3
        assert any('Use pytest for testing' in item for item in guidance)
        assert any('001_tools.yaml' in item for item in guidance)
    
    def test_load_role_from_directory_complete(self, mock_lib_dir, sample_job_desc_data, 
                                             sample_rules_data, sample_context_data, sample_tools_data):
        """Test loading a complete role from directory structure"""
        role_dir = mock_lib_dir / "test_role"
        role_dir.mkdir()
        
        # Create job_desc.yaml
        job_desc_file = role_dir / "job_desc.yaml"
        with open(job_desc_file, 'w') as f:
            yaml.dump(sample_job_desc_data, f)
        
        # Create rules directory and file
        rules_dir = role_dir / "rules"
        rules_dir.mkdir()
        rules_file = rules_dir / "001_rules.yaml"
        with open(rules_file, 'w') as f:
            yaml.dump(sample_rules_data, f)
        
        # Create contexts directory and file
        contexts_dir = role_dir / "contexts"
        contexts_dir.mkdir()
        context_file = contexts_dir / "001_context.yaml"
        with open(context_file, 'w') as f:
            yaml.dump(sample_context_data, f)
        
        # Create tools directory and file
        tools_dir = role_dir / "tools"
        tools_dir.mkdir()
        tools_file = tools_dir / "001_tools.yaml"
        with open(tools_file, 'w') as f:
            yaml.dump(sample_tools_data, f)
        
        role_manager = RoleManager(mock_lib_dir)
        role = role_manager._load_role_from_directory(role_dir)
        
        assert role is not None
        assert isinstance(role, AgentRole)
        assert role.name == 'Test Role'
        assert role.persona == 'Expert test persona'
        assert role.primary_focus == 'Testing and validation'
        assert len(role.rules) == 3
        assert len(role.context_instructions) == 3
        assert len(role.tools_guidance) == 3
    
    def test_load_role_from_directory_missing_job_desc(self, mock_lib_dir):
        """Test loading role from directory without job_desc.yaml"""
        role_dir = mock_lib_dir / "test_role"
        role_dir.mkdir()
        
        role_manager = RoleManager(mock_lib_dir)
        role = role_manager._load_role_from_directory(role_dir)
        
        assert role is None
    
    def test_load_specific_roles(self, mock_lib_dir, sample_job_desc_data):
        """Test loading specific roles by name"""
        # Create multiple role directories
        role_names = ['task_planner', 'senior_developer', 'qa_engineer']
        
        for role_name in role_names:
            role_dir = mock_lib_dir / role_name
            role_dir.mkdir()
            
            job_desc_data = sample_job_desc_data.copy()
            job_desc_data['name'] = f"Test {role_name.replace('_', ' ').title()}"
            job_desc_data['role'] = role_name
            
            job_desc_file = role_dir / "job_desc.yaml"
            with open(job_desc_file, 'w') as f:
                yaml.dump(job_desc_data, f)
        
        role_manager = RoleManager(mock_lib_dir)
        loaded_roles = role_manager.load_specific_roles(['task_planner', 'qa_engineer'])
        
        assert len(loaded_roles) == 2
        assert 'task_planner' in loaded_roles
        assert 'qa_engineer' in loaded_roles
        assert 'senior_developer' not in loaded_roles
        
        # Check role properties
        task_planner_role = loaded_roles['task_planner']
        assert task_planner_role.name == "Test Task Planner"
        assert task_planner_role.persona == 'Expert test persona'
    
    def test_assignee_to_role_mapping(self, mock_lib_dir):
        """Test assignee to role mapping functionality"""
        role_manager = RoleManager(mock_lib_dir)
        
        # Test various assignee mappings
        assert role_manager.get_role_from_assignee("Lead Developer") == "senior_developer"
        assert role_manager.get_role_from_assignee("QA Engineer") == "qa_engineer"
        assert role_manager.get_role_from_assignee("Task Planner") == "task_planner"
        assert role_manager.get_role_from_assignee("Code Reviewer") == "code_reviewer"
        assert role_manager.get_role_from_assignee("Unknown Role") is None
    
    def test_create_mock_role(self, mock_lib_dir):
        """Test mock role creation for testing environments"""
        role_manager = RoleManager(mock_lib_dir)
        
        mock_role = role_manager._create_mock_role("qa_engineer")
        
        assert isinstance(mock_role, AgentRole)
        # The mock role name might be simplified, so check for key components
        assert "qa" in mock_role.name.lower() or "engineer" in mock_role.name.lower()
        assert "quality" in mock_role.persona.lower() or "test" in mock_role.persona.lower()
        assert len(mock_role.rules) > 0
        # Mock roles might not have context instructions, so just check they exist as lists
        assert isinstance(mock_role.context_instructions, list)
        assert isinstance(mock_role.tools_guidance, list)
    
    def test_yaml_structure_variations(self, mock_lib_dir):
        """Test handling of different YAML structure variations"""
        rules_dir = mock_lib_dir / "rules"
        rules_dir.mkdir()
        
        # Test direct list structure
        rule_file1 = rules_dir / "001_direct_list.yaml"
        with open(rule_file1, 'w') as f:
            yaml.dump(['Direct rule 1', 'Direct rule 2'], f)
        
        # Test items structure
        rule_file2 = rules_dir / "002_items_structure.yaml"
        with open(rule_file2, 'w') as f:
            yaml.dump({'items': ['Item rule 1', 'Item rule 2']}, f)
        
        # Test single string
        rule_file3 = rules_dir / "003_single_string.yaml"
        with open(rule_file3, 'w') as f:
            yaml.dump('Single string rule', f)
        
        role_manager = RoleManager(mock_lib_dir)
        rules = role_manager._load_rules_from_yaml_directory(rules_dir)
        
        assert 'Direct rule 1' in rules
        assert 'Direct rule 2' in rules
        assert 'Item rule 1' in rules
        assert 'Item rule 2' in rules
        assert 'Single string rule' in rules
    
    def test_error_handling_empty_yaml(self, mock_lib_dir):
        """Test error handling for empty YAML files"""
        rules_dir = mock_lib_dir / "rules"
        rules_dir.mkdir()
        
        # Create empty YAML file
        empty_file = rules_dir / "empty.yaml"
        empty_file.touch()
        
        role_manager = RoleManager(mock_lib_dir)
        rules = role_manager._load_rules_from_yaml_directory(rules_dir)
        
        # Should handle empty files gracefully
        assert isinstance(rules, list)
    
    def test_recursive_yaml_loading(self, mock_lib_dir):
        """Test recursive YAML loading from subdirectories"""
        rules_dir = mock_lib_dir / "rules"
        rules_dir.mkdir()
        
        # Create subdirectory with YAML files
        sub_dir = rules_dir / "subdirectory"
        sub_dir.mkdir()
        
        # Create YAML file in subdirectory
        sub_file = sub_dir / "sub_rules.yaml"
        with open(sub_file, 'w') as f:
            yaml.dump({'rules': ['Subdirectory rule']}, f)
        
        role_manager = RoleManager(mock_lib_dir)
        rules = role_manager._load_rules_from_yaml_directory(rules_dir)
        
        assert 'Subdirectory rule' in rules


class TestYAMLRoleIntegration:
    """Integration tests for YAML role system with actual project structure"""
    
    def test_load_actual_project_roles(self):
        """Test loading roles from actual project structure"""
        # Use actual project directory
        project_root = Path(__file__).parent.parent.parent.parent
        lib_dir = project_root / "yaml-lib"
        
        if not lib_dir.exists():
            pytest.skip("Project yaml-lib directory not found")
        
        role_manager = RoleManager(lib_dir)
        available_roles = role_manager.get_available_roles()
        
        # Should find the actual roles in the project
        expected_roles = [
            'cache_engineer', 'cli_engineer', 'code_reviewer', 'context_engineer',
            'devops_engineer', 'metrics_engineer', 'platform_engineer', 'qa_engineer',
            'security_engineer', 'senior_developer', 'task_planner', 'technical_writer'
        ]
        
        for expected_role in expected_roles:
            assert expected_role in available_roles, f"Expected role {expected_role} not found"
    
    def test_load_actual_task_planner_role(self):
        """Test loading actual task_planner role from project"""
        project_root = Path(__file__).parent.parent.parent.parent
        lib_dir = project_root / "yaml-lib"
        
        if not lib_dir.exists():
            pytest.skip("Project yaml-lib directory not found")
        
        role_manager = RoleManager(lib_dir)
        loaded_roles = role_manager.load_specific_roles(['task_planner'])
        
        assert 'task_planner' in loaded_roles
        
        task_planner = loaded_roles['task_planner']
        assert task_planner.name == "📅 Task Planning Agent"
        assert "Expert 📅 Task Planning Agent" in task_planner.persona
        assert "decomposing complex project requirements into structured, actionable task hierarchies" in task_planner.primary_focus
        assert len(task_planner.rules) > 0
        assert len(task_planner.context_instructions) > 0
    
    def test_load_actual_senior_developer_role(self):
        """Test loading actual senior_developer role from project"""
        project_root = Path(__file__).parent.parent.parent.parent
        lib_dir = project_root / "yaml-lib"
        
        if not lib_dir.exists():
            pytest.skip("Project yaml-lib directory not found")
        
        role_manager = RoleManager(lib_dir)
        loaded_roles = role_manager.load_specific_roles(['senior_developer'])
        
        assert 'senior_developer' in loaded_roles
        
        senior_dev = loaded_roles['senior_developer']
        assert senior_dev.name == "💻 Coding Agent (Feature Implementation)"
        assert "Expert 💻 Coding Agent (Feature Implementation)" in senior_dev.persona
        assert "transforms detailed specifications and algorithmic designs into high-quality, production-ready code" in senior_dev.primary_focus
        assert len(senior_dev.rules) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 