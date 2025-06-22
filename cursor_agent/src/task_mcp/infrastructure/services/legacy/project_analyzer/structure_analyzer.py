"""
Project structure analysis functionality.
Handles directory tree analysis and structure detection.
"""

from pathlib import Path
from typing import Dict


class StructureAnalyzer:
    """Handles project structure analysis"""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def analyze_project_structure(self) -> Dict:
        """Analyze current project structure"""
        structure = {}

        # Directories to exclude from analysis
        excluded_dirs = {
            "htmlcov",  # Coverage reports
            "__pycache__",  # Python cache
            ".pytest_cache",  # Pytest cache
            "node_modules",  # Node.js dependencies
            ".git",  # Git directory
            ".vscode",  # VS Code settings
            ".idea",  # IntelliJ settings
            "dist",  # Distribution files
            "build",  # Build artifacts
            "egg-info",  # Python egg info
        }

        def analyze_directory(
            dir_path: Path, max_depth: int = 3, current_depth: int = 0
        ) -> Dict:
            """Recursively analyze directory structure with depth limit"""
            dir_structure = {}

            if current_depth >= max_depth:
                return dir_structure

            try:
                items = sorted(
                    dir_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower())
                )

                for item in items:
                    # Skip hidden files and directories
                    if item.name.startswith("."):
                        continue

                    # Skip excluded directories
                    if item.is_dir() and item.name in excluded_dirs:
                        continue

                    if item.is_dir():
                        # Include all directories (except excluded ones)
                        dir_structure[item.name] = analyze_directory(
                            item, max_depth, current_depth + 1
                        )
                    elif item.is_file():
                        # Include ALL files (without emoji prefix to avoid Unicode issues in JSON)
                        dir_structure[item.name] = {}

            except PermissionError:
                pass

            return dir_structure

        try:
            # ONLY analyze the cursor_agent directory contents
            cursor_agent_dir = self.project_root / "cursor_agent"
            if cursor_agent_dir.exists():
                # Return the contents of cursor_agent directory directly
                # Increase max_depth to ensure we see all files
                structure = analyze_directory(cursor_agent_dir, max_depth=4)
            else:
                # Fallback if cursor_agent directory doesn't exist
                structure = {}

        except Exception as e:
            print(f"⚠️  Error analyzing project structure: {e}")
            # Enhanced fallback structure based on actual project
            structure = {
                "src": {
                    "core": {
                        "__init__.py": {},
                        "manager.py": {},
                        "models.py": {},
                        "tasks_manager.py": {},
                        "exceptions.py": {},
                    },
                    "cli": {"__init__.py": {}, "commands.py": {}},
                    "storage": {"__init__.py": {}, "state_manager.py": {}},
                    "validation": {"__init__.py": {}, "validator.py": {}},
                    "__init__.py": {},
                },
                "lib": {
                    "senior_developer": {},
                    "task_planner": {},
                    "qa_engineer": {},
                    "code_reviewer": {},
                },
                "cursor_agent.py": {},
                "cursor_agent_cli.py": {},
                "requirements.txt": {},
                "README_REFACTORING.md": {},
            }

        return structure

    def format_directory_tree(self, structure: Dict, level: int = 0) -> str:
        """Format directory structure as a tree string"""
        tree_lines = []

        def format_item(name: str, content: Dict, current_level: int) -> None:
            """Format a single item in the tree"""
            indent = "  " * current_level

            if isinstance(content, dict) and content:
                # Directory with contents
                tree_lines.append(f"{indent}📁 {name}/")

                # Sort items: directories first, then files
                items = sorted(
                    content.items(),
                    key=lambda x: (not isinstance(x[1], dict) or not x[1], x[0]),
                )

                for sub_name, sub_content in items:
                    format_item(sub_name, sub_content, current_level + 1)
            elif isinstance(content, dict) and not content:
                # File or empty directory
                if name.endswith(
                    (".py", ".js", ".ts", ".json", ".md", ".txt", ".yml", ".yaml")
                ):
                    tree_lines.append(f"{indent}📄 {name}")
                else:
                    tree_lines.append(f"{indent}📁 {name}/")
            else:
                # Other content
                tree_lines.append(f"{indent}📄 {name}")

        # Format root level items
        if isinstance(structure, dict):
            items = sorted(
                structure.items(),
                key=lambda x: (not isinstance(x[1], dict) or not x[1], x[0]),
            )
            for name, content in items:
                format_item(name, content, level)

        return "\n".join(tree_lines)
