"""Call Agent Use Case"""

import os
import yaml
import logging
import traceback
from pathlib import Path
from typing import Dict, Any, Optional

from ...infrastructure.services.agent_doc_generator import generate_docs_for_assignees


class CallAgentUseCase:
    """Use case for retrieving agent information and triggering agent documentation generation"""
    
    def __init__(self, cursor_agent_dir: Path):
        self._cursor_agent_dir = cursor_agent_dir
    
    def execute(self, name_agent: str) -> Dict[str, Any]:
        """Execute the call agent use case"""
        try:
            # Use absolute path for agent YAML files
            base_dir = self._cursor_agent_dir / "yaml-lib" / name_agent
            
            # Log the path for debugging
            logging.debug(f"Looking for agent in: {base_dir}")
            
            if not base_dir.exists() or not base_dir.is_dir():
                return {
                    "success": False,
                    "error": f"Agent directory not found: {base_dir}"
                }
            
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
                return {
                    "success": False,
                    "error": f"No YAML files found for agent: {name_agent}"
                }
            
            # Generate agent documentation (MDC file) for this agent
            # This ensures that calling call_agent also generates the .cursor/rules/agents/{agent_name}.mdc file
            # just like get_task and do_next operations do
            try:
                generate_docs_for_assignees([name_agent], clear_all=False)
                logging.debug(f"Generated agent documentation for: {name_agent}")
            except Exception as e:
                logging.warning(f"Failed to generate agent documentation for {name_agent}: {str(e)}")
                # Don't fail the entire operation if MDC generation fails
            
            return {
                "success": True,
                "agent_info": combined_content
            }
            
        except Exception as e:
            logging.error(f"Error in CallAgentUseCase: {str(e)}")
            logging.error(traceback.format_exc())
            return {
                "success": False,
                "error": f"Failed to retrieve agent information: {str(e)}"
            } 