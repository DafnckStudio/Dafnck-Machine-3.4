"""TaskTree Domain Entity"""

from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

from .task import Task
from ..value_objects.task_id import TaskId
from ..value_objects.task_status import TaskStatus


@dataclass
class TaskTree:
    """TaskTree entity representing an independent hierarchical task structure"""
    
    id: str
    name: str
    description: str
    project_id: str
    created_at: datetime
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Task hierarchy
    root_tasks: Dict[str, Task] = field(default_factory=dict)  # task_id -> Task
    all_tasks: Dict[str, Task] = field(default_factory=dict)   # Flattened view for quick lookup
    
    # Tree metadata
    assigned_agent_id: Optional[str] = None
    priority: str = "medium"  # Tree-level priority
    status: str = "active"    # active, paused, completed, archived
    
    def add_root_task(self, task: Task) -> None:
        """Add a root-level task to this tree"""
        self.root_tasks[task.id.value] = task
        self.all_tasks[task.id.value] = task
        self._add_subtasks_to_index(task)
        self.updated_at = datetime.now()
    
    def add_task(self, task: Task, parent_task_id: Optional[str] = None) -> None:
        """Add a task to the tree, optionally as a subtask of another task"""
        if parent_task_id:
            parent_task = self.all_tasks.get(parent_task_id)
            if not parent_task:
                raise ValueError(f"Parent task {parent_task_id} not found in tree")
            
            # Add as subtask to parent
            parent_task.add_subtask({
                "id": task.id.value,
                "title": task.title,
                "description": task.description,
                "completed": task.status.is_done(),
                "assignees": task.assignees
            })
        else:
            # Add as root task
            self.root_tasks[task.id.value] = task
        
        # Add to flattened index
        self.all_tasks[task.id.value] = task
        self._add_subtasks_to_index(task)
        self.updated_at = datetime.now()
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a specific task from the tree"""
        return self.all_tasks.get(task_id)
    
    def has_task(self, task_id: str) -> bool:
        """Check if a task exists in this tree"""
        return task_id in self.all_tasks
    
    def get_available_tasks(self) -> List[Task]:
        """Get tasks that are ready to be worked on (dependencies satisfied, not completed)"""
        available_tasks = []
        
        for task in self.all_tasks.values():
            if self._is_task_available_for_work(task):
                available_tasks.append(task)
        
        return available_tasks
    
    def get_next_task(self) -> Optional[Task]:
        """Get the next highest priority task that's ready for work"""
        available_tasks = self.get_available_tasks()
        
        if not available_tasks:
            return None
        
        # Sort by priority and return highest priority task
        # PriorityLevel: LOW=1, MEDIUM=2, HIGH=3, URGENT=4, CRITICAL=5
        priority_order = {
            "critical": 5,
            "urgent": 4,
            "high": 3,
            "medium": 2,
            "low": 1
        }
        available_tasks.sort(
            key=lambda t: (priority_order.get(t.priority.value, 0), t.created_at),
            reverse=True
        )
        
        return available_tasks[0]
    
    def get_task_count(self) -> int:
        """Get total number of tasks in the tree"""
        return len(self.all_tasks)
    
    def get_completed_task_count(self) -> int:
        """Get number of completed tasks in the tree"""
        return sum(1 for task in self.all_tasks.values() if task.status.is_done())
    
    def get_progress_percentage(self) -> float:
        """Get completion percentage for the entire tree"""
        total_tasks = self.get_task_count()
        if total_tasks == 0:
            return 0.0
        
        completed_tasks = self.get_completed_task_count()
        return (completed_tasks / total_tasks) * 100.0
    
    def get_tree_status(self) -> Dict:
        """Get comprehensive status of the task tree"""
        status_counts = {}
        priority_counts = {}
        
        for task in self.all_tasks.values():
            status = task.status.value
            priority = task.priority.value
            
            status_counts[status] = status_counts.get(status, 0) + 1
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        return {
            "tree_id": self.id,
            "tree_name": self.name,
            "assigned_agent": self.assigned_agent_id,
            "status": self.status,
            "priority": self.priority,
            "total_tasks": self.get_task_count(),
            "completed_tasks": self.get_completed_task_count(),
            "progress_percentage": self.get_progress_percentage(),
            "status_breakdown": status_counts,
            "priority_breakdown": priority_counts,
            "available_tasks": len(self.get_available_tasks()),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def mark_as_completed(self) -> None:
        """Mark the entire tree as completed"""
        self.status = "completed"
        self.updated_at = datetime.now()
    
    def pause_tree(self) -> None:
        """Pause work on this tree"""
        self.status = "paused"
        self.updated_at = datetime.now()
    
    def resume_tree(self) -> None:
        """Resume work on this tree"""
        self.status = "active"
        self.updated_at = datetime.now()
    
    def archive_tree(self) -> None:
        """Archive this tree"""
        self.status = "archived"
        self.updated_at = datetime.now()
    
    def _add_subtasks_to_index(self, task: Task) -> None:
        """Recursively add all subtasks to the flattened index"""
        for subtask_data in task.subtasks:
            subtask_id = subtask_data.get("id")
            if subtask_id and subtask_id not in self.all_tasks:
                # Create Task object for subtask (simplified)
                subtask = Task.create(
                    id=TaskId.from_string(subtask_id),
                    title=subtask_data.get("title", ""),
                    description=subtask_data.get("description", ""),
                    status=TaskStatus.done() if subtask_data.get("completed", False) else TaskStatus.todo(),
                    assignees=subtask_data.get("assignees", []) or [subtask_data.get("assignee", "")] if subtask_data.get("assignee") else []
                )
                self.all_tasks[subtask_id] = subtask
    
    def _is_task_available_for_work(self, task: Task) -> bool:
        """Check if a task is available for work"""
        # Task must not be completed
        if task.status.is_done():
            return False
        
        # Check if all dependencies within this tree are satisfied
        for dep_id in task.dependencies:
            dep_task = self.all_tasks.get(dep_id.value)
            if dep_task and not dep_task.status.is_done():
                return False  # Dependency not completed
        
        return True
    
    def get_dependency_graph(self) -> Dict:
        """Get a representation of the dependency graph for this tree"""
        graph = {}
        
        for task in self.all_tasks.values():
            task_id = task.id.value
            dependencies = [dep.value for dep in task.dependencies if dep.value in self.all_tasks]
            
            graph[task_id] = {
                "title": task.title,
                "status": task.status.value,
                "dependencies": dependencies,
                "blocks": []  # Will be populated below
            }
        
        # Populate what each task blocks
        for task_id, task_info in graph.items():
            for dep_id in task_info["dependencies"]:
                if dep_id in graph:
                    graph[dep_id]["blocks"].append(task_id)
        
        return graph 