#!/bin/bash

# Project Uninstall Script for AI Environment with MCP Server
# Usage: ./uninstall.sh <project_name> <project_path>
# Example: ./uninstall.sh chaxiaiv2 /home/daihungpham/__projects__/chaxiai

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
    echo -e "${BLUE} AI Environment Uninstall Script${NC}"
    echo -e "${BLUE}========================================${NC}"
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
    
    # Check if target project exists
    if [ ! -d "$PROJECT_PATH" ]; then
        print_warning "Project directory not found: $PROJECT_PATH"
        print_warning "Nothing to uninstall for this path."
        exit 0
    fi
    
    print_status "Project Name: $PROJECT_NAME"
    print_status "Project Path: $PROJECT_PATH"
}

# Function to confirm uninstall
confirm_uninstall() {
    print_warning "⚠️  WARNING: This will completely remove the following:"
    echo -e "  - Project directory: ${YELLOW}$PROJECT_PATH${NC}"
    echo -e "  - All files and subdirectories within it"
    echo -e "  - Project entry from brain/projects.json"
    echo -e "  - Any backup files created during setup"
    echo ""
    
    # List some key files that will be removed
    if [ -d "$PROJECT_PATH" ]; then
        print_status "Files and directories to be removed:"
        find "$PROJECT_PATH" -maxdepth 3 -type f | head -10 | while read -r file; do
            echo -e "  - ${file#$PROJECT_PATH/}"
        done
        
        local total_files=$(find "$PROJECT_PATH" -type f | wc -l)
        local total_dirs=$(find "$PROJECT_PATH" -type d | wc -l)
        echo -e "  ... and ${total_files} more files in ${total_dirs} directories"
        echo ""
    fi
    
    read -p "Are you sure you want to proceed? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Uninstall cancelled by user."
        exit 0
    fi
}

# Function to create backup before uninstall
create_uninstall_backup() {
    print_status "Creating backup before uninstall..."
    
    local backup_dir="/tmp/uninstall_backup_${PROJECT_NAME}_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$backup_dir"
    
    # Backup critical configuration files only (not the entire project)
    if [ -f "$PROJECT_PATH/.cursor/rules/auto_rule.mdc" ]; then
        cp "$PROJECT_PATH/.cursor/rules/auto_rule.mdc" "$backup_dir/"
    fi
    
    if [ -f "$PROJECT_PATH/.cursor/rules/need-update-this-file-if-change-project-tree.mdc" ]; then
        cp "$PROJECT_PATH/.cursor/rules/need-update-this-file-if-change-project-tree.mdc" "$backup_dir/"
    fi
    
    if [ -f "$PROJECT_PATH/.cursor/rules/brain/projects.json" ]; then
        cp "$PROJECT_PATH/.cursor/rules/brain/projects.json" "$backup_dir/"
    fi
    
    if [ -f "$PROJECT_PATH/.cursor/rules/tasks/default_id/$PROJECT_NAME/main/tasks.json" ]; then
        mkdir -p "$backup_dir/tasks"
        cp "$PROJECT_PATH/.cursor/rules/tasks/default_id/$PROJECT_NAME/main/tasks.json" "$backup_dir/tasks/"
    fi
    
    print_status "Backup created at: $backup_dir"
    echo "$backup_dir" > "/tmp/last_uninstall_backup_${PROJECT_NAME}.txt"
}

# Function to remove project from brain/projects.json
remove_from_brain_projects() {
    print_status "Removing project from brain/projects.json..."
    
    local brain_file="$SOURCE_PROJECT/.cursor/rules/brain/projects.json"
    
    if [ -f "$brain_file" ]; then
        # Create a backup of the brain file
        cp "$brain_file" "${brain_file}.uninstall_backup_$(date +%Y%m%d_%H%M%S)"
        
        # Remove project entry using Python
        python3 << EOF
import json
import os
from datetime import datetime

brain_file = "$brain_file"
project_name = "$PROJECT_NAME"

try:
    with open(brain_file, 'r') as f:
        brain_data = json.load(f)
    
    if project_name in brain_data:
        del brain_data[project_name]
        
        with open(brain_file, 'w') as f:
            json.dump(brain_data, f, indent=2)
        
        print(f"Project '{project_name}' removed from brain file successfully")
    else:
        print(f"Project '{project_name}' not found in brain file")
        
except Exception as e:
    print(f"Error updating brain file: {e}")
    exit(1)
EOF
        
        if [ $? -eq 0 ]; then
            print_status "Project removed from brain/projects.json successfully"
        else
            print_error "Failed to remove project from brain/projects.json"
            return 1
        fi
    else
        print_warning "Brain file not found: $brain_file"
    fi
}

# Function to remove project directory
remove_project_directory() {
    print_status "Removing project directory..."
    
    if [ -d "$PROJECT_PATH" ]; then
        # Double-check we're not removing critical system directories
        case "$PROJECT_PATH" in
            "/" | "/home" | "/usr" | "/var" | "/etc" | "/bin" | "/sbin")
                print_error "Refusing to remove system directory: $PROJECT_PATH"
                exit 1
                ;;
            "/home/$USERNAME")
                print_error "Refusing to remove user home directory: $PROJECT_PATH"
                exit 1
                ;;
        esac
        
        # Ensure the path contains our expected structure
        if [ ! -d "$PROJECT_PATH/.cursor" ]; then
            print_warning "Directory doesn't appear to be an AI project (no .cursor directory found)"
            read -p "Continue anyway? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                print_status "Uninstall cancelled."
                exit 0
            fi
        fi
        
        # Remove the directory
        rm -rf "$PROJECT_PATH"
        
        if [ ! -d "$PROJECT_PATH" ]; then
            print_status "✅ Project directory removed successfully"
        else
            print_error "❌ Failed to remove project directory"
            return 1
        fi
    else
        print_warning "Project directory not found: $PROJECT_PATH"
    fi
}

# Function to clean up backup files
cleanup_setup_backups() {
    print_status "Cleaning up setup backup files..."
    
    # Remove backup files created during setup
    local brain_backup="$SOURCE_PROJECT/.cursor/rules/brain/projects.json.backup"
    if [ -f "$brain_backup" ]; then
        rm -f "$brain_backup"
        print_status "Removed setup backup: projects.json.backup"
    fi
    
    # Clean up any other backup files that might have been created
    find "$SOURCE_PROJECT/.cursor/rules/brain/" -name "projects.json.backup*" -type f -delete 2>/dev/null || true
}

# Function to validate uninstall
validate_uninstall() {
    print_status "Validating uninstall..."
    
    local validation_errors=()
    
    # Check that project directory is gone
    if [ -d "$PROJECT_PATH" ]; then
        validation_errors+=("Project directory still exists: $PROJECT_PATH")
    fi
    
    # Check that project is removed from brain file
    if [ -f "$SOURCE_PROJECT/.cursor/rules/brain/projects.json" ]; then
        if grep -q "\"$PROJECT_NAME\"" "$SOURCE_PROJECT/.cursor/rules/brain/projects.json" 2>/dev/null; then
            validation_errors+=("Project still exists in brain/projects.json")
        fi
    fi
    
    if [ ${#validation_errors[@]} -eq 0 ]; then
        print_status "✅ Uninstall validation passed"
        return 0
    else
        print_error "❌ Uninstall validation failed:"
        for error in "${validation_errors[@]}"; do
            print_error "  - $error"
        done
        return 1
    fi
}

# Function to display completion summary
display_summary() {
    print_header
    echo -e "${GREEN}🗑️  Project uninstall completed successfully!${NC}"
    echo ""
    echo -e "${BLUE}Removed:${NC}"
    echo -e "  - Project: $PROJECT_NAME"
    echo -e "  - Directory: $PROJECT_PATH"
    echo -e "  - Brain registry entry"
    echo -e "  - Setup backup files"
    echo ""
    
    # Show backup location
    local backup_file="/tmp/last_uninstall_backup_${PROJECT_NAME}.txt"
    if [ -f "$backup_file" ]; then
        local backup_dir=$(cat "$backup_file")
        echo -e "${BLUE}Backup Location:${NC}"
        echo -e "  - Configuration backup: ${YELLOW}$backup_dir${NC}"
        echo -e "  - To restore: manually copy files from backup if needed"
        echo ""
    fi
    
    echo -e "${BLUE}Brain File Backups:${NC}"
    find "$SOURCE_PROJECT/.cursor/rules/brain/" -name "projects.json.uninstall_backup*" -type f 2>/dev/null | while read -r backup; do
        echo -e "  - ${backup}"
    done
    echo ""
    
    echo -e "${GREEN}Uninstall completed successfully!${NC}"
    print_header
}

# Function to handle errors
handle_error() {
    print_error "An error occurred during uninstall. Check the output above for details."
    print_status "You may need to manually clean up remaining files."
    
    # Show what might need manual cleanup
    echo -e "${YELLOW}Manual cleanup may be needed for:${NC}"
    if [ -d "$PROJECT_PATH" ]; then
        echo -e "  - Project directory: $PROJECT_PATH"
    fi
    echo -e "  - Brain file entry for: $PROJECT_NAME"
    
    exit 1
}

# Main execution
main() {
    print_header
    
    # Set error handler
    trap handle_error ERR
    
    # Validate inputs
    validate_inputs "$@"
    
    # Confirm uninstall
    confirm_uninstall
    
    # Create backup
    create_uninstall_backup
    
    # Remove from brain projects
    remove_from_brain_projects
    
    # Remove project directory
    remove_project_directory
    
    # Clean up setup backups
    cleanup_setup_backups
    
    # Validate uninstall
    if validate_uninstall; then
        display_summary
        exit 0
    else
        print_error "Uninstall validation failed. Some manual cleanup may be required."
        exit 1
    fi
}

# Run main function with all arguments
main "$@" 