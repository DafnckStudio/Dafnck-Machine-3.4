#!/usr/bin/env python3
"""
Cleanup script to remove test data from production projects.json file.

This script removes any test projects that may have been created by test runs
that didn't properly isolate their data.
"""

import os
import json
import shutil
import re
from pathlib import Path


def find_projects_file():
    """Find the production projects.json file"""
    # Look for projects.json in the workspace root (.cursor/rules/brain/projects.json)
    # Find the .cursor directory that contains rules/brain/projects.json with test data
    current_dir = Path(__file__).parent
    
    # Walk up the directory tree to find .cursor directories with projects.json
    check_dir = current_dir
    
    # Look for workspace indicators (go up max 10 levels)
    for _ in range(10):
        if (check_dir / ".cursor").exists():
            projects_file = check_dir / ".cursor" / "rules" / "brain" / "projects.json"
            if projects_file.exists():
                # Check if this projects.json has test data by looking for test projects
                try:
                    with open(projects_file, 'r') as f:
                        data = json.load(f)
                    # Look for test project indicators
                    test_indicators = ["test", "proj1", "proj2", "e2e", "migration", "default_project"]
                    has_test_data = any(
                        any(indicator in project_id.lower() for indicator in test_indicators)
                        for project_id in data.keys()
                    )
                    if has_test_data:
                        return projects_file
                except (json.JSONDecodeError, Exception):
                    pass
        
        parent = check_dir.parent
        if parent == check_dir:  # reached filesystem root
            break
        check_dir = parent
    
    # Fallback: use the agentic-project workspace
    fallback_root = Path("/home/daihungpham/agentic-project")
    projects_file = fallback_root / ".cursor" / "rules" / "brain" / "projects.json"
    return projects_file


def backup_projects_file(projects_file):
    """Create a backup of the projects file before cleaning"""
    if projects_file.exists():
        backup_file = projects_file.with_suffix('.json.backup')
        shutil.copy2(projects_file, backup_file)
        print(f"✅ Created backup: {backup_file}")
        return backup_file
    return None


def clean_test_projects(projects_file):
    """Remove test projects from the production file"""
    if not projects_file.exists():
        print(f"ℹ️  Projects file does not exist: {projects_file}")
        return
    
    # Load current data
    try:
        with open(projects_file, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        print(f"❌ Error reading projects file: {e}")
        return
    
    # Comprehensive test project patterns based on actual test projects found
    test_project_patterns = [
        # Basic test patterns
        "test",
        "test_project",
        "test_project2", 
        "test_project3",
        "test1",
        "test2",
        "test_isolated",
        "test_isolated_mcp",
        "isolation_test",
        "project1",
        "project2",
        
        # Auto-detection test patterns
        "test_auto_detect",
        "test_from_tmp",
        
        # E2E test patterns (exact matches and patterns)
        "e2e_project_1",
        "e2e_lifecycle_project",
        
        # Migration test patterns
        "migration_test_project",
        "migration_workflow_test",
    ]
    
    # Regex patterns for dynamic test projects (with timestamps)
    test_project_regex_patterns = [
        r"e2e_querying_project_\d+",
        r"e2e_collaboration_project_\d+", 
        r"e2e_dependency_project_\d+",
    ]
    
    # Track what we're removing
    removed_projects = []
    original_count = len(data)
    
    # Remove test projects
    for project_id in list(data.keys()):
        project = data[project_id]
        
        # Check if this looks like a test project
        is_test_project = False
        
        # Check by exact ID match
        if project_id.lower() in [p.lower() for p in test_project_patterns]:
            is_test_project = True
        
        # Check by regex patterns for dynamic test projects
        for pattern in test_project_regex_patterns:
            if re.match(pattern, project_id):
                is_test_project = True
                break
        
        # Check by name containing test keywords
        if isinstance(project, dict) and "name" in project:
            project_name = project["name"].lower()
            test_keywords = ["test", "isolated", "e2e", "migration", "temp"]
            if any(keyword in project_name for keyword in test_keywords):
                is_test_project = True
        
        # Check for test-specific creation dates (like the hardcoded test date)
        if isinstance(project, dict) and "created_at" in project:
            if project["created_at"] == "2025-01-01T00:00:00Z":
                is_test_project = True
        
        # Check for test-specific paths (temp directories)
        if isinstance(project, dict) and "path" in project:
            project_path = project["path"].lower()
            if "/tmp/" in project_path or "temp" in project_path:
                is_test_project = True
        
        # Check for test-specific descriptions
        if isinstance(project, dict) and "description" in project:
            description = project["description"].lower()
            if any(keyword in description for keyword in ["test", "testing", "e2e", "migration"]):
                is_test_project = True
        
        if is_test_project:
            removed_projects.append(project_id)
            del data[project_id]
    
    # Save cleaned data
    if removed_projects:
        try:
            with open(projects_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"🧹 Cleaned {len(removed_projects)} test project(s):")
            for project_id in removed_projects:
                print(f"   - {project_id}")
            print(f"📊 Projects before: {original_count}, after: {len(data)}")
            
        except Exception as e:
            print(f"❌ Error saving cleaned projects file: {e}")
    else:
        print("✨ No test projects found to clean")


def clean_test_task_files():
    """Clean up test task files from .cursor/rules/tasks/ directories"""
    # Find the workspace root that contains test data
    current_dir = Path(__file__).parent
    
    # Walk up the directory tree to find .cursor directories with test data
    workspace_root = None
    check_dir = current_dir
    
    # Look for workspace indicators (go up max 10 levels)
    for _ in range(10):
        if (check_dir / ".cursor").exists():
            projects_file = check_dir / ".cursor" / "rules" / "brain" / "projects.json"
            if projects_file.exists():
                # Check if this projects.json has test data by looking for test projects
                try:
                    with open(projects_file, 'r') as f:
                        data = json.load(f)
                    # Look for test project indicators
                    test_indicators = ["test", "proj1", "proj2", "e2e", "migration", "default_project"]
                    has_test_data = any(
                        any(indicator in project_id.lower() for indicator in test_indicators)
                        for project_id in data.keys()
                    )
                    if has_test_data:
                        workspace_root = check_dir
                        break
                except (json.JSONDecodeError, Exception):
                    pass
        
        parent = check_dir.parent
        if parent == check_dir:  # reached filesystem root
            break
        check_dir = parent
    
    # Fallback: use the agentic-project workspace
    if workspace_root is None:
        workspace_root = Path("/home/daihungpham/agentic-project")
    
    cursor_rules_dir = workspace_root / ".cursor" / "rules"
    tasks_dir = cursor_rules_dir / "tasks"
    
    if not tasks_dir.exists():
        print("ℹ️  No tasks directory found")
        return
    
    # Look for test user directories and test project directories
    removed_dirs = []
    
    for user_dir in tasks_dir.iterdir():
        if not user_dir.is_dir():
            continue
            
        # Check if this is a test user directory
        if user_dir.name == "default_id":  # Default test user
            for project_dir in user_dir.iterdir():
                if not project_dir.is_dir():
                    continue
                
                # Check if this looks like a test project directory
                project_name = project_dir.name
                if any(pattern in project_name.lower() for pattern in [
                    "test", "e2e", "migration", "temp", "proj1", "proj2", "default_project", "workflow"
                ]):
                    try:
                        shutil.rmtree(project_dir)
                        removed_dirs.append(str(project_dir))
                        print(f"🗑️  Removed test task directory: {project_dir}")
                    except Exception as e:
                        print(f"❌ Error removing {project_dir}: {e}")
    
    if removed_dirs:
        print(f"📁 Cleaned {len(removed_dirs)} test task directories")
    else:
        print("✨ No test task directories found to clean")


def clean_test_context_files():
    """Clean up test context files from .cursor/rules/contexts/ directories"""
    # Find the workspace root that contains test data
    current_dir = Path(__file__).parent
    
    # Walk up the directory tree to find .cursor directories with test data
    workspace_root = None
    check_dir = current_dir
    
    # Look for workspace indicators (go up max 10 levels)
    for _ in range(10):
        if (check_dir / ".cursor").exists():
            projects_file = check_dir / ".cursor" / "rules" / "brain" / "projects.json"
            if projects_file.exists():
                # Check if this projects.json has test data by looking for test projects
                try:
                    with open(projects_file, 'r') as f:
                        data = json.load(f)
                    # Look for test project indicators
                    test_indicators = ["test", "proj1", "proj2", "e2e", "migration", "default_project"]
                    has_test_data = any(
                        any(indicator in project_id.lower() for indicator in test_indicators)
                        for project_id in data.keys()
                    )
                    if has_test_data:
                        workspace_root = check_dir
                        break
                except (json.JSONDecodeError, Exception):
                    pass
        
        parent = check_dir.parent
        if parent == check_dir:  # reached filesystem root
            break
        check_dir = parent
    
    # Fallback: use the agentic-project workspace
    if workspace_root is None:
        workspace_root = Path("/home/daihungpham/agentic-project")
    
    cursor_rules_dir = workspace_root / ".cursor" / "rules"
    contexts_dir = cursor_rules_dir / "contexts"
    
    if not contexts_dir.exists():
        print("ℹ️  No contexts directory found")
        return
    
    # Look for test user directories and test project directories
    removed_dirs = []
    
    for user_dir in contexts_dir.iterdir():
        if not user_dir.is_dir():
            continue
            
        # Check if this is a test user directory
        if user_dir.name == "default_id":  # Default test user
            for project_dir in user_dir.iterdir():
                if not project_dir.is_dir():
                    continue
                
                # Check if this looks like a test project directory
                project_name = project_dir.name
                if any(pattern in project_name.lower() for pattern in [
                    "test", "e2e", "migration", "temp", "proj1", "proj2", "default_project", "workflow", "project_a"
                ]):
                    try:
                        shutil.rmtree(project_dir)
                        removed_dirs.append(str(project_dir))
                        print(f"🗑️  Removed test context directory: {project_dir}")
                    except Exception as e:
                        print(f"❌ Error removing {project_dir}: {e}")
    
    if removed_dirs:
        print(f"📁 Cleaned {len(removed_dirs)} test context directories")
    else:
        print("✨ No test context directories found to clean")


def main():
    """Main cleanup function"""
    print("🧹 Starting comprehensive test data cleanup...")
    
    # Find the projects file
    projects_file = find_projects_file()
    print(f"📁 Projects file: {projects_file}")
    
    # Create backup
    backup_file = backup_projects_file(projects_file)
    
    # Clean test projects from projects.json
    clean_test_projects(projects_file)
    
    # Clean test task files
    clean_test_task_files()
    
    # Clean test context files
    clean_test_context_files()
    
    print("✅ Cleanup completed!")
    if backup_file:
        print(f"💾 Backup available at: {backup_file}")


if __name__ == "__main__":
    main() 