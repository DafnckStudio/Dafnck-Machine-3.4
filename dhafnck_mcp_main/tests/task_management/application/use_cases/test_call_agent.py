"""Tests for CallAgentUseCase"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


import os
import tempfile
import pytest
import logging
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
import yaml

from fastmcp.task_management.application.use_cases.call_agent import CallAgentUseCase


class TestCallAgentUseCase:
    """Test cases for CallAgentUseCase"""

    @pytest.fixture
    def temp_agent_dir(self):
        """Create a temporary directory structure for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            cursor_agent_dir = Path(temp_dir)
            yaml_lib_dir = cursor_agent_dir / "yaml-lib"
            yaml_lib_dir.mkdir()
            
            # Create test agent directory
            test_agent_dir = yaml_lib_dir / "test_agent"
            test_agent_dir.mkdir()
            
            # Create test YAML file
            test_yaml = test_agent_dir / "job_desc.yaml"
            test_yaml.write_text("""
job_desc:
  role: "Test Agent"
  description: "A test agent for testing"
  capabilities:
    - "testing"
    - "validation"
""")
            
            yield cursor_agent_dir

    @pytest.fixture
    def call_agent_use_case(self, temp_agent_dir):
        """Create CallAgentUseCase instance with temp directory"""
        return CallAgentUseCase(temp_agent_dir)

    def test_execute_success_with_valid_agent(self, call_agent_use_case, temp_agent_dir):
        """Test successful execution with valid agent"""
        with patch('fastmcp.task_management.application.use_cases.call_agent.generate_docs_for_assignees') as mock_generate:
            result = call_agent_use_case.execute("test_agent")
            
            assert result["success"] is True
            assert "agent_info" in result
            assert "role" in result["agent_info"]
            assert result["agent_info"]["role"] == "Test Agent"
            assert "capabilities" in result["agent_info"]
            assert "testing" in result["agent_info"]["capabilities"]
            
            # Verify docs generation was called
            mock_generate.assert_called_once_with(["test_agent"], clear_all=False)

    def test_execute_agent_directory_not_found(self, call_agent_use_case):
        """Test execution with non-existent agent directory"""
        result = call_agent_use_case.execute("nonexistent_agent")
        
        assert result["success"] is False
        assert "Agent directory not found" in result["error"]

    def test_execute_no_yaml_files_found(self, temp_agent_dir):
        """Test execution when agent directory exists but has no YAML files"""
        # Create empty agent directory
        empty_agent_dir = temp_agent_dir / "yaml-lib" / "empty_agent"
        empty_agent_dir.mkdir(parents=True)
        
        call_agent_use_case = CallAgentUseCase(temp_agent_dir)
        result = call_agent_use_case.execute("empty_agent")
        
        assert result["success"] is False
        assert "No YAML files found for agent" in result["error"]

    def test_execute_with_nested_yaml_files(self, temp_agent_dir):
        """Test execution with YAML files in nested directories"""
        # Create nested directory structure
        agent_dir = temp_agent_dir / "yaml-lib" / "nested_agent"
        contexts_dir = agent_dir / "contexts"
        rules_dir = agent_dir / "rules"
        contexts_dir.mkdir(parents=True)
        rules_dir.mkdir(parents=True)
        
        # Create YAML files in different directories
        (contexts_dir / "context.yaml").write_text("""
context_info:
  environment: "test"
  version: "1.0"
""")
        
        (rules_dir / "rules.yaml").write_text("""
rules:
  - "Always test thoroughly"
  - "Document everything"
""")
        
        call_agent_use_case = CallAgentUseCase(temp_agent_dir)
        
        with patch('fastmcp.task_management.application.use_cases.call_agent.generate_docs_for_assignees'):
            result = call_agent_use_case.execute("nested_agent")
            
            assert result["success"] is True
            assert "agent_info" in result
            assert "context_info" in result["agent_info"]
            assert "environment" in result["agent_info"]["context_info"]
            assert "rules" in result["agent_info"]

    def test_execute_with_invalid_yaml_file(self, temp_agent_dir):
        """Test execution with invalid YAML file"""
        # Create agent directory with invalid YAML
        agent_dir = temp_agent_dir / "yaml-lib" / "invalid_agent"
        agent_dir.mkdir(parents=True)
        
        invalid_yaml = agent_dir / "invalid.yaml"
        invalid_yaml.write_text("invalid: yaml: content: [")
        
        call_agent_use_case = CallAgentUseCase(temp_agent_dir)
        
        with patch('fastmcp.task_management.application.use_cases.call_agent.generate_docs_for_assignees'):
            result = call_agent_use_case.execute("invalid_agent")
            
            # Should still succeed but with error info in the content
            assert result["success"] is True
            assert "agent_info" in result

    def test_execute_with_docs_generation_failure(self, call_agent_use_case):
        """Test execution when docs generation fails"""
        with patch('fastmcp.task_management.application.use_cases.call_agent.generate_docs_for_assignees') as mock_generate:
            mock_generate.side_effect = Exception("Docs generation failed")
            
            result = call_agent_use_case.execute("test_agent")
            
            # Should still succeed even if docs generation fails
            assert result["success"] is True
            assert "agent_info" in result

    def test_execute_with_file_read_permission_error(self, temp_agent_dir):
        """Test execution with file permission error"""
        agent_dir = temp_agent_dir / "yaml-lib" / "permission_agent"
        agent_dir.mkdir(parents=True)
        
        call_agent_use_case = CallAgentUseCase(temp_agent_dir)
        
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            result = call_agent_use_case.execute("permission_agent")
            
            assert result["success"] is False
            assert "No YAML files found for agent" in result["error"]

    def test_execute_with_yaml_content_variations(self, temp_agent_dir):
        """Test execution with different YAML content structures"""
        agent_dir = temp_agent_dir / "yaml-lib" / "varied_agent"
        agent_dir.mkdir(parents=True)
        
        # Create YAML with single key matching filename
        (agent_dir / "job_desc.yaml").write_text("""
job_desc:
  role: "Varied Agent"
  type: "single_key"
""")
        
        # Create YAML with multiple top-level keys
        (agent_dir / "config.yaml").write_text("""
setting1: "value1"
setting2: "value2"
nested:
  key: "value"
""")
        
        # Create YAML with non-dict content
        (agent_dir / "simple.yaml").write_text("""
simple: "just a string"
""")
        
        call_agent_use_case = CallAgentUseCase(temp_agent_dir)
        
        with patch('fastmcp.task_management.application.use_cases.call_agent.generate_docs_for_assignees'):
            result = call_agent_use_case.execute("varied_agent")
            
            assert result["success"] is True
            assert "agent_info" in result
            assert "role" in result["agent_info"]
            assert "setting1" in result["agent_info"]
            assert "simple" in result["agent_info"]

    def test_execute_with_os_walk_exception(self, call_agent_use_case):
        """Test execution when os.walk raises an exception"""
        with patch('os.walk', side_effect=OSError("OS error")):
            result = call_agent_use_case.execute("test_agent")
            
            assert result["success"] is False
            assert "Failed to retrieve agent information" in result["error"]

    def test_execute_with_yaml_load_exception(self, temp_agent_dir):
        """Test execution when YAML loading raises an exception"""
        agent_dir = temp_agent_dir / "yaml-lib" / "error_agent"
        agent_dir.mkdir(parents=True)
        
        (agent_dir / "test.yaml").write_text("valid: yaml")
        
        call_agent_use_case = CallAgentUseCase(temp_agent_dir)
        
        with patch('yaml.safe_load', side_effect=yaml.YAMLError("YAML error")):
            with patch('fastmcp.task_management.application.use_cases.call_agent.generate_docs_for_assignees'):
                result = call_agent_use_case.execute("error_agent")
                
                # Should still succeed with error info
                assert result["success"] is True

    def test_execute_logs_debug_info(self, call_agent_use_case, caplog):
        """Test that debug information is logged"""
        caplog.set_level(logging.DEBUG)
        with patch('fastmcp.task_management.application.use_cases.call_agent.generate_docs_for_assignees'):
            result = call_agent_use_case.execute("test_agent")
            
            assert "Looking for agent in:" in caplog.text
            if result["success"]:
                assert "Generated agent documentation for:" in caplog.text

    def test_execute_handles_empty_yaml_content(self, temp_agent_dir):
        """Test execution with empty YAML files"""
        agent_dir = temp_agent_dir / "yaml-lib" / "empty_yaml_agent"
        agent_dir.mkdir(parents=True)
        
        # Create empty YAML file
        (agent_dir / "empty.yaml").write_text("")
        
        call_agent_use_case = CallAgentUseCase(temp_agent_dir)
        
        with patch('fastmcp.task_management.application.use_cases.call_agent.generate_docs_for_assignees'):
            result = call_agent_use_case.execute("empty_yaml_agent")
            
            # Should handle empty YAML gracefully
            assert result["success"] is False
            assert "No YAML files found for agent" in result["error"] 