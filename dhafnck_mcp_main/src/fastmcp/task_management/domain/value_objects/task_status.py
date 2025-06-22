"""Task Status Value Object"""

from dataclasses import dataclass
from enum import Enum
from typing import Set


class TaskStatusEnum(Enum):
    """Enumeration of valid task statuses"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    REVIEW = "review"
    TESTING = "testing"
    DONE = "done"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class TaskStatus:
    """Value object for Task Status with validation"""
    
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Task status cannot be empty")
        
        valid_statuses = {status.value for status in TaskStatusEnum}
        if self.value not in valid_statuses:
            raise ValueError(f"Invalid task status: {self.value}. Valid statuses: {', '.join(valid_statuses)}")
    
    def __str__(self) -> str:
        return self.value
    
    @classmethod
    def todo(cls) -> 'TaskStatus':
        return cls(TaskStatusEnum.TODO.value)
    
    @classmethod
    def in_progress(cls) -> 'TaskStatus':
        return cls(TaskStatusEnum.IN_PROGRESS.value)
    
    @classmethod
    def blocked(cls) -> 'TaskStatus':
        return cls(TaskStatusEnum.BLOCKED.value)
    
    @classmethod
    def review(cls) -> 'TaskStatus':
        return cls(TaskStatusEnum.REVIEW.value)
    
    @classmethod
    def testing(cls) -> 'TaskStatus':
        return cls(TaskStatusEnum.TESTING.value)
    
    @classmethod
    def done(cls) -> 'TaskStatus':
        return cls(TaskStatusEnum.DONE.value)
    
    @classmethod
    def cancelled(cls) -> 'TaskStatus':
        return cls(TaskStatusEnum.CANCELLED.value)
    
    def is_todo(self) -> bool:
        return self.value == TaskStatusEnum.TODO.value
    
    def is_in_progress(self) -> bool:
        return self.value == TaskStatusEnum.IN_PROGRESS.value
    
    def is_done(self) -> bool:
        return self.value == TaskStatusEnum.DONE.value
    
    def is_completed(self) -> bool:
        """Alias for is_done() for backward compatibility"""
        return self.is_done()
    
    def can_transition_to(self, new_status: str) -> bool:
        """Check if transition to new status is valid"""
        transitions = {
            TaskStatusEnum.TODO.value: {TaskStatusEnum.IN_PROGRESS.value, TaskStatusEnum.CANCELLED.value},
            TaskStatusEnum.IN_PROGRESS.value: {TaskStatusEnum.BLOCKED.value, TaskStatusEnum.REVIEW.value, TaskStatusEnum.TESTING.value, TaskStatusEnum.CANCELLED.value},
            TaskStatusEnum.BLOCKED.value: {TaskStatusEnum.IN_PROGRESS.value, TaskStatusEnum.CANCELLED.value},
            TaskStatusEnum.REVIEW.value: {TaskStatusEnum.IN_PROGRESS.value, TaskStatusEnum.TESTING.value, TaskStatusEnum.DONE.value, TaskStatusEnum.CANCELLED.value},
            TaskStatusEnum.TESTING.value: {TaskStatusEnum.IN_PROGRESS.value, TaskStatusEnum.REVIEW.value, TaskStatusEnum.DONE.value, TaskStatusEnum.CANCELLED.value},
            TaskStatusEnum.DONE.value: set(),  # No transitions from completed
            TaskStatusEnum.CANCELLED.value: {TaskStatusEnum.TODO.value}  # Can reopen cancelled tasks
        }
        
        return new_status in transitions.get(self.value, set()) 