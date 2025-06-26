"""Tests for Consolidated MCP Tools v2 (Updated from old MCPTaskTools) - Using Test Isolation"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

import pytest
import tempfile
import os
import shutil
from unittest.mock import Mock, patch

# Import test isolation system
from test_environment_config import isolated_test_environment

# Updated import to use consolidated v2 tools
from fastmcp.task_management.interface.consolidated_mcp_tools import ConsolidatedMCPTools


class TestConsolidatedMCPToolsIsolated:
    """Test consolidated MCP tools v2 functionality with complete test isolation"""
    
    def test_production_data_safety_verification(self):
        """Verify that production data is never touched during testing"""
        import json
        from pathlib import Path
        
        # Check production files exist and are untouched
        production_projects = Path(".cursor/rules/brain/projects.json")
        
        if production_projects.exists():
            with open(production_projects, 'r') as f:
                original_data = json.load(f)
            
            # Run test with isolation
            with isolated_test_environment(test_id="safety_test") as config:
                # Verify test files are separate
                assert str(config.test_files["projects"]).endswith(".test.json")
                assert config.test_files["projects"] != production_projects
                
                # Modify test data
                config.add_test_project("safety_test_project", "Safety Test")
                
                # Verify test file has our changes
                with open(config.test_files["projects"], 'r') as f:
                    test_data = json.load(f)
                assert "safety_test_project" in test_data
            
            # Verify production file is unchanged
            with open(production_projects, 'r') as f:
                final_data = json.load(f)
            
            assert original_data == final_data
            print("✅ Production data safety verified")
        else:
            print("ℹ️  No production projects.json found - safety test skipped")
    
    @pytest.mark.isolated
    def test_isolated_project_creation(self):
        """Test project creation in isolated environment"""
        with isolated_test_environment(test_id="project_test") as config:
            # Verify isolation
            assert config.test_files["projects"].suffix == ".json"
            assert ".test." in str(config.test_files["projects"])
            
            # Test project operations
            config.add_test_project(
                project_id="isolated_test_project",
                name="Isolated Test Project",
                description="This is a test project in isolation"
            )
            
            # Verify project was created
            import json
            with open(config.test_files["projects"], 'r') as f:
                data = json.load(f)
            
            assert "isolated_test_project" in data
            assert data["isolated_test_project"]["test_environment"] == True
            assert data["isolated_test_project"]["name"] == "Isolated Test Project"
            
            print("✅ Isolated project creation test passed")
    
    @pytest.mark.isolated  
    def test_multiple_isolated_environments(self):
        """Test that multiple isolated environments don't interfere"""
        import json
        
        # Create first environment
        with isolated_test_environment(test_id="env1") as config1:
            config1.add_test_project("project1", "Project One")
            
            with open(config1.test_files["projects"], 'r') as f:
                data1 = json.load(f)
            
            # Create second environment
            with isolated_test_environment(test_id="env2") as config2:
                config2.add_test_project("project2", "Project Two")
                
                with open(config2.test_files["projects"], 'r') as f:
                    data2 = json.load(f)
                
                # Verify environments are separate
                assert "project1" in data1
                assert "project1" not in data2
                assert "project2" in data2
                assert "project2" not in data1
                
                # Verify different directories
                assert config1.temp_dir != config2.temp_dir
                assert config1.test_files["projects"] != config2.test_files["projects"]
        
        print("✅ Multiple isolated environments test passed")
    
    @pytest.mark.isolated
    def test_test_file_naming_convention(self):
        """Verify all test files use .test.json/.test.mdc naming"""
        with isolated_test_environment(test_id="naming_test") as config:
            # Check all test files have correct naming
            assert config.test_files["projects"].name == "projects.test.json"
            assert config.test_files["tasks"].name == "tasks.test.json"
            assert config.test_files["auto_rule"].name == "auto_rule.test.mdc"
            assert config.test_files["agents"].name == "agents.test.json"
            assert config.test_files["subtasks"].name == "subtasks.test.json"
            
            # Verify files exist
            for file_key, file_path in config.test_files.items():
                assert file_path.exists(), f"{file_key} file should exist"
                
            print("✅ Test file naming convention verified")
    
    def test_cleanup_only_affects_test_files(self):
        """Verify cleanup only removes .test.json files"""
        import tempfile
        from pathlib import Path
        from test_environment_config import cleanup_test_data_files_only
        
        # Create temporary directory with mixed files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test data files (should be removed)
            test_files = [
                temp_path / "data.test.json",
                temp_path / "config.test.mdc",
                temp_path / "settings.test.yaml"
            ]
            
            # Create production files (should NOT be removed)
            production_files = [
                temp_path / "production.json",
                temp_path / "config.mdc",
                temp_path / "test_code.py",  # This is test CODE, not test DATA
                temp_path / "important_data.json"
            ]
            
            # Write all files
            for file_path in test_files + production_files:
                file_path.write_text("test content")
            
            # Run cleanup
            cleaned_count = cleanup_test_data_files_only(temp_path)
            
            # Verify only test data files were removed
            for file_path in test_files:
                assert not file_path.exists(), f"Test data file {file_path} should be removed"
            
            for file_path in production_files:
                assert file_path.exists(), f"Production file {file_path} should be preserved"
            
            assert cleaned_count == len(test_files)
            
        print("✅ Cleanup selectivity verified")


# Run tests if executed directly
if __name__ == "__main__":
    test_instance = TestConsolidatedMCPToolsIsolated()
    
    print("🧪 Running isolated MCP tools tests...")
    
    test_instance.test_production_data_safety_verification()
    test_instance.test_isolated_project_creation()
    test_instance.test_multiple_isolated_environments()
    test_instance.test_test_file_naming_convention()
    test_instance.test_cleanup_only_affects_test_files()
    
    print("🎉 All tests passed!") 