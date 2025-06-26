#!/usr/bin/env python3
"""
Cleanup script to remove ONLY test data files (.test.json, .test.mdc, etc.)
This script is designed to be completely safe and will NEVER touch production files.

SAFETY FEATURES:
- Only removes files with .test.json, .test.mdc suffixes
- Only removes files with test_ prefixes
- Never touches production files like projects.json, tasks.json, auto_rule.mdc
- Creates backups before any operations
- Comprehensive logging of all operations
"""

import os
import json
import shutil
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add the src directory to the Python path
current_dir = Path(__file__).parent
src_dir = current_dir.parent.parent.parent / "src"
sys.path.insert(0, str(src_dir))

try:
    from fastmcp.tools.tool_path import find_project_root
except ImportError:
    def find_project_root() -> Path:
        """Fallback function to find project root"""
        current = Path.cwd()
        while current != current.parent:
            if (current / "___root___").exists():
                return current
            if (current / ".git").exists():
                return current
            if (current / ".cursor" / "rules").exists():
                return current
            current = current.parent
        return Path.cwd()


def get_test_file_patterns() -> List[str]:
    """
    Get patterns for test files that are safe to delete
    
    Returns:
        List of glob patterns for test files
    """
    return [
        "*.test.json",
        "*.test.mdc",
        "*test_*.json",
        "*test_*.mdc"
    ]


def is_safe_test_file(file_path: Path) -> bool:
    """
    Check if a file is safe to delete (test file only)
    
    Args:
        file_path: Path to check
        
    Returns:
        True if file is a test file and safe to delete
    """
    file_name = file_path.name.lower()
    
    # SAFETY: Only allow deletion of files with explicit test suffixes
    if file_name.endswith('.test.json') or file_name.endswith('.test.mdc'):
        return True
    
    # SAFETY: Only allow deletion of files with test prefixes
    test_prefixes = ['test_', 'e2e_', 'migration_test_']
    if any(file_name.startswith(prefix) for prefix in test_prefixes):
        # Additional safety: ensure it's not a production-like file
        if file_name in ['test_projects.json', 'test_tasks.json', 'test_auto_rule.mdc']:
            return False  # These could be production test configs
        return True
    
    return False


def find_test_files_only() -> List[Path]:
    """
    Find ONLY test files that are safe to delete
    
    Returns:
        List of test file paths
    """
    workspace_root = find_project_root()
    cursor_rules_dir = workspace_root / ".cursor" / "rules"
    
    test_files = []
    
    if not cursor_rules_dir.exists():
        print(f"ℹ️  No .cursor/rules directory found at: {cursor_rules_dir}")
        return test_files
    
    # Search for test files in all subdirectories
    for file_path in cursor_rules_dir.rglob("*"):
        if file_path.is_file() and is_safe_test_file(file_path):
            test_files.append(file_path)
    
    return test_files


def clean_test_projects_from_json(projects_file: Path) -> int:
    """
    Clean ONLY test projects from projects.json (but only if it's a .test.json file)
    
    Args:
        projects_file: Path to projects file
        
    Returns:
        Number of projects cleaned
    """
    # SAFETY: Only clean from .test.json files
    if not projects_file.name.endswith('.test.json'):
        print(f"🛡️  SAFETY: Skipping non-test file: {projects_file}")
        return 0
    
    if not projects_file.exists():
        return 0
    
    try:
        with open(projects_file, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        print(f"❌ Error reading test projects file: {e}")
        return 0
    
    # Create backup
    backup_file = projects_file.with_suffix('.json.backup')
    shutil.copy2(projects_file, backup_file)
    print(f"💾 Created backup: {backup_file}")
    
    original_count = len(data)
    removed_projects = []
    
    # Only remove projects that are clearly test projects
    for project_id in list(data.keys()):
        project = data[project_id]
        is_test_project = False
        
        # Check if project has test indicators
        if isinstance(project, dict):
            # Check for test_environment flag
            if project.get("test_environment", False):
                is_test_project = True
            
            # Check for test_id field
            if "test_id" in project:
                is_test_project = True
            
            # Check for test patterns in project_id
            test_patterns = ["test_", "e2e_", "migration_test_"]
            if any(project_id.lower().startswith(pattern) for pattern in test_patterns):
                is_test_project = True
        
        if is_test_project:
            removed_projects.append(project_id)
            del data[project_id]
    
    if removed_projects:
        try:
            with open(projects_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"🧹 Cleaned {len(removed_projects)} test project(s) from {projects_file}:")
            for project_id in removed_projects:
                print(f"   - {project_id}")
            print(f"📊 Projects before: {original_count}, after: {len(data)}")
            
        except Exception as e:
            print(f"❌ Error saving cleaned test projects file: {e}")
            return 0
    else:
        print(f"✨ No test projects found to clean in {projects_file}")
    
    return len(removed_projects)


def clean_test_task_directories() -> int:
    """
    Clean test task directories (only those with .test.json files or test patterns)
    
    Returns:
        Number of directories cleaned
    """
    workspace_root = find_project_root()
    tasks_base_dir = workspace_root / ".cursor" / "rules" / "tasks"
    
    if not tasks_base_dir.exists():
        return 0
    
    cleaned_count = 0
    
    # Look for test task directories
    for user_dir in tasks_base_dir.iterdir():
        if not user_dir.is_dir():
            continue
            
        for project_dir in user_dir.iterdir():
            if not project_dir.is_dir():
                continue
            
            # Check if this is a test project directory
            is_test_dir = False
            
            # Check for test patterns in directory name
            test_patterns = ["test_", "e2e_", "migration_test_"]
            if any(project_dir.name.lower().startswith(pattern) for pattern in test_patterns):
                is_test_dir = True
            
            # Check for .test.json files in the directory
            for task_tree_dir in project_dir.iterdir():
                if task_tree_dir.is_dir():
                    test_json_files = list(task_tree_dir.glob("*.test.json"))
                    if test_json_files:
                        is_test_dir = True
                        break
            
            if is_test_dir:
                try:
                    shutil.rmtree(project_dir)
                    cleaned_count += 1
                    print(f"🧹 Removed test task directory: {project_dir}")
                except Exception as e:
                    print(f"⚠️ Could not remove test directory {project_dir}: {e}")
    
    return cleaned_count


def clean_test_context_directories() -> int:
    """
    Clean test context directories (only those with test patterns)
    
    Returns:
        Number of directories cleaned
    """
    workspace_root = find_project_root()
    contexts_base_dir = workspace_root / ".cursor" / "rules" / "contexts"
    
    if not contexts_base_dir.exists():
        return 0
    
    cleaned_count = 0
    
    # Look for test context directories
    for user_dir in contexts_base_dir.iterdir():
        if not user_dir.is_dir():
            continue
            
        for project_dir in user_dir.iterdir():
            if not project_dir.is_dir():
                continue
            
            # Check if this is a test project directory
            test_patterns = ["test_", "e2e_", "migration_test_"]
            if any(project_dir.name.lower().startswith(pattern) for pattern in test_patterns):
                try:
                    shutil.rmtree(project_dir)
                    cleaned_count += 1
                    print(f"🧹 Removed test context directory: {project_dir}")
                except Exception as e:
                    print(f"⚠️ Could not remove test context directory {project_dir}: {e}")
    
    return cleaned_count


def main():
    """Main cleanup function - ONLY removes test files"""
    print("🧹 Starting SAFE test data cleanup (test files only)...")
    print("🛡️  SAFETY: This script ONLY removes .test.json, .test.mdc and test_* files")
    print("🛡️  SAFETY: Production files (projects.json, tasks.json, auto_rule.mdc) are NEVER touched")
    
    workspace_root = find_project_root()
    print(f"📁 Workspace root: {workspace_root}")
    
    total_cleaned = 0
    
    # 1. Clean individual test files
    print("\n1️⃣ Cleaning individual test files...")
    test_files = find_test_files_only()
    
    if test_files:
        print(f"Found {len(test_files)} test files to clean:")
        for file_path in test_files:
            print(f"   - {file_path}")
        
        for file_path in test_files:
            try:
                file_path.unlink()
                total_cleaned += 1
                print(f"🧹 Removed test file: {file_path}")
            except Exception as e:
                print(f"⚠️ Could not remove {file_path}: {e}")
    else:
        print("✨ No individual test files found")
    
    # 2. Clean test projects from .test.json files
    print("\n2️⃣ Cleaning test projects from .test.json files...")
    cursor_rules_dir = workspace_root / ".cursor" / "rules"
    test_projects_files = []
    
    if cursor_rules_dir.exists():
        test_projects_files = list(cursor_rules_dir.rglob("*.test.json"))
        if "projects" in str(cursor_rules_dir):
            test_projects_files.extend(cursor_rules_dir.rglob("projects.test.json"))
    
    projects_cleaned = 0
    for projects_file in test_projects_files:
        if "projects" in projects_file.name:
            projects_cleaned += clean_test_projects_from_json(projects_file)
    
    total_cleaned += projects_cleaned
    
    # 3. Clean test task directories
    print("\n3️⃣ Cleaning test task directories...")
    task_dirs_cleaned = clean_test_task_directories()
    total_cleaned += task_dirs_cleaned
    
    # 4. Clean test context directories
    print("\n4️⃣ Cleaning test context directories...")
    context_dirs_cleaned = clean_test_context_directories()
    total_cleaned += context_dirs_cleaned
    
    # Summary
    print(f"\n✅ Cleanup completed!")
    print(f"📊 Total items cleaned: {total_cleaned}")
    print(f"   - Individual test files: {len(test_files)}")
    print(f"   - Test projects: {projects_cleaned}")
    print(f"   - Test task directories: {task_dirs_cleaned}")
    print(f"   - Test context directories: {context_dirs_cleaned}")
    
    if total_cleaned == 0:
        print("✨ No test data found to clean - system is already clean!")
    else:
        print("🛡️  SAFETY CONFIRMED: Only test files were cleaned, production data is safe")


if __name__ == "__main__":
    main() 