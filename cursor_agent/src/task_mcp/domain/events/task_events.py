"""Task Domain Events"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

from ..value_objects import TaskId


@dataclass(frozen=True)
class DomainEvent:
    """Base class for domain events"""

    occurred_at: datetime = None

    def __post_init__(self):
        if self.occurred_at is None:
            object.__setattr__(self, "occurred_at", datetime.now())


@dataclass(frozen=True)
class TaskCreated:
    """Event raised when a task is created"""

    task_id: TaskId
    title: str
    created_at: datetime
    occurred_at: datetime = None

    def __post_init__(self):
        if self.occurred_at is None:
            object.__setattr__(self, "occurred_at", datetime.now())


@dataclass(frozen=True)
class TaskUpdated:
    """Event raised when a task is updated"""

    task_id: TaskId
    field_name: str
    old_value: Any
    new_value: Any
    updated_at: datetime
    occurred_at: datetime = None

    def __post_init__(self):
        if self.occurred_at is None:
            object.__setattr__(self, "occurred_at", datetime.now())


@dataclass(frozen=True)
class TaskRetrieved:
    """Event raised when a task is retrieved (triggers auto rule generation)"""

    task_id: TaskId
    task_data: Dict[str, Any]
    retrieved_at: datetime
    occurred_at: datetime = None

    def __post_init__(self):
        if self.occurred_at is None:
            object.__setattr__(self, "occurred_at", datetime.now())


@dataclass(frozen=True)
class TaskDeleted:
    """Event raised when a task is deleted"""

    task_id: TaskId
    title: str
    deleted_at: datetime
    occurred_at: datetime = None

    def __post_init__(self):
        if self.occurred_at is None:
            object.__setattr__(self, "occurred_at", datetime.now())
