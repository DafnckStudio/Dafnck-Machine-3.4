import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


import pytest
from unittest.mock import MagicMock
from fastmcp.task_management.interface.consolidated_mcp_tools import (
    ConsolidatedMCPTools,
)

mock_multi_agent_tools = MagicMock()


@pytest.fixture
def mcp_tools():
    tools = ConsolidatedMCPTools()
    tools._multi_agent_tools = mock_multi_agent_tools
    return tools


def test_register_agent_happy_path(mcp_tools):
    mock_multi_agent_tools.register_agent.return_value = {"success": True}
    result = mcp_tools._multi_agent_tools.register_agent(
        project_id="proj1", agent_id="agent1", name="Test Agent", description="A test agent"
    )
    assert result["success"] is True
    mock_multi_agent_tools.register_agent.assert_called_once_with(
        project_id="proj1", agent_id="agent1", name="Test Agent", description="A test agent"
    )

def test_assign_agent_to_tree_happy_path(mcp_tools):
    mock_multi_agent_tools.assign_agent_to_tree.return_value = {"success": True}
    result = mcp_tools._multi_agent_tools.assign_agent_to_tree(
        project_id="proj1", agent_id="agent1", tree_id="tree1"
    )
    assert result["success"] is True
    mock_multi_agent_tools.assign_agent_to_tree.assert_called_once_with(
        project_id="proj1", agent_id="agent1", tree_id="tree1"
    ) 