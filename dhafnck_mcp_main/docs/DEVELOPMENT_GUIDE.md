# Development Guide

## Development with Docker Live Reload

### Quick Setup

Your Docker setup now supports live code reloading for development. Here's how to use it:

```bash
# Navigate to the dhafnck_mcp_main directory
cd /home/daihungpham/agentic-project/dhafnck_mcp_main

# Use the development script
./scripts/dev-docker.sh start    # Start with live reload
./scripts/dev-docker.sh logs     # View logs
./scripts/dev-docker.sh test     # Run tests
./scripts/dev-docker.sh shell    # Open shell in container
./scripts/dev-docker.sh stop     # Stop development container
```

### How Live Reload Works

#### Current Setup
✅ **Source Code Mounting**: Your `src/` directory is mounted into the container  
✅ **Test Mounting**: Your `tests/` directory is mounted for in-container testing  
✅ **Rule Files**: Your `00_RULES/` directory is accessible in the container  
✅ **No Restart Required**: Code changes are immediately available in the container  

#### What's Mounted
```yaml
volumes:
  - ./src:/app/src:ro          # Source code (read-only)
  - ./tests:/app/tests:ro      # Tests (read-only) 
  - ../00_RULES:/data/rules/mounted:ro  # Rule files (read-only)
```

### Development Workflow

#### 1. Make Code Changes
Edit files in your local `src/` directory as usual:
```bash
# Edit any file in src/
vim src/fastmcp/dual_mode_config.py
vim src/fastmcp/task_management/interface/cursor_rules_tools.py
```

#### 2. Test Changes
```bash
# Option 1: Run tests in container
./scripts/dev-docker.sh test

# Option 2: Manual testing
./scripts/dev-docker.sh shell
# Inside container:
python3 -c "from fastmcp.dual_mode_config import get_runtime_mode; print(get_runtime_mode())"
```

#### 3. For Server Restart (if needed)
Some changes (like environment variables or server configuration) require a restart:
```bash
./scripts/dev-docker.sh restart
```

### Python Import Caching

**Important**: Python caches imports, so changes to already-imported modules won't show up immediately. For development:

#### For Testing New Code
```bash
# Restart Python process to reload all imports
./scripts/dev-docker.sh restart
```

#### For Web Server Auto-Reload
The FastAPI server can be configured for auto-reload in development mode. This is handled in the Docker entrypoint.

### Development vs Production

#### Development Mode
```bash
# docker-compose.yml with volume mounts enabled
- ./src:/app/src:ro
```
- ✅ Live code reloading
- ✅ Immediate testing
- ✅ No rebuild required
- ⚠️ Performance impact (file watching)

#### Production Mode
```bash
# docker-compose.yml with volume mounts disabled
# - ./src:/app/src:ro
```
- ✅ Better performance
- ✅ Immutable deployments
- ❌ Requires rebuild for changes

### Switching Between Modes

#### Enable Development Mode
```bash
# Edit docker-compose.yml
- ./src:/app/src:ro              # Uncomment this line
./scripts/dev-docker.sh restart
```

#### Enable Production Mode
```bash
# Edit docker-compose.yml  
# - ./src:/app/src:ro            # Comment this line
docker-compose restart
```

### Development Script Features

The `./scripts/dev-docker.sh` script provides:

```bash
./scripts/dev-docker.sh start     # Start with live reload
./scripts/dev-docker.sh stop      # Stop container
./scripts/dev-docker.sh restart   # Full restart
./scripts/dev-docker.sh logs      # View logs (add -f to follow)
./scripts/dev-docker.sh shell     # Interactive shell
./scripts/dev-docker.sh test      # Run development tests
./scripts/dev-docker.sh status    # Container health check
./scripts/dev-docker.sh clean     # Clean up dev environment
```

### Testing in Development

#### Quick Tests
```bash
./scripts/dev-docker.sh test
```

#### Full Test Suite
```bash
./scripts/dev-docker.sh shell
# Inside container:
python3 -m pytest /app/tests/ -v
```

#### Specific Tests
```bash
docker exec dhafnck-mcp-server python3 /app/tests/task_management/interface/test_dual_mode_simple.py
```

### Troubleshooting

#### Container Won't Start
```bash
./scripts/dev-docker.sh logs     # Check for errors
./scripts/dev-docker.sh clean    # Clean up and restart
```

#### Changes Not Showing
```bash
# Python import caching - restart to reload
./scripts/dev-docker.sh restart

# Check if volume is mounted correctly
./scripts/dev-docker.sh shell
ls -la /app/src/
```

#### Permission Issues
```bash
# Container runs as 'dhafnck' user
# Host files should be readable by container
ls -la src/
```

### Performance Considerations

#### Development Mode Impact
- File system watching overhead
- Slightly slower container startup
- Network latency for file access

#### Optimization Tips
- Use `.dockerignore` to exclude unnecessary files
- Consider using bind mounts vs. named volumes
- Disable volume mounts for production deployments

### Best Practices

#### Code Organization
- Keep changes small and testable
- Test in container before committing
- Use the dual-mode configuration for path handling

#### Git Workflow
```bash
# Make changes locally
vim src/fastmcp/some_file.py

# Test in development container
./scripts/dev-docker.sh test

# Commit when tests pass
git add src/fastmcp/some_file.py
git commit -m "feature: add new functionality"
```

#### Configuration Management
- Use environment variables for config
- Keep development/production configs separate
- Document configuration changes

### Integration with IDE

#### VS Code
The mounted volumes work with VS Code Remote-Containers:
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "/app/.venv/bin/python",
    "python.terminal.activateEnvironment": false
}
```

#### PyCharm
Configure Docker interpreter to point to the container's Python:
- Docker: `dhafnck-mcp-server`
- Python: `/app/.venv/bin/python`

### Deployment Considerations

When deploying to production:

1. **Disable Volume Mounts**: Comment out the development volume mounts
2. **Rebuild Image**: Ensure latest code is baked into the image
3. **Environment Variables**: Set production-specific environment variables
4. **Resource Limits**: Apply appropriate CPU/memory limits

```bash
# Production deployment
git pull origin main
docker-compose build
docker-compose up -d --no-deps dhafnck-mcp
```

This development setup provides the best of both worlds: fast iteration during development and reliable, immutable deployments in production.