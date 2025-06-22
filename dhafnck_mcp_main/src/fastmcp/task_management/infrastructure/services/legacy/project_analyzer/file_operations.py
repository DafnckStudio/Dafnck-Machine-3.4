"""
File operations functionality for project analysis.
Handles saving and loading of analysis context data.
"""

import json
import time
from pathlib import Path
from typing import Dict, Optional


class FileOperations:
    """Handles file operations for project analysis context"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def save_context_to_file(self, context_file: Path, context_data: Dict, task_phase: str = "coding") -> bool:
        """Save analyzed context to project_context.json file"""
        try:
            # Generate complete context data
            save_data = {
                "timestamp": time.time(),
                "project_root": str(self.project_root),
                "analysis_version": "1.0",
                "project_structure": context_data.get("project_structure", {}),
                "existing_patterns": context_data.get("existing_patterns", []),
                "dependencies": context_data.get("dependencies", []),
                "context_summary": context_data.get("context_summary", ""),
                "phase_specific_context": context_data.get("phase_specific_context", ""),
                "tree_formatter": None  # Will be set by caller if needed
            }
            
            # Ensure directory exists
            context_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Save to file with atomic operation
            temp_file = context_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            # Atomic rename
            temp_file.rename(context_file)
            return True
            
        except Exception as e:
            print(f"⚠️  Error saving context to file: {e}")
            return False
    
    def load_context_from_file(self, context_file: Path) -> Optional[Dict]:
        """Load analyzed context from project_context.json file"""
        if not context_file.exists():
            return None
        
        try:
            with open(context_file, 'r') as f:
                context_data = json.load(f)
            
            # Validate context data
            required_keys = ["timestamp", "project_root", "project_structure", "existing_patterns", "dependencies"]
            if all(key in context_data for key in required_keys):
                return context_data
            else:
                print(f"⚠️  Invalid context file format: {context_file}")
                return None
                
        except (json.JSONDecodeError, OSError) as e:
            print(f"⚠️  Error loading context from file: {e}")
            return None 