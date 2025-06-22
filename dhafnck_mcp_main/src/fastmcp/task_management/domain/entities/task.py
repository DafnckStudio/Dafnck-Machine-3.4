"""Task Domain Entity"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any, Union

from ..value_objects.task_id import TaskId
from ..value_objects.task_status import TaskStatus
from ..value_objects.priority import Priority
from ..enums.estimated_effort import EstimatedEffort, EffortLevel
from ..enums.agent_roles import AgentRole, resolve_legacy_role
from ..enums.common_labels import CommonLabel, LabelValidator
from ..events.task_events import TaskCreated, TaskUpdated, TaskDeleted, TaskRetrieved


@dataclass
class Task:
    """Task domain entity with business logic"""
    
    id: TaskId
    title: str
    description: str
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None
    project_id: Optional[str] = None
    details: str = ""
    estimated_effort: str = ""
    assignees: List[str] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    dependencies: List[TaskId] = field(default_factory=list)
    subtasks: List[Dict[str, Any]] = field(default_factory=list)
    due_date: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Domain events
    _events: List[Any] = field(default_factory=list, init=False)
    
    def __post_init__(self):
        """Validate task data after initialization"""
        # Set default values if not provided
        if self.status is None:
            self.status = TaskStatus.todo()
        if self.priority is None:
            self.priority = Priority.medium()
        if self.assignees is None:
            self.assignees = []
        if self.labels is None:
            self.labels = []
            
        self._validate()
        
        # Set timestamps if not provided (ensure timezone-aware)
        # For new tasks, both timestamps should be identical
        if self.created_at is None and self.updated_at is None:
            now = datetime.now(timezone.utc)
            self.created_at = now
            self.updated_at = now
        else:
            # Handle existing timestamps separately
            if self.created_at is None:
                self.created_at = datetime.now(timezone.utc)
            elif self.created_at.tzinfo is None:
                self.created_at = self.created_at.replace(tzinfo=timezone.utc)
                
            if self.updated_at is None:
                self.updated_at = datetime.now(timezone.utc)
            elif self.updated_at.tzinfo is None:
                self.updated_at = self.updated_at.replace(tzinfo=timezone.utc)
    
    def __eq__(self, other):
        """Tasks are equal if they have the same ID"""
        if not isinstance(other, Task):
            return False
        return self.id == other.id
    
    def __hash__(self):
        """Hash based on task ID for use in sets and dictionaries"""
        return hash(self.id.value)
    
    # Properties for backward compatibility and convenience
    @property
    def is_blocked(self) -> bool:
        """Check if task is blocked"""
        return self.status.value == 'blocked'
    
    @property
    def is_completed(self) -> bool:
        """Check if task is completed"""
        return self.status.is_completed()
    
    @property
    def can_be_assigned(self) -> bool:
        """Check if task can be assigned (not completed or cancelled)"""
        return self.status.value not in ['done', 'cancelled']
    
    def _validate(self):
        """Validate task business rules"""
        if not self.title or not self.title.strip():
            raise ValueError("Task title cannot be empty")
        
        if not self.description or not self.description.strip():
            raise ValueError("Task description cannot be empty")
        
        if len(self.title) > 200:
            raise ValueError("Task title cannot exceed 200 characters")
        
        if len(self.description) > 1000:
            raise ValueError("Task description cannot exceed 1000 characters")
    
    def update_status(self, new_status: TaskStatus) -> None:
        """Update task status with validation"""
        if not self.status.can_transition_to(new_status.value):
            raise ValueError(f"Cannot transition from {self.status} to {new_status}")
        
        old_status = self.status
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)
        
        # Raise domain event
        self._events.append(TaskUpdated(
            task_id=self.id,
            field_name="status",
            old_value=str(old_status),
            new_value=str(new_status),
            updated_at=self.updated_at
        ))
    
    def update_priority(self, new_priority: Priority) -> None:
        """Update task priority"""
        old_priority = self.priority
        self.priority = new_priority
        self.updated_at = datetime.now(timezone.utc)
        
        # Raise domain event
        self._events.append(TaskUpdated(
            task_id=self.id,
            field_name="priority",
            old_value=str(old_priority),
            new_value=str(new_priority),
            updated_at=self.updated_at
        ))
    
    def update_title(self, title: str) -> None:
        """Update task title"""
        if not title.strip():
            raise ValueError("Task title cannot be empty")
        
        old_title = self.title
        self.title = title
        self.updated_at = datetime.now(timezone.utc)
        
        # Raise domain event
        self._events.append(TaskUpdated(
            task_id=self.id,
            field_name="title",
            old_value=old_title,
            new_value=title,
            updated_at=self.updated_at
        ))
    
    def update_description(self, description: str) -> None:
        """Update task description"""
        if not description.strip():
            raise ValueError("Task description cannot be empty")
        
        old_description = self.description
        self.description = description
        self.updated_at = datetime.now(timezone.utc)
        
        # Raise domain event
        self._events.append(TaskUpdated(
            task_id=self.id,
            field_name="description",
            old_value=old_description,
            new_value=description,
            updated_at=self.updated_at
        ))
    
    def update_details(self, details: str) -> None:
        """Update task details"""
        old_details = self.details
        self.details = details
        self.updated_at = datetime.now(timezone.utc)
        
        # Raise domain event
        self._events.append(TaskUpdated(
            task_id=self.id,
            field_name="details",
            old_value=old_details,
            new_value=details,
            updated_at=self.updated_at
        ))
    
    def update_estimated_effort(self, estimated_effort: str) -> None:
        """Update task estimated effort with enum validation"""
        # Validate estimated effort using EstimatedEffort enum
        try:
            EstimatedEffort(estimated_effort)
        except ValueError:
            # Use default if invalid
            estimated_effort = EffortLevel.MEDIUM.label
        
        old_effort = self.estimated_effort
        self.estimated_effort = estimated_effort
        self.updated_at = datetime.now(timezone.utc)
        
        # Raise domain event
        self._events.append(TaskUpdated(
            task_id=self.id,
            field_name="estimated_effort",
            old_value=old_effort,
            new_value=estimated_effort,
            updated_at=self.updated_at
        ))
    
    def update_assignees(self, assignees: List[str]) -> None:
        """Update task assignees"""
        # Debug: Log incoming assignees
        logging.debug(f"[update_assignees] Incoming assignees: {assignees}")
        # Validate assignees using AgentRole enum
        validated_assignees = []
        for assignee in assignees:
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
        # Debug: Log validated assignees
        logging.debug(f"[update_assignees] Validated assignees: {validated_assignees}")
        old_assignees = self.assignees.copy()
        self.assignees = validated_assignees
        self.updated_at = datetime.now(timezone.utc)
        # Raise domain event
        self._events.append(TaskUpdated(
            task_id=self.id,
            field_name="assignees",
            old_value=old_assignees,
            new_value=validated_assignees,
            updated_at=self.updated_at
        ))
    
    def add_assignee(self, assignee: Union[str, AgentRole]) -> None:
        """Add an assignee to the task"""
        # Handle both string and AgentRole enum inputs
        if isinstance(assignee, AgentRole):
            assignee_str = f"@{assignee.value}"
        else:
            assignee_str = str(assignee)
        
        if not assignee_str or not assignee_str.strip():
            return
        
        # Validate assignee using AgentRole enum
        validated_assignee = assignee_str
        resolved_assignee = resolve_legacy_role(assignee_str)
        if resolved_assignee:
            # Ensure resolved assignee has @ prefix
            if not resolved_assignee.startswith("@"):
                resolved_assignee = f"@{resolved_assignee}"
            validated_assignee = resolved_assignee
        elif AgentRole.is_valid_role(assignee_str):
            # Ensure valid agent role has @ prefix
            if not assignee_str.startswith("@"):
                assignee_str = f"@{assignee_str}"
            validated_assignee = assignee_str
        elif assignee_str.startswith("@"):
            # Already has @ prefix, keep as is
            validated_assignee = assignee_str
        else:
            # Keep original if not a valid role but not empty
            pass
        
        if validated_assignee not in self.assignees:
            self.assignees.append(validated_assignee)
            self.updated_at = datetime.now(timezone.utc)
            
            # Raise domain event
            self._events.append(TaskUpdated(
                task_id=self.id,
                field_name="assignees",
                old_value="assignee_added",
                new_value=validated_assignee,
                updated_at=self.updated_at
            ))
    
    def remove_assignee(self, assignee: Union[str, AgentRole]) -> None:
        """Remove an assignee from the task"""
        # Handle both string and AgentRole enum inputs
        if isinstance(assignee, AgentRole):
            assignee_str = f"@{assignee.value}"
        else:
            assignee_str = str(assignee)
        
        if assignee_str in self.assignees:
            self.assignees.remove(assignee_str)
            self.updated_at = datetime.now(timezone.utc)
            
            # Raise domain event
            self._events.append(TaskUpdated(
                task_id=self.id,
                field_name="assignees",
                old_value="assignee_removed",
                new_value=assignee_str,
                updated_at=self.updated_at
            ))
    
    def has_assignee(self, assignee: str) -> bool:
        """Check if task has a specific assignee"""
        return assignee in self.assignees
    
    def get_primary_assignee(self) -> Optional[str]:
        """Get the primary (first) assignee"""
        return self.assignees[0] if self.assignees else None
    
    def get_assignees_count(self) -> int:
        """Get the number of assignees"""
        return len(self.assignees)
    
    def is_multi_assignee(self) -> bool:
        """Check if task has multiple assignees"""
        return len(self.assignees) > 1
    
    def get_assignees_info(self) -> List[Dict[str, Any]]:
        """Get role information for all assignees"""
        assignees_info = []
        
        for assignee in self.assignees:
            if not assignee:
                continue
            
            try:
                # Try to get role from AgentRole enum
                role = AgentRole.get_role_by_slug(assignee)
                if role:
                    from ..enums.agent_roles import get_role_metadata_from_yaml
                    metadata = get_role_metadata_from_yaml(role)
                    assignees_info.append({
                        "role": role.value,
                        "display_name": role.display_name,
                        "folder_name": role.folder_name,
                        "metadata": metadata
                    })
                else:
                    # Return basic info for non-enum assignees
                    assignees_info.append({
                        "role": assignee,
                        "display_name": assignee.replace("-", " ").replace("_", " ").title(),
                        "folder_name": assignee.replace("-", "_"),
                        "metadata": None
                    })
            except Exception:
                # Fallback for any errors
                assignees_info.append({
                    "role": assignee,
                    "display_name": assignee,
                    "folder_name": assignee,
                    "metadata": None
                })
        
        return assignees_info
    
    def update_labels(self, labels: List[str]) -> None:
        """Update task labels with enum validation"""
        # Validate labels using CommonLabel enum
        validated_labels = []
        for label in labels:
            if LabelValidator.is_valid_label(label):
                validated_labels.append(label)
            else:
                # Try to find a close match or suggest alternatives
                suggestions = CommonLabel.suggest_labels(label)
                if suggestions:
                    validated_labels.extend(suggestions[:1])  # Take first suggestion
                else:
                    validated_labels.append(label)  # Keep original if no suggestions
        
        old_labels = self.labels.copy()
        self.labels = validated_labels
        self.updated_at = datetime.now(timezone.utc)
        
        # Raise domain event
        self._events.append(TaskUpdated(
            task_id=self.id,
            field_name="labels",
            old_value=old_labels,
            new_value=validated_labels,
            updated_at=self.updated_at
        ))
    
    def update_due_date(self, due_date: Optional[str]) -> None:
        """Update task due date"""
        old_due_date = self.due_date
        self.due_date = due_date
        self.updated_at = datetime.now(timezone.utc)
        
        # Raise domain event
        self._events.append(TaskUpdated(
            task_id=self.id,
            field_name="due_date",
            old_value=old_due_date,
            new_value=due_date,
            updated_at=self.updated_at
        ))
    
    def mark_as_deleted(self) -> None:
        """Mark task as deleted (triggers domain event)"""
        self._events.append(TaskDeleted(
            task_id=self.id,
            title=self.title,
            deleted_at=datetime.now(timezone.utc)
        ))

    def update_details_legacy(self, title: Optional[str] = None, description: Optional[str] = None, 
                      details: Optional[str] = None, assignees: Optional[List[str]] = None) -> None:
        """Update task details"""
        changes = {}
        
        if title is not None and title != self.title:
            if not title.strip():
                raise ValueError("Task title cannot be empty")
            changes["title"] = (self.title, title)
            self.title = title
        
        if description is not None and description != self.description:
            if not description.strip():
                raise ValueError("Task description cannot be empty")
            changes["description"] = (self.description, description)
            self.description = description
        
        if details is not None and details != self.details:
            changes["details"] = (self.details, details)
            self.details = details
        
        if assignees is not None and assignees != self.assignees:
            changes["assignees"] = (self.assignees, assignees)
            self.assignees = assignees
        
        if changes:
            self.updated_at = datetime.now(timezone.utc)
            
            # Raise domain events for each change
            for field_name, (old_value, new_value) in changes.items():
                self._events.append(TaskUpdated(
                    task_id=self.id,
                    field_name=field_name,
                    old_value=old_value,
                    new_value=new_value,
                    updated_at=self.updated_at
                ))
    
    def add_dependency(self, dependency_id: TaskId) -> None:
        """Add a task dependency"""
        if dependency_id == self.id:
            raise ValueError("Task cannot depend on itself")
        
        # Handle both TaskId objects and string values when checking for duplicates
        existing_deps = [dep.value if hasattr(dep, 'value') else str(dep) for dep in self.dependencies]
        if dependency_id.value not in existing_deps:
            self.dependencies.append(dependency_id)
            self.updated_at = datetime.now(timezone.utc)
    
    def remove_dependency(self, dependency_id: TaskId) -> None:
        """Remove a task dependency"""
        # Find and remove dependency by value comparison
        for i, dep in enumerate(self.dependencies):
            # Handle both TaskId objects and string values
            dep_value = dep.value if hasattr(dep, 'value') else str(dep)
            if dep_value == dependency_id.value:
                self.dependencies.pop(i)
                self.updated_at = datetime.now(timezone.utc)
                break
    
    def has_dependency(self, dependency_id: TaskId) -> bool:
        """Check if task has a specific dependency"""
        # Handle both TaskId objects and string values
        return dependency_id.value in [dep.value if hasattr(dep, 'value') else str(dep) for dep in self.dependencies]
    
    def get_dependency_ids(self) -> List[str]:
        """Get list of dependency IDs as strings"""
        # Handle both TaskId objects and string values
        return [dep.value if hasattr(dep, 'value') else str(dep) for dep in self.dependencies]
    
    def clear_dependencies(self) -> None:
        """Remove all dependencies"""
        if self.dependencies:
            self.dependencies.clear()
            self.updated_at = datetime.now(timezone.utc)
    
    def has_circular_dependency(self, new_dependency_id: TaskId) -> bool:
        """Check if adding a dependency would create a circular reference"""
        # This is a simplified check - in a real system you'd need to traverse the full dependency graph
        if new_dependency_id == self.id:
            return True
        
        # Check if new dependency is already in our dependencies (would create immediate cycle)
        if self.has_dependency(new_dependency_id):
            return True
            
        # For now, assume no circular dependencies beyond immediate self-reference
        # In a full implementation, you'd need to check the entire dependency graph
        return False
    
    def add_label(self, label: Union[str, CommonLabel]) -> None:
        """Add a label to the task with enum validation"""
        # Handle both string and CommonLabel enum inputs
        if isinstance(label, CommonLabel):
            label_str = label.value
        else:
            label_str = str(label)
        
        if not label_str:
            return
        
        # Validate label using CommonLabel enum
        valid_label = label_str
        if not LabelValidator.is_valid_label(label_str):
            # Try to find a close match
            suggestions = CommonLabel.suggest_labels(label_str)
            if suggestions:
                valid_label = suggestions[0]  # Use first suggestion
        
        if valid_label not in self.labels:
            self.labels.append(valid_label)
            self.updated_at = datetime.now(timezone.utc)
    
    def remove_label(self, label: Union[str, CommonLabel]) -> None:
        """Remove a label from the task"""
        # Handle both string and CommonLabel enum inputs
        if isinstance(label, CommonLabel):
            label_str = label.value
        else:
            label_str = str(label)
        
        if label_str in self.labels:
            self.labels.remove(label_str)
            self.updated_at = datetime.now(timezone.utc)
    
    def add_subtask(self, subtask_title: str = None, title: str = None, description: str = None, 
                   assignee: str = None, estimated_effort: str = None, **kwargs) -> str:
        """Add a subtask to the task with flexible parameter support"""
        # Handle dictionary input (test compatibility)
        if isinstance(subtask_title, dict):
            # Dictionary style: add_subtask({"title": "title", "completed": True})
            subtask_data = subtask_title.copy()
        elif subtask_title is not None and title is None and isinstance(subtask_title, str):
            # Old style: add_subtask("title")
            subtask_data = {"title": subtask_title}
        elif title is not None:
            # New style: add_subtask(title="title", description="desc", ...)
            subtask_data = {"title": title}
            if description is not None:
                subtask_data["description"] = description
            if assignee is not None:
                subtask_data["assignee"] = assignee
            if estimated_effort is not None:
                subtask_data["estimated_effort"] = estimated_effort
            # Add any additional kwargs
            subtask_data.update(kwargs)
        else:
            raise ValueError("Either subtask_title or title must be provided")
        
        if not subtask_data.get("title"):
            raise ValueError("Subtask must have a title")
        
        # Generate a proper hierarchical ID for the subtask if not provided
        if "id" not in subtask_data:
            # Get existing subtask IDs for this task
            existing_subtask_ids = []
            for st in self.subtasks:
                if st.get("id"):
                    # Handle both old integer IDs and new hierarchical IDs
                    if isinstance(st["id"], int):
                        # Convert old integer ID to new format for consistency
                        existing_subtask_ids.append(f"{self.id}.{st['id']:03d}")
                    else:
                        existing_subtask_ids.append(str(st["id"]))
            
            # Generate new hierarchical subtask ID
            from ..value_objects.task_id import TaskId
            try:
                new_subtask_id = TaskId.generate_subtask(self.id, existing_subtask_ids)
                subtask_data["id"] = str(new_subtask_id)
            except Exception:
                # Fallback to old integer-based ID generation if TaskId generation fails
                existing_ids = [st.get("id", 0) for st in self.subtasks if isinstance(st.get("id"), int)]
                subtask_data["id"] = max(existing_ids, default=0) + 1
        
        # Set default values
        subtask_data.setdefault("completed", False)
        subtask_data.setdefault("description", description or "")
        subtask_data.setdefault("assignees", [])  # Add assignees field support
        
        self.subtasks.append(subtask_data)
        self.updated_at = datetime.now(timezone.utc)
        
        # Raise domain event
        self._events.append(TaskUpdated(
            task_id=self.id,
            field_name="subtasks",
            old_value="subtask_added",
            new_value=subtask_data,
            updated_at=self.updated_at
        ))
        
        # Return the subtask title for backward compatibility with tests
        return subtask_data["title"]
    
    def remove_subtask(self, subtask_id: Union[int, str]) -> bool:
        """Remove a subtask by ID (supports both integer and hierarchical IDs)"""
        for i, subtask in enumerate(self.subtasks):
            current_id = subtask.get("id")
            # Normalize comparison - handle both old integer IDs and new hierarchical IDs
            if self._subtask_ids_match(current_id, subtask_id):
                removed_subtask = self.subtasks.pop(i)
                self.updated_at = datetime.now(timezone.utc)
                
                # Raise domain event
                self._events.append(TaskUpdated(
                    task_id=self.id,
                    field_name="subtasks",
                    old_value="subtask_removed",
                    new_value=removed_subtask,
                    updated_at=self.updated_at
                ))
                return True
        # Return False for non-existent subtasks instead of raising error
        return False
    
    def update_subtask(self, subtask_id: Union[int, str], updates: Dict[str, Any]) -> bool:
        """Update a subtask by ID (supports both integer and hierarchical IDs)"""
        for subtask in self.subtasks:
            current_id = subtask.get("id")
            # Normalize comparison - handle both old integer IDs and new hierarchical IDs
            if self._subtask_ids_match(current_id, subtask_id):
                old_subtask = subtask.copy()
                subtask.update(updates)
                self.updated_at = datetime.now(timezone.utc)
                
                # Raise domain event
                self._events.append(TaskUpdated(
                    task_id=self.id,
                    field_name="subtasks",
                    old_value=old_subtask,
                    new_value=subtask,
                    updated_at=self.updated_at
                ))
                return True
        # Return False for non-existent subtasks instead of raising error
        return False
    
    def complete_subtask(self, subtask_id: Union[int, str]) -> bool:
        """Mark a subtask as completed (supports both integer and hierarchical IDs)"""
        # Handle both index-based and ID-based completion
        if isinstance(subtask_id, int) and subtask_id < len(self.subtasks):
            # Treat as index if it's a small integer within range
            self.subtasks[subtask_id]["completed"] = True
            self.updated_at = datetime.now(timezone.utc)
            return True
        else:
            # Treat as ID - returns False if not found
            return self.update_subtask(subtask_id, {"completed": True})
    
    def complete_task(self) -> None:
        """Complete the task by marking all subtasks as completed and setting status to done"""
        # Complete all subtasks
        for subtask in self.subtasks:
            subtask["completed"] = True
        
        # Update task status to done
        old_status = self.status
        self.status = TaskStatus.done()
        self.updated_at = datetime.now(timezone.utc)
        
        # Raise domain event for task completion
        self._events.append(TaskUpdated(
            task_id=self.id,
            field_name="status",
            old_value=str(old_status),
            new_value=str(self.status),
            updated_at=self.updated_at
        ))
        
        # Raise domain event for subtasks completion if there are any
        if self.subtasks:
            self._events.append(TaskUpdated(
                task_id=self.id,
                field_name="subtasks",
                old_value="all_subtasks_completed",
                new_value=self.subtasks,
                updated_at=self.updated_at
            ))
    
    def get_subtask(self, subtask_id: Union[int, str]) -> Optional[Dict[str, Any]]:
        """Get a subtask by ID (supports both integer and hierarchical IDs)"""
        for subtask in self.subtasks:
            current_id = subtask.get("id")
            # Normalize comparison - handle both old integer IDs and new hierarchical IDs
            if self._subtask_ids_match(current_id, subtask_id):
                return subtask
        return None
    
    def get_subtask_by_id(self, subtask_id: Union[int, str]) -> Optional[Dict[str, Any]]:
        """Get a subtask by ID - alias for get_subtask for backward compatibility"""
        return self.get_subtask(subtask_id)
    
    def _subtask_ids_match(self, current_id: Union[int, str], target_id: Union[int, str]) -> bool:
        """Helper method to compare subtask IDs regardless of type"""
        # Convert both to strings for comparison
        current_str = str(current_id)
        target_str = str(target_id)
        
        # Direct string comparison
        if current_str == target_str:
            return True
        
        # If one is integer and other is string, compare as integers
        try:
            current_int = int(current_id) if isinstance(current_id, (int, str)) else None
            target_int = int(target_id) if isinstance(target_id, (int, str)) else None
            if current_int is not None and target_int is not None:
                return current_int == target_int
        except (ValueError, TypeError):
            pass
        
        return False
    
    def get_subtask_progress(self) -> Dict[str, Any]:
        """Get subtask completion progress"""
        if not self.subtasks:
            return {"total": 0, "completed": 0, "percentage": 0}  # No subtasks = 0% complete
        
        total = len(self.subtasks)
        completed = sum(1 for st in self.subtasks if st.get("completed", False))
        percentage = round((completed / total) * 100, 1) if total > 0 else 0
        
        return {
            "total": total,
            "completed": completed,
            "percentage": percentage
        }
    
    def is_overdue(self) -> bool:
        """Check if task is overdue"""
        if not self.due_date:
            return False
        
        try:
            due_date = datetime.fromisoformat(self.due_date)
            now = datetime.now(timezone.utc)
            
            # Make both timezone-aware or both timezone-naive for comparison
            if due_date.tzinfo is None:
                # Make due_date timezone-aware
                due_date = due_date.replace(tzinfo=timezone.utc)
            
            return now > due_date and not self.status.is_completed()
        except ValueError:
            return False
    
    def get_suggested_labels(self, context: str = "") -> List[str]:
        """Get suggested labels based on task content and context"""
        suggestions = []
        
        # Suggest labels based on title and description
        content = f"{self.title} {self.description} {context}".lower()
        
        # Use CommonLabel enum to suggest appropriate labels
        for label in CommonLabel:
            if any(keyword in content for keyword in label.get_keywords()):
                suggestions.append(label.value)
        
        return suggestions[:5]  # Return top 5 suggestions
    
    def get_effort_level(self) -> str:
        """Get the effort level category for this task"""
        try:
            effort_enum = EstimatedEffort(self.estimated_effort)
            return effort_enum.get_level()
        except ValueError:
            return "medium"
    
    def get_assignee_role_info(self) -> Optional[Dict[str, Any]]:
        """Get role information for the primary assignee (first assignee)"""
        if not self.assignees:
            return None
        
        primary_assignee = self.assignees[0]
        
        try:
            # Try to get role from AgentRole enum
            role = AgentRole.get_role_by_slug(primary_assignee)
            if role:
                from ..enums.agent_roles import get_role_metadata_from_yaml
                metadata = get_role_metadata_from_yaml(role)
                if metadata:
                    return {
                        "role": role.value,
                        "display_name": role.display_name,
                        "folder_name": role.folder_name,
                        "metadata": metadata
                    }
                else:
                    return {
                        "role": role.value,
                        "display_name": role.display_name,
                        "folder_name": role.folder_name,
                        "metadata": None
                    }
            else:
                # Return basic info for non-enum assignees
                return {
                    "role": primary_assignee,
                    "display_name": primary_assignee.replace("-", " ").replace("_", " ").title(),
                    "folder_name": primary_assignee.replace("-", "_"),
                    "metadata": None
                }
        except Exception:
            # Fallback for any errors
            return {
                "role": primary_assignee,
                "display_name": primary_assignee,
                "folder_name": primary_assignee,
                "metadata": None
            }
    
    def can_be_started(self) -> bool:
        """Check if task can be started (no blocking dependencies)"""
        return self.status.is_todo()
    
    def get_events(self) -> List[Any]:
        """Get and clear domain events"""
        events = self._events.copy()
        self._events.clear()
        return events
    
    def mark_as_retrieved(self) -> None:
        """Mark task as retrieved (triggers auto rule generation)"""
        self._events.append(TaskRetrieved(
            task_id=self.id,
            task_data=self.to_dict(),
            retrieved_at=datetime.now(timezone.utc)
        ))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary representation"""
        # Handle assignees - convert AgentRole enums to strings
        assignees_list = []
        if self.assignees is not None:
            for assignee in self.assignees:
                if hasattr(assignee, 'value'):
                    # Handle AgentRole enum - convert to string with @ prefix
                    assignees_list.append(f"@{assignee.value}")
                else:
                    # Handle string assignees
                    assignees_list.append(str(assignee))
        
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "project_id": self.project_id,
            "status": str(self.status),
            "priority": str(self.priority),
            "details": self.details,
            "estimatedEffort": self.estimated_effort,
            "assignees": assignees_list,
            "labels": self.labels.copy() if self.labels is not None else [],
            "dependencies": [dep.value if hasattr(dep, 'value') else str(dep) for dep in self.dependencies],
            "subtasks": self.subtasks.copy(),
            "dueDate": self.due_date,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
    
    def migrate_subtask_ids(self) -> None:
        """Migrate old integer subtask IDs to new hierarchical format"""
        from ..value_objects.task_id import TaskId
        
        for subtask in self.subtasks:
            if isinstance(subtask.get("id"), int):
                old_id = subtask["id"]
                try:
                    # Convert to hierarchical format
                    new_id = f"{self.id}.{old_id:03d}"
                    subtask["id"] = new_id
                except Exception:
                    # Keep old ID if conversion fails
                    pass
        
        if any(isinstance(st.get("id"), int) for st in self.subtasks):
            self.updated_at = datetime.now(timezone.utc)
    
    @classmethod
    def create(cls, id: TaskId, title: str, description: str, 
               status: Optional[TaskStatus] = None, priority: Optional[Priority] = None,
               **kwargs) -> 'Task':
        """Factory method to create a new task"""
        if status is None:
            status = TaskStatus.todo()
        if priority is None:
            priority = Priority.medium()
        
        task = cls(
            id=id,
            title=title,
            description=description,
            status=status,
            priority=priority,
            **kwargs
        )
        
        # Raise domain event
        task._events.append(TaskCreated(
            task_id=task.id,
            title=task.title,
            created_at=task.created_at
        ))
        
        return task 