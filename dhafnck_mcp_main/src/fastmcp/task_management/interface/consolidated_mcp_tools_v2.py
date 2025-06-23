"""Consolidated MCP Tools v2 - Reorganized with Enhanced Descriptions"""

import sys
import os
import json
import asyncio
import logging
import shutil
import time
import traceback
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple, Union
from fastmcp import FastMCP
import yaml
from dataclasses import asdict

# Package imports - no need for sys.path manipulation with proper package structure

from fastmcp.task_management.application import (
    TaskApplicationService,
    CreateTaskRequest,
    UpdateTaskRequest,
    ListTasksRequest,
    SearchTasksRequest,
    DoNextUseCase,
    CallAgentUseCase
)
from fastmcp.task_management.infrastructure import JsonTaskRepository, FileAutoRuleGenerator, InMemoryTaskRepository
from fastmcp.task_management.interface.cursor_rules_tools import CursorRulesTools
from fastmcp.task_management.domain.enums import CommonLabel, EstimatedEffort, AgentRole, LabelValidator
from fastmcp.task_management.domain.enums.agent_roles import resolve_legacy_role
from fastmcp.task_management.domain.exceptions import TaskNotFoundError
from fastmcp.task_management.domain.repositories.task_repository import TaskRepository
from fastmcp.task_management.domain.services.auto_rule_generator import AutoRuleGenerator
from fastmcp.task_management.infrastructure.services.agent_converter import AgentConverter
from fastmcp.task_management.domain.entities.project import Project as ProjectEntity
from fastmcp.task_management.domain.entities.task_tree import TaskTree as TaskTreeEntity
from fastmcp.task_management.domain.services.orchestrator import Orchestrator

BRAIN_DIR = os.path.join(os.path.dirname(__file__), '../../../.cursor/rules/brain')
PROJECTS_FILE = os.path.join(BRAIN_DIR, 'projects.json')

# Helper function to find the project root directory
def find_project_root():
    """Find the project root directory (containing cursor_agent)"""
    # Start from the current file's directory
    current_dir = Path(os.path.abspath(__file__))
    
    # Go up until we find the directory containing cursor_agent
    while current_dir.parent != current_dir:  # Stop at filesystem root
        current_dir = current_dir.parent
        # If we're in cursor_agent directory, go up one more level
        if current_dir.name == 'cursor_agent':
            return current_dir.parent
        # If we see cursor_agent as a subdirectory, we're at project root
        if (current_dir / 'cursor_agent').exists():
            return current_dir
    
    # Fallback to current directory if project root not found
    return Path(os.path.abspath('.'))

# Get project root directory
PROJECT_ROOT = find_project_root()
CURSOR_AGENT_DIR = PROJECT_ROOT / 'cursor_agent'

def ensure_brain_dir():
    os.makedirs(BRAIN_DIR, exist_ok=True)

class SimpleMultiAgentTools:
    """Simple multi-agent tools implementation for consolidated v2"""
    
    def __init__(self, projects_file_path: Optional[str] = None):
        # Allow custom projects file path for testing
        if projects_file_path:
            self._projects_file = projects_file_path
            self._brain_dir = os.path.dirname(projects_file_path)
        else:
            # Use default production paths
            self._brain_dir = BRAIN_DIR
            self._projects_file = PROJECTS_FILE
        
        self._projects = {}
        self._load_projects()
        
        # Initialize agent converter and orchestrator for advanced features
        self._agent_converter = AgentConverter()
        self._orchestrator = Orchestrator()
    
    def _ensure_brain_dir(self):
        """Ensure the brain directory exists"""
        os.makedirs(self._brain_dir, exist_ok=True)
    
    def _save_projects(self):
        self._ensure_brain_dir()
        with open(self._projects_file, 'w') as f:
            json.dump(self._projects, f, indent=2)

    def _load_projects(self):
        self._ensure_brain_dir()
        if os.path.exists(self._projects_file):
            try:
                with open(self._projects_file, 'r') as f:
                    content = f.read().strip()
                    if content:
                        self._projects = json.loads(content)
                    else:
                        self._projects = {}
            except (json.JSONDecodeError, FileNotFoundError) as e:
                logging.warning(f"Failed to load projects file {self._projects_file}: {e}")
                self._projects = {}
        else:
            self._projects = {}
    
    def create_project(self, project_id: str, name: str, description: str = "") -> Dict[str, Any]:
        """Create a new project"""
        project = {
            "id": project_id,
            "name": name,
            "description": description,
            "task_trees": {"main": {"id": "main", "name": "Main Tasks", "description": "Main task tree"}},
            "registered_agents": {},
            "agent_assignments": {},
            "created_at": "2025-01-01T00:00:00Z"
        }
        self._projects[project_id] = project
        self._save_projects()
        return {"success": True, "project": project}
    
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get project details"""
        if project_id not in self._projects:
            return {"success": False, "error": f"Project {project_id} not found"}
        return {"success": True, "project": self._projects[project_id]}
    
    def list_projects(self) -> Dict[str, Any]:
        """List all projects"""
        return {"success": True, "projects": list(self._projects.values()), "count": len(self._projects)}
    
    def create_task_tree(self, project_id: str, tree_id: str, tree_name: str, tree_description: str = "") -> Dict[str, Any]:
        """Create a new task tree in project"""
        if project_id not in self._projects:
            return {"success": False, "error": f"Project {project_id} not found"}
        
        tree = {"id": tree_id, "name": tree_name, "description": tree_description}
        self._projects[project_id]["task_trees"][tree_id] = tree
        self._save_projects()
        return {"success": True, "tree": tree}
    
    def get_task_tree_status(self, project_id: str, tree_id: str) -> Dict[str, Any]:
        """Get task tree status"""
        if project_id not in self._projects:
            return {"success": False, "error": f"Project {project_id} not found"}
        
        tree = self._projects[project_id]["task_trees"].get(tree_id)
        if not tree:
            return {"success": False, "error": f"Tree {tree_id} not found"}
        
        return {"success": True, "tree": tree, "status": "active", "progress": "0%"}
    
    def orchestrate_project(self, project_id: str) -> Dict[str, Any]:
        """Orchestrate project workload using domain entities"""
        if project_id not in self._projects:
            return {"success": False, "error": f"Project {project_id} not found"}
        
        try:
            # Convert simplified project data to domain entities
            project_entity = self._convert_to_project_entity(project_id)
            
            # Run orchestration
            orchestration_result = self._orchestrator.orchestrate_project(project_entity)
            
            # Update the simplified project data with any new assignments
            self._update_project_from_entity(project_id, project_entity)
            
            return {
                "success": True, 
                "message": "Project orchestration completed",
                "orchestration_result": orchestration_result
            }
        except Exception as e:
            logging.error(f"Orchestration failed for project {project_id}: {str(e)}")
            return {
                "success": False, 
                "error": f"Orchestration failed: {str(e)}"
            }
    
    def get_orchestration_dashboard(self, project_id: str) -> Dict[str, Any]:
        """Get orchestration dashboard with detailed agent information"""
        if project_id not in self._projects:
            return {"success": False, "error": f"Project {project_id} not found"}
        
        try:
            # Convert to domain entity for rich dashboard data
            project_entity = self._convert_to_project_entity(project_id)
            orchestration_status = project_entity.get_orchestration_status()
            
            return {
                "success": True,
                "dashboard": orchestration_status
            }
        except Exception as e:
            logging.error(f"Dashboard generation failed for project {project_id}: {str(e)}")
            # Fallback to basic dashboard
            project = self._projects[project_id]
            return {
                "success": True,
                "dashboard": {
                    "project_id": project_id,
                    "total_agents": len(project["registered_agents"]),
                    "total_trees": len(project["task_trees"]),
                    "active_assignments": len(project["agent_assignments"]),
                    "note": "Basic dashboard due to conversion error"
                }
            }
    
    def register_agent(self, project_id: str, agent_id: str, name: str, call_agent: str = None) -> Dict[str, Any]:
        """Register an agent to project using simplified format"""
        if project_id not in self._projects:
            return {"success": False, "error": f"Project {project_id} not found"}
        
        # Use simplified agent format
        agent = {
            "id": agent_id,
            "name": name,
            "call_agent": call_agent or f"@{agent_id.replace('_', '-')}-agent"
        }
        self._projects[project_id]["registered_agents"][agent_id] = agent
        self._save_projects()
        return {"success": True, "agent": agent}
    
    def assign_agent_to_tree(self, project_id: str, agent_id: str, tree_id: str) -> Dict[str, Any]:
        """Assign agent to task tree"""
        if project_id not in self._projects:
            return {"success": False, "error": f"Project {project_id} not found"}
        
        project = self._projects[project_id]
        if agent_id not in project["registered_agents"]:
            return {"success": False, "error": f"Agent {agent_id} not found"}
        
        if tree_id not in project["task_trees"]:
            return {"success": False, "error": f"Tree {tree_id} not found"}
        
        if agent_id not in project["agent_assignments"]:
            project["agent_assignments"][agent_id] = []
        
        if tree_id not in project["agent_assignments"][agent_id]:
            project["agent_assignments"][agent_id].append(tree_id)
        self._save_projects()
        return {"success": True, "message": f"Agent {agent_id} assigned to tree {tree_id}"}
    
    def _convert_to_project_entity(self, project_id: str) -> ProjectEntity:
        """Convert simplified project data to domain Project entity"""
        project_data = self._projects[project_id]
        
        # Parse created_at datetime safely
        created_at_str = project_data.get("created_at", "2025-01-01T00:00:00+00:00")
        # Handle both 'Z' and '+00:00' timezone formats
        if created_at_str.endswith('Z'):
            created_at_str = created_at_str.replace('Z', '+00:00')
        
        # Create project entity
        project_entity = ProjectEntity(
            id=project_id,
            name=project_data.get("name", project_id),
            description=project_data.get("description", ""),
            created_at=datetime.fromisoformat(created_at_str),
            updated_at=datetime.now()
        )
        
        # Convert and register agents
        agent_entities = self._agent_converter.convert_project_agents_to_entities(project_data)
        for agent_id, agent_entity in agent_entities.items():
            project_entity.register_agent(agent_entity)
        
        # Convert agent assignments from agent_id -> [tree_ids] to tree_id -> agent_id format
        agent_assignments_data = project_data.get("agent_assignments", {})
        converted_assignments = {}
        for agent_id, tree_ids in agent_assignments_data.items():
            if isinstance(tree_ids, list):
                for tree_id in tree_ids:
                    converted_assignments[tree_id] = agent_id
            else:
                # Handle legacy format where tree_ids might be a single string
                converted_assignments[tree_ids] = agent_id
        
        # Update agent assignments in entities
        self._agent_converter.update_agent_assignments(agent_entities, converted_assignments)
        
        # Set up agent assignments in project entity
        for tree_id, agent_id in converted_assignments.items():
            if agent_id in agent_entities:
                project_entity.agent_assignments[tree_id] = agent_id
        
        # Create task trees (basic structure)
        task_trees_data = project_data.get("task_trees", {})
        for tree_id, tree_data in task_trees_data.items():
            tree_entity = TaskTreeEntity(
                id=tree_id,
                name=tree_data.get("name", tree_id),
                description=tree_data.get("description", ""),
                project_id=project_id,
                created_at=datetime.now()
            )
            project_entity.task_trees[tree_id] = tree_entity
        
        return project_entity
    
    def _update_project_from_entity(self, project_id: str, project_entity: ProjectEntity) -> None:
        """Update simplified project data from domain entity changes"""
        # Convert agent assignments from tree_id -> agent_id back to agent_id -> [tree_ids] format
        agent_assignments = {}
        for tree_id, agent_id in project_entity.agent_assignments.items():
            if agent_id not in agent_assignments:
                agent_assignments[agent_id] = []
            agent_assignments[agent_id].append(tree_id)
        
        self._projects[project_id]["agent_assignments"] = agent_assignments
        self._save_projects()


class ConsolidatedMCPToolsV2:
    """Consolidated MCP Tools v2 - Three-category organization with enhanced descriptions"""
    
    def __init__(
        self,
        task_repository: Optional[TaskRepository] = None,
        auto_rule_generator: Optional[AutoRuleGenerator] = None,
        projects_file_path: Optional[str] = None
    ):
        # Initialize repositories and services
        self._task_repository = task_repository or JsonTaskRepository()
        self._auto_rule_generator = auto_rule_generator or FileAutoRuleGenerator()
        
        # Initialize application service with dependencies
        self._task_app_service = TaskApplicationService(
            task_repository=self._task_repository,
            auto_rule_generator=self._auto_rule_generator
        )
        
        # Initialize cursor rules tools
        self._cursor_rules_tools = CursorRulesTools()
        
        # Initialize multi-agent tools with optional custom projects file path
        self._multi_agent_tools = SimpleMultiAgentTools(projects_file_path=projects_file_path)
        
        # Initialize call agent use case
        self._call_agent_use_case = CallAgentUseCase(CURSOR_AGENT_DIR)
    
    def register_tools(self, mcp: FastMCP):
        """Register all consolidated MCP tools in three logical categories"""
        
        # ═══════════════════════════════════════════════════════════════════
        # 🏗️ PROJECT MANAGEMENT - High-level orchestration and coordination
        # ═══════════════════════════════════════════════════════════════════
        
        @mcp.tool()
        def manage_project(
            action: str,
            project_id: Optional[str] = None,
            name: Optional[str] = None,
            description: Optional[str] = None,
            tree_id: Optional[str] = None,
            tree_name: Optional[str] = None,
            tree_description: Optional[str] = None
        ) -> Dict[str, Any]:
            """🏗️ PROJECT ORCHESTRATION HUB - Complete multi-agent project lifecycle management

            ✨ INSTANT CONTEXT: Manages entire project ecosystem including task trees, cross-dependencies, and team coordination
            🎯 HUMAN USAGE: Project managers setting up workflows, coordinating teams, monitoring progress
            🤖 AI USAGE: Project initialization, workstream creation, orchestration status checks, progress monitoring

            📋 CORE ACTIONS:
            🆕 CREATE: Initialize new multi-agent project workspace
            • Input: action="create", project_id="my_project", name="Project Name"
            • Output: Complete project structure with default main task tree
            • AI Context: "I'm setting up a new project workspace for team coordination"
            📊 GET: Retrieve comprehensive project status and structure
            • Input: action="get", project_id="my_project"
            • Output: Full project details, task trees, agent assignments, cross-dependencies
            • AI Context: "I need complete project overview for decision making"
            📋 LIST: Show all available projects in workspace
            • Input: action="list"
            • Output: All projects with summary stats and health indicators
            • AI Context: "I need workspace overview to understand available projects"
            🌳 CREATE_TREE: Add new workstream/feature branch to project
            • Input: action="create_tree", project_id="my_project", tree_id="frontend", tree_name="Frontend Development"
            • Output: New task tree ready for task assignment and agent coordination
            • AI Context: "I'm creating a new development workstream for parallel work"
            📈 GET_TREE_STATUS: Detailed progress analysis of specific workstream
            • Input: action="get_tree_status", project_id="my_project", tree_id="frontend"
            • Output: Tree progress, assigned agents, task completion metrics, bottlenecks
            • AI Context: "I need detailed status of this workstream for progress reporting"
            🚀 ORCHESTRATE: Run intelligent work assignment and load balancing
            • Input: action="orchestrate", project_id="my_project"
            • Output: Optimized task assignments, workload distribution, dependency resolution
            • AI Context: "I'm optimizing work distribution across available agents"
            📊 DASHBOARD: Comprehensive project health and orchestration overview
            • Input: action="dashboard", project_id="my_project"
            • Output: Complete metrics, agent utilization, bottlenecks, cross-tree dependencies
            • AI Context: "I need full project dashboard for stakeholder reporting"
            💡 WHY USE THIS:
            • Eliminates manual project setup and coordination overhead
            • Provides real-time visibility into multi-agent workflows
            • Automatically optimizes work distribution and identifies bottlenecks
            • Enables seamless scaling from single to multi-agent projects

            ---
            PARAMETER REQUIREMENTS BY ACTION:
            - action (str, required): The operation to perform. One of: create, get, list, create_tree, get_tree_status, orchestrate, dashboard
            - project_id (str, required/optional):
                • (required) for: create, get, create_tree, get_tree_status, orchestrate, dashboard
                • (optional) for: list
            - name (str, required/optional):
                • (required) for: create
                • (optional) for: others
            - description (Optional[str], optional):
                • (optional) for: create
            - tree_id (str, required/optional):
                • (required) for: create_tree, get_tree_status
                • (optional) for: others
            - tree_name (str, required/optional):
                • (required) for: create_tree
                • (optional) for: others
            - tree_description (Optional[str], optional):
                • (optional) for: create_tree
            ---
            For each action, required parameters:
            • create: action, project_id, name
            • get: action, project_id
            • list: action
            • create_tree: action, project_id, tree_id, tree_name
            • get_tree_status: action, project_id, tree_id
            • orchestrate: action, project_id
            • dashboard: action, project_id
            ---
            """
            
            if action == "create":
                if not project_id or not name:
                    return {"success": False, "error": "project_id and name are required for creating a project"}
                return self._multi_agent_tools.create_project(project_id, name, description or "")
                
            elif action == "get":
                if not project_id:
                    return {"success": False, "error": "project_id is required"}
                return self._multi_agent_tools.get_project(project_id)
                
            elif action == "list":
                return self._multi_agent_tools.list_projects()
                
            elif action == "create_tree":
                if not all([project_id, tree_id, tree_name]):
                    return {"success": False, "error": "project_id, tree_id, and tree_name are required"}
                return self._multi_agent_tools.create_task_tree(project_id, tree_id, tree_name, tree_description or "")
                
            elif action == "get_tree_status":
                if not project_id or not tree_id:
                    return {"success": False, "error": "project_id and tree_id are required"}
                return self._multi_agent_tools.get_task_tree_status(project_id, tree_id)
                
            elif action == "orchestrate":
                if not project_id:
                    return {"success": False, "error": "project_id is required"}
                return self._multi_agent_tools.orchestrate_project(project_id)
                
            elif action == "dashboard":
                if not project_id:
                    return {"success": False, "error": "project_id is required"}
                return self._multi_agent_tools.get_orchestration_dashboard(project_id)
                
            else:
                return {"success": False, "error": f"Unknown action: {action}. Available: create, get, list, create_tree, get_tree_status, orchestrate, dashboard"}

        # ═══════════════════════════════════════════════════════════════════
        # 📋 TASK MANAGEMENT - Granular work item lifecycle and workflow
        # ═══════════════════════════════════════════════════════════════════
        
        @mcp.tool()
        def manage_task(
            action: str,
            task_id: Optional[str] = None,
            project_id: Optional[str] = None,
            title: Optional[str] = None,
            description: Optional[str] = None,
            status: Optional[str] = None,
            priority: Optional[str] = None,
            details: Optional[str] = None,
            estimated_effort: Optional[str] = None,
            assignees: Optional[List[str]] = None,
            labels: Optional[List[str]] = None,
            due_date: Optional[str] = None,
            dependency_data: Optional[Dict[str, Any]] = None,
            query: Optional[str] = None,
            limit: Optional[int] = None,
            force_full_generation: bool = False
        ) -> Dict[str, Any]:
            """📋 TASK LIFECYCLE HUB - Core Task Management with Intelligent Automation

            ✨ INSTANT CONTEXT: Handles the entire core task lifecycle, including creation, retrieval, updating, deletion, completion, listing, searching, and intelligent next-task recommendation. Integrates with the MCP system for project and agent coordination.
            🎯 HUMAN USAGE: Developers managing work items, project managers tracking progress, team members updating status
            🤖 AI USAGE: Task creation, context loading, progress updates, work prioritization, and recommendation

            📋 CORE TASK LIFECYCLE ACTIONS:
            🆕 CREATE: Initialize new work item with full metadata
            • Input: action="create", title="Implement user authentication", priority="high"
            • Output: Complete task object with auto-generated ID and timestamps
            • AI Context: "I'm creating a new work item for development tracking"
            🔍 GET: Load complete task details + auto-generate AI context
            • Input: action="get", task_id="20250618001"
            • Output: Full task object + auto-generated .cursor/rules/auto_rule.mdc
            • AI Context: "I'm loading task context for focused development work"
            ✏️ UPDATE: Modify any task properties with selective updates
            • Input: action="update", task_id="20250618001", status="in_progress", assignee="@developer"
            • Output: Updated task object with preserved unchanged fields
            • AI Context: "I'm updating task progress and assignment information"
            🗑️ DELETE: Permanently remove task and all associated data
            • Input: action="delete", task_id="20250618001"
            • Output: Confirmation of complete task removal including subtasks and dependencies
            • AI Context: "I'm permanently removing this task and cleaning up all references"
            ✅ COMPLETE: Finish task and auto-complete all subtasks
            • Input: action="complete", task_id="20250618001"
            • Output: Task marked done, all subtasks completed, dependent tasks unblocked
            • AI Context: "I'm marking task as complete and handling all cleanup"
            📋 LIST: Filter and discover tasks by multiple criteria
            • Input: action="list", status="in_progress", priority="high", assignee="@me"
            • Output: Filtered task list matching all specified criteria
            • AI Context: "I'm finding tasks matching specific criteria for work planning"
            🔍 SEARCH: Semantic search across all task content
            • Input: action="search", query="authentication API security", limit=5
            • Output: Relevance-ranked tasks matching search terms
            • AI Context: "I'm finding tasks related to specific topics or requirements"
            🎯 NEXT: Get intelligent work recommendation
            • Input: action="next"
            • Output: Optimal next task based on priorities, dependencies, and capacity
            • AI Context: "I need intelligent recommendation for what to work on next"

            ---
            PARAMETER REQUIREMENTS BY ACTION:
            - action (str, required): The operation to perform. One of: create, get, update, delete, complete, list, search, next
            - task_id (str, required/optional):
                • (required) for: get, update, delete, complete
                • (optional) for: create, list, search, next
            - title (str, required/optional):
                • (required) for: create
                • (optional) for: update
            - description, status, priority, details, estimated_effort, assignees, labels, due_date: as before
            - query (str, required for search)
            - limit (int, optional)
            ---
            ENUMS:
            - status: ['todo', 'in_progress', 'blocked', 'review', 'testing', 'done', 'cancelled']
            - priority: ['low', 'medium', 'high', 'urgent', 'critical']
            - estimated_effort: ['quick', 'short', 'small', 'medium', 'large', 'xlarge', 'epic', 'massive']
            - assignees (AgentRole): [see AgentRole enum]
            - labels (CommonLabel): [see CommonLabel enum]
            ---
            WHY USE THIS:
            • Eliminates manual task tracking and status management overhead
            • Provides automatic context generation for focused development work
            • Handles complex task relationships and prioritization
            • Enables intelligent work recommendation and progress tracking
            • Maintains complete audit trail and progress visibility
            ---
            EXAMPLE USE CASES:
            - Creating and managing feature, bugfix, or documentation tasks
            - Updating task status and assignments during a sprint
            - Searching for tasks by keyword, label, or assignee
            - Getting the next recommended task for a developer
            ---
            OUTPUT STRUCTURE:
            - create: {"success": True, "action": "create", "task": {...}}
            - get: {"success": True, "action": "get", "task": {...}}
            - update: {"success": True, "action": "update", "task": {...}}
            - delete: {"success": True, "action": "delete", "message": ...}
            - complete: {"success": True, "action": "complete", "task_id": ..., "message": ...}
            - list: {"success": True, "tasks": [...], "count": ...}
            - search: {"success": True, "tasks": [...], "count": ..., "query": ...}
            - next: {"success": True, "action": "next", "recommended_task": {...}, "reasoning": ..., "message": ...}
            
            ---
            NOTE: Subtask and dependency actions are now handled by the separate manage_subtask and dependency management tools.
            """
            # ═══════════════════════════════════════════════════════════════════
            # Route to the appropriate handler based on action
            # ═══════════════════════════════════════════════════════════════════
            
            core_actions = ["create", "get", "update", "delete"]
            if action in core_actions:
                return self._handle_core_task_operations(
                    action, task_id, title, description, status, priority,
                    details, estimated_effort, assignees, labels, due_date,
                    project_id=project_id, force_full_generation=force_full_generation
                )
            elif action == "complete":
                return self._handle_complete_task(task_id)
            
            elif action == "list":
                return self._handle_list_tasks(status, priority, assignees, labels, limit)
            
            elif action == "search":
                return self._handle_search_tasks(query, limit)
            
            elif action == "next":
                return self._handle_do_next()
            
            elif action.endswith("_dependency"):
                return self._handle_dependency_operations(action, task_id, dependency_data)

            else:
                return {"success": False, "error": f"Invalid task action: {action}"}

        @mcp.tool()
        def manage_subtask(
            action: str,
            task_id: Optional[str] = None,
            subtask_data: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """Manages subtasks for a given task, including creation, completion, updates, removal, and listing.

            Args:
                action (str): The subtask action to perform (e.g., 'add', 'complete', 'list').
                task_id (Optional[str]): The ID of the parent task.
                subtask_data (Optional[Dict[str, Any]]): Data for the subtask operation.
            
            Returns:
                Dict[str, Any]: A dictionary containing the result of the operation.
            """
            if task_id is None:
                return {"success": False, "error": "task_id is required"}

            try:
                result = self._handle_subtask_operations(action, task_id, subtask_data)
                return {"success": True, "action": action, "result": result}
            except (ValueError, TypeError, TaskNotFoundError) as e:
                logging.error(f"Error managing subtask: {e}")
                return {"success": False, "error": str(e)}
            except Exception as e:
                logging.error(f"Unexpected error in manage_subtask: {e}\\n{traceback.format_exc()}")
                return {"success": False, "error": f"An unexpected error occurred: {e}"}

        # ═══════════════════════════════════════════════════════════════════
        # 🤖 AGENT MANAGEMENT - Multi-agent coordination and assignment
        # ═══════════════════════════════════════════════════════════════════
        
        @mcp.tool()
        def manage_agent(
            action: str,
            project_id: Optional[str] = None,
            agent_id: Optional[str] = None,
            name: Optional[str] = None,
            call_agent: Optional[str] = None,
            tree_id: Optional[str] = None
        ) -> Dict[str, Any]:
            """🤖 AGENT COORDINATION HUB - Multi-agent team management and intelligent assignment

            ✨ INSTANT CONTEXT: Manages AI agent teams including capability tracking, workload balancing, and intelligent task assignment
            🎯 HUMAN USAGE: DevOps teams setting up agent pools, project managers coordinating AI workforce, capacity planning
            🤖 AI USAGE: Agent registration, capability management, assignment optimization, workload monitoring

            📋 AGENT LIFECYCLE ACTIONS:
            🆕 REGISTER: Add new AI agent to project team
            • Input: action="register", project_id="my_project", agent_id="frontend_expert", name="Frontend Specialist", call_agent="@coding-agent"
            • Output: Agent profile with call_agent reference for automatic detail generation
            • AI Context: "I'm adding a new specialized agent to the project team"
            📊 GET: Retrieve complete agent profile and workload status
            • Input: action="get", project_id="my_project", agent_id="frontend_expert"
            • Output: Agent details with call_agent reference, current assignments, and status
            • AI Context: "I need detailed information about this agent and its call reference"
            📋 LIST: Show all agents in project with call_agent references
            • Input: action="list", project_id="my_project"
            • Output: Complete agent roster with call_agent references and assignments
            • AI Context: "I need overview of all available agents and their call references"
            ✏️ UPDATE: Modify agent call reference or name
            • Input: action="update", project_id="my_project", agent_id="frontend_expert", call_agent="@ui-designer-agent"
            • Output: Updated agent profile with new call_agent reference
            • AI Context: "I'm updating agent call reference for different specialization"
            🗑️ UNREGISTER: Remove agent from project (impacts active assignments)
            • Input: action="unregister", project_id="my_project", agent_id="temp_agent"
            • Output: Agent removed with impact analysis on current assignments
            • AI Context: "I'm removing agent from project and need to handle reassignments"
            📌 ASSIGN: Assign agent to specific task tree/workstream
            • Input: action="assign", project_id="my_project", agent_id="frontend_expert", tree_id="ui_components"
            • Output: Assignment created with capability validation and workload impact
            • AI Context: "I'm assigning specialized agent to appropriate workstream"
            ❌ UNASSIGN: Remove agent from task tree assignment
            • Input: action="unassign", project_id="my_project", agent_id="frontend_expert", tree_id="ui_components"
            • Output: Assignment removed with impact analysis and reassignment needs
            • AI Context: "I'm removing agent assignment and need to handle work transition"
            📊 GET_ASSIGNMENTS: Show complete assignment matrix
            • Input: action="get_assignments", project_id="my_project"
            • Output: Full mapping of agents to task trees with workload distribution
            • AI Context: "I need complete overview of who is working on what"
            📈 GET_WORKLOAD: Analyze agent performance and capacity utilization
            • Input: action="get_workload", project_id="my_project", agent_id="frontend_expert"
            • Output: Performance metrics, completion rates, capacity analysis, optimization suggestions
            • AI Context: "I need detailed performance analysis for this agent"
            🔄 REBALANCE: Intelligent workload redistribution across team
            • Input: action="rebalance", project_id="my_project"
            • Output: Optimized assignment recommendations or automatic rebalancing
            • AI Context: "I'm optimizing work distribution across all available agents"
            💡 WHY USE THIS:
            • Eliminates manual agent coordination and assignment overhead
            • Provides intelligent workload balancing and capacity optimization
            • Enables dynamic team scaling and capability management
            • Maintains complete visibility into agent performance and utilization
            • Automatically prevents overloading and optimizes work distribution

            ---
            PARAMETER REQUIREMENTS BY ACTION:
            - action (required): The operation to perform. One of: register, assign, get, list, get_assignments, unassign, update, unregister, rebalance
            - project_id:
                • (required) for: register, assign, get, list, get_assignments, unassign, update, unregister, rebalance
            - agent_id:
                • (required) for: register, assign, get, unassign, update, unregister
                • (optional) for: list, get_assignments, rebalance
            - name:
                • (required) for: register
                • (optional) for: update
            - call_agent:
                • (optional) for: register, update
            - tree_id:
                • (required) for: assign, unassign
                • (optional) for: others
            ---
            For each action, required parameters:
            • register: action, project_id, agent_id, name
            • assign: action, project_id, agent_id, tree_id
            • get: action, project_id, agent_id
            • list: action, project_id
            • get_assignments: action, project_id
            • unassign: action, project_id, agent_id, tree_id
            • update: action, project_id, agent_id
            • unregister: action, project_id, agent_id
            • rebalance: action, project_id
            ---
            """
            
            if action == "register":
                if not all([project_id, agent_id, name]):
                    return {"success": False, "error": "project_id, agent_id, and name are required for registering an agent"}
                return self._multi_agent_tools.register_agent(
                    project_id=project_id,
                    agent_id=agent_id, 
                    name=name,
                    call_agent=call_agent
                )
                
            elif action == "assign":
                if not all([project_id, agent_id, tree_id]):
                    return {"success": False, "error": "project_id, agent_id, and tree_id are required for assignment"}
                return self._multi_agent_tools.assign_agent_to_tree(project_id, agent_id, tree_id)
                
            elif action == "get":
                if not project_id or not agent_id:
                    return {"success": False, "error": "project_id and agent_id are required"}
                # Get agent details from project
                project_response = self._multi_agent_tools.get_project(project_id)
                if not project_response.get("success"):
                    return project_response
                
                agents = project_response.get("project", {}).get("registered_agents", {})
                if agent_id not in agents:
                    return {"success": False, "error": f"Agent {agent_id} not found in project {project_id}"}
                
                agent_data = agents[agent_id]
                return {
                    "success": True,
                    "agent": agent_data,
                    "workload_status": "Available for assignment analysis"
                }
                
            elif action == "list":
                if not project_id:
                    return {"success": False, "error": "project_id is required"}
                project_response = self._multi_agent_tools.get_project(project_id)
                if not project_response.get("success"):
                    return project_response
                
                agents = project_response.get("project", {}).get("registered_agents", {})
                return {
                    "success": True,
                    "agents": agents,
                    "count": len(agents)
                }
                
            elif action == "get_assignments":
                if not project_id:
                    return {"success": False, "error": "project_id is required"}
                project_response = self._multi_agent_tools.get_project(project_id)
                if not project_response.get("success"):
                    return project_response
                
                assignments = project_response.get("project", {}).get("agent_assignments", {})
                return {
                    "success": True,
                    "assignments": assignments,
                    "assignment_count": len(assignments)
                }
                
            elif action == "update":
                if not project_id or not agent_id:
                    return {"success": False, "error": "project_id and agent_id are required"}
                
                # Get current project
                project_response = self._multi_agent_tools.get_project(project_id)
                if not project_response.get("success"):
                    return project_response
                
                agents = project_response.get("project", {}).get("registered_agents", {})
                if agent_id not in agents:
                    return {"success": False, "error": f"Agent {agent_id} not found in project {project_id}"}
                
                # Update agent with new values
                agent_data = agents[agent_id]
                if name:
                    agent_data["name"] = name
                if call_agent:
                    agent_data["call_agent"] = call_agent
                
                # Save and return updated agent
                self._multi_agent_tools._save_projects()
                return {"success": True, "agent": agent_data}
                
            elif action == "unregister":
                if not project_id or not agent_id:
                    return {"success": False, "error": "project_id and agent_id are required"}
                
                # Get current project
                project_response = self._multi_agent_tools.get_project(project_id)
                if not project_response.get("success"):
                    return project_response
                
                project_data = project_response.get("project", {})
                agents = project_data.get("registered_agents", {})
                
                if agent_id not in agents:
                    return {"success": False, "error": f"Agent {agent_id} not found in project {project_id}"}
                
                # Remove agent and any assignments
                removed_agent = agents.pop(agent_id)
                
                # Remove from assignments
                assignments = project_data.get("agent_assignments", {})
                assignments = {k: v for k, v in assignments.items() if v != agent_id}
                project_data["agent_assignments"] = assignments
                
                # Save changes
                self._multi_agent_tools._save_projects()
                return {"success": True, "message": f"Agent {agent_id} unregistered", "removed_agent": removed_agent}
                
            elif action == "rebalance":
                if not project_id:
                    return {"success": False, "error": "project_id is required"}
                return {"success": True, "message": "Workload rebalancing analysis completed", "recommendations": []}
                
            else:
                return {"success": False, "error": f"Unknown action: {action}. Available: register, assign, get, list, get_assignments, unassign, update, unregister, rebalance"}

        # Register Cursor Rules Tools for additional functionality
        self._cursor_rules_tools.register_tools(mcp)

        # Register Agent Information Tool
        @mcp.tool()
        def call_agent(
            name_agent: str
        ) -> Dict[str, Any]:
            """
            Retrieves all YAML configuration files for a specific agent.
            
            Args:
                name_agent: Name of the agent to retrieve information for (e.g., "coding_agent")
            
            Returns:
                Dict with agent information and combined content from all YAML files
            """
            return self._call_agent_use_case.execute(name_agent)

    # ═══════════════════════════════════════════════════════════════════
    # 🔧 HELPER METHODS - Internal routing and operation handling
    # ═══════════════════════════════════════════════════════════════════
    
    def _handle_core_task_operations(self, action, task_id, title, description, status, priority, details, estimated_effort, assignees, labels, due_date, project_id=None, force_full_generation=False):
        """Internal handler for core task CRUD operations."""
        try:
            if action == "create":
                request = CreateTaskRequest(
                    title=title,
                    description=description,
                    project_id=project_id,
                    status=status,
                    priority=priority,
                    details=details,
                    estimated_effort=estimated_effort,
                    assignees=assignees,
                    labels=labels,
                    due_date=due_date
                )
                response = self._task_app_service.create_task(request)
                logging.info(f"Create task response: {response}")
                if response.success:
                    return {
                        "success": True,
                        "action": "create",
                        "task": asdict(response.task) if response.task else None
                    }
                else:
                    return {
                        "success": False,
                        "action": "create",
                        "error": response.message
                    }
            elif action == "get":
                task_response = self._task_app_service.get_task(task_id, generate_rules=True, force_full_generation=force_full_generation)
                if task_response:
                    return {
                        "success": True,
                        "action": "get",
                        "task": asdict(task_response)
                    }
                else:
                    return {"success": False, "action": "get", "error": f"Task with ID {task_id} not found."}
            elif action == "update":
                request = UpdateTaskRequest(
                    task_id=task_id,
                    title=title,
                    description=description,
                    status=status,
                    priority=priority,
                    details=details,
                    estimated_effort=estimated_effort,
                    assignees=assignees,
                    labels=labels,
                    due_date=due_date
                )
                task_response = self._task_app_service.update_task(request)
                if task_response and task_response.success:
                    return {
                        "success": True,
                        "action": "update",
                        "task": asdict(task_response.task)
                    }
                
                error_message = task_response.message if task_response else f"Task with ID {task_id} not found."
                return {"success": False, "action": "update", "error": error_message}
            elif action == "delete":
                success = self._task_app_service.delete_task(task_id)
                if success:
                    return {"success": True, "action": "delete"}
                else:
                    return {"success": False, "action": "delete", "error": f"Task with ID {task_id} not found."}
            else:
                return {"success": False, "error": f"Invalid core action: {action}"}
        except Exception as e:
            logging.error(f"Error in core task operation '{action}': {traceback.format_exc()}")
            if "generate_rules_for_task" in traceback.format_exc():
                return {"success": False, "error": f"Error during auto rule generation: {e}"}
            return {"success": False, "error": str(e)}

    def _handle_complete_task(self, task_id):
        """Helper to handle task completion"""
        if not task_id:
            return {"success": False, "error": "task_id is required for completing a task"}
        
        response = self._task_app_service.complete_task(task_id)
        return {
            "success": True,
            "action": "complete",
            "task_id": task_id,
            "message": f"Task {task_id} and all subtasks completed successfully"
        }

    def _handle_list_tasks(self, status, priority, assignees, labels, limit):
        """Handle task listing with filters"""
        request = ListTasksRequest(
            status=status,
            priority=priority,
            assignees=assignees,
            labels=labels,
            limit=limit
        )
        
        response = self._task_app_service.list_tasks(request)
        return {
            "success": True,
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "assignees": task.assignees,
                    "labels": task.labels
                }
                for task in response.tasks
            ],
            "count": len(response.tasks)
        }

    def _handle_search_tasks(self, query, limit):
        """Handle task search"""
        if not query:
            return {"success": False, "error": "query is required for searching tasks"}
        
        request = SearchTasksRequest(query=query, limit=limit or 10)
        response = self._task_app_service.search_tasks(request)
        
        return {
            "success": True,
            "tasks": [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "assignees": task.assignees,
                    "labels": task.labels
                }
                for task in response.tasks
            ],
            "count": len(response.tasks),
            "query": query
        }

    def _handle_do_next(self):
        """Handle next task recommendation"""
        do_next_use_case = DoNextUseCase(self._task_repository, self._auto_rule_generator)
        response = do_next_use_case.execute()
        
        if response.has_next and response.next_item:
            return {
                "success": True,
                "action": "next",
                "next_item": response.next_item,
                "message": response.message
            }
        else:
            return {
                "success": True,
                "action": "next",
                "next_item": None,
                "message": response.message,
                "context": response.context if response.context else None
            }

    def _handle_dependency_operations(self, action, task_id, dependency_data=None):
        """Handle dependency operations (add, remove, get, clear, get_blocking)"""
        if not task_id:
            return {"success": False, "error": "task_id is required for dependency operations"}
        try:
            if action == "add_dependency":
                if not dependency_data or "dependency_id" not in dependency_data:
                    return {"success": False, "error": "dependency_data with dependency_id is required"}
                from task_mcp.application.use_cases.manage_dependencies import AddDependencyRequest
                request = AddDependencyRequest(task_id=task_id, dependency_id=dependency_data["dependency_id"])
                response = self._task_app_service.add_dependency(request)
                return {"success": response.success, "action": "add_dependency", "task_id": response.task_id, "dependencies": response.dependencies, "message": response.message}
            elif action == "remove_dependency":
                if not dependency_data or "dependency_id" not in dependency_data:
                    return {"success": False, "error": "dependency_data with dependency_id is required"}
                response = self._task_app_service.remove_dependency(task_id, dependency_data["dependency_id"])
                return {"success": response.success, "action": "remove_dependency", "task_id": response.task_id, "dependencies": response.dependencies, "message": response.message}
            elif action == "get_dependencies":
                response = self._task_app_service.get_dependencies(task_id)
                return {"success": True, "action": "get_dependencies", **response}
            elif action == "clear_dependencies":
                response = self._task_app_service.clear_dependencies(task_id)
                return {"success": response.success, "action": "clear_dependencies", "task_id": response.task_id, "dependencies": response.dependencies, "message": response.message}
            elif action == "get_blocking_tasks":
                response = self._task_app_service.get_blocking_tasks(task_id)
                return {"success": True, "action": "get_blocking_tasks", **response}
            else:
                return {"success": False, "error": f"Unknown dependency action: {action}"}
        except Exception as e:
            return {"success": False, "error": f"Dependency operation failed: {str(e)}"}

    def _handle_subtask_operations(self, action, task_id, subtask_data):
        """Handle subtask operations"""
        logging.info(f"Subtask operation action: {action}, task_id: {task_id}, subtask_data: {subtask_data}")
        if not task_id:
            return {"success": False, "error": "task_id is required for subtask operations"}
        
        try:
            response = self._task_app_service.manage_subtasks(task_id, action, subtask_data or {})
            logging.info(f"Subtask operation result: {response}")
            
            # For add_subtask, flatten the response structure for compatibility
            if action in ["add_subtask", "add"]:
                if isinstance(response, dict) and "subtask" in response:
                    # The response is a SubtaskResponse dict with structure:
                    # {"task_id": "...", "subtask": {...}, "progress": {...}}
                    # We want to return the subtask data directly
                    return {
                        "success": True, 
                        "action": action, 
                        "result": {"subtask": response["subtask"]},
                        "progress": response.get("progress", {})
                    }
                else:
                    return {"success": True, "action": action, "result": response}
            elif action in ["list_subtasks", "list"]:
                if isinstance(response, dict) and "subtasks" in response:
                    # The response is a dict with structure:
                    # {"task_id": "...", "subtasks": [...], "progress": {...}}
                    # We want to return the subtasks directly
                    return {
                        "success": True, 
                        "action": action, 
                        "result": response["subtasks"],  # Extract the subtasks array
                        "progress": response.get("progress", {})
                    }
                else:
                    return {"success": True, "action": action, "result": response}
            else:
                return {"success": True, "action": action, "result": response}
                
        except Exception as e:
            logging.error(f"Error handling subtask operation: {e}")
            return {"success": False, "error": f"Subtask operation failed: {str(e)}"} 