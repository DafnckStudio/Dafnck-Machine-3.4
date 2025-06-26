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
    
    # Define CLEAR test project patterns - only obvious test projects
    obvious_test_patterns = [
        # Basic test patterns - clearly test projects
        "test_project",
        "test_project2", 
        "test_project3",
        "test1",
        "test2",
        "test_isolated",
        "test_isolated_mcp",
        "isolation_test",
        "proj1",  # Generic test project names
        "proj2",
        "project1",  # Generic test project names  
        "project2",
        "default_project",  # Default test project
        "workflow_proj",  # Test workflow project
        
        # Auto-detection test patterns
        "test_auto_detect",
        "test_from_tmp",
        
        # E2E test patterns (exact matches)
        "e2e_project_1",
        "e2e_lifecycle_project",
        
        # Migration test patterns
        "migration_test_project",
        "migration_workflow_test",
    ]
    
    # Regex patterns for dynamic test projects (with timestamps)
    test_project_regex_patterns = [
        r"^e2e_querying_project_\d+$",
        r"^e2e_collaboration_project_\d+$", 
        r"^e2e_dependency_project_\d+$",
        r"^test_.*_\d+$",  # test_something_123456
        r"^temp_.*$",      # temp_anything
    ]
    
    # Track what we're removing
    removed_projects = []
    original_count = len(data)
    
    # Remove test projects
    for project_id in list(data.keys()):
        project = data[project_id]
        
        # Check if this looks like a test project
        is_test_project = False
        
        # 1. Check by exact ID match with obvious test patterns
        if project_id.lower() in [p.lower() for p in obvious_test_patterns]:
            is_test_project = True
            print(f"🎯 Test project (exact match): {project_id}")
        
        # 2. Check by regex patterns for dynamic test projects
        if not is_test_project:
            for pattern in test_project_regex_patterns:
                if re.match(pattern, project_id, re.IGNORECASE):
                    is_test_project = True
                    print(f"🎯 Test project (regex match): {project_id}")
                    break
        
        # 3. Check for obvious test project names (very specific)
        if not is_test_project and isinstance(project, dict) and "name" in project:
            project_name = project["name"].lower()
            # Only flag if name explicitly says it's for testing
            obvious_test_names = [
                "test project",
                "e2e test project", 
                "migration test project",
                "isolated test",
                "temp project",
                "testing project"
            ]
            if any(test_name in project_name for test_name in obvious_test_names):
                is_test_project = True
                print(f"🎯 Test project (test name): {project_id}")
        
        # 4. Check for test-specific paths (temp directories)
        if not is_test_project and isinstance(project, dict) and "path" in project:
            project_path = project["path"].lower()
            if "/tmp/" in project_path or "/temp/" in project_path:
                is_test_project = True
                print(f"🎯 Test project (temp path): {project_id}")
        
        # 5. Check for explicit test descriptions
        if not is_test_project and isinstance(project, dict) and "description" in project:
            description = project["description"].lower()
            # Only flag if description explicitly mentions it's for testing
            test_phrases = [
                "for testing",
                "test project", 
                "e2e testing",
                "migration testing",
                "temporary project",
                "testing purposes"
            ]
            if any(phrase in description for phrase in test_phrases):
                is_test_project = True
                print(f"🎯 Test project (test description): {project_id}")
        
        # PROTECTION: If project has a meaningful name that doesn't look like a test,
        # and has a real description, protect it even if other criteria match
        if is_test_project and isinstance(project, dict):
            project_name = project.get("name", "").lower()
            project_desc = project.get("description", "").lower()
            
            # Signs of a legitimate project
            has_meaningful_name = (
                len(project_name) > 10 and  # Longer than simple test names
                not any(word in project_name for word in ["test", "temp", "proj"]) and
                any(word in project_name for word in ["framework", "server", "application", "system", "platform"])
            )
            
            has_meaningful_description = (
                len(project_desc) > 50 and  # Substantial description
                not any(phrase in project_desc for phrase in ["for testing", "test project"]) and
                any(word in project_desc for word in ["comprehensive", "framework", "production", "development"])
            )
            
            if has_meaningful_name or has_meaningful_description:
                is_test_project = False
                print(f"🛡️  Protecting project with meaningful content: {project_id}")
        
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

    # Also clean up legacy tasks.json file if it exists and contains test data
    legacy_tasks_file = tasks_dir / "tasks.json"
    if legacy_tasks_file.exists():
        try:
            with open(legacy_tasks_file, 'r') as f:
                legacy_data = json.load(f)
            
            # Check if this contains test data (tasks with project_id: null or test patterns)
            if "tasks" in legacy_data:
                has_test_data = False
                for task in legacy_data["tasks"]:
                    # Check for null project_id (legacy test data)
                    if task.get("project_id") is None:
                        has_test_data = True
                        break
                    # Check for test patterns in title/description
                    title = task.get("title", "").lower()
                    description = task.get("description", "").lower()
                    if any(pattern in title or pattern in description for pattern in [
                        "test", "auto rule integration", "persistence test"
                    ]):
                        has_test_data = True
                        break
                
                if has_test_data:
                    # Create backup before removing
                    backup_file = legacy_tasks_file.with_suffix('.json.backup')
                    shutil.copy2(legacy_tasks_file, backup_file)
                    
                    # Remove the legacy file
                    legacy_tasks_file.unlink()
                    print(f"🗑️  Removed legacy test tasks.json file")
                    print(f"💾 Backup created: {backup_file}")
                else:
                    print("ℹ️  Legacy tasks.json contains production data, keeping it")
            else:
                print("ℹ️  Legacy tasks.json has no tasks, keeping it")
                
        except (json.JSONDecodeError, Exception) as e:
            print(f"⚠️  Could not process legacy tasks.json: {e}")
    else:
        print("ℹ️  No legacy tasks.json file found")


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