"""JSON Task Repository Implementation"""

import json
import os
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import logging

from ...domain import Task, TaskRepository, TaskId, TaskStatus, Priority
from ...domain.exceptions import TaskNotFoundError


def _get_project_root() -> Path:
    """Find the project root directory by locating the 'dhafnck_mcp_main' directory."""
    current_dir = Path(__file__).resolve()
    while current_dir != current_dir.parent:
        if (current_dir / "dhafnck_mcp_main").is_dir():
            return current_dir
        current_dir = current_dir.parent
    
    # Fallback for when script is inside dhafnck_mcp_main
    current_dir = Path(__file__).resolve()
    if 'dhafnck_mcp_main' in current_dir.parts:
        while current_dir.name != "dhafnck_mcp_main":
            current_dir = current_dir.parent
        return current_dir.parent

    raise FileNotFoundError("Could not find the project root containing 'dhafnck_mcp_main' directory.")


class InMemoryTaskRepository(TaskRepository):
    """In-memory implementation of TaskRepository for testing"""
    
    def __init__(self):
        self._tasks: Dict[int, Task] = {}
        self._next_id = 1
    
    def find_by_id(self, task_id: TaskId) -> Optional[Task]:
        """Find task by ID"""
        return self._tasks.get(task_id.value)
    
    def find_all(self) -> List[Task]:
        """Find all tasks"""
        return list(self._tasks.values())
    
    def find_by_criteria(self, criteria: Dict[str, Any], limit: Optional[int] = None) -> List[Task]:
        """Find tasks by criteria"""
        tasks = self.find_all()
        filtered_tasks = []
        
        for task in tasks:
            matches = True
            
            # Check status filter
            if 'status' in criteria:
                expected_status = criteria['status']
                if hasattr(expected_status, 'value'):
                    # TaskStatus object
                    if task.status.value != expected_status.value:
                        matches = False
                else:
                    # String value
                    if task.status.value != expected_status:
                        matches = False
            
            # Check priority filter
            if 'priority' in criteria:
                expected_priority = criteria['priority']
                if hasattr(expected_priority, 'value'):
                    # Priority object
                    if task.priority.value != expected_priority.value:
                        matches = False
                else:
                    # String value
                    if task.priority.value != expected_priority:
                        matches = False
            
            # Check assignee filter (both singular and plural forms)
            if 'assignee' in criteria:
                if criteria['assignee'] not in task.assignees:
                    matches = False
            
            # Check assignees filter (plural form)
            if 'assignees' in criteria:
                required_assignees = criteria['assignees']
                if not any(assignee in task.assignees for assignee in required_assignees):
                    matches = False
            
            # Check labels filter
            if 'labels' in criteria:
                required_labels = criteria['labels']
                if not all(label in task.labels for label in required_labels):
                    matches = False
            
            if matches:
                filtered_tasks.append(task)
                if limit and len(filtered_tasks) >= limit:
                    break
        
        return filtered_tasks
    
    def search(self, query: str, limit: Optional[int] = None) -> List[Task]:
        """Search tasks by query"""
        tasks = self.find_all()
        matching_tasks = []
        query_lower = query.lower()
        
        for task in tasks:
            # Search in title, description, and details
            searchable_text = f"{task.title} {task.description} {task.details}".lower()
            if query_lower in searchable_text:
                matching_tasks.append(task)
                if limit and len(matching_tasks) >= limit:
                    break
        
        return matching_tasks
    
    def save(self, task: Task):
        """Save task"""
        self._tasks[task.id.value] = task
        # Note: _next_id is no longer used since TaskIds are now generated with YYYYMMDDXXX format
    
    def delete(self, task_id: TaskId) -> bool:
        """Delete task"""
        if task_id.value in self._tasks:
            del self._tasks[task_id.value]
            return True
        return False
    
    def get_next_id(self) -> TaskId:
        """Get next available ID"""
        next_id = self._next_id
        self._next_id += 1
        return TaskId.from_int(next_id)
    
    def find_by_status(self, status: TaskStatus) -> List[Task]:
        """Find tasks by status"""
        return [task for task in self._tasks.values() if task.status == status]
    
    def find_by_priority(self, priority: Priority) -> List[Task]:
        """Find tasks by priority"""
        return [task for task in self._tasks.values() if task.priority == priority]
    
    def find_by_assignee(self, assignee: str) -> List[Task]:
        """Find tasks by assignee"""
        return [task for task in self._tasks.values() if assignee in task.assignees]
    
    def find_by_labels(self, labels: List[str]) -> List[Task]:
        """Find tasks by labels"""
        return [task for task in self._tasks.values() if all(label in task.labels for label in labels)]
    
    def exists(self, task_id: TaskId) -> bool:
        """Check if task exists"""
        return task_id.value in self._tasks
    
    def count(self) -> int:
        """Get total number of tasks"""
        return len(self._tasks)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get repository statistics"""
        tasks = list(self._tasks.values())
        status_counts = {}
        priority_counts = {}
        
        for task in tasks:
            status_counts[task.status.value] = status_counts.get(task.status.value, 0) + 1
            priority_counts[task.priority.value] = priority_counts.get(task.priority.value, 0) + 1
        
        return {
            "total_tasks": len(tasks),
            "status_distribution": status_counts,
            "priority_distribution": priority_counts
        }


class JsonTaskRepository(TaskRepository):
    """JSON file-based implementation of TaskRepository"""
    
    def __init__(self, file_path: Optional[str] = None):
        if file_path:
            self._file_path = str(Path(file_path).resolve())
        else:
            # Default path relative to this file
            current_dir = Path(__file__).parent
            # Navigate up from dhafnck_mcp_main/src/fastmcp/task_management/infrastructure/repositories
            # to project root (agentic-project) and then down to .cursor/rules/tasks/tasks.json
            self._file_path = str(current_dir.parent.parent.parent.parent.parent / ".cursor" / "rules" / "tasks" / "tasks.json")

        logging.info(f"JsonTaskRepository using file_path: {self._file_path}")

        if self._file_path == ":memory:":
            raise ValueError(
                "JsonTaskRepository requires a valid file_path. "
                "Use InMemoryTaskRepository for in-memory storage."
            )
        
        self._ensure_file_exists()
        self._backup_path = os.path.join(os.path.dirname(self._file_path), 'backup')
    
    def _ensure_file_exists(self):
        """Ensure the tasks file exists"""
        os.makedirs(os.path.dirname(self._file_path), exist_ok=True)
        if not os.path.exists(self._file_path):
            self._save_data({"tasks": []})
    
    def _create_backup(self):
        """Create a backup of the current tasks file"""
        if os.path.exists(self._file_path):
            os.makedirs(self._backup_path, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self._backup_path, f"tasks_backup_{timestamp}.json")
            
            # Copy current file to backup
            import shutil
            shutil.copy2(self._file_path, backup_file)
            
            # Keep only last 10 backups
            backup_files = sorted([f for f in os.listdir(self._backup_path) if f.startswith("tasks_backup_")])
            if len(backup_files) > 10:
                for old_backup in backup_files[:-10]:
                    os.remove(os.path.join(self._backup_path, old_backup))
    
    def _load_data(self) -> Dict[str, Any]:
        """Load data from JSON file"""
        try:
            with open(self._file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"tasks": []}
    
    def _save_data(self, data: Dict[str, Any]):
        """Save data to JSON file"""
        with open(self._file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _task_dict_to_domain(self, task_dict: Dict[str, Any]) -> Task:
        """Convert a dictionary to a Task domain object"""
        if 'id' not in task_dict:
            raise ValueError("Task dictionary must contain an 'id' field.")
        
        try:
            task_id = TaskId(task_dict["id"])
        except ValueError:
            task_id = TaskId.from_int(int(task_dict["id"]))
        
        status = TaskStatus(task_dict.get("status", "todo"))
        priority = Priority(task_dict.get("priority", "medium"))
        
        created_at_str = task_dict.get("created_at")
        updated_at_str = task_dict.get("updated_at")
        
        created_at = datetime.fromisoformat(created_at_str) if created_at_str else datetime.now()
        updated_at = datetime.fromisoformat(updated_at_str) if updated_at_str else datetime.now()
        
        assignees = task_dict.get("assignees", [])
        if assignees is None:
            assignees = []
        
        labels = task_dict.get("labels", [])
        if labels is None:
            labels = []
        
        dependency_ids = task_dict.get("dependencies", [])
        dependencies = [TaskId(dep_id) for dep_id in dependency_ids]
        
        return Task(
            id=task_id,
            title=task_dict.get("title", ""),
            description=task_dict.get("description", ""),
            project_id=task_dict.get("project_id"),
            status=status,
            priority=priority,
            details=task_dict.get("details", ""),
            estimated_effort=task_dict.get("estimatedEffort", ""),
            assignees=assignees,
            labels=labels,
            dependencies=dependencies,
            subtasks=task_dict.get("subtasks", []),
            due_date=task_dict.get("dueDate"),
            created_at=created_at,
            updated_at=updated_at
        )

    def _domain_to_task_dict(self, task: Task) -> Dict[str, Any]:
        return task.to_dict()

    def find_by_id(self, task_id: TaskId) -> Optional[Task]:
        data = self._load_data()
        for task_dict in data.get("tasks", []):
            if task_dict["id"] == str(task_id):
                try:
                    return self._task_dict_to_domain(task_dict)
                except ValueError as e:
                    logging.error(f"Error converting task dict to domain: {e} - Task data: {task_dict}")
                    continue
        return None

    def find_all(self) -> List[Task]:
        data = self._load_data()
        tasks = []
        for task_dict in data.get("tasks", []):
            try:
                tasks.append(self._task_dict_to_domain(task_dict))
            except ValueError as e:
                logging.error(f"Error converting task dict to domain: {e} - Task data: {task_dict}")
                continue
        return tasks

    def find_by_criteria(self, criteria: Dict[str, Any], limit: Optional[int] = None) -> List[Task]:
        all_tasks = self.find_all()
        
        temp_repo = InMemoryTaskRepository()
        for task in all_tasks:
            temp_repo.save(task)
            
        return temp_repo.find_by_criteria(criteria, limit)

    def search(self, query: str, limit: Optional[int] = None) -> List[Task]:
        all_tasks = self.find_all()
        
        temp_repo = InMemoryTaskRepository()
        for task in all_tasks:
            temp_repo.save(task)
            
        return temp_repo.search(query, limit)

    def save(self, task: Task):
        data = self._load_data()
        tasks = data.get("tasks", [])
        
        task_dict = self._domain_to_task_dict(task)
        
        found = False
        for i, existing_task in enumerate(tasks):
            if existing_task["id"] == task_dict["id"]:
                tasks[i] = task_dict
                found = True
                break
        
        if not found:
            tasks.append(task_dict)
        
        data["tasks"] = tasks
        self._save_data(data)

    def delete(self, task_id: TaskId) -> bool:
        data = self._load_data()
        tasks = data.get("tasks", [])
        
        initial_len = len(tasks)
        tasks = [t for t in tasks if t["id"] != str(task_id)]
        
        if len(tasks) < initial_len:
            data["tasks"] = tasks
            self._save_data(data)
            return True
        return False

    def get_next_id(self) -> TaskId:
        data = self._load_data()
        tasks = data.get("tasks", [])
        
        today_str = datetime.now().strftime("%Y%m%d")
        
        highest_daily_index = 0
        for task in tasks:
            task_id = task["id"]
            if task_id.startswith(today_str):
                try:
                    daily_index = int(task_id[8:])
                    if daily_index > highest_daily_index:
                        highest_daily_index = daily_index
                except (ValueError, IndexError):
                    continue
        
        new_daily_index = highest_daily_index + 1
        new_id_str = f"{today_str}{new_daily_index:03d}"
        
        return TaskId(new_id_str)

    def find_by_status(self, status: TaskStatus) -> List[Task]:
        return self.find_by_criteria({"status": status.value})

    def find_by_priority(self, priority: Priority) -> List[Task]:
        return self.find_by_criteria({"priority": priority.value})

    def find_by_assignee(self, assignee: str) -> List[Task]:
        return self.find_by_criteria({"assignee": assignee})

    def find_by_assignees(self, assignees: List[str]) -> List[Task]:
        return self.find_by_criteria({"assignees": assignees})

    def find_by_labels(self, labels: List[str]) -> List[Task]:
        return self.find_by_criteria({"labels": labels})

    def exists(self, task_id: TaskId) -> bool:
        return self.find_by_id(task_id) is not None

    def count(self) -> int:
        data = self._load_data()
        return len(data.get("tasks", []))

    def get_statistics(self) -> Dict[str, Any]:
        all_tasks = self.find_all()
        
        temp_repo = InMemoryTaskRepository()
        for task in all_tasks:
            temp_repo.save(task)
            
        return temp_repo.get_statistics() 