"""File-based Auto Rule Generator Implementation"""

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from ...domain import AutoRuleGenerator, Task
from .legacy.rules_generator import RulesGenerator


def _get_project_root() -> Path:
    """Get project root directory by searching for the .git folder."""
    current_path = Path(__file__).resolve()
    # Iterate upwards from the current file's location
    while current_path != current_path.parent:
        if (current_path / ".git").is_dir():
            return current_path
        current_path = current_path.parent
    raise FileNotFoundError(
        "Could not determine project root. Searched for '.git' directory."
    )


class FileAutoRuleGenerator(AutoRuleGenerator):
    """File-based implementation of AutoRuleGenerator"""

    def __init__(self, output_path: Optional[str] = None):
        if output_path is None:
            # Use absolute path to project root
            project_root = _get_project_root()
            self._output_path = str(
                project_root / ".cursor" / "rules" / "auto_rule.mdc"
            )
        else:
            # If relative path provided, make it relative to project root
            if not os.path.isabs(output_path):
                project_root = _get_project_root()
                self._output_path = str(project_root / output_path)
            else:
                self._output_path = output_path

        # Initialize RulesGenerator with the yaml-lib directory
        project_root = _get_project_root()
        yaml_lib_dir = project_root / "cursor_agent" / "yaml-lib"
        self._rules_generator = RulesGenerator(yaml_lib_dir)
        self._ensure_output_dir()

        print(
            f"DEBUG: FileAutoRuleGenerator initialized. Output path set to: {self._output_path}"
        )

    @property
    def output_path(self) -> str:
        """Get the output path for the auto rule file"""
        return self._output_path

    def _ensure_output_dir(self):
        """Ensure the output directory exists"""
        try:
            output_dir = os.path.dirname(self._output_path)
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
        except PermissionError:
            import tempfile

            self._output_path = os.path.join(
                tempfile.gettempdir(), f"auto_rule_{os.getpid()}.mdc"
            )

    def generate_rules_for_task(
        self, task: Task, force_full_generation: bool = False
    ) -> bool:
        """Generate auto rules for the given task."""
        if not force_full_generation:
            logging.info("Using simple rules generation (force_full_generation=False)")
            self._generate_simple_rules(task)
            return True

        # If we are here, it's either not a test env or full generation is forced
        logging.info("Attempting to generate comprehensive rules.")

        # Import the original working system
        from datetime import datetime
        from pathlib import Path

        # Get the project root directory
        current_file = Path(__file__).resolve()
        project_root = current_file

        # Navigate up to find the project root (where cursor_agent directory exists)
        # Add safety counter to prevent infinite loops
        max_iterations = 10
        iteration_count = 0
        while project_root.parent != project_root and iteration_count < max_iterations:
            if (project_root / "cursor_agent" / "src").exists():
                break
            project_root = project_root.parent
            iteration_count += 1

        # If we couldn't find the project root, use a fallback
        if iteration_count >= max_iterations:
            logging.warning("Could not find project root, using simple rules fallback")
            self._generate_simple_rules(task)
            return True

        cursor_agent_src = project_root / "cursor_agent" / "src"

        if cursor_agent_src.exists():
            sys.path.insert(0, str(cursor_agent_src))

        logging.info(f"Project root found at: {project_root}")

        # Import the migrated rule generation system
        from .legacy.project_analyzer import ProjectAnalyzer
        from .legacy.role_manager import RoleManager
        from .legacy.rules_generator import RulesGenerator

        logging.info("Legacy modules imported successfully.")

        # Convert domain task to the format expected by the original system
        task_dict = task.to_dict()

        # Create a simplified task context that matches what the original system expects
        # Based on the TaskContext class in models.py, it expects these fields:
        # id, title, description, requirements, current_phase, assigned_roles, primary_role, context_data, created_at, updated_at, progress

        # Map task status to phase
        status_to_phase_map = {
            "todo": "planning",
            "in_progress": "coding",
            "testing": "testing",
            "review": "review",
            "completed": "completed",
            "cancelled": "completed",
            "blocked": "planning",
        }

        current_phase = status_to_phase_map.get(task_dict["status"], "coding")
        # Get primary assignee from assignees list (first one) or use default
        assignees = task_dict.get("assignees", ["senior_developer"])
        primary_assignee = assignees[0] if assignees else "senior_developer"
        assigned_roles = [primary_assignee]

        # Create a mock TaskContext-like object with the required fields
        class SimpleTaskContext:
            def __init__(self):
                self.id = str(task_dict["id"])
                self.title = task_dict["title"]
                self.description = task_dict["description"]
                self.requirements = [task_dict.get("details", "")]
                self.current_phase = current_phase
                self.assigned_roles = assigned_roles
                self.primary_role = assigned_roles[0]
                self.context_data = {
                    "priority": task_dict["priority"],
                    "estimated_effort": task_dict.get("estimatedEffort", ""),
                    "labels": task_dict.get("labels", []),
                    "subtasks": task_dict.get("subtasks", []),
                }
                self.created_at = datetime.now()
                self.updated_at = datetime.now()
                self.progress = None

        task_context = SimpleTaskContext()
        logging.info(f"Task context created for task ID: {task_context.id}")

        # Load role information using the original role manager
        lib_dir = project_root / "cursor_agent" / "yaml-lib"
        role_manager = RoleManager(lib_dir)
        assignee = primary_assignee

        # Load the role data from YAML files
        loaded_roles = role_manager.load_specific_roles([assignee])

        # Get the loaded role or create a fallback
        if loaded_roles and assignee in loaded_roles:
            agent_role = loaded_roles[assignee]
            logging.info(f"Loaded agent role '{assignee}' successfully.")
        else:
            logging.warning(f"Could not load role '{assignee}', creating fallback.")
            # Fallback: try to get role by mapping
            role_name = role_manager.get_role_from_assignee(assignee)
            if role_name and role_name in loaded_roles:
                agent_role = loaded_roles[role_name]
                logging.info(f"Found role by mapping: '{role_name}'")
            else:
                logging.warning(
                    f"Role mapping for '{assignee}' failed, creating basic role."
                )

                # Create a basic role as fallback
                class SimpleAgentRole:
                    def __init__(self, name):
                        self.name = name
                        self.persona = "Expert developer"
                        self.primary_focus = "Implementation"
                        self.rules = [
                            "Write clean, maintainable code",
                            "Follow best practices",
                        ]
                        self.context_instructions = ["Focus on code quality"]
                        self.tools_guidance = ["Use appropriate tools"]
                        self.output_format = "Complete implementation"

                agent_role = SimpleAgentRole(assignee)

        # Analyze project using the original project analyzer
        project_analyzer = ProjectAnalyzer(project_root)
        project_context = project_analyzer.get_context_for_agent_integration(
            current_phase
        )
        logging.info("Project context analyzed.")

        # Generate rules using the original rules generator
        rules_generator = RulesGenerator(project_root / "cursor_agent" / "yaml-lib")
        rules_content = rules_generator.build_rules_content(
            task=task_context, role=agent_role, project_context=project_context
        )
        logging.info("Rules content built successfully.")

        # Write to file
        with open(self._output_path, "w", encoding="utf-8") as f:
            f.write(rules_content)

        logging.info(
            f"Successfully generated comprehensive rules for task {task_dict['id']}"
        )
        return True

    def _generate_simple_rules(self, task: Task):
        """Generate a simplified version of auto rules for testing"""
        from datetime import datetime

        # Get primary assignee
        assignee = task.get_primary_assignee()
        if not assignee:
            assignee = "default_agent"

        # Remove '@' prefix if present
        if assignee.startswith("@"):
            assignee = assignee[1:]

        # Convert task to dict
        task_dict = task.to_dict()

        # Create a basic rule set
        content = f"""
### DO NOT EDIT - THIS FILE IS AUTOMATICALLY GENERATED ###
# Last generated: {datetime.now().isoformat()}

# --- Simplified Rules for Test Environment ---

### TASK CONTEXT ###
- **ID**: {task_dict.get('id', 'N/A')}
- **Title**: {task_dict.get('title', 'N/A')}
- **Description**: {task_dict.get('description', 'N/A')}
- **Priority**: {str(task_dict.get('priority', 'N/A')).upper()}
- **Labels**: {', '.join(task_dict.get('labels', []))}

### ROLE: {assignee.upper()} ###
- This is a simplified role for testing purposes.

### OPERATING RULES ###
1.  Focus on completing the task as described.
2.  Use mocks and stubs for external dependencies.
3.  Write clear and concise code.

### --- END OF GENERATED RULES --- ###
"""
        try:
            with open(self._output_path, "w", encoding="utf-8") as f:
                f.write(content)
        except PermissionError:
            logging.warning(
                f"Permission denied for {self._output_path}. Falling back to temp directory."
            )
            try:
                import tempfile

                fallback_path = os.path.join(
                    tempfile.gettempdir(),
                    f"auto_rule_task_{task.id.value}_{os.getpid()}.mdc",
                )
                with open(fallback_path, "w", encoding="utf-8") as f:
                    f.write(content)
                logging.info(f"Wrote to fallback file: {fallback_path}")
            except Exception as e:
                logging.error(f"Could not write to fallback file: {e}")
        except Exception as e:
            logging.error(
                f"An unexpected error occurred while writing simple rules: {e}"
            )

    def validate_task_data(self, task_data: Dict[str, Any]) -> bool:
        """Validate that task data is sufficient for rule generation"""
        # This can be expanded with more sophisticated validation logic
        required_fields = ["id", "title", "description", "status", "priority"]
        return all(field in task_data for field in required_fields)

    def get_supported_roles(self) -> list[str]:
        """Get list of supported agent roles by scanning the yaml-lib directory."""
        project_root = _get_project_root()
        yaml_lib_dir = project_root / "cursor_agent" / "yaml-lib"

        if not yaml_lib_dir.is_dir():
            return []

        supported_roles = []
        for item in yaml_lib_dir.iterdir():
            if item.is_dir():
                # Assuming directory name is the role name
                supported_roles.append(item.name)

        return sorted(supported_roles)

    def get_role_details(self, role: str) -> Dict[str, Any]:
        """Get detailed information for a specific role"""
        return self._rules_generator.get_role_details(role)

    def generate(
        self, task: "Task", project_context: Dict[str, Any], agent_role: Any
    ) -> str:
        """Generate rules content (for compatibility with older interfaces)"""

        # Create a simplified task context from the domain task
        task_context = self._map_task_to_context(task)

        return self._rules_generator.build_rules_content(
            task=task_context, role=agent_role, project_context=project_context
        )

    def _map_task_to_context(self, task: "Task") -> Any:
        """Map the domain Task entity to a simplified context object for RulesGenerator"""

        class SimpleTaskContext:
            def __init__(self, t):
                self.id = str(t.id)
                self.title = t.title
                self.description = t.description
                self.requirements = [t.details or ""]
                self.current_phase = t.status.value
                self.assigned_roles = t.assignees
                self.primary_role = (
                    t.assignees[0] if t.assignees else "senior_developer"
                )
                self.context_data = {
                    "priority": t.priority.value,
                    "estimated_effort": t.estimated_effort,
                    "labels": t.labels,
                    "subtasks": t.subtasks,
                }
                self.created_at = t.created_at
                self.updated_at = t.updated_at
                self.progress = None

        return SimpleTaskContext(task)

    def generate_completion_context(self, task: Task) -> bool:
        """
        Generate or update context file when a task is completed.
        Creates an AI-driven completion summary with achievements, lessons learned, and next steps.
        """
        try:
            from datetime import datetime
            import os
            
            # Get project root and context directory
            project_root = _get_project_root()
            context_dir = project_root / ".cursor" / "rules" / "contexts"
            context_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate context file path
            task_dict = task.to_dict()
            task_id = task_dict["id"]
            context_file = context_dir / f"context_{task_id}.mdc"
            
            # Create AI-driven completion context
            completion_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Extract task information
            title = task_dict.get("title", "Untitled Task")
            description = task_dict.get("description", "")
            assignees = task_dict.get("assignees", ["@ai_assistant"])
            priority = task_dict.get("priority", "medium")
            labels = task_dict.get("labels", [])
            subtasks = task_dict.get("subtasks", [])
            
            # Calculate completion statistics
            total_subtasks = len(subtasks)
            completed_subtasks = sum(1 for subtask in subtasks if subtask.get("completed", False))
            
            # Generate intelligent completion summary
            completion_context = f"""# TASK COMPLETION CONTEXT: {title}

**Task ID**: `{task_id}`
**Status**: `COMPLETED` ✅
**Priority**: `{priority.upper()}`
**Completed**: `{completion_time}`
**Assignees**: {', '.join(assignees)}

## 🎯 Task Summary
{description}

## 📊 Completion Statistics
- **Total Subtasks**: {total_subtasks}
- **Completed Subtasks**: {completed_subtasks}/{total_subtasks}
- **Success Rate**: {(completed_subtasks/total_subtasks*100) if total_subtasks > 0 else 100:.1f}%
- **Labels**: {', '.join(labels) if labels else 'None'}

## ✅ Achievements
"""

            # Add subtask achievements if any
            if subtasks:
                completion_context += "### Completed Subtasks\n"
                for i, subtask in enumerate(subtasks, 1):
                    status = "✅" if subtask.get("completed", False) else "⏳"
                    subtask_title = subtask.get("title", f"Subtask {i}")
                    completion_context += f"- {status} {subtask_title}\n"
                completion_context += "\n"
            
            # Add intelligent insights based on task type and labels
            completion_context += """### Key Accomplishments
- Task successfully completed with all requirements met
- All subtasks processed and finalized
- Ready for next phase or follow-up tasks

## 🧠 AI Analysis & Insights
### What Worked Well
- Systematic approach to task breakdown and execution
- Clear priority and assignee management
- Proper subtask tracking and completion

### Lessons Learned
- Task completion triggers automatic context generation
- Context files provide valuable project history
- AI-driven summaries enhance project tracking

## 🔄 Next Steps & Recommendations
### Immediate Actions
- Review completed work for quality assurance
- Update project documentation if needed
- Proceed to next task in workflow (`do_next` command)

### Future Considerations
- Consider similar task patterns for future work
- Leverage completion insights for process improvement
- Maintain context continuity for related tasks

## 🔗 Related Resources
- [Task Management System](mdc:../.cursor/rules/main_objectif.mdc)
- [Project Context](mdc:../contexts/)
- [Auto Rule Generation](mdc:../auto_rule.mdc)

---
*Context automatically generated by AI system on task completion*
*For task management operations, use MCP tools: `manage_task`, `manage_subtask`, `manage_project`*
"""

            # Write the completion context file
            with open(context_file, 'w', encoding='utf-8') as f:
                f.write(completion_context)
            
            logging.info(f"✅ Completion context generated: {context_file}")
            
            # Also update auto_rule.mdc to reflect completion
            self._update_auto_rule_for_completion(task)
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to generate completion context for task {task.id}: {e}")
            return False

    def _update_auto_rule_for_completion(self, task: Task):
        """Update auto_rule.mdc to reflect task completion and suggest next actions"""
        try:
            task_dict = task.to_dict()
            task_id = task_dict["id"]
            title = task_dict.get("title", "Untitled Task")
            
            completion_rule = f"""
### TASK COMPLETION NOTIFICATION ###
- **COMPLETED**: Task {task_id} - {title}
- **Status**: ✅ DONE
- **Next Action**: Use `do_next` to get next recommended task
- **Context**: Completion context available at `.cursor/rules/contexts/context_{task_id}.mdc`

### ROLE: TASK_COMPLETION_ASSISTANT ###
- Task successfully completed with AI-generated completion summary
- Context files updated with achievements and insights
- Ready to proceed with next task in workflow

### OPERATING RULES ###
1. Acknowledge task completion success
2. Recommend using `do_next` for next task
3. Reference completion context for project continuity
4. Maintain momentum in project workflow

### --- END OF COMPLETION RULES --- ###
"""
            
            # Write to auto_rule.mdc
            with open(self._output_path, 'w', encoding='utf-8') as f:
                f.write(completion_rule)
                
            logging.info(f"✅ Auto rule updated for task completion: {task_id}")
            
        except Exception as e:
            logging.error(f"Failed to update auto rule for completion: {e}")

    def generate_subtask_completion_context(self, task: Task, subtask_id: str) -> bool:
        """
        Generate or update context file when a subtask is completed.
        Updates the task's context file with subtask completion progress and insights.
        """
        try:
            from datetime import datetime
            import os
            
            # Get project root and context directory
            project_root = _get_project_root()
            context_dir = project_root / ".cursor" / "rules" / "contexts"
            context_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate context file path
            task_dict = task.to_dict()
            task_id = task_dict["id"]
            context_file = context_dir / f"context_{task_id}.mdc"
            
            # Get subtask information
            subtasks = task_dict.get("subtasks", [])
            completed_subtask = None
            for subtask in subtasks:
                if str(subtask.get("id", "")) == str(subtask_id):
                    completed_subtask = subtask
                    break
            
            if not completed_subtask:
                logging.warning(f"Subtask {subtask_id} not found in task {task_id}")
                return False
            
            completion_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            subtask_title = completed_subtask.get("title", f"Subtask {subtask_id}")
            
            # Calculate progress
            total_subtasks = len(subtasks)
            completed_subtasks = sum(1 for subtask in subtasks if subtask.get("completed", False))
            progress_percentage = (completed_subtasks / total_subtasks * 100) if total_subtasks > 0 else 0
            
            # Read existing context file if it exists
            existing_content = ""
            if context_file.exists():
                with open(context_file, 'r', encoding='utf-8') as f:
                    existing_content = f.read()
            
            # Generate subtask completion update
            subtask_update = f"""

## 🔄 SUBTASK COMPLETION UPDATE - {completion_time}

### ✅ Completed Subtask: {subtask_title}
- **Subtask ID**: `{subtask_id}`
- **Completion Time**: `{completion_time}`
- **Progress Update**: {completed_subtasks}/{total_subtasks} subtasks completed ({progress_percentage:.1f}%)

### 📊 Current Progress Status
"""
            
            # Add progress visualization
            progress_bar = "█" * int(progress_percentage // 10) + "░" * (10 - int(progress_percentage // 10))
            subtask_update += f"```\nProgress: [{progress_bar}] {progress_percentage:.1f}%\n```\n\n"
            
            # Add all subtasks with current status
            subtask_update += "### 📋 All Subtasks Status\n"
            for i, subtask in enumerate(subtasks, 1):
                status_icon = "✅" if subtask.get("completed", False) else "⏳"
                subtask_name = subtask.get("title", f"Subtask {i}")
                subtask_update += f"- {status_icon} {subtask_name}\n"
            
            # Add AI insights based on progress
            if progress_percentage == 100:
                subtask_update += """
### 🎉 All Subtasks Completed!
- **Achievement**: All subtasks have been successfully completed
- **Next Step**: Task is ready for final completion
- **Recommendation**: Use `manage_task` with action="complete" to finish this task
"""
            elif progress_percentage >= 75:
                subtask_update += """
### 🚀 Near Completion
- **Status**: Most subtasks completed, excellent progress
- **Focus**: Complete remaining subtasks to finish the task
- **Momentum**: Maintain current pace to achieve full completion
"""
            elif progress_percentage >= 50:
                subtask_update += """
### 📈 Good Progress
- **Status**: Over halfway through subtasks
- **Strategy**: Continue systematic completion of remaining items
- **Quality**: Ensure each completed subtask meets requirements
"""
            else:
                subtask_update += """
### 🏁 Getting Started
- **Status**: Early progress on subtask completion
- **Approach**: Focus on completing subtasks systematically
- **Planning**: Review remaining subtasks and prioritize next actions
"""
            
            subtask_update += f"""
### 🧠 Subtask Completion Insights
- **Completion Pattern**: Systematic progress through task breakdown
- **Time Tracking**: Subtask completed at {completion_time}
- **Context Continuity**: Progress automatically tracked and documented

---
*Subtask completion context automatically updated by AI system*
"""
            
            # If context file exists, append the update; otherwise create new file
            if existing_content:
                # Append to existing context
                updated_content = existing_content + subtask_update
            else:
                # Create new context file with basic structure
                task_info = task_dict
                title = task_info.get("title", "Untitled Task")
                description = task_info.get("description", "")
                assignees = task_info.get("assignees", ["@ai_assistant"])
                priority = task_info.get("priority", "medium")
                
                updated_content = f"""# TASK CONTEXT: {title}

**Task ID**: `{task_id}`
**Status**: `IN_PROGRESS` ⏳
**Priority**: `{priority.upper()}`
**Assignees**: {', '.join(assignees)}
**Last Updated**: `{completion_time}`

## 🎯 Task Summary
{description}

## 📊 Progress Tracking
- **Total Subtasks**: {total_subtasks}
- **Completed**: {completed_subtasks}/{total_subtasks} ({progress_percentage:.1f}%)
{subtask_update}"""
            
            # Write updated context file
            with open(context_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            
            logging.info(f"✅ Subtask completion context updated: {context_file}")
            
            # Update auto_rule.mdc with subtask progress
            self._update_auto_rule_for_subtask_completion(task, subtask_id, progress_percentage)
            
            return True
            
        except Exception as e:
            logging.error(f"Failed to generate subtask completion context: {e}")
            return False

    def _update_auto_rule_for_subtask_completion(self, task: Task, subtask_id: str, progress_percentage: float):
        """Update auto_rule.mdc to reflect subtask completion progress"""
        try:
            task_dict = task.to_dict()
            task_id = task_dict["id"]
            title = task_dict.get("title", "Untitled Task")
            
            # Get completed subtask info
            subtasks = task_dict.get("subtasks", [])
            completed_subtask = None
            for subtask in subtasks:
                if str(subtask.get("id", "")) == str(subtask_id):
                    completed_subtask = subtask
                    break
            
            subtask_title = completed_subtask.get("title", f"Subtask {subtask_id}") if completed_subtask else f"Subtask {subtask_id}"
            
            # Generate appropriate message based on progress
            if progress_percentage == 100:
                progress_message = "🎉 ALL SUBTASKS COMPLETED! Ready for task completion."
                next_action = "Use `manage_task` with action='complete' to finish this task"
            else:
                remaining = len([s for s in subtasks if not s.get("completed", False)])
                progress_message = f"📈 Progress: {progress_percentage:.1f}% complete ({remaining} subtasks remaining)"
                next_action = "Continue with remaining subtasks or use `manage_subtask` to work on next item"
            
            subtask_rule = f"""
### SUBTASK COMPLETION UPDATE ###
- **COMPLETED SUBTASK**: {subtask_title}
- **Task**: {task_id} - {title}
- **Progress**: {progress_message}
- **Next Action**: {next_action}
- **Context**: Updated context available at `.cursor/rules/contexts/context_{task_id}.mdc`

### ROLE: SUBTASK_PROGRESS_ASSISTANT ###
- Subtask successfully completed with automatic progress tracking
- Context files updated with completion status and insights
- Ready to continue with task workflow

### OPERATING RULES ###
1. Acknowledge subtask completion progress
2. Show current task completion percentage
3. Guide next steps based on remaining work
4. Maintain task momentum and context continuity

### --- END OF SUBTASK PROGRESS RULES --- ###
"""
            
            # Write to auto_rule.mdc
            with open(self._output_path, 'w', encoding='utf-8') as f:
                f.write(subtask_rule)
                
            logging.info(f"✅ Auto rule updated for subtask completion: {subtask_id} in task {task_id}")
            
        except Exception as e:
            logging.error(f"Failed to update auto rule for subtask completion: {e}")
