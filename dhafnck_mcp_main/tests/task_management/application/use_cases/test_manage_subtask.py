import pytest
from unittest.mock import MagicMock
from fastmcp.task_management.interface.consolidated_mcp_tools_v2 import (
    ConsolidatedMCPToolsV2,
)

mock_task_app_service = MagicMock()


@pytest.fixture
def mcp_tools():
    tools = ConsolidatedMCPToolsV2()
    tools._task_app_service = mock_task_app_service
    return tools


@pytest.fixture
def sample_task_id():
    return "20250620001"


@pytest.fixture
def sample_subtask_data():
    return {"title": "New Subtask"}


@pytest.fixture
def sample_subtask_id():
    return 1


def test_add_subtask_happy_path(mcp_tools, sample_task_id, sample_subtask_data):
    mock_task_app_service.reset_mock()
    mock_task_app_service.manage_subtasks.return_value = {
        "id": 1, "title": "New Subtask", "completed": False
    }
    result = mcp_tools._handle_subtask_operations(
        action="add",
        task_id=sample_task_id,
        subtask_data=sample_subtask_data,
    )
    assert result["success"] is True
    assert result["result"]["title"] == "New Subtask"
    mock_task_app_service.manage_subtasks.assert_called_once_with(
        sample_task_id, "add", sample_subtask_data
    )


def test_complete_subtask_happy_path(mcp_tools, sample_task_id, sample_subtask_id):
    mock_task_app_service.reset_mock()
    mock_task_app_service.manage_subtasks.return_value = {"status": "completed"}
    result = mcp_tools._handle_subtask_operations(
        action="complete",
        task_id=sample_task_id,
        subtask_data={"subtask_id": sample_subtask_id},
    )
    assert result["success"] is True
    mock_task_app_service.manage_subtasks.assert_called_once_with(
        sample_task_id, "complete", {"subtask_id": sample_subtask_id}
    )


def test_update_subtask_happy_path(mcp_tools, sample_task_id, sample_subtask_id):
    mock_task_app_service.reset_mock()
    updated_data = {"subtask_id": sample_subtask_id, "title": "Updated Subtask"}
    mock_task_app_service.manage_subtasks.return_value = {
        "id": 1, "title": "Updated Subtask", "completed": False
    }
    result = mcp_tools._handle_subtask_operations(
        action="update", task_id=sample_task_id, subtask_data=updated_data
    )
    assert result["success"] is True
    mock_task_app_service.manage_subtasks.assert_called_once_with(
        sample_task_id, "update", updated_data
    )


def test_remove_subtask_happy_path(mcp_tools, sample_task_id, sample_subtask_id):
    mock_task_app_service.reset_mock()
    mock_task_app_service.manage_subtasks.return_value = {"status": "removed"}
    result = mcp_tools._handle_subtask_operations(
        action="remove",
        task_id=sample_task_id,
        subtask_data={"subtask_id": sample_subtask_id},
    )
    assert result["success"] is True
    mock_task_app_service.manage_subtasks.assert_called_once_with(
        sample_task_id, "remove", {"subtask_id": sample_subtask_id}
    )


def test_list_subtasks_happy_path(mcp_tools, sample_task_id):
    mock_task_app_service.reset_mock()
    mock_task_app_service.manage_subtasks.return_value = []
    result = mcp_tools._handle_subtask_operations(
        action="list", task_id=sample_task_id, subtask_data=None
    )
    assert result["success"] is True
    assert isinstance(result["result"], list)
    mock_task_app_service.manage_subtasks.assert_called_once_with(
        sample_task_id, "list", {}
    ) 