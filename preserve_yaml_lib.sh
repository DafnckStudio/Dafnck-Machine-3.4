#!/bin/bash

# YAML-LIB PROTECTION SCRIPT
# This script ensures yaml-lib files are always preserved

set -e

PROJECT_ROOT="/home/daihungpham/agentic-project"
YAML_LIB_DIR="$PROJECT_ROOT/dhafnck_mcp_main/yaml-lib"
BACKUP_DIR="$PROJECT_ROOT/.yaml-lib-backup"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🛡️  YAML-LIB PROTECTION SCRIPT${NC}"
echo "======================================="

# Function to create backup
create_backup() {
    echo -e "${YELLOW}📦 Creating backup...${NC}"
    if [ -d "$YAML_LIB_DIR" ]; then
        rsync -av --delete "$YAML_LIB_DIR/" "$BACKUP_DIR/"
        echo -e "${GREEN}✅ Backup created at: $BACKUP_DIR${NC}"
    else
        echo -e "${RED}❌ yaml-lib directory not found!${NC}"
    fi
}

# Function to restore from backup
restore_backup() {
    echo -e "${YELLOW}🔄 Restoring from backup...${NC}"
    if [ -d "$BACKUP_DIR" ]; then
        mkdir -p "$YAML_LIB_DIR"
        rsync -av --delete "$BACKUP_DIR/" "$YAML_LIB_DIR/"
        echo -e "${GREEN}✅ Restored from backup${NC}"
    else
        echo -e "${RED}❌ No backup found!${NC}"
        exit 1
    fi
}

# Function to add git protection
add_git_protection() {
    echo -e "${YELLOW}🔒 Adding Git protection...${NC}"
    cd "$PROJECT_ROOT"
    
    # Create .gitignore patterns to protect yaml-lib (if needed)
    if ! grep -q "!dhafnck_mcp_main/yaml-lib" .gitignore 2>/dev/null; then
        echo "# Protect yaml-lib directory" >> .gitignore
        echo "!dhafnck_mcp_main/yaml-lib/**" >> .gitignore
        echo -e "${GREEN}✅ Added Git protection${NC}"
    fi
    
    # Ensure yaml-lib is tracked
    git add dhafnck_mcp_main/yaml-lib/ 2>/dev/null || true
}

# Function to monitor directory
monitor_directory() {
    echo -e "${YELLOW}👁️  Monitoring yaml-lib directory...${NC}"
    echo "Press Ctrl+C to stop monitoring"
    
    # Install inotify-tools if not present
    if ! command -v inotifywait &> /dev/null; then
        echo "Installing inotify-tools..."
        sudo apt-get update && sudo apt-get install -y inotify-tools
    fi
    
    # Monitor for deletions and automatically restore
    inotifywait -m -r -e delete,delete_self,moved_from "$YAML_LIB_DIR" --format '%w%f %e' |
    while read file event; do
        echo -e "${RED}🚨 DETECTED: $event on $file${NC}"
        sleep 1
        restore_backup
    done
}

# Function to check yaml-lib integrity
check_integrity() {
    echo -e "${YELLOW}🔍 Checking yaml-lib integrity...${NC}"
    
    local issues=0
    
    # Check if main directory exists
    if [ ! -d "$YAML_LIB_DIR" ]; then
        echo -e "${RED}❌ yaml-lib directory missing${NC}"
        issues=$((issues + 1))
    fi
    
    # Check for empty agent directories
    if [ -d "$YAML_LIB_DIR" ]; then
        for agent_dir in "$YAML_LIB_DIR"/*_agent; do
            if [ -d "$agent_dir" ] && [ -z "$(find "$agent_dir" -name "*.yaml" -type f)" ]; then
                echo -e "${RED}❌ Empty agent directory: $(basename "$agent_dir")${NC}"
                issues=$((issues + 1))
            fi
        done
    fi
    
    if [ $issues -eq 0 ]; then
        echo -e "${GREEN}✅ yaml-lib integrity OK${NC}"
    else
        echo -e "${RED}❌ Found $issues integrity issues${NC}"
        echo "Run with --restore to fix"
    fi
    
    return $issues
}

# Main command handling
case "${1:-help}" in
    "backup")
        create_backup
        ;;
    "restore")
        restore_backup
        ;;
    "protect")
        create_backup
        add_git_protection
        echo -e "${GREEN}🛡️  Protection enabled${NC}"
        ;;
    "monitor")
        monitor_directory
        ;;
    "check")
        check_integrity
        ;;
    "help"|*)
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  backup   - Create backup of yaml-lib"
        echo "  restore  - Restore from backup"
        echo "  protect  - Enable full protection (backup + git)"
        echo "  monitor  - Monitor and auto-restore on deletion"
        echo "  check    - Check yaml-lib integrity"
        echo "  help     - Show this help"
        echo ""
        echo "Examples:"
        echo "  $0 protect   # Enable protection"
        echo "  $0 check     # Check if files are intact"
        echo "  $0 restore   # Restore if files are missing"
        ;;
esac