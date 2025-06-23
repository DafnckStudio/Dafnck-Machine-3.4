#!/bin/bash

# =============================================================================
# MCP Server Diagnostic Script for WSL/Cursor/Claude Desktop
# =============================================================================
# This script diagnoses MCP server connection issues and provides detailed
# information about paths, configurations, and server status.
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/home/daihungpham/agentic-project"
DHAFNCK_MCP_DIR="$PROJECT_ROOT/dhafnck_mcp_main"
VENV_PATH="$DHAFNCK_MCP_DIR/.venv"
PYTHON_PATH="$VENV_PATH/bin/python"
SERVER_SCRIPT="$DHAFNCK_MCP_DIR/src/fastmcp/task_management/interface/consolidated_mcp_server.py"
TASKS_JSON_PATH="$PROJECT_ROOT/.cursor/rules/tasks/tasks.json"
BACKUP_PATH="$PROJECT_ROOT/.cursor/rules/tasks/backup"

echo -e "${PURPLE}=============================================================================${NC}"
echo -e "${PURPLE}               MCP SERVER DIAGNOSTIC TOOL FOR WSL/CURSOR                     ${NC}"
echo -e "${PURPLE}=============================================================================${NC}"
echo ""

# Function to print section headers
print_section() {
    echo -e "\n${CYAN}📋 $1${NC}"
    echo -e "${CYAN}$(printf '=%.0s' {1..60})${NC}"
}

# Function to check file/directory existence
check_path() {
    local path="$1"
    local description="$2"
    local required="$3"
    
    if [ -e "$path" ]; then
        echo -e "  ✅ ${GREEN}$description${NC}: $path"
        if [ -f "$path" ]; then
            echo -e "     📄 File size: $(stat -c%s "$path") bytes"
            echo -e "     🕒 Modified: $(stat -c%y "$path")"
        elif [ -d "$path" ]; then
            echo -e "     📁 Directory contents: $(ls -1 "$path" 2>/dev/null | wc -l) items"
        fi
    else
        if [ "$required" = "required" ]; then
            echo -e "  ❌ ${RED}$description${NC}: $path (MISSING - REQUIRED)"
        else
            echo -e "  ⚠️  ${YELLOW}$description${NC}: $path (MISSING - OPTIONAL)"
        fi
    fi
}

# Function to test server startup
test_server_startup() {
    local test_env="$1"
    local description="$2"
    
    echo -e "\n${BLUE}🧪 Testing server startup: $description${NC}"
    
    # Create temporary test script
    local test_script="/tmp/mcp_test_$$.py"
    cat > "$test_script" << 'EOF'
import sys
import os
import asyncio
import traceback
from pathlib import Path

# Add src to path
sys.path.insert(0, '/home/daihungpham/agentic-project/dhafnck_mcp_main/src')

try:
    from fastmcp.task_management.interface.consolidated_mcp_server import mcp_instance
    print("✅ Import successful")
    
    async def test_tools():
        try:
            tools = await mcp_instance.get_tools()
            print(f"✅ Tools loaded: {len(tools)} tools available")
            for i, tool in enumerate(tools[:5]):  # Show first 5 tools
                print(f"   {i+1}. {tool}")
            if len(tools) > 5:
                print(f"   ... and {len(tools) - 5} more tools")
            return True
        except Exception as e:
            print(f"❌ Error loading tools: {e}")
            traceback.print_exc()
            return False
    
    # Test tools
    success = asyncio.run(test_tools())
    
    if success:
        print("✅ Server test PASSED")
        sys.exit(0)
    else:
        print("❌ Server test FAILED")
        sys.exit(1)
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    traceback.print_exc()
    sys.exit(1)
EOF

    # Run test with specified environment
    local cmd="cd '$DHAFNCK_MCP_DIR' && source .venv/bin/activate && $test_env python '$test_script'"
    
    echo -e "  🔧 Command: $cmd"
    
    if eval "$cmd" 2>&1; then
        echo -e "  ✅ ${GREEN}Server startup test PASSED${NC}"
    else
        echo -e "  ❌ ${RED}Server startup test FAILED${NC}"
    fi
    
    # Cleanup
    rm -f "$test_script"
}

# Function to check process status
check_processes() {
    echo -e "\n${BLUE}🔍 Checking running processes${NC}"
    
    local mcp_processes=$(ps aux | grep -E "(consolidated_mcp_server|fastmcp)" | grep -v grep || true)
    if [ -n "$mcp_processes" ]; then
        echo -e "  ✅ ${GREEN}MCP server processes found:${NC}"
        echo "$mcp_processes" | while read line; do
            echo -e "     📊 $line"
        done
    else
        echo -e "  ⚠️  ${YELLOW}No MCP server processes running${NC}"
    fi
    
    local cursor_processes=$(ps aux | grep -E "(cursor|code)" | grep -v grep || true)
    if [ -n "$cursor_processes" ]; then
        echo -e "  ✅ ${GREEN}Cursor processes found:${NC}"
        echo "$cursor_processes" | while read line; do
            echo -e "     📊 $line"
        done
    else
        echo -e "  ⚠️  ${YELLOW}No Cursor processes running${NC}"
    fi
}

# Function to check Claude Desktop logs
check_claude_logs() {
    echo -e "\n${BLUE}📜 Checking Claude Desktop logs${NC}"
    
    # Common Claude Desktop log locations
    local log_locations=(
        "$HOME/.claude/logs"
        "$HOME/.config/claude/logs"
        "$HOME/.local/share/claude/logs"
        "$HOME/AppData/Roaming/Claude/logs"  # Windows path (might be accessible via WSL)
    )
    
    for log_dir in "${log_locations[@]}"; do
        if [ -d "$log_dir" ]; then
            echo -e "  ✅ ${GREEN}Claude logs found at:${NC} $log_dir"
            local recent_logs=$(find "$log_dir" -name "*.log" -type f -mtime -1 2>/dev/null | head -5)
            if [ -n "$recent_logs" ]; then
                echo -e "     📄 Recent log files:"
                echo "$recent_logs" | while read log_file; do
                    echo -e "        - $(basename "$log_file") ($(stat -c%s "$log_file") bytes, modified: $(stat -c%y "$log_file" | cut -d' ' -f1-2))"
                done
                
                # Show last few lines of most recent log
                local latest_log=$(find "$log_dir" -name "*.log" -type f -printf '%T@ %p\n' 2>/dev/null | sort -n | tail -1 | cut -d' ' -f2-)
                if [ -n "$latest_log" ]; then
                    echo -e "     📖 Last 10 lines of latest log ($latest_log):"
                    tail -10 "$latest_log" 2>/dev/null | while read line; do
                        echo -e "        $line"
                    done
                fi
            else
                echo -e "     ⚠️  No recent log files found"
            fi
        else
            echo -e "  ❌ ${RED}Claude logs not found at:${NC} $log_dir"
        fi
    done
}

# Function to validate MCP configuration
validate_mcp_config() {
    local config_file="$1"
    local description="$2"
    
    echo -e "\n${BLUE}🔧 Validating MCP configuration: $description${NC}"
    echo -e "  📁 Config file: $config_file"
    
    if [ ! -f "$config_file" ]; then
        echo -e "  ❌ ${RED}Configuration file not found${NC}"
        return 1
    fi
    
    echo -e "  ✅ ${GREEN}Configuration file exists${NC}"
    echo -e "  📄 File size: $(stat -c%s "$config_file") bytes"
    echo -e "  🕒 Modified: $(stat -c%y "$config_file")"
    
    # Validate JSON syntax
    if python3 -m json.tool "$config_file" > /dev/null 2>&1; then
        echo -e "  ✅ ${GREEN}JSON syntax is valid${NC}"
    else
        echo -e "  ❌ ${RED}JSON syntax is invalid${NC}"
        echo -e "  🔍 JSON validation error:"
        python3 -m json.tool "$config_file" 2>&1 | head -5 | while read line; do
            echo -e "     $line"
        done
        return 1
    fi
    
    # Check for task_management server
    if grep -q '"task_management"' "$config_file"; then
        echo -e "  ✅ ${GREEN}task_management server found in config${NC}"
        
        # Extract and validate task_management configuration
        echo -e "  🔍 task_management configuration:"
        python3 -c "
import json
with open('$config_file', 'r') as f:
    config = json.load(f)
    
if 'mcpServers' in config and 'task_management' in config['mcpServers']:
    tm_config = config['mcpServers']['task_management']
    print(f'     Command: {tm_config.get(\"command\", \"NOT SET\")}')
    print(f'     Args: {tm_config.get(\"args\", \"NOT SET\")}')
    print(f'     CWD: {tm_config.get(\"cwd\", \"NOT SET\")}')
    print(f'     Env vars: {len(tm_config.get(\"env\", {}))} variables')
    
    # Validate paths
    import os
    command = tm_config.get('command', '')
    if os.path.exists(command):
        print(f'     ✅ Command path exists: {command}')
    else:
        print(f'     ❌ Command path missing: {command}')
        
    cwd = tm_config.get('cwd', '')
    if os.path.exists(cwd):
        print(f'     ✅ Working directory exists: {cwd}')
    else:
        print(f'     ❌ Working directory missing: {cwd}')
        
    # Check environment variables
    env = tm_config.get('env', {})
    for key, value in env.items():
        print(f'     🌍 {key}={value}')
        if key.endswith('_PATH') and value:
            if os.path.exists(value):
                print(f'        ✅ Path exists: {value}')
            else:
                print(f'        ❌ Path missing: {value}')
else:
    print('     ❌ task_management not found in mcpServers')
" 2>/dev/null || echo -e "     ❌ ${RED}Error parsing configuration${NC}"
    else
        echo -e "  ❌ ${RED}task_management server not found in config${NC}"
    fi
}

# Function to compare expected vs actual paths
compare_paths() {
    echo -e "\n${BLUE}🔍 Path Comparison Analysis${NC}"
    
    echo -e "\n  ${YELLOW}Expected vs Actual Paths:${NC}"
    
    # Project structure paths
    local paths=(
        "Project Root:$PROJECT_ROOT"
        "dhafnck_mcp_main:$DHAFNCK_MCP_DIR"
        "Virtual Environment:$VENV_PATH"
        "Python Executable:$PYTHON_PATH"
        "Server Script:$SERVER_SCRIPT"
        "Tasks JSON:$TASKS_JSON_PATH"
        "Backup Directory:$BACKUP_PATH"
    )
    
    for path_info in "${paths[@]}"; do
        local label="${path_info%%:*}"
        local path="${path_info##*:}"
        
        echo -e "\n  📁 ${CYAN}$label${NC}:"
        echo -e "     Expected: $path"
        if [ -e "$path" ]; then
            echo -e "     Status: ✅ ${GREEN}EXISTS${NC}"
            if [ -f "$path" ] && [ -x "$path" ]; then
                echo -e "     Permissions: ✅ ${GREEN}EXECUTABLE${NC}"
            elif [ -f "$path" ]; then
                echo -e "     Permissions: ✅ ${GREEN}READABLE${NC}"
            elif [ -d "$path" ]; then
                echo -e "     Permissions: ✅ ${GREEN}DIRECTORY${NC}"
            fi
        else
            echo -e "     Status: ❌ ${RED}MISSING${NC}"
        fi
    done
    
    # Configuration file paths
    echo -e "\n  ${YELLOW}Configuration Files:${NC}"
    local config_files=(
        "Global MCP Config:$HOME/.cursor/mcp.json"
        "Project MCP Config:$PROJECT_ROOT/.cursor/mcp.json"
        "Cursor Settings:$PROJECT_ROOT/.cursor/settings.json"
    )
    
    for config_info in "${config_files[@]}"; do
        local label="${config_info%%:*}"
        local path="${config_info##*:}"
        
        echo -e "\n  ⚙️  ${CYAN}$label${NC}:"
        echo -e "     Path: $path"
        if [ -f "$path" ]; then
            echo -e "     Status: ✅ ${GREEN}EXISTS${NC}"
            echo -e "     Size: $(stat -c%s "$path") bytes"
            echo -e "     Modified: $(stat -c%y "$path" | cut -d' ' -f1-2)"
        else
            echo -e "     Status: ❌ ${RED}MISSING${NC}"
        fi
    done
}

# Function to test manual server startup
test_manual_startup() {
    echo -e "\n${BLUE}🚀 Testing manual server startup${NC}"
    
    local startup_cmd="cd '$DHAFNCK_MCP_DIR' && source .venv/bin/activate && PYTHONPATH='$DHAFNCK_MCP_DIR/src' TASK_MANAGEMENT_TASKS_PATH='$TASKS_JSON_PATH' TASK_MANAGEMENT_BACKUP_PATH='$BACKUP_PATH' python -m fastmcp.task_management.interface.consolidated_mcp_server"
    
    echo -e "  🔧 Startup command:"
    echo -e "     $startup_cmd"
    
    echo -e "\n  🧪 Testing server startup (5 second test)..."
    
    # Start server in background and capture output
    local log_file="/tmp/mcp_server_test_$$.log"
    eval "$startup_cmd" > "$log_file" 2>&1 &
    local server_pid=$!
    
    # Wait a few seconds
    sleep 5
    
    # Check if process is still running
    if kill -0 "$server_pid" 2>/dev/null; then
        echo -e "  ✅ ${GREEN}Server started successfully (PID: $server_pid)${NC}"
        
        # Show server output
        echo -e "  📜 Server output:"
        head -20 "$log_file" | while read line; do
            echo -e "     $line"
        done
        
        # Kill the test server
        kill "$server_pid" 2>/dev/null || true
        wait "$server_pid" 2>/dev/null || true
        echo -e "  🛑 Test server stopped"
    else
        echo -e "  ❌ ${RED}Server failed to start or crashed${NC}"
        echo -e "  📜 Error output:"
        cat "$log_file" | while read line; do
            echo -e "     $line"
        done
    fi
    
    # Cleanup
    rm -f "$log_file"
}

# Function to provide recommendations
provide_recommendations() {
    echo -e "\n${PURPLE}💡 DIAGNOSTIC RECOMMENDATIONS${NC}"
    echo -e "${PURPLE}$(printf '=%.0s' {1..60})${NC}"
    
    # Check critical issues
    local issues=()
    
    if [ ! -f "$PYTHON_PATH" ]; then
        issues+=("Virtual environment Python not found at $PYTHON_PATH")
    fi
    
    if [ ! -f "$SERVER_SCRIPT" ]; then
        issues+=("Server script not found at $SERVER_SCRIPT")
    fi
    
    if [ ! -f "$TASKS_JSON_PATH" ]; then
        issues+=("Tasks JSON file not found at $TASKS_JSON_PATH")
    fi
    
    if [ ! -f "$PROJECT_ROOT/.cursor/mcp.json" ] && [ ! -f "$HOME/.cursor/mcp.json" ]; then
        issues+=("No MCP configuration file found")
    fi
    
    if [ ${#issues[@]} -eq 0 ]; then
        echo -e "✅ ${GREEN}No critical issues detected!${NC}"
        echo -e "\n${YELLOW}If Cursor still shows 0 tools, try:${NC}"
        echo -e "  1. Restart Cursor completely"
        echo -e "  2. Check Cursor logs for MCP connection errors"
        echo -e "  3. Verify you're in the correct project directory"
        echo -e "  4. Try running the manual server test above"
    else
        echo -e "❌ ${RED}Critical issues found:${NC}"
        for issue in "${issues[@]}"; do
            echo -e "  • $issue"
        done
        
        echo -e "\n${YELLOW}Recommended fixes:${NC}"
        echo -e "  1. Ensure you're in the correct directory: cd $PROJECT_ROOT"
        echo -e "  2. Activate virtual environment: cd $DHAFNCK_MCP_DIR && source .venv/bin/activate"
        echo -e "  3. Install dependencies: uv sync"
        echo -e "  4. Create missing directories: mkdir -p $(dirname "$TASKS_JSON_PATH")"
        echo -e "  5. Initialize tasks file: echo '[]' > $TASKS_JSON_PATH"
    fi
    
    echo -e "\n${YELLOW}For further debugging:${NC}"
    echo -e "  • Check this diagnostic script output"
    echo -e "  • Run manual server test above"
    echo -e "  • Check Cursor developer console (F12)"
    echo -e "  • Verify WSL and Windows path mappings"
}

# Main execution
main() {
    print_section "SYSTEM INFORMATION"
    echo -e "  🖥️  Operating System: $(uname -a)"
    echo -e "  🐧 WSL Version: $(cat /proc/version | grep -o 'Microsoft.*' || echo 'Not WSL or version unknown')"
    echo -e "  🏠 Home Directory: $HOME"
    echo -e "  📁 Current Directory: $(pwd)"
    echo -e "  🕒 Current Time: $(date)"
    echo -e "  👤 Current User: $(whoami)"
    
    print_section "PROJECT STRUCTURE VALIDATION"
    check_path "$PROJECT_ROOT" "Project Root" "required"
    check_path "$DHAFNCK_MCP_DIR" "dhafnck_mcp_main Directory" "required"
    check_path "$VENV_PATH" "Virtual Environment" "required"
    check_path "$PYTHON_PATH" "Python Executable" "required"
    check_path "$SERVER_SCRIPT" "Server Script" "required"
    check_path "$DHAFNCK_MCP_DIR/src/fastmcp" "FastMCP Package" "required"
    check_path "$DHAFNCK_MCP_DIR/src/fastmcp/task_management" "Task Management Package" "required"
    
    print_section "TASK MANAGEMENT FILES"
    check_path "$TASKS_JSON_PATH" "Tasks JSON File" "required"
    check_path "$BACKUP_PATH" "Backup Directory" "optional"
    check_path "$(dirname "$TASKS_JSON_PATH")" "Tasks Directory" "required"
    
    print_section "CONFIGURATION FILES"
    validate_mcp_config "$PROJECT_ROOT/.cursor/mcp.json" "Project MCP Config"
    validate_mcp_config "$HOME/.cursor/mcp.json" "Global MCP Config"
    check_path "$PROJECT_ROOT/.cursor/settings.json" "Cursor Settings" "optional"
    
    compare_paths
    check_processes
    
    print_section "SERVER FUNCTIONALITY TESTS"
    test_server_startup "PYTHONPATH='$DHAFNCK_MCP_DIR/src'" "Default Environment"
    test_server_startup "PYTHONPATH='$DHAFNCK_MCP_DIR/src' TASK_MANAGEMENT_TASKS_PATH='$TASKS_JSON_PATH' TASK_MANAGEMENT_BACKUP_PATH='$BACKUP_PATH'" "Full Environment"
    
    test_manual_startup
    
    print_section "CLAUDE DESKTOP LOGS"
    check_claude_logs
    
    provide_recommendations
    
    echo -e "\n${PURPLE}=============================================================================${NC}"
    echo -e "${PURPLE}                            DIAGNOSTIC COMPLETE                             ${NC}"
    echo -e "${PURPLE}=============================================================================${NC}"
    echo -e "\nDiagnostic completed at $(date)"
    echo -e "Save this output for debugging: ${CYAN}./diagnostic_connect.sh > diagnostic_output.txt 2>&1${NC}"
}

# Run main function
main "$@" 