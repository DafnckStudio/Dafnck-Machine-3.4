@echo off
echo Testing WSL bridge for MCP server...
echo.

echo 1. Testing basic WSL connectivity...
wsl.exe -d Ubuntu echo "WSL connection successful"

echo.
echo 2. Testing Python environment...
wsl.exe -d Ubuntu --cd /home/daihungpham/agentic-project/dhafnck_mcp_main bash -c "source .venv/bin/activate && python --version"

echo.
echo 3. Testing MCP server import...
wsl.exe -d Ubuntu --cd /home/daihungpham/agentic-project/dhafnck_mcp_main bash -c "source .venv/bin/activate && PYTHONPATH=/home/daihungpham/agentic-project/dhafnck_mcp_main/src python -c 'from fastmcp.task_management.interface.consolidated_mcp_server import mcp_instance; print(f\"MCP server loaded: {mcp_instance.name}\")'"

echo.
echo 4. Testing quick tool check...
wsl.exe -d Ubuntu --cd /home/daihungpham/agentic-project/dhafnck_mcp_main bash -c "./diagnostic_connect.sh --quick-test"

echo.
echo WSL bridge test complete!
pause 