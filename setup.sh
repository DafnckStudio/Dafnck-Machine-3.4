#!/bin/bash

# Project Setup Script for AI Environment with MCP Server
# Usage: ./setup.sh <project_name> <project_path>
# Example: ./setup.sh chaxiaiv2 /home/daihungpham/__projects__/chaxiai

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SOURCE_PROJECT="/home/daihungpham/agentic-project"
USERNAME="daihungpham"

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

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE} AI Environment Setup Script${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Function to initialize file tracking
init_file_tracking() {
    print_status "Initializing file tracking..."
    
    TRACKING_FILE="$PROJECT_PATH/dhafnck_mcp.txt"
    
    # Create tracking file with header
    cat > "$TRACKING_FILE" << EOF
# dhafnck_mcp Setup Tracking File
# This file tracks all files and directories created by setup.sh
# Generated on: $(date -Iseconds)
# Project: $PROJECT_NAME
# Path: $PROJECT_PATH

# Format: Each line contains a file or directory path relative to project root
# Directories are marked with trailing /
# Files created by setup.sh are listed here for safe removal

EOF
    
    # Add the tracking file itself to the list
    echo "dhafnck_mcp.txt" >> "$TRACKING_FILE"
}

# Function to log created files/directories
log_created_item() {
    local item="$1"
    local item_type="$2"  # "file" or "dir"
    
    # Define tracking file path
    local tracking_file="$PROJECT_PATH/dhafnck_mcp.txt"
    
    # Convert absolute path to relative path
    local relative_path="${item#$PROJECT_PATH/}"
    
    # Add trailing slash for directories
    if [ "$item_type" = "dir" ]; then
        relative_path="${relative_path}/"
    fi
    
    # Add to tracking file
    echo "$relative_path" >> "$tracking_file"
}

# Function to validate inputs
validate_inputs() {
    if [ $# -ne 2 ]; then
        print_error "Usage: $0 <project_name> <project_path>"
        print_error "Example: $0 chaxiaiv2 /home/daihungpham/__projects__/chaxiai"
        exit 1
    fi

    PROJECT_NAME="$1"
    PROJECT_PATH="$2"
    
    # Validate project name (alphanumeric and underscore only)
    if [[ ! "$PROJECT_NAME" =~ ^[a-zA-Z0-9_]+$ ]]; then
        print_error "Project name must contain only alphanumeric characters and underscores"
        exit 1
    fi
    
    # Check if source project exists
    if [ ! -d "$SOURCE_PROJECT" ]; then
        print_error "Source project directory not found: $SOURCE_PROJECT"
        exit 1
    fi
    
    print_status "Project Name: $PROJECT_NAME"
    print_status "Project Path: $PROJECT_PATH"
}

# Function to create project directory structure
create_project_structure() {
    print_status "Creating project directory structure..."
    
    # Create main project directory
    mkdir -p "$PROJECT_PATH"
    
    # Create .cursor directory structure and log each directory
    local dirs_to_create=(
        ".cursor/"
        ".cursor/rules/"
        ".cursor/rules/brain/"
        ".cursor/rules/contexts/"
        ".cursor/rules/contexts/default_id/"
        ".cursor/rules/contexts/default_id/$PROJECT_NAME/"
        ".cursor/rules/tasks/"
        ".cursor/rules/tasks/default_id/"
        ".cursor/rules/tasks/default_id/$PROJECT_NAME/"
        ".cursor/rules/tasks/default_id/$PROJECT_NAME/main/"
        ".cursor/rules/agents/"
        ".cursor/rules/02_AI-DOCS/"
    )
    
    for dir in "${dirs_to_create[@]}"; do
        local full_path="$PROJECT_PATH/$dir"
        if [ ! -d "$full_path" ]; then
            mkdir -p "$full_path"
            log_created_item "$full_path" "dir"
        fi
    done
    
    print_status "Directory structure created successfully"
}

# Function to copy essential rule files
copy_rule_files() {
    print_status "Copying essential rule files..."
    
    # Copy core rule files and log each one
    local core_files=(
        "dhafnck_mcp.mdc"
        "agents.mdc"
        "memory.mdc"
        "global_rule.txt"
    )
    
    for file in "${core_files[@]}"; do
        if [ -f "$SOURCE_PROJECT/.cursor/rules/$file" ]; then
            cp "$SOURCE_PROJECT/.cursor/rules/$file" "$PROJECT_PATH/.cursor/rules/"
            log_created_item "$PROJECT_PATH/.cursor/rules/$file" "file"
        fi
    done
    
    # Copy AI documentation directory
    if [ -d "$SOURCE_PROJECT/.cursor/rules/02_AI-DOCS" ]; then
        cp -r "$SOURCE_PROJECT/.cursor/rules/02_AI-DOCS" "$PROJECT_PATH/.cursor/rules/"
        # Log all files in the copied directory
        find "$PROJECT_PATH/.cursor/rules/02_AI-DOCS" -type f | while read -r file; do
            log_created_item "$file" "file"
        done
        find "$PROJECT_PATH/.cursor/rules/02_AI-DOCS" -type d | while read -r dir; do
            log_created_item "$dir" "dir"
        done
    fi
    
    # Copy agent configurations directory
    if [ -d "$SOURCE_PROJECT/.cursor/rules/agents" ]; then
        cp -r "$SOURCE_PROJECT/.cursor/rules/agents" "$PROJECT_PATH/.cursor/rules/"
        # Log all files in the copied directory
        find "$PROJECT_PATH/.cursor/rules/agents" -type f | while read -r file; do
            log_created_item "$file" "file"
        done
        find "$PROJECT_PATH/.cursor/rules/agents" -type d | while read -r dir; do
            log_created_item "$dir" "dir"
        done
    fi
    
    # Copy tools directory
    if [ -d "$SOURCE_PROJECT/.cursor/rules/tools" ]; then
        cp -r "$SOURCE_PROJECT/.cursor/rules/tools" "$PROJECT_PATH/.cursor/rules/"
        # Log all files in the copied directory
        find "$PROJECT_PATH/.cursor/rules/tools" -type f | while read -r file; do
            log_created_item "$file" "file"
        done
        find "$PROJECT_PATH/.cursor/rules/tools" -type d | while read -r dir; do
            log_created_item "$dir" "dir"
        done
    fi
    
    print_status "Rule files copied successfully"
}

# Function to create project-specific configuration files
create_project_config() {
    print_status "Creating project-specific configuration files..."
    
    # Create project-specific need-update file
    local need_update_file="$PROJECT_PATH/.cursor/rules/need-update-this-file-if-change-project-tree.mdc"
    cat > "$need_update_file" << EOF
---
description: 
globs: 
alwaysApply: true
---
# Main objective: $PROJECT_NAME

ROOT_PATH on WSL Ubuntu: /home/<username>/__projects__

username: $USERNAME

project_id: $PROJECT_NAME
projet_path_root: $PROJECT_PATH
---

task_tree_id: main
EOF
    log_created_item "$need_update_file" "file"

    # Create empty auto_rule.mdc (will be generated by MCP)
    local auto_rule_file="$PROJECT_PATH/.cursor/rules/auto_rule.mdc"
    cat > "$auto_rule_file" << EOF

### DO NOT EDIT - THIS FILE IS AUTOMATICALLY GENERATED ###
# Last generated: $(date -Iseconds)

# --- Project: $PROJECT_NAME ---

### TASK CONTEXT ###
- **Project**: $PROJECT_NAME
- **Location**: $PROJECT_PATH
- **Status**: Initial setup

### ROLE: CODING_AGENT ###
- Ready for task assignment and context generation.

### OPERATING RULES ###
1. Follow project-specific requirements
2. Use MCP server for task management
3. Maintain code quality and standards

### --- END OF GENERATED RULES --- ###
EOF
    log_created_item "$auto_rule_file" "file"

    # Create empty tasks.json
    local tasks_file="$PROJECT_PATH/.cursor/rules/tasks/default_id/$PROJECT_NAME/main/tasks.json"
    cat > "$tasks_file" << EOF
{
  "tasks": [],
  "metadata": {
    "version": "1.0",
    "project_id": "$PROJECT_NAME",
    "task_tree_id": "main",
    "user_id": "default_id",
    "created_at": "$(date -Iseconds)",
    "last_updated": "$(date -Iseconds)"
  }
}
EOF
    log_created_item "$tasks_file" "file"

    print_status "Project-specific configuration files created"
}

# Function to update brain/projects.json
update_brain_projects() {
    print_status "Updating brain/projects.json..."
    
    # Create brain/projects.json for the new project
    local brain_file="$PROJECT_PATH/.cursor/rules/brain/projects.json"
    cat > "$brain_file" << EOF
{
  "$PROJECT_NAME": {
    "id": "$PROJECT_NAME",
    "name": "$PROJECT_NAME",
    "description": "AI-powered project with MCP server integration",
    "task_trees": {
      "main": {
        "id": "main",
        "name": "Main Tasks",
        "description": "Main task tree for $PROJECT_NAME"
      }
    },
    "registered_agents": {},
    "agent_assignments": {},
    "created_at": "$(date -Iseconds)"
  }
}
EOF
    log_created_item "$brain_file" "file"

    # Also update the source project's brain file to include the new project
    if [ -f "$SOURCE_PROJECT/.cursor/rules/brain/projects.json" ]; then
        # Create a backup
        cp "$SOURCE_PROJECT/.cursor/rules/brain/projects.json" "$SOURCE_PROJECT/.cursor/rules/brain/projects.json.backup"
        
        # Add new project to existing brain file
        python3 << EOF
import json
import os
from datetime import datetime

brain_file = "$SOURCE_PROJECT/.cursor/rules/brain/projects.json"
project_name = "$PROJECT_NAME"
project_path = "$PROJECT_PATH"

new_project = {
    "id": project_name,
    "name": project_name, 
    "description": "AI-powered project with MCP server integration",
    "path": project_path,
    "task_trees": {
        "main": {
            "id": "main",
            "name": "Main Tasks",
            "description": f"Main task tree for {project_name}"
        }
    },
    "registered_agents": {},
    "agent_assignments": {},
    "created_at": datetime.now().isoformat() + "Z"
}

try:
    with open(brain_file, 'r') as f:
        brain_data = json.load(f)
    
    brain_data[project_name] = new_project
    
    with open(brain_file, 'w') as f:
        json.dump(brain_data, f, indent=2)
    
    print("Brain file updated successfully")
except Exception as e:
    print(f"Error updating brain file: {e}")
    exit(1)
EOF
        
        if [ $? -ne 0 ]; then
            print_error "Failed to update brain file"
            exit 1
        fi
    fi
    
    print_status "Brain projects file updated"
}

# Function to create project-specific uninstall script
create_uninstall_script() {
    print_status "Creating project-specific uninstall script..."
    
    cat > "$PROJECT_PATH/uninstall.sh" << 'UNINSTALL_EOF'
#!/bin/bash

# Project-Specific Uninstall Script
# This script was automatically generated during project setup
# It will remove only files created by setup.sh, preserving existing project content

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project-specific configuration (auto-generated)
PROJECT_NAME="PROJECT_NAME_PLACEHOLDER"
PROJECT_PATH="PROJECT_PATH_PLACEHOLDER"
SOURCE_PROJECT="SOURCE_PROJECT_PLACEHOLDER"
USERNAME="USERNAME_PLACEHOLDER"

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

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE} dhafnck_mcp Uninstall: $PROJECT_NAME${NC}"
    echo -e "${BLUE}========================================${NC}"
}

# Function to confirm uninstall
confirm_uninstall() {
    print_warning "⚠️  WARNING: This will remove files created by setup.sh:"
    echo -e "  - Project: ${YELLOW}$PROJECT_NAME${NC}"
    echo -e "  - Only files/directories created by setup.sh will be removed"
    echo -e "  - Existing project files will be preserved"
    echo -e "  - Project entry from brain/projects.json will be removed"
    echo ""
    
    # Show files that will be removed
    local tracking_file="$PROJECT_PATH/dhafnck_mcp.txt"
    if [ -f "$tracking_file" ]; then
        print_status "Files/directories that will be removed:"
        
        # Create temporary file to avoid stdin conflicts
        local preview_file="/tmp/uninstall_preview_$$"
        grep -v '^#' "$tracking_file" | grep -v '^$' > "$preview_file"
        
        local count=0
        while IFS= read -r line; do
            echo -e "  - $line"
            count=$((count + 1))
            
            # Limit display to first 15 items
            if [ $count -ge 15 ]; then
                local total_lines=$(wc -l < "$preview_file")
                if [ $total_lines -gt 15 ]; then
                    echo -e "  ... and $((total_lines - 15)) more items"
                fi
                break
            fi
        done < "$preview_file"
        
        rm -f "$preview_file"
        echo ""
    else
        print_error "Tracking file not found: $tracking_file"
        exit 1
    fi
    
    read -p "Are you sure you want to proceed? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Uninstall cancelled by user."
        exit 0
    fi
}

# Function to create backup
create_backup() {
    print_status "Creating backup before uninstall..."
    
    local backup_dir="/tmp/uninstall_backup_${PROJECT_NAME}_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup critical files
    if [ -f "$PROJECT_PATH/.cursor/rules/auto_rule.mdc" ]; then
        cp "$PROJECT_PATH/.cursor/rules/auto_rule.mdc" "$backup_dir/"
    fi
    
    if [ -f "$PROJECT_PATH/.cursor/rules/need-update-this-file-if-change-project-tree.mdc" ]; then
        cp "$PROJECT_PATH/.cursor/rules/need-update-this-file-if-change-project-tree.mdc" "$backup_dir/"
    fi
    
    if [ -f "$PROJECT_PATH/.cursor/rules/tasks/default_id/$PROJECT_NAME/main/tasks.json" ]; then
        mkdir -p "$backup_dir/tasks"
        cp "$PROJECT_PATH/.cursor/rules/tasks/default_id/$PROJECT_NAME/main/tasks.json" "$backup_dir/tasks/"
    fi
    
    # Backup the tracking file itself
    if [ -f "$PROJECT_PATH/dhafnck_mcp.txt" ]; then
        cp "$PROJECT_PATH/dhafnck_mcp.txt" "$backup_dir/"
    fi
    
    print_status "Backup created at: $backup_dir"
    echo "$backup_dir" > "/tmp/last_uninstall_backup_${PROJECT_NAME}.txt"
}

# Function to remove from brain projects
remove_from_brain() {
    print_status "Removing project from brain/projects.json..."
    
    local brain_file="$SOURCE_PROJECT/.cursor/rules/brain/projects.json"
    
    if [ -f "$brain_file" ]; then
        cp "$brain_file" "${brain_file}.uninstall_backup_$(date +%Y%m%d_%H%M%S)"
        
        python3 << EOF
import json

brain_file = "$brain_file"
project_name = "$PROJECT_NAME"

try:
    with open(brain_file, 'r') as f:
        brain_data = json.load(f)
    
    if project_name in brain_data:
        del brain_data[project_name]
        
        with open(brain_file, 'w') as f:
            json.dump(brain_data, f, indent=2)
        
        print(f"Project '{project_name}' removed from brain file")
    else:
        print(f"Project '{project_name}' not found in brain file")
        
except Exception as e:
    print(f"Error updating brain file: {e}")
    exit(1)
EOF
        
        if [ $? -eq 0 ]; then
            print_status "✅ Removed from brain/projects.json"
        else
            print_error "❌ Failed to update brain file"
            return 1
        fi
    else
        print_warning "Brain file not found: $brain_file"
    fi
}

# Function to remove tracked files
remove_tracked_files() {
    print_status "Removing files created by setup.sh..."
    
    local tracking_file="$PROJECT_PATH/dhafnck_mcp.txt"
    
    if [ ! -f "$tracking_file" ]; then
        print_error "Tracking file not found: $tracking_file"
        print_error "Cannot determine which files to remove safely."
        exit 1
    fi
    
    print_status "Reading tracking file: $tracking_file"
    
    local files_removed=0
    local dirs_removed=0
    local failed_removals=0
    
    # Create a temporary file with items to remove (excluding tracking file itself for now)
    local temp_file="/tmp/items_to_remove_$$"
    grep -v '^#' "$tracking_file" | grep -v '^$' > "$temp_file"
    
    # First pass: remove files (except tracking file)
    while IFS= read -r line; do
        # Skip directories in first pass
        [[ "$line" =~ .*/$  ]] && continue
        
        # Skip tracking file itself for now
        [[ "$line" = "dhafnck_mcp.txt" ]] && continue
        
        local full_path="$PROJECT_PATH/$line"
        
        if [ -f "$full_path" ]; then
            if rm -f "$full_path" 2>/dev/null; then
                print_status "Removed file: $line"
                ((files_removed++))
            else
                print_warning "Failed to remove file: $line"
                ((failed_removals++))
            fi
        fi
    done < "$temp_file"
    
    # Second pass: remove empty directories (in reverse order)
    tac "$temp_file" | while IFS= read -r line; do
        # Only process directories
        [[ "$line" =~ .*/$  ]] || continue
        
        local full_path="$PROJECT_PATH/$line"
        
        if [ -d "$full_path" ]; then
            # Only remove if directory is empty
            if rmdir "$full_path" 2>/dev/null; then
                print_status "Removed empty directory: $line"
                ((dirs_removed++))
            else
                print_warning "Directory not empty, keeping: $line"
            fi
        fi
    done
    
    # Finally, remove the tracking file itself
    if [ -f "$tracking_file" ]; then
        rm -f "$tracking_file"
        print_status "Removed tracking file: dhafnck_mcp.txt"
        ((files_removed++))
    fi
    
    # Clean up temp file
    rm -f "$temp_file"
    
    print_status "✅ Removal summary:"
    print_status "  - Files removed: $files_removed"
    print_status "  - Directories removed: $dirs_removed"
    if [ $failed_removals -gt 0 ]; then
        print_warning "  - Failed removals: $failed_removals"
    fi
}

# Function to display summary
display_summary() {
    print_header
    echo -e "${GREEN}🗑️  dhafnck_mcp files removed successfully!${NC}"
    echo ""
    echo -e "${BLUE}Removed:${NC}"
    echo -e "  - Project: $PROJECT_NAME"
    echo -e "  - Files created by setup.sh (see backup for details)"
    echo -e "  - Brain registry entry"
    echo -e "  - Empty directories (where possible)"
    echo ""
    echo -e "${BLUE}Preserved:${NC}"
    echo -e "  - Existing project files"
    echo -e "  - Non-empty directories"
    echo -e "  - User-created content"
    echo ""
    
    local backup_file="/tmp/last_uninstall_backup_${PROJECT_NAME}.txt"
    if [ -f "$backup_file" ]; then
        local backup_dir=$(cat "$backup_file")
        echo -e "${BLUE}Backup Location:${NC}"
        echo -e "  - ${YELLOW}$backup_dir${NC}"
        echo ""
    fi
    
    echo -e "${GREEN}dhafnck_mcp uninstall completed successfully!${NC}"
    print_header
}

# Main execution
main() {
    print_header
    
    # Validate that we have a tracking file
    if [ ! -f "$PROJECT_PATH/dhafnck_mcp.txt" ]; then
        print_error "dhafnck_mcp tracking file not found: $PROJECT_PATH/dhafnck_mcp.txt"
        print_error "This project may not have been set up with the enhanced setup.sh script"
        print_error "Cannot safely determine which files to remove."
        exit 1
    fi
    
    print_status "Project: $PROJECT_NAME"
    print_status "Path: $PROJECT_PATH"
    
    # Confirm uninstall
    confirm_uninstall
    
    # Create backup
    create_backup
    
    # Remove from brain
    remove_from_brain
    
    # Remove tracked files
    remove_tracked_files
    
    # Display summary
    display_summary
}

# Run main function
main "$@"
UNINSTALL_EOF

    # Replace placeholders with actual values
    sed -i "s|PROJECT_NAME_PLACEHOLDER|$PROJECT_NAME|g" "$PROJECT_PATH/uninstall.sh"
    sed -i "s|PROJECT_PATH_PLACEHOLDER|$PROJECT_PATH|g" "$PROJECT_PATH/uninstall.sh"
    sed -i "s|SOURCE_PROJECT_PLACEHOLDER|$SOURCE_PROJECT|g" "$PROJECT_PATH/uninstall.sh"
    sed -i "s|USERNAME_PLACEHOLDER|$USERNAME|g" "$PROJECT_PATH/uninstall.sh"
    
    # Make it executable
    chmod +x "$PROJECT_PATH/uninstall.sh"
    log_created_item "$PROJECT_PATH/uninstall.sh" "file"
    
    print_status "Project-specific uninstall script created and configured"
}

# Function to create CLAUDE.md for the new project
create_claude_md() {
    print_status "Creating CLAUDE.md for the new project..."
    
    cat > "$PROJECT_PATH/CLAUDE.md" << EOF
# Claude Code Project Configuration
User Identification:
   - You should assume that you are interacting with default_user
   - If you have not identified default_user, proactively try to do so.

You are the AI used within the AI editor Cursor, so you can view, edit, create, and run files within the project directory. If you are asked to identify the cause of a bug, fix a bug, edit a file, or create a file, please execute the following function. Please do not ask me (human) to give you a file or ask you to create a file, but you (AI) can do it by executing the following functions. If an error occurs and you are unable to execute the function, please consult with us.

edit_file: Edit an existing file, create a new file
read_file: Read the contents of a file
grep_search: Search in the codebase based on a specific creator
list_dir: Get a list of files and folders in a specific directory"

- ALWAYS edit file in small chunks
- ALWAYS read \`.cursor/rules/dhafnck_mcp.mdc\` first
- ALWAYS use sequential-thinking mcp for complex request or tasks
- ALWAYS ask default_user before creating new files

- Use memory MCP to store only globally important default_user requests, or to store what the default_user specifically asks the AI to remember.

- Fix root causes, not symptoms

- Detailed summaries without missing important details

- AI files config, rules in .cursor/rules/

- No root directory file creation without permission

- Respect project structure unless changes requested

- Monitor for requests that would exceed Pro plan token limits

- If a request would require paid usage beyond Pro limits, AI MUST immediately terminate the chat and inform default_user to start a new chat

---

when open claude:
- read \`$PROJECT_PATH/.cursor/rules/dhafnck_mcp.mdc\`
- read \`$PROJECT_PATH/.cursor/rules/agents.mdc\`
- read \`$PROJECT_PATH/.cursor/rules/memory.mdc\`
- read \`.cursor/rules/need-update-this-file-if-change-project-tree.mdc\`

when get_task() or next_task() : read \`.cursor/rules/auto_rule.mdc\`

when change project or change git branch: update .cursor/rules/need-update-this-file-if-change-project-tree.mdc

# important-instruction-reminders
Do what has been asked; nothing more, nothing less.
NEVER create files unless they're absolutely necessary for achieving your goal.
ALWAYS prefer editing an existing file to creating a new one.
NEVER proactively create documentation files (*.md) or README files. Only create documentation files if explicitly requested by the User.
EOF
    log_created_item "$PROJECT_PATH/CLAUDE.md" "file"

    print_status "CLAUDE.md created for the new project"
}

# Function to copy MCP server configuration
copy_mcp_config() {
    print_status "Setting up MCP server configuration..."
    
    # Copy MCP-related files if they exist
    if [ -f "$SOURCE_PROJECT/mcp_project_template.json" ]; then
        cp "$SOURCE_PROJECT/mcp_project_template.json" "$PROJECT_PATH/"
        log_created_item "$PROJECT_PATH/mcp_project_template.json" "file"
        
        # Update the template with project-specific information
        sed -i "s/dhafnck_mcp_main/$PROJECT_NAME/g" "$PROJECT_PATH/mcp_project_template.json"
    fi
    
    # Create a project-specific MCP configuration note
    local mcp_notes_file="$PROJECT_PATH/MCP_SETUP_NOTES.md"
    cat > "$mcp_notes_file" << EOF
# MCP Server Setup Notes for $PROJECT_NAME

## Configuration
- Project ID: $PROJECT_NAME
- Project Path: $PROJECT_PATH
- MCP Server: dhafnck_mcp (shared across projects)

## Usage
1. The MCP server dhafnck_mcp is shared across all projects
2. Use the manage_project, manage_task, and manage_agent tools
3. All tasks are stored in .cursor/rules/tasks/default_id/$PROJECT_NAME/
4. Context files are auto-generated in .cursor/rules/contexts/default_id/$PROJECT_NAME/

## Commands
- Create tasks: Use manage_task tool with project_id="$PROJECT_NAME"
- Get tasks: Use manage_task("list", project_id="$PROJECT_NAME")
- Switch context: Auto-handled when tasks are retrieved

## File Structure
\`\`\`
$PROJECT_PATH/
├── .cursor/
│   └── rules/
│       ├── dhafnck_mcp.mdc          # Core MCP configuration
│       ├── agents.mdc               # Agent definitions
│       ├── memory.mdc               # Memory management
│       ├── auto_rule.mdc            # Auto-generated context
│       ├── brain/
│       │   └── projects.json        # Project registry
│       ├── tasks/
│       │   └── default_id/
│       │       └── $PROJECT_NAME/
│       │           └── main/
│       │               └── tasks.json
│       └── contexts/
│           └── default_id/
│               └── $PROJECT_NAME/
└── CLAUDE.md                        # Project instructions
\`\`\`
EOF
    log_created_item "$mcp_notes_file" "file"

    print_status "MCP configuration setup completed"
}

# Function to set permissions
set_permissions() {
    print_status "Setting appropriate permissions..."
    
    # Make sure the project directory is accessible
    chmod -R 755 "$PROJECT_PATH"
    
    # Make rule files readable
    find "$PROJECT_PATH/.cursor/rules" -type f -exec chmod 644 {} \;
    
    print_status "Permissions set successfully"
}

# Function to validate setup
validate_setup() {
    print_status "Validating setup..."
    
    # Check essential files exist
    local essential_files=(
        ".cursor/rules/dhafnck_mcp.mdc"
        ".cursor/rules/agents.mdc"
        ".cursor/rules/memory.mdc"
        ".cursor/rules/need-update-this-file-if-change-project-tree.mdc"
        ".cursor/rules/auto_rule.mdc"
        ".cursor/rules/brain/projects.json"
        ".cursor/rules/tasks/default_id/$PROJECT_NAME/main/tasks.json"
        "CLAUDE.md"
        "uninstall.sh"
        "dhafnck_mcp.txt"
    )
    
    local missing_files=()
    
    for file in "${essential_files[@]}"; do
        if [ ! -f "$PROJECT_PATH/$file" ]; then
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -eq 0 ]; then
        print_status "✅ All essential files are present"
        return 0
    else
        print_error "❌ Missing files:"
        for file in "${missing_files[@]}"; do
            print_error "  - $file"
        done
        return 1
    fi
}

# Function to display completion summary
display_summary() {
    print_header
    echo -e "${GREEN}🎉 Project setup completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}Project Details:${NC}"
    echo -e "  Name: $PROJECT_NAME"
    echo -e "  Path: $PROJECT_PATH"
    echo -e "  MCP Server: dhafnck_mcp (shared)"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo -e "  1. Open the project in Cursor: ${YELLOW}cursor $PROJECT_PATH${NC}"
    echo -e "  2. Claude will automatically load the configuration"
    echo -e "  3. Start creating tasks with MCP tools"
    echo -e "  4. Read MCP_SETUP_NOTES.md for detailed usage"
    echo -e "  5. To remove project later: ${YELLOW}cd $PROJECT_PATH && ./uninstall.sh${NC}"
    echo ""
    echo -e "${BLUE}Key Files Created:${NC}"
    echo -e "  - CLAUDE.md (project instructions)"
    echo -e "  - uninstall.sh (project removal script)"
    echo -e "  - .cursor/rules/ (AI configuration)"
    echo -e "  - MCP_SETUP_NOTES.md (usage guide)"
    echo ""
    echo -e "${GREEN}Setup completed in: $PROJECT_PATH${NC}"
    print_header
}

# Main execution
main() {
    print_header
    
    # Validate inputs
    validate_inputs "$@"
    
    # Create project structure
    create_project_structure
    
    # Initialize file tracking
    init_file_tracking
    
    # Copy rule files
    copy_rule_files
    
    # Create project-specific configs
    create_project_config
    
    # Update brain projects
    update_brain_projects
    
    # Create project-specific uninstall script
    create_uninstall_script
    
    # Create CLAUDE.md
    create_claude_md
    
    # Copy MCP config
    copy_mcp_config
    
    # Set permissions
    set_permissions
    
    # Validate setup
    if validate_setup; then
        display_summary
        exit 0
    else
        print_error "Setup validation failed. Please check the missing files."
        exit 1
    fi
}

# Run main function with all arguments
main "$@"