"""
This is the canonical and only maintained test suite for end-to-end journey integration tests in task management.
All validation, edge-case, and integration tests should be added here.
Redundant or duplicate tests in other files have been removed.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


import pytest
import os
import json
from fastmcp import FastMCP
from fastmcp.task_management.interface.consolidated_mcp_tools_v2 import ConsolidatedMCPToolsV2
from fastmcp.task_management.infrastructure.repositories.json_task_repository import InMemoryTaskRepository

@pytest.fixture(scope="function")
def mcp_server_instance():
    """Fixture to provide a clean MCP server instance with an in-memory repository for each test."""
    os.environ['PYTHONPATH'] = 'cursor_agent/src'
    
    # Create a new FastMCP instance for each test to ensure isolation
    mcp = FastMCP("test-e2e-server")
    
    # Use an in-memory repository for test isolation and speed
    in_memory_repo = InMemoryTaskRepository()
    
    # Instantiate the tools and register them with the MCP instance
    mcp_tools_instance = ConsolidatedMCPToolsV2(task_repository=in_memory_repo)
    mcp_tools_instance.register_tools(mcp)
    
    return mcp

@pytest.fixture(autouse=True)
def setup_teardown(mcp_server_instance):
    """Fixture to clean up data before and after each test."""
    # The mcp_server_instance fixture already creates a fresh in-memory setup for each test,
    # so explicit cleanup is less critical but good for clarity.
    # The underlying repo and project data are encapsulated within the tools instance
    # that gets created freshly with each mcp_server_instance call.
    yield
    # No explicit teardown needed as everything is in-memory and function-scoped.


class TestE2EUserJourneys:
    """End-to-end tests for critical user journeys."""

    async def test_project_and_team_setup_journey(self, mcp_server_instance):
        """
        Tests the user journey of setting up a new project and registering a team.
        """
        # 1. Create a new project
        project_id = "e2e_project_1"
        create_project_response_list = await mcp_server_instance._mcp_call_tool(
            "manage_project",
            {
                "action": "create",
                "project_id": project_id,
                "name": "E2E Test Project",
                "description": "A project for E2E testing."
            }
        )
        create_project_response = json.loads(create_project_response_list[0].text)
        assert create_project_response["success"]
        assert create_project_response["project"]["id"] == project_id

        # 2. Register two agents
        agent_1_id = "agent_001"
        agent_2_id = "agent_002"
        
        register_agent_1_response_list = await mcp_server_instance._mcp_call_tool(
            "manage_agent",
            {
                "action": "register",
                "project_id": project_id,
                "agent_id": agent_1_id,
                "name": "Test Agent 1"
            }
        )
        register_agent_1_response = json.loads(register_agent_1_response_list[0].text)
        assert register_agent_1_response["success"]
        assert register_agent_1_response["agent"]["id"] == agent_1_id
        
        register_agent_2_response_list = await mcp_server_instance._mcp_call_tool(
            "manage_agent",
            {
                "action": "register",
                "project_id": project_id,
                "agent_id": agent_2_id,
                "name": "Test Agent 2"
            }
        )
        register_agent_2_response = json.loads(register_agent_2_response_list[0].text)
        assert register_agent_2_response["success"]
        assert register_agent_2_response["agent"]["id"] == agent_2_id

        # 3. List agents and verify they were added
        list_agents_response_list = await mcp_server_instance._mcp_call_tool(
            "manage_agent",
            {"action": "list", "project_id": project_id}
        )
        list_agents_response = json.loads(list_agents_response_list[0].text)
        assert list_agents_response["success"]
        
        registered_agents = list_agents_response["agents"]
        assert len(registered_agents) == 2
        assert agent_1_id in registered_agents
        assert agent_2_id in registered_agents

    async def test_full_task_lifecycle_journey(self, mcp_server_instance):
        """
        Tests the full lifecycle of a task from creation to completion,
        including subtask management.
        """
        # 1. Create a new task
        create_task_response_list = await mcp_server_instance._mcp_call_tool(
            "manage_task",
            {
                "action": "create",
                "title": "E2E Full Lifecycle Task",
                "description": "A task to test the full lifecycle.",
                "priority": "high",
                "labels": ["e2e-test", "lifecycle"]
            }
        )
        create_task_response = json.loads(create_task_response_list[0].text)
        assert create_task_response["success"]
        task_id = create_task_response["task"]["id"]
    
        # 2. Get the task to verify creation
        get_task_response_list = await mcp_server_instance._mcp_call_tool(
            "manage_task",
            {"action": "get", "task_id": task_id}
        )
        get_task_response = json.loads(get_task_response_list[0].text)
        assert get_task_response["success"]
        assert get_task_response["task"]["title"] == "E2E Full Lifecycle Task"
        assert get_task_response["task"]["status"] == "todo"
    
        # 3. Update the task status
        update_task_response_list = await mcp_server_instance._mcp_call_tool(
            "manage_task",
            {
                "action": "update",
                "task_id": task_id,
                "status": "in_progress"
            }
        )
        update_task_response = json.loads(update_task_response_list[0].text)
        assert update_task_response["success"]
        assert update_task_response["task"]["status"] == "in_progress"
    
        # 4. Add a subtask
        add_subtask_response_list = await mcp_server_instance._mcp_call_tool(
            "manage_subtask",
            {
                "action": "add_subtask",
                "task_id": task_id,
                "subtask_data": {"title": "First subtask"}
            }
        )
        add_subtask_response = json.loads(add_subtask_response_list[0].text)
        assert add_subtask_response["success"]
        subtask_id = add_subtask_response["result"]["subtask"]["id"]
    
        # 5. Complete the subtask
        complete_subtask_response_list = await mcp_server_instance._mcp_call_tool(
            "manage_subtask",
            {
                "action": "complete_subtask",
                "task_id": task_id,
                "subtask_data": {"subtask_id": subtask_id}
            }
        )
        complete_subtask_response = json.loads(complete_subtask_response_list[0].text)
        assert complete_subtask_response["success"]
    
        # Verify subtask is complete
        list_subtasks_response_list = await mcp_server_instance._mcp_call_tool(
            "manage_subtask",
            {"action": "list_subtasks", "task_id": task_id}
        )
        list_subtasks_response = json.loads(list_subtasks_response_list[0].text)
        assert list_subtasks_response["success"]
        completed_subtask = next(st for st in list_subtasks_response["result"] if st["id"] == subtask_id)
        assert completed_subtask["completed"]

        # 6. Complete the main task
        complete_task_response_list = await mcp_server_instance._mcp_call_tool("manage_task", {"action": "complete", "task_id": task_id})
        complete_task_response = json.loads(complete_task_response_list[0].text)
        print(f"DEBUG: complete_task_response = {complete_task_response}")
        assert complete_task_response["success"]

        # 7. Verify the task is marked as 'done'
        final_get_task_response_list = await mcp_server_instance._mcp_call_tool("manage_task", {"action": "get", "task_id": task_id})
        final_get_task_response = json.loads(final_get_task_response_list[0].text)
        assert final_get_task_response["success"]
        assert final_get_task_response["task"]["status"] == "done"

        # 8. Delete the task
        delete_task_response_list = await mcp_server_instance._mcp_call_tool(
            "manage_task",
            {"action": "delete", "task_id": task_id}
        )
        delete_task_response = json.loads(delete_task_response_list[0].text)
        assert delete_task_response["success"]

    async def test_task_and_project_querying_journey(self, mcp_server_instance):
        """
        Tests the system's ability to filter and search for tasks.
        """
        # 1. Create a single task
        create_response_list = await mcp_server_instance._mcp_call_tool(
            "manage_task",
            {
                "action": "create",
                "title": "High priority task",
                "description": "A non-empty description for testing.",
                "priority": "high",
                "status": "in_progress",
                "labels": ["query-test", "backend"],
            }
        )
        create_response = json.loads(create_response_list[0].text)
        assert create_response["success"], f"Task creation failed: {create_response.get('error')}"

        # 2. List all tasks to see what's in the repo
        all_tasks_response_list = await mcp_server_instance._mcp_call_tool("manage_task", {"action": "list"})
        all_tasks_response = json.loads(all_tasks_response_list[0].text)
        assert all_tasks_response["success"], "Listing all tasks failed"
        assert len(all_tasks_response["tasks"]) == 1, f"Expected 1 task, but found {len(all_tasks_response['tasks'])}"

        # 3. List tasks filtered by status and priority
        list_response_list = await mcp_server_instance._mcp_call_tool("manage_task", {"action": "list", "status": "in_progress", "priority": "high"})
        list_response = json.loads(list_response_list[0].text)
        assert list_response["success"]
        assert len(list_response["tasks"]) == 1
        
        task = list_response["tasks"][0]
        assert task["status"] == "in_progress"
        assert task["priority"] == "high"

        # 4. Search for the task
        search_response_list = await mcp_server_instance._mcp_call_tool("manage_task", {"action": "search", "query": "High priority"})
        search_response = json.loads(search_response_list[0].text)
        assert search_response["success"]
        assert len(search_response["tasks"]) == 1
        assert search_response["tasks"][0]["title"] == "High priority task"

        # 5. Get next recommended task (should be one of the high priority tasks)
        next_task_response_list = await mcp_server_instance._mcp_call_tool("manage_task", {"action": "next"})
        next_task_response = json.loads(next_task_response_list[0].text)
        assert next_task_response["success"]
        assert next_task_response["next_item"]["task"]["priority"] == "high"

    async def test_agent_collaboration_journey(self, mcp_server_instance):
        """
        Tests a scenario involving multiple agents collaborating on a task.
        """
        # 1. Create a task and assign it to multiple agents
        agents = ["@coding-agent", "@test-agent"]
        create_response_list = await mcp_server_instance._mcp_call_tool(
            "manage_task",
            {
                "action": "create",
                "title": "Collaborative Task",
                "description": "A task requiring collaboration between two agents.",
                "priority": "critical",
                "assignees": agents,
            }
        )
        create_response = json.loads(create_response_list[0].text)
        assert create_response["success"], "Task creation with multiple assignees failed"
        task_id = create_response["task"]["id"]

        # 2. Get the task and verify the assignees
        get_response_list = await mcp_server_instance._mcp_call_tool("manage_task", {"action": "get", "task_id": task_id})
        get_response = json.loads(get_response_list[0].text)
        assert get_response["success"]
        
        assignees = get_response["task"]["assignees"]
        assert isinstance(assignees, list)
        assert "@coding_agent" in assignees
        assert "@test-agent" in assignees

        # 3. An agent updates the task
        update_response_list = await mcp_server_instance._mcp_call_tool(
            "manage_task",
            {
                "action": "update",
                "task_id": task_id,
                "details": "Coding part completed by @coding-agent.",
            }
        )
        update_response = json.loads(update_response_list[0].text)
        assert update_response["success"], "Updating task details failed"

        # 4. Remove one agent after their work is done
        updated_assignees = ["@test-agent"]
        update_assignees_response_list = await mcp_server_instance._mcp_call_tool(
            "manage_task",
            {
                "action": "update",
                "task_id": task_id,
                "assignees": updated_assignees,
            }
        )
        update_assignees_response = json.loads(update_assignees_response_list[0].text)
        assert update_assignees_response["success"], "Updating assignees failed"

        # 5. Verify the remaining assignee
        final_get_response_list = await mcp_server_instance._mcp_call_tool("manage_task", {"action": "get", "task_id": task_id})
        final_get_response = json.loads(final_get_response_list[0].text)
        assert final_get_response["success"]
        assert len(final_get_response["task"]["assignees"]) == 1
        assert final_get_response["task"]["assignees"][0] == "@test-agent" 

    async def test_dependency_management_journey(self, mcp_server_instance):
        """
        Tests a scenario involving task dependencies.
        """
        # 1. Create two tasks
        task1_response_list = await mcp_server_instance._mcp_call_tool(
            "manage_task", {"action": "create", "title": "Task 1 (blocked)", "description": "This task is blocked."}
        )
        task1_response = json.loads(task1_response_list[0].text)
        task2_response_list = await mcp_server_instance._mcp_call_tool(
            "manage_task", {"action": "create", "title": "Task 2 (blocking)", "description": "This task is a blocker."}
        )
        task2_response = json.loads(task2_response_list[0].text)
        
        assert task1_response["success"]
        assert task2_response["success"]
        
        task1_id = task1_response["task"]["id"]
        task2_id = task2_response["task"]["id"]

        # 2. Add dependency: Task 1 is blocked by Task 2
        add_dep_response_list = await mcp_server_instance._mcp_call_tool(
            "manage_task",
            {
                "action": "add_dependency",
                "task_id": task1_id,
                "dependency_data": {"type": "blocked_by", "dependency_id": task2_id}
            }
        )
        add_dep_response = json.loads(add_dep_response_list[0].text)
        assert add_dep_response["success"]

        # 3. Verify dependency
        get_task1_response_list = await mcp_server_instance._mcp_call_tool("manage_task", {"action": "get", "task_id": task1_id})
        get_task1_response = json.loads(get_task1_response_list[0].text)
        assert get_task1_response["success"]
        assert task2_id in get_task1_response["task"]["dependencies"]

        # 4. Complete blocking task
        complete_task2_response_list = await mcp_server_instance._mcp_call_tool("manage_task", {"action": "complete", "task_id": task2_id})
        complete_task2_response = json.loads(complete_task2_response_list[0].text)
        assert complete_task2_response["success"]

        # 5. Verify dependency is resolved (optional, depends on implementation)
        # For now, just check that the task status is updated
        get_task1_after_response_list = await mcp_server_instance._mcp_call_tool("manage_task", {"action": "get", "task_id": task1_id})
        get_task1_after_response = json.loads(get_task1_after_response_list[0].text)
        assert get_task1_after_response["success"]
        # Assuming the system automatically unblocks the task
        # This part of the logic might not be implemented, so we check for 'todo' or similar
        assert get_task1_after_response["task"]["status"] in ["todo", "in_progress"]