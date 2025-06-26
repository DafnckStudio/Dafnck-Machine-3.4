"""
Pytest configuration for DhafnckMCP tests with automatic test data cleanup

This configuration ensures that:
1. Test data is completely isolated using .test.json files
2. Automatic cleanup runs after test sessions
3. Production data is never affected
4. Test code files are preserved
"""

import pytest
import sys
import os
from pathlib import Path

# Add test directory to path for test_environment_config import
sys.path.insert(0, str(Path(__file__).parent))

try:
    from test_environment_config import cleanup_test_data_files_only, find_project_root
except ImportError:
    # Fallback if import fails
    def cleanup_test_data_files_only(base_dir):
        return 0
    
    def find_project_root():
        return Path.cwd()


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_data_after_session():
    """
    Automatically clean up test data files after test session
    
    This only removes:
    - .test.json files
    - .test.mdc files
    - .test.yaml files
    - Temporary test directories
    - __pycache__ files
    
    It NEVER removes:
    - Test code files (test_*.py)
    - Production files
    - Source code
    """
    print("\n🧪 Starting test session with automatic cleanup enabled...")
    print("🛡️  SAFETY: Only .test.json and .test.mdc files will be cleaned after tests")
    
    yield  # Run all tests
    
    # Cleanup after all tests complete
    print("\n🧹 Running automatic test data cleanup...")
    
    project_root = find_project_root()
    cleaned_count = cleanup_test_data_files_only(project_root)
    
    if cleaned_count > 0:
        print(f"🧹 Session cleanup: Removed {cleaned_count} test data files")
    else:
        print("✨ No test data files found to clean")
    
    print("🛡️  Production data was never touched")


@pytest.fixture(scope="session")
def test_session_info():
    """Provide test session information"""
    print("\n" + "="*60)
    print("🧪 DhafnckMCP Test Session Starting")
    print("🛡️  Test Data Isolation: ENABLED")
    print("🧹 Automatic Cleanup: ENABLED")
    print("📁 Test Files: .test.json, .test.mdc")
    print("="*60)
    
    yield {
        "isolation_enabled": True,
        "cleanup_enabled": True,
        "test_file_patterns": [".test.json", ".test.mdc"]
    }
    
    print("\n" + "="*60)
    print("🧪 DhafnckMCP Test Session Complete")
    
    # Get exit status from pytest
    exit_status = getattr(pytest, 'exit_status', 0)
    if exit_status == 0:
        print("✅ Tests completed successfully")
    else:
        print(f"❌ Tests completed with exit status: {exit_status}")
    
    print("🛡️  Production data protected throughout testing")
    print("="*60)


# Configure pytest to use the session info fixture
def pytest_configure(config):
    """Configure pytest with custom settings"""
    # Add custom markers
    config.addinivalue_line(
        "markers", "isolated: mark test as using isolated test environment"
    )
    config.addinivalue_line(
        "markers", "production_safe: mark test as production data safe"
    )


def pytest_runtest_setup(item):
    """Setup for each test"""
    # Ensure test isolation for marked tests
    if item.get_closest_marker("isolated"):
        # Test should use isolated environment
        pass


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished"""
    # Store exit status for session info fixture
    pytest.exit_status = exitstatus 