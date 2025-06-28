# 🚀 Project-Specific Task & Project Management System

The DhafnckMCP system now supports **project-specific task management** that works with any project location, not just fixed paths. Each project can have its own independent task management system.

## 🎯 What This Solves

**Before**: Task management was tied to `/home/<username>/agentic-project`
**Now**: Each project has its own `.cursor/rules/` structure and can be located anywhere

## 📁 Project Structure

Each project will have its own independent structure:

```
<your-project>/
├── .cursor/
│   ├── mcp.json                    # MCP server configuration
│   ├── tool_config.json           # Tool configuration
│   └── rules/
│       ├── tasks/
│       │   ├── tasks.json          # Project-specific tasks
│       │   └── backup/             # Task backups
│       ├── brain/
│       │   └── projects.json       # Project management data
│       ├── agents/                 # Agent configurations
│       ├── auto_rule.mdc           # Auto-generated rules
│       └── main_objectif.mdc       # Project objectives
├── cursor_agent/                   # Optional: project-specific agents
└── dhafnck_mcp_main/              # Optional: local MCP server
```

## 🚀 Quick Setup

### Option 1: Automated Setup (Recommended)

```bash
# Navigate to your project
cd /path/to/your/project

# Run the setup script
python /path/to/dhafnck_mcp_main/setup_project_mcp.py

# Or specify a different project path
python /path/to/dhafnck_mcp_main/setup_project_mcp.py /path/to/another/project
```

### Option 2: Manual Setup

1. **Create directory structure**:
```bash
mkdir -p .cursor/rules/{tasks,brain,agents}
```

2. **Initialize files**:
```bash
echo '{"tasks": [], "metadata": {"version": "1.0.0"}}' > .cursor/rules/tasks/tasks.json
echo '{}' > .cursor/rules/brain/projects.json
```

3. **Copy MCP configuration template**:
```bash
cp dhafnck_mcp_main/mcp_project_template.json .cursor/mcp.json
# Edit the {{PROJECT_PATH}} placeholders
```

## 🔧 Configuration

### MCP Configuration (`.cursor/mcp.json`)

The system uses environment variables for dynamic path resolution:

```json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "wsl.exe",
      "args": [
        "--cd", "/path/to/your/project",
        "--exec", "/path/to/dhafnck_mcp_main/.venv/bin/python",
        "-m", "fastmcp.server.mcp_entry_point"
      ],
      "env": {
        "PROJECT_ROOT_PATH": ".",
        "TASKS_JSON_PATH": ".cursor/rules/tasks/tasks.json",
        "BRAIN_DIR_PATH": ".cursor/rules/brain",
        "AUTO_RULE_PATH": ".cursor/rules/auto_rule.mdc"
      }
    }
  }
}
```

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PROJECT_ROOT_PATH` | Project root directory | Current working directory |
| `TASKS_JSON_PATH` | Tasks database file | `.cursor/rules/tasks/tasks.json` |
| `BRAIN_DIR_PATH` | Brain directory | `.cursor/rules/brain` |
| `AUTO_RULE_PATH` | Auto-generated rules | `.cursor/rules/auto_rule.mdc` |
| `CURSOR_AGENT_DIR_PATH` | Agent configurations | `dhafnck_mcp_main/yaml-lib` |

## 🏗️ How It Works

### Dynamic Project Detection

The system automatically detects the project root using this priority order:

1. **Environment Variable**: `PROJECT_ROOT_PATH` if set
2. **Current Directory**: If it contains `.cursor/rules/` or `.git`
3. **Search Upwards**: Look for project markers (`.git`, `.cursor/rules/`, `package.json`, etc.)
4. **Fallback**: Current working directory

### Path Resolution

All paths are resolved relative to the detected project root:

```python
# Example: If project is at /home/user/my-project
# TASKS_JSON_PATH=".cursor/rules/tasks/tasks.json"
# Resolves to: /home/user/my-project/.cursor/rules/tasks/tasks.json
```

## 🎮 Usage Examples

### Setting Up Multiple Projects

```bash
# Project 1: Web Application
cd /home/user/webapp
python dhafnck_mcp_main/setup_project_mcp.py

# Project 2: Mobile App
cd /home/user/mobile-app  
python dhafnck_mcp_main/setup_project_mcp.py

# Project 3: Data Science Project
cd /home/user/data-science
python dhafnck_mcp_main/setup_project_mcp.py
```

Each project will have independent:
- Task databases
- Project configurations  
- Agent assignments
- Auto-generated rules

### Using MCP Tools

Once set up, use the same MCP tools in any project:

```python
# Create project-specific task
manage_task(
    action="create",
    title="Implement user authentication",
    description="Add JWT-based auth for this project",
    assignees=["@coding_agent"]
)

# Create project
manage_project(
    action="create", 
    project_id="webapp_v2",
    name="Web Application v2"
)
```

## 🔄 Migration from Fixed Path System

### For Existing Projects

If you have an existing project at `/home/<username>/agentic-project`:

1. **Backup existing data**:
```bash
cp -r .cursor/rules .cursor/rules.backup
```

2. **Run setup script**:
```bash
python dhafnck_mcp_main/setup_project_mcp.py
```

3. **Update MCP configuration**:
```bash
# The setup script will create new .cursor/mcp.json
# Restart Cursor to apply changes
```

### For New Projects

Simply run the setup script in any new project directory.

## 🛠️ Advanced Configuration

### Project-Specific Agent Libraries

You can have project-specific agent configurations:

```bash
# Copy agent library to project
cp -r dhafnck_mcp_main/yaml-lib ./cursor_agent

# The system will automatically use project-specific agents
# if cursor_agent/ directory exists in project root
```

### Custom Tool Configuration

Create `.cursor/tool_config.json` to enable/disable specific tools:

```json
{
  "enabled_tools": {
    "manage_task": true,
    "manage_project": true,
    "manage_agent": false,
    "call_agent": true
  },
  "debug_mode": false,
  "tool_logging": true
}
```

## 🚨 Troubleshooting

### Common Issues

1. **MCP Server Not Found**
   - Ensure dhafnck_mcp_main/.venv exists
   - Check paths in .cursor/mcp.json are correct
   - Restart Cursor completely

2. **Tasks Not Loading**
   - Verify .cursor/rules/tasks/tasks.json exists
   - Check file permissions
   - Validate JSON format

3. **Path Resolution Issues**
   - Set PROJECT_ROOT_PATH environment variable explicitly
   - Ensure project has .git or .cursor/rules/ directory
   - Check working directory when starting Cursor

### Debug Mode

Enable debug logging in .cursor/mcp.json:

```json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "debug": true,
      "env": {
        "DEBUG": "true"
      }
    }
  }
}
```

## 📚 API Reference

### Setup Script Options

```bash
python setup_project_mcp.py [OPTIONS] [PROJECT_PATH]

Options:
  PROJECT_PATH    Path to project (default: current directory)
  
Examples:
  python setup_project_mcp.py                    # Setup current directory
  python setup_project_mcp.py /path/to/project  # Setup specific project
```

### Environment Variables Reference

All environment variables support both absolute and relative paths. Relative paths are resolved from the project root.

## 🎉 Benefits

✅ **Project Independence**: Each project has its own task management
✅ **Portable**: Works with any project location  
✅ **Scalable**: Support multiple projects simultaneously
✅ **Backward Compatible**: Existing projects continue to work
✅ **Auto-Detection**: Intelligent project root detection
✅ **Flexible**: Customizable paths and configurations

## 📞 Support

If you encounter issues:

1. Check this documentation
2. Run the setup script again
3. Verify environment variables
4. Check Cursor logs for MCP errors
5. Ensure all paths exist and are accessible

---

**Ready to get started?** Run the setup script in your project directory! 🚀 