import pytest
import os
from fastmcp.task_management.interface.consolidated_mcp_tools_v2 import ConsolidatedMCPToolsV2
from fastmcp.task_management.infrastructure.repositories.json_task_repository import InMemoryTaskRepository

@pytest.fixture(scope="module")
def mcp_tools():
    """Fixture to provide an instance of the MCP tools with an in-memory repository."""
    # This ensures that PYTHONPATH is set correctly for the test environment
    # Note: In a real CI/CD, this should be configured globally.
    os.environ['PYTHONPATH'] = 'cursor_agent/src'
    # Use an in-memory repository for test isolation and speed
    in_memory_repo = InMemoryTaskRepository()
    return ConsolidatedMCPToolsV2(task_repository=in_memory_repo)

@pytest.fixture(autouse=True)
def setup_teardown(mcp_tools):
    """Fixture to clean up created projects and tasks before and after each test."""
    # Setup: Clear any existing data to ensure a clean slate.
    mcp_tools._multi_agent_tools._projects = {}
    mcp_tools._multi_agent_tools._save_projects()
    # Clear the in-memory repository
    mcp_tools._task_repository._tasks = {}
    mcp_tools._task_repository._next_id = 1
    yield
    # Teardown: Clean up after the test.
    mcp_tools._multi_agent_tools._projects = {}
    mcp_tools._multi_agent_tools._save_projects()
    mcp_tools._task_repository._tasks = {}
    mcp_tools._task_repository._next_id = 1

class TestE2EUserJourneys:
    """End-to-end tests for critical user journeys."""

    def test_project_and_team_setup_journey(self, mcp_tools):
        """
        Tests the user journey of setting up a new project and registering a team.
        """
        # 1. Create a new project
        project_id = "e2e_project_1"
        create_project_response = mcp_tools._multi_agent_tools.create_project(
            project_id=project_id,
            name="E2E Test Project",
            description="A project for E2E testing."
        )
        assert create_project_response["success"]
        assert create_project_response["project"]["id"] == project_id

        # 2. Register two agents
        agent_1_id = "agent_001"
        agent_2_id = "agent_002"
        
        register_agent_1_response = mcp_tools._multi_agent_tools.register_agent(
            project_id=project_id,
            agent_id=agent_1_id,
            name="Test Agent 1"
        )
        assert register_agent_1_response["success"]
        assert register_agent_1_response["agent"]["id"] == agent_1_id
        
        register_agent_2_response = mcp_tools._multi_agent_tools.register_agent(
            project_id=project_id,
            agent_id=agent_2_id,
            name="Test Agent 2"
        )
        assert register_agent_2_response["success"]
        assert register_agent_2_response["agent"]["id"] == agent_2_id

        # 3. List agents and verify they were added
        list_agents_response = mcp_tools._multi_agent_tools.list_projects() #This should be list_agents in project, but it is not available, so I am just checking project list
        # We need to get project and check agents
        get_project_response = mcp_tools._multi_agent_tools.get_project(project_id)
        assert get_project_response["success"]
        
        registered_agents = get_project_response["project"]["registered_agents"]
        assert len(registered_agents) == 2
        assert agent_1_id in registered_agents
        assert agent_2_id in registered_agents

    def test_full_task_lifecycle_journey(self, mcp_tools):
        """
        Tests the full lifecycle of a task from creation to completion,
        including subtask management.
        """
        # 1. Create a new task
        create_task_response = mcp_tools.manage_task(
            action="create",
            title="E2E Full Lifecycle Task",
            description="A task to test the full lifecycle.",
            priority="high",
            labels=["e2e-test", "lifecycle"]
        )
        assert create_task_response["success"]
        task_id = create_task_response["task"]["id"]
    
        # 2. Get the task to verify creation
        get_task_response = mcp_tools.manage_task(
            action="get", task_id=task_id
        )
        assert get_task_response["success"]
        assert get_task_response["task"]["title"] == "E2E Full Lifecycle Task"
        assert get_task_response["task"]["status"] == "todo"
    
        # 3. Update the task status
        update_task_response = mcp_tools.manage_task(
            action="update",
            task_id=task_id,
            status="in_progress"
        )
        assert update_task_response["success"]
        assert update_task_response["task"]["status"] == "in_progress"
    
        # 4. Add a subtask
        add_subtask_response = mcp_tools.manage_subtask(
            action="add",
            task_id=task_id,
            subtask_data={"title": "First subtask"}
        )
        assert add_subtask_response["success"]
        subtask_id = add_subtask_response["result"]["subtask"]["id"]
    
        # 5. Complete the subtask
        complete_subtask_response = mcp_tools.manage_subtask(
            action="complete",
            task_id=task_id,
            subtask_data={"subtask_id": subtask_id}
        )
        assert complete_subtask_response["success"]
    
        # Verify subtask is complete
        list_subtasks_response = mcp_tools.manage_subtask(
            action="list", task_id=task_id
        )
        assert list_subtasks_response["success"]
        completed_subtask = next(st for st in list_subtasks_response["result"]["subtasks"] if st["id"] == subtask_id)
        assert completed_subtask["completed"] is True

        # 6. Complete the main task
        complete_task_response = mcp_tools._handle_complete_task(task_id=task_id)
        assert complete_task_response["success"]

        # 7. Verify the task is marked as 'done'
        final_get_task_response = mcp_tools._handle_core_task_operations(
            action="get", task_id=task_id, title=None, description=None, status=None, priority=None, details=None, estimated_effort=None, assignees=None, labels=None, due_date=None
        )
        assert final_get_task_response["success"]
        assert final_get_task_response["task"]["status"] == "done"

    def test_task_and_project_querying_journey(self, mcp_tools):
        """
        Tests the system's ability to filter and search for tasks.
        """
        # 1. Create a single task
        create_response = mcp_tools._handle_core_task_operations(
            action="create",
            title="High priority task",
            description="A non-empty description for testing.",
            priority="high",
            status="in_progress",
            labels=["query-test", "backend"],
            task_id=None, details=None, estimated_effort=None, assignees=None, due_date=None
        )
        assert create_response["success"], f"Task creation failed: {create_response.get('error')}"

        # 2. List all tasks to see what's in the repo
        all_tasks_response = mcp_tools._handle_list_tasks(status=None, priority=None, assignees=None, labels=None, limit=None)
        assert all_tasks_response["success"], "Listing all tasks failed"
        assert len(all_tasks_response["tasks"]) == 1, f"Expected 1 task, but found {len(all_tasks_response['tasks'])}"

        # 3. List tasks filtered by status and priority
        list_response = mcp_tools._handle_list_tasks(status="in_progress", priority="high", assignees=None, labels=None, limit=None)
        assert list_response["success"]
        assert len(list_response["tasks"]) == 1
        
        task = list_response["tasks"][0]
        assert task["status"] == "in_progress"
        assert task["priority"] == "high"

        # 4. Search for the task
        search_response = mcp_tools._handle_search_tasks(query="High priority", limit=None)
        assert search_response["success"]
        assert len(search_response["tasks"]) == 1
        assert search_response["tasks"][0]["title"] == "High priority task"

        # 5. Get next recommended task (should be one of the high priority tasks)
        next_task_response = mcp_tools._handle_do_next()
        assert next_task_response["success"]
        assert next_task_response["next_item"]["task"]["priority"] == "high"

    def test_agent_collaboration_journey(self, mcp_tools):
        """
        Tests a scenario involving multiple agents collaborating on a task.
        """
        # 1. Create a task and assign it to multiple agents
        agents = ["@coding-agent", "@functional-tester-agent"]
        create_response = mcp_tools._handle_core_task_operations(
            action="create",
            title="Collaborative Task",
            description="A task requiring collaboration between two agents.",
            priority="critical",
            assignees=agents,
            task_id=None, status=None, details=None, estimated_effort=None, labels=None, due_date=None
        )
        assert create_response["success"], "Task creation with multiple assignees failed"
        task_id = create_response["task"]["id"]

        # 2. Get the task and verify the assignees
        get_response = mcp_tools._handle_core_task_operations(
            action="get", task_id=task_id, title=None, description=None, status=None, priority=None, details=None, estimated_effort=None, assignees=None, labels=None, due_date=None
        )
        assert get_response["success"]
        assert len(get_response["task"]["assignees"]) == 2
        assert "@coding_agent" in get_response["task"]["assignees"]
        assert "@functional_tester_agent" in get_response["task"]["assignees"]

        # 3. Simulate one agent completing their part (by updating status)
        # In a real scenario, this would be a more complex interaction.
        # Here, we'll just update the task details to reflect the work done.
        update_response = mcp_tools._handle_core_task_operations(
            action="update",
            task_id=task_id,
            details="Coding part completed by @coding-agent.",
            title=None, description=None, status=None, priority=None, estimated_effort=None, assignees=None, labels=None, due_date=None
        )
        assert update_response["success"], "Updating task details failed"

        # 4. Remove one agent after their work is done
        updated_assignees = ["@functional_tester_agent"]
        update_assignees_response = mcp_tools._handle_core_task_operations(
            action="update",
            task_id=task_id,
            assignees=updated_assignees,
            title=None, description=None, status=None, priority=None, details=None, estimated_effort=None, labels=None, due_date=None
        )
        assert update_assignees_response["success"], "Updating assignees failed"

        # 5. Verify the remaining assignee
        final_get_response = mcp_tools._handle_core_task_operations(
            action="get", task_id=task_id, title=None, description=None, status=None, priority=None, details=None, estimated_effort=None, assignees=None, labels=None, due_date=None
        )
        assert final_get_response["success"]
        assert len(final_get_response["task"]["assignees"]) == 1
        assert final_get_response["task"]["assignees"][0] == "@functional_tester_agent" 