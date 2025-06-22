"""
Legacy services migrated from the old modules system.
These are preserved to maintain auto rule generation functionality.
"""

from .models import AgentRole, TaskContext
from .project_analyzer import ProjectAnalyzer
from .role_manager import RoleManager
from .rules_generator import RulesGenerator

__all__ = [
    "TaskContext",
    "AgentRole",
    "RulesGenerator",
    "RoleManager",
    "ProjectAnalyzer",
]
