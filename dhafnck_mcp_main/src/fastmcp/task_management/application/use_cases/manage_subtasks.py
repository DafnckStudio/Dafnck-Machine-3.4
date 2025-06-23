"""Subtask Management Use Cases"""

from typing import Dict, Any, List, Union
from dataclasses import dataclass

from ...domain import TaskRepository, TaskId, TaskNotFoundError


@dataclass
class AddSubtaskRequest:
    """Request to add a subtask"""
    task_id: Union[str, int]
    title: str
    description: str = ""
    assignee: str = ""


@dataclass
class UpdateSubtaskRequest:
    """Request to update a subtask"""
    task_id: Union[str, int]
    subtask_id: Union[str, int]
    title: str = None
    description: str = None
    completed: bool = None
    assignee: str = None


@dataclass
class SubtaskResponse:
    """Response containing subtask information"""
    task_id: str
    subtask: Dict[str, Any]
    progress: Dict[str, Any]


class ManageSubtasksUseCase:
    """Use case for managing task subtasks"""
    
    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository
    
    def _convert_to_task_id(self, task_id: Union[str, int]) -> TaskId:
        """Convert task_id to TaskId domain object (handle both int and str)"""
        if isinstance(task_id, int):
            return TaskId.from_int(task_id)
        else:
            return TaskId.from_string(str(task_id))
    
    def add_subtask(self, request: AddSubtaskRequest) -> SubtaskResponse:
        """Add a subtask to a task"""
        task_id = self._convert_to_task_id(request.task_id)
        task = self._task_repository.find_by_id(task_id)
        
        if not task:
            raise TaskNotFoundError(f"Task {request.task_id} not found")
        
        subtask = {
            "title": request.title,
            "description": request.description,
            "completed": False,
            "assignee": request.assignee
        }
        
        added_subtask = task.add_subtask(subtask)
        self._task_repository.save(task)
        
        return SubtaskResponse(
            task_id=str(request.task_id),
            subtask=added_subtask,
            progress=task.get_subtask_progress()
        )
    
    def remove_subtask(self, task_id: Union[str, int], subtask_id: Union[str, int]) -> Dict[str, Any]:
        """Remove a subtask from a task"""
        task_id_obj = self._convert_to_task_id(task_id)
        task = self._task_repository.find_by_id(task_id_obj)
        
        if not task:
            raise TaskNotFoundError(f"Task {task_id} not found")
        
        try:
            task.remove_subtask(subtask_id)
            self._task_repository.save(task)
            success = True
        except ValueError:
            success = False
        
        return {
            "success": success,
            "task_id": str(task_id),
            "subtask_id": str(subtask_id),
            "progress": task.get_subtask_progress()
        }
    
    def update_subtask(self, request: UpdateSubtaskRequest) -> SubtaskResponse:
        """Update a subtask"""
        task_id = self._convert_to_task_id(request.task_id)
        task = self._task_repository.find_by_id(task_id)
        
        if not task:
            raise TaskNotFoundError(f"Task {request.task_id} not found")
        
        updates = {}
        if request.title is not None:
            updates["title"] = request.title
        if request.description is not None:
            updates["description"] = request.description
        if request.completed is not None:
            updates["completed"] = request.completed
        if request.assignee is not None:
            updates["assignee"] = request.assignee
        
        try:
            task.update_subtask(request.subtask_id, updates)
            self._task_repository.save(task)
            
            # Find the updated subtask
            updated_subtask = task.get_subtask(request.subtask_id)
            
            return SubtaskResponse(
                task_id=str(request.task_id),
                subtask=updated_subtask,
                progress=task.get_subtask_progress()
            )
        except ValueError:
            raise ValueError(f"Subtask {request.subtask_id} not found in task {request.task_id}")
    
    def complete_subtask(self, task_id: Union[str, int], subtask_id: Union[str, int]) -> Dict[str, Any]:
        """Mark a subtask as completed"""
        task_id_obj = self._convert_to_task_id(task_id)
        task = self._task_repository.find_by_id(task_id_obj)
        
        if not task:
            raise TaskNotFoundError(f"Task {task_id} not found")
        
        try:
            task.complete_subtask(subtask_id)
            self._task_repository.save(task)
            success = True
        except ValueError:
            success = False
        
        return {
            "success": success,
            "task_id": str(task_id),
            "subtask_id": str(subtask_id),
            "progress": task.get_subtask_progress()
        }
    
    def get_subtasks(self, task_id: Union[str, int]) -> Dict[str, Any]:
        """Get all subtasks for a task"""
        task_id_obj = self._convert_to_task_id(task_id)
        task = self._task_repository.find_by_id(task_id_obj)
        
        if not task:
            raise TaskNotFoundError(f"Task {task_id} not found")
        
        return {
            "task_id": str(task_id),
            "subtasks": task.subtasks,
            "progress": task.get_subtask_progress()
        } 