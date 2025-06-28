"""Context Repository for JSON-based storage"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import logging

from ...domain.entities.context import TaskContext, ContextSchema
from ....tools.tool_path import find_project_root

logger = logging.getLogger(__name__)


class ContextRepository:
    """Repository for managing context data in JSON format"""
    
    def __init__(self, context_root_path: Optional[str] = None):
        """Initialize context repository with optional custom root path"""
        if context_root_path:
            self.context_root_path = Path(context_root_path)
        else:
            # Default path: .cursor/rules/contexts/
            project_root = find_project_root()
            self.context_root_path = project_root / ".cursor" / "rules" / "contexts"
        
        # Ensure the context root directory exists
        self.context_root_path.mkdir(parents=True, exist_ok=True)
    
    def _get_context_directory(self, user_id: str, project_id: str, task_tree_id: str = "main") -> Path:
        """Get the directory path for a specific context hierarchy"""
        return self.context_root_path / user_id / project_id / task_tree_id
    
    def _get_context_file_path(self, user_id: str, project_id: str, task_id: str, task_tree_id: str = "main") -> Path:
        """Get the file path for a specific context"""
        context_dir = self._get_context_directory(user_id, project_id, task_tree_id)
        return context_dir / f"context_{task_id}.json"
    
    def _get_index_file_path(self, user_id: str, project_id: str, task_tree_id: str = "main") -> Path:
        """Get the index file path for a context hierarchy"""
        context_dir = self._get_context_directory(user_id, project_id, task_tree_id)
        return context_dir / "contexts.json"
    
    def _ensure_directory_exists(self, directory: Path) -> None:
        """Ensure a directory exists"""
        directory.mkdir(parents=True, exist_ok=True)
    
    def _load_index(self, user_id: str, project_id: str, task_tree_id: str = "main") -> Dict[str, Any]:
        """Load the context index file"""
        index_path = self._get_index_file_path(user_id, project_id, task_tree_id)
        
        if not index_path.exists():
            return {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "contexts": {}
            }
        
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"Failed to load context index {index_path}: {e}")
            return {
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "contexts": {}
            }
    
    def _save_index(self, index_data: Dict[str, Any], user_id: str, project_id: str, task_tree_id: str = "main") -> None:
        """Save the context index file"""
        index_path = self._get_index_file_path(user_id, project_id, task_tree_id)
        self._ensure_directory_exists(index_path.parent)
        
        index_data["updated_at"] = datetime.now().isoformat()
        
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            logger.error(f"Failed to save context index {index_path}: {e}")
            raise
    
    def create_context(self, context: TaskContext, user_id: str = "default_id") -> bool:
        """Create a new context"""
        try:
            task_id = context.metadata.task_id
            project_id = context.metadata.project_id
            task_tree_id = context.metadata.task_tree_id
            
            # Check if context already exists
            if self.context_exists(task_id, user_id, project_id, task_tree_id):
                logger.warning(f"Context already exists for task {task_id}")
                return False
            
            # Save context file
            context_path = self._get_context_file_path(user_id, project_id, task_id, task_tree_id)
            self._ensure_directory_exists(context_path.parent)
            
            context_data = context.to_dict()
            
            with open(context_path, 'w', encoding='utf-8') as f:
                json.dump(context_data, f, indent=2, ensure_ascii=False)
            
            # Update index
            index_data = self._load_index(user_id, project_id, task_tree_id)
            index_data["contexts"][task_id] = {
                "title": context.objective.title,
                "status": context.metadata.status,
                "created_at": context.metadata.created_at,
                "updated_at": context.metadata.updated_at,
                "assignees": context.metadata.assignees,
                "file_path": f"context_{task_id}.json"
            }
            self._save_index(index_data, user_id, project_id, task_tree_id)
            
            logger.info(f"Created context for task {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create context for task {task_id}: {e}")
            return False
    
    def get_context(self, task_id: str, user_id: str = "default_id", project_id: str = "", task_tree_id: str = "main") -> Optional[TaskContext]:
        """Get a context by task ID"""
        try:
            context_path = self._get_context_file_path(user_id, project_id, task_id, task_tree_id)
            
            if not context_path.exists():
                return None
            
            with open(context_path, 'r', encoding='utf-8') as f:
                context_data = json.load(f)
            
            # Validate context data
            is_valid, errors = ContextSchema.validate_context(context_data)
            if not is_valid:
                logger.warning(f"Invalid context data for task {task_id}: {errors}")
                # Could attempt to fix or migrate here
            
            return TaskContext.from_dict(context_data)
            
        except Exception as e:
            logger.error(f"Failed to get context for task {task_id}: {e}")
            return None
    
    def update_context(self, context: TaskContext, user_id: str = "default_id") -> bool:
        """Update an existing context"""
        try:
            task_id = context.metadata.task_id
            project_id = context.metadata.project_id
            task_tree_id = context.metadata.task_tree_id
            
            # Update timestamp
            context.metadata.updated_at = datetime.now().isoformat()
            
            # Save context file
            context_path = self._get_context_file_path(user_id, project_id, task_id, task_tree_id)
            
            if not context_path.exists():
                logger.warning(f"Context does not exist for task {task_id}")
                return False
            
            context_data = context.to_dict()
            
            with open(context_path, 'w', encoding='utf-8') as f:
                json.dump(context_data, f, indent=2, ensure_ascii=False)
            
            # Update index
            index_data = self._load_index(user_id, project_id, task_tree_id)
            if task_id in index_data["contexts"]:
                index_data["contexts"][task_id].update({
                    "title": context.objective.title,
                    "status": context.metadata.status,
                    "updated_at": context.metadata.updated_at,
                    "assignees": context.metadata.assignees
                })
                self._save_index(index_data, user_id, project_id, task_tree_id)
            
            logger.info(f"Updated context for task {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update context for task {task_id}: {e}")
            return False
    
    def delete_context(self, task_id: str, user_id: str = "default_id", project_id: str = "", task_tree_id: str = "main") -> bool:
        """Delete a context"""
        try:
            context_path = self._get_context_file_path(user_id, project_id, task_id, task_tree_id)
            
            if context_path.exists():
                context_path.unlink()
            
            # Update index
            index_data = self._load_index(user_id, project_id, task_tree_id)
            if task_id in index_data["contexts"]:
                del index_data["contexts"][task_id]
                self._save_index(index_data, user_id, project_id, task_tree_id)
            
            logger.info(f"Deleted context for task {task_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete context for task {task_id}: {e}")
            return False
    
    def context_exists(self, task_id: str, user_id: str = "default_id", project_id: str = "", task_tree_id: str = "main") -> bool:
        """Check if a context exists"""
        context_path = self._get_context_file_path(user_id, project_id, task_id, task_tree_id)
        return context_path.exists()
    
    def list_contexts(self, user_id: str = "default_id", project_id: str = "", task_tree_id: str = "main") -> Dict[str, Any]:
        """List all contexts in a project/tree"""
        try:
            index_data = self._load_index(user_id, project_id, task_tree_id)
            return index_data
        except Exception as e:
            logger.error(f"Failed to list contexts: {e}")
            return {"contexts": {}}
    
    def get_property(self, task_id: str, property_path: str, user_id: str = "default_id", project_id: str = "", task_tree_id: str = "main") -> Any:
        """Get a specific property from a context using dot notation"""
        context = self.get_context(task_id, user_id, project_id, task_tree_id)
        if not context:
            return None
        
        try:
            # Convert to dict for easier property access
            context_dict = context.to_dict()
            
            # Split property path and navigate
            path_parts = property_path.split('.')
            current = context_dict
            
            for part in path_parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                elif isinstance(current, list) and part.isdigit():
                    index = int(part)
                    if 0 <= index < len(current):
                        current = current[index]
                    else:
                        return None
                else:
                    return None
            
            return current
            
        except Exception as e:
            logger.error(f"Failed to get property {property_path} for task {task_id}: {e}")
            return None
    
    def update_property(self, task_id: str, property_path: str, value: Any, user_id: str = "default_id", project_id: str = "", task_tree_id: str = "main") -> bool:
        """Update a specific property in a context using dot notation"""
        context = self.get_context(task_id, user_id, project_id, task_tree_id)
        if not context:
            return False
        
        try:
            # Convert to dict for easier manipulation
            context_dict = context.to_dict()
            
            # Split property path and navigate to parent
            path_parts = property_path.split('.')
            current = context_dict
            
            # Navigate to the parent of the target property
            for part in path_parts[:-1]:
                if isinstance(current, dict):
                    if part not in current:
                        current[part] = {}
                    current = current[part]
                elif isinstance(current, list) and part.isdigit():
                    index = int(part)
                    if 0 <= index < len(current):
                        current = current[index]
                    else:
                        return False
                else:
                    return False
            
            # Set the final property
            final_key = path_parts[-1]
            if isinstance(current, dict):
                current[final_key] = value
            elif isinstance(current, list) and final_key.isdigit():
                index = int(final_key)
                if 0 <= index < len(current):
                    current[index] = value
                else:
                    return False
            else:
                return False
            
            # Recreate context from updated dict and save
            updated_context = TaskContext.from_dict(context_dict)
            return self.update_context(updated_context, user_id)
            
        except Exception as e:
            logger.error(f"Failed to update property {property_path} for task {task_id}: {e}")
            return False
    
    def merge_context_data(self, task_id: str, data: Dict[str, Any], user_id: str = "default_id", project_id: str = "", task_tree_id: str = "main") -> bool:
        """Merge data into an existing context"""
        context = self.get_context(task_id, user_id, project_id, task_tree_id)
        if not context:
            return False
        
        try:
            # Convert to dict, merge, and convert back
            context_dict = context.to_dict()
            
            def deep_merge(target: Dict, source: Dict):
                """Deep merge two dictionaries"""
                for key, value in source.items():
                    if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                        deep_merge(target[key], value)
                    else:
                        target[key] = value
            
            deep_merge(context_dict, data)
            
            # Recreate context from merged dict and save
            updated_context = TaskContext.from_dict(context_dict)
            return self.update_context(updated_context, user_id)
            
        except Exception as e:
            logger.error(f"Failed to merge data for task {task_id}: {e}")
            return False 