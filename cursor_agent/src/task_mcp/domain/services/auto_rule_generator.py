"""Auto Rule Generator Domain Service Interface"""

from abc import ABC, abstractmethod
from typing import Any, Dict

from ..entities.task import Task


class AutoRuleGenerator(ABC):
    """Domain service interface for generating auto rules"""

    @abstractmethod
    def generate_rules_for_task(
        self, task: Task, force_full_generation: bool = False
    ) -> bool:
        """
        Generate auto_rule.mdc file for the given task.

        :param task: The task entity to generate rules for.
        :param force_full_generation: If True, bypasses environment checks and forces full generation.
        """

    @abstractmethod
    def generate_completion_context(self, task: Task) -> bool:
        """
        Generate or update context file when a task is completed.
        Creates an AI-driven completion summary with achievements, lessons learned, and next steps.

        :param task: The completed task entity to generate context for.
        :return: True if context was generated successfully, False otherwise.
        """

    @abstractmethod
    def generate_subtask_completion_context(self, task: Task, subtask_id: str) -> bool:
        """
        Generate or update context file when a subtask is completed.
        Updates the task's context file with subtask completion progress and insights.

        :param task: The task entity containing the completed subtask.
        :param subtask_id: The ID of the completed subtask.
        :return: True if context was updated successfully, False otherwise.
        """

    @abstractmethod
    def validate_task_data(self, task_data: Dict[str, Any]) -> bool:
        """Validate task data for rule generation"""

    @abstractmethod
    def get_supported_roles(self) -> list[str]:
        """Get list of supported roles for rule generation"""
