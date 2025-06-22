"""Task Repository Interface"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..entities.task import Task
from ..value_objects import Priority, TaskId, TaskStatus


class TaskRepository(ABC):
    """Repository interface for Task aggregate"""

    @abstractmethod
    def save(self, task: Task) -> bool:
        """Save a task"""

    @abstractmethod
    def find_by_id(self, task_id: TaskId) -> Optional[Task]:
        """Find task by ID"""

    @abstractmethod
    def find_all(self) -> List[Task]:
        """Find all tasks"""

    @abstractmethod
    def find_by_status(self, status: TaskStatus) -> List[Task]:
        """Find tasks by status"""

    @abstractmethod
    def find_by_priority(self, priority: Priority) -> List[Task]:
        """Find tasks by priority"""

    @abstractmethod
    def find_by_assignee(self, assignee: str) -> List[Task]:
        """Find tasks by assignee"""

    @abstractmethod
    def find_by_labels(self, labels: List[str]) -> List[Task]:
        """Find tasks containing any of the specified labels"""

    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[Task]:
        """Search tasks by query string"""

    @abstractmethod
    def delete(self, task_id: TaskId) -> bool:
        """Delete a task"""

    @abstractmethod
    def exists(self, task_id: TaskId) -> bool:
        """Check if task exists"""

    @abstractmethod
    def get_next_id(self) -> TaskId:
        """Get next available task ID"""

    @abstractmethod
    def count(self) -> int:
        """Get total number of tasks"""

    @abstractmethod
    def get_statistics(self) -> Dict[str, Any]:
        """Get task statistics"""
