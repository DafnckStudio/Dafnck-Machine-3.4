"""
Test Document Manager Integration
Tests the document management system integration with the MCP server.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

from fastmcp.task_management.domain.document_manager import DocumentManager
from fastmcp.task_management.domain.document_entities import DocumentType, DocumentCategory


class TestDocumentManagerIntegration:
    """Test document manager integration with MCP tools"""
    
    def setup_method(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.document_manager = DocumentManager(base_path=self.temp_dir)
    
    def teardown_method(self):
        """Cleanup test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_document_manager_initialization(self):
        """Test document manager initializes correctly"""
        assert self.document_manager.base_path == Path(self.temp_dir)
        assert self.document_manager.index is not None
        assert len(self.document_manager.index.location_rules) > 0
    
    def test_scan_directory_basic(self):
        """Test basic directory scanning functionality"""
        # Create test files
        test_file = Path(self.temp_dir) / "test.py"
        test_file.write_text("# Test Python file")
        
        doc_file = Path(self.temp_dir) / "docs" / "readme.md"
        doc_file.parent.mkdir(exist_ok=True)
        doc_file.write_text("# Test Documentation")
        
        # Scan directory
        result = self.document_manager.scan_directory(project_id="test_project")
        
        assert result["success"] is True
        assert result["added"] == 2
        assert result["total_documents"] == 2
    
    def test_add_document_manually(self):
        """Test manually adding a document"""
        # Create test file
        test_file = Path(self.temp_dir) / "manual.py"
        test_file.write_text("# Manual test file")
        
        # Add document
        result = self.document_manager.add_document(
            path="manual.py",
            project_id="test_project",
            tags=["manual", "test"],
            category="code"
        )
        
        assert result["success"] is True
        assert "document" in result
        assert result["document"]["name"] == "manual.py"
        assert result["document"]["category"] == "code"
        assert "manual" in result["document"]["tags"]
    
    def test_get_document(self):
        """Test getting document by path"""
        # Create and add test file
        test_file = Path(self.temp_dir) / "get_test.py"
        test_file.write_text("# Get test file")
        
        add_result = self.document_manager.add_document(
            path="get_test.py",
            project_id="test_project"
        )
        
        # Get document by path
        result = self.document_manager.get_document(path="get_test.py")
        
        assert result["success"] is True
        assert "document" in result
        assert result["document"]["name"] == "get_test.py"
        assert result["document"]["access_count"] == 1
    
    def test_list_documents_with_filter(self):
        """Test listing documents with category filter"""
        # Create test files
        py_file = Path(self.temp_dir) / "test.py"
        py_file.write_text("# Python file")
        
        md_file = Path(self.temp_dir) / "docs" / "test.md"
        md_file.parent.mkdir(exist_ok=True)
        md_file.write_text("# Markdown file")
        
        # Scan directory
        self.document_manager.scan_directory(project_id="test_project")
        
        # List code documents
        result = self.document_manager.list_documents(category="code")
        
        assert result["success"] is True
        assert len(result["documents"]) == 1
        assert result["documents"][0]["name"] == "test.py"
    
    def test_add_dependency(self):
        """Test adding dependencies between documents"""
        # Create test files
        file1 = Path(self.temp_dir) / "file1.py"
        file1.write_text("# File 1")
        file2 = Path(self.temp_dir) / "file2.py"
        file2.write_text("# File 2")
        
        # Add documents
        result1 = self.document_manager.add_document("file1.py", "test_project")
        result2 = self.document_manager.add_document("file2.py", "test_project")
        
        doc1_id = result1["document"]["id"]
        doc2_id = result2["document"]["id"]
        
        # Add dependency
        dep_result = self.document_manager.add_dependency(
            source_id=doc1_id,
            target_id=doc2_id,
            dependency_type="one_to_one",
            relationship_nature="imports",
            strength="strong"
        )
        
        assert dep_result["success"] is True
        assert "dependency" in dep_result
        assert dep_result["dependency"]["source_document_id"] == doc1_id
        assert dep_result["dependency"]["target_document_id"] == doc2_id
    
    def test_validate_locations(self):
        """Test location validation against rules"""
        # Create files in wrong locations
        wrong_rule = Path(self.temp_dir) / "wrong_rule.mdc"
        wrong_rule.write_text("# Rule in wrong place")
        
        wrong_doc = Path(self.temp_dir) / "wrong_doc.md"
        wrong_doc.write_text("# Doc in wrong place")
        
        # Add documents
        self.document_manager.add_document("wrong_rule.mdc", "test_project")
        self.document_manager.add_document("wrong_doc.md", "test_project")
        
        # Validate locations
        result = self.document_manager.validate_locations("test_project")
        
        assert result["success"] is True
        assert result["total_violations"] > 0
        assert len(result["violations"]) > 0
    
    def test_search_knowledge_empty(self):
        """Test knowledge search with no entries"""
        result = self.document_manager.search_knowledge("test query")
        
        assert result["success"] is True
        assert result["total"] == 0
        assert result["results"] == []
    
    def test_get_statistics(self):
        """Test getting document statistics"""
        # Create test files
        py_file = Path(self.temp_dir) / "stats.py"
        py_file.write_text("# Stats test")
        
        md_file = Path(self.temp_dir) / "docs" / "stats.md"
        md_file.parent.mkdir(exist_ok=True)
        md_file.write_text("# Stats doc")
        
        # Scan directory
        self.document_manager.scan_directory(project_id="test_project")
        
        # Get statistics
        result = self.document_manager.get_statistics("test_project")
        
        assert result["success"] is True
        stats = result["statistics"]
        assert stats["total_documents"] == 2
        assert "by_category" in stats
        assert "by_type" in stats
        assert stats["total_dependencies"] == 0
        assert stats["total_knowledge_entries"] == 0
    
    def test_document_type_detection(self):
        """Test document type detection"""
        manager = self.document_manager
        
        assert manager._detect_document_type("test.py") == DocumentType.PYTHON
        assert manager._detect_document_type("test.md") == DocumentType.MARKDOWN
        assert manager._detect_document_type("test.mdc") == DocumentType.RULE
        assert manager._detect_document_type("test.json") == DocumentType.JSON
        assert manager._detect_document_type("test.ts") == DocumentType.TYPESCRIPT
        assert manager._detect_document_type("test.txt") == DocumentType.TEXT
        assert manager._detect_document_type("test.unknown") == DocumentType.OTHER
    
    def test_document_category_detection(self):
        """Test document category detection"""
        manager = self.document_manager
        
        assert manager._detect_document_category(".cursor/rules/test.mdc", DocumentType.RULE) == DocumentCategory.RULES
        assert manager._detect_document_category("docs/test.md", DocumentType.MARKDOWN) == DocumentCategory.DOCUMENTATION
        assert manager._detect_document_category("test/test.py", DocumentType.PYTHON) == DocumentCategory.TESTS
        assert manager._detect_document_category("config/test.json", DocumentType.JSON) == DocumentCategory.CONFIGURATION
        assert manager._detect_document_category("src/test.py", DocumentType.PYTHON) == DocumentCategory.CODE
        assert manager._detect_document_category("random/test.txt", DocumentType.TEXT) == DocumentCategory.OTHER


class TestDocumentManagerMCPIntegration:
    """Test MCP tool integration"""
    
    def test_mcp_tool_registration(self):
        """Test that manage_document tool can be registered"""
        from fastmcp.task_management.interface.consolidated_mcp_tools import ToolConfig, ToolRegistrationOrchestrator
        from fastmcp.task_management.domain.task_repository_factory import TaskRepositoryFactory
        from fastmcp.task_management.domain.services.auto_rule_generator import AutoRuleGenerator
        from fastmcp.task_management.interface.consolidated_mcp_tools import ProjectManager, PathResolver
        from fastmcp.task_management.application.use_cases.call_agent_use_case import CallAgentUseCase
        
        # Mock dependencies
        config = ToolConfig()
        path_resolver = PathResolver()
        project_manager = ProjectManager(path_resolver)
        repository_factory = Mock(spec=TaskRepositoryFactory)
        auto_rule_generator = Mock(spec=AutoRuleGenerator)
        call_agent_use_case = Mock(spec=CallAgentUseCase)
        
        # Create task handler mock
        task_handler = Mock()
        
        # Create orchestrator
        orchestrator = ToolRegistrationOrchestrator(
            config=config,
            task_handler=task_handler,
            project_manager=project_manager,
            call_agent_use_case=call_agent_use_case
        )
        
        # Check that document manager is initialized
        assert hasattr(orchestrator, '_document_manager')
        assert orchestrator._document_manager is not None
        
        # Check that manage_document is enabled in config
        assert config.is_enabled("manage_document") is True


if __name__ == "__main__":
    pytest.main([__file__]) 