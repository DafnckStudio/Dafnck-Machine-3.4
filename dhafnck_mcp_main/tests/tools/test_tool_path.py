import os
from pathlib import Path
import pytest
from fastmcp.tools.tool_path import find_project_root


def test_find_project_root_from_this_file():
    # Should find the project root from this test file
    project_root = find_project_root()
    # After our fix, should prioritize .git directory and find the true project root
    assert (project_root / ".git").exists(), (
        f"Project root {project_root} should contain .git directory"
    )
    # Should also have the dhafnck_mcp_main subdirectory
    assert (project_root / "dhafnck_mcp_main").is_dir(), (
        f"Project root {project_root} should contain dhafnck_mcp_main directory"
    )
    # Should be an ancestor of this file
    assert Path(__file__).resolve().is_relative_to(project_root)


def test_find_project_root_from_custom_path():
    # Try from a known subdirectory (e.g., tests/tools)
    subdir = Path(__file__).parent
    project_root = find_project_root(subdir)
    # Should find the true project root with .git directory
    assert (project_root / ".git").exists(), (
        f"Project root {project_root} should contain .git directory"
    )
    assert subdir.resolve().is_relative_to(project_root)


def test_find_project_root_from_project_root():
    # Try from the project root itself - note that cwd is dhafnck_mcp_main
    project_root = find_project_root(Path.cwd())
    # Should find the true project root (parent of dhafnck_mcp_main)
    assert (project_root / ".git").exists(), (
        f"Project root {project_root} should contain .git directory"
    )
    # Should be ancestor of current working directory (dhafnck_mcp_main)
    assert Path.cwd().resolve().is_relative_to(project_root) 