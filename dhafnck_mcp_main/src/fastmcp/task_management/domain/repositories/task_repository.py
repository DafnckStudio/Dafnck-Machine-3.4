"""Task Repository Interface"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from ..entities.task import Task
from ..value_objects import TaskId, TaskStatus, Priority


class TaskRepository(ABC):
    """Repository interface for Task aggregate"""
    
    @abstractmethod
    def save(self, task: Task) -> bool:
        """Save a task"""
        pass
    
    @abstractmethod
    def find_by_id(self, task_id: TaskId) -> Optional[Task]:
        """Find task by ID"""
        pass
    
    @abstractmethod
    def find_all(self) -> List[Task]:
        """Find all tasks"""
        pass
    
    @abstractmethod
    def find_by_status(self, status: TaskStatus) -> List[Task]:
        """Find tasks by status"""
        pass
    
    @abstractmethod
    def find_by_priority(self, priority: Priority) -> List[Task]:
        """Find tasks by priority"""
        pass
    
    @abstractmethod
    def find_by_assignee(self, assignee: str) -> List[Task]:
        """Find tasks by assignee"""
        pass
    
    @abstractmethod
    def find_by_labels(self, labels: List[str]) -> List[Task]:
        """Find tasks containing any of the specified labels"""
        pass
    
    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[Task]:
        """Search tasks by query string"""
        pass
    
    @abstractmethod
    def delete(self, task_id: TaskId) -> bool:
        """Delete a task"""
        pass
    
    @abstractmethod
    def exists(self, task_id: TaskId) -> bool:
        """Check if task exists"""
        pass
    
    @abstractmethod
    def get_next_id(self) -> TaskId:
        """Get next available task ID"""
        pass
    
    @abstractmethod
    def count(self) -> int:
        """Get total number of tasks"""
        pass
    
    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """Get task statistics"""
        pass 