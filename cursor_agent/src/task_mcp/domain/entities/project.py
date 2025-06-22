"""Project Domain Entity"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Dict, List, Optional, Set

from .agent import Agent
from .task_tree import TaskTree

if TYPE_CHECKING:
    from .task import Task
    from .work_session import WorkSession


@dataclass
class Project:
    """Project aggregate root for multi-agent task orchestration"""

    id: str
    name: str
    description: str
    created_at: datetime
    updated_at: datetime

    # Multi-tree structure
    task_trees: Dict[str, TaskTree] = field(default_factory=dict)

    # Agent management
    registered_agents: Dict[str, Agent] = field(default_factory=dict)
    agent_assignments: Dict[str, str] = field(
        default_factory=dict
    )  # tree_id -> agent_id

    # Cross-tree dependencies
    cross_tree_dependencies: Dict[str, Set[str]] = field(
        default_factory=dict
    )  # task_id -> dependent_task_ids

    # Work coordination
    active_work_sessions: Dict[str, "WorkSession"] = field(default_factory=dict)
    resource_locks: Dict[str, str] = field(default_factory=dict)  # resource -> agent_id

    def create_task_tree(
        self, tree_id: str, name: str, description: str = ""
    ) -> TaskTree:
        """Create a new task tree/branch within the project"""
        if tree_id in self.task_trees:
            raise ValueError(f"Task tree {tree_id} already exists")

        task_tree = TaskTree(
            id=tree_id,
            name=name,
            description=description,
            project_id=self.id,
            created_at=datetime.now(),
        )

        self.task_trees[tree_id] = task_tree
        self.updated_at = datetime.now()
        return task_tree

    def register_agent(self, agent: Agent) -> None:
        """Register an AI agent to work on this project"""
        self.registered_agents[agent.id] = agent
        self.updated_at = datetime.now()

    def assign_agent_to_tree(self, agent_id: str, tree_id: str) -> None:
        """Assign an agent to work on a specific task tree"""
        if agent_id not in self.registered_agents:
            raise ValueError(f"Agent {agent_id} not registered")
        if tree_id not in self.task_trees:
            raise ValueError(f"Task tree {tree_id} not found")

        # Check if tree is already assigned
        if tree_id in self.agent_assignments:
            current_agent = self.agent_assignments[tree_id]
            if current_agent != agent_id:
                raise ValueError(
                    f"Task tree {tree_id} already assigned to agent {current_agent}"
                )

        self.agent_assignments[tree_id] = agent_id
        self.updated_at = datetime.now()

    def add_cross_tree_dependency(
        self, dependent_task_id: str, prerequisite_task_id: str
    ) -> None:
        """Add a dependency between tasks in different trees"""
        # Validate that tasks exist and are in different trees
        dependent_tree = self._find_task_tree(dependent_task_id)
        prerequisite_tree = self._find_task_tree(prerequisite_task_id)

        if not dependent_tree or not prerequisite_tree:
            raise ValueError("One or both tasks not found in project")

        if dependent_tree.id == prerequisite_tree.id:
            raise ValueError(
                "Use regular task dependencies for tasks within the same tree"
            )

        # Add cross-tree dependency
        if dependent_task_id not in self.cross_tree_dependencies:
            self.cross_tree_dependencies[dependent_task_id] = set()

        self.cross_tree_dependencies[dependent_task_id].add(prerequisite_task_id)
        self.updated_at = datetime.now()

    def get_available_work_for_agent(self, agent_id: str) -> List["Task"]:
        """Get available tasks for a specific agent based on their assignments and dependencies"""
        if agent_id not in self.registered_agents:
            raise ValueError(f"Agent {agent_id} not registered")

        available_tasks = []

        # Find trees assigned to this agent
        assigned_trees = [
            tree_id
            for tree_id, assigned_agent in self.agent_assignments.items()
            if assigned_agent == agent_id
        ]

        for tree_id in assigned_trees:
            tree = self.task_trees[tree_id]
            tree_tasks = tree.get_available_tasks()

            # Filter out tasks blocked by cross-tree dependencies
            for task in tree_tasks:
                if self._is_task_ready_for_work(task.id.value):
                    available_tasks.append(task)

        return available_tasks

    def start_work_session(
        self, agent_id: str, task_id: str, max_duration_hours: Optional[float] = None
    ) -> "WorkSession":
        """Start a work session for an agent on a specific task"""
        from .work_session import WorkSession

        if agent_id not in self.registered_agents:
            raise ValueError(f"Agent {agent_id} not registered")

        # Check if agent is assigned to the tree containing this task
        task_tree = self._find_task_tree(task_id)
        if not task_tree:
            raise ValueError(f"Task {task_id} not found")

        if self.agent_assignments.get(task_tree.id) != agent_id:
            raise ValueError(f"Agent {agent_id} not assigned to tree {task_tree.id}")

        # Create work session using factory method
        session = WorkSession.create_session(
            agent_id=agent_id,
            task_id=task_id,
            tree_id=task_tree.id,
            max_duration_hours=max_duration_hours,
        )

        self.active_work_sessions[session.id] = session
        self.updated_at = datetime.now()
        return session

    def _find_task_tree(self, task_id: str) -> Optional[TaskTree]:
        """Find which task tree contains a specific task"""
        for tree in self.task_trees.values():
            if tree.has_task(task_id):
                return tree
        return None

    def _is_task_ready_for_work(self, task_id: str) -> bool:
        """Check if a task is ready for work (all cross-tree dependencies satisfied)"""
        if task_id not in self.cross_tree_dependencies:
            return True  # No cross-tree dependencies

        # Check if all prerequisite tasks are completed
        for prerequisite_id in self.cross_tree_dependencies[task_id]:
            prerequisite_tree = self._find_task_tree(prerequisite_id)
            if not prerequisite_tree:
                return False  # Prerequisite task not found

            prerequisite_task = prerequisite_tree.get_task(prerequisite_id)
            if not prerequisite_task or not prerequisite_task.status.is_done():
                return False  # Prerequisite not completed

        return True

    def get_orchestration_status(self) -> Dict:
        """Get comprehensive status for orchestration dashboard"""
        return {
            "project_id": self.id,
            "project_name": self.name,
            "total_trees": len(self.task_trees),
            "registered_agents": len(self.registered_agents),
            "active_assignments": len(self.agent_assignments),
            "active_sessions": len(self.active_work_sessions),
            "cross_tree_dependencies": sum(
                len(deps) for deps in self.cross_tree_dependencies.values()
            ),
            "resource_locks": len(self.resource_locks),
            "trees": {
                tree_id: {
                    "name": tree.name,
                    "assigned_agent": self.agent_assignments.get(tree_id),
                    "total_tasks": tree.get_task_count(),
                    "completed_tasks": tree.get_completed_task_count(),
                    "progress": tree.get_progress_percentage(),
                }
                for tree_id, tree in self.task_trees.items()
            },
            "agents": {
                agent_id: {
                    "name": agent.name,
                    "capabilities": [
                        cap.value for cap in agent.capabilities
                    ],  # Convert set to list
                    "assigned_trees": [
                        tree_id
                        for tree_id, assigned_agent in self.agent_assignments.items()
                        if assigned_agent == agent_id
                    ],
                    "active_sessions": [
                        session.id
                        for session in self.active_work_sessions.values()
                        if session.agent_id == agent_id
                    ],
                }
                for agent_id, agent in self.registered_agents.items()
            },
        }

    def coordinate_cross_tree_dependencies(self) -> Dict:
        """Coordinate and validate cross-tree dependencies"""
        coordination_result = {
            "total_dependencies": sum(
                len(deps) for deps in self.cross_tree_dependencies.values()
            ),
            "validated_dependencies": 0,
            "blocked_tasks": [],
            "ready_tasks": [],
            "missing_prerequisites": [],
        }

        for dependent_task_id, prerequisite_ids in self.cross_tree_dependencies.items():
            # Check if dependent task exists
            dependent_tree = self._find_task_tree(dependent_task_id)
            if not dependent_tree:
                coordination_result["missing_prerequisites"].append(
                    {"task_id": dependent_task_id, "issue": "Dependent task not found"}
                )
                continue

            # Check each prerequisite
            all_prerequisites_met = True
            for prerequisite_id in prerequisite_ids:
                prerequisite_tree = self._find_task_tree(prerequisite_id)
                if not prerequisite_tree:
                    coordination_result["missing_prerequisites"].append(
                        {
                            "task_id": prerequisite_id,
                            "issue": "Prerequisite task not found",
                        }
                    )
                    all_prerequisites_met = False
                    continue

                prerequisite_task = prerequisite_tree.get_task(prerequisite_id)
                if not prerequisite_task or not prerequisite_task.status.is_done():
                    all_prerequisites_met = False

            if all_prerequisites_met:
                coordination_result["ready_tasks"].append(dependent_task_id)
            else:
                coordination_result["blocked_tasks"].append(dependent_task_id)

            coordination_result["validated_dependencies"] += 1

        return coordination_result
