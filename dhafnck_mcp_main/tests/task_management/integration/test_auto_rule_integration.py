"""
This is the canonical and only maintained test suite for auto rule integration tests in task management.
All validation, edge-case, and integration tests should be added here.
Redundant or duplicate tests in other files have been removed.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


import pytest
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import MCP and application classes
from fastmcp.task_management.interface.consolidated_mcp_tools_v2 import ConsolidatedMCPToolsV2
from fastmcp.task_management.application.services.task_application_service import TaskApplicationService
from fastmcp.task_management.infrastructure.repositories.json_task_repository import JsonTaskRepository
from fastmcp.task_management.infrastructure.services.file_auto_rule_generator import FileAutoRuleGenerator


class TestAutoRuleIntegration:
    """Integration test suite for auto rule generation with MCP tools"""

    def setup_method(self):
        """Set up test fixtures"""
        self.test_dir = tempfile.mkdtemp()
        self.test_tasks_file = os.path.join(self.test_dir, "test_tasks.json")
        self.test_auto_rule_file = os.path.join(self.test_dir, "test_auto_rule.mdc")
        
        from datetime import datetime
        current_date = datetime.now().strftime('%Y%m%d')
        task_id_1 = f"{current_date}101"
        task_id_2 = f"{current_date}102"
        
        self.test_tasks_data = {
            "tasks": [
                {
                    "id": task_id_1,
                    "title": "Test Auto Rule Generation Trigger",
                    "description": "Test that auto_rule.mdc is generated when get_task is called",
                    "status": "todo",
                    "priority": "high",
                    "details": "Integration test for auto rule generation system",
                    "estimated_effort": "small",
                    "assignees": ["system_architect"],
                    "labels": ["auto-generation", "testing", "integration"],
                    "dependencies": [],
                    "subtasks": [],
                    "created_at": "2025-01-22T10:00:00Z",
                    "updated_at": "2025-01-22T10:00:00Z",
                    "due_date": "2025-01-23"
                },
                {
                    "id": task_id_2,
                    "title": "Test Senior Developer Rules",
                    "description": "Test auto rule generation for senior developer role",
                    "status": "in_progress",
                    "priority": "medium",
                    "details": "Test role-specific rule generation",
                    "estimated_effort": "medium",
                    "assignees": ["senior_developer"],
                    "labels": ["development", "testing"],
                    "dependencies": [],
                    "subtasks": [],
                    "created_at": "2025-01-22T11:00:00Z",
                    "updated_at": "2025-01-22T11:00:00Z",
                    "due_date": "2025-01-24"
                }
            ]
        }
        
        with open(self.test_tasks_file, 'w') as f:
            json.dump(self.test_tasks_data, f, indent=2)
        
        self.task_id_1 = self.test_tasks_data['tasks'][0]['id']
        self.task_id_2 = self.test_tasks_data['tasks'][1]['id']

    def teardown_method(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
            
    def _get_registered_tool(self, mcp_tools, tool_name):
        """Helper to get a registered tool from the MCP mock"""
        mock_mcp = MagicMock()
        registered_tools = {}

        def mock_tool_decorator(name=None):
            def decorator(func):
                actual_name = name or func.__name__
                registered_tools[actual_name] = func
                return func
            return decorator

        mock_mcp.tool = mock_tool_decorator
        mcp_tools.register_tools(mock_mcp)
        return registered_tools.get(tool_name)

    def test_mcp_get_task_triggers_auto_rule_generation(self):
        """Test that MCP get_task tool triggers auto rule generation"""
        task_repository = JsonTaskRepository(self.test_tasks_file)
        auto_rule_generator = FileAutoRuleGenerator(self.test_auto_rule_file)
        mcp_tools = ConsolidatedMCPToolsV2(
            task_repository=task_repository,
            auto_rule_generator=auto_rule_generator
        )
        manage_task_func = self._get_registered_tool(mcp_tools, 'manage_task')
        assert manage_task_func is not None
        result = manage_task_func(action="get", task_id=self.task_id_1)
        assert result.get("success") is True, f"manage_task failed: {result.get('error')}"
        assert result["task"]["id"] == self.task_id_1
        assert os.path.exists(self.test_auto_rule_file), f"Auto rule file not found at {self.test_auto_rule_file}"

    def test_mcp_get_task_with_different_roles(self):
        """Test auto rule generation with different roles through MCP"""
        task_repository = JsonTaskRepository(self.test_tasks_file)
        auto_rule_generator = FileAutoRuleGenerator(self.test_auto_rule_file)
        mcp_tools = ConsolidatedMCPToolsV2(
            task_repository=task_repository,
            auto_rule_generator=auto_rule_generator
        )
        manage_task_func = self._get_registered_tool(mcp_tools, 'manage_task')
        assert manage_task_func is not None
        result1 = manage_task_func(action="get", task_id=self.task_id_1)
        assert result1["success"] is True
        result2 = manage_task_func(action="get", task_id=self.task_id_2)
        assert result2["success"] is True

    def test_mcp_get_task_nonexistent_task(self):
        """Test MCP get_task with nonexistent task"""
        task_repository = JsonTaskRepository(self.test_tasks_file)
        auto_rule_generator = FileAutoRuleGenerator(self.test_auto_rule_file)
        mcp_tools = ConsolidatedMCPToolsV2(
            task_repository=task_repository, 
            auto_rule_generator=auto_rule_generator
        )
        manage_task_func = self._get_registered_tool(mcp_tools, 'manage_task')
        assert manage_task_func is not None
        result = manage_task_func(action="get", task_id="20250101999")
        assert result["success"] is False
        assert "not found" in result["error"].lower()

    def test_auto_rule_generation_content_structure(self):
        """Test the structure and quality of generated auto rule content"""
        task_repository = JsonTaskRepository(self.test_tasks_file)
        auto_rule_generator = FileAutoRuleGenerator(self.test_auto_rule_file)
        mcp_tools = ConsolidatedMCPToolsV2(
            task_repository=task_repository,
            auto_rule_generator=auto_rule_generator
        )
        manage_task_func = self._get_registered_tool(mcp_tools, 'manage_task')
        result = manage_task_func(action="get", task_id=self.task_id_1, force_full_generation=False)
        assert result.get("success") is True, f"manage_task failed: {result.get('error')}"
        assert os.path.exists(self.test_auto_rule_file)
        with open(self.test_auto_rule_file, 'r') as f:
            content = f.read()
        
        task1_assignee = self.test_tasks_data['tasks'][0]['assignees'][0]
        
        assert "### TASK CONTEXT ###" in content, "Missing '### TASK CONTEXT ###' section in simple rules."
        assert f"ROLE: {task1_assignee.upper()}" in content, f"Missing correct ROLE section for {task1_assignee.upper()} in simple rules."
        assert "### OPERATING RULES ###" in content, "Missing '### OPERATING RULES ###' section in simple rules."

    def test_auto_rule_file_overwrite_behavior(self):
        """Test that auto rule file is overwritten on subsequent calls"""
        task_repository = JsonTaskRepository(self.test_tasks_file)
        auto_rule_generator = FileAutoRuleGenerator(self.test_auto_rule_file)
        mcp_tools = ConsolidatedMCPToolsV2(
            task_repository=task_repository,
            auto_rule_generator=auto_rule_generator
        )
        manage_task_func = self._get_registered_tool(mcp_tools, 'manage_task')
        result1 = manage_task_func(action="get", task_id=self.task_id_1)
        assert result1.get("success") is True, f"manage_task failed: {result1.get('error')}"
        
        with open(self.test_auto_rule_file, 'r') as f:
            content_before = f.read()
            
        update_request = {
            "action": "update",
            "task_id": self.task_id_1,
            "title": "Updated Test Task Title"
        }
        manage_task_func(**update_request)
        
        result2 = manage_task_func(action="get", task_id=self.task_id_1)
        assert result2.get("success") is True, f"manage_task failed: {result2.get('error')}"
        
        with open(self.test_auto_rule_file, 'r') as f:
            content_after = f.read()
            
        assert content_before != content_after, "File content should be different after update"
        assert "Updated Test Task Title" in content_after, "Updated title not found in content"

    def test_auto_rule_generation_error_recovery(self):
        """Test that the system gracefully handles errors during auto rule generation"""
        task_repository = JsonTaskRepository(self.test_tasks_file)
        mock_generator = MagicMock(spec=FileAutoRuleGenerator)
        mock_generator.generate_rules_for_task.side_effect = Exception("Simulated generation error")
        mcp_tools = ConsolidatedMCPToolsV2(
            task_repository=task_repository,
            auto_rule_generator=mock_generator
        )
        manage_task_func = self._get_registered_tool(mcp_tools, 'manage_task')
        result = manage_task_func(action="get", task_id=self.task_id_1)
        assert result.get("success") is False, "Expected manage_task to fail"
        assert "Error during auto rule generation" in result.get("error", ""), "Error message should indicate auto rule generation failure"
        assert "Simulated generation error" in result.get("error", ""), "Original exception should be in the error message"


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 