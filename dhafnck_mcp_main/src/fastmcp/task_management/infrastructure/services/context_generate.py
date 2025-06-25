"""Context file generation service for tasks"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from ...domain.entities.task import Task


class ContextGenerator:
    """Service for generating and managing task context files"""
    
    def __init__(self, context_root_path: Optional[str] = None):
        """Initialize context generator with optional custom root path"""
        if context_root_path:
            self.context_root_path = Path(context_root_path)
        else:
            # Default path: .cursor/rules/contexts/
            # Get current working directory and navigate to cursor rules
            current_dir = Path.cwd()
            self.context_root_path = current_dir / ".cursor" / "rules" / "contexts"
    
    def generate_context_file_if_not_exists(self, task: Task, user_id: str = "default_id") -> bool:
        """
        Generate context file for task if it doesn't exist
        
        Args:
            task: Task entity to generate context for
            user_id: User identifier for hierarchical storage
            
        Returns:
            bool: True if file was created, False if it already existed
        """
        context_file_path = self._get_context_file_path(task, user_id)
        
        # Check if file already exists
        if context_file_path.exists():
            return False
        
        # Create directory structure if it doesn't exist
        context_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Generate context content
        context_content = self._generate_context_content(task)
        
        # Write context file
        with open(context_file_path, 'w', encoding='utf-8') as f:
            f.write(context_content)
        
        return True
    
    def update_context_file(self, task: Task, user_id: str = "default_id") -> bool:
        """
        Update existing context file with current task information
        
        Args:
            task: Task entity to update context for
            user_id: User identifier for hierarchical storage
            
        Returns:
            bool: True if file was updated, False if file doesn't exist
        """
        context_file_path = self._get_context_file_path(task, user_id)
        
        if not context_file_path.exists():
            return False
        
        # Read existing content
        with open(context_file_path, 'r', encoding='utf-8') as f:
            existing_content = f.read()
        
        # Update the metadata section
        updated_content = self._update_context_metadata(existing_content, task)
        
        # Write updated content
        with open(context_file_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        return True
    
    def _get_context_file_path(self, task: Task, user_id: str) -> Path:
        """
        Get the full path for a task's context file
        
        Path format: .cursor/rules/contexts/{user_id}/{project_id}/context_{task_id}.md
        """
        return (self.context_root_path / 
                user_id / 
                task.project_id / 
                f"context_{task.id.value}.md")
    
    def _generate_context_content(self, task: Task) -> str:
        """Generate the full context file content based on template"""
        assignee = task.assignees[0] if task.assignees else "unassigned"
        
        # Calculate requirements checklist
        requirements_section = self._generate_requirements_section(task)
        
        # Generate dependencies section
        dependencies_section = self._generate_dependencies_section(task)
        
        # Generate current session summary
        session_summary = self._generate_session_summary(task)
        
        # Generate next steps
        next_steps = self._generate_next_steps(task)
        
        content = f"""# TASK CONTEXT: {task.title}

**Task ID**: `{task.id.value}`
**Project ID**: `{task.project_id}`
**Task tree ID**: `{getattr(task, 'task_tree_id', 'main')}`
**Status**: `{task.status.value}`
**Priority**: `{task.priority.value}`
**Assignee**: `{assignee}`
**Created**: `{task.created_at.isoformat()}`
**Last Updated**: `{task.updated_at.isoformat()}`

## 🎯 Objective
{task.description or 'No description provided'}

## 📋 Requirements
{requirements_section}

## 🔧 Technical Details
### Technologies/Frameworks
- Technology/Framework to be determined based on task requirements

### Key Files/Directories
- Files/directories to be determined during task execution

{dependencies_section}

## 🚀 Progress Tracking
### Completed Actions
- Task created - {task.created_at.strftime('%Y-%m-%d')} - {assignee}

### Current Session Summary
{session_summary}

### Next Steps
{next_steps}

## 🔍 Context Notes
### Agent Insights
[Key insights or decisions made by the AI agent - to be updated during task execution]

### Challenges Encountered
[Any issues or blockers encountered - to be updated during task execution]

### Solutions Applied
[How challenges were resolved - to be updated during task execution]
"""
        return content
    
    def _generate_requirements_section(self, task: Task) -> str:
        """Generate requirements checklist based on task information"""
        requirements = []
        
        # Add basic requirement for task completion
        if task.status.value == "done":
            requirements.append("- [x] Complete task objectives")
        else:
            requirements.append("- [ ] Complete task objectives")
        
        # Add requirements based on labels
        if task.labels:
            for label in task.labels:
                if label == "test":
                    if task.status.value == "done":
                        requirements.append("- [x] Write and execute tests")
                    else:
                        requirements.append("- [ ] Write and execute tests")
                elif label == "documentation":
                    if task.status.value == "done":
                        requirements.append("- [x] Update documentation")
                    else:
                        requirements.append("- [ ] Update documentation")
                elif label == "review":
                    if task.status.value == "done":
                        requirements.append("- [x] Code review completed")
                    else:
                        requirements.append("- [ ] Code review required")
        
        # Add subtask requirements
        if task.subtasks:
            for subtask in task.subtasks:
                status = "[x]" if subtask.get('completed', False) else "[ ]"
                requirements.append(f"- {status} {subtask.get('title', 'Subtask')}")
        
        return "\n".join(requirements) if requirements else "- [ ] Task requirements to be defined"
    
    def _generate_dependencies_section(self, task: Task) -> str:
        """Generate dependencies section"""
        if not task.dependencies:
            return "### Dependencies\n- No dependencies"
        
        deps_list = []
        for dep_id in task.dependencies:
            deps_list.append(f"- Depends on Task ID: {dep_id.value}")
        
        return "### Dependencies\n" + "\n".join(deps_list)
    
    def _generate_session_summary(self, task: Task) -> str:
        """Generate current session summary based on task status"""
        if task.status.value == "todo":
            return "Task created and ready to be started."
        elif task.status.value == "in_progress":
            return "Task is currently in progress. Work has begun but not yet completed."
        elif task.status.value == "done":
            return "Task has been completed successfully."
        elif task.status.value == "blocked":
            return "Task is currently blocked and cannot proceed until blockers are resolved."
        elif task.status.value == "review":
            return "Task implementation is complete and awaiting review."
        elif task.status.value == "testing":
            return "Task implementation is complete and currently in testing phase."
        elif task.status.value == "cancelled":
            return "Task has been cancelled and will not be completed."
        else:
            return "Task status is being tracked."
    
    def _generate_next_steps(self, task: Task) -> str:
        """Generate next steps based on task status and information"""
        if task.status.value == "todo":
            steps = ["- [ ] Begin task implementation"]
            if task.assignees:
                steps.append(f"- [ ] {task.assignees[0]} to start work")
        elif task.status.value == "in_progress":
            steps = ["- [ ] Continue implementation"]
            steps.append("- [ ] Update progress as work proceeds")
        elif task.status.value == "done":
            steps = ["- [x] Task completed successfully"]
        elif task.status.value == "blocked":
            steps = ["- [ ] Identify and resolve blockers"]
            steps.append("- [ ] Update status once blockers are cleared")
        elif task.status.value == "review":
            steps = ["- [ ] Complete code review"]
            steps.append("- [ ] Address any review feedback")
        elif task.status.value == "testing":
            steps = ["- [ ] Complete testing phase"]
            steps.append("- [ ] Verify all tests pass")
        else:
            steps = ["- [ ] Next steps to be determined"]
        
        # Add subtask next steps
        if task.subtasks:
            incomplete_subtasks = [st for st in task.subtasks if not st.get('completed', False)]
            if incomplete_subtasks:
                steps.append(f"- [ ] Complete remaining {len(incomplete_subtasks)} subtask(s)")
        
        return "\n".join(steps)
    
    def _update_context_metadata(self, existing_content: str, task: Task) -> str:
        """Update the metadata section of existing context file"""
        lines = existing_content.split('\n')
        updated_lines = []
        in_metadata = False
        
        for line in lines:
            if line.startswith('**Task ID**'):
                in_metadata = True
                updated_lines.append(f"**Task ID**: `{task.id.value}`")
            elif line.startswith('**Project ID**'):
                updated_lines.append(f"**Project ID**: `{task.project_id}`")
            elif line.startswith('**Task tree ID**'):
                updated_lines.append(f"**Task tree ID**: `{getattr(task, 'task_tree_id', 'main')}`")
            elif line.startswith('**Status**'):
                updated_lines.append(f"**Status**: `{task.status.value}`")
            elif line.startswith('**Priority**'):
                updated_lines.append(f"**Priority**: `{task.priority.value}`")
            elif line.startswith('**Assignee**'):
                assignee = task.assignees[0] if task.assignees else "unassigned"
                updated_lines.append(f"**Assignee**: `{assignee}`")
            elif line.startswith('**Last Updated**'):
                updated_lines.append(f"**Last Updated**: `{task.updated_at.isoformat()}`")
                in_metadata = False
            else:
                updated_lines.append(line)
        
        return '\n'.join(updated_lines)


# Convenience function for easy integration
def generate_task_context_if_needed(task: Task, user_id: str = "default_id") -> bool:
    """
    Convenience function to generate task context file if it doesn't exist
    
    Args:
        task: Task entity to generate context for
        user_id: User identifier for hierarchical storage
        
    Returns:
        bool: True if file was created, False if it already existed
    """
    generator = ContextGenerator()
    return generator.generate_context_file_if_not_exists(task, user_id)


def update_task_context(task: Task, user_id: str = "default_id") -> bool:
    """
    Convenience function to update existing task context file
    
    Args:
        task: Task entity to update context for
        user_id: User identifier for hierarchical storage
        
    Returns:
        bool: True if file was updated, False if file doesn't exist
    """
    generator = ContextGenerator()
    return generator.update_context_file(task, user_id)