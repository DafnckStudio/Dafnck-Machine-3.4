"""Get Task Use Case"""

from typing import Optional, Union

from ...domain import TaskRepository, TaskId, AutoRuleGenerator
from ...domain.exceptions.task_exceptions import TaskNotFoundError, AutoRuleGenerationError
from ...domain.events import TaskRetrieved
from ..dtos.task_dto import TaskResponse
from ...infrastructure.services.agent_doc_generator import generate_agent_docs, generate_docs_for_assignees


class GetTaskUseCase:
    """Use case for retrieving a task and triggering auto rule generation"""
    
    def __init__(self, task_repository: TaskRepository, auto_rule_generator: AutoRuleGenerator):
        self._task_repository = task_repository
        self._auto_rule_generator = auto_rule_generator
    
    def execute(self, task_id: Union[str, int], generate_rules: bool = True, force_full_generation: bool = False) -> TaskResponse:
        """Execute the get task use case"""
        # Convert to domain value object (handle both int and str)
        if isinstance(task_id, int):
            domain_task_id = TaskId.from_int(task_id)
        else:
            domain_task_id = TaskId.from_string(str(task_id))
        
        # Find the task
        task = self._task_repository.find_by_id(domain_task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        
        if generate_rules:
            # Mark task as retrieved (triggers domain event)
            task.mark_as_retrieved()
            
            # Handle domain events (auto rule generation)
            events = task.get_events()
            for event in events:
                if isinstance(event, TaskRetrieved):
                    try:
                        # Generate auto rules for the retrieved task
                        self._auto_rule_generator.generate_rules_for_task(
                            task,
                            force_full_generation=force_full_generation
                        )
                        # Generate agent documentation for all unique assignees
                        generate_docs_for_assignees(task.assignees, clear_all=False)
                    except Exception as e:
                        raise AutoRuleGenerationError(
                            f"Error during auto rule generation: {e}",
                            original_exception=e
                        )
        
        # Convert to response DTO
        return TaskResponse.from_domain(task) 