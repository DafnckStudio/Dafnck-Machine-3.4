import os
from pathlib import Path
import pytest
from fastmcp.tools.tool_path import find_project_root


def test_find_project_root_from_this_file():
    # Should find the project root from this test file
    project_root = find_project_root()
    assert (project_root / "pyproject.toml").exists() or (project_root / ".git").exists(), (
        f"Project root {project_root} does not contain pyproject.toml or .git"
    )
    # Should be an ancestor of this file
    assert Path(__file__).resolve().is_relative_to(project_root)


def test_find_project_root_from_custom_path():
    # Try from a known subdirectory (e.g., tests/tools)
    subdir = Path(__file__).parent
    project_root = find_project_root(subdir)
    assert (project_root / "pyproject.toml").exists() or (project_root / ".git").exists(), (
        f"Project root {project_root} does not contain pyproject.toml or .git"
    )
    assert subdir.resolve().is_relative_to(project_root)


def test_find_project_root_from_project_root():
    # Try from the project root itself
    project_root = find_project_root(Path.cwd())
    assert (project_root / "pyproject.toml").exists() or (project_root / ".git").exists(), (
        f"Project root {project_root} does not contain pyproject.toml or .git"
    )
    # Should be self or ancestor
    assert Path.cwd().resolve().is_relative_to(project_root) or Path.cwd().resolve() == project_root 