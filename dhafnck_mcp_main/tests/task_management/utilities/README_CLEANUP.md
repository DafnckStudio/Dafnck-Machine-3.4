# Test Data Cleanup System

This directory contains utilities for automatically cleaning up test data created during test runs.

## Problem Solved

During test execution, various test files create projects and data that can accumulate in the system:
- E2E test projects (`e2e_project_1`, `e2e_querying_project_*`, etc.)
- Migration test projects (`migration_test_project`, `migration_workflow_test`)
- Auto-detection test projects (`test_auto_detect`, `test_from_tmp`)
- Basic test projects (`test_project`, `test_project2`, `test_project3`)

Without cleanup, these test projects clutter the system and can interfere with future tests.

## Components

### 1. `cleanup_test_data.py`
Main cleanup script that:
- ✅ Removes test projects from `.cursor/rules/brain/projects.json`
- ✅ Cleans up test task directories from `.cursor/rules/tasks/`
- ✅ Creates backups before making changes
- ✅ Uses comprehensive pattern matching to identify test projects
- ✅ Preserves production projects

**Test Project Detection Patterns:**
- **Exact matches**: `test_project`, `e2e_project_1`, `migration_test_project`, etc.
- **Regex patterns**: `e2e_querying_project_\d+`, `e2e_collaboration_project_\d+`
- **Name keywords**: Projects with "test", "e2e", "migration", "temp" in name
- **Path patterns**: Projects in `/tmp/` or containing "temp"
- **Test timestamps**: Projects with creation date `2025-01-01T00:00:00Z`
- **Description keywords**: Projects with test-related descriptions

### 2. `pytest_cleanup_plugin.py`
Pytest plugin that:
- ✅ Automatically runs cleanup after test sessions complete
- ✅ Handles cleanup even if tests fail or are interrupted
- ✅ Registers with pytest hook system
- ✅ Provides timeout protection (30s limit)
- ✅ Uses `atexit` for emergency cleanup

### 3. `test_cleanup_verification.py`
Verification script that:
- ✅ Tests the cleanup functionality
- ✅ Creates mock test data
- ✅ Verifies test projects are removed
- ✅ Ensures production projects are preserved
- ✅ Provides comprehensive test coverage

### 4. Integration with `conftest.py`
The main test configuration:
- ✅ Registers the cleanup plugin automatically
- ✅ Provides session-scoped cleanup fixtures
- ✅ Isolates test environments
- ✅ Handles fallback if plugin fails to load

## Usage

### Automatic Cleanup (Recommended)
The cleanup system runs automatically when you run pytest:

```bash
# Cleanup runs automatically after tests complete
pytest tests/task_management/

# Cleanup also runs if tests are interrupted (Ctrl+C)
```

### Manual Cleanup
You can also run cleanup manually:

```bash
# Run cleanup script directly
python tests/task_management/utilities/cleanup_test_data.py

# Test the cleanup functionality
python tests/task_management/utilities/test_cleanup_verification.py
```

## How It Works

### 1. Test Execution
- Tests create projects using `manage_project` MCP tool
- Projects are stored in `.cursor/rules/brain/projects.json`
- Task data is stored in `.cursor/rules/tasks/default_id/project_id/`

### 2. Automatic Detection
The cleanup system identifies test projects by:
- **Project ID patterns** (e.g., starts with "test_", "e2e_", contains timestamps)
- **Project names** (contains test keywords)
- **Creation timestamps** (hardcoded test dates)
- **File paths** (temporary directories)
- **Descriptions** (test-related content)

### 3. Safe Removal
- Creates backup before making changes
- Only removes projects matching test patterns
- Preserves all production projects
- Provides detailed logging of actions taken

### 4. Multiple Triggers
Cleanup runs:
- ✅ After pytest session completes normally
- ✅ When tests are interrupted (Ctrl+C)
- ✅ On Python process exit (atexit handler)
- ✅ When manually invoked

## Test Files Affected

The cleanup system handles test projects created by:

### E2E Tests (`test_e2e_journeys.py`)
- `e2e_project_1`
- `e2e_lifecycle_project`
- `e2e_querying_project_*` (with timestamps)
- `e2e_collaboration_project_*` (with timestamps)
- `e2e_dependency_project_*` (with timestamps)

### Migration Tests (`test_migration_integration.py`)
- `migration_test_project`
- `migration_workflow_test`

### Auto Rule Tests (`test_auto_rule_integration.py`)
- `test_project` (created for auto rule testing)

### Project Setup Tests
- `test_auto_detect`
- `test_from_tmp`
- `test_project2`
- `test_project3`

## Safety Features

### Production Project Protection
The cleanup system **NEVER** removes:
- `dhafnck_mcp_main` (main project)
- `chaxiaiv2` (production project)
- Any project without test patterns
- Projects with realistic creation dates
- Projects in production paths

### Backup System
- Creates `.json.backup` files before making changes
- Allows easy restoration if needed
- Preserves original data integrity

### Error Handling
- Graceful failure if files don't exist
- Timeout protection (30s limit)
- Detailed error reporting
- Continues operation even if individual steps fail

## Verification

Run the verification script to ensure cleanup works correctly:

```bash
python tests/task_management/utilities/test_cleanup_verification.py
```

Expected output:
```
🧪 Starting cleanup verification test...
🧪 Testing cleanup functionality...
📁 Created test projects file: /tmp/.../projects.json
📊 Initial projects count: 7
🔧 Running cleanup script...
✅ Cleanup script executed successfully
🧹 Starting comprehensive test data cleanup...
...
🧹 Cleaned 5 test project(s):
   - test_project
   - e2e_project_1
   - e2e_querying_project_1750925473
   - migration_test_project
   - test_auto_detect
📊 Projects before: 7, after: 2
✅ Production project 'dhafnck_mcp_main' preserved
✅ Production project 'chaxiaiv2' preserved
✅ Test project 'test_project' correctly removed
...
🎉 Cleanup verification PASSED!
✅ All cleanup tests PASSED!
```

## Troubleshooting

### Cleanup Not Running
If cleanup doesn't run automatically:
1. Check that the plugin is registered in `conftest.py`
2. Run manual cleanup: `python cleanup_test_data.py`
3. Verify pytest finds the plugin: `pytest --collect-only`

### Test Projects Not Removed
If test projects persist:
1. Check the project patterns in `cleanup_test_data.py`
2. Add new patterns for your test projects
3. Run verification script to test patterns

### Production Projects Removed
If production projects are accidentally removed:
1. Restore from `.json.backup` file
2. Review and fix the detection patterns
3. Add production project IDs to the safe list

## Adding New Test Projects

When creating new test files that generate projects:

1. **Use test-friendly naming**:
   ```python
   project_id = "test_my_feature"  # Will be auto-detected
   project_id = f"e2e_test_{int(time.time())}"  # Will be auto-detected
   ```

2. **Add cleanup patterns** if needed:
   ```python
   # In cleanup_test_data.py, add to test_project_patterns:
   "my_test_pattern",
   
   # Or add regex pattern:
   r"my_test_pattern_\d+",
   ```

3. **Test your patterns**:
   ```bash
   python test_cleanup_verification.py
   ```

## Best Practices

1. **Always use test-identifiable names** for test projects
2. **Use temporary directories** when possible for file-based tests
3. **Add cleanup verification** for new test patterns
4. **Document new test project patterns** in this README
5. **Test cleanup functionality** before committing new test files

This system ensures that test data doesn't accumulate and interfere with future test runs or production usage. 