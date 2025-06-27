# 🚀 Getting Started with DhafnckMCP

Quick start guide to get DhafnckMCP running in 5 minutes.

## ⚡ 5-Minute Quick Start

### 1. Choose Your Installation Method

#### Option A: Docker (Recommended for beginners)
```bash
git clone https://github.com/dhafnck/dhafnck_mcp.git
cd dhafnck_mcp_main
docker-compose up -d --build
```

#### Option B: Python (For developers)
```bash
git clone https://github.com/dhafnck/dhafnck_mcp.git
cd dhafnck_mcp_main
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
pip install -e .
```

### 2. Verify Installation
```bash
# Test the server
./diagnose_mcp_connection.sh

# Expected: ✅ DhafnckMCP Server is healthy
```

### 3. Configure Cursor IDE

Create `.cursor/mcp.json` in your project:

**Linux/Mac:**
```json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "python",
      "args": ["-m", "fastmcp.server.mcp_entry_point"],
      "cwd": "/path/to/dhafnck_mcp_main",
      "env": {
        "PYTHONPATH": "/path/to/dhafnck_mcp_main/src"
      }
    }
  }
}
```

**Windows (WSL):**
```json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "wsl.exe",
      "args": [
        "--cd", "/home/username/dhafnck_mcp_main",
        "--exec", "/home/username/dhafnck_mcp_main/.venv/bin/python",
        "-m", "fastmcp.server.mcp_entry_point"
      ]
    }
  }
}
```

### 4. Test in Cursor

1. Restart Cursor IDE
2. Open chat (Ctrl+L)
3. Try: `@dhafnck_mcp create a test task`

## 🎯 What You Can Do Now

### Task Management
```
@dhafnck_mcp create a task to implement user login
@dhafnck_mcp list all tasks
@dhafnck_mcp mark task as completed
```

### Agent Collaboration
```
@coding_agent help me implement this function
@system_architect_agent review this design
@test_orchestrator_agent create tests for this
```

### Project Management
```
@dhafnck_mcp create project "My Web App"
@dhafnck_mcp show project status
```

## 📖 Next Steps

1. **Read Full Guides**:
   - [User Guide](./USER_GUIDE.md) - Complete feature overview
   - [Docker Setup](./DOCKER_SETUP_GUIDE.md) - Production deployment
   - [Cursor Integration](./CURSOR_INTEGRATION_GUIDE.md) - Advanced IDE setup

2. **Explore Features**:
   - Multi-agent system with 50+ specialized agents
   - Task dependencies and subtasks
   - Project-specific configurations
   - Automated documentation generation

3. **Join Community**:
   - GitHub discussions
   - Discord server
   - Documentation contributions

## 🆘 Need Help?

### Common Issues

**Server won't start?**
```bash
# Check Python environment
which python
pip list | grep fastmcp

# Reinstall if needed
pip install -e . --force-reinstall
```

**Cursor can't connect?**
```bash
# Check MCP configuration
cat .cursor/mcp.json

# Test server manually
python -m fastmcp.server.mcp_entry_point
```

**WSL issues on Windows?**
- Ensure WSL2 is installed
- Use full paths in MCP configuration
- Check [WSL Troubleshooting Guide](./WSL_MCP_TROUBLESHOOTING_GUIDE.md)

### Resources

- 📖 [Complete Documentation](./USER_GUIDE.md)
- 🐛 [GitHub Issues](https://github.com/dhafnck/dhafnck_mcp/issues)
- 💬 [Community Discord](#)
- 📺 [Video Tutorials](#)

---

**Welcome to DhafnckMCP!** 🎉  
You're now ready to supercharge your development workflow with AI-powered task management and multi-agent collaboration. 