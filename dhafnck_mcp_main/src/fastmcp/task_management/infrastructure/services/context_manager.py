"""Context Manager Service for business logic and CRUD operations"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import logging

from .context_schema import TaskContext, ContextSchema, ContextInsight, ContextProgressAction, ContextSubtask, ContextRequirement
from ..repositories.context_repository import ContextRepository
from ...domain.entities.task import Task

logger = logging.getLogger(__name__)


class ContextManager:
    """Service for managing context business logic and operations"""
    
    def __init__(self, context_repository: Optional[ContextRepository] = None):
        """Initialize context manager with repository"""
        self.repository = context_repository or ContextRepository()
    
    def create_context_from_task(self, task: Task, user_id: str = "default_id", project_id: str = "", task_tree_id: str = "main") -> bool:
        """Create a new context from a Task entity"""
        try:
            # Create context from task data
            context = self._task_to_context(task, user_id, project_id, task_tree_id)
            
            # Save context
            return self.repository.create_context(context, user_id)
            
        except Exception as e:
            logger.error(f"Failed to create context from task {task.id}: {e}")
            return False
    
    def get_context(self, task_id: str, user_id: str = "default_id", project_id: str = "", task_tree_id: str = "main") -> Optional[TaskContext]:
        """Get a context by task ID"""
        return self.repository.get_context(task_id, user_id, project_id, task_tree_id)
    
    def update_context_from_task(self, task: Task, user_id: str = "default_id", project_id: str = "", task_tree_id: str = "main") -> bool:
        """Update an existing context from a Task entity"""
        try:
            # Get existing context
            existing_context = self.repository.get_context(
                task.id.value, user_id, project_id, task_tree_id
            )
            
            if not existing_context:
                # Create new context if it doesn't exist
                return self.create_context_from_task(task, user_id, project_id, task_tree_id)
            
            # Update context with task data
            updated_context = self._update_context_from_task(existing_context, task)
            
            # Save updated context
            return self.repository.update_context(updated_context, user_id)
            
        except Exception as e:
            logger.error(f"Failed to update context from task {task.id}: {e}")
            return False
    
    def delete_context(self, task_id: str, user_id: str = "default_id", project_id: str = "", task_tree_id: str = "main") -> bool:
        """Delete a context"""
        return self.repository.delete_context(task_id, user_id, project_id, task_tree_id)
    
    def context_exists(self, task_id: str, user_id: str = "default_id", project_id: str = "", task_tree_id: str = "main") -> bool:
        """Check if a context exists"""
        return self.repository.context_exists(task_id, user_id, project_id, task_tree_id)
    
    def list_contexts(self, user_id: str = "default_id", project_id: str = "", task_tree_id: str = "main") -> Dict[str, Any]:
        """List all contexts in a project/tree"""
        return self.repository.list_contexts(user_id, project_id, task_tree_id)
    
    def get_property(self, task_id: str, property_path: str, user_id: str = "default_id", project_id: str = "", task_tree_id: str = "main") -> Any:
        """Get a specific property from a context using dot notation"""
        return self.repository.get_property(task_id, property_path, user_id, project_id, task_tree_id)
    
    def update_property(self, task_id: str, property_path: str, value: Any, user_id: str = "default_id", project_id: str = "", task_tree_id: str = "main") -> bool:
        """Update a specific property in a context using dot notation"""
        return self.repository.update_property(task_id, property_path, value, user_id, project_id, task_tree_id)
    
    def merge_data(self, task_id: str, data: Dict[str, Any], user_id: str = "default_id", project_id: str = "", task_tree_id: str = "main") -> bool:
        """Merge data into an existing context"""
        return self.repository.merge_context_data(task_id, data, user_id, project_id, task_tree_id)
    
    def add_insight(self, task_id: str, agent: str, category: str, content: str, importance: str = "medium", 
                   user_id: str = "default_id", project_id: str = "", task_tree_id: str = "main") -> bool:
        """Add an insight to a context"""
        try:
            insight = ContextInsight(
                timestamp=datetime.now().isoformat(),
                agent=agent,
                category=category,
                content=content,
                importance=importance
            )
            
            # Get current context
            context = self.repository.get_context(task_id, user_id, project_id, task_tree_id)
            if not context:
                return False
            
            # Add insight to appropriate category
            if category == "insight":
                context.notes.agent_insights.append(insight)
            elif category == "challenge":
                context.notes.challenges_encountered.append(insight)
            elif category == "solution":
                context.notes.solutions_applied.append(insight)
            elif category == "decision":
                context.notes.decisions_made.append(insight)
            else:
                # Default to general insights
                context.notes.agent_insights.append(insight)
            
            # Save updated context
            return self.repository.update_context(context, user_id)
            
        except Exception as e:
            logger.error(f"Failed to add insight to task {task_id}: {e}")
            return False
    
    def add_progress_action(self, task_id: str, action: str, agent: str, details: str = "", status: str = "completed",
                          user_id: str = "default_id", project_id: str = "", task_tree_id: str = "main") -> bool:
        """Add a progress action to a context"""
        try:
            progress_action = ContextProgressAction(
                timestamp=datetime.now().isoformat(),
                action=action,
                agent=agent,
                details=details,
                status=status
            )
            
            # Get current context
            context = self.repository.get_context(task_id, user_id, project_id, task_tree_id)
            if not context:
                return False
            
            # Add progress action
            context.progress.completed_actions.append(progress_action)
            
            # Update session summary
            if not context.progress.current_session_summary:
                context.progress.current_session_summary = f"Latest action: {action}"
            else:
                context.progress.current_session_summary += f"\nLatest action: {action}"
            
            # Save updated context
            return self.repository.update_context(context, user_id)
            
        except Exception as e:
            logger.error(f"Failed to add progress action to task {task_id}: {e}")
            return False
    
    def update_next_steps(self, task_id: str, next_steps: List[str], user_id: str = "default_id", project_id: str = "", task_tree_id: str = "main") -> bool:
        """Update the next steps for a context"""
        try:
            context = self.repository.get_context(task_id, user_id, project_id, task_tree_id)
            if not context:
                return False
            
            context.progress.next_steps = next_steps
            return self.repository.update_context(context, user_id)
            
        except Exception as e:
            logger.error(f"Failed to update next steps for task {task_id}: {e}")
            return False
    
    def should_create_context_for_task(self, task: Task, user_id: str = "default_id", project_id: str = "", task_tree_id: str = "main") -> bool:
        """
        Check if context should be created for a task.
        Conditions:
        1. Task status is "todo"
        2. All subtasks are "todo" or no subtasks exist
        3. Context doesn't already exist
        """
        try:
            # Check if task status is todo
            if task.status.value != "todo":
                return False
            
            # Check subtasks - all must be todo or not completed
            if task.subtasks:
                for subtask in task.subtasks:
                    if subtask.get('completed', False):
                        return False
            
            # Check if context already exists
            if self.context_exists(
                task.id.value, 
                user_id, 
                project_id, 
                task_tree_id
            ):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to check context creation conditions for task {task.id}: {e}")
            return False
    
    def _task_to_context(self, task: Task, user_id: str, project_id: str, task_tree_id: str) -> TaskContext:
        """Convert a Task entity to a TaskContext"""
        # Create empty context with basic information
        context = ContextSchema.create_empty_context(
            task_id=task.id.value,
            project_id=project_id,
            title=task.title,
            description=task.description,
            task_tree_id=task_tree_id,
            user_id=user_id,
            status=task.status.value,
            priority=task.priority.value,
            assignees=task.assignees,
            labels=task.labels,
            estimated_effort=task.estimated_effort,
            due_date=task.due_date.isoformat() if task.due_date else None
        )
        
        # Add requirements from task details
        if task.details:
            context.requirements.custom_requirements.append(task.details)
        
        # Add subtasks
        if task.subtasks:
            for subtask in task.subtasks:
                context_subtask = ContextSubtask(
                    id=subtask.get('id', ''),
                    title=subtask.get('title', ''),
                    description=subtask.get('description', ''),
                    status=subtask.get('status', 'todo'),
                    assignee=subtask.get('assignee', ''),
                    completed=subtask.get('completed', False),
                    progress_notes=subtask.get('progress_notes', '')
                )
                context.subtasks.items.append(context_subtask)
            
            # Update subtask counts
            context.subtasks.total_count = len(task.subtasks)
            context.subtasks.completed_count = sum(1 for st in task.subtasks if st.get('completed', False))
            if context.subtasks.total_count > 0:
                context.subtasks.progress_percentage = (context.subtasks.completed_count / context.subtasks.total_count) * 100
        
        # Add dependencies
        if task.dependencies:
            for dep_id in task.dependencies:
                context.dependencies.task_dependencies.append({
                    "task_id": dep_id.value,
                    "title": "",  # Could be populated by looking up the dependency
                    "status": "unknown",
                    "blocking_reason": ""
                })
        
        # Add initial progress action
        initial_action = ContextProgressAction(
            timestamp=task.created_at.isoformat(),
            action="Task created",
            agent=task.assignees[0] if task.assignees else "system",
            details=f"Task '{task.title}' created with status '{task.status.value}'",
            status="completed"
        )
        context.progress.completed_actions.append(initial_action)
        
        # Set initial session summary
        context.progress.current_session_summary = f"Task created and ready to be started. Status: {task.status.value}"
        
        # Set initial next steps based on task status
        if task.status.value == "todo":
            context.progress.next_steps = [
                "Begin task implementation",
                "Review task requirements and dependencies",
                "Set up development environment if needed"
            ]
            if task.assignees:
                context.progress.next_steps.append(f"{task.assignees[0]} to start work")
        
        return context
    
    def _update_context_from_task(self, context: TaskContext, task: Task) -> TaskContext:
        """Update an existing context with data from a Task entity"""
        # Update metadata
        context.metadata.status = task.status.value
        context.metadata.priority = task.priority.value
        context.metadata.assignees = task.assignees
        context.metadata.labels = task.labels
        context.metadata.updated_at = datetime.now().isoformat()
        
        # Update objective
        context.objective.title = task.title
        context.objective.description = task.description
        context.objective.estimated_effort = task.estimated_effort
        if task.due_date:
            context.objective.due_date = task.due_date.isoformat()
        
        # Update subtasks if they exist in the task
        if task.subtasks:
            # Clear existing subtasks and rebuild
            context.subtasks.items = []
            
            for subtask in task.subtasks:
                context_subtask = ContextSubtask(
                    id=subtask.get('id', ''),
                    title=subtask.get('title', ''),
                    description=subtask.get('description', ''),
                    status=subtask.get('status', 'todo'),
                    assignee=subtask.get('assignee', ''),
                    completed=subtask.get('completed', False),
                    progress_notes=subtask.get('progress_notes', '')
                )
                context.subtasks.items.append(context_subtask)
            
            # Update subtask counts
            context.subtasks.total_count = len(task.subtasks)
            context.subtasks.completed_count = sum(1 for st in task.subtasks if st.get('completed', False))
            if context.subtasks.total_count > 0:
                context.subtasks.progress_percentage = (context.subtasks.completed_count / context.subtasks.total_count) * 100
        
        # Update session summary based on status change
        if task.status.value == "in_progress":
            context.progress.current_session_summary = "Task is currently in progress. Work has begun but not yet completed."
        elif task.status.value == "done":
            context.progress.current_session_summary = "Task has been completed successfully."
        elif task.status.value == "blocked":
            context.progress.current_session_summary = "Task is currently blocked and cannot proceed until blockers are resolved."
        elif task.status.value == "review":
            context.progress.current_session_summary = "Task implementation is complete and awaiting review."
        elif task.status.value == "testing":
            context.progress.current_session_summary = "Task implementation is complete and currently in testing phase."
        elif task.status.value == "cancelled":
            context.progress.current_session_summary = "Task has been cancelled and will not be completed."
        
        return context 