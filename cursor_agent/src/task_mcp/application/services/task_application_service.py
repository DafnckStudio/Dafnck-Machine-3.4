"""Task Application Service"""

from typing import Optional

from ...domain import AutoRuleGenerator, TaskRepository
from ...domain.exceptions import TaskNotFoundError
from ..dtos import (
    AddDependencyRequest,
    AddSubtaskRequest,
    CreateTaskRequest,
    DependencyResponse,
    ListTasksRequest,
    SearchTasksRequest,
    SubtaskResponse,
    TaskListResponse,
    TaskResponse,
    UpdateSubtaskRequest,
    UpdateTaskRequest,
)
from ..use_cases import (
    CompleteTaskUseCase,
    CreateTaskUseCase,
    DeleteTaskUseCase,
    GetTaskUseCase,
    ListTasksUseCase,
    ManageDependenciesUseCase,
    ManageSubtasksUseCase,
    SearchTasksUseCase,
    UpdateTaskUseCase,
)


class TaskApplicationService:
    """Application service that orchestrates use cases"""

    def __init__(
        self, task_repository: TaskRepository, auto_rule_generator: AutoRuleGenerator
    ):
        self._task_repository = task_repository
        self._auto_rule_generator = auto_rule_generator

        # Initialize use cases
        self._create_task_use_case = CreateTaskUseCase(task_repository)
        self._get_task_use_case = GetTaskUseCase(task_repository, auto_rule_generator)
        self._update_task_use_case = UpdateTaskUseCase(task_repository)
        self._list_tasks_use_case = ListTasksUseCase(task_repository)
        self._search_tasks_use_case = SearchTasksUseCase(task_repository)
        self._delete_task_use_case = DeleteTaskUseCase(task_repository)
        self._complete_task_use_case = CompleteTaskUseCase(task_repository, auto_rule_generator)
        self._manage_subtasks_use_case = ManageSubtasksUseCase(task_repository, auto_rule_generator)
        self._manage_dependencies_use_case = ManageDependenciesUseCase(task_repository)

    def create_task(self, request: CreateTaskRequest) -> TaskResponse:
        """Create a new task"""
        return self._create_task_use_case.execute(request)

    def get_task(
        self,
        task_id: str,
        generate_rules: bool = True,
        force_full_generation: bool = False,
    ) -> Optional[TaskResponse]:
        """Get a single task by its ID"""
        try:
            return self._get_task_use_case.execute(
                task_id,
                generate_rules=generate_rules,
                force_full_generation=force_full_generation,
            )
        except TaskNotFoundError:
            return None

    def update_task(self, request: UpdateTaskRequest) -> Optional[TaskResponse]:
        """Update an existing task"""
        return self._update_task_use_case.execute(request)

    def list_tasks(self, request: ListTasksRequest) -> TaskListResponse:
        """List tasks with optional filtering"""
        return self._list_tasks_use_case.execute(request)

    def search_tasks(self, request: SearchTasksRequest) -> TaskListResponse:
        """Search tasks by keyword"""
        return self._search_tasks_use_case.execute(request)

    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        return self._delete_task_use_case.execute(task_id)

    def complete_task(self, task_id: str) -> dict:
        """Complete a task (mark all subtasks as completed and set status to done)"""
        return self._complete_task_use_case.execute(task_id)

    # Subtask management methods
    def add_subtask(self, request: AddSubtaskRequest) -> SubtaskResponse:
        """Add a subtask to a task"""
        return self._manage_subtasks_use_case.add_subtask(request)

    def remove_subtask(self, task_id: str, subtask_id: str) -> dict:
        """Remove a subtask from a task"""
        return self._manage_subtasks_use_case.remove_subtask(task_id, subtask_id)

    def update_subtask(self, request: UpdateSubtaskRequest) -> SubtaskResponse:
        """Update a subtask"""
        return self._manage_subtasks_use_case.update_subtask(request)

    def complete_subtask(self, task_id: str, subtask_id: str) -> dict:
        """Mark a subtask as completed"""
        return self._manage_subtasks_use_case.complete_subtask(task_id, subtask_id)

    def get_subtasks(self, task_id: str) -> dict:
        """Get all subtasks for a task"""
        return self._manage_subtasks_use_case.get_subtasks(task_id)

    # Dependency management methods
    def add_dependency(self, request: AddDependencyRequest) -> DependencyResponse:
        """Add a dependency to a task"""
        return self._manage_dependencies_use_case.add_dependency(request)

    def remove_dependency(self, task_id: str, dependency_id: str) -> DependencyResponse:
        """Remove a dependency from a task"""
        return self._manage_dependencies_use_case.remove_dependency(
            task_id, dependency_id
        )

    def get_dependencies(self, task_id: str) -> dict:
        """Get all dependencies for a task"""
        return self._manage_dependencies_use_case.get_dependencies(task_id)

    def clear_dependencies(self, task_id: str) -> DependencyResponse:
        """Remove all dependencies from a task"""
        return self._manage_dependencies_use_case.clear_dependencies(task_id)

    def get_blocking_tasks(self, task_id: str) -> dict:
        """Get all tasks that are blocked by this task"""
        return self._manage_dependencies_use_case.get_blocking_tasks(task_id)

    # Convenience methods for common operations
    def get_all_tasks(self) -> TaskListResponse:
        """Get all tasks"""
        request = ListTasksRequest()
        return self.list_tasks(request)

    def get_tasks_by_status(self, status: str) -> TaskListResponse:
        """Get tasks by status"""
        request = ListTasksRequest(status=status)
        return self.list_tasks(request)

    def get_tasks_by_assignee(self, assignee: str) -> TaskListResponse:
        """Get tasks by assignee"""
        request = ListTasksRequest(assignees=[assignee])
        return self.list_tasks(request)

    def manage_subtasks(self, task_id: str, action: str, subtask_data: dict) -> dict:
        """Unified subtask management interface for MCP tools"""
        if action in ["add_subtask", "add"]:
            request = AddSubtaskRequest(
                task_id=task_id,
                title=subtask_data.get("title", ""),
                description=subtask_data.get("description", ""),
                assignee=subtask_data.get("assignee", ""),
            )
            return self.add_subtask(request).__dict__
        elif action in ["complete_subtask", "complete"]:
            subtask_id = subtask_data.get("subtask_id")
            if subtask_id is None:
                raise ValueError("subtask_id is required for completing a subtask")
            return self.complete_subtask(task_id, subtask_id)
        elif action in ["update_subtask", "update"]:
            request = UpdateSubtaskRequest(
                task_id=task_id,
                subtask_id=subtask_data.get("subtask_id"),
                title=subtask_data.get("title"),
                description=subtask_data.get("description"),
                completed=subtask_data.get("completed"),
                assignee=subtask_data.get("assignee"),
            )
            return self.update_subtask(request).__dict__
        elif action in ["remove_subtask", "remove"]:
            subtask_id = subtask_data.get("subtask_id")
            if subtask_id is None:
                raise ValueError("subtask_id is required for removing a subtask")
            return self.remove_subtask(task_id, subtask_id)
        elif action in ["list_subtasks", "list"]:
            return self.get_subtasks(task_id)
        else:
            raise ValueError(f"Unknown subtask action: {action}")
