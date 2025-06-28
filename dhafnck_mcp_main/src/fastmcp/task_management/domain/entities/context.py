"""Context Domain Entities"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
from pathlib import Path


@dataclass
class ContextMetadata:
    """Context metadata structure"""
    task_id: str
    project_id: str
    task_tree_id: str = "main"
    user_id: str = "default_id"
    status: str = "todo"
    priority: str = "medium"
    assignees: List[str] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    version: str = "1.0"


@dataclass
class ContextObjective:
    """Task objective and description"""
    title: str
    description: str = ""
    estimated_effort: str = "medium"
    due_date: Optional[str] = None


@dataclass
class ContextRequirement:
    """Individual requirement item"""
    id: str
    title: str
    completed: bool = False
    priority: str = "medium"
    notes: str = ""


@dataclass
class ContextRequirements:
    """Requirements section"""
    checklist: List[ContextRequirement] = field(default_factory=list)
    custom_requirements: List[str] = field(default_factory=list)
    completion_criteria: List[str] = field(default_factory=list)


@dataclass
class ContextTechnical:
    """Technical details section"""
    technologies: List[str] = field(default_factory=list)
    frameworks: List[str] = field(default_factory=list)
    key_files: List[str] = field(default_factory=list)
    key_directories: List[str] = field(default_factory=list)
    architecture_notes: str = ""
    patterns_used: List[str] = field(default_factory=list)


@dataclass
class ContextDependency:
    """Dependency information"""
    task_id: str
    title: str = ""
    status: str = "unknown"
    blocking_reason: str = ""


@dataclass
class ContextDependencies:
    """Dependencies section"""
    task_dependencies: List[ContextDependency] = field(default_factory=list)
    external_dependencies: List[str] = field(default_factory=list)
    blocked_by: List[str] = field(default_factory=list)


@dataclass
class ContextProgressAction:
    """Individual progress action"""
    timestamp: str
    action: str
    agent: str
    details: str = ""
    status: str = "completed"


@dataclass
class ContextProgress:
    """Progress tracking section"""
    completed_actions: List[ContextProgressAction] = field(default_factory=list)
    current_session_summary: str = ""
    next_steps: List[str] = field(default_factory=list)
    completion_percentage: float = 0.0
    time_spent_minutes: int = 0


@dataclass
class ContextInsight:
    """Agent insight or note"""
    timestamp: str
    agent: str
    category: str  # "insight", "challenge", "solution", "decision"
    content: str
    importance: str = "medium"  # "low", "medium", "high", "critical"


@dataclass
class ContextNotes:
    """Context notes and insights"""
    agent_insights: List[ContextInsight] = field(default_factory=list)
    challenges_encountered: List[ContextInsight] = field(default_factory=list)
    solutions_applied: List[ContextInsight] = field(default_factory=list)
    decisions_made: List[ContextInsight] = field(default_factory=list)
    general_notes: str = ""


@dataclass
class ContextSubtask:
    """Subtask information"""
    id: str
    title: str
    description: str = ""
    status: str = "todo"
    assignee: str = ""
    completed: bool = False
    progress_notes: str = ""


@dataclass
class ContextSubtasks:
    """Subtasks section"""
    items: List[ContextSubtask] = field(default_factory=list)
    total_count: int = 0
    completed_count: int = 0
    progress_percentage: float = 0.0


@dataclass
class ContextCustomSection:
    """Custom extensible section"""
    name: str
    data: Dict[str, Any] = field(default_factory=dict)
    schema_version: str = "1.0"


@dataclass
class TaskContext:
    """Complete task context structure"""
    metadata: ContextMetadata
    objective: ContextObjective
    requirements: ContextRequirements = field(default_factory=ContextRequirements)
    technical: ContextTechnical = field(default_factory=ContextTechnical)
    dependencies: ContextDependencies = field(default_factory=ContextDependencies)
    progress: ContextProgress = field(default_factory=ContextProgress)
    subtasks: ContextSubtasks = field(default_factory=ContextSubtasks)
    notes: ContextNotes = field(default_factory=ContextNotes)
    custom_sections: List[ContextCustomSection] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for JSON serialization"""
        def convert_dataclass(obj):
            if hasattr(obj, '__dataclass_fields__'):
                return {k: convert_dataclass(v) for k, v in obj.__dict__.items()}
            elif isinstance(obj, list):
                return [convert_dataclass(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: convert_dataclass(v) for k, v in obj.items()}
            else:
                return obj
        
        return convert_dataclass(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TaskContext':
        """Create TaskContext from dictionary"""
        # This would implement the reverse conversion
        # For now, returning a basic implementation
        metadata = ContextMetadata(**data.get('metadata', {}))
        objective = ContextObjective(**data.get('objective', {}))
        
        context = cls(metadata=metadata, objective=objective)
        
        # Load other sections if present
        if 'requirements' in data:
            context.requirements = ContextRequirements(**data['requirements'])
        if 'technical' in data:
            context.technical = ContextTechnical(**data['technical'])
        if 'dependencies' in data:
            context.dependencies = ContextDependencies(**data['dependencies'])
        if 'progress' in data:
            context.progress = ContextProgress(**data['progress'])
        if 'subtasks' in data:
            context.subtasks = ContextSubtasks(**data['subtasks'])
        if 'notes' in data:
            context.notes = ContextNotes(**data['notes'])
        if 'custom_sections' in data:
            context.custom_sections = [ContextCustomSection(**section) for section in data['custom_sections']]
        
        return context


class ContextSchema:
    """Context schema management and validation"""
    
    SCHEMA_VERSION = "1.0"
    
    @staticmethod
    def get_default_schema() -> Dict[str, Any]:
        """Get the default context JSON schema"""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "title": "Task Context Schema",
            "description": "Schema for task context JSON files",
            "version": ContextSchema.SCHEMA_VERSION,
            "required": ["metadata", "objective"],
            "properties": {
                "metadata": {
                    "type": "object",
                    "required": ["task_id", "project_id"],
                    "properties": {
                        "task_id": {"type": "string"},
                        "project_id": {"type": "string"},
                        "task_tree_id": {"type": "string", "default": "main"},
                        "user_id": {"type": "string", "default": "default_id"},
                        "status": {"type": "string", "enum": ["todo", "in_progress", "blocked", "review", "testing", "done", "cancelled"]},
                        "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent", "critical"]},
                        "assignees": {"type": "array", "items": {"type": "string"}},
                        "labels": {"type": "array", "items": {"type": "string"}},
                        "created_at": {"type": "string", "format": "date-time"},
                        "updated_at": {"type": "string", "format": "date-time"},
                        "version": {"type": "string", "default": "1.0"}
                    }
                },
                "objective": {
                    "type": "object",
                    "required": ["title"],
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "estimated_effort": {"type": "string", "enum": ["quick", "short", "small", "medium", "large", "xlarge", "epic", "massive"]},
                        "due_date": {"type": ["string", "null"], "format": "date"}
                    }
                },
                "requirements": {
                    "type": "object",
                    "properties": {
                        "checklist": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["id", "title"],
                                "properties": {
                                    "id": {"type": "string"},
                                    "title": {"type": "string"},
                                    "completed": {"type": "boolean", "default": False},
                                    "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                                    "notes": {"type": "string"}
                                }
                            }
                        },
                        "custom_requirements": {"type": "array", "items": {"type": "string"}},
                        "completion_criteria": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "technical": {
                    "type": "object",
                    "properties": {
                        "technologies": {"type": "array", "items": {"type": "string"}},
                        "frameworks": {"type": "array", "items": {"type": "string"}},
                        "key_files": {"type": "array", "items": {"type": "string"}},
                        "key_directories": {"type": "array", "items": {"type": "string"}},
                        "architecture_notes": {"type": "string"},
                        "patterns_used": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "dependencies": {
                    "type": "object",
                    "properties": {
                        "task_dependencies": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["task_id"],
                                "properties": {
                                    "task_id": {"type": "string"},
                                    "title": {"type": "string"},
                                    "status": {"type": "string"},
                                    "blocking_reason": {"type": "string"}
                                }
                            }
                        },
                        "external_dependencies": {"type": "array", "items": {"type": "string"}},
                        "blocked_by": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "progress": {
                    "type": "object",
                    "properties": {
                        "completed_actions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["timestamp", "action", "agent"],
                                "properties": {
                                    "timestamp": {"type": "string", "format": "date-time"},
                                    "action": {"type": "string"},
                                    "agent": {"type": "string"},
                                    "details": {"type": "string"},
                                    "status": {"type": "string", "enum": ["completed", "in_progress", "failed"]}
                                }
                            }
                        },
                        "current_session_summary": {"type": "string"},
                        "next_steps": {"type": "array", "items": {"type": "string"}},
                        "completion_percentage": {"type": "number", "minimum": 0, "maximum": 100},
                        "time_spent_minutes": {"type": "integer", "minimum": 0}
                    }
                },
                "subtasks": {
                    "type": "object",
                    "properties": {
                        "items": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["id", "title"],
                                "properties": {
                                    "id": {"type": "string"},
                                    "title": {"type": "string"},
                                    "description": {"type": "string"},
                                    "status": {"type": "string", "enum": ["todo", "in_progress", "done", "cancelled"]},
                                    "assignee": {"type": "string"},
                                    "completed": {"type": "boolean"},
                                    "progress_notes": {"type": "string"}
                                }
                            }
                        },
                        "total_count": {"type": "integer", "minimum": 0},
                        "completed_count": {"type": "integer", "minimum": 0},
                        "progress_percentage": {"type": "number", "minimum": 0, "maximum": 100}
                    }
                },
                "notes": {
                    "type": "object",
                    "properties": {
                        "agent_insights": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["timestamp", "agent", "category", "content"],
                                "properties": {
                                    "timestamp": {"type": "string", "format": "date-time"},
                                    "agent": {"type": "string"},
                                    "category": {"type": "string", "enum": ["insight", "challenge", "solution", "decision"]},
                                    "content": {"type": "string"},
                                    "importance": {"type": "string", "enum": ["low", "medium", "high", "critical"]}
                                }
                            }
                        },
                        "challenges_encountered": {"type": "array", "items": {"$ref": "#/properties/notes/properties/agent_insights/items"}},
                        "solutions_applied": {"type": "array", "items": {"$ref": "#/properties/notes/properties/agent_insights/items"}},
                        "decisions_made": {"type": "array", "items": {"$ref": "#/properties/notes/properties/agent_insights/items"}},
                        "general_notes": {"type": "string"}
                    }
                },
                "custom_sections": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["name"],
                        "properties": {
                            "name": {"type": "string"},
                            "data": {"type": "object"},
                            "schema_version": {"type": "string", "default": "1.0"}
                        }
                    }
                }
            }
        }
    
    @staticmethod
    def validate_context(context_data: Dict[str, Any]) -> tuple[bool, List[str]]:
        """Validate context data against schema"""
        errors = []
        
        # Basic validation
        if not isinstance(context_data, dict):
            errors.append("Context data must be a dictionary")
            return False, errors
        
        # Check required fields
        if 'metadata' not in context_data:
            errors.append("Missing required field: metadata")
        if 'objective' not in context_data:
            errors.append("Missing required field: objective")
        
        # Validate metadata
        if 'metadata' in context_data:
            metadata = context_data['metadata']
            if 'task_id' not in metadata:
                errors.append("Missing required field: metadata.task_id")
            if 'project_id' not in metadata:
                errors.append("Missing required field: metadata.project_id")
        
        # Validate objective
        if 'objective' in context_data:
            objective = context_data['objective']
            if 'title' not in objective:
                errors.append("Missing required field: objective.title")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def create_empty_context(task_id: str, project_id: str, title: str, **kwargs) -> TaskContext:
        """Create an empty context with minimal required fields"""
        metadata = ContextMetadata(
            task_id=task_id,
            project_id=project_id,
            task_tree_id=kwargs.get('task_tree_id', 'main'),
            user_id=kwargs.get('user_id', 'default_id'),
            status=kwargs.get('status', 'todo'),
            priority=kwargs.get('priority', 'medium'),
            assignees=kwargs.get('assignees', []),
            labels=kwargs.get('labels', [])
        )
        
        objective = ContextObjective(
            title=title,
            description=kwargs.get('description', ''),
            estimated_effort=kwargs.get('estimated_effort', 'medium'),
            due_date=kwargs.get('due_date')
        )
        
        return TaskContext(metadata=metadata, objective=objective) 