"""Create Task Use Case"""

from ...domain import Task, TaskRepository, TaskId, TaskStatus, Priority
from ...domain.events import TaskCreated
from ..dtos.task_dto import CreateTaskRequest, TaskResponse


class CreateTaskUseCase:
    """Use case for creating a new task"""
    
    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository
    
    def execute(self, request: CreateTaskRequest) -> TaskResponse:
        """Execute the create task use case"""
        # Generate new task ID
        task_id = self._task_repository.get_next_id()
        
        # Create domain value objects
        status = TaskStatus(request.status or "todo")
        priority = Priority(request.priority or "medium")
        
        # Create domain entity
        task = Task(
            id=task_id,
            title=request.title,
            description=request.description,
            project_id=request.project_id,
            status=status,
            priority=priority,
            details=request.details,
            estimated_effort=request.estimated_effort,
            assignees=request.assignees,
            labels=request.labels,
            due_date=request.due_date
        )
        
        # Save the task
        self._task_repository.save(task)
        
        # Handle domain events
        events = task.get_events()
        for event in events:
            if isinstance(event, TaskCreated):
                # Could trigger notifications, logging, etc.
                pass
        
        # Convert to response DTO
        return TaskResponse.from_domain(task) 