"""
Core project analyzer that coordinates all analysis modules.
Acts as the main facade for project analysis functionality.
"""

from pathlib import Path
from typing import Dict, List, Optional

from .structure_analyzer import StructureAnalyzer
from .pattern_detector import PatternDetector
from .dependency_analyzer import DependencyAnalyzer
from .context_generator import ContextGenerator
from .file_operations import FileOperations
from fastmcp.tools.tool_path import find_project_root


class ProjectAnalyzer:
    """Main project analyzer that coordinates all analysis modules"""
    
    def __init__(self, project_root: Path = None, cache_dir: Optional[Path] = None):
        self.project_root = project_root or find_project_root()
        context_dir = self.project_root / ".cursor/rules/contexts"
        # Initialize analysis modules (no cache)
        self.structure_analyzer = StructureAnalyzer(self.project_root)
        self.pattern_detector = PatternDetector(self.project_root)
        self.dependency_analyzer = DependencyAnalyzer(self.project_root)
        self.context_generator = ContextGenerator(context_dir=context_dir)
        self.file_operations = FileOperations(self.project_root)
    
    def analyze_project_structure(self, use_cache: bool = True) -> Dict:
        """Analyze current project structure (cache parameter ignored)"""
        return self.structure_analyzer.analyze_project_structure()
    
    def detect_existing_patterns(self, use_cache: bool = True) -> List[str]:
        """Detect existing code patterns and frameworks (cache parameter ignored)"""
        return self.pattern_detector.detect_existing_patterns()
    
    def analyze_dependencies(self, use_cache: bool = True) -> List[str]:
        """Analyze project dependencies by scanning actual imports in Python files (cache parameter ignored)"""
        return self.dependency_analyzer.analyze_dependencies()
    
    def format_directory_tree(self, structure: Dict, level: int = 0) -> str:
        """Format directory structure as tree"""
        return self.context_generator.format_directory_tree(structure, level)
    
    def generate_context_summary(self, task_phase: str = "coding") -> str:
        """Generate contextual guidance for agent roles based on project analysis"""
        # Get all analysis results
        structure = self.analyze_project_structure()
        patterns = self.detect_existing_patterns()
        dependencies = self.analyze_dependencies()
        
        return self.context_generator.generate_context_summary(structure, patterns, dependencies, task_phase)
    
    def save_context_to_file(self, context_file: Path, task_phase: str = "coding") -> bool:
        """Save analyzed context to project_context.json file"""
        # Get all analysis results
        structure = self.analyze_project_structure()
        patterns = self.detect_existing_patterns()
        dependencies = self.analyze_dependencies()
        context_summary = self.generate_context_summary(task_phase)
        phase_specific_context = self.context_generator._get_phase_specific_context(task_phase, patterns)
        
        context_data = {
            "project_structure": structure,
            "existing_patterns": patterns,
            "dependencies": dependencies,
            "context_summary": context_summary,
            "phase_specific_context": phase_specific_context
        }
        
        return self.file_operations.save_context_to_file(context_file, context_data, task_phase)
    
    def load_context_from_file(self, context_file: Path) -> Optional[Dict]:
        """Load analyzed context from project_context.json file"""
        return self.file_operations.load_context_from_file(context_file)
    
    def get_context_for_agent_integration(self, task_phase: str = "coding") -> Dict:
        """Get context data formatted for agent role integration"""
        structure = self.analyze_project_structure()
        patterns = self.detect_existing_patterns()
        dependencies = self.analyze_dependencies()
        
        return {
            "project_structure": structure,
            "existing_patterns": patterns,
            "dependencies": dependencies,
            "context_summary": self.context_generator.generate_context_summary(structure, patterns, dependencies, task_phase),
            "phase_specific_context": self.context_generator._get_phase_specific_context(task_phase, patterns),
            "tree_formatter": self.format_directory_tree
        }
    
    def invalidate_cache(self, analysis_type: Optional[str] = None) -> None:
        """Invalidate cached analysis results (no-op since cache is disabled)"""
        pass
    
    def cleanup_cache(self) -> None:
        """Clean up expired cache entries (no-op since cache is disabled)"""
        pass
    
    # Backward compatibility methods for tests
    def _get_requirements_dependencies(self, cursor_agent_dir: Path) -> List[str]:
        """Extract dependencies from requirements.txt files"""
        return self.dependency_analyzer._get_requirements_dependencies(cursor_agent_dir)
    
    def _scan_python_imports(self, cursor_agent_dir: Path) -> List[str]:
        """Recursively scan Python files for import statements"""
        return self.dependency_analyzer._scan_python_imports(cursor_agent_dir)
    
    def _extract_imports_from_content(self, content: str) -> List[str]:
        """Extract import statements from Python file content"""
        return self.dependency_analyzer._extract_imports_from_content(content)
    
    def _categorize_imports(self, imports: List[str]) -> List[str]:
        """Categorize imports into standard library, third-party, and local"""
        return self.dependency_analyzer._categorize_imports(imports)
    
    def _get_phase_specific_context(self, phase: str) -> str:
        """Get phase-specific context for analysis"""
        return self.context_generator._get_phase_specific_context(phase, self.detect_existing_patterns()) 