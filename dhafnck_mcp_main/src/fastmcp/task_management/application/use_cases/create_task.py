"""Create Task Use Case"""

from typing import Optional
from ...domain import Task, TaskRepository, TaskId, TaskStatus, Priority, AutoRuleGenerator
from ...domain.events import TaskCreated
from ..dtos.task_dto import CreateTaskRequest, TaskResponse, CreateTaskResponse


class CreateTaskUseCase:
    """Use case for creating a new task"""
    
    def __init__(self, task_repository: TaskRepository, auto_rule_generator: Optional[AutoRuleGenerator] = None):
        self._task_repository = task_repository
        self._auto_rule_generator = auto_rule_generator
    
    def execute(self, request: CreateTaskRequest) -> CreateTaskResponse:
        """Execute the create task use case"""
        try:
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
            
            # Generate auto rules if generator is provided
            if self._auto_rule_generator:
                try:
                    self._auto_rule_generator.generate_rules_for_task(task)
                except Exception as e:
                    # Log the error but don't fail the task creation
                    import logging
                    logging.warning(f"Failed to generate auto rules for task {task.id}: {e}")
            
            # Handle domain events
            events = task.get_events()
            for event in events:
                if isinstance(event, TaskCreated):
                    # Could trigger notifications, logging, etc.
                    pass
            
            # Convert to response DTO
            task_response = TaskResponse.from_domain(task)
            return CreateTaskResponse.success_response(task_response)
            
        except Exception as e:
            # Handle any errors during task creation
            import logging
            logging.error(f"Failed to create task: {e}")
            return CreateTaskResponse.error_response(f"Failed to create task: {str(e)}") 