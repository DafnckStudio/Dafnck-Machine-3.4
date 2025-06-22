"""Update Task Use Case"""

from typing import Optional, Union

from ...domain import TaskRepository, TaskId, TaskStatus, Priority, TaskNotFoundError, AutoRuleGenerator
from ...domain.events import TaskUpdated
from ..dtos.task_dto import UpdateTaskRequest, TaskResponse, UpdateTaskResponse


class UpdateTaskUseCase:
    """Use case for updating an existing task"""
    
    def __init__(self, task_repository: TaskRepository, auto_rule_generator: Optional[AutoRuleGenerator] = None):
        self._task_repository = task_repository
        self._auto_rule_generator = auto_rule_generator
    
    def execute(self, request: UpdateTaskRequest) -> UpdateTaskResponse:
        """Execute the update task use case"""
        # Convert to domain value object with proper type handling
        domain_task_id = self._convert_to_task_id(request.task_id)
        
        # Find the task
        task = self._task_repository.find_by_id(domain_task_id)
        if not task:
            raise TaskNotFoundError(f"Task {request.task_id} not found")
        
        # Update task fields if provided
        if request.title is not None:
            task.update_title(request.title)
        
        if request.description is not None:
            task.update_description(request.description)
        
        if request.status is not None:
            new_status = TaskStatus(request.status)
            task.update_status(new_status)
        
        if request.priority is not None:
            new_priority = Priority(request.priority)
            task.update_priority(new_priority)
        
        if request.details is not None:
            task.update_details(request.details)
        
        if request.estimated_effort is not None:
            task.update_estimated_effort(request.estimated_effort)
        
        if request.assignees is not None:
            task.update_assignees(request.assignees)
        
        if request.labels is not None:
            task.update_labels(request.labels)
        
        if request.due_date is not None:
            task.update_due_date(request.due_date)
        
        # Save the updated task
        self._task_repository.save(task)
        
        # Generate auto rules if generator is provided
        if self._auto_rule_generator:
            try:
                self._auto_rule_generator.generate_rules_for_task(task)
            except Exception as e:
                # Log the error but don't fail the task update
                import logging
                logging.warning(f"Failed to generate auto rules for task {task.id}: {e}")
        
        # Handle domain events
        events = task.get_events()
        for event in events:
            if isinstance(event, TaskUpdated):
                # Could trigger notifications, logging, etc.
                pass
        
        # Convert to response DTO
        task_response = TaskResponse.from_domain(task)
        return UpdateTaskResponse.success_response(task_response)
    
    def _convert_to_task_id(self, task_id: Union[str, int, TaskId]) -> TaskId:
        """Convert task_id to TaskId domain object"""
        if isinstance(task_id, TaskId):
            return task_id
        if isinstance(task_id, int):
            return TaskId.from_int(task_id)
        elif isinstance(task_id, str):
            # Try to parse as int first (for legacy compatibility)
            try:
                return TaskId.from_int(int(task_id))
            except ValueError:
                # If not an int string, treat as TaskId string
                return TaskId.from_string(task_id)
        else:
            raise ValueError(f"Invalid task_id type: {type(task_id)}") 