import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


import pytest
import os
import yaml
from pathlib import Path
import shutil
from unittest.mock import patch, Mock

from fastmcp.task_management.infrastructure.services.agent_doc_generator import generate_agent_docs, generate_docs_for_assignees
from fastmcp.task_management.application.use_cases.get_task import GetTaskUseCase
from fastmcp.task_management.domain.events import TaskRetrieved
from fastmcp.task_management.domain.value_objects import TaskId


@pytest.fixture
def temp_agent_setup():
    """Setup temporary directories for agent YAMLs and output docs."""
    temp_root = Path("./temp_test_agent_root")
    agent_yaml_lib_path = temp_root / "cursor_agent/yaml-lib"
    agents_output_dir_path = temp_root / ".cursor/rules/agents"

    # Create dummy agent files for coding_agent
    coding_agent_dir = agent_yaml_lib_path / "coding_agent"
    coding_agent_dir.mkdir(parents=True, exist_ok=True)
    with open(coding_agent_dir / "job_desc.yaml", "w") as f:
        yaml.dump({
            "name": "Coding Agent", 
            "slug": "coding_agent",
            "role_definition": "To write code.",
            "when_to_use": "For coding tasks.",
            "groups": ["development"]
        }, f)
    
    # Add dummy context file for coding_agent
    (coding_agent_dir / "contexts").mkdir(exist_ok=True)
    with open(coding_agent_dir / "contexts" / "context1.yaml", "w") as f:
        yaml.dump({"key": "value"}, f)

    # Create dummy agent files for design_agent
    design_agent_dir = agent_yaml_lib_path / "design_agent"
    design_agent_dir.mkdir(parents=True, exist_ok=True)
    with open(design_agent_dir / "job_desc.yaml", "w") as f:
        yaml.dump({"name": "Design Agent", "slug": "design_agent"}, f)

    # Patch the constants
    with patch('fastmcp.task_management.infrastructure.services.agent_doc_generator.AGENT_YAML_LIB', agent_yaml_lib_path), \
         patch('fastmcp.task_management.infrastructure.services.agent_doc_generator.AGENTS_OUTPUT_DIR', agents_output_dir_path):
        yield agent_yaml_lib_path, agents_output_dir_path

    shutil.rmtree(temp_root)


class TestAgentDocGeneration:

    def test_generate_agent_docs_creates_file_with_details(self, temp_agent_setup):
        _, agents_output_dir_path = temp_agent_setup
        
        generate_agent_docs(agent_name="coding_agent")
        
        expected_file = agents_output_dir_path / "coding_agent.mdc"
        assert expected_file.exists()
        with open(expected_file, 'r') as f:
            content = f.read()
        
        assert "# Coding Agent" in content
        assert "**Slug:** `coding_agent`" in content
        assert "**Role Definition:** To write code." in content
        assert "## Contexts" in content
        assert "### context1" in content
        assert "key: value" in content

    def test_generate_agent_docs_handles_non_existent_agent(self, temp_agent_setup):
        _, agents_output_dir_path = temp_agent_setup
        
        generate_agent_docs(agent_name="non_existent_agent")
        
        expected_file = agents_output_dir_path / "non_existent_agent.mdc"
        assert not expected_file.exists()

    def test_generate_docs_for_assignees_with_clear_all(self, temp_agent_setup):
        agent_yaml_lib_path, agents_output_dir_path = temp_agent_setup
        
        # Pre-create a dummy file
        dummy_file = agents_output_dir_path / "stale_doc.mdc"
        agents_output_dir_path.mkdir(parents=True, exist_ok=True)
        dummy_file.touch()

        generate_docs_for_assignees(["@design_agent"], clear_all=True)

        assert not dummy_file.exists()
        expected_file = agents_output_dir_path / "design_agent.mdc"
        assert expected_file.exists()

    def test_generate_docs_for_assignees_simple(self, temp_agent_setup):
        _, agents_output_dir_path = temp_agent_setup

        generate_docs_for_assignees(["@coding_agent"])

        expected_file = agents_output_dir_path / "coding_agent.mdc"
        assert expected_file.exists()
        with open(expected_file, 'r') as f:
            content = f.read()
        assert "# Coding Agent" in content

    def test_generate_docs_for_assignees_handles_no_at_sign(self, temp_agent_setup):
        _, agents_output_dir_path = temp_agent_setup

        generate_docs_for_assignees(["design_agent"])

        expected_file = agents_output_dir_path / "design_agent.mdc"
        assert expected_file.exists()

    def test_generate_docs_for_assignees_adds_agent_suffix(self, temp_agent_setup):
        _, agents_output_dir_path = temp_agent_setup

        generate_docs_for_assignees(["coding"])

        expected_file = agents_output_dir_path / "coding_agent.mdc"
        assert expected_file.exists()

    def test_generate_docs_for_assignees_unique(self, temp_agent_setup):
        _, agents_output_dir_path = temp_agent_setup

        generate_docs_for_assignees(["@coding", "coding_agent", "@coding_agent"])

        expected_file = agents_output_dir_path / "coding_agent.mdc"
        assert expected_file.exists()
        
        # Check that only one file was created
        generated_files = list(agents_output_dir_path.glob("*.mdc"))
        assert len(generated_files) == 1

    def test_get_task_use_case_triggers_doc_generation(self, temp_agent_setup):
        mock_repo = Mock()
        mock_task = Mock()
        mock_task.assignees = ["@coding_agent"]
        mock_task.id = "mock_task_id"
        mock_task.get_events.return_value = [Mock(spec=TaskRetrieved)] # Simulate event
        mock_task.to_dict.return_value = {
            "id": "20240101001", "title": "Test Task", "description": "Test",
            "status": "todo", "priority": "medium", "details": "",
            "estimatedEffort": "", "assignees": ["@coding_agent"], "labels": [],
            "dependencies": [], "subtasks": [], "dueDate": None,
            "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"
        }
        mock_auto_rule_generator = Mock()

        use_case = GetTaskUseCase(mock_repo, mock_auto_rule_generator)
        mock_repo.find_by_id.return_value = mock_task
        valid_task_id = TaskId.from_int(1)

        with patch('fastmcp.task_management.application.use_cases.get_task.generate_docs_for_assignees') as mock_generate:
            response = use_case.execute(valid_task_id)
            mock_generate.assert_called_once_with(["@coding_agent"], clear_all=False)
            assert response.id == "20240101001"

    def test_get_task_use_case_no_assignees(self, temp_agent_setup):
        mock_repo = Mock()
        mock_task = Mock()
        mock_task.assignees = []
        mock_task.id = "mock_task_id_2"
        mock_task.get_events.return_value = [Mock(spec=TaskRetrieved)]
        mock_task.to_dict.return_value = {
            "id": "20240101002", "title": "Test Task 2", "description": "Test 2",
            "status": "todo", "priority": "medium", "details": "",
            "estimatedEffort": "", "assignees": [], "labels": [],
            "dependencies": [], "subtasks": [], "dueDate": None,
            "created_at": "2024-01-01T00:00:00", "updated_at": "2024-01-01T00:00:00"
        }
        mock_auto_rule_generator = Mock()

        use_case = GetTaskUseCase(mock_repo, mock_auto_rule_generator)
        mock_repo.find_by_id.return_value = mock_task
        valid_task_id = TaskId.from_int(2)

        with patch('fastmcp.task_management.application.use_cases.get_task.generate_docs_for_assignees') as mock_generate:
            response = use_case.execute(valid_task_id)
            mock_generate.assert_called_once_with([], clear_all=False)
            assert response.id == "20240101002"