"""
Integration Test: MCP Server Integration
Task 1 - MCP Server Core Functionality Testing (Integration)
Duration: 2-3 minutes
"""

import pytest
import asyncio
import sys
import os
import tempfile
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))

# Use the new consolidated tools
from fastmcp.task_management.interface.consolidated_mcp_tools_v2 import ConsolidatedMCPToolsV2


class TestMCPIntegration:
    """Test MCP server integration functionality."""
    
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
            
            # Create sample tasks.json
            tasks_data = {
                "tasks": []
            }
            
            tasks_file = tasks_dir / "tasks.json"
            with open(tasks_file, 'w') as f:
                json.dump(tasks_data, f, indent=2)
            
            yield temp_path
    
    @pytest.mark.integration
    @pytest.mark.mcp
    @pytest.mark.slow
    def test_mcp_server_full_lifecycle(self, temp_project_structure):
        """Test complete MCP server lifecycle with real components."""
        try:
            # Change working directory to temp structure for test
            original_cwd = os.getcwd()
            os.chdir(temp_project_structure)
            
            from fastmcp.task_management.infrastructure.repositories.json_task_repository import JsonTaskRepository
            from fastmcp.task_management.infrastructure.services.file_auto_rule_generator import FileAutoRuleGenerator
            
            # Initialize real components
            repository = JsonTaskRepository()
            auto_rule_generator = FileAutoRuleGenerator()
            mcp_tools = ConsolidatedMCPToolsV2(task_repository=repository)
            
            # Test that components are properly initialized
            assert repository is not None
            assert auto_rule_generator is not None
            assert mcp_tools is not None
            
            # Test that MCP tools has the required dependencies
            assert mcp_tools._task_repository is not None
            assert mcp_tools._auto_rule_generator is not None
            assert mcp_tools._task_app_service is not None
            
            # Test that register_tools method exists
            assert hasattr(mcp_tools, 'register_tools')
            
            # Test basic repository functionality
            from fastmcp.task_management.domain.entities.task import Task
            from fastmcp.task_management.domain.value_objects.task_id import TaskId
            from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
            from fastmcp.task_management.domain.value_objects.priority import Priority
            
            # Create a test task
            task_id = repository.get_next_id()
            task = Task.create(
                id=task_id,
                title="Integration Test Task",
                description="Test task for integration testing",
                status=TaskStatus.todo(),
                priority=Priority.high(),
                assignees=["qa_engineer"],
                labels=["integration", "test"],
            )
            
            # Test repository save
            repository.save(task)
            
            # Test repository find_by_id
            retrieved_task = repository.find_by_id(task_id)
            assert retrieved_task is not None
            assert retrieved_task.title == "Integration Test Task"
            assert retrieved_task.priority.value == "high"
            assert "qa_engineer" in retrieved_task.assignees
            
            # Test repository find_all
            all_tasks = repository.find_all()
            assert len(all_tasks) >= 1
            
            # Test repository search
            search_results = repository.search("Integration")
            assert len(search_results) >= 1
            
            # Test repository delete
            success = repository.delete(task_id)
            assert success is True
            
            # Verify deletion
            deleted_task = repository.find_by_id(task_id)
            assert deleted_task is None
                
        finally:
            # Restore original working directory
            os.chdir(original_cwd)
    
    @pytest.mark.integration
    @pytest.mark.mcp
    def test_repository_integration(self, temp_project_structure):
        """Test repository integration with file system."""
        try:
            original_cwd = os.getcwd()
            os.chdir(temp_project_structure)
            
            from fastmcp.task_management.infrastructure.repositories.json_task_repository import JsonTaskRepository
            from fastmcp.task_management.domain.entities.task import Task
            from fastmcp.task_management.domain.value_objects.task_id import TaskId
            from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
            from fastmcp.task_management.domain.value_objects.priority import Priority
            
            # Initialize repository
            repository = JsonTaskRepository()
            
            # Create a task entity
            task_id = repository.get_next_id()
            task = Task.create(
                id=task_id,
                title="Repository Integration Test",
                description="Test repository integration",
                status=TaskStatus.todo(),
                priority=Priority.high(),
                assignees=["qa_engineer"],
                labels=["integration"],
            )
            
            # Test save
            repository.save(task)
            
            # Test find_by_id
            retrieved_task = repository.find_by_id(task_id)
            assert retrieved_task is not None
            assert retrieved_task.title == "Repository Integration Test"
            
            # Test find_all
            all_tasks = repository.find_all()
            assert len(all_tasks) >= 1
            
            # Test update by saving again with different title
            task.update_title("Updated Repository Test")
            repository.save(task)
            updated_task = repository.find_by_id(task_id)
            assert updated_task.title == "Updated Repository Test"
            
            # Test search
            search_results = repository.search("Repository")
            assert len(search_results) >= 1
            
            # Test delete
            success = repository.delete(task_id)
            assert success is True
            
            # Verify deletion
            deleted_task = repository.find_by_id(task_id)
            assert deleted_task is None
                
        finally:
            os.chdir(original_cwd)
    
    @pytest.mark.integration
    @pytest.mark.mcp
    def test_auto_rule_generation_integration(self, temp_project_structure):
        """Test auto rule generation integration."""
        try:
            original_cwd = os.getcwd()
            os.chdir(temp_project_structure)
            
            from fastmcp.task_management.infrastructure.services.file_auto_rule_generator import FileAutoRuleGenerator
            from fastmcp.task_management.domain.entities.task import Task
            from fastmcp.task_management.domain.value_objects.task_id import TaskId
            from fastmcp.task_management.domain.value_objects.task_status import TaskStatus
            from fastmcp.task_management.domain.value_objects.priority import Priority
            from fastmcp.task_management.application.use_cases.get_task import GetTaskUseCase
            from fastmcp.task_management.infrastructure.repositories.json_task_repository import JsonTaskRepository
            from fastmcp.task_management.application.dtos.task_dto import TaskResponse

            # Initialize components
            repository = JsonTaskRepository()
            auto_rule_generator = FileAutoRuleGenerator()
            get_task_use_case = GetTaskUseCase(
                task_repository=repository, 
                auto_rule_generator=auto_rule_generator
            )

            # Create a test task
            task_id = repository.get_next_id()
            task = Task.create(
                id=task_id,
                title="Auto Rule Integration Test",
                description="Test rule generation on get_task",
                status=TaskStatus.todo(),
                priority=Priority.high(),
                assignees=["senior_developer"]
            )
            repository.save(task)

            # Execute use case, forcing full generation logic
            result = get_task_use_case.execute(task_id.value, force_full_generation=True)
            
            # Assert success and that auto rule file exists
            assert isinstance(result, TaskResponse)
            assert os.path.exists(auto_rule_generator.output_path)
            
            # Check content of generated file
            with open(auto_rule_generator.output_path, 'r') as f:
                content = f.read()
            
            assert "Dynamic AI Agent Rules for 💻 Coding Agent" in content
            assert "Auto Rule Integration Test" in content
                
        finally:
            os.chdir(original_cwd)
    
    @pytest.mark.integration
    @pytest.mark.mcp
    def test_error_handling_integration(self, temp_project_structure):
        """Test error handling integration."""
        try:
            original_cwd = os.getcwd()
            os.chdir(temp_project_structure)
            
            from fastmcp.task_management.infrastructure.repositories.json_task_repository import JsonTaskRepository
            from fastmcp.task_management.domain.value_objects.task_id import TaskId
            
            repository = JsonTaskRepository()
            
            # Test finding non-existent task
            non_existent_id = TaskId.from_string("20250101999")
            assert repository.find_by_id(non_existent_id) is None
            
            # Test deleting non-existent task
            assert repository.delete(non_existent_id) is False

        finally:
            os.chdir(original_cwd)
            
    @pytest.mark.integration
    @pytest.mark.mcp
    def test_file_system_persistence(self, temp_project_structure):
        """Test file system persistence across instances."""
        try:
            original_cwd = os.getcwd()
            os.chdir(temp_project_structure)

            from fastmcp.task_management.infrastructure.repositories.json_task_repository import JsonTaskRepository
            from fastmcp.task_management.domain.entities.task import Task
            from fastmcp.task_management.domain.value_objects.task_id import TaskId
            
            # First instance
            repo1 = JsonTaskRepository()
            task_id = repo1.get_next_id()
            task = Task.create(id=task_id, title="Persistence Test", description="Test persistence")
            repo1.save(task)
            
            # Second instance should load the data
            repo2 = JsonTaskRepository()
            retrieved_task = repo2.find_by_id(task_id)
            
            assert retrieved_task is not None
            assert retrieved_task.title == "Persistence Test"

        finally:
            os.chdir(original_cwd) 