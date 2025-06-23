"""Tests for context generator module."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


import pytest
from unittest.mock import Mock, patch
from fastmcp.dhafnck_mcp.infrastructure.services.legacy.project_analyzer.context_generator import ContextGenerator


class TestContextGenerator:
    """Test the ContextGenerator class functionality"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.context_generator = ContextGenerator()
    
    def test_init(self):
        """Test ContextGenerator initialization"""
        generator = ContextGenerator()
        assert generator is not None
    
    def test_generate_context_summary_empty_inputs(self):
        """Test context summary generation with empty inputs"""
        result = self.context_generator.generate_context_summary({}, [], [])
        
        assert "## Project Context Analysis" in result
        assert "Technology Stack" not in result
        assert "Key Dependencies" not in result
        assert "Project Structure Insights" not in result
    
    def test_generate_context_summary_with_patterns(self):
        """Test context summary generation with patterns"""
        patterns = ["Python", "CLI", "Dataclass", "Modular", "MCP"]
        
        result = self.context_generator.generate_context_summary({}, patterns, [])
        
        assert "## Project Context Analysis" in result
        assert "### Technology Stack" in result
        assert "- Python" in result
        assert "- CLI" in result
        assert "- Dataclass" in result
        assert "- Modular" in result
        assert "- MCP" in result
    
    def test_generate_context_summary_with_dependencies(self):
        """Test context summary generation with dependencies"""
        dependencies = ["fastapi", "pydantic", "pytest", "uvicorn", "sqlalchemy", "redis", "celery", "docker"]
        
        result = self.context_generator.generate_context_summary({}, [], dependencies)
        
        assert "## Project Context Analysis" in result
        assert "### Key Dependencies" in result
        assert "- fastapi" in result
        assert "- pydantic" in result
        assert "- pytest" in result
        assert "- uvicorn" in result
        assert "- sqlalchemy" in result
        assert "- redis" in result
        assert "- celery" in result
        assert "- docker" in result
    
    def test_generate_context_summary_limits_patterns(self):
        """Test that patterns are limited to top 5"""
        patterns = ["Pattern1", "Pattern2", "Pattern3", "Pattern4", "Pattern5", "Pattern6", "Pattern7"]
        
        result = self.context_generator.generate_context_summary({}, patterns, [])
        
        # Should only include first 5 patterns
        assert "- Pattern1" in result
        assert "- Pattern2" in result
        assert "- Pattern3" in result
        assert "- Pattern4" in result
        assert "- Pattern5" in result
        assert "- Pattern6" not in result
        assert "- Pattern7" not in result
    
    def test_generate_context_summary_limits_dependencies(self):
        """Test that dependencies are limited to top 8"""
        dependencies = [f"dep{i}" for i in range(1, 12)]  # 11 dependencies
        
        result = self.context_generator.generate_context_summary({}, [], dependencies)
        
        # Should only include first 8 dependencies
        for i in range(1, 9):
            assert f"- dep{i}" in result
        
        # Should not include dependencies 9, 10, 11
        assert "- dep9" not in result
        assert "- dep10" not in result
        assert "- dep11" not in result
    
    def test_generate_context_summary_with_structure_insights(self):
        """Test context summary generation with project structure"""
        structure = {
            "src": {"main.py": {}, "utils.py": {}},
            "tests": {"test_main.py": {}},
            "lib": {"helper.py": {}},
            "requirements.txt": {}
        }
        
        result = self.context_generator.generate_context_summary(structure, [], [])
        
        assert "### Project Structure Insights" in result
        assert "- Modular architecture with src/ directory" in result
        assert "- Test suite present" in result
        assert "- Library/component structure detected" in result
        assert "- Python dependency management configured" in result
    
    def test_generate_context_summary_different_phases(self):
        """Test context summary generation with different phases"""
        phases = ["planning", "coding", "testing", "review"]
        
        for phase in phases:
            result = self.context_generator.generate_context_summary({}, [], [], phase)
            assert f"### {phase.title()} Phase Context" in result
    
    def test_get_phase_specific_context_planning(self):
        """Test phase-specific context for planning phase"""
        result = self.context_generator._get_phase_specific_context("planning", [])
        
        assert "### Planning Phase Context" in result
        assert "Consider existing project patterns when designing new features" in result
        assert "Leverage established architecture and conventions" in result
        assert "Plan for integration with existing components" in result
        assert "Analyze current project structure for optimal placement" in result
    
    def test_get_phase_specific_context_coding(self):
        """Test phase-specific context for coding phase"""
        result = self.context_generator._get_phase_specific_context("coding", [])
        
        assert "### Coding Phase Context" in result
        assert "Follow established coding patterns and conventions" in result
        assert "Maintain consistency with existing architecture" in result
        assert "Consider integration points with current components" in result
    
    def test_get_phase_specific_context_testing(self):
        """Test phase-specific context for testing phase"""
        result = self.context_generator._get_phase_specific_context("testing", [])
        
        assert "### Testing Phase Context" in result
        assert "Test against existing project patterns and conventions" in result
        assert "Ensure compatibility with current architecture" in result
        assert "Validate integration points with existing components" in result
        assert "Follow established testing patterns" in result
    
    def test_get_phase_specific_context_review(self):
        """Test phase-specific context for review phase"""
        result = self.context_generator._get_phase_specific_context("review", [])
        
        assert "### Review Phase Context" in result
        assert "Verify adherence to established project patterns" in result
        assert "Check consistency with existing code style" in result
        assert "Validate architectural decisions align with project structure" in result
        assert "Ensure quality standards match project conventions" in result
    
    def test_get_phase_specific_context_unknown_phase(self):
        """Test phase-specific context for unknown phase"""
        result = self.context_generator._get_phase_specific_context("unknown", [])
        
        assert "### Unknown Phase Context" in result
        assert "Focus on unknown activities according to project patterns" in result
    
    def test_get_pattern_specific_guidance_python_coding(self):
        """Test pattern-specific guidance for Python in coding phase"""
        patterns = ["Python", "CLI"]
        
        result = self.context_generator._get_pattern_specific_guidance("coding", patterns)
        
        assert "- Follow Python PEP 8 style guidelines" in result
        assert "- Use type hints for better code clarity" in result
        assert "- Consider existing module structure for new code" in result
        assert "- Maintain consistency with existing CLI patterns" in result
        assert "- Follow established command structure" in result
    
    def test_get_pattern_specific_guidance_python_testing(self):
        """Test pattern-specific guidance for Python in testing phase"""
        patterns = ["Python"]
        
        result = self.context_generator._get_pattern_specific_guidance("testing", patterns)
        
        assert "- Use pytest or unittest following project conventions" in result
    
    def test_get_pattern_specific_guidance_cli_planning(self):
        """Test pattern-specific guidance for CLI in planning phase"""
        patterns = ["CLI"]
        
        result = self.context_generator._get_pattern_specific_guidance("planning", patterns)
        
        assert "- Maintain consistency with existing CLI patterns" in result
        assert "- Follow established command structure" in result
    
    def test_get_pattern_specific_guidance_dataclass_coding(self):
        """Test pattern-specific guidance for Dataclass in coding phase"""
        patterns = ["Dataclass"]
        
        result = self.context_generator._get_pattern_specific_guidance("coding", patterns)
        
        assert "- Use dataclasses for data models following existing patterns" in result
    
    def test_get_pattern_specific_guidance_modular_planning(self):
        """Test pattern-specific guidance for Modular in planning phase"""
        patterns = ["Modular"]
        
        result = self.context_generator._get_pattern_specific_guidance("planning", patterns)
        
        assert "- Maintain modular architecture principles" in result
    
    def test_get_pattern_specific_guidance_mcp_coding(self):
        """Test pattern-specific guidance for MCP in coding phase"""
        patterns = ["MCP"]
        
        result = self.context_generator._get_pattern_specific_guidance("coding", patterns)
        
        assert "- Follow MCP (Model Context Protocol) patterns and conventions" in result
    
    def test_get_pattern_specific_guidance_no_matching_patterns(self):
        """Test pattern-specific guidance with no matching patterns"""
        patterns = ["UnknownPattern"]
        
        result = self.context_generator._get_pattern_specific_guidance("coding", patterns)
        
        assert result == []
    
    def test_format_directory_tree_empty(self):
        """Test directory tree formatting with empty structure"""
        result = self.context_generator.format_directory_tree({})
        
        assert result == "No project structure analyzed"
    
    def test_format_directory_tree_simple(self):
        """Test directory tree formatting with simple structure"""
        structure = {
            "file1.py": {},
            "dir1": {
                "file2.py": {}
            }
        }
        
        result = self.context_generator.format_directory_tree(structure)
        
        assert "📄 file1.py" in result
        assert "dir1/" in result
        assert "📄 file2.py" in result
    
    def test_format_directory_tree_complex(self):
        """Test directory tree formatting with complex nested structure"""
        structure = {
            "src": {
                "main.py": {},
                "utils": {
                    "helper.py": {},
                    "config.py": {}
                }
            },
            "tests": {
                "test_main.py": {}
            },
            "README.md": {}
        }
        
        result = self.context_generator.format_directory_tree(structure)
        
        # Check that all items are present
        assert "src/" in result
        assert "📄 main.py" in result
        assert "utils/" in result
        assert "📄 helper.py" in result
        assert "📄 config.py" in result
        assert "tests/" in result
        assert "📄 test_main.py" in result
        assert "📄 README.md" in result
        
        # Check tree structure formatting
        lines = result.split('\n')
        assert len(lines) > 0
    
    def test_format_directory_tree_deep_nesting(self):
        """Test directory tree formatting with deep nesting"""
        structure = {
            "level1": {
                "level2": {
                    "level3": {
                        "deep_file.py": {}
                    }
                }
            }
        }
        
        result = self.context_generator.format_directory_tree(structure)
        
        assert "level1/" in result
        assert "level2/" in result
        assert "level3/" in result
        assert "📄 deep_file.py" in result
    
    def test_format_directory_tree_multiple_files_and_dirs(self):
        """Test directory tree formatting with multiple files and directories at same level"""
        structure = {
            "file1.py": {},
            "file2.py": {},
            "dir1": {
                "subfile1.py": {}
            },
            "dir2": {
                "subfile2.py": {}
            }
        }
        
        result = self.context_generator.format_directory_tree(structure)
        
        # All items should be present
        assert "📄 file1.py" in result
        assert "📄 file2.py" in result
        assert "dir1/" in result
        assert "dir2/" in result
        assert "📄 subfile1.py" in result
        assert "📄 subfile2.py" in result 