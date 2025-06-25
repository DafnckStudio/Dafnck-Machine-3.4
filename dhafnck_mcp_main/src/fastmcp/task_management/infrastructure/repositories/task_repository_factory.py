"""Task Repository Factory for Hierarchical Storage with User Support"""

from typing import Optional
from pathlib import Path
import os

from ...domain.repositories.task_repository import TaskRepository
from .json_task_repository import JsonTaskRepository, InMemoryTaskRepository
from fastmcp.tools.tool_path import find_project_root


class TaskRepositoryFactory:
    """Factory for creating task repositories with hierarchical user/project/tree structure"""
    
    def __init__(self, base_path: Optional[str] = None, default_user_id: str = "default_id"):
        """
        Initialize repository factory
        
        Args:
            base_path: Base path for task storage (defaults to project root)
            default_user_id: Default user ID for single-user mode
        """
        self.project_root = find_project_root()
        self.base_path = base_path or str(self.project_root / ".cursor" / "rules" / "tasks")
        self.default_user_id = default_user_id
    
    def create_repository(self, project_id: str, task_tree_id: str = "main", user_id: Optional[str] = None) -> TaskRepository:
        """
        Create a task repository for specific user/project/task tree
        
        Args:
            project_id: Project identifier (REQUIRED)
            task_tree_id: Task tree identifier (defaults to "main")
            user_id: User identifier (defaults to default_user_id)
            
        Returns:
            TaskRepository instance scoped to user/project/tree
        """
        if not project_id:
            raise ValueError("project_id is required")
        
        if not task_tree_id:
            task_tree_id = "main"
            
        if not user_id:
            user_id = self.default_user_id
        
        # Create hierarchical path: .cursor/rules/tasks/{user_id}/{project_id}/{task_tree_id}/tasks.json
        file_path = Path(self.base_path) / user_id / project_id / task_tree_id / "tasks.json"
        
        # Ensure directory structure exists
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        return JsonTaskRepository(
            file_path=str(file_path), 
            project_id=project_id, 
            task_tree_id=task_tree_id,
            user_id=user_id
        )
    
    def create_memory_repository(self) -> TaskRepository:
        """Create in-memory repository for testing"""
        return InMemoryTaskRepository()
    
    def get_all_user_repositories(self, user_id: Optional[str] = None) -> dict[str, dict[str, TaskRepository]]:
        """
        Get repositories for all projects and task trees for a specific user
        
        Args:
            user_id: User identifier (defaults to default_user_id)
            
        Returns:
            Dict structure: {project_id: {task_tree_id: repository}}
        """
        if not user_id:
            user_id = self.default_user_id
            
        repositories = {}
        
        user_path = Path(self.base_path) / user_id
        if not user_path.exists():
            return repositories
        
        # Scan for existing project directories under user
        for project_dir in user_path.iterdir():
            if project_dir.is_dir():
                project_id = project_dir.name
                repositories[project_id] = {}
                
                # Scan for task tree directories within project
                for tree_dir in project_dir.iterdir():
                    if tree_dir.is_dir() and (tree_dir / "tasks.json").exists():
                        task_tree_id = tree_dir.name
                        repositories[project_id][task_tree_id] = self.create_repository(
                            project_id, task_tree_id, user_id
                        )
        
        return repositories
    
    def validate_user_project_tree(self, project_id: str, task_tree_id: str, user_id: Optional[str] = None) -> bool:
        """
        Validate if user/project/task tree combination exists
        
        Args:
            project_id: Project identifier
            task_tree_id: Task tree identifier
            user_id: User identifier
            
        Returns:
            True if valid combination exists
        """
        if not user_id:
            user_id = self.default_user_id
            
        file_path = Path(self.base_path) / user_id / project_id / task_tree_id / "tasks.json"
        return file_path.parent.exists()
    
    def create_user_project_structure(self, project_id: str, task_tree_id: str = "main", user_id: Optional[str] = None) -> None:
        """
        Create directory structure for new user/project/tree combination
        
        Args:
            project_id: Project identifier
            task_tree_id: Task tree identifier
            user_id: User identifier
        """
        if not user_id:
            user_id = self.default_user_id
            
        file_path = Path(self.base_path) / user_id / project_id / task_tree_id / "tasks.json"
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create empty tasks.json if it doesn't exist
        if not file_path.exists():
            import json
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump({"tasks": []}, f, indent=2)
    
    def get_task_file_path(self, project_id: str, task_tree_id: str = "main", user_id: Optional[str] = None) -> str:
        """
        Get the full file path for a specific user/project/tree combination
        
        Args:
            project_id: Project identifier
            task_tree_id: Task tree identifier
            user_id: User identifier
            
        Returns:
            Full path to tasks.json file
        """
        if not user_id:
            user_id = self.default_user_id
            
        return str(Path(self.base_path) / user_id / project_id / task_tree_id / "tasks.json")