"""
Dependency analysis functionality for project analysis.
Handles analysis of project dependencies and imports.
"""

import json
from pathlib import Path
from typing import List


class DependencyAnalyzer:
    """Handles project dependency analysis"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
    
    def analyze_dependencies(self) -> List[str]:
        """Analyze project dependencies by scanning actual imports in Python files"""
        deps = []
        
        # Define cursor_agent directory for consistent analysis
        cursor_agent_dir = self.project_root / "cursor_agent"
        
        # Check if this is primarily a Python project (only in cursor_agent directory)
        has_python_files = any(cursor_agent_dir.glob("**/*.py")) if cursor_agent_dir.exists() else False
        has_requirements_txt = (cursor_agent_dir / "requirements.txt").exists() or (self.project_root / "requirements.txt").exists()
        has_package_json = (self.project_root / "package.json").exists()
        
        # For Python projects, analyze actual imports from code
        if has_python_files or has_requirements_txt:
            # First, get dependencies from requirements.txt
            requirements_deps = self._get_requirements_dependencies(cursor_agent_dir)
            deps.extend(requirements_deps)
            
            # Then, scan Python files for actual imports
            import_deps = self._scan_python_imports(cursor_agent_dir)
            
            # Combine and deduplicate
            all_deps = list(set(deps + import_deps))
            deps = all_deps
            
            # Only add JavaScript dependencies if no Python dependencies were found
            if not deps and has_package_json:
                try:
                    with open(self.project_root / "package.json") as f:
                        package_data = json.load(f)
                        js_deps = []
                        if "dependencies" in package_data:
                            js_deps.extend([f"{k} (JS)" for k in package_data["dependencies"].keys()])
                        if "devDependencies" in package_data:
                            js_deps.extend([f"{k} (JS dev)" for k in package_data["devDependencies"].keys()])
                        deps.extend(js_deps[:3])  # Limit JS deps
                except Exception:
                    pass
        else:
            # For non-Python projects, use original logic
            # Node.js dependencies
            if has_package_json:
                try:
                    with open(self.project_root / "package.json") as f:
                        package_data = json.load(f)
                        if "dependencies" in package_data:
                            deps.extend(package_data["dependencies"].keys())
                except Exception:
                    pass
        
        return deps[:15]  # Limit to first 15 for readability
    
    def _get_requirements_dependencies(self, cursor_agent_dir: Path) -> List[str]:
        """Extract dependencies from requirements.txt files"""
        deps = []
        requirements_paths = [
            cursor_agent_dir / "requirements.txt",
            self.project_root / "requirements.txt"
        ]
        
        for req_path in requirements_paths:
            if req_path.exists():
                try:
                    with open(req_path) as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and not line.startswith('-'):
                                # Extract package name (before ==, >=, etc.)
                                dep_name = line.split('==')[0].split('>=')[0].split('<=')[0].split('~=')[0].split('!=')[0].strip()
                                if dep_name:  # Only add non-empty dependencies
                                    deps.append(dep_name)
                        break  # Use first found requirements.txt
                except Exception:
                    pass
        
        return deps
    
    def _scan_python_imports(self, cursor_agent_dir: Path) -> List[str]:
        """Recursively scan Python files for import statements"""
        imports = set()
        
        if not cursor_agent_dir.exists():
            return []
        
        try:
            # Find all Python files recursively
            python_files = list(cursor_agent_dir.glob("**/*.py"))
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        file_imports = self._extract_imports_from_content(content)
                        imports.update(file_imports)
                except Exception:
                    # Skip files that can't be read
                    continue
                    
        except Exception:
            pass
        
        # Filter and categorize imports
        categorized_imports = self._categorize_imports(list(imports))
        return categorized_imports
    
    def _extract_imports_from_content(self, content: str) -> List[str]:
        """Extract import statements from Python file content"""
        imports = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith('#'):
                continue
            
            # Handle 'import module' statements
            if line.startswith('import '):
                import_part = line[7:].split('#')[0].strip()  # Remove comments
                if ',' in import_part:
                    # Handle multiple imports: import os, sys, json
                    modules = [m.strip() for m in import_part.split(',')]
                    imports.extend(modules)
                else:
                    imports.append(import_part.strip())
            
            # Handle 'from module import ...' statements
            elif line.startswith('from '):
                try:
                    from_part = line[5:].split('import')[0].strip()
                    if from_part and not from_part.startswith('.'):  # Skip relative imports
                        imports.append(from_part)
                except:
                    continue
        
        return imports
    
    def _categorize_imports(self, imports: List[str]) -> List[str]:
        """Categorize imports into standard library, third-party, and local"""
        import sys
        
        # Python standard library modules (common ones)
        stdlib_modules = {
            'os', 'sys', 'json', 'pathlib', 'datetime', 'typing', 'dataclasses', 
            'argparse', 'hashlib', 'collections', 'itertools', 'functools', 
            'operator', 're', 'math', 'random', 'time', 'urllib', 'http',
            'logging', 'unittest', 'tempfile', 'shutil', 'subprocess', 'threading',
            'multiprocessing', 'asyncio', 'io', 'csv', 'xml', 'html', 'email',
            'base64', 'binascii', 'struct', 'array', 'copy', 'pickle', 'sqlite3'
        }
        
        third_party = []
        stdlib_found = []
        
        for imp in imports:
            # Get the top-level module name
            top_level = imp.split('.')[0]
            
            if top_level in stdlib_modules:
                if top_level not in stdlib_found:
                    stdlib_found.append(top_level)
            else:
                # Check if it's likely a third-party package
                if not top_level.startswith('_') and len(top_level) > 1:
                    third_party.append(top_level)
        
        result = []
        
        # Add third-party packages first
        if third_party:
            unique_third_party = list(set(third_party))
            result.extend(unique_third_party[:8])  # Limit third-party
        
        # Add standard library summary
        if stdlib_found:
            stdlib_summary = f"Python Standard Library ({', '.join(sorted(stdlib_found)[:10])})"
            result.append(stdlib_summary)
        
        return result 