"""Do Next Use Case - Find the next task or subtask to work on"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ...domain import AutoRuleGenerator, TaskRepository
from ...infrastructure.services.agent_doc_generator import (
    generate_docs_for_assignees,
)


@dataclass
class DoNextResponse:
    """Response containing the next item to work on"""

    has_next: bool
    next_item: Optional[Dict[str, Any]] = None
    context: Optional[Dict[str, Any]] = None
    message: str = ""


class DoNextUseCase:
    """Use case for finding the next task or subtask to work on"""

    def __init__(
        self, task_repository: TaskRepository, auto_rule_generator: AutoRuleGenerator
    ):
        self._task_repository = task_repository
        self._auto_rule_generator = auto_rule_generator

    def execute(self) -> DoNextResponse:
        """Find the next task or subtask to work on"""
        all_tasks = self._task_repository.find_all()

        if not all_tasks:
            return DoNextResponse(
                has_next=False, message="No tasks found. Create a task to get started!"
            )

        # Filter actionable tasks (todo or in_progress, not done/cancelled/blocked/review/testing)
        actionable_statuses = {"todo", "in_progress"}
        active_tasks = [
            task for task in all_tasks if task.status.value in actionable_statuses
        ]

        if not active_tasks:
            # Check if all tasks are actually completed
            completed_tasks = [task for task in all_tasks if task.status.is_done()]
            if len(completed_tasks) == len(all_tasks):
                return DoNextResponse(
                    has_next=False,
                    context=self._get_completion_context(all_tasks),
                    message="🎉 All tasks completed! Great job!",
                )
            else:
                # There are tasks but none are actionable (e.g., in review/testing)
                return DoNextResponse(
                    has_next=False, message="No actionable tasks found."
                )

        # Sort tasks by priority and status
        sorted_tasks = self._sort_tasks_by_priority(active_tasks)

        # Find the next actionable item
        for task in sorted_tasks:
            # Check if task can be started (dependencies satisfied)
            if not self._can_task_be_started(task, all_tasks):
                continue

            # Check if task has incomplete subtasks
            next_subtask = self._find_next_subtask(task)
            if next_subtask:
                # Trigger auto rule generation for the parent task
                self._auto_rule_generator.generate_rules_for_task(task)
                # Generate agent documentation for all unique assignees (task and subtask)
                generate_docs_for_assignees(task.assignees, clear_all=False)
                if "assignees" in next_subtask and next_subtask["assignees"]:
                    generate_docs_for_assignees(
                        next_subtask["assignees"], clear_all=False
                    )
                return DoNextResponse(
                    has_next=True,
                    next_item={
                        "type": "subtask",
                        "task": self._task_to_dict(task),
                        "subtask": next_subtask,
                        "context": self._get_task_context(task, all_tasks),
                    },
                    message=f"Next action: Work on subtask '{next_subtask['title']}' in task '{task.title}'",
                )
            else:
                # Task itself is the next item to work on
                self._auto_rule_generator.generate_rules_for_task(task)
                # Generate agent documentation for all unique assignees
                generate_docs_for_assignees(task.assignees, clear_all=False)
                return DoNextResponse(
                    has_next=True,
                    next_item={
                        "type": "task",
                        "task": self._task_to_dict(task),
                        "context": self._get_task_context(task, all_tasks),
                    },
                    message=f"Next action: Work on task '{task.title}'",
                )

        # All remaining tasks are blocked by dependencies
        blocked_tasks = [
            task
            for task in active_tasks
            if not self._can_task_be_started(task, all_tasks)
        ]
        if blocked_tasks:
            blocking_info = self._get_blocking_info(blocked_tasks, all_tasks)
            return DoNextResponse(
                has_next=False,
                context=blocking_info,
                message="All remaining tasks are blocked by dependencies. Complete prerequisite tasks first.",
            )

        return DoNextResponse(has_next=False, message="No actionable tasks found.")

    def _sort_tasks_by_priority(self, tasks: List) -> List:
        """Sort tasks by priority (high > medium > low) then by status (todo > in_progress)"""
        priority_order = {"critical": -1, "high": 0, "medium": 1, "low": 2}
        status_order = {"todo": 0, "in_progress": 1}

        return sorted(
            tasks,
            key=lambda task: (
                priority_order.get(task.priority.value, 3),
                status_order.get(task.status.value, 2),
            ),
        )

    def _can_task_be_started(self, task, all_tasks: List) -> bool:
        """Check if a task can be started (all dependencies satisfied)"""
        if not task.dependencies:
            return True

        # Check if all dependencies are completed
        for dep_id in task.dependencies:
            dep_task = next((t for t in all_tasks if t.id.value == dep_id.value), None)
            if not dep_task or not dep_task.status.is_done():
                return False

        return True

    def _find_next_subtask(self, task) -> Optional[Dict[str, Any]]:
        """Find the first incomplete subtask in a task"""
        if not task.subtasks:
            return None

        for subtask in task.subtasks:
            if not subtask.get("completed", False):
                return subtask

        return None

    def _task_to_dict(self, task) -> Dict[str, Any]:
        """Convert task entity to dictionary"""
        task_dict = task.to_dict()

        # Calculate subtask progress
        if task.subtasks:
            progress = task.get_subtask_progress()
            task_dict["subtask_progress"] = progress

        return task_dict

    def _get_task_context(self, task, all_tasks: List) -> Dict[str, Any]:
        """Get context information for a task"""
        # Count dependencies
        dependency_count = len(task.dependencies) if task.dependencies else 0

        # Find tasks blocked by this task
        blocking_tasks = [
            t
            for t in all_tasks
            if t.dependencies
            and any(dep.value == task.id.value for dep in t.dependencies)
        ]

        # Calculate overall progress
        total_tasks = len(all_tasks)
        completed_tasks = len([t for t in all_tasks if t.status.is_done()])

        context = {
            "task_id": task.id.value,
            "can_start": self._can_task_be_started(task, all_tasks),
            "dependency_count": dependency_count,
            "blocking_count": len(blocking_tasks),
            "overall_progress": {
                "completed": completed_tasks,
                "total": total_tasks,
                "percentage": (
                    round((completed_tasks / total_tasks) * 100, 1)
                    if total_tasks > 0
                    else 0
                ),
            },
        }

        # Add subtask progress if available
        if task.subtasks:
            progress = task.get_subtask_progress()
            context["subtask_progress"] = progress

        return context

    def _get_completion_context(self, all_tasks: List) -> Dict[str, Any]:
        """Get context when all tasks are completed"""
        total_tasks = len(all_tasks)

        # Count by priority
        priority_counts = {}
        for task in all_tasks:
            priority = str(task.priority)
            priority_counts[priority] = priority_counts.get(priority, 0) + 1

        return {
            "total_completed": total_tasks,
            "priority_breakdown": priority_counts,
            "completion_rate": 100.0,
        }

    def _get_blocking_info(
        self, blocked_tasks: List, all_tasks: List
    ) -> Dict[str, Any]:
        """Get information about blocked tasks and their dependencies"""
        blocking_info = {"blocked_tasks": [], "required_completions": []}

        for task in blocked_tasks:
            task_info = {
                "id": task.id.value,
                "title": task.title,
                "priority": str(task.priority),
                "blocked_by": [],
            }

            # Find which dependencies are not completed
            for dep_id in task.dependencies:
                dep_task = next(
                    (t for t in all_tasks if t.id.value == dep_id.value), None
                )
                if dep_task and not dep_task.status.is_done():
                    task_info["blocked_by"].append(
                        {
                            "id": dep_task.id.value,
                            "title": dep_task.title,
                            "status": str(dep_task.status),
                        }
                    )

                    # Add to required completions if not already there
                    if not any(
                        req["id"] == dep_task.id.value
                        for req in blocking_info["required_completions"]
                    ):
                        blocking_info["required_completions"].append(
                            {
                                "id": dep_task.id.value,
                                "title": dep_task.title,
                                "status": str(dep_task.status),
                                "priority": str(dep_task.priority),
                            }
                        )

            blocking_info["blocked_tasks"].append(task_info)

        return blocking_info
