"""Application DTOs"""

from ..use_cases.manage_dependencies import AddDependencyRequest, DependencyResponse

# Import DTOs from use cases
from ..use_cases.manage_subtasks import (
    AddSubtaskRequest,
    SubtaskResponse,
    UpdateSubtaskRequest,
)
from .task_dto import (
    CreateTaskRequest,
    ListTasksRequest,
    SearchTasksRequest,
    TaskListResponse,
    TaskResponse,
    UpdateTaskRequest,
)

__all__ = [
    "CreateTaskRequest",
    "UpdateTaskRequest",
    "ListTasksRequest",
    "SearchTasksRequest",
    "TaskResponse",
    "TaskListResponse",
    "AddSubtaskRequest",
    "UpdateSubtaskRequest",
    "SubtaskResponse",
    "AddDependencyRequest",
    "DependencyResponse",
]
