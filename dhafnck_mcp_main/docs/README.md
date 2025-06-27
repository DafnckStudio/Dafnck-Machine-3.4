# 📚 DhafnckMCP Documentation

Welcome to the comprehensive documentation for DhafnckMCP - your cloud-scale MCP server for task management, agent orchestration, and project management.

## 🚀 Quick Navigation

### New Users - Start Here!
- **[Getting Started](./GETTING_STARTED.md)** - 5-minute quick start guide
- **[User Guide](./USER_GUIDE.md)** - Complete feature overview and usage guide

### Setup & Installation
- **[Docker Setup Guide](./DOCKER_SETUP_GUIDE.md)** - Production-ready Docker deployment
- **[Cursor Integration Guide](./CURSOR_INTEGRATION_GUIDE.md)** - Complete Cursor IDE integration

### Existing Documentation
- **[Installation Guide](./getting-started/installation.mdx)** - Detailed installation instructions
- **[Quick Start](./getting-started/quickstart.mdx)** - Basic usage examples
- **[Welcome Guide](./getting-started/welcome.mdx)** - Introduction to DhafnckMCP

## 📖 Documentation Structure

### 🎯 Getting Started (New Users)

| Document | Description | Time to Read |
|----------|-------------|--------------|
| [Getting Started](./GETTING_STARTED.md) | Fastest way to get running | 5 minutes |
| [User Guide](./USER_GUIDE.md) | Comprehensive feature guide | 20 minutes |

### 🛠️ Setup & Configuration

| Document | Description | Best For |
|----------|-------------|----------|
| [Docker Setup Guide](./DOCKER_SETUP_GUIDE.md) | Complete Docker deployment | Production, beginners |
| [Cursor Integration Guide](./CURSOR_INTEGRATION_GUIDE.md) | IDE integration setup | Developers using Cursor |

### 🔧 Specialized Guides

| Document | Description | Use Case |
|----------|-------------|----------|
| [WSL Troubleshooting Guide](../WSL_MCP_TROUBLESHOOTING_GUIDE.md) | Windows WSL issues | Windows users |
| [MCP Inspector Guide](../MCP_INSPECTOR_GUIDE.md) | Debugging MCP connections | Troubleshooting |
| [Project Setup Guide](../PROJECT_SPECIFIC_SETUP.md) | Multi-project configuration | Advanced users |

### 📋 Reference Documentation

| Document | Description | Reference Type |
|----------|-------------|----------------|
| [Task Manager Guide](../TASK_MANAGER_AGENT_GUIDE.md) | Task management features | Feature reference |
| [Architecture Documentation](../.cursor/rules/technical_architect/) | Cloud scaling architecture | Technical specs |
| [Agent Configurations](../yaml-lib/) | Available AI agents | Agent reference |

## 🎯 Choose Your Path

### I'm New to DhafnckMCP
1. Start with **[Getting Started](./GETTING_STARTED.md)** (5 min)
2. Read **[User Guide](./USER_GUIDE.md)** (20 min)
3. Set up **[Cursor Integration](./CURSOR_INTEGRATION_GUIDE.md)** (10 min)

### I Want to Deploy in Production
1. Read **[Docker Setup Guide](./DOCKER_SETUP_GUIDE.md)**
2. Review **[Architecture Documentation](../.cursor/rules/technical_architect/)**
3. Set up monitoring and backups

### I'm Having Issues
1. Check **[Troubleshooting Section](./USER_GUIDE.md#troubleshooting)** in User Guide
2. For WSL issues: **[WSL Troubleshooting Guide](../WSL_MCP_TROUBLESHOOTING_GUIDE.md)**
3. For MCP issues: **[MCP Inspector Guide](../MCP_INSPECTOR_GUIDE.md)**

### I Want to Understand the Architecture
1. Review **[Architecture Overview](../README.md#architecture-documentation)**
2. Read **[Phase Documentation](../.cursor/rules/technical_architect/)**
3. Explore **[Implementation Roadmap](../.cursor/rules/technical_architect/phase_09.mdc)**

## 🔍 What's New in This Documentation

### Recently Added (Day 3-4: Documentation & Getting Started Guide)

✅ **[User Guide](./USER_GUIDE.md)** - Comprehensive user documentation  
✅ **[Docker Setup Guide](./DOCKER_SETUP_GUIDE.md)** - Enhanced Docker instructions  
✅ **[Cursor Integration Guide](./CURSOR_INTEGRATION_GUIDE.md)** - Complete Cursor setup  
✅ **[Getting Started](./GETTING_STARTED.md)** - Quick start reference  

### Key Improvements

- **Unified Documentation**: All essential information in one place
- **Step-by-Step Guides**: Clear, actionable instructions
- **Troubleshooting**: Comprehensive problem-solving guides
- **Multi-Platform Support**: Windows (WSL), macOS, and Linux instructions
- **Production Ready**: Docker deployment with security best practices

## 🚀 Features Covered

### Core Functionality
- ✅ **Task Management**: Complete lifecycle with dependencies and subtasks
- ✅ **Multi-Agent System**: 50+ specialized AI agents for different domains
- ✅ **Project Management**: Multi-project support with hierarchical organization
- ✅ **Cursor Integration**: Native IDE integration for seamless workflow
- ✅ **Context Management**: Intelligent context synchronization and rule generation

### Advanced Features
- ✅ **Cloud-Scale Architecture**: Designed for 50 RPS to 1M+ RPS
- ✅ **Docker Deployment**: Production-ready containerization
- ✅ **WSL Support**: Complete Windows WSL2 integration
- ✅ **Multi-Project Setup**: Independent task management per project
- ✅ **Automated Workflows**: Agent coordination and task automation

## 🛠️ Installation Quick Reference

### Docker (Recommended)
```bash
git clone https://github.com/dhafnck/dhafnck_mcp.git
cd dhafnck_mcp_main
docker-compose up -d --build
```

### Python Virtual Environment
```bash
git clone https://github.com/dhafnck/dhafnck_mcp.git
cd dhafnck_mcp_main
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### Cursor MCP Configuration
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

## 🆘 Getting Help

### Self-Service Resources
1. **Search Documentation**: Use Ctrl+F to search within guides
2. **Check Troubleshooting**: Each guide has a troubleshooting section
3. **Use Diagnostic Tools**: Run `./diagnose_mcp_connection.sh`
4. **Test with MCP Inspector**: Interactive debugging tool

### Community Support
- 🐛 **GitHub Issues**: Report bugs and request features
- 💬 **Discord Community**: Real-time help and discussions  
- 📖 **Documentation**: Contribute improvements and corrections
- 🎥 **Video Tutorials**: Community-created learning resources

### Common Issues Quick Fix

| Issue | Quick Solution | Full Guide |
|-------|---------------|------------|
| Server won't start | `pip install -e . --force-reinstall` | [User Guide](./USER_GUIDE.md#troubleshooting) |
| Cursor can't connect | Check `.cursor/mcp.json` paths | [Cursor Guide](./CURSOR_INTEGRATION_GUIDE.md#troubleshooting) |
| WSL spawn errors | Use `wsl.exe` in MCP config | [WSL Guide](../WSL_MCP_TROUBLESHOOTING_GUIDE.md) |
| Docker issues | `docker-compose down && docker-compose up --build` | [Docker Guide](./DOCKER_SETUP_GUIDE.md#troubleshooting) |

## 📊 Documentation Statistics

- **Total Guides**: 8 comprehensive guides
- **Coverage**: Installation, setup, usage, troubleshooting, advanced configuration
- **Platforms**: Windows (WSL), macOS, Linux
- **Deployment**: Docker, Python virtual environment, production setups
- **Integration**: Cursor IDE, MCP protocol, multi-agent systems

## 🎯 Next Steps

1. **Start with [Getting Started](./GETTING_STARTED.md)** if you're new
2. **Bookmark this page** for easy navigation
3. **Join our community** for ongoing support
4. **Contribute** to help improve the documentation

---

**Welcome to DhafnckMCP!** 🚀  
Your journey to enhanced development productivity starts here.

*Last updated: Day 3-4 of Week 2 - Documentation & Getting Started Guide* 