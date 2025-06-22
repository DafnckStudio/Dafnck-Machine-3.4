import sys
import os
from pprint import pprint

# Adjust path for direct script execution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from task_mcp.domain.entities.task import Task
from task_mcp.domain.enums.agent_roles import AgentRole, resolve_legacy_role
from datetime import datetime

# Simulate a task (minimal required fields)
task = Task(
    id="20250620012",
    title="Identify untested or under-tested modules/functions",
    description="List all code areas below the target coverage threshold.",
    status="todo",
    priority="high",
    created_at=datetime.now(),
    updated_at=datetime.now()
)

assignee_variants = [
    "coding_agent",   # Enum value
    "coding-agent",   # Dash variant
    "senior_developer", # Legacy mapping
    "@coding_agent",  # At-sign variant
    "not_a_real_agent" # Invalid
]

for assignee in assignee_variants:
    print(f"\nTrying assignee: {assignee}")
    task.update_assignees([assignee])
    print("Task assignees after update:", task.assignees)
    print("Is valid AgentRole:", AgentRole.is_valid_role(assignee))
    print("Resolved legacy role:", resolve_legacy_role(assignee))
    print("Task to_dict output:")
    pprint(task.to_dict()) 