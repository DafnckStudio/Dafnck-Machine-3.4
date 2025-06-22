"""Use Cases Module"""

from .call_agent import CallAgentUseCase
from .complete_task import CompleteTaskUseCase
from .create_task import CreateTaskUseCase
from .delete_task import DeleteTaskUseCase
from .do_next import DoNextUseCase
from .get_task import GetTaskUseCase
from .list_tasks import ListTasksUseCase
from .manage_dependencies import (
    AddDependencyRequest,
    DependencyResponse,
    ManageDependenciesUseCase,
)
from .manage_subtasks import (
    AddSubtaskRequest,
    ManageSubtasksUseCase,
    SubtaskResponse,
    UpdateSubtaskRequest,
)
from .search_tasks import SearchTasksUseCase
from .update_task import UpdateTaskUseCase

__all__ = [
    "CreateTaskUseCase",
    "GetTaskUseCase",
    "UpdateTaskUseCase",
    "ListTasksUseCase",
    "SearchTasksUseCase",
    "DeleteTaskUseCase",
    "CompleteTaskUseCase",
    "ManageSubtasksUseCase",
    "ManageDependenciesUseCase",
    "AddSubtaskRequest",
    "UpdateSubtaskRequest",
    "SubtaskResponse",
    "AddDependencyRequest",
    "DependencyResponse",
    "DoNextUseCase",
    "CallAgentUseCase",
]
