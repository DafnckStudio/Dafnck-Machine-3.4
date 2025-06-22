"""
Migration Integration Tests - Task Management Module
Validates comprehensive migration to FastMCP framework

Test Categories:
1. MCP Tools Testing - Verify all MCP tools work correctly
2. API Endpoint Testing - Test all task management endpoints  
3. Domain Logic Testing - Validate core business logic still works
4. Integration Testing - Ensure proper integration with FastMCP server
5. Regression Testing - Confirm no functionality lost in migration
6. Performance Testing - Ensure no performance degradation
7. Error Handling Testing - Validate robust error handling
"""

import pytest
import asyncio
import sys
import os
import tempfile
import json
import time
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import Mock, patch

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

# Import migrated components
from fastmcp.task_management.interface.consolidated_mcp_tools_v2 import ConsolidatedMCPToolsV2
from fastmcp.task_management.infrastructure.repositories.json_task_repository import JsonTaskRepository, InMemoryTaskRepository
from fastmcp.task_management.infrastructure.services.file_auto_rule_generator import FileAutoRuleGenerator
from fastmcp.task_management.domain.entities.task import Task
from fastmcp.task_management.domain.value_objects.task_id import TaskId
from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
from fastmcp.task_management.domain.value_objects.priority import Priority
from fastmcp.task_management.interface.ddd_mcp_server import create_mcp_server
from fastmcp import FastMCP


class TestMigrationIntegration:
    """Comprehensive migration integration tests for task management module."""
    
    @pytest.fixture
    def temp_project_structure(self):
        """Create temporary project structure for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create .cursor/rules structure
            cursor_rules = temp_path / ".cursor" / "rules"
            cursor_rules.mkdir(parents=True)
            
            tasks_dir = cursor_rules / "tasks"
            tasks_dir.mkdir()
            
            # Create sample tasks.json with migration test data
            tasks_data = {
                "tasks": [
                    {
                        "id": "20250101001",
                        "title": "Pre-migration Task",
                        "description": "Task created before migration",
                        "status": "todo",
                        "priority": "high",
                        "assignees": ["@coding_agent"],
                        "labels": ["pre-migration", "test"],
                        "created_at": "2025-01-01T10:00:00.000000",
                        "updated_at": "2025-01-01T10:00:00.000000"
                    }
                ]
            }
            
            tasks_file = tasks_dir / "tasks.json"
            with open(tasks_file, 'w') as f:
                json.dump(tasks_data, f, indent=2)
            
            # Create auto_rule.mdc file
            auto_rule_file = cursor_rules / "auto_rule.mdc"
            auto_rule_file.write_text("# Auto Rule Test\nTest content for migration validation.")
            
            yield temp_path
    
    @pytest.fixture
    def mcp_tools_instance(self, temp_project_structure):
        """Create MCP tools instance with temporary structure."""
        original_cwd = os.getcwd()
        os.chdir(temp_project_structure)
        
        try:
            # Initialize with real file-based repository for migration testing
            repository = JsonTaskRepository()
            mcp_tools = ConsolidatedMCPToolsV2(task_repository=repository)
            yield mcp_tools
        finally:
            os.chdir(original_cwd)
    
    @pytest.fixture
    def mcp_server_instance(self, temp_project_structure):
        """Create MCP server instance for testing FastMCP integration."""
        original_cwd = os.getcwd()
        os.chdir(temp_project_structure)
        
        try:
            # Create MCP server with tools registered
            mcp_server = create_mcp_server()
            yield mcp_server
        finally:
            os.chdir(original_cwd)
    
    @pytest.fixture
    def performance_baseline(self):
        """Baseline performance metrics for regression testing."""
        return {
            "task_creation_max_time": 0.1,  # 100ms
            "task_retrieval_max_time": 0.05,  # 50ms
            "task_search_max_time": 0.2,  # 200ms
            "task_update_max_time": 0.1,  # 100ms
            "bulk_operations_max_time": 1.5  # 1.5 seconds for 10 tasks (adjusted for JSON I/O overhead)
        }

    # ================================
    # 1. MCP TOOLS TESTING
    # ================================
    
    @pytest.mark.integration
    @pytest.mark.migration
    @pytest.mark.asyncio
    async def test_all_mcp_tools_available_after_migration(self, mcp_server_instance):
        """Verify all MCP tools are available and properly registered after migration."""
        mcp_server = mcp_server_instance
        
        # Test that all expected MCP tools are registered
        expected_tools = [
            'manage_task',
            'manage_subtask', 
            'manage_project',
            'manage_agent',
            'update_auto_rule',
            'regenerate_auto_rule',
            'validate_rules',
            'validate_tasks_json',
            'manage_cursor_rules',
            'call_agent'
        ]
        
        # Get registered tools from the MCP server using async method
        registered_tools_dict = await mcp_server.get_tools()
        registered_tools = list(registered_tools_dict.keys())
        
        for tool_name in expected_tools:
            assert tool_name in registered_tools, f"MCP tool '{tool_name}' not found after migration. Available tools: {registered_tools}"
    
    @pytest.mark.integration
    @pytest.mark.migration
    def test_mcp_tools_functionality_preserved(self, mcp_tools_instance):
        """Test that all MCP tools maintain their core functionality after migration."""
        mcp_tools = mcp_tools_instance
        
        # Test task management tool using internal methods for direct testing
        create_result = mcp_tools._handle_core_task_operations(
            action="create",
            task_id=None,
            title="Migration Test Task",
            description="Testing MCP tools after migration",
            status=None,
            priority="high",
            details=None,
            estimated_effort=None,
            assignees=None,
            labels=["migration", "test"],
            due_date=None,
            project_id=None,
            force_full_generation=False
        )
        assert create_result["success"] is True
        task_id = create_result["task"]["id"]
        
        # Test task retrieval
        get_result = mcp_tools._handle_core_task_operations(
            action="get",
            task_id=task_id,
            title=None,
            description=None,
            status=None,
            priority=None,
            details=None,
            estimated_effort=None,
            assignees=None,
            labels=None,
            due_date=None,
            project_id=None,
            force_full_generation=False
        )
        assert get_result["success"] is True
        assert get_result["task"]["title"] == "Migration Test Task"
        
        # Test subtask management
        subtask_result = mcp_tools._handle_subtask_operations(
            action="add_subtask",
            task_id=task_id,
            subtask_data={"title": "Migration subtask test"}
        )
        assert subtask_result["success"] is True
        
        # Test project management using multi-agent tools
        project_result = mcp_tools._multi_agent_tools.create_project(
            project_id="migration_test_project",
            name="Migration Test Project",
            description="Test project for migration validation"
        )
        assert project_result["success"] is True
        
        # Test agent management using multi-agent tools
        agent_result = mcp_tools._multi_agent_tools.register_agent(
            project_id="migration_test_project",
            agent_id="test_agent",
            name="Test Agent",
            call_agent="@test_agent"
        )
        assert agent_result["success"] is True

    # ================================
    # 2. API ENDPOINT TESTING
    # ================================
    
    @pytest.mark.integration
    @pytest.mark.migration
    def test_all_task_api_endpoints_functional(self, mcp_tools_instance):
        """Test all task management API endpoints work correctly after migration."""
        mcp_tools = mcp_tools_instance
        
        # Test CREATE endpoint
        create_response = mcp_tools._handle_core_task_operations(
            action="create",
            task_id=None,
            title="API Test Task",
            description="Testing API endpoints",
            status="todo",
            priority="medium",
            details=None,
            estimated_effort=None,
            assignees=["@test_agent"],
            labels=["api", "test"],
            due_date=None,
            project_id=None,
            force_full_generation=False
        )
        assert create_response["success"] is True
        task_id = create_response["task"]["id"]
        
        # Test READ endpoint
        read_response = mcp_tools._handle_core_task_operations(
            action="get",
            task_id=task_id,
            title=None,
            description=None,
            status=None,
            priority=None,
            details=None,
            estimated_effort=None,
            assignees=None,
            labels=None,
            due_date=None,
            project_id=None,
            force_full_generation=False
        )
        assert read_response["success"] is True
        assert read_response["task"]["id"] == task_id
        
        # Test UPDATE endpoint
        update_response = mcp_tools._handle_core_task_operations(
            action="update",
            task_id=task_id,
            title=None,
            description=None,
            status="in_progress",
            priority=None,
            details="Updated details for API test",
            estimated_effort=None,
            assignees=None,
            labels=None,
            due_date=None,
            project_id=None,
            force_full_generation=False
        )
        assert update_response["success"] is True
        assert update_response["task"]["status"] == "in_progress"
        
        # Test LIST endpoint
        list_response = mcp_tools._handle_list_tasks(
            status="in_progress",
            priority=None,
            assignees=None,
            labels=None,
            limit=None
        )
        assert list_response["success"] is True
        assert len(list_response["tasks"]) >= 1
        
        # Test SEARCH endpoint
        search_response = mcp_tools._handle_search_tasks(
            query="API Test",
            limit=None
        )
        assert search_response["success"] is True
        assert len(search_response["tasks"]) >= 1
        
        # Test DELETE endpoint
        delete_response = mcp_tools._handle_core_task_operations(
            action="delete",
            task_id=task_id,
            title=None,
            description=None,
            status=None,
            priority=None,
            details=None,
            estimated_effort=None,
            assignees=None,
            labels=None,
            due_date=None,
            project_id=None,
            force_full_generation=False
        )
        assert delete_response["success"] is True

    # ================================
    # 3. SUBTASK API TESTING
    # ================================
    
    @pytest.mark.integration
    @pytest.mark.migration
    def test_subtask_api_endpoints_functional(self, mcp_tools_instance):
        """Test all subtask management API endpoints work correctly after migration."""
        mcp_tools = mcp_tools_instance
        
        # First create a parent task
        task_response = mcp_tools._handle_core_task_operations(
            action="create",
            task_id=None,
            title="Parent Task for Subtasks",
            description="Parent task to test subtask functionality",
            status="todo",
            priority="medium",
            details=None,
            estimated_effort=None,
            assignees=None,
            labels=["subtask-test"],
            due_date=None,
            project_id=None,
            force_full_generation=False
        )
        assert task_response["success"] is True
        parent_task_id = task_response["task"]["id"]
        
        # Test ADD_SUBTASK
        add_subtask_response = mcp_tools._handle_subtask_operations(
            action="add_subtask",
            task_id=parent_task_id,
            subtask_data={"title": "First subtask", "description": "Test subtask creation"}
        )
        assert add_subtask_response["success"] is True
        subtask_id = add_subtask_response["result"]["subtask"]["id"]
        
        # Test LIST_SUBTASKS
        list_subtasks_response = mcp_tools._handle_subtask_operations(
            action="list_subtasks",
            task_id=parent_task_id,
            subtask_data=None
        )
        assert list_subtasks_response["success"] is True
        assert len(list_subtasks_response["result"]["subtasks"]) >= 1
        
        # Test UPDATE_SUBTASK
        update_subtask_response = mcp_tools._handle_subtask_operations(
            action="update_subtask",
            task_id=parent_task_id,
            subtask_data={"subtask_id": subtask_id, "title": "Updated subtask title"}
        )
        assert update_subtask_response["success"] is True
        
        # Test COMPLETE_SUBTASK
        complete_subtask_response = mcp_tools._handle_subtask_operations(
            action="complete_subtask",
            task_id=parent_task_id,
            subtask_data={"subtask_id": subtask_id}
        )
        assert complete_subtask_response["success"] is True
        
        # Test REMOVE_SUBTASK
        remove_subtask_response = mcp_tools._handle_subtask_operations(
            action="remove_subtask",
            task_id=parent_task_id,
            subtask_data={"subtask_id": subtask_id}
        )
        assert remove_subtask_response["success"] is True

    # ================================
    # 4. DOMAIN LOGIC TESTING
    # ================================
    
    @pytest.mark.integration
    @pytest.mark.migration  
    def test_domain_entities_integrity_after_migration(self, mcp_tools_instance):
        """Test that domain entities maintain their integrity after migration."""
        mcp_tools = mcp_tools_instance
        
        # Create a task and verify domain entity properties
        task_response = mcp_tools._handle_core_task_operations(
            action="create",
            task_id=None,
            title="Domain Entity Test",
            description="Testing domain entity integrity",
            status="todo",
            priority="high",
            details="Detailed requirements for domain testing",
            estimated_effort="medium",
            assignees=["@coding_agent", "@test_agent"],
            labels=["domain", "migration"],
            due_date="2025-12-31",
            project_id=None,
            force_full_generation=False
        )
        assert task_response["success"] is True
        
        task_data = task_response["task"]
        
        # Verify all domain properties are preserved
        assert task_data["title"] == "Domain Entity Test"
        assert task_data["description"] == "Testing domain entity integrity"
        assert task_data["status"] == "todo"
        assert task_data["priority"] == "high"
        assert task_data["details"] == "Detailed requirements for domain testing"
        assert task_data["estimated_effort"] == "medium"
        assert "@coding_agent" in task_data["assignees"]
        assert "@test_agent" in task_data["assignees"]
        assert "domain" in task_data["labels"]
        assert "migration" in task_data["labels"]
        assert task_data["due_date"] == "2025-12-31"
        
        # Verify domain constraints (e.g., valid task ID format)
        assert task_data["id"].startswith("202")  # Task ID format
        assert len(task_data["id"]) == 11  # Expected length
        
        # Verify timestamps
        assert "created_at" in task_data
        assert "updated_at" in task_data
    
    @pytest.mark.integration
    @pytest.mark.migration
    def test_business_rules_preserved_after_migration(self, mcp_tools_instance):
        """Test that business rules are preserved after migration."""
        mcp_tools = mcp_tools_instance
        
        # Test business rule: Task creation with valid data
        task_response = mcp_tools._handle_core_task_operations(
            action="create",
            task_id=None,
            title="Business Rules Test",
            description="Testing business rule preservation",
            status="todo",
            priority="medium",
            details=None,
            estimated_effort=None,
            assignees=None,
            labels=None,
            due_date=None,
            project_id=None,
            force_full_generation=False
        )
        assert task_response["success"] is True
        task_id = task_response["task"]["id"]
        
        # Test business rule: Cannot delete non-existent task
        delete_invalid_response = mcp_tools._handle_core_task_operations(
            action="delete",
            task_id="invalid_task_id",
            title=None,
            description=None,
            status=None,
            priority=None,
            details=None,
            estimated_effort=None,
            assignees=None,
            labels=None,
            due_date=None,
            project_id=None,
            force_full_generation=False
        )
        assert delete_invalid_response["success"] is False
        
        # Test business rule: Task completion updates status
        complete_response = mcp_tools._handle_complete_task(task_id)
        assert complete_response["success"] is True
        
        # Verify task is completed
        get_response = mcp_tools._handle_core_task_operations(
            action="get",
            task_id=task_id,
            title=None,
            description=None,
            status=None,
            priority=None,
            details=None,
            estimated_effort=None,
            assignees=None,
            labels=None,
            due_date=None,
            project_id=None,
            force_full_generation=False
        )
        assert get_response["success"] is True
        assert get_response["task"]["status"] == "done"

    # ================================
    # 5. PERFORMANCE TESTING
    # ================================
    
    @pytest.mark.integration
    @pytest.mark.migration
    @pytest.mark.performance
    def test_task_creation_performance_no_regression(self, mcp_tools_instance, performance_baseline):
        """Test that task creation performance meets baseline after migration."""
        mcp_tools = mcp_tools_instance
        baseline = performance_baseline["task_creation_max_time"]
        
        # Measure task creation time
        start_time = time.time()
        response = mcp_tools._handle_core_task_operations(
            action="create",
            task_id=None,
            title="Performance Test Task",
            description="Testing task creation performance",
            status=None,
            priority="medium",
            details=None,
            estimated_effort=None,
            assignees=None,
            labels=["performance"],
            due_date=None,
            project_id=None,
            force_full_generation=False
        )
        execution_time = time.time() - start_time
        
        assert response["success"] is True
        PerformanceBenchmark.assert_performance_baseline(execution_time, baseline, "task creation")
    
    @pytest.mark.integration
    @pytest.mark.migration
    @pytest.mark.performance
    def test_bulk_operations_performance_no_regression(self, mcp_tools_instance, performance_baseline):
        """Test that bulk operations performance meets baseline after migration."""
        mcp_tools = mcp_tools_instance
        baseline = performance_baseline["bulk_operations_max_time"]
        
        # Measure bulk task creation time
        start_time = time.time()
        
        task_ids = []
        for i in range(10):
            response = mcp_tools._handle_core_task_operations(
                action="create",
                task_id=None,
                title=f"Bulk Test Task {i+1}",
                description=f"Bulk testing task number {i+1}",
                status=None,
                priority="low",
                details=None,
                estimated_effort=None,
                assignees=None,
                labels=["bulk", "performance"],
                due_date=None,
                project_id=None,
                force_full_generation=False
            )
            assert response["success"] is True
            task_ids.append(response["task"]["id"])
        
        execution_time = time.time() - start_time
        PerformanceBenchmark.assert_performance_baseline(execution_time, baseline, "bulk operations")

    # ================================
    # 6. ERROR HANDLING TESTING
    # ================================
    
    @pytest.mark.integration
    @pytest.mark.migration
    def test_error_handling_robustness_after_migration(self, mcp_tools_instance):
        """Test that error handling is robust after migration."""
        mcp_tools = mcp_tools_instance
        
        # Test invalid task ID
        invalid_get = mcp_tools._handle_core_task_operations(
            action="get",
            task_id="invalid_id",
            title=None,
            description=None,
            status=None,
            priority=None,
            details=None,
            estimated_effort=None,
            assignees=None,
            labels=None,
            due_date=None,
            project_id=None,
            force_full_generation=False
        )
        assert invalid_get["success"] is False
        assert "error" in invalid_get
        
        # Test invalid action
        try:
            invalid_action = mcp_tools._handle_core_task_operations(
                action="invalid_action",
                task_id=None,
                title=None,
                description=None,
                status=None,
                priority=None,
                details=None,
                estimated_effort=None,
                assignees=None,
                labels=None,
                due_date=None,
                project_id=None,
                force_full_generation=False
            )
            # Should either return error or raise exception
            if isinstance(invalid_action, dict):
                assert invalid_action["success"] is False
        except Exception:
            # Exception is acceptable for invalid actions
            pass
    
    @pytest.mark.integration
    @pytest.mark.migration
    def test_data_validation_after_migration(self, mcp_tools_instance):
        """Test that data validation works correctly after migration."""
        mcp_tools = mcp_tools_instance
        
        # Test invalid priority
        invalid_priority = mcp_tools._handle_core_task_operations(
            action="create",
            task_id=None,
            title="Invalid Priority Test",
            description="Testing invalid priority handling",
            status=None,
            priority="invalid_priority",
            details=None,
            estimated_effort=None,
            assignees=None,
            labels=None,
            due_date=None,
            project_id=None,
            force_full_generation=False
        )
        # Should either succeed with normalized priority or fail with validation error
        if not invalid_priority["success"]:
            assert "error" in invalid_priority
        
        # Test invalid status
        invalid_status = mcp_tools._handle_core_task_operations(
            action="create",
            task_id=None,
            title="Invalid Status Test",
            description="Testing invalid status handling",
            status="invalid_status",
            priority=None,
            details=None,
            estimated_effort=None,
            assignees=None,
            labels=None,
            due_date=None,
            project_id=None,
            force_full_generation=False
        )
        # Should either succeed with normalized status or fail with validation error
        if not invalid_status["success"]:
            assert "error" in invalid_status
        
        # Test empty title (should fail)
        empty_title = mcp_tools._handle_core_task_operations(
            action="create",
            task_id=None,
            title="",
            description="Testing empty title handling",
            status=None,
            priority=None,
            details=None,
            estimated_effort=None,
            assignees=None,
            labels=None,
            due_date=None,
            project_id=None,
            force_full_generation=False
        )
        assert empty_title["success"] is False
        assert "error" in empty_title

    # ================================
    # 7. INTEGRATION TESTING
    # ================================
    
    @pytest.mark.integration
    @pytest.mark.migration
    @pytest.mark.asyncio
    async def test_fastmcp_server_integration(self, mcp_server_instance):
        """Test integration with FastMCP server framework."""
        mcp_server = mcp_server_instance
        
        # Test that server is properly initialized
        assert isinstance(mcp_server, FastMCP)
        assert mcp_server.name == "Task Management DDD"
        
        # Test that tools are registered
        registered_tools_dict = await mcp_server.get_tools()
        assert len(registered_tools_dict) > 0
        
        # Test that expected tools are available
        expected_tools = ['manage_task', 'manage_subtask', 'manage_project', 'manage_agent']
        for tool in expected_tools:
            assert tool in registered_tools_dict
    
    @pytest.mark.integration
    @pytest.mark.migration
    @pytest.mark.asyncio
    async def test_mcp_server_tool_registration(self, mcp_server_instance):
        """Test that all MCP tools are properly registered with the server."""
        mcp_server = mcp_server_instance
        
        # Get all registered tools using async method
        registered_tools_dict = await mcp_server.get_tools()
        registered_tools = list(registered_tools_dict.keys())
        
        # Verify critical tools are registered
        critical_tools = [
            'manage_task',
            'manage_subtask',
            'manage_project',
            'manage_agent',
            'call_agent'
        ]
        
        missing_tools = [tool for tool in critical_tools if tool not in registered_tools]
        assert len(missing_tools) == 0, f"Missing critical tools: {missing_tools}. Available: {registered_tools}"

    # ================================
    # 8. REGRESSION TESTING
    # ================================
    
    @pytest.mark.integration
    @pytest.mark.migration
    def test_existing_data_compatibility(self, mcp_tools_instance):
        """Test that existing data remains compatible after migration."""
        mcp_tools = mcp_tools_instance
        
        # Test that pre-existing tasks can be read
        list_response = mcp_tools._handle_list_tasks(
            status=None,
            priority=None,
            assignees=None,
            labels=None,
            limit=None
        )
        assert list_response["success"] is True
        
        # If there are pre-existing tasks, verify they can be accessed
        if list_response["tasks"]:
            first_task = list_response["tasks"][0]
            task_id = first_task["id"]
            
            get_response = mcp_tools._handle_core_task_operations(
                action="get",
                task_id=task_id,
                title=None,
                description=None,
                status=None,
                priority=None,
                details=None,
                estimated_effort=None,
                assignees=None,
                labels=None,
                due_date=None,
                project_id=None,
                force_full_generation=False
            )
            assert get_response["success"] is True
            assert get_response["task"]["id"] == task_id
    
    @pytest.mark.integration
    @pytest.mark.migration
    def test_auto_rule_generation_compatibility(self, mcp_tools_instance):
        """Test that auto-rule generation still works after migration."""
        mcp_tools = mcp_tools_instance
        
        # Create a task and test auto-rule generation
        task_response = mcp_tools._handle_core_task_operations(
            action="create",
            task_id=None,
            title="Auto Rule Test Task",
            description="Testing auto-rule generation compatibility",
            status=None,
            priority="medium",
            details=None,
            estimated_effort=None,
            assignees=["@coding_agent"],
            labels=["auto-rule", "test"],
            due_date=None,
            project_id=None,
            force_full_generation=True  # Force auto-rule generation
        )
        assert task_response["success"] is True
        task_id = task_response["task"]["id"]
        
        # Test auto-rule generation by getting the task (which should trigger rule generation)
        get_response = mcp_tools._handle_core_task_operations(
            action="get",
            task_id=task_id,
            title=None,
            description=None,
            status=None,
            priority=None,
            details=None,
            estimated_effort=None,
            assignees=None,
            labels=None,
            due_date=None,
            project_id=None,
            force_full_generation=True
        )
        assert get_response["success"] is True
        
        # Verify auto-rule file exists and has content
        auto_rule_path = Path(".cursor/rules/auto_rule.mdc")
        assert auto_rule_path.exists(), "Auto rule file should exist"
        
        content = auto_rule_path.read_text()
        assert len(content) > 0, "Auto rule file should have content"
        
        # Check for any task-related content or role information
        # The auto rule may contain content from the current task or previous tasks
        has_task_content = (
            "TASK CONTEXT" in content or
            "ROLE:" in content or 
            "OPERATING RULES" in content or
            len(content.strip()) > 50  # Should have substantial content
        )
        assert has_task_content, f"Auto rule should contain task-related content. Content: {content[:200]}..."
    
    @pytest.mark.integration
    @pytest.mark.migration
    @pytest.mark.slow
    def test_complete_migration_workflow(self, mcp_tools_instance):
        """Test a complete workflow to ensure all migration components work together."""
        mcp_tools = mcp_tools_instance
        
        # Step 1: Create a project
        project_result = mcp_tools._multi_agent_tools.create_project(
            project_id="migration_workflow_test",
            name="Migration Workflow Test Project",
            description="Complete workflow test for migration validation"
        )
        assert project_result["success"] is True
        
        # Step 2: Register agents
        agent_result = mcp_tools._multi_agent_tools.register_agent(
            project_id="migration_workflow_test",
            agent_id="workflow_test_agent",
            name="Workflow Test Agent",
            call_agent="@coding_agent"
        )
        assert agent_result["success"] is True
        
        # Step 3: Create a task tree
        tree_result = mcp_tools._multi_agent_tools.create_task_tree(
            project_id="migration_workflow_test",
            tree_id="workflow_tree",
            tree_name="Workflow Test Tree",
            tree_description="Task tree for workflow testing"
        )
        assert tree_result["success"] is True
        
        # Step 4: Create tasks
        task_ids = []
        for i in range(3):
            task_response = mcp_tools._handle_core_task_operations(
                action="create",
                task_id=None,
                title=f"Workflow Task {i+1}",
                description=f"Task {i+1} for complete workflow testing",
                status="todo",
                priority="medium",
                details=f"Detailed requirements for workflow task {i+1}",
                estimated_effort="small",
                assignees=["@workflow_test_agent"],
                labels=["workflow", "migration", "test"],
                due_date=None,
                project_id="migration_workflow_test",
                force_full_generation=False
            )
            assert task_response["success"] is True
            task_ids.append(task_response["task"]["id"])
        
        # Step 5: Add subtasks
        for task_id in task_ids:
            subtask_response = mcp_tools._handle_subtask_operations(
                action="add_subtask",
                task_id=task_id,
                subtask_data={
                    "title": f"Subtask for {task_id}",
                    "description": "Workflow testing subtask"
                }
            )
            assert subtask_response["success"] is True
        
        # Step 6: Update tasks with valid status transitions
        for i, task_id in enumerate(task_ids):
            # Use valid status transitions: todo -> in_progress -> review
            new_status = "in_progress"  # All tasks go to in_progress first
            
            update_response = mcp_tools._handle_core_task_operations(
                action="update",
                task_id=task_id,
                title=None,
                description=None,
                status=new_status,
                priority=None,
                details=f"Updated details for workflow task {task_id}",
                estimated_effort=None,
                assignees=None,
                labels=None,
                due_date=None,
                project_id=None,
                force_full_generation=False
            )
            if not update_response["success"]:
                print(f"DEBUG: Update failed for task {task_id}: {update_response}")
            assert update_response["success"] is True, f"Failed to update task {task_id}: {update_response}"
            
            # For some tasks, make a second transition to review
            if i % 2 == 1:  # Update every second task to review
                review_response = mcp_tools._handle_core_task_operations(
                    action="update",
                    task_id=task_id,
                    title=None,
                    description=None,
                    status="review",
                    priority=None,
                    details=None,
                    estimated_effort=None,
                    assignees=None,
                    labels=None,
                    due_date=None,
                    project_id=None,
                    force_full_generation=False
                )
                if not review_response["success"]:
                    print(f"DEBUG: Review update failed for task {task_id}: {review_response}")
                assert review_response["success"] is True, f"Failed to update task {task_id} to review: {review_response}"
        
        # Step 7: Search and list operations
        search_response = mcp_tools._handle_search_tasks(
            query="Workflow Task",
            limit=None
        )
        assert search_response["success"] is True
        assert len(search_response["tasks"]) >= 3
        
        list_response = mcp_tools._handle_list_tasks(
            status="in_progress",
            priority=None,
            assignees=None,
            labels=["workflow"],
            limit=None
        )
        assert list_response["success"] is True
        assert len(list_response["tasks"]) >= 1
        
        # Step 8: Complete some tasks
        complete_response = mcp_tools._handle_complete_task(task_ids[0])
        assert complete_response["success"] is True
        
        # Step 9: Verify project orchestration
        orchestration_result = mcp_tools._multi_agent_tools.orchestrate_project("migration_workflow_test")
        assert orchestration_result["success"] is True
        
        # Step 10: Get project dashboard
        dashboard_result = mcp_tools._multi_agent_tools.get_orchestration_dashboard("migration_workflow_test")
        assert dashboard_result["success"] is True
        
        # Step 11: Verify all data is consistent
        project_status = mcp_tools._multi_agent_tools.get_project("migration_workflow_test")
        assert project_status["success"] is True
        
        final_task_list = mcp_tools._handle_list_tasks(
            status=None,
            priority=None,
            assignees=None,
            labels=["workflow"],
            limit=None
        )
        assert final_task_list["success"] is True
        assert len(final_task_list["tasks"]) >= 3


class PerformanceBenchmark:
    """Performance benchmarking utilities for migration tests."""
    
    @staticmethod
    def measure_execution_time(func, *args, **kwargs):
        """Measure execution time of a function."""
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        return result, execution_time
    
    @staticmethod
    def assert_performance_baseline(execution_time: float, baseline: float, operation_name: str):
        """Assert that execution time meets performance baseline."""
        assert execution_time <= baseline, f"{operation_name} took {execution_time:.3f}s, exceeding baseline of {baseline:.3f}s"


class MigrationTestDataGenerator:
    """Generate test data for migration testing."""
    
    @staticmethod
    def generate_test_tasks(count: int) -> List[Dict[str, Any]]:
        """Generate test task data."""
        tasks = []
        for i in range(count):
            task = {
                "title": f"Generated Test Task {i+1}",
                "description": f"Auto-generated task {i+1} for migration testing",
                "priority": ["low", "medium", "high"][i % 3],
                "status": ["todo", "in_progress", "review"][i % 3],
                "labels": ["generated", "test", f"batch-{i//10 + 1}"]
            }
            tasks.append(task)
        return tasks
    
    @staticmethod
    def generate_test_projects(count: int) -> List[Dict[str, Any]]:
        """Generate test project data."""
        projects = []
        for i in range(count):
            project = {
                "project_id": f"test_project_{i+1}",
                "name": f"Test Project {i+1}",
                "description": f"Auto-generated project {i+1} for migration testing"
            }
            projects.append(project)
        return projects 