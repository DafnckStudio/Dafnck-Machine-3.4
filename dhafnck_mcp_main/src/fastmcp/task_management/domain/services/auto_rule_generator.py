"""Auto Rule Generator Domain Service Interface"""

from abc import ABC, abstractmethod
from typing import Dict, Any

from ..entities.task import Task


class AutoRuleGenerator(ABC):
    """Domain service interface for generating auto rules"""
    
    @abstractmethod
    def generate_rules_for_task(self, task: Task, force_full_generation: bool = False) -> bool:
        """
        Generate auto_rule.mdc file for the given task.

        :param task: The task entity to generate rules for.
        :param force_full_generation: If True, bypasses environment checks and forces full generation.
        """
        pass
    
    @abstractmethod
    def validate_task_data(self, task_data: Dict[str, Any]) -> bool:
        """Validate task data for rule generation"""
        pass
    
    @abstractmethod
    def get_supported_roles(self) -> list[str]:
        """Get list of supported roles for rule generation"""
        pass 