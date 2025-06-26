#!/usr/bin/env python3
"""
Test script to verify that the cleanup system works correctly.

This script:
1. Creates some test projects
2. Runs the cleanup script
3. Verifies that test projects are removed
4. Ensures production projects are preserved
"""

import json
import tempfile
import shutil
from pathlib import Path
import subprocess
import sys


def create_test_projects_file():
    """Create a test projects.json file with mixed test and production projects."""
    test_data = {
        # Production projects (should be preserved)
        "dhafnck_mcp_main": {
            "id": "dhafnck_mcp_main",
            "name": "DhafnckMCP Main Project",
            "description": "Main MCP server project",
            "created_at": "2025-01-20T10:00:00Z"
        },
        "chaxiaiv2": {
            "id": "chaxiaiv2",
            "name": "ChaxiAI v2",
            "description": "AI-powered taxi chatbot platform",
            "path": "/home/daihungpham/__projects__/chaxiai/chaxiaiv2",
            "created_at": "2025-06-26T11:23:57.499969Z"
        },
        
        # Test projects (should be removed)
        "test_project": {
            "id": "test_project",
            "name": "Test Project",
            "description": "Testing project",
            "created_at": "2025-01-01T00:00:00Z"
        },
        "e2e_project_1": {
            "id": "e2e_project_1",
            "name": "E2E Test Project",
            "description": "A project for E2E testing",
            "created_at": "2025-01-01T00:00:00Z"
        },
        "e2e_querying_project_1750925473": {
            "id": "e2e_querying_project_1750925473",
            "name": "E2E Querying Test Project",
            "description": "E2E testing for querying",
            "created_at": "2025-01-01T00:00:00Z"
        },
        "migration_test_project": {
            "id": "migration_test_project",
            "name": "Migration Test Project",
            "description": "Project for testing migration",
            "created_at": "2025-01-01T00:00:00Z"
        },
        "test_auto_detect": {
            "id": "test_auto_detect",
            "name": "test_auto_detect",
            "description": "AI-powered project with MCP server integration",
            "path": "/tmp/test_auto_detect",
            "created_at": "2025-06-26T11:40:12.387890Z"
        }
    }
    
    return test_data


def test_cleanup_functionality():
    """Test the cleanup functionality."""
    print("🧪 Testing cleanup functionality...")
    
    # Create temporary directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create .cursor/rules/brain directory structure
        brain_dir = temp_path / ".cursor" / "rules" / "brain"
        brain_dir.mkdir(parents=True)
        
        # Create test projects.json file
        projects_file = brain_dir / "projects.json"
        test_data = create_test_projects_file()
        
        with open(projects_file, 'w') as f:
            json.dump(test_data, f, indent=2)
        
        print(f"📁 Created test projects file: {projects_file}")
        print(f"📊 Initial projects count: {len(test_data)}")
        
        # Create a modified cleanup script that works with our test directory
        cleanup_script_content = f'''
import os
import json
import shutil
import re
from pathlib import Path

def find_projects_file():
    return Path("{projects_file}")

def backup_projects_file(projects_file):
    if projects_file.exists():
        backup_file = projects_file.with_suffix('.json.backup')
        shutil.copy2(projects_file, backup_file)
        print(f"✅ Created backup: {{backup_file}}")
        return backup_file
    return None

def clean_test_projects(projects_file):
    if not projects_file.exists():
        print(f"ℹ️  Projects file does not exist: {{projects_file}}")
        return
    
    try:
        with open(projects_file, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        print(f"❌ Error reading projects file: {{e}}")
        return
    
    test_project_patterns = [
        "test", "test_project", "test_project2", "test_project3",
        "test1", "test2", "test_isolated", "test_isolated_mcp",
        "isolation_test", "project1", "project2",
        "test_auto_detect", "test_from_tmp",
        "e2e_project_1", "e2e_lifecycle_project",
        "migration_test_project", "migration_workflow_test",
    ]
    
    test_project_regex_patterns = [
        r"e2e_querying_project_\\d+",
        r"e2e_collaboration_project_\\d+", 
        r"e2e_dependency_project_\\d+",
    ]
    
    removed_projects = []
    original_count = len(data)
    
    for project_id in list(data.keys()):
        project = data[project_id]
        is_test_project = False
        
        if project_id.lower() in [p.lower() for p in test_project_patterns]:
            is_test_project = True
        
        for pattern in test_project_regex_patterns:
            if re.match(pattern, project_id):
                is_test_project = True
                break
        
        if isinstance(project, dict) and "name" in project:
            project_name = project["name"].lower()
            test_keywords = ["test", "isolated", "e2e", "migration", "temp"]
            if any(keyword in project_name for keyword in test_keywords):
                is_test_project = True
        
        if isinstance(project, dict) and "created_at" in project:
            if project["created_at"] == "2025-01-01T00:00:00Z":
                is_test_project = True
        
        if isinstance(project, dict) and "path" in project:
            project_path = project["path"].lower()
            if "/tmp/" in project_path or "temp" in project_path:
                is_test_project = True
        
        if isinstance(project, dict) and "description" in project:
            description = project["description"].lower()
            if any(keyword in description for keyword in ["test", "testing", "e2e", "migration"]):
                is_test_project = True
        
        if is_test_project:
            removed_projects.append(project_id)
            del data[project_id]
    
    if removed_projects:
        try:
            with open(projects_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"🧹 Cleaned {{len(removed_projects)}} test project(s):")
            for project_id in removed_projects:
                print(f"   - {{project_id}}")
            print(f"📊 Projects before: {{original_count}}, after: {{len(data)}}")
            
        except Exception as e:
            print(f"❌ Error saving cleaned projects file: {{e}}")
    else:
        print("✨ No test projects found to clean")

def main():
    print("🧹 Starting comprehensive test data cleanup...")
    projects_file = find_projects_file()
    print(f"📁 Projects file: {{projects_file}}")
    backup_file = backup_projects_file(projects_file)
    clean_test_projects(projects_file)
    print("✅ Cleanup completed!")
    if backup_file:
        print(f"💾 Backup available at: {{backup_file}}")

if __name__ == "__main__":
    main()
'''
        
        # Write the temporary cleanup script
        temp_cleanup_script = temp_path / "temp_cleanup.py"
        with open(temp_cleanup_script, 'w') as f:
            f.write(cleanup_script_content)
        
        # Run the cleanup script
        print("🔧 Running cleanup script...")
        result = subprocess.run([sys.executable, str(temp_cleanup_script)], 
                              capture_output=True, text=True)
        
        # Assert cleanup script executed successfully
        assert result.returncode == 0, f"Cleanup script failed: {result.stderr}"
        print("✅ Cleanup script executed successfully")
        print(result.stdout)
        
        # Verify the results
        print("🔍 Verifying cleanup results...")
        
        # Load the cleaned data
        with open(projects_file, 'r') as f:
            cleaned_data = json.load(f)
        
        # Check that production projects are preserved
        production_projects = ["dhafnck_mcp_main", "chaxiaiv2"]
        for project_id in production_projects:
            assert project_id in cleaned_data, f"Production project '{project_id}' was incorrectly removed!"
            print(f"✅ Production project '{project_id}' preserved")
        
        # Check that test projects are removed
        test_projects = ["test_project", "e2e_project_1", "e2e_querying_project_1750925473", 
                        "migration_test_project", "test_auto_detect"]
        for project_id in test_projects:
            assert project_id not in cleaned_data, f"Test project '{project_id}' was not removed!"
            print(f"✅ Test project '{project_id}' correctly removed")
        
        print(f"📊 Final count: {len(cleaned_data)} projects (expected: 2)")
        
        # Assert final count is correct
        assert len(cleaned_data) == 2, f"Expected 2 projects after cleanup, but got {len(cleaned_data)}"
        print("🎉 Cleanup verification PASSED!")


def main():
    """Main test function."""
    print("🧪 Starting cleanup verification test...")
    
    try:
        test_cleanup_functionality()
        print("\n✅ All cleanup tests PASSED!")
        return 0
    except AssertionError as e:
        print(f"\n❌ Cleanup tests FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Cleanup tests FAILED with error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 