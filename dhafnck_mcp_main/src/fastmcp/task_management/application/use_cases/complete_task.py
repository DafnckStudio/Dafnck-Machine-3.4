"""Complete Task Use Case"""

from typing import Union, Dict, Any
from ...domain import TaskRepository, TaskId, TaskNotFoundError
from ...domain.events import TaskUpdated


class CompleteTaskUseCase:
    """Use case for completing a task (marking all subtasks as completed and task status as done)"""
    
    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository
    
    def execute(self, task_id: Union[str, int]) -> Dict[str, Any]:
        """Execute the complete task use case"""
        # Convert to domain value object (handle both int and str)
        if isinstance(task_id, int):
            domain_task_id = TaskId.from_int(task_id)
        else:
            domain_task_id = TaskId.from_string(str(task_id))
        
        # Find the task
        task = self._task_repository.find_by_id(domain_task_id)
        if not task:
            raise TaskNotFoundError(f"Task {task_id} not found")
        
        # Check if task is already completed
        if task.status.is_done():
            return {
                "success": False,
                "task_id": str(task_id),
                "message": f"Task {task_id} is already completed",
                "status": str(task.status)
            }
        
        # Complete the task (will complete all subtasks and set status to done)
        task.complete_task()
        
        # Save the task
        self._task_repository.save(task)
        
        # Handle domain events
        events = task.get_events()
        for event in events:
            if isinstance(event, TaskUpdated):
                # Could trigger notifications, logging, etc.
                pass
        
        # Get subtask progress for the response
        progress = task.get_subtask_progress()
        
        # Return success response with required message format
        return {
            "success": True,
            "task_id": str(task_id),
            "status": str(task.status),
            "subtask_progress": progress,
            "message": f"task {task_id} done, can do_next"
        } 