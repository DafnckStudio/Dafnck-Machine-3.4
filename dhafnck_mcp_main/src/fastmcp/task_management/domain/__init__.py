"""
Domain Layer

Contains core business logic, entities, value objects, domain services, and repository interfaces.
This layer has no dependencies on other layers and represents the heart of the business logic.
"""

# Import all domain components
from .entities import Task
from .value_objects import TaskId, TaskStatus, Priority
from .repositories import TaskRepository
from .services import AutoRuleGenerator
from .events import DomainEvent, TaskCreated, TaskUpdated, TaskRetrieved, TaskDeleted
from .exceptions import TaskNotFoundError

__all__ = [
    'Task',
    'TaskId', 'TaskStatus', 'Priority',
    'TaskRepository',
    'AutoRuleGenerator',
    'DomainEvent', 'TaskCreated', 'TaskUpdated', 'TaskRetrieved', 'TaskDeleted',
    'TaskNotFoundError'
] 