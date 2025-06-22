"""
Project analyzer module facade.
Imports all modular project analyzer components.
"""

from .project_analyzer.core_analyzer import ProjectAnalyzer
from .project_analyzer.models import (
    Dependency,
    DependencyType,
    FileInfo,
    FrameworkType,
    ProjectAnalysisConfig,
    ProjectAnalysisResult,
    ProjectMetadata,
    ProjectStructure,
    ProjectType,
)

# Export the main class for backward compatibility
__all__ = [
    "ProjectAnalyzer",
    "ProjectAnalysisResult",
    "ProjectAnalysisConfig",
    "ProjectType",
    "FrameworkType",
    "DependencyType",
    "ProjectStructure",
    "ProjectMetadata",
    "Dependency",
    "FileInfo",
]
