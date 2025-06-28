# MCP Server Setup for Cursor

This guide provides step-by-step instructions for configuring the `dhafnck_mcp` server for use with Cursor.

## 1. Prerequisites

- You have successfully cloned the `dhafnck_mcp_main` repository.
- You have installed the project dependencies using `uv sync`.
- The Python virtual environment (`.venv`) is located in the `dhafnck_mcp_main` directory.

## 2. Configuration

Cursor uses a central configuration file to manage MCP servers. You need to add the configuration for this project to that file.

### Step 1: Locate your Cursor MCP configuration file

The file is located at `~/.cursor/mcp.json`. This is in your home directory, under the `.cursor` folder.

### Step 2: Add the server configuration

Open `~/.cursor/mcp.json` in a text editor. It will contain a JSON object. You need to add the `dhafnck_mcp` server configuration to this object.

Copy the entire content of the `mcp_config.json` file from this project and merge it into your `~/.cursor/mcp.json` file.

For your convenience, here is the required configuration:

```json
{
    "dhafnck_mcp": {
      "command": "/home/<username>/agentic-project/dhafnck_mcp_main/.venv/bin/python",
      "args": [
        "/home/<username>/agentic-project/dhafnck_mcp_main/src/fastmcp/task_management/interface/consolidated_mcp_server.py"
      ],
      "cwd": "/home/<username>/agentic-project/dhafnck_mcp_main",
      "env": {
        "PYTHONPATH": "/home/<username>/agentic-project/dhafnck_mcp_main/src"
      }
    }
}
```

**Important**: 
- If your `mcp.json` file already has other servers configured, simply add `dhafnck_mcp` as a new key to the main JSON object.
- The paths in this configuration are absolute and specific to the username `<username>`. If you are running this on a different machine or with a different username, you will need to update the paths accordingly.

## 3. Verification

After configuring `mcp.json`, you need to verify that Cursor can correctly connect to and use the MCP server.

### Step 1: Restart Cursor

To ensure that Cursor picks up the new configuration, it's best to restart the application.

### Step 2: Use the Diagnostic Tool

The `dhafnck_mcp` server comes with a built-in diagnostic tool. To use it, open an AI chat in Cursor and send the following message:

```
@dhafnck_mcp
```

Then, in a new message, call the `manage_project` tool with the `diagnostic` action:

```
manage_project(action="diagnostic")
```

If the server is running correctly, you should receive a response indicating that all 8 tools are registered and the system is operational.

### Step 3: Alternative Verification with MCP Inspector

You can also use the MCP Inspector to test the server connection. Run the following command in your terminal from the project root:

```bash
DANGEROUSLY_OMIT_AUTH=true npx @modelcontextprotocol/inspector .venv/bin/python src/fastmcp/task_management/interface/consolidated_mcp_server.py
```

This will launch a web interface (usually at `http://127.0.0.1:6274/#tools`) where you can see all the registered tools and interact with them.

## 4. Troubleshooting

If you encounter issues, please refer to the troubleshooting section in the [project's configuration guide](.cursor/rules/dhafnck_mcp_main/configuration.mdc). Common issues include incorrect paths in `mcp.json`, permission errors, or problems with the Python environment. 