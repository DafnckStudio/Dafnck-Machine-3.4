"""Tests for Consolidated MCP Tools v2"""

import pytest
import tempfile
import os
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import the consolidated tools
from task_mcp.interface.consolidated_mcp_tools_v2 import ConsolidatedMCPToolsV2, SimpleMultiAgentTools


class TestSimpleMultiAgentTools:
    """Test the SimpleMultiAgentTools class with proper isolation"""
    
    @pytest.fixture
    def temp_projects_file(self):
        """Create a temporary projects file for testing"""
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, 'test_projects.json')
        
        yield temp_file
        
        # Cleanup after test
        if os.path.exists(temp_file):
            os.remove(temp_file)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def multi_agent_tools(self, temp_projects_file):
        """Create SimpleMultiAgentTools instance with temporary file"""
        return SimpleMultiAgentTools(projects_file_path=temp_projects_file)
    
    def test_create_project(self, multi_agent_tools, temp_projects_file):
        """Test project creation with isolated temporary file"""
        result = multi_agent_tools.create_project("test_project", "Test Project", "Test description")
        
        assert result["success"] is True
        assert result["project"]["id"] == "test_project"
        assert result["project"]["name"] == "Test Project"
        assert result["project"]["description"] == "Test description"
        assert "main" in result["project"]["task_trees"]
        
        # Verify file was created and contains expected data
        assert os.path.exists(temp_projects_file)
        
        # Verify the file doesn't interfere with production
        production_file = os.path.join(os.path.dirname(__file__), '../../../.cursor/rules/brain/projects.json')
        if os.path.exists(production_file):
            # If production file exists, ensure our test data isn't in it
            import json
            with open(production_file, 'r') as f:
                prod_data = json.load(f)
            assert "test_project" not in prod_data
    
    def test_get_project_success(self, multi_agent_tools):
        """Test getting an existing project"""
        # Create project first
        multi_agent_tools.create_project("test_project", "Test Project")
        
        result = multi_agent_tools.get_project("test_project")
        assert result["success"] is True
        assert result["project"]["id"] == "test_project"
    
    def test_get_project_not_found(self, multi_agent_tools):
        """Test getting a non-existent project"""
        result = multi_agent_tools.get_project("nonexistent")
        assert result["success"] is False
        assert "not found" in result["error"]
    
    def test_list_projects(self, multi_agent_tools):
        """Test listing projects"""
        # Initially empty
        result = multi_agent_tools.list_projects()
        assert result["success"] is True
        assert result["count"] == 0
        
        # Create a project
        multi_agent_tools.create_project("test1", "Test 1")
        multi_agent_tools.create_project("test2", "Test 2")
        
        result = multi_agent_tools.list_projects()
        assert result["success"] is True
        assert result["count"] == 2
    
    def test_create_task_tree(self, multi_agent_tools):
        """Test creating task tree"""
        multi_agent_tools.create_project("test_project", "Test Project")
        
        result = multi_agent_tools.create_task_tree("test_project", "frontend", "Frontend Tasks", "UI development")
        assert result["success"] is True
        assert result["tree"]["id"] == "frontend"
        assert result["tree"]["name"] == "Frontend Tasks"
    
    def test_register_agent(self, multi_agent_tools):
        """Test agent registration"""
        multi_agent_tools.create_project("test_project", "Test Project")
        
        result = multi_agent_tools.register_agent(
            "test_project", "agent1", "Test Agent", call_agent="@test-agent"
        )
        
        assert result["success"] is True
        assert result["agent"]["id"] == "agent1"
        assert result["agent"]["name"] == "Test Agent"
        assert result["agent"]["call_agent"] == "@test-agent"
    
    def test_assign_agent_to_tree(self, multi_agent_tools):
        """Test agent assignment to task tree"""
        multi_agent_tools.create_project("test_project", "Test Project")
        multi_agent_tools.register_agent("test_project", "agent1", "Test Agent")
        multi_agent_tools.create_task_tree("test_project", "frontend", "Frontend Tasks")
        
        result = multi_agent_tools.assign_agent_to_tree("test_project", "agent1", "frontend")
        assert result["success"] is True
        assert "assigned" in result["message"]
    
    def test_projects_file_isolation(self, temp_projects_file):
        """Test that temporary projects file is completely isolated"""
        # Create two separate instances with different temp files
        temp_dir1 = tempfile.mkdtemp()
        temp_dir2 = tempfile.mkdtemp()
        temp_file1 = os.path.join(temp_dir1, 'test1.json')
        temp_file2 = os.path.join(temp_dir2, 'test2.json')
        
        try:
            tools1 = SimpleMultiAgentTools(projects_file_path=temp_file1)
            tools2 = SimpleMultiAgentTools(projects_file_path=temp_file2)
            
            # Create projects in each instance
            tools1.create_project("project1", "Project 1")
            tools2.create_project("project2", "Project 2")
            
            # Verify isolation
            result1 = tools1.list_projects()
            result2 = tools2.list_projects()
            
            assert result1["count"] == 1
            assert result2["count"] == 1
            assert result1["projects"][0]["id"] == "project1"
            assert result2["projects"][0]["id"] == "project2"
            
        finally:
            # Cleanup
            for temp_dir in [temp_dir1, temp_dir2]:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)


class TestConsolidatedMCPToolsV2:
    """Test the main ConsolidatedMCPToolsV2 class with proper isolation"""
    
    @pytest.fixture
    def temp_projects_file(self):
        """Create a temporary projects file for testing"""
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, 'test_projects.json')
        
        yield temp_file
        
        # Cleanup after test
        if os.path.exists(temp_file):
            os.remove(temp_file)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def temp_tasks_file(self):
        """Create a temporary tasks file"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.write('{"tasks": {}, "project_meta": {}}')
        temp_file.close()
        yield temp_file.name
        os.unlink(temp_file.name)
    
    @pytest.fixture
    def consolidated_tools(self, temp_tasks_file, temp_projects_file):
        """Create ConsolidatedMCPToolsV2 instance with mocked dependencies and isolated files"""
        with patch('task_mcp.interface.consolidated_mcp_tools_v2.JsonTaskRepository') as mock_repo_class, \
             patch('task_mcp.interface.consolidated_mcp_tools_v2.FileAutoRuleGenerator') as mock_generator_class, \
             patch('task_mcp.interface.consolidated_mcp_tools_v2.TaskApplicationService') as mock_service_class, \
             patch('task_mcp.interface.consolidated_mcp_tools_v2.CursorRulesTools') as mock_cursor_class:
            
            # Configure mock instances
            mock_repo = Mock()
            mock_generator = Mock()
            mock_service = Mock()
            mock_cursor = Mock()
            
            mock_repo_class.return_value = mock_repo
            mock_generator_class.return_value = mock_generator
            mock_service_class.return_value = mock_service
            mock_cursor_class.return_value = mock_cursor
            
            # Create tools with isolated projects file
            tools = ConsolidatedMCPToolsV2(projects_file_path=temp_projects_file)
            tools._mock_repo = mock_repo
            tools._mock_generator = mock_generator
            tools._mock_service = mock_service
            tools._mock_cursor = mock_cursor
            
            return tools
    
    def test_initialization(self, consolidated_tools):
        """Test that ConsolidatedMCPToolsV2 initializes correctly"""
        assert consolidated_tools is not None
        assert hasattr(consolidated_tools, '_task_repository')
        assert hasattr(consolidated_tools, '_auto_rule_generator')
        assert hasattr(consolidated_tools, '_task_app_service')
        assert hasattr(consolidated_tools, '_cursor_rules_tools')
        assert hasattr(consolidated_tools, '_multi_agent_tools')
        assert isinstance(consolidated_tools._multi_agent_tools, SimpleMultiAgentTools)
    
    def test_register_tools_method_exists(self, consolidated_tools):
        """Test that register_tools method exists and can be called"""
        mock_mcp = Mock()
        mock_mcp.tool = Mock(return_value=lambda f: f)  # Mock decorator
        
        # Should not raise an exception
        consolidated_tools.register_tools(mock_mcp)
        
        # Verify that tool decorator was called (indicating tools were registered)
        assert mock_mcp.tool.called
    
    def test_handle_core_task_operations_exists(self, consolidated_tools):
        """Test that helper methods exist"""
        assert hasattr(consolidated_tools, '_handle_core_task_operations')
        assert hasattr(consolidated_tools, '_handle_complete_task')
        assert hasattr(consolidated_tools, '_handle_list_tasks')
        assert hasattr(consolidated_tools, '_handle_search_tasks')
        assert hasattr(consolidated_tools, '_handle_do_next')
        assert hasattr(consolidated_tools, '_handle_subtask_operations')
        assert hasattr(consolidated_tools, '_handle_dependency_operations')
    
    def test_multi_agent_integration_isolated(self, consolidated_tools, temp_projects_file):
        """Test that multi-agent functionality is integrated and isolated"""
        # Test project creation through multi-agent tools
        result = consolidated_tools._multi_agent_tools.create_project("test_isolated", "Test Isolated Project")
        assert result["success"] is True
        
        # Test that we can get the project back
        result = consolidated_tools._multi_agent_tools.get_project("test_isolated")
        assert result["success"] is True
        assert result["project"]["name"] == "Test Isolated Project"
        
        # Verify the test data is in the temporary file, not production
        assert os.path.exists(temp_projects_file)
        
        # Verify production file is not affected
        production_file = os.path.join(os.path.dirname(__file__), '../../../.cursor/rules/brain/projects.json')
        if os.path.exists(production_file):
            import json
            with open(production_file, 'r') as f:
                prod_data = json.load(f)
            assert "test_isolated" not in prod_data


class TestConsolidatedToolsIntegration:
    """Integration tests for the consolidated tools with proper isolation"""
    
    @pytest.fixture
    def temp_projects_file(self):
        """Create a temporary projects file for integration tests"""
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, 'integration_test_projects.json')
        
        yield temp_file
        
        # Cleanup after test
        if os.path.exists(temp_file):
            os.remove(temp_file)
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
    
    def test_tool_registration_integration(self, temp_projects_file):
        """Test that tools can be registered without errors"""
        mock_mcp = Mock()
        mock_mcp.tool = Mock(return_value=lambda f: f)
        
        with patch('task_mcp.interface.consolidated_mcp_tools_v2.JsonTaskRepository'), \
             patch('task_mcp.interface.consolidated_mcp_tools_v2.FileAutoRuleGenerator'), \
             patch('task_mcp.interface.consolidated_mcp_tools_v2.TaskApplicationService'), \
             patch('task_mcp.interface.consolidated_mcp_tools_v2.CursorRulesTools'):
            
            tools = ConsolidatedMCPToolsV2(projects_file_path=temp_projects_file)
            tools.register_tools(mock_mcp)
            
            # Verify tools were registered
            assert mock_mcp.tool.call_count >= 3  # At least 3 main tools
    
    def test_error_handling(self, temp_projects_file):
        """Test basic error handling with isolated files"""
        with patch('task_mcp.interface.consolidated_mcp_tools_v2.JsonTaskRepository'), \
             patch('task_mcp.interface.consolidated_mcp_tools_v2.FileAutoRuleGenerator'), \
             patch('task_mcp.interface.consolidated_mcp_tools_v2.TaskApplicationService'), \
             patch('task_mcp.interface.consolidated_mcp_tools_v2.CursorRulesTools'):
            
            tools = ConsolidatedMCPToolsV2(projects_file_path=temp_projects_file)
            
            # Test invalid task operations
            result = tools._handle_core_task_operations("invalid_action", None, None, None, None, None, None, None, None, None, None)
            # Should not raise an exception - error handling should be graceful
            assert isinstance(result, (dict, type(None)))
    
    def test_complete_isolation_verification(self):
        """Comprehensive test to verify complete isolation from production data"""
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, 'isolation_test.json')
        
        try:
            # Create tools with isolated file
            tools = SimpleMultiAgentTools(projects_file_path=temp_file)
            
            # Create test data
            tools.create_project("isolation_test", "Isolation Test Project")
            
            # Verify test file exists and has our data
            assert os.path.exists(temp_file)
            import json
            with open(temp_file, 'r') as f:
                test_data = json.load(f)
            assert "isolation_test" in test_data
            
            # Verify production file is not affected
            production_file = os.path.join(os.path.dirname(__file__), '../../../.cursor/rules/brain/projects.json')
            if os.path.exists(production_file):
                with open(production_file, 'r') as f:
                    prod_data = json.load(f)
                assert "isolation_test" not in prod_data, "Test data leaked into production file!"
            
        finally:
            # Cleanup
            if os.path.exists(temp_file):
                os.remove(temp_file)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir) 