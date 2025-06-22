"""Subtask Management Use Cases"""

from dataclasses import dataclass
from typing import Any, Dict, Union

from ...domain import AutoRuleGenerator, TaskId, TaskNotFoundError, TaskRepository


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

    def __init__(self, task_repository: TaskRepository, auto_rule_generator: AutoRuleGenerator = None):
        self._task_repository = task_repository
        self._auto_rule_generator = auto_rule_generator

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
            "assignee": request.assignee,
        }

        task.add_subtask(subtask)
        self._task_repository.save(task)

        return SubtaskResponse(
            task_id=str(request.task_id),
            subtask=subtask,
            progress=task.get_subtask_progress(),
        )

    def remove_subtask(
        self, task_id: Union[str, int], subtask_id: Union[str, int]
    ) -> Dict[str, Any]:
        """Remove a subtask from a task"""
        task_id_obj = self._convert_to_task_id(task_id)
        task = self._task_repository.find_by_id(task_id_obj)

        if not task:
            raise TaskNotFoundError(f"Task {task_id} not found")

        success = task.remove_subtask(subtask_id)
        if success:
            self._task_repository.save(task)

        return {
            "success": success,
            "task_id": str(task_id),
            "subtask_id": str(subtask_id),
            "progress": task.get_subtask_progress(),
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

        success = task.update_subtask(request.subtask_id, updates)
        if success:
            self._task_repository.save(task)

            # 🚀 NEW: Generate context update for subtask completion
            if request.completed and self._auto_rule_generator:
                try:
                    self._auto_rule_generator.generate_subtask_completion_context(task, request.subtask_id)
                except Exception as e:
                    import logging
                    logging.warning(f"Subtask context generation failed for task {task_id}, subtask {request.subtask_id}: {e}")

            # Find the updated subtask
            updated_subtask = task.get_subtask(request.subtask_id)

            return SubtaskResponse(
                task_id=str(request.task_id),
                subtask=updated_subtask,
                progress=task.get_subtask_progress(),
            )
        else:
            raise ValueError(
                f"Subtask {request.subtask_id} not found in task {request.task_id}"
            )

    def complete_subtask(
        self, task_id: Union[str, int], subtask_id: Union[str, int]
    ) -> Dict[str, Any]:
        """Mark a subtask as completed"""
        task_id_obj = self._convert_to_task_id(task_id)
        task = self._task_repository.find_by_id(task_id_obj)

        if not task:
            raise TaskNotFoundError(f"Task {task_id} not found")

        success = task.complete_subtask(subtask_id)
        if success:
            self._task_repository.save(task)
            
            # 🚀 NEW: Generate AI-driven subtask completion context
            if self._auto_rule_generator:
                try:
                    self._auto_rule_generator.generate_subtask_completion_context(task, subtask_id)
                except Exception as e:
                    import logging
                    logging.warning(f"Subtask context generation failed for task {task_id}, subtask {subtask_id}: {e}")

        return {
            "success": success,
            "task_id": str(task_id),
            "subtask_id": str(subtask_id),
            "progress": task.get_subtask_progress(),
            "next_action_agent": "Call @documentation_agent to update context for add information to this task (contextmaster.mdc)"
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
            "progress": task.get_subtask_progress(),
        }

    def execute(self, action: str, task_id: Union[str, int], subtask_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute subtask management action (unified interface for tests)"""
        if action == "add_subtask":
            if not subtask_data or "title" not in subtask_data:
                raise ValueError("title is required for add_subtask action")
            request = AddSubtaskRequest(
                task_id=task_id,
                title=subtask_data["title"],
                description=subtask_data.get("description", ""),
                assignee=subtask_data.get("assignee", "")
            )
            response = self.add_subtask(request)
            return {
                "success": True,
                "action": "add_subtask",
                "subtask": response.subtask
            }
        
        elif action == "complete_subtask":
            if not subtask_data or "subtask_id" not in subtask_data:
                raise ValueError("subtask_id is required for complete_subtask action")
            result = self.complete_subtask(task_id, subtask_data["subtask_id"])
            return {
                "success": result["success"],
                "action": "complete_subtask",
                "result": result
            }
        
        elif action == "update_subtask":
            if not subtask_data or "subtask_id" not in subtask_data:
                raise ValueError("subtask_id is required for update_subtask action")
            request = UpdateSubtaskRequest(
                task_id=task_id,
                subtask_id=subtask_data["subtask_id"],
                title=subtask_data.get("title"),
                description=subtask_data.get("description"),
                completed=subtask_data.get("completed"),
                assignee=subtask_data.get("assignee")
            )
            response = self.update_subtask(request)
            return {
                "success": True,
                "action": "update_subtask",
                "result": response
            }
        
        elif action == "remove_subtask":
            if not subtask_data or "subtask_id" not in subtask_data:
                raise ValueError("subtask_id is required for remove_subtask action")
            result = self.remove_subtask(task_id, subtask_data["subtask_id"])
            return {
                "success": result["success"],
                "action": "remove_subtask",
                "result": result
            }
        
        elif action == "list_subtasks":
            result = self.get_subtasks(task_id)
            return {
                "success": True,
                "action": "list_subtasks",
                "subtasks": result["subtasks"]
            }
        
        else:
            raise ValueError(f"Invalid action: {action}. Supported actions: add_subtask, complete_subtask, update_subtask, remove_subtask, list_subtasks")
