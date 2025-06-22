"""Task Data Transfer Objects"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime

from ...domain.enums import AgentRole, CommonLabel, EstimatedEffort, LabelValidator
from ...domain.enums.agent_roles import resolve_legacy_role


@dataclass
class CreateTaskRequest:
    """Request DTO for creating a task"""
    title: str
    description: str
    project_id: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    details: str = ""
    estimated_effort: str = ""
    assignees: List[str] = field(default_factory=list)
    labels: List[str] = None
    due_date: Optional[str] = None
    
    def __post_init__(self):
        if self.labels is None:
            self.labels = []
        
        # Validate and suggest labels using CommonLabel enum
        if self.labels:
            validated_labels = []
            for label in self.labels:
                if LabelValidator.is_valid_label(label):
                    validated_labels.append(label)
                else:
                    # Try to find a close match or suggest alternatives
                    suggestions = CommonLabel.suggest_labels(label)
                    if suggestions:
                        validated_labels.extend(suggestions[:1])  # Take first suggestion
                    else:
                        validated_labels.append(label)  # Keep original if no suggestions
            self.labels = validated_labels
        
        # Validate estimated effort using EstimatedEffort enum
        if self.estimated_effort:
            try:
                EstimatedEffort(self.estimated_effort)
            except ValueError:
                # Try to parse as custom format or use default
                if not self.estimated_effort:
                    self.estimated_effort = "medium"
        
        # Validate assignees using AgentRole enum
        if self.assignees:
            validated_assignees = []
            for assignee in self.assignees:
                if assignee and assignee.strip():
                    # Try to resolve legacy role names
                    resolved_assignee = resolve_legacy_role(assignee)
                    if resolved_assignee:
                        # Ensure resolved assignee has @ prefix
                        if not resolved_assignee.startswith("@"):
                            resolved_assignee = f"@{resolved_assignee}"
                        validated_assignees.append(resolved_assignee)
                    elif AgentRole.is_valid_role(assignee):
                        # Ensure valid agent role has @ prefix
                        if not assignee.startswith("@"):
                            assignee = f"@{assignee}"
                        validated_assignees.append(assignee)
                    elif assignee.startswith("@"):
                        # Already has @ prefix, keep as is
                        validated_assignees.append(assignee)
                    else:
                        # Keep original if not a valid role but not empty
                        validated_assignees.append(assignee)
            self.assignees = validated_assignees


@dataclass
class UpdateTaskRequest:
    """Request DTO for updating a task"""
    task_id: Any
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    details: Optional[str] = None
    estimated_effort: Optional[str] = None
    assignees: Optional[List[str]] = None
    labels: Optional[List[str]] = None
    due_date: Optional[str] = None


@dataclass
class TaskResponse:
    """Response DTO for task operations"""
    id: str
    title: str
    description: str
    status: str
    priority: str
    details: str
    estimated_effort: str
    assignees: List[str]
    labels: List[str]
    dependencies: List[str]
    subtasks: List[Dict[str, Any]]
    due_date: Optional[str]
    created_at: Optional[str]
    updated_at: Optional[str]
    
    @classmethod
    def from_domain(cls, task) -> 'TaskResponse':
        """Create response DTO from domain entity"""
        task_dict = task.to_dict()
        return cls(
            id=task_dict["id"],
            title=task_dict["title"],
            description=task_dict["description"],
            status=task_dict["status"],
            priority=task_dict["priority"],
            details=task_dict["details"],
            estimated_effort=task_dict["estimatedEffort"],
            assignees=task_dict["assignees"],
            labels=task_dict["labels"],
            dependencies=task_dict["dependencies"],
            subtasks=task_dict["subtasks"],
            due_date=task_dict["dueDate"],
            created_at=task_dict["created_at"],
            updated_at=task_dict["updated_at"]
        )


@dataclass
class CreateTaskResponse:
    """Response DTO for create task operations"""
    success: bool
    task: TaskResponse
    message: str = ""
    
    @classmethod
    def success_response(cls, task: TaskResponse, message: str = "Task created successfully") -> 'CreateTaskResponse':
        """Create a successful response"""
        return cls(success=True, task=task, message=message)
    
    @classmethod
    def error_response(cls, message: str, task: Optional[TaskResponse] = None) -> 'CreateTaskResponse':
        """Create an error response"""
        return cls(success=False, task=task, message=message)


@dataclass
class ListTasksRequest:
    """Request DTO for listing tasks"""
    status: Optional[str] = None
    priority: Optional[str] = None
    assignees: Optional[List[str]] = None
    labels: Optional[List[str]] = None
    limit: Optional[int] = None


@dataclass
class SearchTasksRequest:
    """Request DTO for searching tasks"""
    query: str
    limit: int = 10


@dataclass
class TaskListResponse:
    """Response DTO for task list operations"""
    tasks: List[TaskResponse]
    count: int
    
    @classmethod
    def from_domain_list(cls, tasks) -> 'TaskListResponse':
        """Create response DTO from list of domain entities"""
        task_responses = [TaskResponse.from_domain(task) for task in tasks]
        return cls(
            tasks=task_responses,
            count=len(task_responses)
        ) 