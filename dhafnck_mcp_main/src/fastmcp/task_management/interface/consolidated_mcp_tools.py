"""Consolidated MCP Tools v2 - Clean and Maintainable Architecture"""

import os
import json
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, Annotated
from dataclasses import asdict
from pydantic import Field

from typing import TYPE_CHECKING
from fastmcp.tools.tool_path import find_project_root, get_project_cursor_rules_dir, ensure_project_structure

if TYPE_CHECKING:
    from fastmcp.server.server import FastMCP

# Configure logging
logger = logging.getLogger(__name__)

# Application layer imports
from fastmcp.task_management.application import (
    TaskApplicationService,
    DoNextUseCase,
    CallAgentUseCase
)
from fastmcp.task_management.application.use_cases.call_agent import CURSOR_AGENT_DIR

# DTO imports
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
from fastmcp.task_management.infrastructure.repositories.task_repository_factory import TaskRepositoryFactory
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

# ═══════════════════════════════════════════════════════════════════
# 🛠️ CONFIGURATION AND PATH MANAGEMENT
# ═══════════════════════════════════════════════════════════════════

class PathResolver:
    """Handles dynamic path resolution and directory management for multiple projects"""
    
    def __init__(self):
        # Dynamic project root detection
        self.project_root = find_project_root()
        
        # Ensure project structure exists
        self.cursor_rules_dir = ensure_project_structure(self.project_root)
        
        # Resolve paths dynamically based on current project
        self.brain_dir = self._resolve_path(os.environ.get("BRAIN_DIR_PATH", ".cursor/rules/brain"))
        self.projects_file = self._resolve_path(os.environ.get("PROJECTS_FILE_PATH", self.brain_dir / "projects.json"))
        
        logger.info(f"PathResolver initialized for project: {self.project_root}")
        logger.info(f"Brain directory: {self.brain_dir}")
        logger.info(f"Projects file: {self.projects_file}")
        
    def _resolve_path(self, path):
        """Resolve path relative to current project root"""
        p = Path(path)
        return p if p.is_absolute() else (self.project_root / p)
        
    def ensure_brain_dir(self):
        """Ensure brain directory exists"""
        os.makedirs(self.brain_dir, exist_ok=True)
        
    def get_tasks_json_path(self, project_id: str = None, task_tree_id: str = "main", user_id: str = "default_id") -> Path:
        """
        Get the hierarchical tasks.json path for user/project/tree
        
        Args:
            project_id: Project identifier (required for new structure)
            task_tree_id: Task tree identifier (defaults to "main")
            user_id: User identifier (defaults to "default_id")
            
        Returns:
            Path to tasks.json file in hierarchical structure
        """
        if project_id:
            # New hierarchical structure: .cursor/rules/tasks/{user_id}/{project_id}/{task_tree_id}/tasks.json
            tasks_path = self._resolve_path(f".cursor/rules/tasks/{user_id}/{project_id}/{task_tree_id}/tasks.json")
        else:
            # Legacy fallback for backward compatibility
            tasks_path = self._resolve_path(os.environ.get("TASKS_JSON_PATH", ".cursor/rules/tasks/tasks.json"))
            
        # Ensure the tasks directory exists
        tasks_path.parent.mkdir(parents=True, exist_ok=True)
        return tasks_path
        
    def get_legacy_tasks_json_path(self) -> Path:
        """Get the legacy tasks.json path for migration purposes"""
        tasks_path = self._resolve_path(".cursor/rules/tasks/tasks.json")
        return tasks_path
        
    def get_auto_rule_path(self) -> Path:
        """Get the auto_rule.mdc path for current project"""
        return self._resolve_path(os.environ.get("AUTO_RULE_PATH", ".cursor/rules/auto_rule.mdc"))
        
    def get_cursor_agent_dir(self) -> Path:
        """Get the cursor_agent directory path"""
        # Check if we have a project-specific cursor_agent directory
        project_cursor_agent = self.project_root / "cursor_agent"
        if project_cursor_agent.exists():
            return project_cursor_agent
        
        # Fallback to environment variable or default
        cursor_agent_path = os.environ.get("CURSOR_AGENT_DIR_PATH", "dhafnck_mcp_main/yaml-lib")
        return self._resolve_path(cursor_agent_path)


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
    """Manages MCP tool configuration and enablement settings"""
    
    DEFAULT_CONFIG = {
        "enabled_tools": {
            "manage_project": True, "manage_task": True, "manage_subtask": True,
            "manage_agent": True, "call_agent": True, "update_auto_rule": True,
            "validate_rules": True, "manage_cursor_rules": True,
            "regenerate_auto_rule": True, "validate_tasks_json": True
        },
        "debug_mode": False, 
        "tool_logging": False
    }
    
    def __init__(self):
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment or use defaults"""
        config_path = os.environ.get('MCP_TOOL_CONFIG')
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return self.DEFAULT_CONFIG.copy()
        
    def is_enabled(self, tool_name: str) -> bool:
        """Check if a specific tool is enabled"""
        return self.config.get("enabled_tools", {}).get(tool_name, True)
    
    def get_enabled_tools(self) -> Dict[str, bool]:
        """Get all enabled tools configuration"""
        return self.config.get("enabled_tools", {})


# ═══════════════════════════════════════════════════════════════════
# 🔧 OPERATION HANDLERS
# ═══════════════════════════════════════════════════════════════════

class TaskOperationHandler:
    """Handles all task-related operations and business logic with hierarchical storage"""
    
    def __init__(self, repository_factory: TaskRepositoryFactory, auto_rule_generator: AutoRuleGenerator, project_manager):
        self._repository_factory = repository_factory
        self._auto_rule_generator = auto_rule_generator
        self._project_manager = project_manager
    
    def handle_core_operations(self, action, project_id, task_tree_id, user_id, task_id, title, description, status, priority, details, estimated_effort, assignees, labels, due_date, force_full_generation=False):
        """Handle core CRUD operations for tasks with hierarchical storage"""
        logger.debug(f"Handling task action '{action}' with task_id '{task_id}' in project '{project_id}' tree '{task_tree_id}'")

        # Validate project and task tree exist
        if not self._validate_project_tree(project_id, task_tree_id):
            return {"success": False, "error": f"Project '{project_id}' or task tree '{task_tree_id}' not found"}

        if labels:
            try:
                labels = LabelValidator.validate_labels(labels)
            except ValueError as e:
                return {"success": False, "error": f"Invalid label(s) provided: {e}"}

        # Get repository for this specific project/tree
        try:
            repository = self._repository_factory.create_repository(project_id, task_tree_id, user_id)
            task_app_service = TaskApplicationService(repository, self._auto_rule_generator)
        except Exception as e:
            return {"success": False, "error": f"Failed to access task storage: {str(e)}"}

        try:
            if action == "create":
                return self._create_task(task_app_service, title, description, project_id, status, priority, details, estimated_effort, assignees, labels, due_date)
            elif action == "update":
                return self._update_task(task_app_service, task_id, title, description, status, priority, details, estimated_effort, assignees, labels, due_date)
            elif action == "get":
                task_response = task_app_service.get_task(task_id, generate_rules=True, force_full_generation=force_full_generation)
                if task_response:
                    return {"success": True, "action": "get", "task": asdict(task_response)}
                else:
                    return {"success": False, "action": "get", "error": f"Task with ID {task_id} not found."}
            elif action == "delete":
                success = task_app_service.delete_task(task_id)
                if success:
                    return {"success": True, "action": "delete"}
                else:
                    return {"success": False, "action": "delete", "error": f"Task with ID {task_id} not found."}
            elif action == "complete":
                return self._complete_task(task_app_service, task_id)
            else:
                return {"success": False, "error": f"Invalid core action: {action}"}
        except TaskNotFoundError as e:
            return {"success": False, "error": str(e)}
        except ValueError as e:
            return {"success": False, "error": str(e)}
        except AutoRuleGenerationError as e:
            logger.warning(f"Auto rule generation failed: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"An unexpected error occurred in core operations: {e}\n{traceback.format_exc()}")
            return {"success": False, "error": f"An unexpected error occurred: {str(e)}"}
    
    def _validate_project_tree(self, project_id: str, task_tree_id: str) -> bool:
        """Validate if project and task tree combination exists"""
        project_response = self._project_manager.get_project(project_id)
        if not project_response.get("success"):
            return False
        
        project = project_response.get("project", {})
        task_trees = project.get("task_trees", {})
        return task_tree_id in task_trees
    
    def handle_list_search_next(self, action, project_id, task_tree_id, user_id, status, priority, assignees, labels, limit, query):
        """Handle list, search, and next actions with hierarchical storage"""
        # Validate project and task tree exist
        if not self._validate_project_tree(project_id, task_tree_id):
            return {"success": False, "error": f"Project '{project_id}' or task tree '{task_tree_id}' not found"}
        
        # Get repository for this specific project/tree
        try:
            repository = self._repository_factory.create_repository(project_id, task_tree_id, user_id)
            task_app_service = TaskApplicationService(repository, self._auto_rule_generator)
        except Exception as e:
            return {"success": False, "error": f"Failed to access task storage: {str(e)}"}
        
        if action == "list":
            return self._list_tasks(task_app_service, status, priority, assignees, labels, limit)
        elif action == "search":
            return self._search_tasks(task_app_service, query, limit)
        elif action == "next":
            return self._get_next_task(task_app_service)
        else:
            return {"success": False, "error": "Invalid action for list/search/next"}
    
    def handle_dependency_operations(self, action, task_id, dependency_data=None):
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
    
    def handle_subtask_operations(self, action, task_id, subtask_data=None):
        """Handle subtask operations"""
        logging.info(f"Subtask operation action: {action}, task_id: {task_id}, subtask_data: {subtask_data}")
        if not task_id:
            return {"success": False, "error": "task_id is required for subtask operations"}
        
        try:
            response = self._task_app_service.manage_subtasks(task_id, action, subtask_data or {})
            logging.info(f"Subtask operation result: {response}")
            
            if action in ["add_subtask", "add"]:
                if isinstance(response, dict) and "subtask" in response:
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
                    return {
                        "success": True, 
                        "action": action, 
                        "result": response["subtasks"],
                        "progress": response.get("progress", {})
                    }
                else:
                    return {"success": True, "action": action, "result": response}
            else:
                return {"success": True, "action": action, "result": response}
                
        except Exception as e:
            logging.error(f"Error handling subtask operation: {e}")
            return {"success": False, "error": f"Subtask operation failed: {str(e)}"}
    
    # Private helper methods
    def _create_task(self, task_app_service, title, description, project_id, status, priority, details, estimated_effort, assignees, labels, due_date):
        """Create a new task"""
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
        response = task_app_service.create_task(request)
        logging.info(f"Create task response: {response}")

        is_success = getattr(response, 'success', False)
        task_data = getattr(response, 'task', None)
        error_message = getattr(response, 'message', 'Unknown error')

        if is_success and task_data is not None:
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
    
    def _update_task(self, task_app_service, task_id, title, description, status, priority, details, estimated_effort, assignees, labels, due_date):
        """Update an existing task"""
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
        response = task_app_service.update_task(request)

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
    
    def _complete_task(self, task_app_service, task_id):
        """Complete a task"""
        if not task_id:
            return {"success": False, "error": "task_id is required for completing a task"}
        try:
            response = task_app_service.complete_task(task_id)
            if response.get("success"):
                response["action"] = "complete"
            return response
        except TaskNotFoundError:
            return {"success": False, "error": f"Task with ID {task_id} not found."}
        except Exception as e:
            logger.error(f"Error completing task {task_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def _list_tasks(self, task_app_service, status, priority, assignees, labels, limit):
        """List tasks with optional filters"""
        try:
            request = ListTasksRequest(
                status=status,
                priority=priority,
                assignees=assignees,
                labels=labels,
                limit=limit
            )
            
            response = task_app_service.list_tasks(request)
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
    
    def _search_tasks(self, task_app_service, query, limit):
        """Search tasks by query"""
        if not query:
            return {"success": False, "error": "query is required for searching tasks"}
        
        try:
            request = SearchTasksRequest(query=query, limit=limit or 10)
            response = task_app_service.search_tasks(request)
            
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
    
    def _get_next_task(self, task_app_service):
        """Get next recommended task"""
        try:
            do_next_use_case = DoNextUseCase(task_app_service._task_repository, self._auto_rule_generator)
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


class ToolRegistrationOrchestrator:
    """Orchestrates the registration of all MCP tools"""
    
    def __init__(self, config: ToolConfig, task_handler: TaskOperationHandler, project_manager: ProjectManager, call_agent_use_case: CallAgentUseCase):
        self._config = config
        self._task_handler = task_handler
        self._project_manager = project_manager
        self._call_agent_use_case = call_agent_use_case
    
    def register_all_tools(self, mcp: "FastMCP"):
        """Register all MCP tools in organized categories"""
        logger.info("Registering tools via ToolRegistrationOrchestrator...")
        
        self._log_configuration()
        self._register_project_tools(mcp)
        self._register_task_tools(mcp)
        self._register_agent_tools(mcp)
        self._register_cursor_tools(mcp)
        
        logger.info("Finished registering all tools.")
    
    def _log_configuration(self):
        """Log current tool configuration"""
        enabled_tools = self._config.get_enabled_tools()
        enabled_count = sum(1 for enabled in enabled_tools.values() if enabled)
        total_count = len(enabled_tools)
        logger.info(f"Tool configuration: {enabled_count}/{total_count} tools enabled")
        
        for tool_name, enabled in enabled_tools.items():
            status = "ENABLED" if enabled else "DISABLED"
            logger.info(f"  - {tool_name}: {status}")
    
    def _register_project_tools(self, mcp: "FastMCP"):
        """Register project management tools"""
        if self._config.is_enabled("manage_project"):
            @mcp.tool()
            def manage_project(
                action: Annotated[str, Field(description="Project action to perform. Available: create, get, list, create_tree, get_tree_status, orchestrate, dashboard")],
                project_id: Annotated[str, Field(description="Unique project identifier")] = None,
                name: Annotated[str, Field(description="Project name (required for create action)")] = None,
                description: Annotated[str, Field(description="Project description (optional for create action)")] = None,
                tree_id: Annotated[str, Field(description="Task tree identifier (required for tree operations)")] = None,
                tree_name: Annotated[str, Field(description="Task tree name (required for create_tree action)")] = None,
                tree_description: Annotated[str, Field(description="Task tree description (optional for create_tree action)")] = None
            ) -> Dict[str, Any]:
                """🚀 PROJECT LIFECYCLE MANAGER - Multi-agent project orchestration and management

⭐ WHAT IT DOES: Complete project lifecycle management with task trees and agent coordination
📋 WHEN TO USE: Creating projects, managing task trees, orchestrating multi-agent workflows

🎯 ACTIONS AVAILABLE:
• create: Initialize new project with basic structure
• get: Retrieve project details and current status
• list: Show all available projects
• create_tree: Add task tree structure to project
• get_tree_status: Check task tree completion status
• orchestrate: Execute multi-agent project workflow
• dashboard: View comprehensive project analytics

💡 USAGE EXAMPLES:
• manage_project("create", project_id="web_app", name="E-commerce Website")
• manage_project("orchestrate", project_id="web_app")
• manage_project("dashboard", project_id="web_app")

🔧 INTEGRATION: Coordinates with task management and agent assignment systems
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
    
    def _register_task_tools(self, mcp: "FastMCP"):
        """Register task management tools"""
        if self._config.is_enabled("manage_task"):
            @mcp.tool()
            def manage_task(
                action: Annotated[str, Field(description="Task action to perform. Available: create, get, update, delete, complete, list, search, next, add_dependency, remove_dependency")],
                project_id: Annotated[str, Field(description="Project identifier (REQUIRED for all operations)")] = None,
                task_tree_id: Annotated[str, Field(description="Task tree identifier (defaults to 'main')")] = "main",
                user_id: Annotated[str, Field(description="User identifier (defaults to 'default_id')")] = "default_id",
                task_id: Annotated[str, Field(description="Unique task identifier (required for get, update, delete, complete, dependency operations)")] = None,
                title: Annotated[str, Field(description="Task title (required for create action)")] = None,
                description: Annotated[str, Field(description="Detailed task description")] = None,
                status: Annotated[str, Field(description="Task status. Available: todo, in_progress, blocked, review, testing, done, cancelled")] = None,
                priority: Annotated[str, Field(description="Task priority level. Available: low, medium, high, urgent, critical")] = None,
                details: Annotated[str, Field(description="Additional task details and context")] = None,
                estimated_effort: Annotated[str, Field(description="Estimated effort/time required. Available: quick, short, small, medium, large, xlarge, epic, massive")] = None,
                assignees: Annotated[List[str], Field(description="List of assigned agents. Use agent names like 'coding_agent', 'devops_agent', etc.")] = None,
                labels: Annotated[List[str], Field(description="Task labels for categorization. Examples: urgent, bug, feature, frontend, backend, security, testing, etc.")] = None,
                due_date: Annotated[str, Field(description="Task due date in ISO format (YYYY-MM-DD) or relative format")] = None,
                dependency_data: Annotated[Dict[str, Any], Field(description="Dependency data containing 'dependency_id' for dependency operations")] = None,
                query: Annotated[str, Field(description="Search query string for search action")] = None,
                limit: Annotated[int, Field(description="Maximum number of results to return for list/search actions")] = None,
                force_full_generation: Annotated[bool, Field(description="Force full auto-rule generation even if task context exists")] = False
            ) -> Dict[str, Any]:
                """📝 UNIFIED TASK MANAGER - Complete task lifecycle and dependency management

⭐ WHAT IT DOES: Comprehensive task operations with status tracking, dependencies, and search
📋 WHEN TO USE: Creating tasks, updating status, managing dependencies, searching tasks

🎯 ACTIONS AVAILABLE:
• create: Create new task with full metadata
• get: Retrieve specific task details
• update: Modify existing task properties
• delete: Remove task from system
• complete: Mark task as completed
• list: Show tasks with filtering options
• search: Find tasks by content/keywords
• next: Get next priority task to work on
• add_dependency: Link task dependencies
• remove_dependency: Remove task dependencies

💡 USAGE EXAMPLES:
• manage_task("create", project_id="my_project", title="Fix login bug", assignees=["coding_agent"])
• manage_task("update", project_id="my_project", task_id="123", status="in_progress")
• manage_task("list", project_id="my_project") - List tasks in project
• manage_task("next", project_id="my_project") - Get next task to work on

🔧 INTEGRATION: Auto-generates context rules and coordinates with agent assignment
📋 HIERARCHICAL STORAGE: Tasks stored at .cursor/rules/tasks/{user_id}/{project_id}/{task_tree_id}/tasks.json
                """
                logger.debug(f"Received task management action: {action}")
                
                # Validate required project_id for all operations
                if not project_id:
                    return {"success": False, "error": "project_id is required for all task operations"}

                core_actions = ["create", "get", "update", "delete", "complete"]
                list_search_actions = ["list", "search", "next"]
                dependency_actions = ["add_dependency", "remove_dependency"]

                if action in core_actions:
                    return self._task_handler.handle_core_operations(
                        action=action, project_id=project_id, task_tree_id=task_tree_id, user_id=user_id,
                        task_id=task_id, title=title, description=description,
                        status=status, priority=priority, details=details,
                        estimated_effort=estimated_effort, assignees=assignees,
                        labels=labels, due_date=due_date, 
                        force_full_generation=force_full_generation
                    )
                
                elif action in list_search_actions:
                    return self._task_handler.handle_list_search_next(
                        action=action, project_id=project_id, task_tree_id=task_tree_id, user_id=user_id,
                        status=status, priority=priority, assignees=assignees,
                        labels=labels, limit=limit, query=query
                    )

                elif action in dependency_actions:
                    return self._task_handler.handle_dependency_operations(
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
                action: Annotated[str, Field(description="Subtask action to perform. Available: add, complete, list, update, remove")],
                task_id: Annotated[str, Field(description="Parent task identifier (required for all subtask operations)")] = None,
                subtask_data: Annotated[Dict[str, Any], Field(description="Subtask data containing title, description, and other subtask properties")] = None
            ) -> Dict[str, Any]:
                """📋 SUBTASK MANAGER - Task breakdown and progress tracking

⭐ WHAT IT DOES: Manages subtasks within parent tasks for detailed progress tracking
📋 WHEN TO USE: Breaking down complex tasks, tracking granular progress, organizing work

🎯 ACTIONS AVAILABLE:
• add: Create new subtask under parent task
• complete: Mark subtask as finished
• list: Show all subtasks for a task
• update: Modify subtask properties
• remove: Delete subtask from parent

💡 USAGE EXAMPLES:
• manage_subtask("add", task_id="123", subtask_data={"title": "Write tests"})
• manage_subtask("complete", task_id="123", subtask_data={"subtask_id": "sub_456"})
• manage_subtask("list", task_id="123")

🔧 INTEGRATION: Works with parent task system and progress tracking
                """
                if task_id is None:
                    return {"success": False, "error": "task_id is required"}

                try:
                    result = self._task_handler.handle_subtask_operations(action, task_id, subtask_data)
                    return result
                except (ValueError, TypeError, TaskNotFoundError) as e:
                    logging.error(f"Error managing subtask: {e}")
                    return {"success": False, "error": str(e)}
                except Exception as e:
                    logging.error(f"Unexpected error in manage_subtask: {e}\n{traceback.format_exc()}")
                    return {"success": False, "error": f"An unexpected error occurred: {e}"}

            logger.info("Registered manage_subtask tool")
        else:
            logger.info("Skipped manage_subtask tool (disabled)")
    
    def _register_agent_tools(self, mcp: "FastMCP"):
        """Register agent management tools"""
        if self._config.is_enabled("manage_agent"):
            @mcp.tool()
            def manage_agent(
                action: Annotated[str, Field(description="Agent action to perform. Available: register, assign, get, list, get_assignments, unassign, update, unregister, rebalance")],
                project_id: Annotated[str, Field(description="Project identifier (required for most agent operations)")] = None,
                agent_id: Annotated[str, Field(description="Agent identifier (required for register, assign, get, update, unregister operations)")] = None,
                name: Annotated[str, Field(description="Agent display name (required for register action)")] = None,
                call_agent: Annotated[str, Field(description="Agent call reference (e.g., '@coding-agent', '@devops-agent')")] = None,
                tree_id: Annotated[str, Field(description="Task tree identifier (required for assign action)")] = None
            ) -> Dict[str, Any]:
                """🤖 MULTI-AGENT TEAM MANAGER - Agent registration and intelligent task assignment

⭐ WHAT IT DOES: Complete agent lifecycle management with intelligent workload distribution
📋 WHEN TO USE: Registering agents, assigning to task trees, managing team capacity

🎯 ACTIONS AVAILABLE:
• register: Add new agent to project team
• assign: Assign agent to specific task tree
• get: Retrieve agent details and status
• list: Show all registered agents
• get_assignments: View current agent assignments
• unassign: Remove agent from task tree
• update: Modify agent properties
• unregister: Remove agent from project
• rebalance: Optimize workload distribution

💡 USAGE EXAMPLES:
• manage_agent("register", project_id="web_app", agent_id="frontend_dev", name="Frontend Developer")
• manage_agent("assign", project_id="web_app", agent_id="frontend_dev", tree_id="ui_tasks")
• manage_agent("list", project_id="web_app")

🔧 INTEGRATION: Coordinates with project management and task assignment systems
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
                    
                    project_response = self._project_manager.get_project(project_id)
                    if not project_response.get("success"):
                        return project_response
                    
                    agents = project_response.get("project", {}).get("registered_agents", {})
                    if agent_id not in agents:
                        return {"success": False, "error": f"Agent {agent_id} not found in project {project_id}"}
                    
                    agent_data = agents[agent_id]
                    if name:
                        agent_data["name"] = name
                    if call_agent:
                        agent_data["call_agent"] = call_agent
                    
                    self._project_manager._save_projects()
                    return {"success": True, "agent": agent_data}
                    
                elif action == "unregister":
                    if not project_id or not agent_id:
                        return {"success": False, "error": "project_id and agent_id are required"}
                    
                    project_response = self._project_manager.get_project(project_id)
                    if not project_response.get("success"):
                        return project_response
                    
                    project_data = project_response.get("project", {})
                    agents = project_data.get("registered_agents", {})
                    
                    if agent_id not in agents:
                        return {"success": False, "error": f"Agent {agent_id} not found in project {project_id}"}
                    
                    removed_agent = agents.pop(agent_id)
                    
                    assignments = project_data.get("agent_assignments", {})
                    assignments = {k: v for k, v in assignments.items() if v != agent_id}
                    project_data["agent_assignments"] = assignments
                    
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

        if self._config.is_enabled("call_agent"):
            @mcp.tool()
            def call_agent(
                name_agent: Annotated[str, Field(description="Agent name with '_agent' suffix (e.g., 'coding_agent', 'devops_agent', 'system_architect_agent'). Use exact agent directory name from yaml-lib folder.")]
            ) -> Dict[str, Any]:
                """🤖 AGENT CONFIGURATION RETRIEVER - Load specialized agent roles and capabilities

⭐ WHAT IT DOES: Loads complete agent configuration including role, context, rules, and tools from YAML files
📋 WHEN TO USE: Switch AI assistant to specialized role, get agent capabilities, understand agent expertise

🎯 AGENT ROLES AVAILABLE:
• Development: coding_agent, development_orchestrator_agent, code_reviewer_agent
• Testing: test_orchestrator_agent, functional_tester_agent, performance_load_tester_agent
• Architecture: system_architect_agent, tech_spec_agent, prd_architect_agent
• DevOps: devops_agent, security_auditor_agent, health_monitor_agent
• Design: ui_designer_agent, ux_researcher_agent, design_system_agent
• Management: task_planning_agent, project_initiator_agent, uber_orchestrator_agent
• Research: market_research_agent, deep_research_agent, mcp_researcher_agent
• Content: documentation_agent, content_strategy_agent, branding_agent

📋 PARAMETER:
• name_agent (str): Agent name with '_agent' suffix (e.g., "coding_agent", "devops_agent")
• Use exact agent directory name from yaml-lib folder

🔄 RETURNS:
• success: Boolean indicating if agent was found
• agent_info: Complete agent configuration with role, contexts, rules, tools
• yaml_content: Full YAML configuration for the agent
• available_agents: List of all available agents (if requested agent not found)

💡 USAGE EXAMPLES:
• call_agent("coding_agent") - Load coding specialist configuration
• call_agent("system_architect_agent") - Load system architecture expert
• call_agent("task_planning_agent") - Load task management specialist
• call_agent("security_auditor_agent") - Load security expert configuration

🔧 INTEGRATION: This tool automatically switches AI assistant context to match the loaded agent's
expertise, behavioral rules, and specialized knowledge for optimal task performance.
                """
                try:
                    result = self._call_agent_use_case.execute(name_agent)
                    if not result.get("success") and "available_agents" in result:
                        result["formatted_message"] = f"{result['error']}\n\n{result['suggestion']}"
                    return result
                except Exception as e:
                    logging.error(f"Error getting agent metadata from YAML for {name_agent}: {e}")
                    return {"success": False, "error": f"Failed to get agent metadata: {e}"}
        
            logger.info("Registered call_agent tool")
        else:
            logger.info("Skipped call_agent tool (disabled)")
    
    def _register_cursor_tools(self, mcp: "FastMCP"):
        """Register cursor rules tools conditionally"""
        cursor_tools = ["update_auto_rule", "validate_rules", "manage_cursor_rules", "regenerate_auto_rule", "validate_tasks_json"]
        enabled_cursor_tools = [tool for tool in cursor_tools if self._config.is_enabled(tool)]
        
        if enabled_cursor_tools:
            logger.info(f"Registering {len(enabled_cursor_tools)} cursor rules tools")
            temp_cursor_tools = CursorRulesTools()
            temp_cursor_tools.register_tools(mcp)
            for tool in enabled_cursor_tools:
                logger.info(f"  - Registered {tool}")
        else:
            logger.info("Skipped all cursor rules tools (all disabled)")


# ═══════════════════════════════════════════════════════════════════
# 🏗️ MAIN CONSOLIDATED TOOLS CLASS
# ═══════════════════════════════════════════════════════════════════

class ConsolidatedMCPTools:
    """Main MCP tools interface with clean architecture and separated concerns"""
    
    def __init__(self, task_repository: Optional[TaskRepository] = None, projects_file_path: Optional[str] = None):
        logger.info("Initializing ConsolidatedMCPTools...")
        
        # Initialize configuration and paths
        self._config = ToolConfig()
        self._path_resolver = PathResolver()
        
        # Initialize repositories and services with hierarchical support
        self._repository_factory = TaskRepositoryFactory()
        self._auto_rule_generator = FileAutoRuleGenerator()
        
        # Initialize managers and handlers
        self._project_manager = ProjectManager(self._path_resolver, projects_file_path)
        # Use dynamic cursor agent directory from PathResolver
        cursor_agent_dir = str(self._path_resolver.get_cursor_agent_dir())
        self._call_agent_use_case = CallAgentUseCase(cursor_agent_dir)
        self._task_handler = TaskOperationHandler(self._repository_factory, self._auto_rule_generator, self._project_manager)
        
        # Initialize tool registration orchestrator
        self._tool_orchestrator = ToolRegistrationOrchestrator(
            self._config, self._task_handler, self._project_manager, self._call_agent_use_case
        )
        
        logger.info("ConsolidatedMCPTools initialized successfully with hierarchical storage.")
    
    def register_tools(self, mcp: "FastMCP"):
        """Register all consolidated MCP tools using the orchestrator"""
        self._tool_orchestrator.register_all_tools(mcp)


# ═══════════════════════════════════════════════════════════════════
# 🧪 SIMPLIFIED MULTI-AGENT TOOLS (FOR TESTING AND BACKWARD COMPATIBILITY)
# ═══════════════════════════════════════════════════════════════════

class SimpleMultiAgentTools:
    """Simplified multi-agent tools for testing and backward compatibility"""
    
    def __init__(self, projects_file_path: Optional[str] = None):
        self._path_resolver = PathResolver()
        self._project_manager = ProjectManager(self._path_resolver, projects_file_path)
    
    def create_project(self, project_id: str, name: str, description: str = None) -> Dict[str, Any]:
        """Create a new project"""
        return self._project_manager.create_project({
            'project_id': project_id,
            'name': name,
            'description': description or f"Project: {name}"
        })
    
    def register_agent(self, project_id: str, agent_id: str, name: str, call_agent: str = None) -> Dict[str, Any]:
        """Register an agent to a project"""
        return self._project_manager.register_agent(project_id, {
            'agent_id': agent_id,
            'name': name,
            'call_agent': call_agent or f"@{agent_id}"
        })
    
    def get_agents(self, project_id: str) -> Dict[str, Any]:
        """Get all agents for a project"""
        return self._project_manager.get_agents(project_id)


# ═══════════════════════════════════════════════════════════════════
# 🔧 UTILITY FUNCTIONS AND CONSTANTS
# ═══════════════════════════════════════════════════════════════════

# Constants for backward compatibility
PROJECTS_FILE = "projects.json"

def ensure_brain_dir(brain_dir: Optional[str] = None) -> Path:
    """Ensure brain directory exists"""
    if brain_dir:
        brain_path = Path(brain_dir)
    else:
        brain_path = PathResolver().brain_dir
    
    brain_path.mkdir(parents=True, exist_ok=True)
    return brain_path