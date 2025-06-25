#!/usr/bin/env python3
"""
Task Management Migration Script
Migrates from flat task storage to hierarchical user/project/task_tree structure

Usage:
    python migration_script.py [--dry-run] [--user-id USER_ID]
"""

import json
import os
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

def get_project_root() -> Path:
    """Find project root directory"""
    current = Path.cwd()
    while current != current.parent:
        if (current / ".cursor").exists() or (current / "dhafnck_mcp_main").exists():
            return current
        current = current.parent
    return Path.cwd()

class TaskMigrationManager:
    """Manages migration from flat to hierarchical task storage"""
    
    def __init__(self, user_id: str = "default_id", dry_run: bool = False):
        self.user_id = user_id
        self.dry_run = dry_run
        self.project_root = get_project_root()
        
        # Paths
        self.legacy_tasks_file = self.project_root / ".cursor" / "rules" / "tasks" / "tasks.json"
        self.projects_file = self.project_root / ".cursor" / "rules" / "brain" / "projects.json"
        self.new_tasks_base = self.project_root / ".cursor" / "rules" / "tasks" / user_id
        self.backup_dir = self.project_root / ".cursor" / "rules" / "tasks" / "backup"
        
        # Migration results
        self.migration_results = {
            "total_tasks": 0,
            "migrated_tasks": 0,
            "tasks_by_project": {},
            "errors": [],
            "created_directories": [],
            "dry_run": dry_run
        }
    
    def load_legacy_tasks(self) -> List[Dict[str, Any]]:
        """Load tasks from legacy flat file"""
        if not self.legacy_tasks_file.exists():
            print(f"Legacy tasks file not found: {self.legacy_tasks_file}")
            return []
        
        try:
            with open(self.legacy_tasks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                return data.get("tasks", [])
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading legacy tasks: {e}")
            return []
    
    def load_projects(self) -> Dict[str, Any]:
        """Load project configuration"""
        if not self.projects_file.exists():
            print(f"Projects file not found: {self.projects_file}")
            return {}
        
        try:
            with open(self.projects_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError) as e:
            print(f"Error loading projects: {e}")
            return {}
    
    def create_backup(self) -> str:
        """Create timestamped backup of current state"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"migration_backup_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        if not self.dry_run:
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Backup legacy tasks file
            if self.legacy_tasks_file.exists():
                shutil.copy2(self.legacy_tasks_file, backup_path / "tasks.json")
            
            # Backup projects file
            if self.projects_file.exists():
                shutil.copy2(self.projects_file, backup_path / "projects.json")
        
        print(f"{'[DRY RUN] ' if self.dry_run else ''}Created backup: {backup_path}")
        return str(backup_path)
    
    def ensure_project_tree_structure(self, project_id: str, task_tree_id: str) -> Path:
        """Ensure directory structure exists for project/tree"""
        target_dir = self.new_tasks_base / project_id / task_tree_id
        tasks_file = target_dir / "tasks.json"
        
        if not self.dry_run:
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Create empty tasks.json if it doesn't exist
            if not tasks_file.exists():
                with open(tasks_file, 'w', encoding='utf-8') as f:
                    json.dump({"tasks": []}, f, indent=2)
        
        self.migration_results["created_directories"].append(str(target_dir))
        return tasks_file
    
    def migrate_task_to_project_tree(self, task: Dict[str, Any], project_id: str, task_tree_id: str):
        """Migrate a single task to specific project/tree"""
        tasks_file = self.ensure_project_tree_structure(project_id, task_tree_id)
        
        if not self.dry_run:
            # Load existing tasks in target location
            existing_tasks = []
            if tasks_file.exists():
                try:
                    with open(tasks_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        existing_tasks = data.get("tasks", [])
                except (json.JSONDecodeError, FileNotFoundError):
                    existing_tasks = []
            
            # Add task to target location
            existing_tasks.append(task)
            
            # Save updated tasks
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump({"tasks": existing_tasks}, f, indent=2, ensure_ascii=False)
        
        # Update migration results
        project_key = f"{project_id}/{task_tree_id}"
        if project_key not in self.migration_results["tasks_by_project"]:
            self.migration_results["tasks_by_project"][project_key] = 0
        self.migration_results["tasks_by_project"][project_key] += 1
        self.migration_results["migrated_tasks"] += 1
    
    def determine_task_destination(self, task: Dict[str, Any], projects: Dict[str, Any]) -> tuple[str, str]:
        """
        Determine destination project_id and task_tree_id for a task
        
        Returns:
            Tuple of (project_id, task_tree_id)
        """
        # Check if task has explicit project_id
        task_project_id = task.get("project_id")
        
        if task_project_id and task_project_id in projects:
            # Task has valid project_id - use it
            project_id = task_project_id
            
            # For now, always use "main" task tree
            # TODO: In future, could examine task properties to determine tree
            task_tree_id = "main"
            
            return project_id, task_tree_id
        else:
            # Task has no project_id or invalid project_id - assign to default
            return "default", "main"
    
    def create_default_project(self, projects: Dict[str, Any]) -> Dict[str, Any]:
        """Create default project for unassigned tasks"""
        if "default" not in projects:
            default_project = {
                "id": "default",
                "name": "Default Project",
                "description": "Default project for migrated tasks without explicit project assignment",
                "task_trees": {
                    "main": {
                        "id": "main", 
                        "name": "Main Tasks",
                        "description": "Main task tree for default project"
                    }
                },
                "registered_agents": {},
                "agent_assignments": {},
                "created_at": datetime.now().isoformat() + "Z"
            }
            projects["default"] = default_project
        
        return projects
    
    def migrate(self) -> Dict[str, Any]:
        """Execute the complete migration process"""
        print(f"{'[DRY RUN] ' if self.dry_run else ''}Starting task migration...")
        print(f"User ID: {self.user_id}")
        print(f"Target structure: .cursor/rules/tasks/{self.user_id}/<project_id>/<task_tree_id>/tasks.json")
        
        # Step 1: Create backup
        backup_path = self.create_backup()
        
        # Step 2: Load data
        legacy_tasks = self.load_legacy_tasks()
        projects = self.load_projects()
        
        self.migration_results["total_tasks"] = len(legacy_tasks)
        print(f"Found {len(legacy_tasks)} tasks to migrate")
        print(f"Found {len(projects)} existing projects")
        
        # Step 3: Create default project if needed
        if legacy_tasks:  # Only create if we have tasks to migrate
            projects = self.create_default_project(projects)
        
        # Step 4: Migrate each task
        for i, task in enumerate(legacy_tasks):
            try:
                task_id = task.get("id", f"unknown_{i}")
                project_id, task_tree_id = self.determine_task_destination(task, projects)
                
                print(f"{'[DRY RUN] ' if self.dry_run else ''}Migrating task {task_id} to {project_id}/{task_tree_id}")
                self.migrate_task_to_project_tree(task, project_id, task_tree_id)
                
            except Exception as e:
                error_msg = f"Failed to migrate task {task.get('id', i)}: {e}"
                print(f"ERROR: {error_msg}")
                self.migration_results["errors"].append(error_msg)
        
        # Step 5: Update projects.json if we created default project
        if "default" in projects and not self.dry_run:
            with open(self.projects_file, 'w', encoding='utf-8') as f:
                json.dump(projects, f, indent=2, ensure_ascii=False)
        
        # Step 6: Archive legacy file (don't delete, just rename)
        if not self.dry_run and self.legacy_tasks_file.exists():
            archive_name = f"tasks_legacy_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            archive_path = self.legacy_tasks_file.parent / archive_name
            shutil.move(self.legacy_tasks_file, archive_path)
            print(f"Archived legacy tasks file to: {archive_path}")
        
        return self.migration_results
    
    def print_migration_summary(self):
        """Print detailed migration summary"""
        results = self.migration_results
        
        print("\n" + "="*60)
        print("MIGRATION SUMMARY")
        print("="*60)
        print(f"Dry Run: {results['dry_run']}")
        print(f"User ID: {self.user_id}")
        print(f"Total tasks: {results['total_tasks']}")
        print(f"Migrated tasks: {results['migrated_tasks']}")
        print(f"Errors: {len(results['errors'])}")
        
        print(f"\nTasks by project/tree:")
        for project_tree, count in results["tasks_by_project"].items():
            print(f"  {project_tree}: {count} tasks")
        
        if results["errors"]:
            print(f"\nErrors:")
            for error in results["errors"]:
                print(f"  - {error}")
        
        print(f"\nCreated directories:")
        for directory in results["created_directories"]:
            print(f"  {directory}")

def main():
    parser = argparse.ArgumentParser(description="Migrate task storage to hierarchical structure")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    parser.add_argument("--user-id", default="default_id", help="User ID for migration (default: default_id)")
    
    args = parser.parse_args()
    
    # Create and run migration
    migration_manager = TaskMigrationManager(user_id=args.user_id, dry_run=args.dry_run)
    migration_manager.migrate()
    migration_manager.print_migration_summary()
    
    if args.dry_run:
        print("\n*** This was a DRY RUN - no changes were made ***")
        print("Run without --dry-run to execute the migration")

if __name__ == "__main__":
    main()