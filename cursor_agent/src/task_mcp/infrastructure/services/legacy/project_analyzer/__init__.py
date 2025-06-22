"""
Project analyzer module exports.
Provides modular project analysis functionality.
"""

from .context_generator import ContextGenerator
from .core_analyzer import ProjectAnalyzer
from .dependency_analyzer import DependencyAnalyzer
from .file_operations import FileOperations
from .models import (
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
from .pattern_detector import PatternDetector
from .structure_analyzer import StructureAnalyzer

__all__ = [
    "ProjectAnalyzer",
    "StructureAnalyzer",
    "PatternDetector",
    "DependencyAnalyzer",
    "ContextGenerator",
    "FileOperations",
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
