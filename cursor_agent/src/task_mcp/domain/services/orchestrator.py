"""Orchestrator Domain Service"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional

from ..entities.agent import Agent, AgentCapability, AgentStatus
from ..entities.project import Project
from ..entities.task import Task
from ..entities.task_tree import TaskTree


class OrchestrationStrategy(ABC):
    """Abstract base class for orchestration strategies"""

    @abstractmethod
    def assign_work(
        self, project: Project, available_agents: List[Agent]
    ) -> Dict[str, str]:
        """Assign work to agents based on strategy"""


class CapabilityBasedStrategy(OrchestrationStrategy):
    """Orchestration strategy based on agent capabilities"""

    def assign_work(
        self, project: Project, available_agents: List[Agent]
    ) -> Dict[str, str]:
        assignments = {}

        for tree_id, tree in project.task_trees.items():
            if tree_id in project.agent_assignments:
                continue  # Already assigned

            # Find best agent for this tree
            best_agent = self._find_best_agent_for_tree(tree, available_agents)
            if best_agent:
                assignments[tree_id] = best_agent.id

        return assignments

    def _find_best_agent_for_tree(
        self, tree: TaskTree, agents: List[Agent]
    ) -> Optional[Agent]:
        """Find the best agent for a specific task tree"""
        available_agents = [agent for agent in agents if agent.is_available()]

        if not available_agents:
            return None

        # Score agents based on tree requirements
        agent_scores = []
        for agent in available_agents:
            score = self._calculate_agent_tree_score(agent, tree)
            agent_scores.append((agent, score))

        # Sort by score and return best agent
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        return agent_scores[0][0] if agent_scores[0][1] > 0 else None

    def _calculate_agent_tree_score(self, agent: Agent, tree: TaskTree) -> float:
        """Calculate how suitable an agent is for a task tree"""
        base_score = 50.0

        # Get tree requirements from tasks
        tree_requirements = self._analyze_tree_requirements(tree)

        # Check capability match
        required_capabilities = tree_requirements.get("capabilities", [])
        capability_match = sum(
            1 for cap in required_capabilities if agent.has_capability(cap)
        )
        capability_score = (
            capability_match / max(len(required_capabilities), 1)
        ) * 30.0

        # Check language preferences
        required_languages = tree_requirements.get("languages", [])
        language_match = sum(
            1 for lang in required_languages if lang in agent.preferred_languages
        )
        language_score = (language_match / max(len(required_languages), 1)) * 10.0

        # Workload factor
        workload_score = (1.0 - agent.get_workload_percentage() / 100.0) * 10.0

        return base_score + capability_score + language_score + workload_score

    def _analyze_tree_requirements(self, tree: TaskTree) -> Dict:
        """Analyze task tree to determine capability requirements"""
        capabilities = set()
        languages = set()

        # Analyze task titles and descriptions for hints
        for task in tree.all_tasks.values():
            task_text = f"{task.title} {task.description}".lower()

            # Detect frontend work
            if any(
                keyword in task_text
                for keyword in ["frontend", "ui", "react", "vue", "angular"]
            ):
                capabilities.add(AgentCapability.FRONTEND_DEVELOPMENT)
                languages.update(["javascript", "typescript", "html", "css"])

            # Detect backend work
            if any(
                keyword in task_text
                for keyword in ["backend", "api", "server", "database"]
            ):
                capabilities.add(AgentCapability.BACKEND_DEVELOPMENT)
                languages.update(["python", "java", "node.js"])

            # Detect DevOps work
            if any(
                keyword in task_text
                for keyword in ["deploy", "docker", "kubernetes", "ci/cd"]
            ):
                capabilities.add(AgentCapability.DEVOPS)

            # Detect testing work
            if any(
                keyword in task_text for keyword in ["test", "testing", "qa", "quality"]
            ):
                capabilities.add(AgentCapability.TESTING)

        return {"capabilities": list(capabilities), "languages": list(languages)}


class Orchestrator:
    """Domain service for orchestrating multi-agent work"""

    def __init__(self, strategy: OrchestrationStrategy = None):
        self.strategy = strategy or CapabilityBasedStrategy()
        self.logger = logging.getLogger(__name__)

    def orchestrate_project(self, project: Project) -> Dict[str, any]:
        """Orchestrate work distribution for a project"""
        self.logger.info(f"Starting orchestration for project {project.id}")

        # Get available agents
        available_agents = [
            agent
            for agent in project.registered_agents.values()
            if agent.status != AgentStatus.OFFLINE
        ]

        # Check for timeout sessions
        self._handle_timeout_sessions(project)

        # Resolve conflicts
        conflicts = self._detect_conflicts(project)
        if conflicts:
            self._resolve_conflicts(project, conflicts)

        # Assign unassigned trees
        new_assignments = self.strategy.assign_work(project, available_agents)
        for tree_id, agent_id in new_assignments.items():
            project.assign_agent_to_tree(agent_id, tree_id)
            self.logger.info(f"Assigned tree {tree_id} to agent {agent_id}")

        # Get next tasks for each agent
        agent_recommendations = {}
        for agent_id, agent in project.registered_agents.items():
            if agent.is_available():
                next_tasks = project.get_available_work_for_agent(agent_id)
                if next_tasks:
                    # Prioritize tasks
                    recommended_task = self._prioritize_tasks_for_agent(
                        agent, next_tasks
                    )
                    agent_recommendations[agent_id] = recommended_task

        return {
            "orchestration_timestamp": datetime.now().isoformat(),
            "project_id": project.id,
            "new_assignments": new_assignments,
            "agent_recommendations": {
                agent_id: task.id.value if task else None
                for agent_id, task in agent_recommendations.items()
            },
            "conflicts_detected": len(conflicts),
            "conflicts_resolved": len(conflicts),  # Assuming all conflicts are resolved
            "active_sessions": len(project.active_work_sessions),
            "available_agents": len([a for a in available_agents if a.is_available()]),
        }

    def coordinate_cross_tree_dependencies(self, project: Project) -> List[Dict]:
        """Coordinate and validate cross-tree dependencies"""
        dependency_issues = []

        for (
            dependent_task_id,
            prerequisite_ids,
        ) in project.cross_tree_dependencies.items():
            dependent_tree = project._find_task_tree(dependent_task_id)
            if not dependent_tree:
                continue

            for prerequisite_id in prerequisite_ids:
                prerequisite_tree = project._find_task_tree(prerequisite_id)
                if not prerequisite_tree:
                    dependency_issues.append(
                        {
                            "type": "missing_prerequisite",
                            "dependent_task": dependent_task_id,
                            "missing_prerequisite": prerequisite_id,
                        }
                    )
                    continue

                prerequisite_task = prerequisite_tree.get_task(prerequisite_id)
                if prerequisite_task and not prerequisite_task.status.is_done():
                    # Check if prerequisite is being worked on
                    prerequisite_agent = project.agent_assignments.get(
                        prerequisite_tree.id
                    )
                    if prerequisite_agent:
                        agent = project.registered_agents.get(prerequisite_agent)
                        if agent and prerequisite_id not in agent.active_tasks:
                            dependency_issues.append(
                                {
                                    "type": "prerequisite_not_active",
                                    "dependent_task": dependent_task_id,
                                    "prerequisite_task": prerequisite_id,
                                    "prerequisite_agent": prerequisite_agent,
                                    "recommendation": "prioritize_prerequisite",
                                }
                            )

        return dependency_issues

    def balance_workload(self, project: Project) -> Dict[str, any]:
        """Balance workload across agents"""
        agents = list(project.registered_agents.values())

        # Calculate workload statistics
        workloads = [(agent.id, agent.get_workload_percentage()) for agent in agents]
        workloads.sort(key=lambda x: x[1])

        # Identify overloaded and underloaded agents
        overloaded_agents = [
            agent_id for agent_id, workload in workloads if workload > 80.0
        ]
        underloaded_agents = [
            agent_id for agent_id, workload in workloads if workload < 50.0
        ]

        rebalancing_recommendations = []

        # Suggest task reassignments
        for overloaded_agent_id in overloaded_agents:
            agent = project.registered_agents[overloaded_agent_id]

            # Find tasks that could be reassigned
            for task_id in agent.active_tasks:
                task_tree = project._find_task_tree(task_id)
                if task_tree:
                    # Find suitable underloaded agents
                    for underloaded_agent_id in underloaded_agents:
                        underloaded_agent = project.registered_agents[
                            underloaded_agent_id
                        ]

                        # Check if underloaded agent can handle the task
                        task = task_tree.get_task(task_id)
                        if task and self._can_agent_handle_task(
                            underloaded_agent, task
                        ):
                            rebalancing_recommendations.append(
                                {
                                    "type": "reassign_task",
                                    "from_agent": overloaded_agent_id,
                                    "to_agent": underloaded_agent_id,
                                    "task_id": task_id,
                                    "tree_id": task_tree.id,
                                }
                            )
                            break

        return {
            "workload_analysis": {
                "overloaded_agents": overloaded_agents,
                "underloaded_agents": underloaded_agents,
                "average_workload": sum(w[1] for w in workloads) / len(workloads),
                "workload_distribution": workloads,
            },
            "rebalancing_recommendations": rebalancing_recommendations,
        }

    def _handle_timeout_sessions(self, project: Project) -> None:
        """Handle sessions that have timed out"""
        for session_id, session in list(project.active_work_sessions.items()):
            if session.is_timeout_due():
                session.timeout_session()

                # Remove from active sessions
                del project.active_work_sessions[session_id]

                # Update agent status
                agent = project.registered_agents.get(session.agent_id)
                if agent:
                    agent.complete_task(session.task_id, success=False)

                self.logger.warning(f"Session {session_id} timed out")

    def _detect_conflicts(self, project: Project) -> List[Dict]:
        """Detect conflicts in the project"""
        conflicts = []

        # Check for resource conflicts
        resource_usage = {}
        for session in project.active_work_sessions.values():
            for resource in session.resources_locked:
                if resource in resource_usage:
                    conflicts.append(
                        {
                            "type": "resource_conflict",
                            "resource": resource,
                            "conflicting_sessions": [
                                resource_usage[resource],
                                session.id,
                            ],
                        }
                    )
                else:
                    resource_usage[resource] = session.id

        return conflicts

    def _resolve_conflicts(self, project: Project, conflicts: List[Dict]) -> None:
        """Resolve detected conflicts"""
        for conflict in conflicts:
            if conflict["type"] == "resource_conflict":
                # Resolve by priority (newer session gets priority)
                sessions = conflict["conflicting_sessions"]
                if len(sessions) >= 2:
                    older_session_id = sessions[0]
                    if older_session_id in project.active_work_sessions:
                        older_session = project.active_work_sessions[older_session_id]
                        older_session.unlock_resource(conflict["resource"])
                        self.logger.info(
                            f"Resolved resource conflict for {conflict['resource']}"
                        )

    def _prioritize_tasks_for_agent(
        self, agent: Agent, tasks: List[Task]
    ) -> Optional[Task]:
        """Prioritize tasks for a specific agent"""
        if not tasks:
            return None

        # Score tasks based on agent preferences and task characteristics
        task_scores = []
        for task in tasks:
            score = 0.0

            # Priority preference
            priority_scores = {"high": 3, "medium": 2, "low": 1}
            task_priority_score = priority_scores.get(task.priority.value, 1)

            if task.priority.value == agent.priority_preference:
                score += task_priority_score * 2
            else:
                score += task_priority_score

            # Task age (older tasks get slight priority)
            if task.created_at:
                age_days = (datetime.now() - task.created_at).days
                score += min(age_days * 0.1, 1.0)

            task_scores.append((task, score))

        # Sort by score and return highest
        task_scores.sort(key=lambda x: x[1], reverse=True)
        return task_scores[0][0]

    def _can_agent_handle_task(self, agent: Agent, task: Task) -> bool:
        """Check if an agent can handle a specific task"""
        # Basic capability check
        task_text = f"{task.title} {task.description}".lower()

        # Frontend tasks
        if any(keyword in task_text for keyword in ["frontend", "ui", "react"]):
            return agent.has_capability(AgentCapability.FRONTEND_DEVELOPMENT)

        # Backend tasks
        if any(keyword in task_text for keyword in ["backend", "api", "server"]):
            return agent.has_capability(AgentCapability.BACKEND_DEVELOPMENT)

        # Default: agent can handle general tasks
        return True
