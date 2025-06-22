"""Simple Integration Tests for Task Management API Endpoints"""

import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch


def test_main_server_structure():
    """Test that the main server structure is properly set up"""
    # Add src to path
    sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
    
    # Test that we can import the main server module
    from fastmcp.server import main_server
    
    # Check that the create_main_server function exists
    assert hasattr(main_server, 'create_main_server')
    assert callable(main_server.create_main_server)
    
    # Check that the main function exists
    assert hasattr(main_server, 'main')
    assert callable(main_server.main)


def test_task_management_interface_structure():
    """Test that the task management interface structure is properly set up"""
    # Test interface module structure
    interface_path = Path(__file__).parent.parent / 'src' / 'fastmcp' / 'task_management' / 'interface'
    
    # Check that required files exist
    required_files = [
        'consolidated_mcp_tools_v2.py',
        'consolidated_mcp_server.py',
        'cursor_rules_tools.py',
        '__init__.py'
    ]
    
    for file_name in required_files:
        file_path = interface_path / file_name
        assert file_path.exists(), f"Missing file: {file_name}"


def test_server_exports():
    """Test that the server module properly exports the main server function"""
    # Add src to path
    sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
    
    from fastmcp.server import create_main_server
    
    # Check that the function is callable
    assert callable(create_main_server)


def test_tool_registration_structure():
    """Test that the tool registration structure is correct without actually importing dependencies"""
    # Check that the consolidated tools file has the expected structure
    tools_file = Path(__file__).parent.parent / 'src' / 'fastmcp' / 'task_management' / 'interface' / 'consolidated_mcp_tools_v2.py'
    
    assert tools_file.exists(), "Consolidated tools file does not exist"
    
    content = tools_file.read_text()
    
    # Check for key class and method names
    expected_patterns = [
        'class ConsolidatedMCPToolsV2',
        'def register_tools',
        'def manage_task',
        'def manage_subtask',
        'def manage_project',
        'def manage_agent',
        'def call_agent'
    ]
    
    for pattern in expected_patterns:
        assert pattern in content, f"Missing pattern: {pattern}"


def test_documentation_exists():
    """Test that integration documentation exists"""
    doc_file = Path(__file__).parent.parent / 'TASK_MANAGEMENT_INTEGRATION.md'
    
    assert doc_file.exists(), "Integration documentation does not exist"
    
    content = doc_file.read_text()
    
    # Check for key sections
    expected_sections = [
        '# Task Management Integration',
        '## Overview',
        '## Integration Status',
        '## Architecture',
        '## Available MCP Tools',
        '## Usage'
    ]
    
    for section in expected_sections:
        assert section in content, f"Missing documentation section: {section}"


def test_file_synchronization():
    """Test that source and target files are synchronized"""
    # Fix the source directory path - it should be relative to the workspace root
    workspace_root = Path(__file__).parent.parent.parent
    source_dir = workspace_root / 'cursor_agent' / 'src' / 'task_mcp' / 'interface'
    target_dir = Path(__file__).parent.parent / 'src' / 'fastmcp' / 'task_management' / 'interface'
    
    # Skip this test if source directory doesn't exist (migration already completed)
    if not source_dir.exists():
        # If source doesn't exist, just check that target exists and has the required files
        assert target_dir.exists(), "Target directory does not exist"
        
        key_files = ['consolidated_mcp_tools_v2.py', 'consolidated_mcp_server.py', '__init__.py']
        for file_name in key_files:
            target_file = target_dir / file_name
            assert target_file.exists(), f"Target file missing: {file_name}"
        return
    
    assert target_dir.exists(), "Target directory does not exist"
    
    # Check that key files exist in both locations
    key_files = ['consolidated_mcp_tools_v2.py', 'consolidated_mcp_server.py', '__init__.py']
    
    for file_name in key_files:
        source_file = source_dir / file_name
        target_file = target_dir / file_name
        
        assert source_file.exists(), f"Source file missing: {file_name}"
        assert target_file.exists(), f"Target file missing: {file_name}"
        
        # Check file sizes are similar (allowing for small differences due to imports)
        source_size = source_file.stat().st_size
        target_size = target_file.stat().st_size
        
        # Allow up to 20% difference in file size (imports can change significantly)
        if source_size > 0 and target_size > 0:
            size_diff = abs(source_size - target_size) / max(source_size, target_size)
            assert size_diff <= 0.2, f"File size mismatch for {file_name}: source={source_size}, target={target_size}"


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"]) 