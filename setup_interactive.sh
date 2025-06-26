#!/bin/bash

# Interactive Project Setup Script for AI Environment with MCP Server
# Enhanced version with step-by-step interactive setup
# Usage: ./setup_interactive.sh

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Configuration - Auto-detected
SOURCE_PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USERNAME="$(whoami)"

# Global variables
PROJECT_NAME=""
PROJECT_PATH=""
INSTALL_CLAUDE_CODE=""
PLATFORM_CHOICE=""
INSTALL_LOCATION=""
INSTALL_SEQUENTIAL_THINKING=""
INSTALL_MEMORY=""

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_question() {
    echo -e "${CYAN}[QUESTION]${NC} $1"
}

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_section() {
    echo ""
    echo ""
    echo -e "${MAGENTA}>>> $1${NC}"
    echo ""
}

# Function to display current choices summary
show_choices_summary() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}📋 Current Selections:${NC}"
    
    if [[ -n "$PROJECT_NAME" ]]; then
        echo -e "  ${GREEN}✓${NC} Project Name: ${YELLOW}$PROJECT_NAME${NC}"
    fi
    
    if [[ -n "$PROJECT_PATH" ]]; then
        echo -e "  ${GREEN}✓${NC} Project Path: ${YELLOW}$PROJECT_PATH${NC}"
    fi
    
    if [[ -n "$INSTALL_CLAUDE_CODE" ]]; then
        if [[ "$INSTALL_CLAUDE_CODE" == "yes" ]]; then
            echo -e "  ${GREEN}✓${NC} Claude Code: ${GREEN}Install${NC}"
        else
            echo -e "  ${GREEN}✓${NC} Claude Code: ${RED}Skip${NC}"
        fi
    fi
    
    if [[ -n "$PLATFORM_CHOICE" ]]; then
        if [[ "$PLATFORM_CHOICE" == "wsl" ]]; then
            echo -e "  ${GREEN}✓${NC} Platform: ${YELLOW}WSL (Windows Subsystem for Linux)${NC}"
        else
            echo -e "  ${GREEN}✓${NC} Platform: ${YELLOW}Linux/macOS (Native)${NC}"
        fi
    fi
    
    if [[ -n "$INSTALL_LOCATION" ]]; then
        if [[ "$INSTALL_LOCATION" == "global" ]]; then
            echo -e "  ${GREEN}✓${NC} Installation: ${YELLOW}Global (All projects)${NC}"
        else
            echo -e "  ${GREEN}✓${NC} Installation: ${YELLOW}Local (This project only)${NC}"
        fi
    fi
    
    if [[ -n "$INSTALL_SEQUENTIAL_THINKING" ]]; then
        if [[ "$INSTALL_SEQUENTIAL_THINKING" == "yes" ]]; then
            echo -e "  ${GREEN}✓${NC} Sequential-Thinking MCP: ${GREEN}Install${NC}"
        else
            echo -e "  ${GREEN}✓${NC} Sequential-Thinking MCP: ${RED}Skip${NC}"
        fi
    fi
    
    if [[ -n "$INSTALL_MEMORY" ]]; then
        if [[ "$INSTALL_MEMORY" == "yes" ]]; then
            echo -e "  ${GREEN}✓${NC} Memory MCP: ${GREEN}Install${NC}"
        else
            echo -e "  ${GREEN}✓${NC} Memory MCP: ${RED}Skip${NC}"
        fi
    fi
    
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
}

# Function to display welcome message with project description
show_welcome() {
    clear
    print_header "🚀 DhafnckMCP Interactive Setup"
    echo ""
    echo -e "${CYAN}Welcome to DhafnckMCP - Advanced Multi-Agent Task Orchestration${NC}"
    echo ""
    echo -e "${YELLOW}🌟 What is DhafnckMCP?${NC}"
    echo "DhafnckMCP is a powerful MCP (Model Context Protocol) server that brings"
    echo "advanced task management and multi-agent orchestration directly to your"
    echo "AI coding environment."
    echo ""
    echo -e "${YELLOW}✨ Key Features:${NC}"
    echo "• 🤖 Intelligent Task Management with AI-powered context generation"
    echo "• 👥 25+ Specialized AI Agents (coding, testing, DevOps, design, etc.)"
    echo "• 📋 Automated Project Planning and task breakdown"
    echo "• 🔄 Smart Context Switching - AI adapts based on current task"
    echo "• 📊 Unified Project Dashboard with real-time progress tracking"
    echo "• 🎭 Role-Based AI Assistance for different development phases"
    echo ""
    echo -e "${YELLOW}🌍 Cross-Platform Support:${NC}"
    echo "• 💻 Cursor (Windows + WSL)"
    echo "• 🍎 Cursor (macOS)"
    echo "• ☁️ Claude Code (Browser-based)"
    echo "• 🖥️ Claude Desktop"
    echo ""
    echo -e "${YELLOW}🎯 Perfect for:${NC}"
    echo "• Enterprise Development (large-scale projects)"
    echo "• Startup Development (rapid prototyping)"
    echo "• Solo Development (personal projects)"
    echo "• Educational Use (learning best practices)"
    echo ""
    echo -e "${GREEN}This setup wizard will guide you through configuring DhafnckMCP${NC}"
    echo -e "${GREEN}for your specific development environment and project needs.${NC}"
    echo ""
    read -p "Press Enter to continue..."
}

# Function to check if project exists in brain/projects.json
check_existing_project() {
    local project_name="$1"
    local brain_file="$SOURCE_PROJECT/.cursor/rules/brain/projects.json"
    
    if [[ -f "$brain_file" ]]; then
        # Use Python to check if project exists
        python3 << EOF
import json
import sys

try:
    with open("$brain_file", 'r') as f:
        brain_data = json.load(f)
    
    if "$project_name" in brain_data:
        print("exists")
        if "path" in brain_data["$project_name"]:
            print(brain_data["$project_name"]["path"])
        else:
            print("unknown_path")
    else:
        print("not_exists")
        
except Exception as e:
    print("error")
    sys.exit(1)
EOF
    else
        echo "not_exists"
    fi
}

# Function to delete existing project
delete_existing_project() {
    local project_name="$1"
    local project_path="$2"
    local brain_file="$SOURCE_PROJECT/.cursor/rules/brain/projects.json"
    
    print_warning "Deleting existing project: $project_name"
    
    # Remove from brain/projects.json
    if [[ -f "$brain_file" ]]; then
        # Backup brain file
        cp "$brain_file" "${brain_file}.backup.$(date +%Y%m%d_%H%M%S)"
        
        # Remove project from brain file
        python3 << EOF
import json
import sys

try:
    with open("$brain_file", 'r') as f:
        brain_data = json.load(f)
    
    if "$project_name" in brain_data:
        del brain_data["$project_name"]
        
        with open("$brain_file", 'w') as f:
            json.dump(brain_data, f, indent=2)
        
        print("✓ Removed from brain/projects.json")
    else:
        print("- Project not found in brain file")
        
except Exception as e:
    print(f"✗ Error updating brain file: {e}")
    sys.exit(1)
EOF
    fi
    
    # Remove project directory if it exists and has uninstall script
    if [[ -d "$project_path" && -f "$project_path/uninstall.sh" ]]; then
        print_status "Running uninstall script for existing project..."
        cd "$project_path" && ./uninstall.sh --force 2>/dev/null || true
        cd "$SOURCE_PROJECT"
        
        # Remove remaining directory if still exists
        if [[ -d "$project_path" ]]; then
            print_status "Removing remaining project directory..."
            rm -rf "$project_path" 2>/dev/null || true
        fi
    elif [[ -d "$project_path" ]]; then
        print_status "Removing existing project directory..."
        rm -rf "$project_path" 2>/dev/null || true
    fi
    
    print_success "Existing project deleted successfully"
}

# Function to get project name and path
get_project_name() {
    clear
    print_section "Step 1: Project Configuration"
    
    # Get project name
    while true; do
        print_question "What is your project name?"
        echo -e "${YELLOW}Note: Use only alphanumeric characters and underscores (a-z, A-Z, 0-9, _)${NC}"
        read -p "Project name: " PROJECT_NAME
        
        # Validate project name
        if [[ -z "$PROJECT_NAME" ]]; then
            print_error "Project name cannot be empty. Please try again."
            continue
        fi
        
        if [[ ! "$PROJECT_NAME" =~ ^[a-zA-Z0-9_]+$ ]]; then
            print_error "Project name must contain only alphanumeric characters and underscores."
            continue
        fi
        
        print_success "Project name set to: $PROJECT_NAME"
        break
    done
    
    # Check if project already exists in brain/projects.json
    local check_result=$(check_existing_project "$PROJECT_NAME")
    local first_line=$(echo "$check_result" | head -n 1)
    
    if [[ "$first_line" == "exists" ]]; then
        echo ""
        print_warning "⚠️  Project '$PROJECT_NAME' already exists in the system!"
        echo -e "${RED}WARNING: If you continue, the existing project will be completely deleted.${NC}"
        echo -e "${RED}This action cannot be undone!${NC}"
        echo ""
        
        # Get existing project path
        local existing_path=$(echo "$check_result" | tail -n 1)
        
        if [[ "$existing_path" != "unknown_path" && "$existing_path" != "exists" ]]; then
            echo -e "${YELLOW}Existing project location: $existing_path${NC}"
        fi
        
        echo ""
        read -p "Do you want to DELETE the existing project and continue? (y/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if [[ "$existing_path" != "unknown_path" && "$existing_path" != "exists" ]]; then
                delete_existing_project "$PROJECT_NAME" "$existing_path"
            else
                delete_existing_project "$PROJECT_NAME" ""
            fi
            echo ""
            print_success "Existing project deleted. Proceeding with new project setup."
        else
            print_error "Setup cancelled. Please run the script again with a different project name."
            exit 0
        fi
    fi
    
    # Get project path
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""
    print_question "Where would you like to create your project?"
    echo -e "${YELLOW}Examples:${NC}"
    echo "  • /home/$USERNAME/projects/$PROJECT_NAME"
    echo "  • /home/$USERNAME/workspace/$PROJECT_NAME"
    echo "  • /home/$USERNAME/__projects__/$PROJECT_NAME"
    echo ""
    
    while true; do
        read -p "Project path: " PROJECT_PATH
        
        if [[ -z "$PROJECT_PATH" ]]; then
            print_error "Project path cannot be empty. Please try again."
            continue
        fi
        
        # Expand tilde to home directory
        PROJECT_PATH="${PROJECT_PATH/#\~/$HOME}"
        
        # Check if path already exists
        if [[ -d "$PROJECT_PATH" ]]; then
            print_warning "Directory already exists: $PROJECT_PATH"
            read -p "Do you want to use this existing directory? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                continue
            fi
        fi
        
        # Check if we can create the directory
        if ! mkdir -p "$PROJECT_PATH" 2>/dev/null; then
            print_error "Cannot create directory: $PROJECT_PATH"
            print_error "Please check permissions and try again."
            continue
        fi
        
        print_success "Project path set to: $PROJECT_PATH"
        break
    done
}

# Function to ask about Claude Code installation
ask_claude_code_installation() {
    clear
    show_choices_summary
    print_section "Step 2: Claude Code Installation"
    echo -e "${YELLOW}Claude Code Integration${NC}"
    echo "Claude Code provides browser-based AI assistance with MCP server support."
    echo "This is recommended for the best DhafnckMCP experience."
    echo ""
    
    read -p "Do you want to install Claude Code? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        INSTALL_CLAUDE_CODE="no"
        print_status "Skipping Claude Code installation"
        return
    fi
    
    INSTALL_CLAUDE_CODE="yes"
    
    # Check if npm is installed
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed!"
        print_warning "Claude Code requires npm to be installed."
        echo ""
        read -p "Do you want to skip Claude Code installation? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            INSTALL_CLAUDE_CODE="no"
            print_status "Skipping Claude Code installation"
            return
        else
            print_error "Please install npm first and run this script again."
            print_status "On Ubuntu/Debian: sudo apt update && sudo apt install npm"
            print_status "On macOS: brew install npm"
            exit 1
        fi
    fi
    
    print_success "npm found, proceeding with Claude Code installation"
    
    # Install Claude Code
    print_status "Installing Claude Code globally..."
    if npm install -g @anthropic-ai/claude-code; then
        print_success "Claude Code installed successfully!"
    else
        print_error "Failed to install Claude Code"
        read -p "Do you want to continue without Claude Code? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
        INSTALL_CLAUDE_CODE="no"
    fi
}

# Function to choose platform version
choose_platform_version() {
    clear
    show_choices_summary
    print_section "Step 3: Platform Configuration"
    echo -e "${YELLOW}Platform Selection${NC}"
    echo "Please select your development platform for MCP server configuration:"
    echo ""
    echo "1) WSL (Windows Subsystem for Linux)"
    echo "2) Linux/macOS (Native)"
    echo ""
    
    while true; do
        read -p "Select platform (1-2): " -n 1 -r
        echo
        case $REPLY in
            1)
                PLATFORM_CHOICE="wsl"
                print_success "Selected: WSL (Windows Subsystem for Linux)"
                break
                ;;
            2)
                PLATFORM_CHOICE="linux_macos"
                print_success "Selected: Linux/macOS (Native)"
                break
                ;;
            *)
                print_error "Invalid selection. Please choose 1 or 2."
                ;;
        esac
    done
}

# Function to choose installation scope
choose_installation_scope() {
    print_question "Installation Scope"
    echo "Where would you like to install the MCP server configuration?"
    echo ""
    echo "1) Global (All projects for this user)"
    echo "2) Local (This project only)"
    echo ""
    echo -e "${YELLOW}Recommendation: Choose Global for easier management across projects${NC}"
    echo ""
    
    while true; do
        read -p "Select installation scope (1-2): " -n 1 -r
        echo
        case $REPLY in
            1)
                INSTALL_LOCATION="global"
                print_success "Selected: Global installation"
                break
                ;;
            2)
                INSTALL_LOCATION="local"
                print_success "Selected: Local installation"
                break
                ;;
            *)
                print_error "Invalid selection. Please choose 1 or 2."
                ;;
        esac
    done
}

# Function to setup MCP configuration
setup_mcp_configuration() {
    clear
    show_choices_summary
    print_section "Step 4: MCP Server Configuration"
    
    if [[ "$INSTALL_LOCATION" == "global" ]]; then
        setup_global_mcp_config
    else
        setup_local_mcp_config
    fi
}

# Function to setup global MCP configuration
setup_global_mcp_config() {
    local cursor_dir="/home/$USERNAME/.cursor"
    local mcp_config_file="$cursor_dir/mcp.json"
    
    print_status "Setting up global MCP configuration..."
    
    # Check if .cursor directory exists
    if [[ ! -d "$cursor_dir" ]]; then
        print_error ".cursor directory not found: $cursor_dir"
        print_error "Please ensure Cursor is installed and has been run at least once."
        echo ""
        print_status "To fix this:"
        print_status "1. Install and run Cursor IDE"
        print_status "2. Open Cursor settings (File → Preferences → Settings)"
        print_status "3. Navigate to Tools & Integrations → MCP Tools"
        print_status "4. This will create the .cursor directory"
        echo ""
        read -p "Press Enter to continue anyway (configuration will be created)..."
        mkdir -p "$cursor_dir"
    fi
    
    # Select appropriate configuration file
    local config_source=""
    if [[ "$PLATFORM_CHOICE" == "wsl" ]]; then
        config_source="$SOURCE_PROJECT/dhafnck_mcp_main/docs/config-mcp/mcp_wsl_alternative.json"
    else
        config_source="$SOURCE_PROJECT/dhafnck_mcp_main/docs/config-mcp/mcp_linux_macos.json"
    fi
    
    # Check if source config exists
    if [[ ! -f "$config_source" ]]; then
        print_error "Configuration template not found: $config_source"
        exit 1
    fi
    
    # Process the configuration
    if [[ -f "$mcp_config_file" ]]; then
        print_warning "MCP configuration already exists: $mcp_config_file"
        
        # Backup existing configuration
        local backup_file="${mcp_config_file}.backup.$(date +%Y%m%d_%H%M%S)"
        cp "$mcp_config_file" "$backup_file"
        print_status "Backup created: $backup_file"
        
        # Merge configurations
        merge_mcp_configurations "$config_source" "$mcp_config_file"
    else
        print_error "MCP configuration file not found: $mcp_config_file"
        echo ""
        print_status "Creating new MCP configuration..."
        
        # Create new configuration with only dhafnck_mcp server
        python3 << EOF
import json
import sys

try:
    # Read source configuration
    with open("$config_source", 'r') as f:
        source_data = json.load(f)
    
    # Create configuration with only dhafnck_mcp server
    if 'mcpServers' in source_data and 'dhafnck_mcp' in source_data['mcpServers']:
        dhafnck_only_config = {
            "mcpServers": {
                "dhafnck_mcp": source_data['mcpServers']['dhafnck_mcp']
            }
        }
        
        # Replace username placeholder
        config_str = json.dumps(dhafnck_only_config, indent=2)
        config_str = config_str.replace('<username>', '$USERNAME')
        
        # Write to target file
        with open("$mcp_config_file", 'w') as f:
            f.write(config_str)
        
        print("✓ Created MCP configuration with dhafnck_mcp server only")
    else:
        print("✗ dhafnck_mcp server not found in source configuration")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ Error creating configuration: {e}")
    sys.exit(1)
EOF
        print_success "MCP configuration created: $mcp_config_file"
        
        echo ""
        print_warning "IMPORTANT: Manual MCP Server Setup Required"
        echo -e "${YELLOW}Since no existing MCP configuration was found, you need to:${NC}"
        echo ""
        echo "1. Open Cursor IDE"
        echo "2. Go to File → Preferences → Cursor Settings"
        echo "3. Navigate to Tools & Integrations → MCP Tools"
        echo "4. Click 'Add a Custom MCP Server'"
        echo "5. Copy and paste this configuration:"
        echo ""
        echo -e "${CYAN}========== MCP Configuration ===========${NC}"
        # Extract and display only the dhafnck_mcp server configuration
        python3 << EOF
import json
import sys

try:
    with open("$mcp_config_file", 'r') as f:
        config_data = json.load(f)
    
    # Create configuration with only dhafnck_mcp server
    dhafnck_only_config = {
        "mcpServers": {
            "dhafnck_mcp": config_data["mcpServers"]["dhafnck_mcp"]
        }
    }
    
    print(json.dumps(dhafnck_only_config, indent=2))
    
except Exception as e:
    print(f"Error reading configuration: {e}")
    sys.exit(1)
EOF
        echo -e "${CYAN}=======================================${NC}"
        echo ""
        echo -e "${YELLOW}Full configuration has been saved to: $mcp_config_file${NC}"
        echo -e "${YELLOW}(Additional MCP servers will be configured separately)${NC}"
        echo ""
        read -p "Press Enter to continue..."
    fi
}

# Function to setup local MCP configuration
setup_local_mcp_config() {
    print_status "Setting up local MCP configuration..."
    
    local local_config_dir="$PROJECT_PATH/.cursor"
    local local_mcp_config="$local_config_dir/mcp.json"
    
    mkdir -p "$local_config_dir"
    
    # Select appropriate configuration file
    local config_source=""
    if [[ "$PLATFORM_CHOICE" == "wsl" ]]; then
        config_source="$SOURCE_PROJECT/dhafnck_mcp_main/docs/config-mcp/mcp_wsl_alternative.json"
    else
        config_source="$SOURCE_PROJECT/dhafnck_mcp_main/docs/config-mcp/mcp_linux_macos.json"
    fi
    
    # Create local configuration with only dhafnck_mcp server
    python3 << EOF
import json
import sys

try:
    # Read source configuration
    with open("$config_source", 'r') as f:
        source_data = json.load(f)
    
    # Create configuration with only dhafnck_mcp server
    if 'mcpServers' in source_data and 'dhafnck_mcp' in source_data['mcpServers']:
        dhafnck_only_config = {
            "mcpServers": {
                "dhafnck_mcp": source_data['mcpServers']['dhafnck_mcp']
            }
        }
        
        # Replace username placeholder
        config_str = json.dumps(dhafnck_only_config, indent=2)
        config_str = config_str.replace('<username>', '$USERNAME')
        
        # Write to target file
        with open("$local_mcp_config", 'w') as f:
            f.write(config_str)
        
        print("✓ Created local MCP configuration with dhafnck_mcp server only")
    else:
        print("✗ dhafnck_mcp server not found in source configuration")
        sys.exit(1)
        
except Exception as e:
    print(f"✗ Error creating local configuration: {e}")
    sys.exit(1)
EOF
    print_success "Local MCP configuration created: $local_mcp_config"
    
    echo ""
    print_status "To use this local configuration:"
    echo "1. Open this project in Cursor"
    echo "2. The MCP configuration will be automatically detected"
}

# Function to merge MCP configurations
merge_mcp_configurations() {
    local source_config="$1"
    local target_config="$2"
    
    print_status "Merging MCP server configurations..."
    
    # Use Python to merge JSON configurations (only dhafnck_mcp server)
    python3 << EOF
import json
import sys

def merge_mcp_configs(source_file, target_file):
    try:
        # Read source configuration
        with open(source_file, 'r') as f:
            source_data = json.load(f)
        
        # Read target configuration
        with open(target_file, 'r') as f:
            target_data = json.load(f)
        
        # Ensure mcpServers exists in target
        if 'mcpServers' not in target_data:
            target_data['mcpServers'] = {}
        
        # Add ONLY dhafnck_mcp server configuration
        if 'mcpServers' in source_data and 'dhafnck_mcp' in source_data['mcpServers']:
            # Replace username placeholder
            dhafnck_config = json.dumps(source_data['mcpServers']['dhafnck_mcp'])
            dhafnck_config = dhafnck_config.replace('<username>', '$USERNAME')
            target_data['mcpServers']['dhafnck_mcp'] = json.loads(dhafnck_config)
            print("✓ Added/updated dhafnck_mcp server configuration")
        
        # Write back to target
        with open(target_file, 'w') as f:
            json.dump(target_data, f, indent=2)
        
        print("✓ dhafnck_mcp server added to MCP configuration")
        return True
        
    except Exception as e:
        print(f"✗ Error merging configurations: {e}")
        return False

# Execute merge
success = merge_mcp_configs("$source_config", "$target_config")
sys.exit(0 if success else 1)
EOF

    if [[ $? -eq 0 ]]; then
        print_success "dhafnck_mcp server added to MCP configuration"
    else
        print_error "Failed to merge MCP configurations"
        print_status "Manual configuration may be required"
    fi
}

# Function to ask about sequential-thinking MCP
ask_sequential_thinking_mcp() {
    clear
    show_choices_summary
    print_section "Step 5: Sequential-Thinking MCP Server"
    echo -e "${YELLOW}Sequential-Thinking MCP Server${NC}"
    echo "This MCP server provides advanced step-by-step reasoning capabilities"
    echo "for complex problem-solving and decision-making processes."
    echo ""
    echo -e "${GREEN}Benefits:${NC}"
    echo "• 🧠 Enhanced logical reasoning and problem breakdown"
    echo "• 📝 Step-by-step solution documentation"
    echo "• 🔍 Complex analysis and decision support"
    echo "• 🎯 Improved accuracy for multi-step tasks"
    echo ""
    echo -e "${CYAN}Recommended: Yes (enhances AI reasoning capabilities)${NC}"
    echo ""
    
    read -p "Install Sequential-Thinking MCP Server? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        INSTALL_SEQUENTIAL_THINKING="no"
        print_status "Skipping Sequential-Thinking MCP installation"
    else
        INSTALL_SEQUENTIAL_THINKING="yes"
        install_additional_mcp_server "sequential-thinking"
    fi
}

# Function to ask about memory MCP
ask_memory_mcp() {
    clear
    show_choices_summary
    print_section "Step 6: Memory MCP Server"
    echo -e "${YELLOW}Memory MCP Server${NC}"
    echo "This MCP server provides persistent memory and knowledge graph"
    echo "capabilities for maintaining context across sessions."
    echo ""
    echo -e "${GREEN}Benefits:${NC}"
    echo "• 🧠 Persistent knowledge storage across AI sessions"
    echo "• 🔗 Relationship mapping and context retention"
    echo "• 📚 Learning from past interactions and decisions"
    echo "• 🎯 Improved continuity in long-term projects"
    echo ""
    echo -e "${CYAN}Recommended: Yes (essential for project continuity)${NC}"
    echo ""
    
    read -p "Install Memory MCP Server? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        INSTALL_MEMORY="no"
        print_status "Skipping Memory MCP installation"
    else
        INSTALL_MEMORY="yes"
        install_additional_mcp_server "memory"
    fi
}

# Function to install additional MCP servers
install_additional_mcp_server() {
    local server_name="$1"
    
    print_status "Installing $server_name MCP server..."
    
    if [[ "$INSTALL_LOCATION" == "global" ]]; then
        local mcp_config_file="/home/$USERNAME/.cursor/mcp.json"
    else
        local mcp_config_file="$PROJECT_PATH/.cursor/mcp.json"
    fi
    
    # Use Python to add the server configuration
    python3 << EOF
import json
import sys

def add_mcp_server(config_file, server_name):
    try:
        # Read current configuration
        with open(config_file, 'r') as f:
            config_data = json.load(f)
        
        # Ensure mcpServers exists
        if 'mcpServers' not in config_data:
            config_data['mcpServers'] = {}
        
        # Add server configuration based on type
        if server_name == "sequential-thinking":
            config_data['mcpServers']['sequential-thinking'] = {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-sequential-thinking"],
                "env": {}
            }
        elif server_name == "memory":
            config_data['mcpServers']['memory'] = {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-memory"],
                "env": {}
            }
        
        # Write back configuration
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        print(f"✓ Added {server_name} MCP server to configuration")
        return True
        
    except Exception as e:
        print(f"✗ Error adding {server_name} server: {e}")
        return False

# Execute addition
success = add_mcp_server("$mcp_config_file", "$server_name")
sys.exit(0 if success else 1)
EOF

    if [[ $? -eq 0 ]]; then
        print_success "$server_name MCP server configured successfully"
    else
        print_error "Failed to configure $server_name MCP server"
    fi
}

# Function to copy and process template files
process_template_files() {
    clear
    show_choices_summary
    print_section "Step 8: Project Template Setup"
    print_status "Setting up project template files..."
    
    # Ensure .cursor/rules directory exists
    mkdir -p "$PROJECT_PATH/.cursor/rules"
    
    # Process PRD template
    local prd_source="$SOURCE_PROJECT/dhafnck_mcp_main/docs/config-mcp/PROJECT_NAME_prd.mdc"
    local prd_target="$PROJECT_PATH/.cursor/rules/${PROJECT_NAME}_prd.mdc"
    
    if [[ -f "$prd_source" ]]; then
        # Replace all placeholders in content
        sed -e "s|\\\$PROJECT_PATH/\\\$PROJECT_NAME|$PROJECT_PATH|g" \
            -e "s|\\\$PROJECT_NAME|$PROJECT_NAME|g" \
            -e "s|\.cursor/rules/\\\$PROJECT_NAME_prd\.mdc|.cursor/rules/${PROJECT_NAME}_prd.mdc|g" \
            -e "s|\.cursor/rules/\\\$PROJECT_NAME_technical_architect\.mdc|.cursor/rules/${PROJECT_NAME}_technical_architect.mdc|g" \
            "$prd_source" > "$prd_target"
        print_success "Created PRD template: ${PROJECT_NAME}_prd.mdc"
    else
        print_warning "PRD template not found: $prd_source"
    fi
    
    # Process Technical Architect template
    local tech_source="$SOURCE_PROJECT/dhafnck_mcp_main/docs/config-mcp/PROJECT_NAME_technical_architect.mdc"
    local tech_target="$PROJECT_PATH/.cursor/rules/${PROJECT_NAME}_technical_architect.mdc"
    
    if [[ -f "$tech_source" ]]; then
        # Replace all placeholders in content
        sed -e "s|\\\$PROJECT_PATH/\\\$PROJECT_NAME|$PROJECT_PATH|g" \
            -e "s|\\\$PROJECT_NAME|$PROJECT_NAME|g" \
            -e "s|\.cursor/rules/\\\$PROJECT_NAME_prd\.mdc|.cursor/rules/${PROJECT_NAME}_prd.mdc|g" \
            -e "s|\.cursor/rules/\\\$PROJECT_NAME_technical_architect\.mdc|.cursor/rules/${PROJECT_NAME}_technical_architect.mdc|g" \
            "$tech_source" > "$tech_target"
        print_success "Created Technical Architect template: ${PROJECT_NAME}_technical_architect.mdc"
    else
        print_warning "Technical Architect template not found: $tech_source"
    fi
}

# Function to run the original setup script
run_original_setup() {
    clear
    show_choices_summary
    print_section "Step 7: Project Structure Creation"
    print_status "Creating project structure with original setup script..."
    
    if [[ -f "$SOURCE_PROJECT/setup.sh" ]]; then
        chmod +x "$SOURCE_PROJECT/setup.sh"
        "$SOURCE_PROJECT/setup.sh" "$PROJECT_NAME" "$PROJECT_PATH"
        print_success "Project structure created successfully"
    else
        print_error "Original setup script not found: $SOURCE_PROJECT/setup.sh"
        exit 1
    fi
}

# Function to display setup summary
display_setup_summary() {
    clear
    print_header "🎉 Setup Complete!"
    echo ""
    echo -e "${GREEN}Your DhafnckMCP project has been successfully configured!${NC}"
    echo ""
    echo -e "${BLUE}Project Details:${NC}"
    echo "  📁 Name: $PROJECT_NAME"
    echo "  📍 Path: $PROJECT_PATH"
    echo "  🖥️  Platform: $([ "$PLATFORM_CHOICE" == "wsl" ] && echo "WSL" || echo "Linux/macOS")"
    echo "  🌐 Installation: $([ "$INSTALL_LOCATION" == "global" ] && echo "Global" || echo "Local")"
    echo ""
    echo -e "${BLUE}Installed Components:${NC}"
    echo "  ✅ DhafnckMCP Server (Core task management)"
    if [[ "$INSTALL_CLAUDE_CODE" == "yes" ]]; then
        echo "  ✅ Claude Code (Browser-based AI)"
    else
        echo "  ❌ Claude Code (Skipped)"
    fi
    if [[ "$INSTALL_SEQUENTIAL_THINKING" == "yes" ]]; then
        echo "  ✅ Sequential-Thinking MCP (Advanced reasoning)"
    else
        echo "  ❌ Sequential-Thinking MCP (Skipped)"
    fi
    if [[ "$INSTALL_MEMORY" == "yes" ]]; then
        echo "  ✅ Memory MCP (Persistent knowledge)"
    else
        echo "  ❌ Memory MCP (Skipped)"
    fi
    echo ""
    echo -e "${BLUE}Template Files Created:${NC}"
    echo "  📄 ${PROJECT_NAME}_prd.mdc (Product Requirements)"
    echo "  📄 ${PROJECT_NAME}_technical_architect.mdc (Technical Architecture)"
    echo ""
    echo -e "${YELLOW}🚀 Next Steps:${NC}"
    echo ""
    echo -e "1. 🔧 Open Cursor IDE and restart it to load MCP servers"
    echo -e "2. 📂 Open your project: ${CYAN}cursor \"$PROJECT_PATH\"${NC}"
    echo -e "3. 🤖 Start a new chat - AI will automatically load project configuration"
    echo -e "4. 📋 Begin creating tasks using MCP tools (manage_task, manage_project)"
    echo -e "5. 🎭 Use specialized agents with @ syntax (e.g., @coding-agent, @system-architect-agent)"
    echo ""
    if [[ "$INSTALL_LOCATION" == "global" ]]; then
        echo -e "${YELLOW}MCP Configuration Location:${NC} /home/$USERNAME/.cursor/mcp.json"
    else
        echo -e "${YELLOW}MCP Configuration Location:${NC} $PROJECT_PATH/.cursor/mcp.json"
    fi
    echo ""
    echo -e "${GREEN}📚 Documentation:${NC}"
    echo -e "  • Read: $PROJECT_PATH/MCP_SETUP_NOTES.md"
    echo -e "  • Read: $PROJECT_PATH/CLAUDE.md"
    echo ""
    echo -e "${GREEN}🗑️  Uninstall:${NC}"
    echo -e "  • Run: ${CYAN}cd \"$PROJECT_PATH\" && ./uninstall.sh${NC}"
    echo ""
    print_header "Happy Coding with DhafnckMCP! 🚀"
}

# Main execution function
main() {
    # Step A: Welcome with project description
    show_welcome
    
    # Step B: Ask project name and path
    get_project_name
    
    # Step C: Ask about Claude Code installation
    ask_claude_code_installation
    
    # Step E: Choose platform version and installation scope
    choose_platform_version
    choose_installation_scope
    setup_mcp_configuration
    
    # Step F: Ask about Sequential-Thinking MCP
    ask_sequential_thinking_mcp
    
    # Step G: Ask about Memory MCP
    ask_memory_mcp
    
    # Run original setup to create project structure FIRST
    run_original_setup
    
    # Step H & I: Process template files AFTER project structure is created
    process_template_files
    
    # Display summary
    display_setup_summary
}

# Execute main function
main "$@"