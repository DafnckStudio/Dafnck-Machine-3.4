"""Consolidated MCP Tools v2 - Clean and Maintainable Architecture"""

import os
import json
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import asdict

from fastmcp import FastMCP
from fastmcp.tools.tool_path import find_project_root

# Configure logging
logger = logging.getLogger(__name__)

# Application layer imports (use cases and service)
from fastmcp.task_management.application import (
    TaskApplicationService,
    DoNextUseCase,
    CallAgentUseCase
)

# DTO imports - use module-level imports to avoid conflicts
from fastmcp.task_management.application.dtos import (
    CreateTaskRequest,
    UpdateTaskRequest,
    ListTasksRequest,
    SearchTasksRequest,
    TaskResponse,
    CreateTaskResponse,
    TaskListResponse,
    AddSubtaskRequest,
    UpdateSubtaskRequest,
    SubtaskResponse,
    AddDependencyRequest,
    DependencyResponse
)

# Infrastructure layer imports
from fastmcp.task_management.infrastructure import JsonTaskRepository, FileAutoRuleGenerator, InMemoryTaskRepository
from fastmcp.task_management.infrastructure.services.agent_converter import AgentConverter

# Interface layer imports
from fastmcp.task_management.interface.cursor_rules_tools import CursorRulesTools

# Domain layer imports
from fastmcp.task_management.domain.enums import CommonLabel, EstimatedEffort, AgentRole, LabelValidator
from fastmcp.task_management.domain.enums.agent_roles import resolve_legacy_role
from fastmcp.task_management.domain.exceptions import TaskNotFoundError, AutoRuleGenerationError
from fastmcp.task_management.domain.repositories.task_repository import TaskRepository
from fastmcp.task_management.domain.services.auto_rule_generator import AutoRuleGenerator
from fastmcp.task_management.domain.entities.project import Project as ProjectEntity
from fastmcp.task_management.domain.entities.task_tree import TaskTree as TaskTreeEntity
from fastmcp.task_management.domain.entities.task import Task
from fastmcp.task_management.domain.services.orchestrator import Orchestrator

# Constants and Configuration
PROJECT_ROOT = find_project_root()


class PathResolver:
    """Handles path resolution and directory management"""
    
    def __init__(self):
        self.project_root = PROJECT_ROOT
        self.brain_dir = self._resolve_path(os.environ.get("BRAIN_DIR_PATH", ".cursor/rules/brain"))
        self.projects_file = self._resolve_path(os.environ.get("PROJECTS_FILE_PATH", self.brain_dir / "projects.json"))
        
    def _resolve_path(self, path):
        p = Path(path)
        return p if p.is_absolute() else (self.project_root / p)
        
    def ensure_brain_dir(self):
        os.makedirs(self.brain_dir, exist_ok=True)

class ProjectManager:
    """Manages project lifecycle and multi-agent coordination"""
    
    def __init__(self, path_resolver: PathResolver, projects_file_path: Optional[str] = None):
        self.path_resolver = path_resolver
        
        if projects_file_path:
            self._projects_file = projects_file_path
            self._brain_dir = os.path.dirname(projects_file_path)
        else:
            self._brain_dir = path_resolver.brain_dir
            self._projects_file = path_resolver.projects_file
        
        self._projects = {}
        self._load_projects()
        
        # Initialize advanced features
        self._agent_converter = AgentConverter()
        self._orchestrator = Orchestrator()
    
    def _ensure_brain_dir(self):
        """Ensure the brain directory exists"""
        self.path_resolver.ensure_brain_dir()
    
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


class ToolConfig:
    """Manages tool configuration and enablement"""
    
    def __init__(self):
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        config_path = os.environ.get('MCP_TOOL_CONFIG')
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return {
            "enabled_tools": {
                "manage_project": True, "manage_task": True, "manage_subtask": True,
                "manage_agent": True, "call_agent": True, "update_auto_rule": True,
                "validate_rules": True, "manage_cursor_rules": True,
                "regenerate_auto_rule": True, "validate_tasks_json": True
            },
            "debug_mode": False, "tool_logging": False
        }
        
    def is_enabled(self, tool_name: str) -> bool:
        return self.config.get("enabled_tools", {}).get(tool_name, True)


class ConsolidatedMCPToolsV2:
    """Main MCP tools interface with clean architecture"""
    
    def __init__(self, task_repository: Optional[TaskRepository] = None, projects_file_path: Optional[str] = None):
        logger.info("Initializing ConsolidatedMCPToolsV2...")
        
        # Initialize configuration
        self._config = ToolConfig()
        
        # Initialize repositories
        self._task_repository = self._init_task_repository(task_repository)
        self._auto_rule_generator = FileAutoRuleGenerator()
        
        # Initialize services
        self._task_app_service = TaskApplicationService(
            task_repository=self._task_repository,
            auto_rule_generator=self._auto_rule_generator
        )
        
        # Initialize components
        self._path_resolver = PathResolver()
        self._project_manager = ProjectManager(self._path_resolver, projects_file_path)
        self._call_agent_use_case = CallAgentUseCase(PROJECT_ROOT / 'yaml-lib')
        logger.info("ConsolidatedMCPToolsV2 initialized successfully.")
        
    def _init_task_repository(self, task_repository: Optional[TaskRepository]) -> TaskRepository:
        if task_repository:
            return task_repository
            
        tasks_file_path = os.environ.get('TASKS_JSON_PATH')
        if tasks_file_path:
            logger.info(f"Found TASKS_JSON_PATH: {tasks_file_path}")
            return JsonTaskRepository(file_path=tasks_file_path)
        else:
            logger.warning("TASKS_JSON_PATH not set, using default.")
            return JsonTaskRepository()
    
    
    def register_tools(self, mcp: FastMCP):
        """Register all consolidated MCP tools in three logical categories"""
        logger.info("Registering tools in ConsolidatedMCPToolsV2...")
        
        # Log enabled tools
        enabled_tools = self._config.config.get("enabled_tools", {})
        enabled_count = sum(1 for enabled in enabled_tools.values() if enabled)
        total_count = len(enabled_tools)
        logger.info(f"Tool configuration: {enabled_count}/{total_count} tools enabled")
        
        for tool_name, enabled in enabled_tools.items():
            status = "ENABLED" if enabled else "DISABLED"
            logger.info(f"  - {tool_name}: {status}")
        
        # ═══════════════════════════════════════════════════════════════════
        # 🏗️ PROJECT MANAGEMENT - High-level orchestration and coordination
        # ═══════════════════════════════════════════════════════════════════
        
        if self._config.is_enabled("manage_project"):
            @mcp.tool()
            def manage_project(
                action: str,
                project_id: str = None,
                name: str = None,
                description: str = None,
                tree_id: str = None,
                tree_name: str = None,
                tree_description: str = None
            ) -> Dict[str, Any]:
                """Multi-agent project lifecycle management.
                
                Actions: create, get, list, create_tree, get_tree_status, orchestrate, dashboard
                
                Examples:
                - action="create", project_id="my_project", name="Project Name"
                - action="get", project_id="my_project"
                - action="orchestrate", project_id="my_project"
                """
                
                if action == "create":
                    if not project_id or not name:
                        return {"success": False, "error": "project_id and name are required for creating a project"}
                    return self._project_manager.create_project(project_id, name, description or "")
                    
                elif action == "get":
                    if not project_id:
                        return {"success": False, "error": "project_id is required"}
                    return self._project_manager.get_project(project_id)
                    
                elif action == "list":
                    return self._project_manager.list_projects()
                    
                elif action == "create_tree":
                    if not all([project_id, tree_id, tree_name]):
                        return {"success": False, "error": "project_id, tree_id, and tree_name are required"}
                    return self._project_manager.create_task_tree(project_id, tree_id, tree_name, tree_description or "")
                    
                elif action == "get_tree_status":
                    if not project_id or not tree_id:
                        return {"success": False, "error": "project_id and tree_id are required"}
                    return self._project_manager.get_task_tree_status(project_id, tree_id)
                    
                elif action == "orchestrate":
                    if not project_id:
                        return {"success": False, "error": "project_id is required"}
                    return self._project_manager.orchestrate_project(project_id)
                    
                elif action == "dashboard":
                    if not project_id:
                        return {"success": False, "error": "project_id is required"}
                    return self._project_manager.get_orchestration_dashboard(project_id)
                    
                else:
                    return {"success": False, "error": f"Unknown action: {action}. Available: create, get, list, create_tree, get_tree_status, orchestrate, dashboard"}

            logger.info("Registered manage_project tool")
        else:
            logger.info("Skipped manage_project tool (disabled)")
        
        # ═══════════════════════════════════════════════════════════════════
        # 📋 TASK MANAGEMENT - Granular work item lifecycle and workflow  
        # ═══════════════════════════════════════════════════════════════════
        
        if self._config.is_enabled("manage_task"):
            @mcp.tool()
            def manage_task(
                action: str,
                task_id: str = None,
                project_id: str = None,
                title: str = None,
                description: str = None,
                status: str = None,
                priority: str = None,
                details: str = None,
                estimated_effort: str = None,
                assignees: List[str] = None,
                labels: List[str] = None,
                due_date: str = None,
                dependency_data: Dict[str, Any] = None,
                query: str = None,
                limit: int = None,
                force_full_generation: bool = False
            ) -> Dict[str, Any]:
                """Unified task management: create, update, delete, list, search tasks and dependencies.
                
                Actions: create, get, update, delete, complete, list, search, next, add_dependency, remove_dependency
                """
                logger.debug(f"Received task management action: {action}")

                core_actions = ["create", "get", "update", "delete", "complete"]
                list_search_actions = ["list", "search", "next"]
                dependency_actions = ["add_dependency", "remove_dependency"]

                if action in core_actions:
                    return self._handle_core_task_operations(
                        action=action, task_id=task_id, title=title, description=description,
                        status=status, priority=priority, details=details,
                        estimated_effort=estimated_effort, assignees=assignees,
                        labels=labels, due_date=due_date, project_id=project_id,
                        force_full_generation=force_full_generation
                    )
                
                elif action in list_search_actions:
                    return self._handle_list_search_next(
                        action=action, status=status, priority=priority, assignees=assignees,
                        labels=labels, limit=limit, query=query
                    )

                elif action in dependency_actions:
                    return self._handle_dependency_operations(
                        action=action, task_id=task_id, dependency_data=dependency_data
                    )
                
                else:
                    return {"success": False, "error": f"Invalid task action: {action}"}
        
            logger.info("Registered manage_task tool")
        else:
            logger.info("Skipped manage_task tool (disabled)")

        if self._config.is_enabled("manage_subtask"):
            @mcp.tool()
            def manage_subtask(
                action: str,
                task_id: str = None,
                subtask_data: Dict[str, Any] = None
            ) -> Dict[str, Any]:
                """Manages subtasks: creation, completion, updates, removal, and listing.
                
                Args:
                    action: Subtask action ('add', 'complete', 'list', etc.)
                    task_id: Parent task ID
                    subtask_data: Subtask operation data
                """
                if task_id is None:
                    return {"success": False, "error": "task_id is required"}

                try:
                    result = self._handle_subtask_operations(action, task_id, subtask_data)
                    return result
                except (ValueError, TypeError, TaskNotFoundError) as e:
                    logging.error(f"Error managing subtask: {e}")
                    return {"success": False, "error": str(e)}
                except Exception as e:
                    logging.error(f"Unexpected error in manage_subtask: {e}\\n{traceback.format_exc()}")
                    return {"success": False, "error": f"An unexpected error occurred: {e}"}

            logger.info("Registered manage_subtask tool")
        else:
            logger.info("Skipped manage_subtask tool (disabled)")
        
        # ═══════════════════════════════════════════════════════════════════
        # 🤖 AGENT MANAGEMENT - Multi-agent coordination and assignment
        # ═══════════════════════════════════════════════════════════════════
        
        if self._config.is_enabled("manage_agent"):
            @mcp.tool()
            def manage_agent(
                action: str,
                project_id: str = None,
                agent_id: str = None,
                name: str = None,
                call_agent: str = None,
                tree_id: str = None
            ) -> Dict[str, Any]:
                """Multi-agent team management and intelligent assignment.
                
                Actions: register, assign, get, list, get_assignments, unassign, update, unregister, rebalance
                
                Examples:
                - action="register", project_id="my_project", agent_id="frontend_expert", name="Frontend Specialist"
                - action="assign", project_id="my_project", agent_id="frontend_expert", tree_id="ui_components"
                - action="list", project_id="my_project"
                """
                
                if action == "register":
                    if not all([project_id, agent_id, name]):
                        return {"success": False, "error": "project_id, agent_id, and name are required for registering an agent"}
                    return self._project_manager.register_agent(
                        project_id=project_id,
                        agent_id=agent_id, 
                        name=name,
                        call_agent=call_agent
                    )
                    
                elif action == "assign":
                    if not all([project_id, agent_id, tree_id]):
                        return {"success": False, "error": "project_id, agent_id, and tree_id are required for assignment"}
                    return self._project_manager.assign_agent_to_tree(project_id, agent_id, tree_id)
                    
                elif action == "get":
                    if not project_id or not agent_id:
                        return {"success": False, "error": "project_id and agent_id are required"}
                    # Get agent details from project
                    project_response = self._project_manager.get_project(project_id)
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
                    project_response = self._project_manager.get_project(project_id)
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
                    project_response = self._project_manager.get_project(project_id)
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
                    project_response = self._project_manager.get_project(project_id)
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
                    self._project_manager._save_projects()
                    return {"success": True, "agent": agent_data}
                    
                elif action == "unregister":
                    if not project_id or not agent_id:
                        return {"success": False, "error": "project_id and agent_id are required"}
                    
                    # Get current project
                    project_response = self._project_manager.get_project(project_id)
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
                    self._project_manager._save_projects()
                    return {"success": True, "message": f"Agent {agent_id} unregistered", "removed_agent": removed_agent}
                    
                elif action == "rebalance":
                    if not project_id:
                        return {"success": False, "error": "project_id is required"}
                    return {"success": True, "message": "Workload rebalancing analysis completed", "recommendations": []}
                    
                else:
                    return {"success": False, "error": f"Unknown action: {action}. Available: register, assign, get, list, get_assignments, unassign, update, unregister, rebalance"}

            logger.info("Registered manage_agent tool")
        else:
            logger.info("Skipped manage_agent tool (disabled)")

        # Register Cursor Rules Tools for additional functionality (conditional)
        cursor_tools = ["update_auto_rule", "validate_rules", "manage_cursor_rules", "regenerate_auto_rule", "validate_tasks_json"]
        enabled_cursor_tools = [tool for tool in cursor_tools if self._config.is_enabled(tool)]
        
        if enabled_cursor_tools:
            logger.info(f"Registering {len(enabled_cursor_tools)} cursor rules tools")
            # Create a filtered config for cursor tools and register conditionally
            self._register_cursor_tools_conditionally(mcp, enabled_cursor_tools)
        else:
            logger.info("Skipped all cursor rules tools (all disabled)")

        # Register Agent Information Tool
        if self._config.is_enabled("call_agent"):
            @mcp.tool()
            def call_agent(
                name_agent: str
            ) -> Dict[str, Any]:
                """Retrieves agent configuration and documentation from YAML files.
                
                Args:
                    name_agent (str): Agent directory name with _agent suffix (e.g., "devops_agent")
                
                Returns:
                    Dict with agent information and combined YAML content
                
                Examples: "devops_agent", "coding_agent", "system_architect_agent"
                """
                try:
                    result = self._call_agent_use_case.execute(name_agent)
                    # If the result contains suggestions, format them for better display
                    if not result.get("success") and "available_agents" in result:
                        result["formatted_message"] = f"{result['error']}\n\n{result['suggestion']}"
                    return result
                except Exception as e:
                    logging.error(f"Error getting agent metadata from YAML for {name_agent}: {e}")
                    return {"success": False, "error": f"Failed to get agent metadata: {e}"}
        
            logger.info("Registered call_agent tool")
        else:
            logger.info("Skipped call_agent tool (disabled)")

        logger.info("Finished registering all tools.")

    def _register_cursor_tools_conditionally(self, mcp, enabled_tools):
        """Register only enabled cursor rules tools"""
        from .cursor_rules_tools import CursorRulesTools
        
        # Create a temporary cursor tools instance just to access the individual tool methods
        temp_cursor_tools = CursorRulesTools()
        
        # For now, register all cursor tools since they're in one method
        # TODO: Split CursorRulesTools.register_tools into individual methods
        if enabled_tools:
            temp_cursor_tools.register_tools(mcp)
            for tool in enabled_tools:
                logger.info(f"  - Registered {tool}")

    # ═══════════════════════════════════════════════════════════════════
    # 🔧 HELPER METHODS - Internal routing and operation handling
    # ═══════════════════════════════════════════════════════════════════
    
    def _handle_core_task_operations(self, action, task_id, title, description, status, priority, details, estimated_effort, assignees, labels, due_date, project_id=None, force_full_generation=False):
        """Helper to manage core CRUD operations for tasks"""
        logger.debug(f"Handling task action '{action}' with task_id '{task_id}'")

        if labels:
            try:
                labels = LabelValidator.validate_labels(labels)
            except ValueError as e:
                return {"success": False, "error": f"Invalid label(s) provided: {e}"}

        try:
            if action == "create":
                return self._core_create_task(title, description, project_id, status, priority, details, estimated_effort, assignees, labels, due_date)
            elif action == "update":
                return self._core_update_task(task_id, title, description, status, priority, details, estimated_effort, assignees, labels, due_date)
            elif action == "get":
                task_response = self._task_app_service.get_task(task_id, generate_rules=True, force_full_generation=force_full_generation)
                if task_response:
                    return {"success": True, "action": "get", "task": asdict(task_response)}
                else:
                    return {"success": False, "action": "get", "error": f"Task with ID {task_id} not found."}
            elif action == "delete":
                success = self._task_app_service.delete_task(task_id)
                if success:
                    return {"success": True, "action": "delete"}
                else:
                    return {"success": False, "action": "delete", "error": f"Task with ID {task_id} not found."}
            elif action == "complete":
                return self._handle_complete_task(task_id)
            else:
                return {"success": False, "error": f"Invalid core action: {action}"}
        except TaskNotFoundError as e:
            return {"success": False, "error": str(e)}
        except ValueError as e:
            # Catches validation errors for labels, etc.
            return {"success": False, "error": str(e)}
        except AutoRuleGenerationError as e:
            logger.warning(f"Auto rule generation failed: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"An unexpected error occurred in _handle_core_task_operations: {e}\n{traceback.format_exc()}")
            return {"success": False, "error": f"An unexpected error occurred: {str(e)}"}

    def _core_create_task(self, title, description, project_id, status, priority, details, estimated_effort, assignees, labels, due_date):
        if not title:
            return {"success": False, "error": "Title is required for creating a task."}
        
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

        # Defensive: Always access nested attributes, never direct task_id
        is_success = getattr(response, 'success', False)
        task_data = getattr(response, 'task', None)
        error_message = getattr(response, 'message', 'Unknown error')

        if is_success and task_data is not None:
            # Defensive: If task_data is a dataclass, convert to dict
            return {
                "success": True,
                "action": "create",
                "task": asdict(task_data) if not isinstance(task_data, dict) else task_data
            }
        else:
            return {
                "success": False,
                "action": "create",
                "error": error_message
            }

    def _core_update_task(self, task_id, title, description, status, priority, details, estimated_effort, assignees, labels, due_date):
        """Core logic to update a task."""
        if task_id is None:
            return {"success": False, "error": "Task ID is required for update action"}
        
        try:
            if labels:
                labels = LabelValidator.validate_labels(labels)
        except ValueError as e:
            return {"success": False, "error": f"Invalid label(s) provided: {e}"}

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
        response = self._task_app_service.update_task(request)

        is_success = False
        task_data = None
        error_message = f"Task with ID {task_id} not found."

        if response:
            is_success = getattr(response, 'success', False)
            task_data = getattr(response, 'task', None)
            error_message = getattr(response, 'message', error_message)

        if is_success and task_data is not None:
            return {
                "success": True,
                "action": "update",
                "task_id": task_id,
                "task": asdict(task_data) if not isinstance(task_data, dict) else task_data
            }
        
        return {"success": False, "action": "update", "error": error_message}

    def _handle_complete_task(self, task_id):
        """Handle completing a task"""
        if not task_id:
            return {"success": False, "error": "task_id is required for completing a task"}
        try:
            response = self._task_app_service.complete_task(task_id)
            if response.get("success"):
                response["action"] = "complete"
            return response
        except TaskNotFoundError:
            return {"success": False, "error": f"Task with ID {task_id} not found."}
        except Exception as e:
            logger.error(f"Error completing task {task_id}: {e}")
            return {"success": False, "error": str(e)}

    def _handle_list_search_next(self, action, status, priority, assignees, labels, limit, query):
        """Handle list, search, and next actions."""
        if action == "list":
            return self._handle_list_tasks(status, priority, assignees, labels, limit)
        elif action == "search":
            return self._handle_search_tasks(query, limit)
        elif action == "next":
            return self._handle_do_next()
        else:
            # This case should not be reached due to the dispatching in manage_task
            return {"success": False, "error": "Invalid action for list/search/next"}

    def _handle_list_tasks(self, status, priority, assignees, labels, limit):
        """Handles listing tasks with optional filters."""
        try:
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
        except Exception as e:
            return {"success": False, "error": f"Failed to list tasks: {str(e)}"}

    def _handle_search_tasks(self, query, limit):
        """Handle task search"""
        if not query:
            return {"success": False, "error": "query is required for searching tasks"}
        
        try:
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
        except Exception as e:
            return {"success": False, "error": f"Failed to search tasks: {str(e)}"}

    def _handle_do_next(self):
        """Handle next task recommendation"""
        try:
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
        except Exception as e:
            return {"success": False, "error": f"Failed to get next task: {str(e)}"}

    def _handle_dependency_operations(self, action, task_id, dependency_data=None):
        """Handle dependency operations (add, remove, get, clear, get_blocking)"""
        if not task_id:
            return {"success": False, "error": "task_id is required for dependency operations"}
        try:
            if action == "add_dependency":
                if not dependency_data or "dependency_id" not in dependency_data:
                    return {"success": False, "error": "dependency_data with dependency_id is required"}
                
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

    def _handle_subtask_operations(self, action, task_id, subtask_data=None):
        """Handle subtask operations"""
        logging.info(f"Subtask operation action: {action}, task_id: {task_id}, subtask_data: {subtask_data}")
        if not task_id:
            return {"success": False, "error": "task_id is required for subtask operations"}
        
        try:
            response = self._task_app_service.manage_subtasks(task_id, action, subtask_data or {})
            logging.info(f"Subtask operation result: {response}")
            
            # Always wrap response data in a "result" key for consistency
            if action in ["add_subtask", "add"]:
                if isinstance(response, dict) and "subtask" in response:
                    # The response is a SubtaskResponse dict with structure:
                    # {"task_id": "...", "subtask": {...}, "progress": {...}}
                    # Wrap the subtask data in a "result" key for consistency
                    return {
                        "success": True, 
                        "action": action, 
                        "result": {
                            "subtask": response["subtask"],
                            "progress": response.get("progress", {})
                        }
                    }
                else:
                    return {"success": True, "action": action, "result": response}
            elif action in ["list_subtasks", "list"]:
                if isinstance(response, dict) and "subtasks" in response:
                    # The response is a dict with structure:
                    # {"task_id": "...", "subtasks": [...], "progress": {...}}
                    # Wrap the subtasks array in a "result" key for consistency
                    return {
                        "success": True, 
                        "action": action, 
                        "result": response["subtasks"],  # Return subtasks array as result
                        "progress": response.get("progress", {})
                    }
                else:
                    return {"success": True, "action": action, "result": response}
            else:
                return {"success": True, "action": action, "result": response}
                
        except Exception as e:
            logging.error(f"Error handling subtask operation: {e}")
            return {"success": False, "error": f"Subtask operation failed: {str(e)}"} 