#!/usr/bin/env python3
"""
Call Agent Tool - A convenient wrapper for the call_agent MCP tool

Usage:
  python call_agent.py <agent_name>
  
Example:
  python call_agent.py coding_agent
  python call_agent.py mcp_researcher_agent
"""

import sys
import json
import os
from pathlib import Path

def find_project_root():
    """Find the project root directory by locating pyproject.toml"""
    current_dir = Path(os.path.abspath(__file__)).parent
    # Traverse up the directory tree until pyproject.toml is found
    while current_dir != current_dir.parent:  # Stop at the filesystem root
        if (current_dir / 'pyproject.toml').exists():
            # The directory containing pyproject.toml is cursor_agent.
            # We need to return its parent, which is the actual project root.
            if current_dir.name == 'cursor_agent':
                 return current_dir.parent
            return current_dir # Should be project root if pyproject.toml is there
        current_dir = current_dir.parent
    
    # Fallback if the loop completes without finding the file
    raise FileNotFoundError("Could not find project root containing 'pyproject.toml'")

# Get project root and add src to Python path
PROJECT_ROOT = find_project_root()
CURSOR_AGENT_DIR = PROJECT_ROOT / 'cursor_agent'
sys.path.insert(0, str(CURSOR_AGENT_DIR / 'src'))

# Import the MCP server and tools
try:
    from task_mcp.interface.consolidated_mcp_tools_v2 import ConsolidatedMCPToolsV2
    MCP_AVAILABLE = True
except ImportError:
    print("Could not import ConsolidatedMCPToolsV2. Running in standalone mode.")
    MCP_AVAILABLE = False

def call_agent_standalone(agent_name):
    """Call agent using standalone implementation"""
    print(f"Using standalone implementation to call agent: {agent_name}")
    
    # Use the project root to find the yaml-lib directory
    base_dir = CURSOR_AGENT_DIR / "yaml-lib" / agent_name
    
    print(f"Looking for agent in: {base_dir}")
    
    if not base_dir.exists() or not base_dir.is_dir():
        print(f"Agent directory not found: {base_dir}")
        return None
    
    # Import yaml
    try:
        import yaml
    except ImportError:
        print("PyYAML is not installed")
        return None
    
    # Dictionary to store all agent content
    combined_content = {}
    
    # Function to safely load YAML file
    def load_yaml_file(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            return {"error": f"Error loading file: {str(e)}"}
    
    # Walk through all directories and files
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.yaml'):
                file_path = os.path.join(root, file)
                
                # Load YAML content
                yaml_content = load_yaml_file(file_path)
                
                # Extract content and merge into combined_content
                if isinstance(yaml_content, dict):
                    # If the content is a dictionary with a single key matching the filename without extension,
                    # extract just that inner content
                    file_name_without_ext = os.path.splitext(os.path.basename(file))[0]
                    if len(yaml_content) == 1 and file_name_without_ext in yaml_content:
                        inner_content = yaml_content[file_name_without_ext]
                        # If the inner content is a dict, merge it
                        if isinstance(inner_content, dict):
                            combined_content.update(inner_content)
                        else:
                            # Otherwise add it with the key
                            combined_content[file_name_without_ext] = inner_content
                    else:
                        # Merge all keys from this file
                        combined_content.update(yaml_content)
    
    # If no files were found, return an error
    if not combined_content:
        print(f"No YAML files found for agent: {agent_name}")
        return None
    
    agent_info = {
        "success": True,
        "agent_info": combined_content
    }
    
    return agent_info

def main():
    """Main function to call agent"""
    # Check if agent name is provided
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <agent_name>")
        print("Example: python call_agent.py coding_agent")
        return
    
    agent_name = sys.argv[1]
    
    # Try to use MCP server if available
    if MCP_AVAILABLE:
        tools = ConsolidatedMCPToolsV2()
        
        # Try to find call_agent method
        call_agent_method = None
        for method_name in dir(tools):
            if method_name == 'call_agent':
                call_agent_method = getattr(tools, method_name)
                break
        
        if call_agent_method:
            print(f"Using MCP server to call agent: {agent_name}")
            result = call_agent_method(agent_name)
            print(json.dumps(result, indent=2))
            return
    
    # Fallback to standalone implementation
    result = call_agent_standalone(agent_name)
    if result:
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main() 