"""Application DTOs"""

from .task_dto import (
    CreateTaskRequest,
    UpdateTaskRequest,
    ListTasksRequest,
    SearchTasksRequest,
    TaskResponse,
    CreateTaskResponse,
    TaskListResponse
)

# Import DTOs from use cases
from ..use_cases.manage_subtasks import AddSubtaskRequest, UpdateSubtaskRequest, SubtaskResponse
from ..use_cases.manage_dependencies import AddDependencyRequest, DependencyResponse

__all__ = [
    "CreateTaskRequest",
    "UpdateTaskRequest", 
    "ListTasksRequest",
    "SearchTasksRequest",
    "TaskResponse",
    "CreateTaskResponse",
    "TaskListResponse",
    "AddSubtaskRequest",
    "UpdateSubtaskRequest",
    "SubtaskResponse",
    "AddDependencyRequest",
    "DependencyResponse"
] 