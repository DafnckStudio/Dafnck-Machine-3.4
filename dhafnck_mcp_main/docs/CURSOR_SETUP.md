# Cursor Setup Guide for DhafnckMCP

This guide will help you set up DhafnckMCP with Cursor IDE for powerful AI-assisted development.

## Prerequisites

- [Cursor IDE](https://cursor.sh/) installed
- [Docker](https://docker.com/) installed and running
- A DhafnckMCP API token (generated from the web interface)

## Quick Setup

### 1. Generate Your API Token

1. Visit the [DhafnckMCP Dashboard](https://your-domain.com/dashboard)
2. Click "Generate Token"
3. Give your token a descriptive name
4. Copy both the token and the MCP configuration

### 2. Configure Cursor

#### Method 1: Using Cursor Settings UI

1. Open Cursor
2. Press `Cmd/Ctrl + ,` to open settings
3. Search for "MCP" in the settings search bar
4. Navigate to **Extensions → MCP**
5. Add your configuration to the MCP settings

#### Method 2: Direct File Configuration

1. Open your Cursor configuration directory:
   - **macOS**: `~/Library/Application Support/Cursor/User/`
   - **Windows**: `%APPDATA%\Cursor\User\`
   - **Linux**: `~/.config/Cursor/User/`

2. Create or edit the `mcp.json` file:

```json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "DHAFNCK_TOKEN=YOUR_TOKEN_HERE",
        "-v", "dhafnck-data:/data",
        "dhafnck/mcp-server:latest"
      ],
      "env": {
        "DHAFNCK_TOKEN": "YOUR_TOKEN_HERE"
      }
    }
  }
}
```

3. Replace `YOUR_TOKEN_HERE` with your actual API token

### 3. Start the MCP Server

The MCP server will start automatically when Cursor loads. You can also run it manually:

```bash
docker run -i --rm \
  -e DHAFNCK_TOKEN="YOUR_TOKEN_HERE" \
  -v dhafnck-data:/data \
  dhafnck/mcp-server:latest
```

### 4. Verify the Setup

1. Restart Cursor
2. Open a new chat session
3. You should see DhafnckMCP tools available
4. Try a simple command: "List available MCP tools"

## Available MCP Tools

Once configured, you'll have access to these powerful tools:

### Project Management
- **`manage_project`** - Create, update, and manage projects
- **`manage_task`** - Complete task lifecycle management
- **`manage_subtask`** - Break down complex tasks

### Agent Orchestration
- **`manage_agent`** - Multi-agent team management
- **`call_agent`** - Load specialized agent configurations

### Rule Management
- **`update_auto_rule`** - Update AI assistant context rules
- **`validate_rules`** - Validate rule file quality
- **`manage_cursor_rules`** - Complete rule file system management
- **`regenerate_auto_rule`** - Smart context generation
- **`validate_tasks_json`** - Task database integrity validation

## Usage Examples

### Create a New Project
```
Create a new project called "E-commerce Website" with task management
```

### Generate Development Tasks
```
Break down the login feature into development tasks with proper assignees
```

### Switch AI Agent Role
```
Switch to coding agent for implementing the authentication system
```

### Validate Project Structure
```
Validate the current project's task structure and rules
```

## Troubleshooting

### MCP Server Not Starting

1. **Check Docker**: Ensure Docker is running
   ```bash
   docker ps
   ```

2. **Verify Token**: Make sure your API token is valid
   ```bash
   docker run --rm -e DHAFNCK_TOKEN="YOUR_TOKEN" dhafnck/mcp-server:latest --validate-token
   ```

3. **Check Logs**: View container logs for errors
   ```bash
   docker logs dhafnck-mcp
   ```

### Tools Not Available in Cursor

1. **Restart Cursor**: Close and reopen Cursor completely
2. **Check Configuration**: Verify your `mcp.json` syntax is correct
3. **Permissions**: Ensure Docker has proper permissions

### Token Issues

1. **Invalid Token**: Generate a new token from the dashboard
2. **Expired Token**: Tokens don't expire, but check if it was revoked
3. **Wrong Format**: Ensure token is exactly as copied (no extra spaces)

## Advanced Configuration

### Custom Docker Network

If you need custom networking:

```json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--network", "your-network",
        "-e", "DHAFNCK_TOKEN=YOUR_TOKEN_HERE",
        "-v", "dhafnck-data:/data",
        "dhafnck/mcp-server:latest"
      ]
    }
  }
}
```

### Persistent Data Storage

For persistent data across container restarts:

```json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "DHAFNCK_TOKEN=YOUR_TOKEN_HERE",
        "-v", "/path/to/local/data:/data",
        "dhafnck/mcp-server:latest"
      ]
    }
  }
}
```

### Development Mode

For development with local code:

```json
{
  "mcpServers": {
    "dhafnck_mcp": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-e", "DHAFNCK_TOKEN=YOUR_TOKEN_HERE",
        "-e", "FASTMCP_LOG_LEVEL=DEBUG",
        "-v", "dhafnck-data:/data",
        "-v", "/path/to/project:/workspace",
        "dhafnck/mcp-server:latest"
      ]
    }
  }
}
```

## Security Best Practices

1. **Token Security**: Keep your API tokens secure and don't share them
2. **Regular Rotation**: Generate new tokens periodically
3. **Revoke Unused**: Revoke tokens you no longer need
4. **Network Isolation**: Use Docker networks for isolation if needed

## Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/dhafnck/dhafnck_mcp/issues)
- **Documentation**: [Complete documentation](https://github.com/dhafnck/dhafnck_mcp/docs)
- **Community**: [Join our Discord](https://discord.gg/dhafnck-mcp)

## Updates

To update to the latest version:

```bash
docker pull dhafnck/mcp-server:latest
```

The MCP server will automatically use the latest version on next restart.

---

**Need more help?** Open an issue on GitHub or reach out to our community! 