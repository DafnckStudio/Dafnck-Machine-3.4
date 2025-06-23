#!/usr/bin/env python3
"""
Cleanup script to remove test data from production projects.json file.

This script removes any test projects that may have been created by test runs
that didn't properly isolate their data.
"""

import os
import json
import shutil
from pathlib import Path


def find_projects_file():
    """Find the production projects.json file"""
    # Start from this script's location and navigate to the projects file
    script_dir = Path(__file__).parent
    projects_file = script_dir.parent / ".cursor" / "rules" / "brain" / "projects.json"
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
    
    # Identify test projects (common test project names/patterns)
    test_project_patterns = [
        "test",
        "test_project",
        "test1",
        "test2",
        "test_isolated",
        "test_isolated_mcp",
        "isolation_test",
        "project1",
        "project2"
    ]
    
    # Track what we're removing
    removed_projects = []
    original_count = len(data)
    
    # Remove test projects
    for project_id in list(data.keys()):
        project = data[project_id]
        
        # Check if this looks like a test project
        is_test_project = False
        
        # Check by ID
        if project_id.lower() in test_project_patterns:
            is_test_project = True
        
        # Check by name
        if isinstance(project, dict) and "name" in project:
            project_name = project["name"].lower()
            if any(pattern in project_name for pattern in ["test", "isolated"]):
                is_test_project = True
        
        # Check for test-specific creation dates (like the hardcoded test date)
        if isinstance(project, dict) and "created_at" in project:
            if project["created_at"] == "2025-01-01T00:00:00Z":
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


def main():
    """Main cleanup function"""
    print("🧹 Starting test data cleanup...")
    
    # Find the projects file
    projects_file = find_projects_file()
    print(f"📁 Projects file: {projects_file}")
    
    # Create backup
    backup_file = backup_projects_file(projects_file)
    
    # Clean test projects
    clean_test_projects(projects_file)
    
    print("✅ Cleanup completed!")
    if backup_file:
        print(f"💾 Backup available at: {backup_file}")


if __name__ == "__main__":
    main() 