#!/usr/bin/env python3
"""
Fix Claude Code MCP Configuration
This script configures the Claude Code extension to use your task_management MCP server
"""

import json
import os
import shutil
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_claude_code_extension():
    """Find the Claude Code extension directory"""
    cursor_server_path = Path.home() / ".cursor-server"
    
    # Search for Claude Code extension
    claude_code_paths = list(cursor_server_path.rglob("*claude-code*"))
    
    if not claude_code_paths:
        logger.error("Claude Code extension not found in ~/.cursor-server")
        return None
    
    # Find the most recent version
    claude_code_path = max(claude_code_paths, key=lambda p: p.stat().st_mtime)
    logger.info(f"Found Claude Code extension at: {claude_code_path}")
    
    return claude_code_path

def create_claude_code_mcp_config():
    """Create MCP configuration for Claude Code extension"""
    
    # Project paths
    project_root = "/home/daihungpham/agentic-project"
    dhafnck_mcp_dir = f"{project_root}/dhafnck_mcp_main"
    
    mcp_config = {
        "mcpServers": {
            "task_management": {
                "command": f"{dhafnck_mcp_dir}/.venv/bin/python",
                "args": ["-m", "fastmcp.task_management.interface.consolidated_mcp_server"],
                "cwd": dhafnck_mcp_dir,
                "env": {
                    "PYTHONPATH": f"{dhafnck_mcp_dir}/src",
                    "TASK_MANAGEMENT_TASKS_PATH": f"{project_root}/.cursor/rules/tasks/tasks.json",
                    "TASK_MANAGEMENT_BACKUP_PATH": f"{project_root}/.cursor/rules/tasks/backup"
                }
            }
        }
    }
    
    return mcp_config

def update_claude_code_settings():
    """Update Claude Code extension settings"""
    
    # Create Claude Code MCP config directory
    claude_mcp_dir = Path.home() / ".claude"
    claude_mcp_dir.mkdir(exist_ok=True)
    
    # Create MCP config file for Claude Code
    mcp_config_path = claude_mcp_dir / "mcp.json"
    mcp_config = create_claude_code_mcp_config()
    
    logger.info(f"Creating Claude Code MCP config at: {mcp_config_path}")
    
    with open(mcp_config_path, 'w') as f:
        json.dump(mcp_config, f, indent=2)
    
    logger.info("Claude Code MCP configuration created successfully")
    
    # Also create in .config/claude for different Claude versions
    claude_config_dir = Path.home() / ".config" / "claude"
    claude_config_dir.mkdir(parents=True, exist_ok=True)
    
    config_mcp_path = claude_config_dir / "mcp.json"
    shutil.copy2(mcp_config_path, config_mcp_path)
    logger.info(f"Also created config at: {config_mcp_path}")
    
    return mcp_config_path

def create_cursor_mcp_settings():
    """Create Cursor-specific MCP settings"""
    
    project_root = Path("/home/daihungpham/agentic-project")
    cursor_dir = project_root / ".cursor"
    cursor_dir.mkdir(exist_ok=True)
    
    # Create settings.json for Cursor
    settings_path = cursor_dir / "settings.json"
    
    cursor_settings = {
        "mcp.enabled": True,
        "mcp.servers": {
            "task_management": {
                "enabled": True,
                "autoStart": True
            }
        }
    }
    
    logger.info(f"Creating Cursor MCP settings at: {settings_path}")
    
    with open(settings_path, 'w') as f:
        json.dump(cursor_settings, f, indent=2)
    
    logger.info("Cursor MCP settings created successfully")
    
    return settings_path

def main():
    """Main function"""
    logger.info("🔧 Fixing Claude Code MCP Configuration...")
    
    try:
        # Find Claude Code extension
        claude_code_path = find_claude_code_extension()
        if not claude_code_path:
            logger.error("Could not find Claude Code extension")
            return False
        
        # Update Claude Code settings
        mcp_config_path = update_claude_code_settings()
        logger.info(f"✅ Created Claude Code MCP config: {mcp_config_path}")
        
        # Create Cursor MCP settings
        cursor_settings_path = create_cursor_mcp_settings()
        logger.info(f"✅ Created Cursor MCP settings: {cursor_settings_path}")
        
        logger.info("\n🎉 Configuration complete!")
        logger.info("\n📋 Next steps:")
        logger.info("1. Restart Cursor completely")
        logger.info("2. The Claude Code extension should now detect your task_management server")
        logger.info("3. Check the MCP servers list in Claude Code extension")
        logger.info("4. If it still doesn't work, try installing Claude Desktop in WSL")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error configuring Claude Code MCP: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 