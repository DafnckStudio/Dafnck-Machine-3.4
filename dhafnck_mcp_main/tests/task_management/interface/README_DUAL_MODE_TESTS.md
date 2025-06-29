# Dual Mode Configuration Tests

This directory contains comprehensive tests for the dual-mode configuration system that allows the MCP server to run in both stdio (local Python) and HTTP (Docker) modes.

## Test Files

### `test_dual_mode_configuration.py`
Comprehensive test suite covering:
- Runtime mode detection
- Path resolution for both modes
- Environment configuration
- Project root detection
- Directory resolution

**Requirements**: Full project dependencies (pydantic, fastmcp, etc.)

### `test_manage_rule_integration.py`
Integration tests for the manage_rule functionality:
- CursorRulesTools integration with dual-mode config
- Rule file operations in both modes
- Settings file compatibility
- Error handling

**Requirements**: Full project dependencies

### `test_dual_mode_simple.py`
Lightweight tests that can run without complex dependencies:
- Basic import tests
- Mode detection logic
- Path resolution
- Convenience functions

**Requirements**: Minimal (only standard library + dual_mode_config)

### `conftest.py`
Pytest configuration and fixtures:
- Test environment setup
- Temporary directories
- Mock fixtures
- Custom assertions

### `run_dual_mode_tests.py`
Test runner script that:
- Runs tests in both stdio and HTTP modes
- Provides environment simulation
- Generates comprehensive reports

## Running Tests

### In Docker Environment (Recommended)

The Docker environment has all dependencies and simulates the production HTTP mode:

```bash
# Copy test file to container
docker cp tests/task_management/interface/test_dual_mode_simple.py dhafnck-mcp-server:/app/

# Run simple tests
docker exec dhafnck-mcp-server python3 /app/test_dual_mode_simple.py

# Run with pytest (if dependencies available)
docker exec dhafnck-mcp-server python3 -m pytest /app/test_dual_mode_simple.py -v
```

### In Local Environment

```bash
# Install dependencies first
pip install -e .

# Run simple tests (works without full dependencies)
python3 tests/task_management/interface/test_dual_mode_simple.py

# Run comprehensive tests (requires dependencies)
python3 tests/task_management/interface/run_dual_mode_tests.py

# Run with pytest
pytest tests/task_management/interface/ -v
```

### Mode-Specific Testing

```bash
# Test stdio mode explicitly
FASTMCP_TRANSPORT=stdio python3 test_dual_mode_simple.py

# Test HTTP mode explicitly  
FASTMCP_TRANSPORT=streamable-http python3 test_dual_mode_simple.py
```

## Test Structure

### TestDualModeConfig
Tests the core `DualModeConfig` class:
- `test_stdio_mode_detection()`: Default mode detection
- `test_http_mode_detection_*()`: Various HTTP mode triggers
- `test_project_root_detection_*()`: Project root resolution
- `test_rules_directory_*()`: Rules directory resolution
- `test_path_resolution_*()`: Path resolution logic
- `test_environment_config_*()`: Environment configuration

### TestCursorRulesToolsIntegration
Tests integration with CursorRulesTools:
- `test_rules_directory_resolution_*()`: Directory resolution
- `test_settings_file_fallback_*()`: Settings file compatibility
- `test_environment_override_*()`: Environment variable overrides

### TestRealWorldScenarios
Tests real-world usage patterns:
- `test_docker_development_scenario()`: Docker deployment
- `test_local_development_scenario()`: Local development
- `test_migration_compatibility()`: Legacy configuration support

## Expected Behavior

### Stdio Mode (Local Development)
- **Detection**: Default mode when no HTTP indicators present
- **Project Root**: Auto-detected from pyproject.toml, .git, etc.
- **Rules Directory**: `<project_root>/00_RULES`
- **Data Directory**: `<project_root>/data`
- **Settings**: Reads from `.cursor/settings.json` and `00_RULES/core/settings.json`

### HTTP Mode (Docker)
- **Detection**: Based on environment variables, Docker indicators
- **Project Root**: `/app`
- **Rules Directory**: `/data/rules`
- **Data Directory**: `/data`
- **Settings**: Uses environment variables, ignores settings files

## Environment Variables

### Mode Detection
- `FASTMCP_TRANSPORT=streamable-http`: Forces HTTP mode
- `CURSOR_RULES_DIR=/data/rules`: Indicates Docker HTTP mode
- `/.dockerenv` file presence: Docker container detection

### Path Overrides
- `PROJECT_ROOT_PATH`: Override project root detection
- `DOCUMENT_RULES_PATH`: Override rules directory (stdio mode only)

## Integration with CI/CD

### Docker Testing
```yaml
# Example GitHub Actions step
- name: Test Dual Mode in Docker
  run: |
    docker exec container python3 /app/test_dual_mode_simple.py
```

### Local Testing
```yaml
# Example GitHub Actions step
- name: Test Dual Mode Locally
  run: |
    pip install -e .
    python3 tests/task_management/interface/test_dual_mode_simple.py
```

## Troubleshooting

### Import Errors
- **Issue**: `ModuleNotFoundError: No module named 'pydantic'`
- **Solution**: Install dependencies with `pip install -e .` or use `test_dual_mode_simple.py`

### Path Resolution Issues
- **Issue**: Wrong rules directory detected
- **Solution**: Check environment variables and mode detection logic
- **Debug**: Print `dual_mode_config.runtime_mode` and `get_rules_directory()`

### Test Failures
- **Issue**: Tests fail in specific environment
- **Solution**: Check that environment matches expected mode
- **Debug**: Use `test_dual_mode_simple.py` for basic functionality verification

## Adding New Tests

When adding new tests:

1. **Choose appropriate file**:
   - Simple tests → `test_dual_mode_simple.py`
   - Integration tests → `test_manage_rule_integration.py`
   - Core functionality → `test_dual_mode_configuration.py`

2. **Use fixtures**:
   - `temp_project_dir`: Temporary project structure
   - `clean_env`: Clean environment variables
   - `mock_docker_env`: Mock Docker environment

3. **Test both modes**:
   - Always test stdio and HTTP modes
   - Use environment variable overrides
   - Mock external dependencies appropriately

4. **Follow patterns**:
   - Setup/teardown environment variables
   - Use descriptive test names
   - Include error case testing

## Configuration Examples

### Stdio Mode Configuration
```python
# Auto-detected in local environment
config = DualModeConfig()
assert config.runtime_mode == "stdio"
assert config.get_rules_directory() == Path("/path/to/project/00_RULES")
```

### HTTP Mode Configuration
```python
# In Docker environment
os.environ["FASTMCP_TRANSPORT"] = "streamable-http"
config = DualModeConfig()
assert config.runtime_mode == "http"
assert config.get_rules_directory() == Path("/data/rules")
```

This test suite ensures the dual-mode configuration system works reliably across different deployment scenarios while maintaining backward compatibility with existing configurations.