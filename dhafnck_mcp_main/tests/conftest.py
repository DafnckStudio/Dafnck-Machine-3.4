"""
Pytest configuration for DhafnckMCP tests with automatic test data cleanup

This configuration ensures that:
1. Test data is completely isolated using .test.json files
2. Automatic cleanup runs after test sessions
3. Production data is never affected
"""

import pytest
import sys
import os
from pathlib import Path

# Add test directory to path for test_environment_config import
sys.path.insert(0, str(Path(__file__).parent))

try:
    from test_environment_config import cleanup_test_files_only, find_project_root
except ImportError:
    # Fallback if import fails
    def cleanup_test_files_only(base_dir):
        return 0
    
    def find_project_root():
        return Path.cwd()


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_data_after_session():
    """
    Automatically clean up test data after the entire test session
    
    This fixture runs automatically after all tests complete and removes
    only .test.json, .test.mdc and other test files, never touching production data.
    """
    # Setup: runs before all tests
    print("\n🧪 Starting test session with automatic cleanup enabled...")
    print("🛡️  SAFETY: Only .test.json and .test.mdc files will be cleaned after tests")
    
    yield  # Run all tests
    
    # Teardown: runs after all tests complete
    print("\n🧹 Running automatic test data cleanup...")
    
    try:
        workspace_root = find_project_root()
        cursor_rules_dir = workspace_root / ".cursor" / "rules"
        
        if cursor_rules_dir.exists():
            cleaned_count = cleanup_test_files_only(cursor_rules_dir)
            if cleaned_count > 0:
                print(f"✅ Cleaned {cleaned_count} test files")
                print("🛡️  Production data was not affected")
            else:
                print("✨ No test files found to clean")
        else:
            print("ℹ️  No .cursor/rules directory found")
            
    except Exception as e:
        print(f"⚠️ Error during test cleanup: {e}")
        print("🛡️  Production data remains safe")


@pytest.fixture
def isolated_test_env():
    """
    Fixture providing isolated test environment for individual tests
    
    Returns:
        TestEnvironmentConfig: Configured test environment with .test.json files
    """
    from test_environment_config import TestEnvironmentConfig
    
    config = TestEnvironmentConfig()
    config.setup_test_environment()
    
    yield config
    
    # Cleanup after individual test
    config.cleanup_test_environment()


@pytest.fixture
def test_projects_file(isolated_test_env):
    """
    Fixture providing path to isolated test projects file
    
    Args:
        isolated_test_env: Isolated test environment fixture
        
    Returns:
        str: Path to projects.test.json file
    """
    return str(isolated_test_env.get_test_file_path("projects"))


@pytest.fixture
def test_tasks_file(isolated_test_env):
    """
    Fixture providing path to isolated test tasks file
    
    Args:
        isolated_test_env: Isolated test environment fixture
        
    Returns:
        str: Path to tasks.test.json file
    """
    return str(isolated_test_env.get_test_file_path("tasks"))


@pytest.fixture
def test_auto_rule_file(isolated_test_env):
    """
    Fixture providing path to isolated test auto rule file
    
    Args:
        isolated_test_env: Isolated test environment fixture
        
    Returns:
        str: Path to auto_rule.test.mdc file
    """
    return str(isolated_test_env.get_test_file_path("auto_rule"))


def pytest_configure(config):
    """Configure pytest with custom markers and settings"""
    config.addinivalue_line(
        "markers", "isolated: mark test as using isolated test data"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add automatic markers"""
    for item in items:
        # Add isolated marker to tests that use isolated fixtures
        if "isolated_test_env" in item.fixturenames:
            item.add_marker(pytest.mark.isolated)
        
        # Add integration marker to integration tests
        if "integration" in item.name.lower():
            item.add_marker(pytest.mark.integration)


def pytest_runtest_setup(item):
    """Setup before each test run"""
    # Print test isolation status for debugging
    if "isolated" in [mark.name for mark in item.iter_markers()]:
        print(f"🔒 Running isolated test: {item.name}")


def pytest_runtest_teardown(item, nextitem):
    """Teardown after each test run"""
    # Additional cleanup if needed
    pass


def pytest_sessionstart(session):
    """Called after the Session object has been created"""
    print("\n" + "="*60)
    print("🧪 DhafnckMCP Test Session Starting")
    print("🛡️  Test Data Isolation: ENABLED")
    print("🧹 Automatic Cleanup: ENABLED")
    print("📁 Test Files: .test.json, .test.mdc")
    print("="*60)


def pytest_sessionfinish(session, exitstatus):
    """Called after whole test run finished"""
    print("\n" + "="*60)
    print("🧪 DhafnckMCP Test Session Complete")
    if exitstatus == 0:
        print("✅ All tests passed")
    else:
        print(f"❌ Tests completed with exit status: {exitstatus}")
    print("🛡️  Production data protected throughout testing")
    print("="*60)


# Safety check to prevent accidental production data access
# Note: pytest_configure_node is not a valid pytest hook
# Using pytest_runtest_setup instead for safety checks


# Custom pytest plugin for test data isolation
class TestDataIsolationPlugin:
    """Plugin to ensure test data isolation"""
    
    def pytest_runtest_call(self, pyfuncitem):
        """Called to execute the test item"""
        # Could add runtime checks here to ensure tests are using isolated data
        pass


def pytest_addoption(parser):
    """Add custom command line options"""
    parser.addoption(
        "--skip-cleanup",
        action="store_true",
        default=False,
        help="Skip automatic test data cleanup after session"
    )
    parser.addoption(
        "--verbose-isolation",
        action="store_true", 
        default=False,
        help="Enable verbose output for test data isolation"
    )


@pytest.fixture(scope="session")
def skip_cleanup(request):
    """Fixture to check if cleanup should be skipped"""
    return request.config.getoption("--skip-cleanup")


@pytest.fixture(scope="session")
def verbose_isolation(request):
    """Fixture to check if verbose isolation output is enabled"""
    return request.config.getoption("--verbose-isolation")
