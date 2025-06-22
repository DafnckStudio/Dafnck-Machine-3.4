"""
Project analyzer module facade.
Imports all modular project analyzer components.
"""

from .project_analyzer.core_analyzer import ProjectAnalyzer
from .project_analyzer.models import (
    ProjectAnalysisResult,
    ProjectAnalysisConfig,
    ProjectType,
    FrameworkType,
    DependencyType,
    ProjectStructure,
    ProjectMetadata,
    Dependency,
    FileInfo
)

# Export the main class for backward compatibility
__all__ = [
    'ProjectAnalyzer',
    'ProjectAnalysisResult', 
    'ProjectAnalysisConfig',
    'ProjectType',
    'FrameworkType', 
    'DependencyType',
    'ProjectStructure',
    'ProjectMetadata',
    'Dependency',
    'FileInfo'
] 