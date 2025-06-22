"""Task Domain Exceptions"""


class TaskDomainError(Exception):
    """Base exception for task domain errors"""


class TaskNotFoundError(TaskDomainError):
    """Raised when a task is not found"""

    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task with ID {task_id} not found")


class InvalidTaskStateError(TaskDomainError):
    """Raised when a task operation is invalid for the current state"""

    def __init__(self, message: str):
        super().__init__(message)


class InvalidTaskTransitionError(TaskDomainError):
    """Raised when a task status transition is invalid"""

    def __init__(self, current_status: str, target_status: str):
        self.current_status = current_status
        self.target_status = target_status
        super().__init__(
            f"Cannot transition from '{current_status}' to '{target_status}'"
        )
