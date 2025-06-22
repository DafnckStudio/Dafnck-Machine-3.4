"""
Data models for the Cursor Agent system.
Contains dataclasses for task context, agent roles, and validation results.
"""

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Dict, List, Literal, Optional


@dataclass
class ValidationResult:
    """Result of input validation"""

    is_valid: bool
    errors: List[str]
    warnings: List[str]

    def add_error(self, error: str):
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str):
        self.warnings.append(warning)


@dataclass
class TaskProgressInfo:
    """Enhanced progress tracking for tasks"""

    current_phase_index: int
    total_phases: int
    completion_percentage: float
    estimated_completion: Optional[str]

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TaskContext:
    """Context for current development task"""

    id: str
    title: str
    description: str
    requirements: List[str]
    current_phase: Literal["planning", "coding", "testing", "review", "completed"]
    assigned_roles: List[str]
    primary_role: str
    context_data: Dict
    created_at: datetime
    updated_at: datetime
    progress: TaskProgressInfo

    def to_dict(self) -> Dict:
        result = asdict(self)
        # Convert datetime objects to ISO strings for JSON serialization
        result["created_at"] = self.created_at.isoformat()
        result["updated_at"] = self.updated_at.isoformat()
        return result


@dataclass
class AgentRole:
    """Definition of an agent role with specific rules and context"""

    name: str
    persona: str
    primary_focus: str
    rules: List[str]
    context_instructions: List[str]
    tools_guidance: List[str]
    output_format: str


@dataclass
class SubtaskInfo:
    """Information about a subtask from tasks.json"""

    id: str
    title: str
    description: str
    status: str
    dependencies: List[str]
    priority: str
    details: str
    test_strategy: str
    estimated_effort: str
    subtasks: List["SubtaskInfo"]

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TaskInfo:
    """Information about a task from tasks.json"""

    id: int
    title: str
    description: str
    status: str
    dependencies: List[int]
    priority: str
    details: str
    test_strategy: str
    estimated_effort: str
    actual_effort: Optional[str]
    assignee: str
    labels: List[str]
    due_date: str
    code_context_paths: List[str]
    complexity_score: int
    recommended_subtasks: int
    subtasks: List[SubtaskInfo]

    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class TaskProgress:
    """Tracks current task and subtask progress"""

    current_task_id: Optional[int]
    current_subtask_id: Optional[str]
    task_start_time: Optional[str]
    subtask_start_time: Optional[str]
    completed_tasks: List[int]
    completed_subtasks: List[str]
    last_updated: str

    def to_dict(self) -> Dict:
        return asdict(self)
