"""List Tasks Use Case"""

from ...domain import Priority, TaskRepository, TaskStatus
from ..dtos.task_dto import ListTasksRequest, TaskListResponse


class ListTasksUseCase:
    """Use case for listing tasks with optional filtering"""

    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository

    def execute(self, request: ListTasksRequest) -> TaskListResponse:
        """Execute the list tasks use case"""
        # Build filter criteria
        filters = {}

        if request.status:
            filters["status"] = TaskStatus(request.status)

        if request.priority:
            filters["priority"] = Priority(request.priority)

        # Handle both new assignees field and legacy assignee field
        if hasattr(request, "assignees") and request.assignees:
            filters["assignees"] = request.assignees
        elif hasattr(request, "assignee") and request.assignee:
            filters["assignee"] = request.assignee

        if request.labels:
            filters["labels"] = request.labels

        # Get tasks from repository
        tasks = self._task_repository.find_by_criteria(filters, limit=request.limit)

        # Convert to response DTO
        return TaskListResponse.from_domain_list(tasks)
