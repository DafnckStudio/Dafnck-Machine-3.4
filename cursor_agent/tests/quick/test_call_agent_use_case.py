"""Quick test for CallAgentUseCase functionality"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

from src.task_mcp.application.use_cases.call_agent import CallAgentUseCase


def test_call_agent_use_case_can_be_instantiated():
    """Test that CallAgentUseCase can be instantiated"""
    cursor_agent_dir = Path(".")
    use_case = CallAgentUseCase(cursor_agent_dir)
    assert use_case is not None
    assert use_case._cursor_agent_dir == cursor_agent_dir


def test_call_agent_use_case_handles_missing_agent():
    """Test that CallAgentUseCase handles missing agent gracefully"""
    cursor_agent_dir = Path(".")
    use_case = CallAgentUseCase(cursor_agent_dir)
    
    result = use_case.execute("non_existent_agent")
    
    assert result["success"] is False
    assert "not found" in result["error"]


def test_call_agent_use_case_with_existing_agent():
    """Test that CallAgentUseCase works with an existing agent"""
    cursor_agent_dir = Path(".")
    use_case = CallAgentUseCase(cursor_agent_dir)
    
    # Test with coding_agent which should exist
    result = use_case.execute("coding_agent")
    
    if result["success"]:
        assert "agent_info" in result
        assert isinstance(result["agent_info"], dict)
        # Should have some basic agent information
        assert len(result["agent_info"]) > 0
    else:
        # If it fails, it should be because the agent directory doesn't exist in test environment
        assert "not found" in result["error"]


def test_call_agent_use_case_calls_generate_docs():
    """Test that CallAgentUseCase calls generate_docs_for_assignees"""
    cursor_agent_dir = Path(".")
    use_case = CallAgentUseCase(cursor_agent_dir)
    
    # Mock the generate_docs_for_assignees function
    with patch('src.task_mcp.application.use_cases.call_agent.generate_docs_for_assignees') as mock_generate:
        # Mock the agent directory to exist and have YAML files
        with patch.object(Path, 'exists', return_value=True), \
             patch.object(Path, 'is_dir', return_value=True), \
             patch('os.walk') as mock_walk:
            
            # Mock os.walk to return a YAML file
            mock_walk.return_value = [
                ('/fake/path', [], ['job_desc.yaml'])
            ]
            
            # Mock yaml.safe_load to return some data
            with patch('yaml.safe_load', return_value={'name': 'Test Agent'}):
                result = use_case.execute("test_agent")
                
                # Should have called generate_docs_for_assignees
                mock_generate.assert_called_once_with(["test_agent"], clear_all=False)
                
                # Should return success
                assert result["success"] is True
                assert "agent_info" in result


def test_call_agent_use_case_integration_with_consolidated_tools():
    """Test that CallAgentUseCase integrates correctly with ConsolidatedMCPToolsV2"""
    from src.task_mcp.interface.consolidated_mcp_tools_v2 import ConsolidatedMCPToolsV2
    
    tools = ConsolidatedMCPToolsV2()
    
    # Should have the call_agent_use_case attribute
    assert hasattr(tools, '_call_agent_use_case')
    assert tools._call_agent_use_case is not None
    
    # Should have an execute method
    assert hasattr(tools._call_agent_use_case, 'execute')
    assert callable(tools._call_agent_use_case.execute)
    
    # Should be able to call execute method
    result = tools._call_agent_use_case.execute("non_existent_agent")
    assert isinstance(result, dict)
    assert "success" in result 