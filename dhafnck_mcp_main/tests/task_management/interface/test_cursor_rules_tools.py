"""
This is the canonical and only maintained test suite for cursor rules tools in task management.
All validation, edge-case, and integration tests should be added here.
Redundant or duplicate tests in other files have been removed.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


import json
import tempfile
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from fastmcp.dhafnck_mcp.interface.cursor_rules_tools import CursorRulesTools, _get_project_root


class TestGetProjectRoot:
    """Test cases for _get_project_root function"""

    def test_get_project_root_finds_correct_root(self):
        """
        Tests that _get_project_root correctly finds the project root directory
        by running it in a real environment.
        """
        # This is now more of an integration test, but it's more robust
        # than trying to mock the complex Path traversal.
        project_root = _get_project_root()
        assert isinstance(project_root, Path)
        
        # Check for the presence of a known marker at the project root
        assert (project_root / "dhafnck_mcp_main").is_dir() or \
               (project_root / ".git").is_dir() or \
               (project_root / "pyproject.toml").exists()


class TestCursorRulesTools:
    """Test cases for CursorRulesTools"""

    @pytest.fixture
    def temp_project_root(self):
        """Create a temporary project root with .cursor/rules directory"""
        with tempfile.TemporaryDirectory() as temp_dir:
            project_root = Path(temp_dir)
            rules_dir = project_root / ".cursor" / "rules"
            rules_dir.mkdir(parents=True)
            
            # Create a sample auto_rule.mdc file
            auto_rule_path = rules_dir / "auto_rule.mdc"
            auto_rule_path.write_text("""# Test Auto Rule

## Task Context
- Task: Test Task
- Priority: High

## Role
- Senior Developer

## Operating Rules
1. Write clean code
2. Test thoroughly
""")
            
            yield project_root

    @pytest.fixture
    def cursor_rules_tools(self, temp_project_root):
        """Create CursorRulesTools instance with mocked project root"""
        with patch('fastmcp.dhafnck_mcp.interface.cursor_rules_tools._get_project_root', return_value=temp_project_root):
            with patch('fastmcp.dhafnck_mcp.infrastructure.services.FileAutoRuleGenerator'):
                return CursorRulesTools()

    @pytest.fixture
    def mock_mcp(self):
        """Create a mock MCP server"""
        registered_tools = {}
        call_count = 0
        
        def mock_tool():
            def decorator(func):
                nonlocal call_count
                call_count += 1
                registered_tools[func.__name__] = func
                return func
            return decorator
        
        mcp = MagicMock()
        mcp.tool = mock_tool
        mcp.registered_tools = registered_tools  # Store for easy access in tests
        mcp.tool.call_count = property(lambda self: call_count)
        return mcp

    def test_init(self, temp_project_root):
        """Test CursorRulesTools initialization"""
        with patch('fastmcp.dhafnck_mcp.interface.cursor_rules_tools._get_project_root', return_value=temp_project_root):
            with patch('fastmcp.dhafnck_mcp.infrastructure.services.FileAutoRuleGenerator') as mock_generator:
                tools = CursorRulesTools()
                
                assert tools._project_root == temp_project_root
                mock_generator.assert_called_once()

    def test_update_auto_rule_success(self, cursor_rules_tools, temp_project_root, mock_mcp):
        """Test successful auto rule update"""
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the registered function
        update_auto_rule = mock_mcp.registered_tools.get('update_auto_rule')
        assert update_auto_rule is not None
        
        new_content = "# New Auto Rule\nThis is new content"
        result = update_auto_rule(content=new_content, backup=True)
        
        assert result["success"] is True
        assert "Auto rule file updated successfully" in result["message"]
        assert result["backup_created"] is True
        
        # Verify file was updated
        auto_rule_path = temp_project_root / ".cursor" / "rules" / "auto_rule.mdc"
        assert auto_rule_path.read_text() == new_content
        
        # Verify backup was created
        backup_path = temp_project_root / ".cursor" / "rules" / "auto_rule.mdc.backup"
        assert backup_path.exists()

    def test_update_auto_rule_no_backup(self, cursor_rules_tools, temp_project_root, mock_mcp):
        """Test auto rule update without backup"""
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the registered function
        update_auto_rule = mock_mcp.registered_tools.get('update_auto_rule')
        assert update_auto_rule is not None
        
        new_content = "# New Auto Rule\nNo backup"
        result = update_auto_rule(content=new_content, backup=False)
        
        assert result["success"] is True
        assert result["backup_created"] is False

    def test_update_auto_rule_error(self, cursor_rules_tools, mock_mcp):
        """Test auto rule update with error"""
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the registered function
        update_auto_rule = mock_mcp.registered_tools.get('update_auto_rule')
        assert update_auto_rule is not None
        
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            result = update_auto_rule(content="test", backup=False)
            
            assert result["success"] is False
            assert "Failed to update auto rule" in result["error"]

    def test_validate_rules_success(self, cursor_rules_tools, temp_project_root, mock_mcp):
        """Test successful rule validation"""
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the registered function
        validate_rules = mock_mcp.registered_tools.get('validate_rules')
        assert validate_rules is not None
        
        result = validate_rules()
        
        assert result["success"] is True
        assert "validation_results" in result
        assert result["validation_results"]["file_exists"] is True
        assert result["validation_results"]["has_task_context"] is True
        assert result["validation_results"]["has_role_info"] is True

    def test_validate_rules_file_not_found(self, cursor_rules_tools, mock_mcp):
        """Test rule validation with non-existent file"""
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the registered function
        validate_rules = mock_mcp.registered_tools.get('validate_rules')
        assert validate_rules is not None
        
        result = validate_rules(file_path="nonexistent.mdc")
        
        assert result["success"] is False
        assert "File not found" in result["error"]

    def test_validate_rules_custom_path(self, cursor_rules_tools, temp_project_root, mock_mcp):
        """Test rule validation with custom file path"""
        # Create a custom rule file
        custom_rule_path = temp_project_root / "custom_rule.mdc"
        custom_rule_path.write_text("# Custom Rule\n## Task Context\n## Role\n## Operating Rules")
        
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the registered function
        validate_rules = mock_mcp.registered_tools.get('validate_rules')
        assert validate_rules is not None
        
        result = validate_rules(file_path="custom_rule.mdc")
        
        assert result["success"] is True

    def test_validate_rules_issues_detected(self, cursor_rules_tools, temp_project_root, mock_mcp):
        """Test rule validation with issues detected"""
        # Create a problematic rule file
        problem_rule_path = temp_project_root / ".cursor" / "rules" / "auto_rule.mdc"
        problem_rule_path.write_text("Small content")  # Too small, no markdown header
        
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the registered function
        validate_rules = mock_mcp.registered_tools.get('validate_rules')
        assert validate_rules is not None
        
        result = validate_rules()
        
        assert result["success"] is True
        assert len(result["issues"]) > 0
        assert any("too small" in issue for issue in result["issues"])

    def test_manage_cursor_rules_list(self, cursor_rules_tools, temp_project_root, mock_mcp):
        """Test listing cursor rules"""
        # Create additional rule files
        (temp_project_root / ".cursor" / "rules" / "test_rule.mdc").write_text("# Test Rule")
        
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the registered function
        manage_cursor_rules = mock_mcp.registered_tools.get('manage_cursor_rules')
        assert manage_cursor_rules is not None
        
        result = manage_cursor_rules(action="list")
        
        assert result["success"] is True
        assert "files" in result
        assert result["count"] >= 2  # auto_rule.mdc + test_rule.mdc

    def test_manage_cursor_rules_list_no_directory(self, cursor_rules_tools, temp_project_root, mock_mcp):
        """Test listing cursor rules when directory doesn't exist"""
        # Remove the rules directory
        import shutil
        shutil.rmtree(temp_project_root / ".cursor" / "rules")
        
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the registered function
        manage_cursor_rules = mock_mcp.registered_tools.get('manage_cursor_rules')
        assert manage_cursor_rules is not None
        
        result = manage_cursor_rules(action="list")
        
        assert result["success"] is True
        assert result["files"] == []
        assert "does not exist" in result["message"]

    def test_manage_cursor_rules_backup(self, cursor_rules_tools, temp_project_root, mock_mcp):
        """Test backing up cursor rules"""
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the registered function
        manage_cursor_rules = mock_mcp.registered_tools.get('manage_cursor_rules')
        assert manage_cursor_rules is not None
        
        result = manage_cursor_rules(action="backup")
        
        assert result["success"] is True
        assert "Backup created successfully" in result["message"]
        
        # Verify backup file exists
        backup_path = temp_project_root / ".cursor" / "rules" / "auto_rule.mdc.backup"
        assert backup_path.exists()

    def test_manage_cursor_rules_backup_no_file(self, cursor_rules_tools, temp_project_root, mock_mcp):
        """Test backing up when auto_rule.mdc doesn't exist"""
        # Remove auto_rule.mdc
        (temp_project_root / ".cursor" / "rules" / "auto_rule.mdc").unlink()
        
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the registered function
        manage_cursor_rules = mock_mcp.registered_tools.get('manage_cursor_rules')
        assert manage_cursor_rules is not None
        
        result = manage_cursor_rules(action="backup")
        
        assert result["success"] is False
        assert "auto_rule.mdc not found" in result["error"]

    def test_manage_cursor_rules_restore(self, cursor_rules_tools, temp_project_root, mock_mcp):
        """Test restoring cursor rules from backup"""
        # Create backup file
        backup_path = temp_project_root / ".cursor" / "rules" / "auto_rule.mdc.backup"
        backup_content = "# Backup Content\nThis is backup"
        backup_path.write_text(backup_content)
        
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the registered function
        manage_cursor_rules = mock_mcp.registered_tools.get('manage_cursor_rules')
        assert manage_cursor_rules is not None
        
        result = manage_cursor_rules(action="restore")
        
        assert result["success"] is True
        assert "Restored from backup successfully" in result["message"]
        
        # Verify content was restored
        auto_rule_path = temp_project_root / ".cursor" / "rules" / "auto_rule.mdc"
        assert auto_rule_path.read_text() == backup_content

    def test_manage_cursor_rules_restore_no_backup(self, cursor_rules_tools, temp_project_root, mock_mcp):
        """Test restoring when backup doesn't exist"""
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the registered function
        manage_cursor_rules = mock_mcp.registered_tools.get('manage_cursor_rules')
        assert manage_cursor_rules is not None
        
        result = manage_cursor_rules(action="restore")
        
        assert result["success"] is False
        assert "Backup file not found" in result["error"]

    def test_manage_cursor_rules_clean(self, cursor_rules_tools, temp_project_root, mock_mcp):
        """Test cleaning backup files"""
        # Create backup files
        (temp_project_root / ".cursor" / "rules" / "auto_rule.mdc.backup").write_text("backup1")
        (temp_project_root / ".cursor" / "rules" / "other.backup").write_text("backup2")
        
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the registered function
        manage_cursor_rules = mock_mcp.registered_tools.get('manage_cursor_rules')
        assert manage_cursor_rules is not None
        
        result = manage_cursor_rules(action="clean")
        
        assert result["success"] is True
        assert "Cleaned 2 backup files" in result["message"]
        
        # Verify backup files were removed
        assert not (temp_project_root / ".cursor" / "rules" / "auto_rule.mdc.backup").exists()
        assert not (temp_project_root / ".cursor" / "rules" / "other.backup").exists()

    def test_manage_cursor_rules_info(self, cursor_rules_tools, temp_project_root, mock_mcp):
        """Test getting cursor rules info"""
        # Create additional files
        (temp_project_root / ".cursor" / "rules" / "test.mdc").write_text("test")
        (temp_project_root / ".cursor" / "rules" / "backup.backup").write_text("backup")
        (temp_project_root / ".cursor" / "rules" / "subdir").mkdir()
        
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the registered function
        manage_cursor_rules = mock_mcp.registered_tools.get('manage_cursor_rules')
        assert manage_cursor_rules is not None
        
        result = manage_cursor_rules(action="info")
        
        assert result["success"] is True
        assert "info" in result

    def test_manage_cursor_rules_info_no_directory(self, cursor_rules_tools, temp_project_root, mock_mcp):
        """Test getting info when rules directory doesn't exist"""
        # Remove the rules directory
        import shutil
        shutil.rmtree(temp_project_root / ".cursor" / "rules")
        
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the registered function
        manage_cursor_rules = mock_mcp.registered_tools.get('manage_cursor_rules')
        assert manage_cursor_rules is not None
        
        result = manage_cursor_rules(action="info")
        
        assert result["success"] is True
        assert result["info"]["directory_exists"] is False

    def test_manage_cursor_rules_unknown_action(self, cursor_rules_tools, mock_mcp):
        """Test unknown action handling"""
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the registered function
        manage_cursor_rules = mock_mcp.registered_tools.get('manage_cursor_rules')
        assert manage_cursor_rules is not None
        
        result = manage_cursor_rules(action="unknown")
        
        assert result["success"] is False
        assert "Unknown action" in result["error"]

    def test_regenerate_auto_rule_success(self, cursor_rules_tools, mock_mcp):
        """Test successful auto rule regeneration"""
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the registered function
        regenerate_auto_rule = mock_mcp.registered_tools.get('regenerate_auto_rule')
        assert regenerate_auto_rule is not None
        
        with patch.object(cursor_rules_tools._auto_rule_generator, 'generate_rules_for_task') as mock_generate:
            mock_generate.return_value = True
            
            result = regenerate_auto_rule(role="senior_developer")
            
            assert result["success"] is True
            mock_generate.assert_called_once()

    def test_regenerate_auto_rule_with_task_context(self, cursor_rules_tools, mock_mcp):
        """Test auto rule regeneration with task context"""
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the registered function
        regenerate_auto_rule = mock_mcp.registered_tools.get('regenerate_auto_rule')
        assert regenerate_auto_rule is not None
        
        task_context = {
            "id": "test123",
            "title": "Test Task",
            "description": "Test description",
            "assignee": "qa_engineer",
            "priority": "medium",
            "details": "Test details"
        }
        
        with patch.object(cursor_rules_tools._auto_rule_generator, 'generate_rules_for_task') as mock_generate:
            mock_generate.return_value = True
            
            result = regenerate_auto_rule(role="qa_engineer", task_context=task_context)
            
            assert result["success"] is True
            mock_generate.assert_called_once()

    def test_regenerate_auto_rule_error(self, cursor_rules_tools, mock_mcp):
        """Test auto rule regeneration with error"""
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the registered function
        regenerate_auto_rule = mock_mcp.registered_tools.get('regenerate_auto_rule')
        assert regenerate_auto_rule is not None
        
        with patch.object(cursor_rules_tools._auto_rule_generator, 'generate_rules_for_task') as mock_generate:
            mock_generate.side_effect = Exception("Generation failed")
            
            result = regenerate_auto_rule()
            
            assert result["success"] is False
            assert "Regeneration failed" in result["error"]

    def test_validate_tasks_json_success(self, cursor_rules_tools, temp_project_root, mock_mcp):
        """Test successful tasks.json validation"""
        # Create a valid tasks.json file
        tasks_json_path = temp_project_root / ".cursor" / "rules" / "tasks" / "tasks.json"
        tasks_json_path.parent.mkdir(parents=True, exist_ok=True)
        
        valid_tasks = {
            "tasks": [
                {
                    "id": "20250101001",
                    "title": "Test Task",
                    "description": "Test description",
                    "status": "todo",
                    "priority": "medium",
                    "assignees": ["@test_agent"],
                    "labels": ["test"],
                    "subtasks": [],
                    "dependencies": [],
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z"
                }
            ]
        }
        
        tasks_json_path.write_text(json.dumps(valid_tasks, indent=2))
        
        # Create mock validator
        validator_path = temp_project_root / ".cursor" / "rules" / "tools" / "tasks_validator.py"
        validator_path.parent.mkdir(parents=True, exist_ok=True)
        validator_path.write_text("""
class TasksValidator:
    def __init__(self, file_path=None):
        self.file_path = file_path
        
    def validate(self):
        return {
            "file_path": self.file_path or "tasks.json",
            "file_exists": True,
            "validation_passed": True,
            "total_issues": 0,
            "summary": {"errors": 0, "warnings": 0, "missing_properties": 0},
            "errors": [],
            "warnings": [],
            "missing_properties": [],
            "recommendations": []
        }
""")
        
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the registered function
        validate_tasks_json = mock_mcp.registered_tools.get('validate_tasks_json')
        assert validate_tasks_json is not None
        
        result = validate_tasks_json()
        
        assert result["success"] is True

    def test_validate_tasks_json_file_not_found(self, cursor_rules_tools, mock_mcp):
        """Test tasks.json validation when file doesn't exist"""
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the registered function
        validate_tasks_json = mock_mcp.registered_tools.get('validate_tasks_json')
        assert validate_tasks_json is not None
        
        result = validate_tasks_json()
        
        assert result["success"] is False
        assert "not found" in result["error"]

    def test_validate_tasks_json_invalid_json(self, cursor_rules_tools, temp_project_root, mock_mcp):
        """Test tasks.json validation with invalid JSON"""
        # Create an invalid tasks.json file
        tasks_json_path = temp_project_root / ".cursor" / "rules" / "tasks" / "tasks.json"
        tasks_json_path.parent.mkdir(parents=True, exist_ok=True)
        tasks_json_path.write_text("invalid json content")
        
        # Create mock validator that will fail
        validator_path = temp_project_root / ".cursor" / "rules" / "tools" / "tasks_validator.py"
        validator_path.parent.mkdir(parents=True, exist_ok=True)
        validator_path.write_text("""
class TasksValidator:
    def __init__(self, file_path=None):
        self.file_path = file_path
        
    def validate(self):
        raise Exception("Invalid JSON format")
""")
        
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the registered function
        validate_tasks_json = mock_mcp.registered_tools.get('validate_tasks_json')
        assert validate_tasks_json is not None
        
        result = validate_tasks_json()
        
        assert result["success"] is False
        assert "Validation failed" in result["error"]

    def test_validate_tasks_json_custom_path(self, cursor_rules_tools, temp_project_root, mock_mcp):
        """Test tasks.json validation with custom file path"""
        # Create a custom tasks.json file
        custom_tasks_path = temp_project_root / "custom_tasks.json"
        custom_tasks_path.write_text('{"tasks": []}')
        
        # Create mock validator
        validator_path = temp_project_root / ".cursor" / "rules" / "tools" / "tasks_validator.py"
        validator_path.parent.mkdir(parents=True, exist_ok=True)
        validator_path.write_text("""
class TasksValidator:
    def __init__(self, file_path=None):
        self.file_path = file_path
        
    def validate(self):
        return {
            "file_path": self.file_path or "tasks.json",
            "file_exists": True,
            "validation_passed": True,
            "total_issues": 0,
            "summary": {"errors": 0, "warnings": 0, "missing_properties": 0},
            "errors": [],
            "warnings": [],
            "missing_properties": [],
            "recommendations": []
        }
""")
        
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the registered function
        validate_tasks_json = mock_mcp.registered_tools.get('validate_tasks_json')
        assert validate_tasks_json is not None
        
        result = validate_tasks_json(file_path="custom_tasks.json")
        
        assert result["success"] is True

    def test_validate_tasks_json_detailed_output(self, cursor_rules_tools, temp_project_root, mock_mcp):
        """Test tasks.json validation with detailed output format"""
        # Create a valid tasks.json file
        tasks_json_path = temp_project_root / ".cursor" / "rules" / "tasks" / "tasks.json"
        tasks_json_path.parent.mkdir(parents=True, exist_ok=True)
        tasks_json_path.write_text('{"tasks": []}')
        
        # Create mock validator
        validator_path = temp_project_root / ".cursor" / "rules" / "tools" / "tasks_validator.py"
        validator_path.parent.mkdir(parents=True, exist_ok=True)
        validator_path.write_text("""
class TasksValidator:
    def __init__(self, file_path=None):
        self.file_path = file_path
        
    def validate(self):
        return {
            "file_path": self.file_path or "tasks.json",
            "file_exists": True,
            "validation_passed": True,
            "total_issues": 0,
            "summary": {"errors": 0, "warnings": 0, "missing_properties": 0},
            "errors": [],
            "warnings": [],
            "missing_properties": [],
            "recommendations": []
        }
""")
        
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the registered function
        validate_tasks_json = mock_mcp.registered_tools.get('validate_tasks_json')
        assert validate_tasks_json is not None
        
        result = validate_tasks_json(output_format="detailed")
        
        assert result["success"] is True
        assert "file_path" in result

    def test_error_handling_in_tools(self, cursor_rules_tools, mock_mcp):
        """Test error handling in tools"""
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Get the manage_cursor_rules function
        manage_cursor_rules = mock_mcp.registered_tools.get('manage_cursor_rules')
        assert manage_cursor_rules is not None
        
        with patch('pathlib.Path.rglob', side_effect=Exception("Filesystem error")):
            result = manage_cursor_rules(action="list")
            
            assert result["success"] is False
            assert "Management operation failed" in result["error"]

    def test_register_tools_called(self, cursor_rules_tools):
        """Test that register_tools can be called"""
        # Create a mock that properly tracks call counts
        registered_tools = {}
        call_count = 0
        
        def mock_tool():
            def decorator(func):
                nonlocal call_count
                call_count += 1
                registered_tools[func.__name__] = func
                return func
            return decorator
        
        mock_mcp = MagicMock()
        mock_mcp.tool = mock_tool
        mock_mcp.registered_tools = registered_tools
        
        cursor_rules_tools.register_tools(mock_mcp)
        
        # Verify that tool registration was called
        assert call_count >= 5  # Should have 5 tools 