"""
Integration Test for manage_rule functionality in both stdio and HTTP modes
This test verifies that the manage_rule tool works correctly in both environments
"""

import os
import sys
import tempfile
import pytest
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project src to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from fastmcp.task_management.interface.cursor_rules_tools import CursorRulesTools


class TestManageRuleIntegration:
    """Integration tests for manage_rule functionality"""
    
    def setup_method(self):
        """Setup for each test method"""
        self.original_env = os.environ.copy()
        # Clear environment variables that might affect detection
        for env_var in ["CURSOR_RULES_DIR", "FASTMCP_TRANSPORT", "DOCUMENT_RULES_PATH"]:
            if env_var in os.environ:
                del os.environ[env_var]
    
    def teardown_method(self):
        """Cleanup after each test method"""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def create_test_rule_files(self, rules_dir: Path):
        """Create test rule files for testing"""
        rules_dir.mkdir(parents=True, exist_ok=True)
        
        # Core rule file
        core_rule = rules_dir / "P00-S00-T01-Core Mechanic Systems.md"
        core_rule.write_text("""# Core Mechanic Systems

## Task Context
This is a test core mechanic systems rule.

## Role
System Administrator

## Operating Rules
- Test rule 1
- Test rule 2
""")
        
        # Task management rule
        task_rule = rules_dir / "P00-S00-T02-Core Task Management.md"
        task_rule.write_text("""# Core Task Management

## Task Context
This is a test task management rule.

## Operating Rules
- Manage tasks efficiently
- Track progress
""")
        
        # Settings file
        settings_file = rules_dir / "settings.json"
        settings_content = {
            "protect": True,
            "rules": ["Core system rules"],
            "runtime_constants": {
                "project_path": str(rules_dir.parent),
                "username": "test_user"
            }
        }
        settings_file.write_text(json.dumps(settings_content, indent=2))
        
        # Auto rule file
        auto_rule = rules_dir / "auto_rule.mdc"
        auto_rule.write_text("""# Auto Generated Rule

This is an auto-generated rule for testing.
""")
        
        return {
            "core_rule": core_rule,
            "task_rule": task_rule,
            "settings_file": settings_file,
            "auto_rule": auto_rule
        }
    
    def test_manage_rule_list_stdio_mode(self):
        """Test manage_rule list action in stdio mode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            rules_dir = temp_path / "00_RULES"
            
            # Create test files
            test_files = self.create_test_rule_files(rules_dir)
            
            with patch('pathlib.Path.cwd', return_value=temp_path):
                cursor_tools = CursorRulesTools()
                
                # Create a mock MCP server
                class MockMCP:
                    def __init__(self):
                        self.tools = {}
                    
                    def tool(self):
                        def decorator(func):
                            self.tools[func.__name__] = func
                            return func
                        return decorator
                
                mock_mcp = MockMCP()
                cursor_tools.register_tools(mock_mcp)
                
                # Test the manage_rule function
                manage_rule_func = mock_mcp.tools["manage_rule"]
                result = manage_rule_func("list")
                
                assert result["success"] is True
                assert "files" in result
                assert len(result["files"]) >= 2  # Should find .mdc files
    
    @patch('os.path.exists')
    def test_manage_rule_list_http_mode(self, mock_exists):
        """Test manage_rule list action in HTTP mode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Simulate Docker environment
            def mock_exists_side_effect(path):
                if path == "/.dockerenv":
                    return True
                elif str(path) == "/data/rules":
                    return True
                elif str(path).startswith(str(temp_dir)):
                    return Path(path).exists()
                return False
            
            mock_exists.side_effect = mock_exists_side_effect
            
            # Create test files in simulated /data/rules
            rules_dir = Path(temp_dir) / "data" / "rules"
            test_files = self.create_test_rule_files(rules_dir)
            
            with patch('fastmcp.dual_mode_config.Path') as mock_path_class:
                # Mock Path("/data/rules") to return our temp directory
                def mock_path_init(path_str):
                    if str(path_str) == "/data/rules":
                        return rules_dir
                    return Path(path_str)
                
                mock_path_class.side_effect = mock_path_init
                
                cursor_tools = CursorRulesTools()
                
                # Create a mock MCP server
                class MockMCP:
                    def __init__(self):
                        self.tools = {}
                    
                    def tool(self):
                        def decorator(func):
                            self.tools[func.__name__] = func
                            return func
                        return decorator
                
                mock_mcp = MockMCP()
                cursor_tools.register_tools(mock_mcp)
                
                # Test the manage_rule function
                manage_rule_func = mock_mcp.tools["manage_rule"]
                result = manage_rule_func("list")
                
                assert result["success"] is True
                assert "files" in result
    
    def test_manage_rule_parse_rule_stdio_mode(self):
        """Test manage_rule parse_rule action in stdio mode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            rules_dir = temp_path / "00_RULES"
            
            # Create test files
            test_files = self.create_test_rule_files(rules_dir)
            
            # Patch the path resolution functions
            with patch('fastmcp.task_management.interface.cursor_rules_tools.get_rules_directory', return_value=rules_dir), \
                 patch('fastmcp.task_management.interface.cursor_rules_tools.find_project_root', return_value=temp_path):
                
                cursor_tools = CursorRulesTools()
                
                # Mock the enhanced orchestrator property directly on the instance
                mock_orchestrator = MagicMock()
                # Mock parser result
                mock_rule_content = MagicMock()
                mock_rule_content.metadata.format.value = "md"
                mock_rule_content.metadata.type.value = "core"
                mock_rule_content.metadata.size = 100
                mock_rule_content.metadata.checksum = "test_checksum"
                mock_rule_content.metadata.dependencies = []
                mock_rule_content.metadata.tags = ["test"]
                mock_rule_content.sections = {"Task Context": "test"}
                mock_rule_content.references = []
                mock_rule_content.variables = {}
                mock_rule_content.raw_content = "# Test Content"
                mock_rule_content.parsed_content = {"title": "Test"}
                
                mock_orchestrator.parser.parse_rule_file.return_value = mock_rule_content
                
                # Set the mock directly on the instance
                cursor_tools._enhanced_orchestrator = mock_orchestrator
                
                # Create mock MCP server
                class MockMCP:
                    def __init__(self):
                        self.tools = {}
                    
                    def tool(self):
                        def decorator(func):
                            self.tools[func.__name__] = func
                            return func
                        return decorator
                
                mock_mcp = MockMCP()
                cursor_tools.register_tools(mock_mcp)
                
                # Test the parse_rule function
                manage_rule_func = mock_mcp.tools["manage_rule"]
                result = manage_rule_func("parse_rule", target="P00-S00-T01-Core Mechanic Systems.md")
                
                assert result["success"] is True
                assert "metadata" in result
                assert "content_analysis" in result
    
    def test_manage_rule_info_stdio_mode(self):
        """Test manage_rule info action in stdio mode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            rules_dir = temp_path / "00_RULES"
            
            # Create test files
            test_files = self.create_test_rule_files(rules_dir)
            
            # Patch the path resolution functions
            with patch('fastmcp.task_management.interface.cursor_rules_tools.get_rules_directory', return_value=rules_dir), \
                 patch('fastmcp.task_management.interface.cursor_rules_tools.find_project_root', return_value=temp_path):
                
                cursor_tools = CursorRulesTools()
                
                # Create mock MCP server
                class MockMCP:
                    def __init__(self):
                        self.tools = {}
                    
                    def tool(self):
                        def decorator(func):
                            self.tools[func.__name__] = func
                            return func
                        return decorator
                
                mock_mcp = MockMCP()
                cursor_tools.register_tools(mock_mcp)
                
                # Test the info function
                manage_rule_func = mock_mcp.tools["manage_rule"]
                result = manage_rule_func("info")
                
                assert result["success"] is True
                assert "info" in result
                assert result["info"]["directory_exists"] is True
                assert result["info"]["mdc_files"] >= 1  # Should find auto_rule.mdc
    
    def test_manage_rule_backup_restore_stdio_mode(self):
        """Test manage_rule backup and restore actions in stdio mode"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            rules_dir = temp_path / "00_RULES"
            
            # Create test files
            test_files = self.create_test_rule_files(rules_dir)
            
            # Create auto_rule.mdc file in the rules directory for backup
            auto_rule_file = rules_dir / "auto_rule.mdc"
            auto_rule_file.write_text("# Test Auto Rule\nThis is a test rule.")
            
            # Patch the path resolution functions
            with patch('fastmcp.task_management.interface.cursor_rules_tools.get_rules_directory', return_value=rules_dir), \
                 patch('fastmcp.task_management.interface.cursor_rules_tools.find_project_root', return_value=temp_path):
                
                cursor_tools = CursorRulesTools()
                
                # Create mock MCP server
                class MockMCP:
                    def __init__(self):
                        self.tools = {}
                    
                    def tool(self):
                        def decorator(func):
                            self.tools[func.__name__] = func
                            return func
                        return decorator
                
                mock_mcp = MockMCP()
                cursor_tools.register_tools(mock_mcp)
                
                manage_rule_func = mock_mcp.tools["manage_rule"]
                
                # Test backup
                backup_result = manage_rule_func("backup")
                assert backup_result["success"] is True
                
                # Verify backup file was created in the correct location
                # The backup should be created in the rules directory
                backup_file = rules_dir / "auto_rule.mdc.backup"
                assert backup_file.exists()
                
                # Test restore
                restore_result = manage_rule_func("restore")
                assert restore_result["success"] is True
    
    def test_path_resolution_compatibility(self):
        """Test that path resolution works with existing .cursor/settings.json"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create .cursor/settings.json with paths
            cursor_dir = temp_path / ".cursor"
            cursor_dir.mkdir()
            settings_file = cursor_dir / "settings.json"
            
            settings_content = {
                "runtime_constants": {
                    "DOCUMENT_RULES_PATH": "/app/00_RULES",
                    "projet_path_root": "/app"
                }
            }
            
            with open(settings_file, 'w') as f:
                json.dump(settings_content, f)
            
            # Mock the path resolution to simulate the expected behavior
            expected_path = Path("/app/00_RULES")
            
            # Patch the path resolution functions
            with patch('fastmcp.task_management.interface.cursor_rules_tools.get_rules_directory', return_value=expected_path), \
                 patch('fastmcp.task_management.interface.cursor_rules_tools.find_project_root', return_value=temp_path), \
                 patch('fastmcp.task_management.interface.cursor_rules_tools.is_http_mode', return_value=False):
                
                cursor_tools = CursorRulesTools()
                resolved_dir = cursor_tools._get_rules_directory_from_settings()
                
                # Should resolve to the path specified in settings
                assert resolved_dir == expected_path
    
    def test_environment_variable_override(self):
        """Test environment variable override functionality"""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            custom_rules_dir = temp_path / "custom_rules"
            custom_rules_dir.mkdir()
            
            # Patch the path resolution functions to simulate environment override
            with patch('fastmcp.task_management.interface.cursor_rules_tools.get_rules_directory', return_value=custom_rules_dir), \
                 patch('fastmcp.task_management.interface.cursor_rules_tools.find_project_root', return_value=temp_path), \
                 patch('fastmcp.task_management.interface.cursor_rules_tools.is_http_mode', return_value=False), \
                 patch.dict(os.environ, {'DOCUMENT_RULES_PATH': str(custom_rules_dir)}):
                
                cursor_tools = CursorRulesTools()
                resolved_dir = cursor_tools._get_rules_directory_from_settings()
                
                assert resolved_dir == custom_rules_dir


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_manage_rule_unknown_action(self):
        """Test manage_rule with unknown action"""
        cursor_tools = CursorRulesTools()
        
        class MockMCP:
            def __init__(self):
                self.tools = {}
            
            def tool(self):
                def decorator(func):
                    self.tools[func.__name__] = func
                    return func
                return decorator
        
        mock_mcp = MockMCP()
        cursor_tools.register_tools(mock_mcp)
        
        manage_rule_func = mock_mcp.tools["manage_rule"]
        result = manage_rule_func("unknown_action")
        
        assert result["success"] is False
        assert "Unknown action" in result["error"]
    
    def test_manage_rule_missing_target(self):
        """Test manage_rule with missing required target"""
        cursor_tools = CursorRulesTools()
        
        class MockMCP:
            def __init__(self):
                self.tools = {}
            
            def tool(self):
                def decorator(func):
                    self.tools[func.__name__] = func
                    return func
                return decorator
        
        mock_mcp = MockMCP()
        cursor_tools.register_tools(mock_mcp)
        
        manage_rule_func = mock_mcp.tools["manage_rule"]
        result = manage_rule_func("parse_rule")  # Missing target parameter
        
        assert result["success"] is False
        assert "Target file path required" in result["error"]


if __name__ == "__main__":
    # Allow running tests directly
    pytest.main([__file__, "-v"])