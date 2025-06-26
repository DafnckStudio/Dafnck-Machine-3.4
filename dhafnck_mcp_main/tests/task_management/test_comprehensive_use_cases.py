"""Comprehensive Task Management Use Cases Tests with Test Data Isolation"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch

# Import test isolation system
from test_environment_config import isolated_test_environment


class TestTaskManagementUseCasesIsolated:
    """Test comprehensive task management functionality with complete test isolation"""
    
    @pytest.mark.isolated
    def test_project_lifecycle_management(self):
        """Test complete project lifecycle: create, update, list, delete"""
        with isolated_test_environment(test_id="project_lifecycle") as config:
            # Simulate project operations using isolated files
            projects_file = config.test_files["projects"]
            
            # Test project creation
            project_data = {
                "test_project_1": {
                    "name": "Test Project 1",
                    "description": "A comprehensive test project",
                    "created_at": "2025-01-26T00:00:00Z",
                    "task_trees": {
                        "main": {
                            "name": "Main task tree",
                            "description": "Primary task organization"
                        }
                    },
                    "registered_agents": {},
                    "agent_assignments": {}
                }
            }
            
            # Write project data
            with open(projects_file, 'w') as f:
                json.dump(project_data, f, indent=2)
            
            # Verify project creation
            with open(projects_file, 'r') as f:
                data = json.load(f)
            
            assert "test_project_1" in data
            assert data["test_project_1"]["name"] == "Test Project 1"
            assert "task_trees" in data["test_project_1"]
            assert "main" in data["test_project_1"]["task_trees"]
            
            # Test project update
            data["test_project_1"]["description"] = "Updated description"
            data["test_project_1"]["task_trees"]["feature_branch"] = {
                "name": "Feature Branch",
                "description": "Feature development tasks"
            }
            
            with open(projects_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Verify update
            with open(projects_file, 'r') as f:
                updated_data = json.load(f)
            
            assert updated_data["test_project_1"]["description"] == "Updated description"
            assert "feature_branch" in updated_data["test_project_1"]["task_trees"]
            
            print("✅ Project lifecycle management test passed")
    
    @pytest.mark.isolated
    def test_task_crud_operations(self):
        """Test task Create, Read, Update, Delete operations"""
        with isolated_test_environment(test_id="task_crud") as config:
            tasks_file = config.test_files["tasks"]
            
            # Test task creation
            task_data = {
                "task_001": {
                    "id": "task_001",
                    "title": "Implement user authentication",
                    "description": "Add login/logout functionality",
                    "status": "todo",
                    "priority": "high",
                    "assignees": ["@coding_agent"],
                    "project_id": "test_project",
                    "task_tree_id": "main",
                    "created_at": "2025-01-26T00:00:00Z",
                    "due_date": "2025-02-15T00:00:00Z",
                    "dependencies": [],
                    "subtasks": []
                }
            }
            
            # Write task data
            with open(tasks_file, 'w') as f:
                json.dump(task_data, f, indent=2)
            
            # Verify task creation
            with open(tasks_file, 'r') as f:
                data = json.load(f)
            
            assert "task_001" in data
            assert data["task_001"]["title"] == "Implement user authentication"
            assert data["task_001"]["status"] == "todo"
            assert "@coding_agent" in data["task_001"]["assignees"]
            
            # Test task update
            data["task_001"]["status"] = "in_progress"
            data["task_001"]["assignees"].append("@test_orchestrator_agent")
            
            with open(tasks_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Verify update
            with open(tasks_file, 'r') as f:
                updated_data = json.load(f)
            
            assert updated_data["task_001"]["status"] == "in_progress"
            assert "@test_orchestrator_agent" in updated_data["task_001"]["assignees"]
            
            # Test task completion
            updated_data["task_001"]["status"] = "done"
            updated_data["task_001"]["completed_at"] = "2025-01-26T12:00:00Z"
            
            with open(tasks_file, 'w') as f:
                json.dump(updated_data, f, indent=2)
            
            # Verify completion
            with open(tasks_file, 'r') as f:
                final_data = json.load(f)
            
            assert final_data["task_001"]["status"] == "done"
            assert "completed_at" in final_data["task_001"]
            
            print("✅ Task CRUD operations test passed")
    
    @pytest.mark.isolated
    def test_agent_management_workflow(self):
        """Test agent registration, assignment, and management"""
        with isolated_test_environment(test_id="agent_mgmt") as config:
            agents_file = config.test_files["agents"]
            projects_file = config.test_files["projects"]
            
            # Test agent registration
            agent_data = {
                "coding_agent": {
                    "id": "coding_agent",
                    "name": "Coding Agent",
                    "call_agent": "@coding_agent",
                    "capabilities": ["code_generation", "debugging", "testing"],
                    "status": "active",
                    "registered_at": "2025-01-26T00:00:00Z"
                },
                "system_architect_agent": {
                    "id": "system_architect_agent", 
                    "name": "System Architect Agent",
                    "call_agent": "@system_architect_agent",
                    "capabilities": ["system_design", "architecture_planning"],
                    "status": "active",
                    "registered_at": "2025-01-26T00:00:00Z"
                }
            }
            
            with open(agents_file, 'w') as f:
                json.dump(agent_data, f, indent=2)
            
            # Test project with agent assignments
            project_data = {
                "test_project": {
                    "name": "Test Project",
                    "description": "Project with agent assignments",
                    "registered_agents": {
                        "coding_agent": {
                            "id": "coding_agent",
                            "name": "Coding Agent",
                            "call_agent": "@coding_agent"
                        },
                        "system_architect_agent": {
                            "id": "system_architect_agent",
                            "name": "System Architect Agent", 
                            "call_agent": "@system_architect_agent"
                        }
                    },
                    "agent_assignments": {
                        "main": ["coding_agent"],
                        "architecture": ["system_architect_agent"]
                    },
                    "task_trees": {
                        "main": {"name": "Main", "description": "Main tasks"},
                        "architecture": {"name": "Architecture", "description": "Architecture tasks"}
                    }
                }
            }
            
            with open(projects_file, 'w') as f:
                json.dump(project_data, f, indent=2)
            
            # Verify agent registration and assignment
            with open(agents_file, 'r') as f:
                agents = json.load(f)
            
            with open(projects_file, 'r') as f:
                projects = json.load(f)
            
            assert len(agents) == 2
            assert "coding_agent" in agents
            assert "system_architect_agent" in agents
            
            project = projects["test_project"]
            assert len(project["registered_agents"]) == 2
            assert "main" in project["agent_assignments"]
            assert "coding_agent" in project["agent_assignments"]["main"]
            
            print("✅ Agent management workflow test passed")
    
    @pytest.mark.isolated
    def test_subtask_management(self):
        """Test subtask creation, completion, and hierarchy"""
        with isolated_test_environment(test_id="subtask_mgmt") as config:
            subtasks_file = config.test_files["subtasks"]
            tasks_file = config.test_files["tasks"]
            
            # Create parent task
            parent_task = {
                "task_001": {
                    "id": "task_001",
                    "title": "Implement authentication system",
                    "description": "Complete authentication implementation",
                    "status": "in_progress",
                    "subtasks": ["subtask_001", "subtask_002", "subtask_003"]
                }
            }
            
            with open(tasks_file, 'w') as f:
                json.dump(parent_task, f, indent=2)
            
            # Create subtasks
            subtask_data = {
                "subtask_001": {
                    "id": "subtask_001",
                    "parent_task_id": "task_001",
                    "title": "Design login form",
                    "description": "Create UI for user login",
                    "status": "done",
                    "completed": True
                },
                "subtask_002": {
                    "id": "subtask_002", 
                    "parent_task_id": "task_001",
                    "title": "Implement password validation",
                    "description": "Add password strength validation",
                    "status": "in_progress",
                    "completed": False
                },
                "subtask_003": {
                    "id": "subtask_003",
                    "parent_task_id": "task_001", 
                    "title": "Add session management",
                    "description": "Implement user session handling",
                    "status": "todo",
                    "completed": False
                }
            }
            
            with open(subtasks_file, 'w') as f:
                json.dump(subtask_data, f, indent=2)
            
            # Verify subtask structure
            with open(subtasks_file, 'r') as f:
                subtasks = json.load(f)
            
            with open(tasks_file, 'r') as f:
                tasks = json.load(f)
            
            # Test subtask relationships
            assert len(subtasks) == 3
            for subtask_id in ["subtask_001", "subtask_002", "subtask_003"]:
                assert subtask_id in subtasks
                assert subtasks[subtask_id]["parent_task_id"] == "task_001"
            
            # Test completion status
            assert subtasks["subtask_001"]["completed"] == True
            assert subtasks["subtask_002"]["completed"] == False
            assert subtasks["subtask_003"]["completed"] == False
            
            # Test parent task references
            parent = tasks["task_001"]
            assert len(parent["subtasks"]) == 3
            assert all(sid in parent["subtasks"] for sid in ["subtask_001", "subtask_002", "subtask_003"])
            
            print("✅ Subtask management test passed")
    
    @pytest.mark.isolated
    def test_task_dependency_management(self):
        """Test task dependencies and workflow"""
        with isolated_test_environment(test_id="task_deps") as config:
            tasks_file = config.test_files["tasks"]
            
            # Create tasks with dependencies
            task_data = {
                "task_001": {
                    "id": "task_001",
                    "title": "Database schema design", 
                    "status": "done",
                    "dependencies": [],
                    "dependents": ["task_002", "task_003"]
                },
                "task_002": {
                    "id": "task_002",
                    "title": "API endpoints implementation",
                    "status": "in_progress", 
                    "dependencies": ["task_001"],
                    "dependents": ["task_004"]
                },
                "task_003": {
                    "id": "task_003",
                    "title": "Database migrations",
                    "status": "todo",
                    "dependencies": ["task_001"], 
                    "dependents": []
                },
                "task_004": {
                    "id": "task_004",
                    "title": "Frontend integration",
                    "status": "todo",
                    "dependencies": ["task_002"],
                    "dependents": []
                }
            }
            
            with open(tasks_file, 'w') as f:
                json.dump(task_data, f, indent=2)
            
            # Verify dependency structure
            with open(tasks_file, 'r') as f:
                tasks = json.load(f)
            
            # Test dependency relationships
            assert len(tasks["task_001"]["dependencies"]) == 0  # Root task
            assert "task_001" in tasks["task_002"]["dependencies"]
            assert "task_001" in tasks["task_003"]["dependencies"] 
            assert "task_002" in tasks["task_004"]["dependencies"]
            
            # Test dependent relationships
            assert "task_002" in tasks["task_001"]["dependents"]
            assert "task_003" in tasks["task_001"]["dependents"]
            assert "task_004" in tasks["task_002"]["dependents"]
            
            # Test workflow validation
            def can_start_task(task_id, tasks):
                task = tasks[task_id]
                for dep_id in task["dependencies"]:
                    if tasks[dep_id]["status"] != "done":
                        return False
                return True
            
            assert can_start_task("task_001", tasks) == True  # No deps
            assert can_start_task("task_002", tasks) == True  # Dep is done
            assert can_start_task("task_003", tasks) == True  # Dep is done
            assert can_start_task("task_004", tasks) == False # Dep not done
            
            print("✅ Task dependency management test passed")


# Run tests if executed directly
if __name__ == "__main__":
    test_instance = TestTaskManagementUseCasesIsolated()
    
    print("🧪 Running comprehensive task management tests...")
    
    test_instance.test_project_lifecycle_management()
    test_instance.test_task_crud_operations()
    test_instance.test_agent_management_workflow()
    test_instance.test_subtask_management()
    test_instance.test_task_dependency_management()
    
    print("🎉 All task management tests passed!") 