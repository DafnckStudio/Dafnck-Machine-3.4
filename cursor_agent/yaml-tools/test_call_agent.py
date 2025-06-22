#!/usr/bin/env python3
"""
Test script for the call_agent MCP tool
"""

import sys
import json
import os
from pathlib import Path

# Helper function to find the project root directory
def find_project_root():
    """Find the project root directory (containing cursor_agent)"""
    current_dir = Path(os.path.abspath(__file__))
    
    # Go up until we find the directory containing cursor_agent
    while current_dir.parent != current_dir:  # Stop at filesystem root
        current_dir = current_dir.parent
        # If we're in cursor_agent directory, go up one more level
        if current_dir.name == 'cursor_agent':
            return current_dir.parent
        # If we see cursor_agent as a subdirectory, we're at project root
        if (current_dir / 'cursor_agent').exists():
            return current_dir
    
    # Fallback to current directory if project root not found
    return Path(os.path.abspath('.'))

# Get project root and add src to Python path
PROJECT_ROOT = find_project_root()
CURSOR_AGENT_DIR = PROJECT_ROOT / 'cursor_agent'
sys.path.insert(0, str(CURSOR_AGENT_DIR / 'src'))

# Import the MCP server and tools
try:
    from task_mcp.interface.consolidated_mcp_tools_v2 import ConsolidatedMCPToolsV2
except ImportError:
    print("Could not import ConsolidatedMCPToolsV2. Running in standalone mode.")
    ConsolidatedMCPToolsV2 = None

def main():
    """Test the call_agent tool"""
    # Create an instance of the ConsolidatedMCPToolsV2 class
    tools = None
    if ConsolidatedMCPToolsV2:
        tools = ConsolidatedMCPToolsV2()
    
    # Get the call_agent method from the class
    call_agent_method = None
    if tools:
        for method_name in dir(tools):
            if method_name == 'call_agent':
                call_agent_method = getattr(tools, method_name)
                break
    
    # Test with a sample agent (you can change this to any agent name)
    agent_name = "mcp_researcher_agent"  # Changed from lead_testing_agent
    
    if not call_agent_method:
        # The method is defined in register_tools, so we need to access it differently
        print("Direct method access not available. Testing with manual implementation...")
        
        # Use the project root to find the yaml-lib directory
        base_dir = CURSOR_AGENT_DIR / "yaml-lib" / agent_name
        
        print(f"Looking for agent in: {base_dir}")
        
        if not base_dir.exists() or not base_dir.is_dir():
            print(f"Agent directory not found: {base_dir}")
            return
        
        # Import yaml
        try:
            import yaml
            print("PyYAML is installed")
        except ImportError:
            print("PyYAML is not installed")
            return
        
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
            return
        
        agent_info = {
            "success": True,
            "agent_info": combined_content
        }
        
        # Print the agent information
        print(json.dumps(agent_info, indent=2))
    else:
        # Call the method directly
        result = call_agent_method(agent_name)
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main() 