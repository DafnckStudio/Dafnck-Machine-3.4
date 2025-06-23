"""Tests for project_analyzer facade module."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src'))


import pytest
from unittest.mock import Mock, patch
from fastmcp.task_management.infrastructure.services.legacy.project_analyzer import (
    ProjectAnalyzer,
    ProjectAnalysisResult,
    ProjectAnalysisConfig,
    ProjectType,
    FrameworkType,
    DependencyType,
    ProjectStructure,
    ProjectMetadata,
    Dependency,
    FileInfo
)


class TestProjectAnalyzerFacade:
    """Test the project analyzer facade imports and exports"""
    
    def test_imports_available(self):
        """Test that all expected imports are available"""
        # Test that the main class is available
        assert ProjectAnalyzer is not None
        
        # Test that all model classes are available
        assert ProjectAnalysisResult is not None
        assert ProjectAnalysisConfig is not None
        assert ProjectType is not None
        assert FrameworkType is not None
        assert DependencyType is not None
        assert ProjectStructure is not None
        assert ProjectMetadata is not None
        assert Dependency is not None
        assert FileInfo is not None
    
    def test_all_exports_defined(self):
        """Test that __all__ contains all expected exports"""
        from fastmcp.task_management.infrastructure.services.legacy import project_analyzer
        
        expected_exports = [
            'ProjectAnalyzer',
            'ProjectAnalysisResult', 
            'ProjectAnalysisConfig',
            'ProjectType',
            'FrameworkType', 
            'DependencyType',
            'ProjectStructure',
            'ProjectMetadata',
            'Dependency',
            'FileInfo',
            'PatternDetector',
            'StructureAnalyzer',
            'DependencyAnalyzer',
            'FileOperations',
            'ContextGenerator'
        ]
        
        assert hasattr(project_analyzer, '__all__')
        assert set(project_analyzer.__all__) == set(expected_exports)
        
        # Check if all expected exports are in __all__
        for export in expected_exports:
            assert export in project_analyzer.__all__, f"Missing export: {export}"
        
        # Check if __all__ has any unexpected exports
        for export in project_analyzer.__all__:
            assert export in expected_exports, f"Unexpected export: {export}"
        
        # Print differences for debugging
        print(f"Expected: {set(expected_exports)}")
        print(f"Actual: {set(project_analyzer.__all__)}")
        print(f"Missing: {set(expected_exports) - set(project_analyzer.__all__)}")
        print(f"Unexpected: {set(project_analyzer.__all__) - set(expected_exports)}")
    
    def test_can_import_all_exports(self):
        """Test that all exports can be imported successfully"""
        from fastmcp.task_management.infrastructure.services.legacy.project_analyzer import (
            ProjectAnalyzer,
            ProjectAnalysisResult,
            ProjectAnalysisConfig,
            ProjectType,
            FrameworkType,
            DependencyType,
            ProjectStructure,
            ProjectMetadata,
            Dependency,
            FileInfo
        )
        
        # Verify all imports are not None
        imports = [
            ProjectAnalyzer,
            ProjectAnalysisResult,
            ProjectAnalysisConfig,
            ProjectType,
            FrameworkType,
            DependencyType,
            ProjectStructure,
            ProjectMetadata,
            Dependency,
            FileInfo
        ]
        
        for import_item in imports:
            assert import_item is not None
    
    def test_module_docstring(self):
        """Test that the module has proper documentation"""
        import fastmcp.task_management.infrastructure.services.legacy.project_analyzer as module
        
        assert module.__doc__ is not None
        assert (
            "Project analyzer module facade" in module.__doc__ or
            "Project analyzer module exports." in module.__doc__
        )
    
    @patch('fastmcp.task_management.infrastructure.services.legacy.project_analyzer.ProjectAnalyzer')
    def test_project_analyzer_can_be_instantiated(self, mock_analyzer):
        """Test that ProjectAnalyzer can be instantiated through the facade"""
        # Mock the ProjectAnalyzer class
        mock_instance = Mock()
        mock_analyzer.return_value = mock_instance
        
        # Import and instantiate
        from fastmcp.task_management.infrastructure.services.legacy.project_analyzer import ProjectAnalyzer
        
        analyzer = ProjectAnalyzer()
        
        # Verify the mock was called
        mock_analyzer.assert_called_once()
        assert analyzer == mock_instance 