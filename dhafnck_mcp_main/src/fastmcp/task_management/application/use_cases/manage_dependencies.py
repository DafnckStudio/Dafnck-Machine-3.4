"""Task Dependencies Management Use Cases"""

from typing import Dict, Any, List, Union
from dataclasses import dataclass

from ...domain import TaskRepository, TaskId, TaskNotFoundError


@dataclass
class AddDependencyRequest:
    """Request to add a dependency"""
    task_id: Union[str, int]
    dependency_id: Union[str, int]


@dataclass
class DependencyResponse:
    """Response containing dependency information"""
    task_id: str
    dependencies: List[str]
    success: bool
    message: str = ""


class ManageDependenciesUseCase:
    """Use case for managing task dependencies"""
    
    def __init__(self, task_repository: TaskRepository):
        self._task_repository = task_repository
    
    def _convert_to_task_id(self, task_id: Union[str, int]) -> TaskId:
        """Convert task_id to TaskId domain object (handle both int and str)"""
        if isinstance(task_id, int):
            return TaskId.from_int(task_id)
        else:
            return TaskId.from_string(str(task_id))
    
    def add_dependency(self, request: AddDependencyRequest) -> DependencyResponse:
        """Add a dependency to a task"""
        task_id = self._convert_to_task_id(request.task_id)
        dependency_id = self._convert_to_task_id(request.dependency_id)
        
        # Validate both tasks exist
        task = self._task_repository.find_by_id(task_id)
        if not task:
            raise TaskNotFoundError(f"Task {request.task_id} not found")
        
        dependency_task = self._task_repository.find_by_id(dependency_id)
        if not dependency_task:
            raise TaskNotFoundError(f"Dependency task {request.dependency_id} not found")
        
        # Check for circular dependency
        if task.has_circular_dependency(dependency_id):
            return DependencyResponse(
                task_id=str(request.task_id),
                dependencies=task.get_dependency_ids(),
                success=False,
                message="Cannot add dependency: would create circular reference"
            )
        
        # Check if dependency already exists
        if task.has_dependency(dependency_id):
            return DependencyResponse(
                task_id=str(request.task_id),
                dependencies=task.get_dependency_ids(),
                success=False,
                message=f"Dependency {request.dependency_id} already exists"
            )
        
        task.add_dependency(dependency_id)
        self._task_repository.save(task)
        
        return DependencyResponse(
            task_id=str(request.task_id),
            dependencies=task.get_dependency_ids(),
            success=True,
            message=f"Dependency {request.dependency_id} added successfully"
        )
    
    def remove_dependency(self, task_id: Union[str, int], dependency_id: Union[str, int]) -> DependencyResponse:
        """Remove a dependency from a task"""
        task_id_obj = self._convert_to_task_id(task_id)
        dependency_id_obj = self._convert_to_task_id(dependency_id)
        
        task = self._task_repository.find_by_id(task_id_obj)
        if not task:
            raise TaskNotFoundError(f"Task {task_id} not found")
        
        if not task.has_dependency(dependency_id_obj):
            return DependencyResponse(
                task_id=str(task_id),
                dependencies=task.get_dependency_ids(),
                success=False,
                message=f"Dependency {dependency_id} does not exist"
            )
        
        task.remove_dependency(dependency_id_obj)
        self._task_repository.save(task)
        
        return DependencyResponse(
            task_id=str(task_id),
            dependencies=task.get_dependency_ids(),
            success=True,
            message=f"Dependency {dependency_id} removed successfully"
        )
    
    def get_dependencies(self, task_id: Union[str, int]) -> Dict[str, Any]:
        """Get all dependencies for a task"""
        task_id_obj = self._convert_to_task_id(task_id)
        task = self._task_repository.find_by_id(task_id_obj)
        
        if not task:
            raise TaskNotFoundError(f"Task {task_id} not found")
        
        # Get detailed dependency information
        dependency_details = []
        for dep_id in task.get_dependency_ids():
            dep_task = self._task_repository.find_by_id(self._convert_to_task_id(str(dep_id)))
            if dep_task:
                dependency_details.append({
                    "id": str(dep_id),
                    "title": dep_task.title,
                    "status": str(dep_task.status),
                    "priority": str(dep_task.priority)
                })
        
        return {
            "task_id": str(task_id),
            "dependency_ids": task.get_dependency_ids(),
            "dependencies": dependency_details,
            "can_start": task.can_be_started()
        }
    
    def clear_dependencies(self, task_id: Union[str, int]) -> DependencyResponse:
        """Remove all dependencies from a task"""
        task_id_obj = self._convert_to_task_id(task_id)
        task = self._task_repository.find_by_id(task_id_obj)
        
        if not task:
            raise TaskNotFoundError(f"Task {task_id} not found")
        
        dependency_count = len(task.dependencies)
        task.clear_dependencies()
        self._task_repository.save(task)
        
        return DependencyResponse(
            task_id=str(task_id),
            dependencies=[],
            success=True,
            message=f"Cleared {dependency_count} dependencies"
        )
    
    def get_blocking_tasks(self, task_id: Union[str, int]) -> Dict[str, Any]:
        """Get all tasks that are blocked by this task (reverse dependencies)"""
        task_id_obj = self._convert_to_task_id(task_id)
        task = self._task_repository.find_by_id(task_id_obj)
        
        if not task:
            raise TaskNotFoundError(f"Task {task_id} not found")
        
        # Find all tasks that depend on this task
        all_tasks = self._task_repository.find_all()
        blocking_tasks = []
        
        for other_task in all_tasks:
            if other_task.has_dependency(task_id_obj):
                blocking_tasks.append({
                    "id": str(other_task.id),
                    "title": other_task.title,
                    "status": str(other_task.status),
                    "priority": str(other_task.priority)
                })
        
        return {
            "task_id": str(task_id),
            "blocking_tasks": blocking_tasks,
            "blocking_count": len(blocking_tasks)
        } 