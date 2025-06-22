"""
Context generation functionality for project analysis.
Handles generation of contextual guidance and summaries.
"""

from typing import Dict, List


class ContextGenerator:
    """Handles context generation for agent roles"""
    
    def __init__(self):
        pass
    
    def generate_context_summary(self, structure: Dict, patterns: List[str], dependencies: List[str], task_phase: str = "coding") -> str:
        """Generate contextual guidance for agent roles based on project analysis"""
        # Generate context summary
        context_parts = []
        
        # Project overview
        context_parts.append("## Project Context Analysis")
        context_parts.append("")
        
        # Technology stack summary
        if patterns:
            context_parts.append("### Technology Stack")
            for pattern in patterns[:5]:  # Limit to top 5 patterns
                context_parts.append(f"- {pattern}")
            context_parts.append("")
        
        # Key dependencies
        if dependencies:
            context_parts.append("### Key Dependencies")
            for dep in dependencies[:8]:  # Limit to top 8 dependencies
                context_parts.append(f"- {dep}")
            context_parts.append("")
        
        # Project structure insights
        if structure:
            context_parts.append("### Project Structure Insights")
            if "src" in structure:
                context_parts.append("- Modular architecture with src/ directory")
            if "tests" in structure:
                context_parts.append("- Test suite present")
            if "lib" in structure:
                context_parts.append("- Library/component structure detected")
            if any("requirements" in str(k).lower() for k in structure.keys()):
                context_parts.append("- Python dependency management configured")
            context_parts.append("")
        
        # Phase-specific guidance
        phase_guidance = self._get_phase_specific_context(task_phase, patterns)
        if phase_guidance:
            context_parts.append(phase_guidance)
        
        return "\n".join(context_parts)
    
    def _get_phase_specific_context(self, phase: str, patterns: List[str]) -> str:
        """Get dynamic context specific to current development phase based on project patterns"""
        context = [f"### {phase.title()} Phase Context"]
        
        # Base guidance for each phase
        base_guidance = {
            "planning": [
                "Consider existing project patterns when designing new features",
                "Leverage established architecture and conventions", 
                "Plan for integration with existing components",
                "Analyze current project structure for optimal placement"
            ],
            "coding": [
                "Follow established coding patterns and conventions",
                "Maintain consistency with existing architecture",
                "Consider integration points with current components"
            ],
            "testing": [
                "Test against existing project patterns and conventions",
                "Ensure compatibility with current architecture", 
                "Validate integration points with existing components",
                "Follow established testing patterns"
            ],
            "review": [
                "Verify adherence to established project patterns",
                "Check consistency with existing code style",
                "Validate architectural decisions align with project structure",
                "Ensure quality standards match project conventions"
            ]
        }
        
        # Add base guidance
        phase_guidance = base_guidance.get(phase, [f"Focus on {phase} activities according to project patterns"])
        for guidance in phase_guidance:
            context.append(f"- {guidance}")
        
        # Add pattern-specific guidance dynamically
        if patterns:
            pattern_guidance = self._get_pattern_specific_guidance(phase, patterns)
            if pattern_guidance:
                context.append("")
                context.append("#### Pattern-Specific Guidance")
                context.extend(pattern_guidance)
        
        return "\n".join(context)
    
    def _get_pattern_specific_guidance(self, phase: str, patterns: List[str]) -> List[str]:
        """Get guidance specific to detected project patterns"""
        guidance = []
        
        # Python-specific guidance
        if any("Python" in pattern for pattern in patterns):
            if phase == "coding":
                guidance.extend([
                    "- Follow Python PEP 8 style guidelines",
                    "- Use type hints for better code clarity",
                    "- Consider existing module structure for new code"
                ])
            elif phase == "testing":
                guidance.append("- Use pytest or unittest following project conventions")
        
        # CLI-specific guidance
        if any("CLI" in pattern for pattern in patterns):
            if phase in ["coding", "planning"]:
                guidance.extend([
                    "- Maintain consistency with existing CLI patterns",
                    "- Follow established command structure"
                ])
        
        # Dataclass-specific guidance
        if any("Dataclass" in pattern for pattern in patterns):
            if phase == "coding":
                guidance.append("- Use dataclasses for data models following existing patterns")
        
        # Architecture-specific guidance
        if any("Modular" in pattern for pattern in patterns):
            if phase in ["planning", "coding"]:
                guidance.append("- Maintain modular architecture principles")
        
        # MCP-specific guidance
        if any("MCP" in pattern for pattern in patterns):
            if phase in ["planning", "coding"]:
                guidance.append("- Follow MCP (Model Context Protocol) patterns and conventions")
        
        return guidance
    
    def format_directory_tree(self, structure: Dict, level: int = 0) -> str:
        """Format directory structure as tree"""
        if not structure:
            return "No project structure analyzed"
        
        lines = []
        items = list(structure.items())
        
        for i, (item, children) in enumerate(items):
            is_last = i == len(items) - 1
            
            # Create the tree prefix
            if level == 0:
                prefix = ""
                connector = ""
            else:
                prefix = "│   " * (level - 1) if level > 1 else ""
                connector = "└── " if is_last else "├── "
            
            # Handle file vs directory detection (files have empty dict, directories have content)
            is_file = isinstance(children, dict) and len(children) == 0
            
            if is_file:
                # File - add emoji prefix for display only
                lines.append(f"{prefix}{connector}📄 {item}")
            else:
                # Directory
                lines.append(f"{prefix}{connector}{item}/")
                
                # Add children if they exist
                if isinstance(children, dict) and children:
                    child_tree = self.format_directory_tree(children, level + 1)
                    if child_tree:
                        child_lines = child_tree.split('\n')
                        for child_line in child_lines:
                            if child_line.strip():  # Skip empty lines
                                # Add proper prefix for child lines
                                if level == 0:
                                    # For top level, add the appropriate prefix
                                    if not is_last:
                                        # If this is not the last item at top level, add │ prefix
                                        lines.append(f"│   {child_line}")
                                    else:
                                        # If this is the last item at top level, add space prefix
                                        lines.append(f"    {child_line}")
                                else:
                                    # For nested levels, maintain the existing logic
                                    if is_last:
                                        # If this is the last item, use spaces instead of │
                                        adjusted_line = child_line.replace("│   " * level, "    " * level, 1)
                                    else:
                                        adjusted_line = child_line
                                    lines.append(adjusted_line)
        
        return '\n'.join(lines) 