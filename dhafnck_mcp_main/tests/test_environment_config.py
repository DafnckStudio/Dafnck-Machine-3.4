"""
Test Environment Configuration System

This module provides complete isolation of test data from production data.
All test files use .test.json suffix to prevent interference with production data.
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
from contextlib import contextmanager


class IsolatedTestEnvironmentConfig:
    """Configuration for isolated test environment"""
    
    def __init__(self, test_id: Optional[str] = None):
        """
        Initialize test environment configuration
        
        Args:
            test_id: Unique identifier for this test session
        """
        self.test_id = test_id or f"test_{os.getpid()}"
        self.temp_dir = Path(tempfile.mkdtemp(prefix=f"dhafnck_test_{self.test_id}_"))
        
        # Add workspace_root attribute for compatibility
        self.workspace_root = find_project_root()
        
        # Create test file paths with .test.json suffix
        self.test_files = {
            "projects": self.temp_dir / "projects.test.json",
            "tasks": self.temp_dir / "tasks.test.json", 
            "auto_rule": self.temp_dir / "auto_rule.test.mdc",
            "agents": self.temp_dir / "agents.test.json",
            "subtasks": self.temp_dir / "subtasks.test.json"
        }
        
        # Initialize test files with empty structures
        self._initialize_test_files()
    
    def _initialize_test_files(self):
        """Initialize test files with proper empty structures"""
        # Initialize JSON files
        for file_key in ["projects", "tasks", "agents", "subtasks"]:
            with open(self.test_files[file_key], 'w') as f:
                json.dump({}, f, indent=2)
        
        # Initialize markdown file
        with open(self.test_files["auto_rule"], 'w') as f:
            f.write("# Test Auto Rule Configuration\n\nThis is a test configuration file.\n")
    
    def add_test_project(self, project_id: str, name: str, description: str = "Test project"):
        """Add a test project to the isolated environment"""
        projects_file = self.test_files["projects"]
        
        with open(projects_file, 'r') as f:
            data = json.load(f)
        
        data[project_id] = {
            "name": name,
            "description": description,
            "test_environment": True,
            "created_at": "2025-01-01T00:00:00Z",
            "task_trees": {
                "main": {
                    "name": "Main task tree",
                    "description": "Main task tree"
                }
            }
        }
        
        with open(projects_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def cleanup(self):
        """Clean up temporary test directory"""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)


def find_project_root() -> Path:
    """Find the project root directory"""
    current = Path.cwd()
    
    # Look for common project indicators
    indicators = ['.git', 'pyproject.toml', 'setup.py', 'requirements.txt']
    
    while current != current.parent:
        if any((current / indicator).exists() for indicator in indicators):
            return current
        current = current.parent
    
    # Fallback to current directory
    return Path.cwd()


def is_test_data_file(file_path: Path) -> bool:
    """
    Check if a file is a TEST DATA file (not test code files)
    
    This function is VERY specific to only target actual test data files,
    NOT test code files like test_*.py
    """
    file_str = str(file_path)
    file_name = file_path.name
    
    # ONLY target specific test data file patterns
    test_data_patterns = [
        '.test.json',      # Test data files
        '.test.mdc',       # Test markdown config files
        '.test.yaml',      # Test YAML files
        '.test.yml',       # Test YAML files
    ]
    
    # Check for explicit test data patterns
    if any(pattern in file_name for pattern in test_data_patterns):
        return True
    
    # Target specific temporary test directories
    if 'dhafnck_test_' in file_str:
        return True
    
    # Target __pycache__ files only (compiled Python)
    if '__pycache__' in file_str and file_name.endswith('.pyc'):
        return True
    
    # DO NOT target actual test code files (test_*.py)
    return False


def cleanup_test_data_files_only(base_dir: Path) -> int:
    """
    Safely clean up ONLY test DATA files, never test code or production files
    
    This function is specifically designed to only remove:
    - Files with .test.json, .test.mdc, .test.yaml extensions
    - Temporary test directories
    - Compiled Python cache files (.pyc)
    
    It will NEVER remove:
    - Test code files (test_*.py)
    - Production files
    - Source code
    
    Returns:
        Number of files cleaned up
    """
    cleaned_count = 0
    
    if not base_dir.exists():
        return 0
    
    # Find all test DATA files (not test code files)
    for file_path in base_dir.rglob("*"):
        if file_path.is_file() and is_test_data_file(file_path):
            try:
                file_path.unlink()
                print(f"🧹 Removed test data file: {file_path}")
                cleaned_count += 1
            except Exception as e:
                print(f"⚠️  Could not remove test data file {file_path}: {e}")
    
    return cleaned_count


@contextmanager
def isolated_test_environment(test_id: Optional[str] = None):
    """
    Context manager for completely isolated test environment
    
    Usage:
        with isolated_test_environment("my_test") as config:
            # Use config.test_files["projects"] etc.
            # All files have .test.json suffix
            pass
    """
    config = IsolatedTestEnvironmentConfig(test_id)
    
    try:
        yield config
    finally:
        config.cleanup()


# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing isolated test environment...")
    
    # Test 1: Create isolated environment
    with isolated_test_environment(test_id="demo_test") as config:
        print(f"✅ Created test environment: {config.temp_dir}")
        print(f"📁 Projects file: {config.test_files['projects']}")
        
        # Verify files exist and have correct naming
        assert config.test_files['projects'].name == 'projects.test.json'
        assert config.test_files['tasks'].name == 'tasks.test.json'
        assert config.test_files['auto_rule'].name == 'auto_rule.test.mdc'
        
        # Add test project
        config.add_test_project('demo_project', 'Demo Test Project')
        
        # Verify project was added
        with open(config.test_files['projects'], 'r') as f:
            data = json.load(f)
        
        assert 'demo_project' in data
        assert data['demo_project']['test_environment'] == True
        
        print("✅ Test project added successfully")
    
    print("✅ Test environment cleaned up automatically")
    
    # Test 2: Verify cleanup function
    test_dir = Path(tempfile.mkdtemp(prefix="cleanup_test_"))
    
    # Create some test data files and production files
    (test_dir / "test_file.test.json").write_text("{}")
    (test_dir / "production_file.json").write_text("{}")
    (test_dir / "another.test.mdc").write_text("# Test")
    (test_dir / "test_code.py").write_text("# This is test code")  # Should NOT be removed
    
    # Run cleanup
    cleaned = cleanup_test_data_files_only(test_dir)
    
    # Verify only test DATA files were removed, not test CODE files
    assert not (test_dir / "test_file.test.json").exists()
    assert not (test_dir / "another.test.mdc").exists()
    assert (test_dir / "production_file.json").exists()  # Should still exist
    assert (test_dir / "test_code.py").exists()  # Should still exist (test code)
    assert cleaned == 2
    
    # Cleanup test directory
    shutil.rmtree(test_dir)
    
    print("✅ Cleanup function works correctly")
    print("🎉 All tests passed!") 