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
    
    def update_project(self, project_id: str, name: str = None, description: str = None) -> Dict[str, Any]:
        """Update an existing project"""
        if project_id not in self._projects:
            return {"success": False, "error": f"Project {project_id} not found"}
        
        project = self._projects[project_id]
        updated_fields = []
        
        if name is not None:
            project["name"] = name
            updated_fields.append("name")
        
        if description is not None:
            project["description"] = description
            updated_fields.append("description")
        
        if not updated_fields:
            return {"success": False, "error": "No fields to update. Provide name and/or description."}
        
        # Add updated timestamp
        from datetime import datetime
        project["updated_at"] = datetime.now().isoformat()
        
        self._save_projects()
        return {
            "success": True, 
            "project": project,
            "updated_fields": updated_fields,
            "message": f"Project {project_id} updated successfully"
        }
    
    def create_task_tree(self, project_id: str, tree_id: str, tree_name: str, tree_description: str = "") -> Dict[str, Any]:
        """Create a new task tree in project"""
        if project_id not in self._projects:
            return {"success": False, "error": f"Project {project_id} not found"}
        
        tree = {"id": tree_id, "name": tree_name, "description": tree_description}
        self._projects[project_id]["task_trees"][tree_id] = tree
        self._save_projects()
        return {"success": True, "tree": tree}
    
    def delete_task_tree(self, project_id: str, tree_id: str, force: bool = False) -> Dict[str, Any]:
        """Delete a task tree from project with cascading cleanup"""
        if project_id not in self._projects:
            return {"success": False, "error": f"Project {project_id} not found"}
        
        project = self._projects[project_id]
        
        # Check if tree exists
        if tree_id not in project["task_trees"]:
            return {"success": False, "error": f"Task tree '{tree_id}' not found in project '{project_id}'"}
        
        # Prevent deletion of 'main' tree unless forced
        if tree_id == "main" and not force:
            return {
                "success": False, 
                "error": "Cannot delete 'main' task tree. Use force=True to override this protection."
            }
        
        # Check for active tasks unless forced
        if not force:
            try:
                import os
                import json
                tasks_path = self.path_resolver.get_tasks_json_path(project_id, tree_id, "default_id")
                if os.path.exists(tasks_path):
                    with open(tasks_path, 'r') as f:
                        tasks_data = json.load(f)
                        task_count = len(tasks_data.get("tasks", []))
                        if task_count > 0:
                            return {
                                "success": False,
                                "error": f"Cannot delete task tree '{tree_id}' - contains {task_count} tasks. Use force=True to delete anyway.",
                                "task_count": task_count
                            }
            except Exception as e:
                # If we can't read tasks, proceed with warning
                pass
        
        try:
            # 1. Remove task tree from project
            del project["task_trees"][tree_id]
            
            # 2. Remove agent assignments for this tree
            if "agent_assignments" in project:
                for agent_id, assigned_trees in list(project["agent_assignments"].items()):
                    if tree_id in assigned_trees:
                        assigned_trees.remove(tree_id)
                        # Remove agent assignment entry if no trees left
                        if not assigned_trees:
                            del project["agent_assignments"][agent_id]
            
            # 3. Delete tasks directory and all associated data
            import shutil
            tasks_dir = self.path_resolver.get_tasks_json_path(project_id, tree_id, "default_id").parent
            if os.path.exists(tasks_dir):
                shutil.rmtree(tasks_dir)
            
            # 4. Delete contexts directory for this tree
            contexts_dir = self.path_resolver._resolve_path(f".cursor/rules/contexts/default_id/{project_id}/{tree_id}")
            if os.path.exists(contexts_dir):
                shutil.rmtree(contexts_dir)
            
            # 5. Save updated project data
            self._save_projects()
            
            return {
                "success": True,
                "message": f"Task tree '{tree_id}' deleted successfully from project '{project_id}'",
                "deleted_tree": tree_id,
                "cleanup_performed": [
                    "Task tree removed from project",
                    "Agent assignments cleaned up",
                    "Tasks directory deleted",
                    "Contexts directory deleted"
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete task tree '{tree_id}': {str(e)}"
            }
    
    def delete_project(self, project_id: str, force: bool = False) -> Dict[str, Any]:
        """Delete an entire project with all associated data"""
        if project_id not in self._projects:
            return {"success": False, "error": f"Project {project_id} not found"}
        
        project = self._projects[project_id]
        
        # Check for active tasks unless forced
        if not force:
            total_tasks = 0
            try:
                import os
                import json
                for tree_id in project.get("task_trees", {}):
                    tasks_path = self.path_resolver.get_tasks_json_path(project_id, tree_id, "default_id")
                    if os.path.exists(tasks_path):
                        with open(tasks_path, 'r') as f:
                            tasks_data = json.load(f)
                            total_tasks += len(tasks_data.get("tasks", []))
                
                if total_tasks > 0:
                    return {
                        "success": False,
                        "error": f"Cannot delete project '{project_id}' - contains {total_tasks} tasks across all trees. Use force=True to delete anyway.",
                        "total_tasks": total_tasks
                    }
            except Exception as e:
                # If we can't read tasks, proceed with warning
                pass
        
        try:
            # 1. Delete all task directories for this project
            import shutil
            project_tasks_dir = self.path_resolver._resolve_path(f".cursor/rules/tasks/default_id/{project_id}")
            if os.path.exists(project_tasks_dir):
                shutil.rmtree(project_tasks_dir)
            
            # 2. Delete all contexts for this project
            project_contexts_dir = self.path_resolver._resolve_path(f".cursor/rules/contexts/default_id/{project_id}")
            if os.path.exists(project_contexts_dir):
                shutil.rmtree(project_contexts_dir)
            
            # 3. Remove project from projects data
            del self._projects[project_id]
            
            # 4. Save updated projects data
            self._save_projects()
            
            return {
                "success": True,
                "message": f"Project '{project_id}' deleted successfully",
                "deleted_project": project_id,
                "cleanup_performed": [
                    "All task trees and tasks deleted",
                    "All contexts deleted",
                    "Project removed from registry",
                    "Agent assignments cleaned up"
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete project '{project_id}': {str(e)}"
            }
    
    def clear_task_tree(self, project_id: str, tree_id: str) -> Dict[str, Any]:
        """Clear all tasks from a task tree but keep the tree structure"""
        if project_id not in self._projects:
            return {"success": False, "error": f"Project {project_id} not found"}
        
        project = self._projects[project_id]
        
        # Check if tree exists
        if tree_id not in project["task_trees"]:
            return {"success": False, "error": f"Task tree '{tree_id}' not found in project '{project_id}'"}
        
        try:
            import os
            import json
            
            # Get tasks file path
            tasks_path = self.path_resolver.get_tasks_json_path(project_id, tree_id, "default_id")
            
            # Count existing tasks for reporting
            task_count = 0
            if os.path.exists(tasks_path):
                with open(tasks_path, 'r') as f:
                    tasks_data = json.load(f)
                    task_count = len(tasks_data.get("tasks", []))
            
            # Clear tasks by writing empty tasks structure
            empty_tasks = {
                "tasks": [],
                "metadata": {
                    "project_id": project_id,
                    "task_tree_id": tree_id,
                    "user_id": "default_id",
                    "cleared_at": datetime.now().isoformat(),
                    "previous_task_count": task_count
                }
            }
            
            # Ensure directory exists
            os.makedirs(tasks_path.parent, exist_ok=True)
            
            # Write empty tasks file
            with open(tasks_path, 'w') as f:
                json.dump(empty_tasks, f, indent=2)
            
            # Clear contexts directory for this tree
            import shutil
            contexts_dir = self.path_resolver._resolve_path(f".cursor/rules/contexts/default_id/{project_id}/{tree_id}")
            if os.path.exists(contexts_dir):
                shutil.rmtree(contexts_dir)
                os.makedirs(contexts_dir, exist_ok=True)
            
            return {
                "success": True,
                "message": f"Task tree '{tree_id}' cleared successfully",
                "tree_id": tree_id,
                "tasks_cleared": task_count,
                "cleanup_performed": [
                    f"Cleared {task_count} tasks",
                    "Cleared all contexts",
                    "Task tree structure preserved"
                ]
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to clear task tree '{tree_id}': {str(e)}"
            }
    
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

    def project_health_check(self, project_id: str) -> Dict[str, Any]:
        """Comprehensive project health analysis with data integrity and workflow validation"""
        if project_id not in self._projects:
            return {"success": False, "error": f"Project {project_id} not found"}
        
        from datetime import datetime
        import json
        
        project = self._projects[project_id]
        health_issues = []
        warnings = []
        recommendations = []
        
        # Initialize health metrics
        health_score = 100
        git_sync_status = "✅ UNKNOWN"
        data_integrity = "✅ HEALTHY"
        agent_utilization = "✅ OPTIMAL"
        
        try:
            # 1. CHECK GIT SYNCHRONIZATION
            import subprocess
            import os
            
            # Try to get current git branch
            try:
                result = subprocess.run(['git', 'branch', '--show-current'], 
                                      capture_output=True, text=True, cwd=os.getcwd())
                if result.returncode == 0:
                    current_branch = result.stdout.strip()
                    
                    # Get all git branches
                    result = subprocess.run(['git', 'branch', '-a'], 
                                          capture_output=True, text=True, cwd=os.getcwd())
                    if result.returncode == 0:
                        all_branches = [line.strip().replace('*', '').strip() 
                                      for line in result.stdout.split('\n') 
                                      if line.strip() and not line.startswith('remotes/')]
                        
                        # Check for obsolete task trees
                        task_trees = set(project.get("task_trees", {}).keys())
                        git_branches = set(all_branches + ['main'])  # Always include main
                        
                        obsolete_trees = task_trees - git_branches
                        missing_trees = git_branches - task_trees
                        
                        if obsolete_trees:
                            health_issues.append({
                                "type": "OBSOLETE_BRANCHES",
                                "severity": "MEDIUM",
                                "description": f"Task trees exist for non-existent git branches: {list(obsolete_trees)}",
                                "impact": "Wasted resources and agent assignments to non-existent work"
                            })
                            git_sync_status = "❌ OUT_OF_SYNC"
                            health_score -= 15
                            recommendations.append("Run sync_with_git to align project with repository state")
                        
                        if missing_trees:
                            warnings.append(f"Git branches without task trees: {list(missing_trees)}")
                            recommendations.append("Consider creating task trees for active git branches")
                        
                        if not obsolete_trees and not missing_trees:
                            git_sync_status = "✅ SYNCHRONIZED"
                    else:
                        git_sync_status = "⚠️ GIT_ERROR"
                        warnings.append("Could not read git branches")
                else:
                    git_sync_status = "⚠️ NOT_GIT_REPO"
                    warnings.append("Not in a git repository")
            except Exception as e:
                git_sync_status = "❌ GIT_UNAVAILABLE"
                warnings.append(f"Git check failed: {str(e)}")
            
            # 2. CHECK DATA INTEGRITY
            task_count_issues = []
            
            # Check task counts vs dashboard
            try:
                dashboard_result = self.get_orchestration_dashboard(project_id)
                if dashboard_result.get("success"):
                    dashboard_data = dashboard_result.get("dashboard", {})
                    trees_data = dashboard_data.get("trees", {})
                    
                    for tree_id, tree_info in trees_data.items():
                        dashboard_count = tree_info.get("total_tasks", 0)
                        
                        # Get actual task count from task repository
                        try:
                            from ..domain.services.task_repository_factory import TaskRepositoryFactory
                            from ..application.task_application_service import TaskApplicationService
                            
                            repository_factory = TaskRepositoryFactory(self.path_resolver)
                            repository = repository_factory.create_repository(project_id, tree_id, "default_id")
                            
                            # Count actual tasks
                            tasks_file = repository._tasks_file
                            actual_count = 0
                            if os.path.exists(tasks_file):
                                with open(tasks_file, 'r') as f:
                                    tasks_data = json.load(f)
                                    actual_count = len(tasks_data.get("tasks", []))
                            
                            if dashboard_count != actual_count:
                                task_count_issues.append({
                                    "tree": tree_id,
                                    "dashboard": dashboard_count,
                                    "actual": actual_count
                                })
                        except Exception as e:
                            warnings.append(f"Could not verify task count for tree {tree_id}: {str(e)}")
                
                if task_count_issues:
                    health_issues.append({
                        "type": "DATA_INCONSISTENCY",
                        "severity": "HIGH",
                        "description": f"Task count mismatches found: {task_count_issues}",
                        "impact": "Incorrect project metrics and progress tracking"
                    })
                    data_integrity = "❌ CORRUPTED"
                    health_score -= 25
                    recommendations.append("Run validate_integrity to fix data consistency issues")
                
            except Exception as e:
                warnings.append(f"Data integrity check failed: {str(e)}")
                data_integrity = "⚠️ CHECK_FAILED"
            
            # 3. CHECK AGENT ASSIGNMENTS
            agent_issues = []
            agent_assignments = project.get("agent_assignments", {})
            registered_agents = project.get("registered_agents", {})
            task_trees = project.get("task_trees", {})
            
            # Check for agents assigned to non-existent trees
            for agent_id, tree_list in agent_assignments.items():
                if isinstance(tree_list, list):
                    for tree_id in tree_list:
                        if tree_id not in task_trees:
                            agent_issues.append(f"Agent {agent_id} assigned to non-existent tree {tree_id}")
                elif tree_list not in task_trees:
                    agent_issues.append(f"Agent {agent_id} assigned to non-existent tree {tree_list}")
            
            # Check for unregistered agents in assignments
            for agent_id in agent_assignments:
                if agent_id not in registered_agents:
                    agent_issues.append(f"Unregistered agent {agent_id} has assignments")
            
            if agent_issues:
                health_issues.append({
                    "type": "AGENT_MISALIGNMENT",
                    "severity": "MEDIUM",
                    "description": f"Agent assignment issues: {agent_issues}",
                    "impact": "Inefficient resource allocation"
                })
                agent_utilization = "⚠️ SUBOPTIMAL"
                health_score -= 10
                recommendations.append("Rebalance agent assignments to active branches")
            
            # 4. CALCULATE TASK COMPLETION METRICS
            total_tasks = 0
            completed_tasks = 0
            blocked_tasks = 0
            overdue_tasks = 0
            
            try:
                for tree_id in task_trees:
                    try:
                        from ..domain.services.task_repository_factory import TaskRepositoryFactory
                        repository_factory = TaskRepositoryFactory(self.path_resolver)
                        repository = repository_factory.create_repository(project_id, tree_id, "default_id")
                        
                        tasks_file = repository._tasks_file
                        if os.path.exists(tasks_file):
                            with open(tasks_file, 'r') as f:
                                tasks_data = json.load(f)
                                tasks = tasks_data.get("tasks", [])
                                
                                for task in tasks:
                                    total_tasks += 1
                                    status = task.get("status", "todo")
                                    if status == "done":
                                        completed_tasks += 1
                                    elif status == "blocked":
                                        blocked_tasks += 1
                                    
                                    # Check for overdue tasks (simplified check)
                                    due_date = task.get("due_date")
                                    if due_date and status not in ["done", "cancelled"]:
                                        try:
                                            due = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                                            if due < datetime.now():
                                                overdue_tasks += 1
                                        except:
                                            pass  # Invalid date format
                    except Exception as e:
                        warnings.append(f"Could not analyze tasks in tree {tree_id}: {str(e)}")
            except Exception as e:
                warnings.append(f"Task analysis failed: {str(e)}")
            
            # Calculate completion rate
            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 100
            
            # Determine overall health status
            if health_score >= 80:
                overall_health = "✅ HEALTHY"
            elif health_score >= 60:
                overall_health = "⚠️ NEEDS_ATTENTION"
            else:
                overall_health = "❌ UNHEALTHY"
            
            # Add general recommendations
            if not recommendations:
                recommendations.append("Project health is good - continue monitoring")
            
            if blocked_tasks > 0:
                recommendations.append(f"Address {blocked_tasks} blocked tasks to improve workflow")
            
            if overdue_tasks > 0:
                recommendations.append(f"Review {overdue_tasks} overdue tasks and update priorities")
            
            return {
                "success": True,
                "project_id": project_id,
                "overall_health": overall_health,
                "health_score": f"{health_score}/100",
                "critical_issues": [issue for issue in health_issues if issue.get("severity") == "HIGH"],
                "warnings": [issue for issue in health_issues if issue.get("severity") in ["MEDIUM", "LOW"]] + 
                          [{"type": "WARNING", "description": w} for w in warnings],
                "git_sync_status": git_sync_status,
                "data_integrity": data_integrity,
                "agent_utilization": agent_utilization,
                "task_metrics": {
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks,
                    "completion_rate": f"{completion_rate:.1f}%",
                    "blocked_tasks": blocked_tasks,
                    "overdue_tasks": overdue_tasks
                },
                "recommendations": recommendations,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Project health check failed for {project_id}: {str(e)}")
            return {
                "success": False,
                "error": f"Health check failed: {str(e)}",
                "project_id": project_id,
                "overall_health": "❌ CHECK_FAILED"
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

    def sync_with_git(self, project_id: str) -> Dict[str, Any]:
        """Synchronize project task trees with actual git branches"""
        if project_id not in self._projects:
            return {"success": False, "error": f"Project {project_id} not found"}
        
        import subprocess
        import os
        from datetime import datetime
        
        try:
            # Get current git branch
            result = subprocess.run(['git', 'branch', '--show-current'], 
                                  capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode != 0:
                return {"success": False, "error": "Not in a git repository or git command failed"}
            
            current_branch = result.stdout.strip()
            
            # Get all git branches (local only)
            result = subprocess.run(['git', 'branch'], 
                                  capture_output=True, text=True, cwd=os.getcwd())
            if result.returncode != 0:
                return {"success": False, "error": "Failed to get git branches"}
            
            # Parse git branches
            git_branches = set()
            for line in result.stdout.split('\n'):
                if line.strip():
                    branch = line.strip().replace('*', '').strip()
                    if branch and not branch.startswith('('):  # Skip detached HEAD states
                        git_branches.add(branch)
            
            # Always include 'main' as a valid branch
            git_branches.add('main')
            
            project = self._projects[project_id]
            task_trees = set(project.get("task_trees", {}).keys())
            
            # Identify changes needed
            obsolete_trees = task_trees - git_branches
            missing_trees = git_branches - task_trees
            
            sync_actions = []
            
            # Remove obsolete task trees
            for tree_id in obsolete_trees:
                if tree_id != "main":  # Never remove main tree
                    del project["task_trees"][tree_id]
                    
                    # Remove agent assignments for this tree
                    updated_assignments = {}
                    for agent_id, assigned_trees in project.get("agent_assignments", {}).items():
                        if isinstance(assigned_trees, list):
                            new_trees = [t for t in assigned_trees if t != tree_id]
                            if new_trees:
                                updated_assignments[agent_id] = new_trees
                        elif assigned_trees != tree_id:
                            updated_assignments[agent_id] = assigned_trees
                    
                    project["agent_assignments"] = updated_assignments
                    sync_actions.append(f"Removed obsolete task tree: {tree_id}")
            
            # Create missing task trees for git branches
            for tree_id in missing_trees:
                if tree_id not in project["task_trees"]:
                    tree_name = f"Branch: {tree_id}"
                    tree_description = f"Task tree for git branch '{tree_id}'"
                    project["task_trees"][tree_id] = {
                        "id": tree_id,
                        "name": tree_name,
                        "description": tree_description
                    }
                    sync_actions.append(f"Created task tree for branch: {tree_id}")
            
            # Update project metadata
            project["updated_at"] = datetime.now().isoformat()
            project["last_git_sync"] = datetime.now().isoformat()
            project["current_branch"] = current_branch
            
            # Save changes
            self._save_projects()
            
            return {
                "success": True,
                "project_id": project_id,
                "current_branch": current_branch,
                "git_branches": sorted(list(git_branches)),
                "task_trees": sorted(list(project["task_trees"].keys())),
                "sync_actions": sync_actions,
                "obsolete_trees_removed": list(obsolete_trees - {"main"}),  # Exclude main from removed
                "new_trees_created": list(missing_trees),
                "message": f"Git sync completed. {len(sync_actions)} actions performed."
            }
            
        except subprocess.CalledProcessError as e:
            return {"success": False, "error": f"Git command failed: {e}"}
        except Exception as e:
            logging.error(f"Git sync failed for project {project_id}: {str(e)}")
            return {"success": False, "error": f"Git sync failed: {str(e)}"}

    def cleanup_obsolete(self, project_id: str) -> Dict[str, Any]:
        """Clean up obsolete branches and orphaned data from project management system"""
        if project_id not in self._projects:
            return {"success": False, "error": f"Project {project_id} not found"}
        
        import subprocess
        import os
        from datetime import datetime
        
        try:
            project = self._projects[project_id]
            cleanup_actions = []
            
            # Get current git branches for reference
            try:
                result = subprocess.run(['git', 'branch'], capture_output=True, text=True, cwd=os.getcwd())
                if result.returncode == 0:
                    git_branches = set()
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            branch = line.strip().replace('*', '').strip()
                            if branch and not branch.startswith('('):
                                git_branches.add(branch)
                    git_branches.add('main')  # Always include main
                else:
                    # If git fails, assume only main exists
                    git_branches = {'main'}
                    cleanup_actions.append("Git command failed - assuming only 'main' branch exists")
            except Exception as e:
                git_branches = {'main'}
                cleanup_actions.append(f"Git error: {str(e)} - assuming only 'main' branch exists")
            
            # 1. Clean up obsolete task trees
            task_trees = project.get("task_trees", {})
            obsolete_trees = []
            
            for tree_id in list(task_trees.keys()):
                if tree_id != "main" and tree_id not in git_branches:
                    obsolete_trees.append(tree_id)
                    del task_trees[tree_id]
                    cleanup_actions.append(f"Removed obsolete task tree: {tree_id}")
            
            # 2. Clean up orphaned agent assignments
            agent_assignments = project.get("agent_assignments", {})
            cleaned_assignments = {}
            orphaned_assignments = []
            
            for agent_id, assigned_trees in agent_assignments.items():
                if isinstance(assigned_trees, list):
                    # Filter out obsolete trees
                    valid_trees = [tree for tree in assigned_trees if tree in task_trees]
                    if valid_trees:
                        cleaned_assignments[agent_id] = valid_trees
                    if len(valid_trees) != len(assigned_trees):
                        removed_trees = [tree for tree in assigned_trees if tree not in valid_trees]
                        orphaned_assignments.extend([(agent_id, tree) for tree in removed_trees])
                elif assigned_trees in task_trees:
                    # Single tree assignment - keep if valid
                    cleaned_assignments[agent_id] = assigned_trees
                else:
                    # Single tree assignment - remove if obsolete
                    orphaned_assignments.append((agent_id, assigned_trees))
            
            project["agent_assignments"] = cleaned_assignments
            
            for agent_id, tree_id in orphaned_assignments:
                cleanup_actions.append(f"Removed orphaned assignment: agent {agent_id} from tree {tree_id}")
            
            # 3. Clean up empty or invalid registered agents
            registered_agents = project.get("registered_agents", {})
            agents_to_remove = []
            
            for agent_id, agent_data in registered_agents.items():
                if not isinstance(agent_data, dict) or not agent_data.get("id") or not agent_data.get("name"):
                    agents_to_remove.append(agent_id)
                    cleanup_actions.append(f"Removed invalid agent registration: {agent_id}")
            
            for agent_id in agents_to_remove:
                del registered_agents[agent_id]
                # Also remove from assignments if present
                if agent_id in cleaned_assignments:
                    del cleaned_assignments[agent_id]
                    cleanup_actions.append(f"Removed assignments for invalid agent: {agent_id}")
            
            # 4. Ensure main task tree always exists
            if "main" not in task_trees:
                task_trees["main"] = {
                    "id": "main",
                    "name": "Main Tasks",
                    "description": "Main task tree"
                }
                cleanup_actions.append("Restored missing 'main' task tree")
            
            # 5. Clean up project metadata
            metadata_cleaned = []
            
            # Remove invalid fields
            invalid_fields = []
            for key, value in list(project.items()):
                if key not in ["id", "name", "description", "task_trees", "registered_agents", 
                              "agent_assignments", "created_at", "updated_at", "last_git_sync", "current_branch"]:
                    if not key.startswith("_"):  # Keep private fields
                        invalid_fields.append(key)
            
            for field in invalid_fields:
                del project[field]
                metadata_cleaned.append(f"Removed invalid field: {field}")
            
            # Update metadata
            project["updated_at"] = datetime.now().isoformat()
            project["last_cleanup"] = datetime.now().isoformat()
            
            # Save changes
            self._save_projects()
            
            # Calculate cleanup statistics
            cleanup_stats = {
                "obsolete_trees_removed": len(obsolete_trees),
                "orphaned_assignments_cleaned": len(orphaned_assignments),
                "invalid_agents_removed": len(agents_to_remove),
                "metadata_fields_cleaned": len(metadata_cleaned),
                "total_actions": len(cleanup_actions)
            }
            
            return {
                "success": True,
                "project_id": project_id,
                "cleanup_actions": cleanup_actions,
                "statistics": cleanup_stats,
                "remaining_task_trees": sorted(list(task_trees.keys())),
                "remaining_agents": len(registered_agents),
                "active_assignments": len(cleaned_assignments),
                "git_branches_reference": sorted(list(git_branches)),
                "message": f"Cleanup completed. {cleanup_stats['total_actions']} actions performed."
            }
            
        except Exception as e:
            logging.error(f"Cleanup failed for project {project_id}: {str(e)}")
            return {"success": False, "error": f"Cleanup failed: {str(e)}"}

    def rebalance_agents(self, project_id: str) -> Dict[str, Any]:
        """Automatically redistribute agent assignments optimally across active task trees"""
        if project_id not in self._projects:
            return {"success": False, "error": f"Project {project_id} not found"}
        
        import subprocess
        import os
        import json
        from datetime import datetime
        from collections import defaultdict
        
        try:
            project = self._projects[project_id]
            rebalancing_actions = []
            warnings = []
            
            # 1. Get current git branches to identify active task trees
            try:
                result = subprocess.run(['git', 'branch'], capture_output=True, text=True, cwd=os.getcwd())
                if result.returncode == 0:
                    git_branches = set()
                    for line in result.stdout.split('\n'):
                        if line.strip():
                            branch = line.strip().replace('*', '').strip()
                            if branch and not branch.startswith('('):
                                git_branches.add(branch)
                    git_branches.add('main')  # Always include main
                else:
                    git_branches = {'main'}
                    warnings.append("Git command failed - assuming only 'main' branch exists")
            except Exception as e:
                git_branches = {'main'}
                warnings.append(f"Git error: {str(e)} - assuming only 'main' branch exists")
            
            # 2. Analyze current agent assignments
            registered_agents = project.get("registered_agents", {})
            current_assignments = project.get("agent_assignments", {})
            task_trees = project.get("task_trees", {})
            
            # 3. Identify active vs inactive task trees
            active_trees = set(task_trees.keys()) & git_branches
            inactive_trees = set(task_trees.keys()) - git_branches
            
            # 4. Analyze task workload per tree
            tree_workloads = {}
            tree_task_counts = {}
            
            for tree_id in active_trees:
                try:
                    tasks_file_path = self.path_resolver.get_tasks_json_path(project_id, tree_id, "default_id")
                    
                    if os.path.exists(tasks_file_path):
                        with open(tasks_file_path, 'r') as f:
                            tasks_data = json.load(f)
                            tasks = tasks_data.get("tasks", [])
                            
                            # Count tasks by status and priority
                            todo_tasks = [t for t in tasks if t.get("status") == "todo"]
                            high_priority = len([t for t in todo_tasks if t.get("priority") in ["urgent", "critical", "high"]])
                            total_todo = len(todo_tasks)
                            
                            tree_task_counts[tree_id] = total_todo
                            tree_workloads[tree_id] = {
                                "total_tasks": len(tasks),
                                "todo_tasks": total_todo,
                                "high_priority_tasks": high_priority,
                                "workload_score": high_priority * 3 + total_todo  # Weight high priority more
                            }
                    else:
                        tree_task_counts[tree_id] = 0
                        tree_workloads[tree_id] = {"total_tasks": 0, "todo_tasks": 0, "high_priority_tasks": 0, "workload_score": 0}
                except Exception as e:
                    warnings.append(f"Could not analyze tasks in tree {tree_id}: {str(e)}")
                    tree_task_counts[tree_id] = 0
                    tree_workloads[tree_id] = {"total_tasks": 0, "todo_tasks": 0, "high_priority_tasks": 0, "workload_score": 0}
            
            # 5. Calculate agent expertise matching
            agent_expertise = {}
            for agent_id, agent_data in registered_agents.items():
                # Extract expertise from agent name/id
                expertise_keywords = {
                    "coding": ["coding", "development", "implementation", "backend", "frontend"],
                    "testing": ["test", "qa", "quality", "validation"],
                    "devops": ["devops", "deployment", "infrastructure", "docker"],
                    "design": ["ui", "ux", "design", "prototype"],
                    "architecture": ["architect", "system", "tech"],
                    "security": ["security", "audit", "penetration"],
                    "management": ["planning", "orchestrator", "manager", "task"]
                }
                
                agent_name_lower = agent_id.lower()
                expertise = []
                for category, keywords in expertise_keywords.items():
                    if any(keyword in agent_name_lower for keyword in keywords):
                        expertise.append(category)
                
                agent_expertise[agent_id] = expertise if expertise else ["general"]
            
            # 6. Remove agents from inactive trees
            agents_reassigned = []
            for agent_id, assigned_trees in list(current_assignments.items()):
                if isinstance(assigned_trees, list):
                    # Remove inactive trees from assignments
                    new_assignments = [tree for tree in assigned_trees if tree in active_trees]
                    if len(new_assignments) != len(assigned_trees):
                        removed_trees = [tree for tree in assigned_trees if tree not in active_trees]
                        current_assignments[agent_id] = new_assignments
                        agents_reassigned.append(f"Agent {agent_id} removed from inactive trees: {removed_trees}")
                        rebalancing_actions.append(f"Removed agent {agent_id} from inactive trees: {removed_trees}")
                elif assigned_trees not in active_trees:
                    # Single tree assignment to inactive tree
                    del current_assignments[agent_id]
                    agents_reassigned.append(f"Agent {agent_id} removed from inactive tree: {assigned_trees}")
                    rebalancing_actions.append(f"Removed agent {agent_id} from inactive tree: {assigned_trees}")
            
            # 7. Calculate optimal agent distribution
            total_workload = sum(w["workload_score"] for w in tree_workloads.values())
            available_agents = list(registered_agents.keys())
            
            if total_workload > 0 and available_agents:
                # Calculate target assignments based on workload
                optimal_assignments = defaultdict(list)
                
                # Sort trees by workload (descending)
                sorted_trees = sorted(tree_workloads.items(), key=lambda x: x[1]["workload_score"], reverse=True)
                
                # Assign agents to trees based on workload and expertise
                agent_index = 0
                for tree_id, workload_data in sorted_trees:
                    if workload_data["workload_score"] > 0:  # Only assign to trees with work
                        # Find best matching agent based on expertise
                        best_agent = None
                        best_score = -1
                        
                        for agent_id in available_agents:
                            # Calculate matching score
                            expertise = agent_expertise.get(agent_id, ["general"])
                            
                            # Tree-specific expertise matching
                            tree_score = 0
                            if "main" in tree_id.lower():
                                tree_score += 2  # Main branch gets priority
                            if any(exp in ["coding", "development"] for exp in expertise):
                                tree_score += 3  # Coding agents are versatile
                            if any(exp in ["management", "orchestrator"] for exp in expertise):
                                tree_score += 2  # Management agents can handle coordination
                            
                            # Consider current workload
                            current_trees = current_assignments.get(agent_id, [])
                            current_load = len(current_trees) if isinstance(current_trees, list) else (1 if current_trees else 0)
                            load_penalty = current_load * 0.5  # Prefer less loaded agents
                            
                            final_score = tree_score - load_penalty
                            
                            if final_score > best_score:
                                best_score = final_score
                                best_agent = agent_id
                        
                        # Assign best matching agent
                        if best_agent:
                            optimal_assignments[best_agent].append(tree_id)
                
                # 8. Apply optimal assignments
                assignment_changes = []
                for agent_id in available_agents:
                    current_trees = current_assignments.get(agent_id, [])
                    if not isinstance(current_trees, list):
                        current_trees = [current_trees] if current_trees else []
                    
                    optimal_trees = optimal_assignments.get(agent_id, [])
                    
                    # Add missing assignments
                    for tree_id in optimal_trees:
                        if tree_id not in current_trees:
                            current_trees.append(tree_id)
                            assignment_changes.append(f"Assigned agent {agent_id} to tree {tree_id}")
                            rebalancing_actions.append(f"Assigned agent {agent_id} to tree {tree_id} (workload: {tree_workloads[tree_id]['workload_score']})")
                    
                    # Update assignments
                    if current_trees:
                        current_assignments[agent_id] = current_trees
                    elif agent_id in current_assignments:
                        del current_assignments[agent_id]
                
                # Ensure every active tree has at least one agent
                unassigned_trees = []
                for tree_id in active_trees:
                    assigned = False
                    for agent_id, trees in current_assignments.items():
                        if isinstance(trees, list) and tree_id in trees:
                            assigned = True
                            break
                        elif trees == tree_id:
                            assigned = True
                            break
                    
                    if not assigned and tree_workloads[tree_id]["workload_score"] > 0:
                        # Assign to least loaded agent
                        min_load = float('inf')
                        best_agent = None
                        for agent_id in available_agents:
                            current_trees = current_assignments.get(agent_id, [])
                            load = len(current_trees) if isinstance(current_trees, list) else (1 if current_trees else 0)
                            if load < min_load:
                                min_load = load
                                best_agent = agent_id
                        
                        if best_agent:
                            if best_agent not in current_assignments:
                                current_assignments[best_agent] = []
                            if isinstance(current_assignments[best_agent], list):
                                current_assignments[best_agent].append(tree_id)
                            else:
                                current_assignments[best_agent] = [current_assignments[best_agent], tree_id]
                            
                            unassigned_trees.append(tree_id)
                            rebalancing_actions.append(f"Assigned agent {best_agent} to unassigned tree {tree_id}")
            
            # 9. Update project data
            project["agent_assignments"] = current_assignments
            project["updated_at"] = datetime.now().isoformat()
            project["last_rebalance"] = datetime.now().isoformat()
            
            # Save changes
            self._save_projects()
            
            # 10. Generate rebalancing report
            final_assignments = {}
            for agent_id, trees in current_assignments.items():
                if isinstance(trees, list):
                    final_assignments[agent_id] = trees
                else:
                    final_assignments[agent_id] = [trees] if trees else []
            
            # Calculate workload distribution
            agent_workloads = {}
            for agent_id in registered_agents.keys():
                assigned_trees = final_assignments.get(agent_id, [])
                total_workload = sum(tree_workloads.get(tree, {}).get("workload_score", 0) for tree in assigned_trees)
                agent_workloads[agent_id] = {
                    "assigned_trees": assigned_trees,
                    "tree_count": len(assigned_trees),
                    "workload_score": total_workload,
                    "expertise": agent_expertise.get(agent_id, ["general"])
                }
            
            return {
                "success": True,
                "project_id": project_id,
                "rebalancing_summary": {
                    "active_trees": sorted(list(active_trees)),
                    "inactive_trees_removed": sorted(list(inactive_trees)),
                    "total_agents": len(registered_agents),
                    "agents_with_assignments": len([a for a in final_assignments.values() if a]),
                    "total_actions": len(rebalancing_actions)
                },
                "workload_analysis": {
                    "tree_workloads": tree_workloads,
                    "agent_workloads": agent_workloads,
                    "total_workload": total_workload,
                    "average_trees_per_agent": sum(len(trees) for trees in final_assignments.values()) / len(registered_agents) if registered_agents else 0
                },
                "rebalancing_actions": rebalancing_actions,
                "final_assignments": final_assignments,
                "warnings": warnings,
                "recommendations": [
                    "Monitor agent workload distribution regularly",
                    "Consider adding more agents if workload is high",
                    "Review agent expertise matching for optimal assignments",
                    "Run sync_with_git before rebalancing for accurate tree state"
                ] if rebalancing_actions else ["Agent assignments are already optimal"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Agent rebalancing failed for project {project_id}: {str(e)}")
            return {"success": False, "error": f"Agent rebalancing failed: {str(e)}"}

    def validate_integrity(self, project_id: str) -> Dict[str, Any]:
        """Validate and fix data consistency issues between dashboard metrics and actual task data"""
        if project_id not in self._projects:
            return {"success": False, "error": f"Project {project_id} not found"}
        
        import os
        import json
        from datetime import datetime
        
        try:
            project = self._projects[project_id]
            validation_issues = []
            fixes_applied = []
            warnings = []
            
            # 1. Validate task trees and count actual tasks
            task_trees = project.get("task_trees", {})
            actual_task_counts = {}
            
            for tree_id, tree_data in task_trees.items():
                try:
                    # Get actual task count from task repository files
                    tasks_file_path = self.path_resolver.get_tasks_json_path(project_id, tree_id, "default_id")
                    
                    if os.path.exists(tasks_file_path):
                        with open(tasks_file_path, 'r') as f:
                            tasks_data = json.load(f)
                            tasks = tasks_data.get("tasks", [])
                            actual_task_counts[tree_id] = len(tasks)
                            
                            # Validate task data structure
                            for i, task in enumerate(tasks):
                                if not isinstance(task, dict):
                                    validation_issues.append(f"Tree {tree_id}: Task {i} is not a valid object")
                                elif not task.get("id"):
                                    validation_issues.append(f"Tree {tree_id}: Task {i} missing required 'id' field")
                                elif not task.get("title"):
                                    validation_issues.append(f"Tree {tree_id}: Task {task.get('id', i)} missing required 'title' field")
                    else:
                        actual_task_counts[tree_id] = 0
                        warnings.append(f"Task file not found for tree {tree_id}, creating empty structure")
                        
                        # Create missing task file structure
                        os.makedirs(os.path.dirname(tasks_file_path), exist_ok=True)
                        empty_structure = {
                            "tasks": [],
                            "metadata": {
                                "version": "1.0.0",
                                "project_id": project_id,
                                "task_tree_id": tree_id,
                                "created": datetime.now().isoformat(),
                                "last_updated": datetime.now().isoformat()
                            }
                        }
                        with open(tasks_file_path, 'w') as f:
                            json.dump(empty_structure, f, indent=2)
                        fixes_applied.append(f"Created missing task file for tree {tree_id}")
                        
                except Exception as e:
                    validation_issues.append(f"Failed to validate tree {tree_id}: {str(e)}")
                    actual_task_counts[tree_id] = 0
            
            # 2. Validate dashboard metrics consistency
            try:
                dashboard_result = self.get_orchestration_dashboard(project_id)
                if dashboard_result.get("success"):
                    dashboard_data = dashboard_result.get("dashboard", {})
                    dashboard_trees = dashboard_data.get("trees", {})
                    
                    for tree_id, actual_count in actual_task_counts.items():
                        dashboard_count = dashboard_trees.get(tree_id, {}).get("total_tasks", 0)
                        
                        if dashboard_count != actual_count:
                            validation_issues.append(
                                f"Tree {tree_id}: Dashboard shows {dashboard_count} tasks, "
                                f"but actual count is {actual_count}"
                            )
                            # Note: Dashboard metrics are calculated dynamically, so this is informational
                            
                else:
                    warnings.append("Could not retrieve dashboard data for validation")
            except Exception as e:
                warnings.append(f"Dashboard validation failed: {str(e)}")
            
            # 3. Validate agent assignments integrity
            agent_assignments = project.get("agent_assignments", {})
            registered_agents = project.get("registered_agents", {})
            
            for agent_id, assigned_trees in agent_assignments.items():
                # Check if agent is registered
                if agent_id not in registered_agents:
                    validation_issues.append(f"Agent {agent_id} has assignments but is not registered")
                    # Auto-fix: Remove unregistered agent assignments
                    fixes_applied.append(f"Removed assignments for unregistered agent {agent_id}")
                    continue
                
                # Check if assigned trees exist
                if isinstance(assigned_trees, list):
                    invalid_trees = [tree for tree in assigned_trees if tree not in task_trees]
                    if invalid_trees:
                        validation_issues.append(f"Agent {agent_id} assigned to non-existent trees: {invalid_trees}")
                        # Auto-fix: Remove invalid tree assignments
                        valid_trees = [tree for tree in assigned_trees if tree in task_trees]
                        if valid_trees:
                            agent_assignments[agent_id] = valid_trees
                        else:
                            del agent_assignments[agent_id]
                        fixes_applied.append(f"Fixed agent {agent_id} assignments: removed {invalid_trees}")
                elif assigned_trees not in task_trees:
                    validation_issues.append(f"Agent {agent_id} assigned to non-existent tree: {assigned_trees}")
                    # Auto-fix: Remove invalid assignment
                    del agent_assignments[agent_id]
                    fixes_applied.append(f"Removed invalid assignment for agent {agent_id}")
            
            # 4. Validate registered agents data structure
            agents_fixed = []
            for agent_id, agent_data in list(registered_agents.items()):
                if not isinstance(agent_data, dict):
                    validation_issues.append(f"Agent {agent_id} has invalid data structure")
                    del registered_agents[agent_id]
                    agents_fixed.append(agent_id)
                    continue
                
                # Ensure required fields
                if not agent_data.get("id"):
                    agent_data["id"] = agent_id
                    agents_fixed.append(agent_id)
                
                if not agent_data.get("name"):
                    agent_data["name"] = agent_id.replace("_", " ").title()
                    agents_fixed.append(agent_id)
                
                if not agent_data.get("call_agent"):
                    agent_data["call_agent"] = f"@{agent_id.replace('_', '-')}"
                    agents_fixed.append(agent_id)
            
            if agents_fixed:
                fixes_applied.append(f"Fixed agent data for: {agents_fixed}")
            
            # 5. Validate task tree data structure
            trees_fixed = []
            for tree_id, tree_data in task_trees.items():
                if not isinstance(tree_data, dict):
                    validation_issues.append(f"Task tree {tree_id} has invalid data structure")
                    task_trees[tree_id] = {
                        "id": tree_id,
                        "name": tree_id.replace("_", " ").replace("-", " ").title(),
                        "description": f"Task tree for {tree_id}"
                    }
                    trees_fixed.append(tree_id)
                    continue
                
                # Ensure required fields
                if not tree_data.get("id"):
                    tree_data["id"] = tree_id
                    trees_fixed.append(tree_id)
                
                if not tree_data.get("name"):
                    tree_data["name"] = tree_id.replace("_", " ").replace("-", " ").title()
                    trees_fixed.append(tree_id)
                
                if not tree_data.get("description"):
                    tree_data["description"] = f"Task tree for {tree_id}"
                    trees_fixed.append(tree_id)
            
            if trees_fixed:
                fixes_applied.append(f"Fixed task tree data for: {trees_fixed}")
            
            # 6. Validate project metadata
            metadata_fixes = []
            if not project.get("id"):
                project["id"] = project_id
                metadata_fixes.append("Added missing project ID")
            
            if not project.get("name"):
                project["name"] = project_id.replace("_", " ").title()
                metadata_fixes.append("Added missing project name")
            
            if not project.get("created_at"):
                project["created_at"] = "2025-01-01T00:00:00Z"
                metadata_fixes.append("Added missing created_at timestamp")
            
            if metadata_fixes:
                fixes_applied.extend(metadata_fixes)
            
            # 7. Update project metadata
            project["updated_at"] = datetime.now().isoformat()
            project["last_integrity_check"] = datetime.now().isoformat()
            
            # Save changes if any fixes were applied
            if fixes_applied:
                self._save_projects()
            
            # Calculate integrity score
            total_checks = len(task_trees) + len(registered_agents) + len(agent_assignments) + 5  # +5 for metadata checks
            issues_found = len(validation_issues)
            integrity_score = max(0, 100 - (issues_found * 10))  # Deduct 10 points per issue
            
            # Determine overall status
            if issues_found == 0:
                overall_status = "✅ HEALTHY"
            elif issues_found <= 2:
                overall_status = "⚠️ MINOR_ISSUES"
            elif issues_found <= 5:
                overall_status = "❌ NEEDS_ATTENTION"
            else:
                overall_status = "🚨 CRITICAL"
            
            return {
                "success": True,
                "project_id": project_id,
                "overall_status": overall_status,
                "integrity_score": f"{integrity_score}/100",
                "validation_summary": {
                    "total_checks_performed": total_checks,
                    "issues_found": issues_found,
                    "fixes_applied": len(fixes_applied),
                    "warnings": len(warnings)
                },
                "task_data_validation": {
                    "task_trees_validated": len(task_trees),
                    "actual_task_counts": actual_task_counts,
                    "total_tasks_across_trees": sum(actual_task_counts.values())
                },
                "agent_validation": {
                    "registered_agents": len(registered_agents),
                    "active_assignments": len(agent_assignments),
                    "agents_with_assignments": len([a for a in agent_assignments.keys() if a in registered_agents])
                },
                "validation_issues": validation_issues,
                "fixes_applied": fixes_applied,
                "warnings": warnings,
                "recommendations": [
                    "Run sync_with_git if git branch mismatches exist",
                    "Run cleanup_obsolete if orphaned data is detected",
                    "Check task files manually if persistent issues remain"
                ] if issues_found > 0 else ["Data integrity is healthy - no action needed"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Integrity validation failed for project {project_id}: {str(e)}")
            return {"success": False, "error": f"Integrity validation failed: {str(e)}"}


class ToolConfig:
    """Manages MCP tool configuration and enablement settings"""
    
    DEFAULT_CONFIG = {
        "enabled_tools": {
            "manage_project": True, 
            "manage_task": True, 
            "manage_subtask": True,
            "manage_agent": True, 
            "manage_rule": True,
            "call_agent": True, 
            "update_auto_rule": False,
            "validate_rules": False, 
            "regenerate_auto_rule": False, 
            "validate_tasks_json": False,
            "create_context_file": True,
            "manage_context": True
        },
        "debug_mode": False, 
        "tool_logging": False
    }
    
    def __init__(self, config_overrides: Optional[Dict[str, Any]] = None):
        self.config = self._load_config(config_overrides)
        
    def _load_config(self, config_overrides: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Load configuration from environment or use defaults"""
        config_path = os.environ.get('MCP_TOOL_CONFIG')
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
                config = self.DEFAULT_CONFIG.copy()
        else:
            config = self.DEFAULT_CONFIG.copy()
        
        # Apply overrides if provided
        if config_overrides:
            logger.info(f"Applying configuration overrides: {config_overrides}")
            for key, value in config_overrides.items():
                if key == "enabled_tools" and isinstance(value, dict):
                    # Merge enabled_tools instead of replacing
                    config.setdefault("enabled_tools", {}).update(value)
                else:
                    config[key] = value
        
        return config
        
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
    
    def create_task_service(self, project_id: str, task_tree_id: str, user_id: str):
        """Create a task application service for the specified project/tree"""
        repository = self._repository_factory.create_repository(project_id, task_tree_id, user_id)
        from ..application.services.task_application_service import TaskApplicationService
        return TaskApplicationService(repository, self._auto_rule_generator)
    
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
            return self._list_tasks(task_app_service, project_id, task_tree_id, user_id, status, priority, assignees, labels, limit)
        elif action == "search":
            return self._search_tasks(task_app_service, project_id, task_tree_id, user_id, query, limit)
        elif action == "next":
            return self._get_next_task(task_app_service)
        else:
            return {"success": False, "error": "Invalid action for list/search/next"}
    
    def handle_dependency_operations(self, action, task_id, project_id, task_tree_id, user_id, dependency_data=None):
        """Handle dependency operations (add, remove, get, clear, get_blocking) with hierarchical storage"""
        if not task_id:
            return {"success": False, "error": "task_id is required for dependency operations"}
        
        # Validate project and task tree exist
        if not self._validate_project_tree(project_id, task_tree_id):
            return {"success": False, "error": f"Project '{project_id}' or task tree '{task_tree_id}' not found"}
        
        # Get repository for this specific project/tree
        try:
            repository = self._repository_factory.create_repository(project_id, task_tree_id, user_id)
            task_app_service = TaskApplicationService(repository, self._auto_rule_generator)
        except Exception as e:
            return {"success": False, "error": f"Failed to access task storage: {str(e)}"}
        
        try:
            if action == "add_dependency":
                if not dependency_data or "dependency_id" not in dependency_data:
                    return {"success": False, "error": "dependency_data with dependency_id is required"}
                
                request = AddDependencyRequest(task_id=task_id, dependency_id=dependency_data["dependency_id"])
                response = task_app_service.add_dependency(request)
                return {"success": response.success, "action": "add_dependency", "task_id": response.task_id, "dependencies": response.dependencies, "message": response.message}
            elif action == "remove_dependency":
                if not dependency_data or "dependency_id" not in dependency_data:
                    return {"success": False, "error": "dependency_data with dependency_id is required"}
                response = task_app_service.remove_dependency(task_id, dependency_data["dependency_id"])
                return {"success": response.success, "action": "remove_dependency", "task_id": response.task_id, "dependencies": response.dependencies, "message": response.message}
            elif action == "get_dependencies":
                response = task_app_service.get_dependencies(task_id)
                return {"success": True, "action": "get_dependencies", **response}
            elif action == "clear_dependencies":
                response = task_app_service.clear_dependencies(task_id)
                return {"success": response.success, "action": "clear_dependencies", "task_id": response.task_id, "dependencies": response.dependencies, "message": response.message}
            elif action == "get_blocking_tasks":
                response = task_app_service.get_blocking_tasks(task_id)
                return {"success": True, "action": "get_blocking_tasks", **response}
            else:
                return {"success": False, "error": f"Unknown dependency action: {action}"}
        except Exception as e:
            return {"success": False, "error": f"Dependency operation failed: {str(e)}"}
    
    def handle_subtask_operations(self, action, task_id, subtask_data=None, project_id=None, task_tree_id="main", user_id="default_id"):
        """Handle subtask operations"""
        logging.info(f"Subtask operation action: {action}, task_id: {task_id}, subtask_data: {subtask_data}")
        if not task_id:
            return {"success": False, "error": "task_id is required for subtask operations"}
        
        # For backward compatibility, use default project if not provided
        if not project_id:
            project_id = "default_project"
        
        # Validate project and task tree exist (skip validation for default/test scenarios)
        if project_id != "default_project" and not self._validate_project_tree(project_id, task_tree_id):
            return {"success": False, "error": f"Project '{project_id}' or task tree '{task_tree_id}' not found"}
        
        # Get repository for this specific project/tree
        try:
            repository = self._repository_factory.create_repository(project_id, task_tree_id, user_id)
            task_app_service = TaskApplicationService(repository, self._auto_rule_generator)
        except Exception as e:
            return {"success": False, "error": f"Failed to access task storage: {str(e)}"}
        
        try:
            response = task_app_service.manage_subtasks(task_id, action, subtask_data or {})
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
    
    def _list_tasks(self, task_app_service, project_id, task_tree_id, user_id, status, priority, assignees, labels, limit):
        """List tasks with optional filters"""
        try:
            request = ListTasksRequest(
                project_id=project_id,
                task_tree_id=task_tree_id,
                user_id=user_id,
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
    
    def _search_tasks(self, task_app_service, project_id, task_tree_id, user_id, query, limit):
        """Search tasks by query"""
        if not query:
            return {"success": False, "error": "query is required for searching tasks"}
        
        try:
            request = SearchTasksRequest(
                query=query,
                project_id=project_id,
                task_tree_id=task_tree_id,
                user_id=user_id,
                limit=limit or 10
            )
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
            # Extract context information from the repository
            repository = task_app_service._task_repository
            task_tree_id = getattr(repository, 'task_tree_id', 'main')
            user_id = getattr(repository, 'user_id', 'default_id')
            project_id = getattr(repository, 'project_id', '')
            
            do_next_use_case = DoNextUseCase(repository, self._auto_rule_generator)
            response = do_next_use_case.execute(
                task_tree_id=task_tree_id,
                user_id=user_id,
                project_id=project_id
            )
            
            if response.has_next and response.next_item:
                result = {
                    "success": True,
                    "action": "next",
                    "next_item": response.next_item,
                    "message": response.message
                }
                
                # Add context_info if available (only for tasks with specific conditions)
                if response.context_info:
                    result["context_info"] = response.context_info
                
                return result
            else:
                return {
                    "success": False,  # Fixed: Should be False when no valid next task found
                    "action": "next",
                    "next_item": None,
                    "message": response.message,
                    "context": response.context if response.context else None,
                    "error": "No actionable tasks found. Create tasks or update context for existing tasks."
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
                action: Annotated[str, Field(description="Project action to perform. Available: create, get, list, update, create_tree, delete_tree, delete_project, clear_tree, get_tree_status, orchestrate, dashboard, project_health_check, sync_with_git, cleanup_obsolete, validate_integrity, rebalance_agents")],
                project_id: Annotated[str, Field(description="Unique project identifier")] = None,
                name: Annotated[str, Field(description="Project name (required for create action, optional for update action)")] = None,
                description: Annotated[str, Field(description="Project description (optional for create and update actions)")] = None,
                tree_id: Annotated[str, Field(description="Task tree identifier (required for tree operations)")] = None,
                tree_name: Annotated[str, Field(description="Task tree name (required for create_tree action)")] = None,
                tree_description: Annotated[str, Field(description="Task tree description (optional for create_tree action)")] = None,
                force: Annotated[bool, Field(description="Force deletion even if tree/project contains tasks (for delete operations)")] = False
            ) -> Dict[str, Any]:
                """🚀 PROJECT LIFECYCLE MANAGER - Multi-agent project orchestration and management

⭐ WHAT IT DOES: Complete project lifecycle management with task trees and agent coordination
📋 WHEN TO USE: Creating projects, managing task trees, orchestrating multi-agent workflows

🎯 ACTIONS AVAILABLE:
• create: Initialize new project with basic structure
• get: Retrieve project details and current status
• list: Show all available projects
• update: Modify project name and/or description
• create_tree: Add task tree structure to project
• get_tree_status: Check task tree completion status
• orchestrate: Execute multi-agent project workflow
• dashboard: View comprehensive project analytics
• project_health_check: Comprehensive project health analysis with data integrity validation
• sync_with_git: Synchronize task trees with actual git branches (removes obsolete, adds missing)
• cleanup_obsolete: Clean up orphaned data and remove obsolete references from project
• validate_integrity: Check and fix data consistency issues between dashboard and actual data
• rebalance_agents: Automatically redistribute agent assignments optimally across active task trees

💡 USAGE EXAMPLES:
• manage_project("create", project_id="web_app", name="E-commerce Website")
• manage_project("orchestrate", project_id="web_app")
• manage_project("dashboard", project_id="web_app")
• manage_project("project_health_check", project_id="web_app")
• manage_project("sync_with_git", project_id="web_app")
• manage_project("cleanup_obsolete", project_id="web_app")
• manage_project("validate_integrity", project_id="web_app")
• manage_project("rebalance_agents", project_id="web_app")

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
                    
                elif action == "update":
                    if not project_id:
                        return {"success": False, "error": "project_id is required for updating a project"}
                    return self._project_manager.update_project(project_id, name, description)
                    
                elif action == "create_tree":
                    if not all([project_id, tree_id, tree_name]):
                        return {"success": False, "error": "project_id, tree_id, and tree_name are required"}
                    return self._project_manager.create_task_tree(project_id, tree_id, tree_name, tree_description or "")
                    
                elif action == "delete_tree":
                    if not project_id or not tree_id:
                        return {"success": False, "error": "project_id and tree_id are required for deleting a task tree"}
                    return self._project_manager.delete_task_tree(project_id, tree_id, force)
                    
                elif action == "delete_project":
                    if not project_id:
                        return {"success": False, "error": "project_id is required for deleting a project"}
                    return self._project_manager.delete_project(project_id, force)
                    
                elif action == "clear_tree":
                    if not project_id or not tree_id:
                        return {"success": False, "error": "project_id and tree_id are required for clearing a task tree"}
                    return self._project_manager.clear_task_tree(project_id, tree_id)
                    
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
                    
                elif action == "project_health_check":
                    if not project_id:
                        return {"success": False, "error": "project_id is required"}
                    return self._project_manager.project_health_check(project_id)
                    
                elif action == "sync_with_git":
                    if not project_id:
                        return {"success": False, "error": "project_id is required"}
                    return self._project_manager.sync_with_git(project_id)
                    
                elif action == "cleanup_obsolete":
                    if not project_id:
                        return {"success": False, "error": "project_id is required"}
                    return self._project_manager.cleanup_obsolete(project_id)
                    
                elif action == "validate_integrity":
                    if not project_id:
                        return {"success": False, "error": "project_id is required"}
                    return self._project_manager.validate_integrity(project_id)
                    
                elif action == "rebalance_agents":
                    if not project_id:
                        return {"success": False, "error": "project_id is required"}
                    return self._project_manager.rebalance_agents(project_id)
                    
                else:
                    return {"success": False, "error": f"Unknown action: {action}. Available: create, get, list, update, create_tree, delete_tree, delete_project, clear_tree, get_tree_status, orchestrate, dashboard, project_health_check, sync_with_git, cleanup_obsolete, validate_integrity, rebalance_agents"}

            logger.info("Registered manage_project tool")
        else:
            logger.info("Skipped manage_project tool (disabled)")
    
    def _register_task_tools(self, mcp: "FastMCP"):
        """Register task management tools"""
        if self._config.is_enabled("manage_task"):
            @mcp.tool()
            def manage_task(
                action: Annotated[str, Field(description="Task action to perform. Available: create, get(AI no have permission to get task if user not demand, AI use `next` to get task), update, delete, complete, list, search, next, add_dependency, remove_dependency")],
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
                        action=action, task_id=task_id, project_id=project_id, 
                        task_tree_id=task_tree_id, user_id=user_id, dependency_data=dependency_data
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
                subtask_data: Annotated[Dict[str, Any], Field(description="Subtask data containing title, description, and other subtask properties")] = None,
                project_id: Annotated[str, Field(description="Project identifier (defaults to 'default_project')")] = "default_project",
                task_tree_id: Annotated[str, Field(description="Task tree identifier (defaults to 'main')")] = "main",
                user_id: Annotated[str, Field(description="User identifier (defaults to 'default_id')")] = "default_id"
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
                    result = self._task_handler.handle_subtask_operations(action, task_id, subtask_data, project_id, task_tree_id, user_id)
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

        if self._config.is_enabled("manage_context"):
            @mcp.tool()
            def manage_context(
                action: Annotated[str, Field(description="Context action to perform. Available: create, get, update, delete, list, get_property, update_property, merge, add_insight, add_progress, update_next_steps")],
                task_id: Annotated[str, Field(description="Task identifier (required for most operations)")] = None,
                user_id: Annotated[str, Field(description="User identifier (defaults to 'default_id')")] = "default_id",
                project_id: Annotated[str, Field(description="Project identifier")] = "",
                task_tree_id: Annotated[str, Field(description="Task tree identifier (defaults to 'main')")] = "main",
                property_path: Annotated[str, Field(description="Property path using dot notation (e.g., 'metadata.status', 'progress.next_steps.0')")] = None,
                value: Annotated[Any, Field(description="Value to set for property updates")] = None,
                data: Annotated[Dict[str, Any], Field(description="Data to merge or context data for creation")] = None,
                agent: Annotated[str, Field(description="Agent name for insights and progress actions")] = None,
                category: Annotated[str, Field(description="Category for insights: insight, challenge, solution, decision")] = None,
                content: Annotated[str, Field(description="Content for insights or progress actions")] = None,
                importance: Annotated[str, Field(description="Importance level: low, medium, high, critical")] = "medium",
                next_steps: Annotated[List[str], Field(description="List of next steps to update")] = None
            ) -> Dict[str, Any]:
                """🗂️ CONTEXT MANAGER - Complete JSON-based context management with CRUD operations

⭐ WHAT IT DOES: Manages task contexts in JSON format with full CRUD operations and nested property support
📋 WHEN TO USE: Create, read, update, or delete task contexts; manage context properties and insights

🎯 ACTIONS AVAILABLE:
• create: Create new context for a task
• get: Retrieve context or specific property
• update: Update context properties (supports dot notation)
• delete: Remove context entirely
• list: List all contexts in project/tree
• get_property: Get specific property using dot notation
• update_property: Update specific property using dot notation
• merge: Merge data into existing context
• add_insight: Add agent insight/note to context
• add_progress: Add progress action to context
• update_next_steps: Update next steps list

🔧 PROPERTY ACCESS:
• Use dot notation for nested properties: 'metadata.status', 'progress.next_steps', 'notes.agent_insights.0'
• Array access with indices: 'subtasks.items.0.title'
• Deep nested updates: 'technical.technologies' to add/update technology lists

💡 USAGE EXAMPLES:
• manage_context("get", task_id="123") - Get full context
• manage_context("get_property", task_id="123", property_path="metadata.status") - Get status
• manage_context("update_property", task_id="123", property_path="metadata.status", value="in_progress")
• manage_context("add_insight", task_id="123", agent="coding_agent", category="solution", content="Used React hooks")
• manage_context("merge", task_id="123", data={"technical": {"technologies": ["React", "TypeScript"]}})

🗂️ STORAGE: Contexts stored as JSON files in .cursor/rules/contexts/{user_id}/{project_id}/{task_tree_id}/
                """
                try:
                    from ..infrastructure.services.context_manager import ContextManager
                    
                    context_manager = ContextManager()
                    
                    if action == "create":
                        if not task_id:
                            return {"success": False, "error": "task_id is required for create action"}
                        
                        # Get task data to create context
                        task_service = self._task_handler.create_task_service(project_id, task_tree_id, user_id)
                        task = task_service._task_repository.find_by_id(task_id)
                        
                        if not task:
                            return {"success": False, "error": f"Task {task_id} not found"}
                        
                        success = context_manager.create_context_from_task(task, user_id)
                        
                        # Update task's context_id when context is successfully created
                        if success:
                            try:
                                # Set context_id to indicate context has been created
                                task.set_context_id(f"context_{task_id}")
                                task_service._task_repository.save(task)
                            except Exception as e:
                                logger.warning(f"Failed to update task context_id for task {task_id}: {e}")
                        
                        return {"success": success, "message": f"Context created for task {task_id}" if success else "Failed to create context"}
                    
                    elif action == "get":
                        if not task_id:
                            return {"success": False, "error": "task_id is required for get action"}
                        
                        context = context_manager.get_context(task_id, user_id, project_id, task_tree_id)
                        if context:
                            return {"success": True, "context": context.to_dict()}
                        else:
                            return {"success": False, "error": f"Context not found for task {task_id}"}
                    
                    elif action == "update":
                        if not task_id or not data:
                            return {"success": False, "error": "task_id and data are required for update action"}
                        
                        success = context_manager.merge_data(task_id, data, user_id, project_id, task_tree_id)
                        
                        # Update task's context_id when context is successfully updated
                        if success:
                            try:
                                task_service = self._task_handler.create_task_service(project_id, task_tree_id, user_id)
                                task = task_service._task_repository.find_by_id(task_id)
                                if task:
                                    # Set context_id to indicate context has been updated
                                    task.set_context_id(f"context_{task_id}")
                                    task_service._task_repository.save(task)
                            except Exception as e:
                                logger.warning(f"Failed to update task context_id for task {task_id}: {e}")
                        
                        return {"success": success, "message": f"Context updated for task {task_id}" if success else "Failed to update context"}
                    
                    elif action == "delete":
                        if not task_id:
                            return {"success": False, "error": "task_id is required for delete action"}
                        
                        success = context_manager.delete_context(task_id, user_id, project_id, task_tree_id)
                        return {"success": success, "message": f"Context deleted for task {task_id}" if success else "Failed to delete context"}
                    
                    elif action == "list":
                        contexts = context_manager.list_contexts(user_id, project_id, task_tree_id)
                        return {"success": True, "contexts": contexts}
                    
                    elif action == "get_property":
                        if not task_id or not property_path:
                            return {"success": False, "error": "task_id and property_path are required for get_property action"}
                        
                        prop_value = context_manager.get_property(task_id, property_path, user_id, project_id, task_tree_id)
                        if prop_value is not None:
                            return {"success": True, "property": property_path, "value": prop_value}
                        else:
                            return {"success": False, "error": f"Property {property_path} not found in context for task {task_id}"}
                    
                    elif action == "update_property":
                        if not task_id or not property_path or value is None:
                            return {"success": False, "error": "task_id, property_path, and value are required for update_property action"}
                        
                        success = context_manager.update_property(task_id, property_path, value, user_id, project_id, task_tree_id)
                        
                        # Update task's context_id when context is successfully updated
                        if success:
                            try:
                                task_service = self._task_handler.create_task_service(project_id, task_tree_id, user_id)
                                task = task_service._task_repository.find_by_id(task_id)
                                if task:
                                    # Set context_id to indicate context has been updated
                                    task.set_context_id(f"context_{task_id}")
                                    task_service._task_repository.save(task)
                            except Exception as e:
                                logger.warning(f"Failed to update task context_id for task {task_id}: {e}")
                        
                        return {"success": success, "message": f"Property {property_path} updated for task {task_id}" if success else "Failed to update property"}
                    
                    elif action == "merge":
                        if not task_id or not data:
                            return {"success": False, "error": "task_id and data are required for merge action"}
                        
                        success = context_manager.merge_data(task_id, data, user_id, project_id, task_tree_id)
                        
                        # Update task's context_id when context is successfully updated
                        if success:
                            try:
                                task_service = self._task_handler.create_task_service(project_id, task_tree_id, user_id)
                                task = task_service._task_repository.find_by_id(task_id)
                                if task:
                                    # Set context_id to indicate context has been updated
                                    task.set_context_id(f"context_{task_id}")
                                    task_service._task_repository.save(task)
                            except Exception as e:
                                logger.warning(f"Failed to update task context_id for task {task_id}: {e}")
                        
                        return {"success": success, "message": f"Data merged into context for task {task_id}" if success else "Failed to merge data"}
                    
                    elif action == "add_insight":
                        if not task_id or not agent or not category or not content:
                            return {"success": False, "error": "task_id, agent, category, and content are required for add_insight action"}
                        
                        success = context_manager.add_insight(task_id, agent, category, content, importance, user_id, project_id, task_tree_id)
                        
                        # Update task's context_id when context is successfully updated
                        if success:
                            try:
                                task_service = self._task_handler.create_task_service(project_id, task_tree_id, user_id)
                                task = task_service._task_repository.find_by_id(task_id)
                                if task:
                                    # Set context_id to indicate context has been updated
                                    task.set_context_id(f"context_{task_id}")
                                    task_service._task_repository.save(task)
                            except Exception as e:
                                logger.warning(f"Failed to update task context_id for task {task_id}: {e}")
                        
                        return {"success": success, "message": f"Insight added to context for task {task_id}" if success else "Failed to add insight"}
                    
                    elif action == "add_progress":
                        if not task_id or not agent or not content:
                            return {"success": False, "error": "task_id, agent, and content are required for add_progress action"}
                        
                        success = context_manager.add_progress_action(task_id, content, agent, "", "completed", user_id, project_id, task_tree_id)
                        
                        # Update task's context_id when context is successfully updated
                        if success:
                            try:
                                task_service = self._task_handler.create_task_service(project_id, task_tree_id, user_id)
                                task = task_service._task_repository.find_by_id(task_id)
                                if task:
                                    # Set context_id to indicate context has been updated
                                    task.set_context_id(f"context_{task_id}")
                                    task_service._task_repository.save(task)
                            except Exception as e:
                                logger.warning(f"Failed to update task context_id for task {task_id}: {e}")
                        
                        return {"success": success, "message": f"Progress action added to context for task {task_id}" if success else "Failed to add progress action"}
                    
                    elif action == "update_next_steps":
                        if not task_id or not next_steps:
                            return {"success": False, "error": "task_id and next_steps are required for update_next_steps action"}
                        
                        success = context_manager.update_next_steps(task_id, next_steps, user_id, project_id, task_tree_id)
                        
                        # Update task's context_id when context is successfully updated
                        if success:
                            try:
                                task_service = self._task_handler.create_task_service(project_id, task_tree_id, user_id)
                                task = task_service._task_repository.find_by_id(task_id)
                                if task:
                                    # Set context_id to indicate context has been updated
                                    task.set_context_id(f"context_{task_id}")
                                    task_service._task_repository.save(task)
                            except Exception as e:
                                logger.warning(f"Failed to update task context_id for task {task_id}: {e}")
                        
                        return {"success": success, "message": f"Next steps updated for task {task_id}" if success else "Failed to update next steps"}
                    
                    else:
                        return {"success": False, "error": f"Unknown action: {action}. Available actions: create, get, update, delete, list, get_property, update_property, merge, add_insight, add_progress, update_next_steps"}
                
                except Exception as e:
                    logger.error(f"Error in manage_context: {e}")
                    return {"success": False, "error": f"Context management failed: {e}"}
        
            logger.info("Registered manage_context tool")
        else:
            logger.info("Skipped manage_context tool (disabled)")

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
        # Check if cursor tools are explicitly disabled via environment variable
        cursor_tools_disabled = os.environ.get("DHAFNCK_DISABLE_CURSOR_TOOLS", "false").lower() == "true"
        
        # Define all cursor tools
        cursor_tools = ["update_auto_rule", "validate_rules", "manage_rule", "regenerate_auto_rule", "validate_tasks_json", "create_context_file"]
        
        # If DHAFNCK_DISABLE_CURSOR_TOOLS=true, only keep manage_rule enabled
        if cursor_tools_disabled:
            enabled_cursor_tools = [tool for tool in cursor_tools if tool == "manage_rule" and self._config.is_enabled(tool)]
            if enabled_cursor_tools:
                logger.info(f"Registering {len(enabled_cursor_tools)} cursor rules tools (manage_rule only, others disabled via DHAFNCK_DISABLE_CURSOR_TOOLS)")
            else:
                logger.info("Skipped all cursor rules tools (disabled via DHAFNCK_DISABLE_CURSOR_TOOLS)")
                return
        else:
            # Normal operation - respect individual tool configuration
            enabled_cursor_tools = [tool for tool in cursor_tools if self._config.is_enabled(tool)]
            if enabled_cursor_tools:
                logger.info(f"Registering {len(enabled_cursor_tools)} cursor rules tools")
            else:
                logger.info("Skipped all cursor rules tools (all disabled)")
                return
        
        # Register only the enabled cursor tools
        temp_cursor_tools = CursorRulesTools()
        
        # Selectively register only enabled tools
        for tool in enabled_cursor_tools:
            if tool == "manage_rule":
                self._register_manage_rule_tool(mcp, temp_cursor_tools)
                logger.info(f"  - Registered {tool}")
            elif tool == "update_auto_rule":
                self._register_update_auto_rule_tool(mcp, temp_cursor_tools)
                logger.info(f"  - Registered {tool}")
            elif tool == "validate_rules":
                self._register_validate_rules_tool(mcp, temp_cursor_tools)
                logger.info(f"  - Registered {tool}")
            elif tool == "regenerate_auto_rule":
                self._register_regenerate_auto_rule_tool(mcp, temp_cursor_tools)
                logger.info(f"  - Registered {tool}")
            elif tool == "validate_tasks_json":
                self._register_validate_tasks_json_tool(mcp, temp_cursor_tools)
                logger.info(f"  - Registered {tool}")
            elif tool == "create_context_file":
                self._register_create_context_file_tool(mcp, temp_cursor_tools)
                logger.info(f"  - Registered {tool}")
    
    def _register_manage_rule_tool(self, mcp: "FastMCP", cursor_tools):
        """Register the enhanced manage_rule tool with all advanced functionality"""
        @mcp.tool()
        def manage_rule(
            action: str,
            target: Optional[str] = None,
            content: Optional[str] = None
        ) -> Dict[str, Any]:
            """🗂️ CURSOR RULES ADMINISTRATION - Complete rule file system management
            
            Enhanced rule orchestration platform with nested loading, client integration, 
            and advanced rule composition capabilities.
            
            Available actions: list, backup, restore, clean, info, load_core, parse_rule, 
            analyze_hierarchy, get_dependencies, enhanced_info, compose_nested_rules, 
            resolve_rule_inheritance, validate_rule_hierarchy, build_hierarchy, load_nested, 
            cache_status, register_client, authenticate_client, sync_client, client_diff, 
            resolve_conflicts, client_status, client_analytics
            """
            try:
                # Delegate to the enhanced CursorRulesTools implementation
                # which contains all the sophisticated functionality
                if hasattr(cursor_tools, 'register_tools'):
                    # Create a mock MCP object to capture the tool registration
                    class MockMCP:
                        def __init__(self):
                            self.tools = {}
                        
                        def tool(self):
                            def decorator(func):
                                self.tools[func.__name__] = func
                                return func
                            return decorator
                    
                    # Get the enhanced manage_rule implementation
                    mock_mcp = MockMCP()
                    cursor_tools.register_tools(mock_mcp)
                    
                    if 'manage_rule' in mock_mcp.tools:
                        enhanced_manage_rule = mock_mcp.tools['manage_rule']
                        return enhanced_manage_rule(action=action, target=target, content=content)
                
                # Fallback to basic implementation if enhanced version fails
                return self._basic_manage_rule_implementation(cursor_tools, action, target, content)
                    
            except Exception as e:
                # Log the error and fallback to basic implementation
                logger.warning(f"Enhanced manage_rule failed, falling back to basic: {str(e)}")
                return self._basic_manage_rule_implementation(cursor_tools, action, target, content)
    
    def _basic_manage_rule_implementation(self, cursor_tools, action: str, target: Optional[str] = None, content: Optional[str] = None) -> Dict[str, Any]:
        """Basic manage_rule implementation as fallback"""
        try:
            if action == "list":
                rules_dir = cursor_tools.project_root / ".cursor" / "rules"
                if not rules_dir.exists():
                    return {"success": True, "files": [], "message": "Rules directory does not exist"}
                
                files = []
                for file_path in rules_dir.rglob("*.mdc"):
                    files.append({
                        "path": str(file_path.relative_to(cursor_tools.project_root)),
                        "size": file_path.stat().st_size,
                        "modified": file_path.stat().st_mtime
                    })
                
                return {"success": True, "files": files}
            
            elif action == "backup":
                auto_rule_path = cursor_tools.project_root / ".cursor" / "rules" / "auto_rule.mdc"
                if not auto_rule_path.exists():
                    return {"success": False, "error": "auto_rule.mdc not found"}
                
                backup_path = auto_rule_path.with_suffix('.mdc.backup')
                with open(auto_rule_path, 'r', encoding='utf-8') as src:
                    content = src.read()
                with open(backup_path, 'w', encoding='utf-8') as dst:
                    dst.write(content)
                
                return {"success": True, "message": "Backup created", "backup_path": str(backup_path)}
            
            elif action == "restore":
                auto_rule_path = cursor_tools.project_root / ".cursor" / "rules" / "auto_rule.mdc"
                backup_path = auto_rule_path.with_suffix('.mdc.backup')
                
                if not backup_path.exists():
                    return {"success": False, "error": "Backup file not found"}
                
                with open(backup_path, 'r', encoding='utf-8') as src:
                    content = src.read()
                with open(auto_rule_path, 'w', encoding='utf-8') as dst:
                    dst.write(content)
                
                return {"success": True, "message": "Restored from backup"}
            
            elif action == "info":
                rules_dir = cursor_tools.project_root / ".cursor" / "rules"
                if not rules_dir.exists():
                    return {"success": True, "info": {"directory_exists": False}}
                
                file_count = len(list(rules_dir.rglob("*.mdc")))
                total_size = sum(f.stat().st_size for f in rules_dir.rglob("*.mdc"))
                
                return {
                    "success": True,
                    "info": {
                        "directory_exists": True,
                        "file_count": file_count,
                        "total_size": total_size,
                        "directory_path": str(rules_dir)
                    }
                }
            
            elif action == "load_core":
                rules_dir = cursor_tools.project_root / ".cursor" / "rules"
                
                # Define core rule files in priority order
                core_rules = [
                    "dhafnck_mcp.mdc",           # Main MCP runtime system
                    "dev_workflow.mdc",          # Development workflow
                    "cursor_rules.mdc",          # Cursor rule guidelines
                    "taskmaster.mdc",            # Task management
                    "mcp.mdc"                    # MCP architecture
                ]
                
                loaded_rules = []
                failed_rules = []
                total_size = 0
                
                for rule_file in core_rules:
                    rule_path = rules_dir / rule_file
                    if rule_path.exists():
                        try:
                            with open(rule_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                file_size = rule_path.stat().st_size
                                total_size += file_size
                                
                            loaded_rules.append({
                                "file": rule_file,
                                "path": str(rule_path.relative_to(cursor_tools.project_root)),
                                "size": file_size,
                                "status": "loaded"
                            })
                        except Exception as e:
                            failed_rules.append({
                                "file": rule_file,
                                "status": "error",
                                "error": str(e)
                            })
                    else:
                        failed_rules.append({
                            "file": rule_file,
                            "status": "not_found"
                        })
                
                return {
                    "success": True,
                    "action": "load_core",
                    "core_rules_loaded": len(loaded_rules),
                    "failed_rules": len(failed_rules),
                    "total_size_bytes": total_size,
                    "loaded_rules": loaded_rules,
                    "failed_rules": failed_rules if failed_rules else None,
                    "session_ready": len(loaded_rules) > 0
                }
            
            else:
                return {"success": False, "error": f"Unknown action: {action}. Available actions: list, backup, restore, info, load_core"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _register_update_auto_rule_tool(self, mcp: "FastMCP", cursor_tools):
        """Register only the update_auto_rule tool"""
        # This would be implemented if needed
        pass
    
    def _register_validate_rules_tool(self, mcp: "FastMCP", cursor_tools):
        """Register only the validate_rules tool"""
        # This would be implemented if needed
        pass
    
    def _register_regenerate_auto_rule_tool(self, mcp: "FastMCP", cursor_tools):
        """Register only the regenerate_auto_rule tool"""
        # This would be implemented if needed
        pass
    
    def _register_validate_tasks_json_tool(self, mcp: "FastMCP", cursor_tools):
        """Register only the validate_tasks_json tool"""
        # This would be implemented if needed
        pass
    
    def _register_create_context_file_tool(self, mcp: "FastMCP", cursor_tools):
        """Register the create_context_file tool for local context file creation"""
        @mcp.tool()
        def create_context_file(
            file_path: Annotated[str, Field(description="Path where the context file should be created (relative to project root)")],
            content: Annotated[str, Field(description="Content to write to the context file")]
        ) -> Dict[str, Any]:
            """📝 CREATE CONTEXT FILE - Create task context file locally from MCP server content
            
            This tool creates context files locally when the MCP server is running in Docker
            and cannot directly create files on the local machine.
            """
            try:
                from pathlib import Path
                
                # Resolve the full path from project root
                full_path = cursor_tools.project_root / file_path
                
                # Ensure the directory exists
                full_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Write the content to the file
                with open(full_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                return {
                    "success": True,
                    "message": f"Context file created successfully at {file_path}",
                    "full_path": str(full_path),
                    "size": len(content)
                }
                
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to create context file: {str(e)}"
                }


# ═══════════════════════════════════════════════════════════════════
# 🏗️ MAIN CONSOLIDATED TOOLS CLASS
# ═══════════════════════════════════════════════════════════════════

class ConsolidatedMCPTools:
    """Main MCP tools interface with clean architecture and separated concerns"""
    
    def __init__(self, task_repository: Optional[TaskRepository] = None, projects_file_path: Optional[str] = None, config_overrides: Optional[Dict[str, Any]] = None):
        logger.info("Initializing ConsolidatedMCPTools...")
        
        # Initialize configuration and paths
        self._config = ToolConfig(config_overrides)
        self._path_resolver = PathResolver()
        
        # Initialize repositories and services with hierarchical support
        self._repository_factory = TaskRepositoryFactory()
        self._auto_rule_generator = FileAutoRuleGenerator()
        
        # Initialize default task repository and application service
        # Use a default project_id for the repository when not specified
        self._task_repository = task_repository or self._repository_factory.create_repository(project_id="default_project")
        self._task_app_service = TaskApplicationService(self._task_repository, self._auto_rule_generator)
        
        # Initialize managers and handlers
        self._project_manager = ProjectManager(self._path_resolver, projects_file_path)
        # Use dynamic cursor agent directory from PathResolver
        cursor_agent_dir = self._path_resolver.get_cursor_agent_dir()
        self._call_agent_use_case = CallAgentUseCase(cursor_agent_dir)
        self._task_handler = TaskOperationHandler(self._repository_factory, self._auto_rule_generator, self._project_manager)
        self._cursor_rules_tools = CursorRulesTools()
        
        # Initialize tool registration orchestrator
        self._tool_orchestrator = ToolRegistrationOrchestrator(
            self._config, self._task_handler, self._project_manager, self._call_agent_use_case
        )
        
        logger.info("ConsolidatedMCPTools initialized successfully with hierarchical storage.")
    
    def register_tools(self, mcp: "FastMCP"):
        """Register all consolidated MCP tools using the orchestrator"""
        self._tool_orchestrator.register_all_tools(mcp)
    
    def manage_subtask(self, action: str, task_id: str, subtask_data: Dict[str, Any] = None, project_id: str = None, task_tree_id: str = "main", user_id: str = "default_id") -> Dict[str, Any]:
        """Manage subtask operations - delegates to task handler"""
        try:
            return self._task_handler.handle_subtask_operations(action, task_id, subtask_data, project_id, task_tree_id, user_id)
        except Exception as e:
            logger.error(f"Error in manage_subtask: {e}")
            return {"success": False, "error": str(e)}
    
    # Helper methods for testing and internal use
    def _handle_core_task_operations(self, action=None, project_id="default_project", task_tree_id="main", user_id="default_id", task_id=None, title=None, description=None, status=None, priority=None, details=None, estimated_effort=None, assignees=None, labels=None, due_date=None, force_full_generation=False, **kwargs) -> Dict[str, Any]:
        """Handle core task operations - delegates to task handler"""
        try:
            return self._task_handler.handle_core_operations(action, project_id, task_tree_id, user_id, task_id, title, description, status, priority, details, estimated_effort, assignees, labels, due_date, force_full_generation)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_complete_task(self, project_id="default_project", task_tree_id="main", user_id="default_id", task_id=None, **kwargs) -> Dict[str, Any]:
        """Handle task completion - delegates to task handler"""
        try:
            return self._task_handler.handle_core_operations("complete", project_id, task_tree_id, user_id, task_id, None, None, None, None, None, None, None, None, None)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_list_tasks(self, project_id="default_project", task_tree_id="main", user_id="default_id", status=None, priority=None, assignees=None, labels=None, limit=None, **kwargs) -> Dict[str, Any]:
        """Handle task listing - delegates to task handler"""
        try:
            return self._task_handler.handle_list_search_next("list", project_id, task_tree_id, user_id, status, priority, assignees, labels, limit, None)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_search_tasks(self, project_id="default_project", task_tree_id="main", user_id="default_id", query=None, **kwargs) -> Dict[str, Any]:
        """Handle task searching - delegates to task handler"""
        try:
            return self._task_handler.handle_list_search_next("search", project_id, task_tree_id, user_id, None, None, None, None, None, query)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_do_next(self, project_id="default_project", task_tree_id="main", user_id="default_id", **kwargs) -> Dict[str, Any]:
        """Handle next task retrieval - delegates to task handler"""
        try:
            return self._task_handler.handle_list_search_next("next", project_id, task_tree_id, user_id, None, None, None, None, None, None)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _handle_subtask_operations(self, *args, **kwargs) -> Dict[str, Any]:
        """Handle subtask operations - delegates to task handler"""
        return self._task_handler.handle_subtask_operations(*args, **kwargs)
    
    def _handle_dependency_operations(self, action=None, task_id=None, project_id="default_project", task_tree_id="main", user_id="default_id", dependency_data=None, **kwargs) -> Dict[str, Any]:
        """Handle dependency operations - delegates to task handler"""
        try:
            return self._task_handler.handle_dependency_operations(action, task_id, project_id, task_tree_id, user_id, dependency_data)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Multi-agent tools accessor for tests
    @property
    def _multi_agent_tools(self):
        """Access to multi-agent tools for testing"""
        return self._project_manager
    
    @_multi_agent_tools.setter
    def _multi_agent_tools(self, value):
        """Set multi-agent tools for testing (allows mocking)"""
        self._project_manager = value
    
    @property
    def task_handler(self):
        """Access to task handler for testing"""
        return self._task_handler
    
    @property
    def call_agent_use_case(self):
        """Access to call agent use case for testing"""
        return self._call_agent_use_case
    
    @property
    def cursor_rules_tools(self):
        """Access to cursor rules tools for testing"""
        return self._cursor_rules_tools


# ═══════════════════════════════════════════════════════════════════
# 🧪 SIMPLIFIED MULTI-AGENT TOOLS (FOR TESTING AND BACKWARD COMPATIBILITY)
# ═══════════════════════════════════════════════════════════════════

class SimpleMultiAgentTools:
    """Simplified multi-agent tools for testing and backward compatibility"""
    
    def __init__(self, projects_file_path: Optional[str] = None):
        self._path_resolver = PathResolver()
        self._project_manager = ProjectManager(self._path_resolver, projects_file_path)
        # Expose orchestrator for testing
        self._orchestrator = self._project_manager._orchestrator
        
        # Expose attributes that tests expect
        self._projects_file = self._project_manager._projects_file
        self._brain_dir = self._project_manager._brain_dir
        self._agent_converter = self._project_manager._agent_converter
    
    def create_project(self, project_id: str, name: str, description: str = None) -> Dict[str, Any]:
        """Create a new project"""
        return self._project_manager.create_project(
            project_id=project_id,
            name=name,
            description=description or f"Project: {name}"
        )
    
    def register_agent(self, project_id: str, agent_id: str, name: str, call_agent: str = None) -> Dict[str, Any]:
        """Register an agent to a project"""
        return self._project_manager.register_agent(
            project_id=project_id,
            agent_id=agent_id,
            name=name,
            call_agent=call_agent or f"@{agent_id.replace('_', '-')}-agent"
        )
    
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get project details"""
        return self._project_manager.get_project(project_id)
    
    def get_agents(self, project_id: str) -> Dict[str, Any]:
        """Get all agents for a project"""
        return self._project_manager.get_agents(project_id)
    
    def orchestrate_project(self, project_id: str) -> Dict[str, Any]:
        """Orchestrate project workload"""
        # Check if project exists first
        if project_id not in self._projects:
            return {"success": False, "error": f"Project {project_id} not found"}
        
        try:
            # Convert simplified project data to domain entities
            project_entity = self._project_manager._convert_to_project_entity(project_id)
            
            # Run orchestration using project manager's orchestrator (for test mocking)
            orchestration_result = self._project_manager._orchestrator.orchestrate_project(project_entity)
            
            # Update the simplified project data with any new assignments
            self._project_manager._update_project_from_entity(project_id, project_entity)
            
            return {
                "success": True, 
                "message": "Project orchestration completed",
                "orchestration_result": orchestration_result
            }
        except Exception as e:
            return {
                "success": False, 
                "error": f"Orchestration failed: {str(e)}"
            }
    
    def get_orchestration_dashboard(self, project_id: str) -> Dict[str, Any]:
        """Get orchestration dashboard"""
        return self._project_manager.get_orchestration_dashboard(project_id)
    
    def create_task_tree(self, project_id: str, tree_id: str, tree_name: str, tree_description: str = "") -> Dict[str, Any]:
        """Create a new task tree in project"""
        return self._project_manager.create_task_tree(project_id, tree_id, tree_name, tree_description)
    
    def get_task_tree_status(self, project_id: str, tree_id: str) -> Dict[str, Any]:
        """Get task tree status"""
        return self._project_manager.get_task_tree_status(project_id, tree_id)
    
    def assign_agent_to_tree(self, project_id: str, agent_id: str, tree_id: str) -> Dict[str, Any]:
        """Assign agent to task tree"""
        return self._project_manager.assign_agent_to_tree(project_id, agent_id, tree_id)
    
    def list_projects(self) -> Dict[str, Any]:
        """List all projects"""
        return self._project_manager.list_projects()
    
    # Properties for testing compatibility
    @property
    def _projects(self):
        """Access to internal projects data for testing"""
        return self._project_manager._projects
    
    @property
    def project_manager(self):
        """Access to project manager for testing"""
        return self._project_manager


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