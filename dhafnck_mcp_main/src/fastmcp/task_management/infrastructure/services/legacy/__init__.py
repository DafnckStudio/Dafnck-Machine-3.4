"""
Legacy services migrated from the old modules system.
These are preserved to maintain auto rule generation functionality.
"""

from .models import TaskContext, AgentRole
from .rules_generator import RulesGenerator
from .role_manager import RoleManager
from .project_analyzer import ProjectAnalyzer

__all__ = [
    "TaskContext",
    "AgentRole", 
    "RulesGenerator",
    "RoleManager",
    "ProjectAnalyzer"
] 