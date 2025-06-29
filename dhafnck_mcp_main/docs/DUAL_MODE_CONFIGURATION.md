# Dual Mode Configuration Guide

## Overview

The DhafnckMCP server supports two runtime modes:
- **Stdio Mode**: Local Python execution for development and testing
- **HTTP Mode**: Docker containerized deployment for production

The system automatically detects the runtime environment and adapts path resolution accordingly.

## How It Works

### Automatic Mode Detection

The system detects the runtime mode based on:

1. **Environment Variables**:
   - `CURSOR_RULES_DIR`: Indicates Docker HTTP mode
   - `FASTMCP_TRANSPORT=streamable-http`: Indicates HTTP mode

2. **Container Detection**:
   - Presence of `/.dockerenv`: Docker container environment
   - `/app` directory without `/home`: Container file structure

3. **Default**: Falls back to stdio mode

### Path Resolution

#### HTTP Mode (Docker)
```
Project Root: /app
Rules Directory: /data/rules
Data Directory: /data
Config Directory: /app/config
Logs Directory: /app/logs
```

#### Stdio Mode (Local)
```
Project Root: <auto-detected from pyproject.toml, .git, etc.>
Rules Directory: <project_root>/00_RULES
Data Directory: <project_root>/data
Config Directory: <project_root>/config
Logs Directory: <project_root>/logs
```

## Configuration

### Environment Variables

#### For HTTP Mode (Docker)
```bash
FASTMCP_TRANSPORT=streamable-http
CURSOR_RULES_DIR=/data/rules
TASKS_JSON_PATH=/data/tasks
PROJECTS_FILE_PATH=/data/projects/projects.json
```

#### For Stdio Mode (Local)
```bash
# No special environment variables needed
# Paths are auto-detected from project structure
```

### Settings File Integration

The system maintains compatibility with existing `.cursor/settings.json` files:

- **HTTP Mode**: Uses Docker paths, ignores settings files
- **Stdio Mode**: Reads from:
  1. `00_RULES/core/settings.json`
  2. `.cursor/settings.json`
  3. Environment variables
  4. Default fallbacks

## Usage Examples

### Import and Use
```python
from fastmcp.dual_mode_config import (
    dual_mode_config,
    get_rules_directory,
    get_data_directory,
    is_http_mode,
    is_stdio_mode,
    resolve_path
)

# Get current mode
print(f"Runtime mode: {dual_mode_config.runtime_mode}")

# Get directories
rules_dir = get_rules_directory()
data_dir = get_data_directory()

# Resolve paths
config_path = resolve_path("my_config.json", "config")
```

### Environment Detection
```python
if is_http_mode():
    print("Running in Docker HTTP mode")
    # Use container-specific logic
elif is_stdio_mode():
    print("Running in local stdio mode")
    # Use local development logic
```

## Benefits

1. **Zero Configuration**: Works out of the box in both modes
2. **Settings Compatibility**: Doesn't require changes to existing `.cursor/settings.json`
3. **Automatic Detection**: No manual mode switching required
4. **Path Safety**: Prevents cross-mode path conflicts
5. **Development Friendly**: Easy testing in both environments

## Migration

### From Manual Path Configuration
```python
# Before (manual)
if os.environ.get("DOCKER_MODE"):
    rules_dir = "/data/rules"
else:
    rules_dir = "./00_RULES"

# After (automatic)
rules_dir = get_rules_directory()
```

### Settings File Updates
No changes needed to `.cursor/settings.json` - the system adapts automatically.

## Troubleshooting

### Rule Files Not Found
1. Check runtime mode detection: `dual_mode_config.runtime_mode`
2. Verify rules directory: `get_rules_directory()`
3. Ensure files exist in the correct location for your mode

### Path Resolution Issues
1. Use `resolve_path()` for all path operations
2. Check base directory type ("project", "rules", "data", etc.)
3. Verify environment variables in Docker mode

### Testing Both Modes
```bash
# Test stdio mode
python3 your_script.py

# Test HTTP mode (simulate Docker environment)
FASTMCP_TRANSPORT=streamable-http python3 your_script.py
```

## Implementation Details

The dual mode system is implemented in:
- `src/fastmcp/dual_mode_config.py`: Core configuration logic
- `src/fastmcp/task_management/interface/cursor_rules_tools.py`: Integration with rule management

The system maintains backward compatibility while providing automatic adaptation to different runtime environments.