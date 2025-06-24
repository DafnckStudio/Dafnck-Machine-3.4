#!/usr/bin/env python3

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from fastmcp.tools.tool_path import find_project_root
    print("✅ Successfully imported find_project_root")
    
    # Test the function
    project_root = find_project_root()
    print(f"✅ Project root found: {project_root}")
    print(f"✅ Project root exists: {project_root.exists()}")
    print(f"✅ Has pyproject.toml: {(project_root / 'pyproject.toml').exists()}")
    print(f"✅ Has .git: {(project_root / '.git').exists()}")
    
    # Test path resolution
    from fastmcp.task_management.interface.consolidated_mcp_tools import PROJECT_ROOT, BRAIN_DIR
    print(f"✅ PROJECT_ROOT: {PROJECT_ROOT}")
    print(f"✅ BRAIN_DIR: {BRAIN_DIR}")
    print(f"✅ BRAIN_DIR exists: {BRAIN_DIR.exists()}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc() 