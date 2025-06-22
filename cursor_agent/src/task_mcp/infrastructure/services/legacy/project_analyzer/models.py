"""
Basic models for project analysis functionality.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class ProjectType(Enum):
    """Types of projects"""

    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    UNKNOWN = "unknown"


class FrameworkType(Enum):
    """Framework types"""

    FASTAPI = "fastapi"
    FLASK = "flask"
    DJANGO = "django"
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    UNKNOWN = "unknown"


class DependencyType(Enum):
    """Dependency types"""

    PRODUCTION = "production"
    DEVELOPMENT = "development"
    OPTIONAL = "optional"


@dataclass
class Dependency:
    """Project dependency information"""

    name: str
    version: str
    type: DependencyType
    description: Optional[str] = None


@dataclass
class FileInfo:
    """File information"""

    path: str
    size: int
    type: str
    last_modified: Optional[str] = None


@dataclass
class ProjectStructure:
    """Project structure information"""

    root_path: str
    directories: List[str]
    files: List[FileInfo]
    total_files: int
    total_size: int


@dataclass
class ProjectMetadata:
    """Project metadata"""

    name: str
    version: Optional[str]
    description: Optional[str]
    author: Optional[str]
    license: Optional[str]


@dataclass
class ProjectAnalysisConfig:
    """Configuration for project analysis"""

    include_hidden: bool = False
    max_depth: int = 10
    exclude_patterns: List[str] = None

    def __post_init__(self):
        if self.exclude_patterns is None:
            self.exclude_patterns = [
                "__pycache__",
                ".git",
                "node_modules",
                ".venv",
                "venv",
            ]


@dataclass
class ProjectAnalysisResult:
    """Result of project analysis"""

    project_type: ProjectType
    framework_type: FrameworkType
    structure: ProjectStructure
    metadata: ProjectMetadata
    dependencies: List[Dependency]
    patterns: Dict[str, Any]
    context: Dict[str, Any]
