"""Delete Task Use Case"""

from typing import Union

from ...domain import TaskId, TaskRepository
from ...domain.events import TaskDeleted


class DeleteTaskUseCase:
    """Use case for deleting a task"""

    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository

    def execute(self, task_id: Union[str, int]) -> bool:
        """Execute the delete task use case"""
        # Convert to domain value object (handle both int and str)
        if isinstance(task_id, int):
            domain_task_id = TaskId.from_int(task_id)
        else:
            domain_task_id = TaskId.from_string(str(task_id))

        # Find the task
        task = self._task_repository.find_by_id(domain_task_id)
        if not task:
            return False

        # Mark task as deleted (triggers domain event)
        task.mark_as_deleted()

        # Delete from repository
        success = self._task_repository.delete(domain_task_id)

        if success:
            # Handle domain events
            events = task.get_events()
            for event in events:
                if isinstance(event, TaskDeleted):
                    # Could trigger cleanup, notifications, etc.
                    pass

        return success
