# 🚀 Production Deployment Guide

**FastMCP with Task Management System**  
**Migration Status**: Complete - `cursor_agent` → `dhafnck_mcp_main`

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Deployment Process](#deployment-process)
4. [Monitoring & Health Checks](#monitoring--health-checks)
5. [Rollback Procedures](#rollback-procedures)
6. [Troubleshooting](#troubleshooting)
7. [Post-Deployment Validation](#post-deployment-validation)

## 🔧 Prerequisites

### System Requirements
- **Python**: 3.10+ (tested on 3.10, 3.11, 3.12)
- **OS**: Linux (Ubuntu 20.04+), Windows 10+, macOS 11+
- **Memory**: Minimum 512MB, Recommended 2GB+
- **Disk**: Minimum 100MB free space

### Dependencies
- **uv**: Package manager (latest version)
- **Git**: Version control
- **pytest**: Testing framework
- **Coverage tools**: pytest-cov

### Environment Setup
```bash
# Install uv package manager
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
git clone <repository-url>
cd dhafnck_mcp_main

# Install dependencies
uv sync --locked
```

## ✅ Pre-Deployment Checklist

### Quality Gates
- [ ] **Test Coverage**: ≥95% (Current requirement)
- [ ] **Security Audit**: No critical vulnerabilities
- [ ] **Performance**: <5% regression from baseline
- [ ] **Integration Tests**: Pass on all supported platforms
- [ ] **Build Validation**: Package builds successfully

### Infrastructure Readiness
- [ ] Production environment configured
- [ ] Monitoring systems in place
- [ ] Backup procedures validated
- [ ] Rollback plan tested
- [ ] Documentation updated

### Security Verification
- [ ] Dependency scan completed (safety, bandit)
- [ ] SAST analysis passed (semgrep)
- [ ] Secrets management configured
- [ ] Access controls validated

## 🚀 Deployment Process

### Automated Deployment (Recommended)

#### Via GitHub Actions
```bash
# Trigger production deployment
gh workflow run "Production Deployment Pipeline" \
  --field deploy_to_production=true \
  --ref main
```

#### Manual Deployment Steps
```bash
# 1. Activate virtual environment
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 2. Run full test suite
uv run pytest --cov=src/fastmcp/task_management --cov-fail-under=95

# 3. Security audit
uv add --dev safety bandit
uv run safety check
uv run bandit -r src/

# 4. Build package
uv build

# 5. Validate package
uv add --dev twine
uv run twine check dist/*

# 6. Deploy to PyPI (production)
uv publish dist/* --token $PYPI_TOKEN
```

### Environment-Specific Deployment

#### Development Environment
```bash
# Install in development mode
uv sync --dev

# Run with development settings
export ENVIRONMENT=development
uv run python -m fastmcp.server.main_server
```

#### Staging Environment
```bash
# Install production dependencies
uv sync --locked

# Run with staging configuration
export ENVIRONMENT=staging
uv run python -m fastmcp.server.main_server
```

#### Production Environment
```bash
# Install locked dependencies only
uv sync --locked --no-dev

# Run with production configuration
export ENVIRONMENT=production
export LOG_LEVEL=INFO
uv run python -m fastmcp.server.main_server
```

## 📊 Monitoring & Health Checks

### Health Check Endpoints
```python
# Server health check
from fastmcp.server.main_server import create_main_server

server = create_main_server()
tools = server._mcp_list_tools()
print(f"✅ Server healthy: {len(tools)} tools registered")
```

### Key Metrics to Monitor
- **Server Startup Time**: Should be <5 seconds
- **Tool Registration**: All 10+ tools should be available
- **Memory Usage**: Monitor for leaks
- **Response Times**: Task operations <100ms
- **Error Rates**: <1% error rate acceptable

### Monitoring Commands
```bash
# Check server status
curl -f http://localhost:8000/health || echo "Server unhealthy"

# Monitor resource usage
ps aux | grep fastmcp
top -p $(pgrep -f fastmcp)

# Check logs
tail -f /var/log/fastmcp/server.log
```

## 🔄 Rollback Procedures

### Automated Rollback
```bash
# Rollback to previous version via GitHub
gh workflow run "Rollback Production" \
  --field target_version=v1.2.3

# Or via package manager
uv pip install fastmcp==1.2.3 --force-reinstall
```

### Manual Rollback Steps
```bash
# 1. Stop current service
systemctl stop fastmcp-server

# 2. Backup current state
cp -r /opt/fastmcp /opt/fastmcp.backup.$(date +%Y%m%d_%H%M%S)

# 3. Restore previous version
git checkout v1.2.3
uv sync --locked

# 4. Restart service
systemctl start fastmcp-server

# 5. Validate rollback
uv run pytest tests/integration/ -v
```

### Rollback Validation
- [ ] Server starts successfully
- [ ] All tools are registered
- [ ] Integration tests pass
- [ ] No data corruption
- [ ] Performance metrics stable

## 🔧 Troubleshooting

### Common Issues

#### Server Won't Start
```bash
# Check Python version
python --version  # Should be 3.10+

# Check dependencies
uv sync --locked

# Check for port conflicts
lsof -i :8000

# Check logs
tail -f logs/server.log
```

#### Tool Registration Failures
```bash
# Verify task management module
python -c "from fastmcp.task_management import ConsolidatedMCPToolsV2; print('✅ Module OK')"

# Check tool registration
python -c "
from fastmcp.server.main_server import create_main_server
server = create_main_server()
tools = server._mcp_list_tools()
print(f'Tools registered: {len(tools)}')
for tool in tools:
    print(f'  - {tool.name}')
"
```

#### Performance Issues
```bash
# Profile memory usage
uv add --dev memory-profiler
uv run python -m memory_profiler server_script.py

# Profile CPU usage
uv run python -m cProfile -o profile.stats server_script.py

# Analyze profile
python -c "
import pstats
p = pstats.Stats('profile.stats')
p.sort_stats('cumulative').print_stats(10)
"
```

### Error Codes & Solutions

| Error Code | Description | Solution |
|------------|-------------|----------|
| `IMPORT_ERROR` | Module import failure | Check Python path, reinstall dependencies |
| `TOOL_REG_FAIL` | Tool registration failed | Verify MCP server setup, check tool definitions |
| `DB_CONNECTION` | Database connection issue | Check file permissions, disk space |
| `CONFIG_ERROR` | Configuration error | Validate environment variables, config files |

## ✅ Post-Deployment Validation

### Functional Tests
```bash
# Run smoke tests
uv run pytest tests/smoke/ -v

# Test MCP tool functionality
python scripts/test_mcp_tools.py

# Validate task management operations
python scripts/validate_task_operations.py
```

### Performance Validation
```bash
# Run performance benchmarks
uv run pytest tests/performance/ --benchmark-only

# Load testing (if applicable)
# artillery run load-test.yml
```

### Security Validation
```bash
# Re-run security scans
uv run safety check
uv run bandit -r src/

# Verify no secrets in logs
grep -r "password\|token\|key" logs/ || echo "No secrets found"
```

## 📚 Additional Resources

### Documentation
- [API Reference](docs/api-reference.md)
- [Architecture Overview](docs/architecture.md)
- [Migration Guide](MIGRATION_GUIDE.md)
- [Troubleshooting Guide](docs/troubleshooting.md)

### Support Contacts
- **DevOps Team**: devops@company.com
- **Security Team**: security@company.com
- **On-Call**: +1-555-0123

### Monitoring Dashboards
- [System Health Dashboard](https://monitoring.company.com/fastmcp)
- [Performance Metrics](https://grafana.company.com/fastmcp)
- [Error Tracking](https://sentry.company.com/fastmcp)

## 🎯 Success Criteria

Deployment is considered successful when:

- [ ] **Server Health**: Server starts and responds within 5 seconds
- [ ] **Tool Availability**: All 10+ MCP tools are registered and functional
- [ ] **Test Coverage**: Maintains ≥95% test coverage
- [ ] **Performance**: No regression >5% from baseline
- [ ] **Security**: No critical vulnerabilities detected
- [ ] **Integration**: All dependent systems function normally
- [ ] **Monitoring**: All health checks pass
- [ ] **Documentation**: All guides updated and accessible

---

**Last Updated**: 2025-06-22  
**Version**: 1.0  
**Migration Phase**: Production Deployment (Phase 8) 