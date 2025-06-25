#!/usr/bin/env python3
"""
Test Script for Project-Specific Task Management
================================================

This script tests that the DhafnckMCP system correctly handles different project locations.
"""

import os
import sys
import tempfile
import json
from pathlib import Path

# Add the source path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_project_specific_paths():
    """Test that PathResolver works with different project locations"""
    
    print("🧪 Testing Project-Specific Path Resolution")
    print("=" * 50)
    
    # Create temporary project directories
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Test Project 1
        project1 = temp_path / "project1"
        project1.mkdir()
        (project1 / ".git").mkdir()  # Make it look like a git repo
        (project1 / ".cursor" / "rules").mkdir(parents=True)
        
        # Test Project 2  
        project2 = temp_path / "project2"
        project2.mkdir()
        (project2 / ".cursor" / "rules").mkdir(parents=True)
        
        print(f"Created test projects:")
        print(f"  Project 1: {project1}")
        print(f"  Project 2: {project2}")
        
        # Test path resolution for each project
        for i, project_path in enumerate([project1, project2], 1):
            print(f"\n🔍 Testing Project {i}: {project_path}")
            
            # Change to project directory
            original_cwd = os.getcwd()
            os.chdir(project_path)
            
            try:
                # Import PathResolver after changing directory
                from fastmcp.task_management.interface.consolidated_mcp_tools import PathResolver
                
                # Create PathResolver instance
                resolver = PathResolver()
                
                # Test path resolution
                print(f"  ✅ Project root detected: {resolver.project_root}")
                print(f"  ✅ Brain directory: {resolver.brain_dir}")
                print(f"  ✅ Tasks JSON path: {resolver.get_tasks_json_path()}")
                print(f"  ✅ Auto rule path: {resolver.get_auto_rule_path()}")
                
                # Verify paths are project-specific
                assert str(resolver.project_root) == str(project_path), f"Wrong project root: {resolver.project_root}"
                assert str(project_path) in str(resolver.brain_dir), f"Brain dir not in project: {resolver.brain_dir}"
                assert str(project_path) in str(resolver.get_tasks_json_path()), f"Tasks path not in project: {resolver.get_tasks_json_path()}"
                
                print(f"  ✅ All paths correctly resolved for Project {i}")
                
            except Exception as e:
                print(f"  ❌ Error testing Project {i}: {e}")
                return False
            finally:
                os.chdir(original_cwd)
    
    print(f"\n✅ All project-specific path tests passed!")
    return True

def test_environment_variable_override():
    """Test that PROJECT_ROOT_PATH environment variable works"""
    
    print("\n🧪 Testing Environment Variable Override")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        project_path = temp_path / "env_test_project"
        project_path.mkdir()
        
        # Set environment variable
        os.environ['PROJECT_ROOT_PATH'] = str(project_path)
        
        try:
            # Import after setting environment variable
            from fastmcp.tools.tool_path import find_project_root
            
            # Test that environment variable is respected
            detected_root = find_project_root()
            print(f"  Environment variable set to: {project_path}")
            print(f"  Detected project root: {detected_root}")
            
            assert str(detected_root) == str(project_path), f"Environment variable not respected: {detected_root}"
            print(f"  ✅ Environment variable override works correctly")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing environment variable: {e}")
            return False
        finally:
            # Clean up environment variable
            if 'PROJECT_ROOT_PATH' in os.environ:
                del os.environ['PROJECT_ROOT_PATH']

def test_setup_script_integration():
    """Test that the setup script creates the correct structure"""
    
    print("\n🧪 Testing Setup Script Integration")
    print("=" * 50)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        project_path = temp_path / "setup_test_project"
        project_path.mkdir()
        
        print(f"Testing setup script on: {project_path}")
        
        # Import setup functions
        sys.path.insert(0, str(Path(__file__).parent))
        from setup_project_mcp import setup_project_structure, create_tool_config
        
        try:
            # Test structure setup
            success = setup_project_structure(project_path)
            assert success, "Setup script failed"
            
            # Verify structure was created
            expected_files = [
                project_path / ".cursor" / "rules" / "tasks" / "tasks.json",
                project_path / ".cursor" / "rules" / "brain" / "projects.json",
                project_path / ".cursor" / "rules" / "auto_rule.mdc",
                project_path / ".cursor" / "rules" / "main_objectif.mdc"
            ]
            
            for file_path in expected_files:
                assert file_path.exists(), f"Expected file not created: {file_path}"
                print(f"  ✅ Created: {file_path.relative_to(project_path)}")
            
            # Test tool config creation
            success = create_tool_config(project_path)
            assert success, "Tool config creation failed"
            
            tool_config_path = project_path / ".cursor" / "tool_config.json"
            assert tool_config_path.exists(), "Tool config not created"
            
            # Verify tool config content
            with open(tool_config_path) as f:
                config = json.load(f)
                assert "enabled_tools" in config, "Tool config missing enabled_tools"
                assert config["project_root"] == str(project_path), "Tool config has wrong project root"
            
            print(f"  ✅ Tool configuration created correctly")
            print(f"  ✅ Setup script integration test passed!")
            
            return True
            
        except Exception as e:
            print(f"  ❌ Error testing setup script: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Run all tests"""
    print("🚀 DhafnckMCP Project-Specific System Tests")
    print("=" * 60)
    
    tests = [
        test_project_specific_paths,
        test_environment_variable_override,
        test_setup_script_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"🏁 Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✅ All tests passed! Project-specific system is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 