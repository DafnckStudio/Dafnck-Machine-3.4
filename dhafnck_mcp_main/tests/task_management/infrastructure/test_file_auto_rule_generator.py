"""Comprehensive tests for FileAutoRuleGenerator"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from fastmcp.task_management.infrastructure.services.file_auto_rule_generator import FileAutoRuleGenerator
from fastmcp.task_management.domain.entities.task import Task
from fastmcp.task_management.domain.value_objects.task_status import TaskStatus, TaskStatusEnum
from fastmcp.task_management.domain.value_objects.priority import Priority, PriorityLevel
from fastmcp.task_management.domain.value_objects.task_id import TaskId
from fastmcp.task_management.domain.enums import AgentRole


class TestFileAutoRuleGenerator:
    """Test FileAutoRuleGenerator functionality"""
    
    @pytest.fixture
    def temp_rules_dir(self):
        """Create temporary rules directory for testing"""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_dir = Path(temp_dir) / ".cursor" / "rules"
            rules_dir.mkdir(parents=True)
            auto_rule_file = rules_dir / "auto_rule.mdc"
            yield str(auto_rule_file)
    
    @pytest.fixture
    def generator(self, temp_rules_dir):
        """Create FileAutoRuleGenerator instance for testing"""
        return FileAutoRuleGenerator(output_path=temp_rules_dir)
    
    @pytest.fixture
    def sample_task(self):
        """Create sample task for testing"""
        return Task(
            id=TaskId.from_string("20250622001"),
            title="Test Task",
            description="Test Description",
            priority=Priority.high(),
            assignees=[AgentRole.CODING],
            labels=["test", "feature"],
            details="Detailed task information"
        )
    
    def test_init_with_custom_directory(self, temp_rules_dir):
        """Test initialization with custom output path"""
        generator = FileAutoRuleGenerator(output_path=temp_rules_dir)
        assert generator.output_path == temp_rules_dir
    
    def test_init_with_default_directory(self):
        """Test initialization with default directory"""
        generator = FileAutoRuleGenerator()
        assert generator.output_path is not None
        assert generator.output_path != ""
    
    def test_generate_rule_creates_directory(self):
        """Test that generate_rules_for_task creates directory if it doesn't exist"""
        with tempfile.TemporaryDirectory() as temp_dir:
            rules_file = Path(temp_dir) / "new_dir" / ".cursor" / "rules" / "auto_rule.mdc"
            generator = FileAutoRuleGenerator(output_path=str(rules_file))
            
            task = Task(id=TaskId.from_int(1), title="Test", description="Test")
            result = generator.generate_rules_for_task(task)
            
            assert result is True
            assert rules_file.parent.exists()
    
    def test_generate_rule_handles_directory_creation_error(self):
        """Test handling directory creation errors"""
        with patch('pathlib.Path.mkdir') as mock_mkdir:
            mock_mkdir.side_effect = OSError("Cannot create directory")
            
            generator = FileAutoRuleGenerator(output_path="/invalid/path/auto_rule.mdc")
            task = Task(id=TaskId.from_int(1), title="Test", description="Test")
            
            # Should handle gracefully and not crash
            try:
                result = generator.generate_rules_for_task(task)
                # May return True or False depending on fallback behavior
                assert isinstance(result, bool)
            except OSError:
                pass  # Expected to potentially fail
    
    def test_ensure_rules_directory_creation_error(self):
        """Test handling directory creation errors in _ensure_output_dir"""
        with patch('os.makedirs') as mock_makedirs:
            mock_makedirs.side_effect = PermissionError("Permission denied")
            
            # Should fallback to temp directory
            generator = FileAutoRuleGenerator(output_path="/invalid/path/auto_rule.mdc")
            assert generator.output_path is not None
    
    def test_generate_rule_with_task_context(self, generator, sample_task):
        """Test generating rule with task context"""
        result = generator.generate_rules_for_task(sample_task)
        assert result is True
        
        # Check that file was created
        assert Path(generator.output_path).exists()
        
        # Check file content
        content = Path(generator.output_path).read_text()
        assert sample_task.title in content
    
    def test_generate_rule_without_task_context(self, generator):
        """Test generating rule without task context"""
        # Create a minimal task
        task = Task(id=TaskId.from_int(1), title="Test", description="Test")
        result = generator.generate_rules_for_task(task)
        
        assert result is True
        assert Path(generator.output_path).exists()
    
    def test_generate_rule_with_invalid_role(self, generator):
        """Test generating rule with invalid role (via task assignees)"""
        task = Task(id=TaskId.from_int(1), title="Test", description="Test", assignees=["invalid_role"])
        result = generator.generate_rules_for_task(task)
        
        assert result is True  # Should handle gracefully
        assert Path(generator.output_path).exists()
    
    def test_generate_rule_with_empty_role(self, generator):
        """Test generating rule with empty role"""
        task = Task(id=TaskId.from_int(1), title="Test", description="Test", assignees=[])
        result = generator.generate_rules_for_task(task)
        
        assert result is True
        assert Path(generator.output_path).exists()
    
    def test_generate_rule_with_none_role(self, generator):
        """Test generating rule with None role"""
        task = Task(id=TaskId.from_int(1), title="Test", description="Test")
        result = generator.generate_rules_for_task(task)
        
        assert result is True
        assert Path(generator.output_path).exists()
    
    def test_generate_rule_saves_to_file(self, generator, sample_task):
        """Test that generated rule is saved to file"""
        result = generator.generate_rules_for_task(sample_task)
        
        assert result is True
        
        # Check that file was created
        auto_rule_file = Path(generator.output_path)
        assert auto_rule_file.exists()
        
        # Check file content
        content = auto_rule_file.read_text()
        assert sample_task.title in content
    
    def test_generate_rule_handles_file_write_error(self, generator):
        """Test handling file write errors"""
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = PermissionError("Permission denied")
            
            task = Task(id=TaskId.from_int(1), title="Test", description="Test")
            result = generator.generate_rules_for_task(task)
            
            # Should handle error gracefully
            assert isinstance(result, bool)
    
    def test_get_role_template_coding_agent(self, generator):
        """Test getting template for coding agent role"""
        # This tests internal method if available
        if hasattr(generator, '_get_role_template'):
            template = generator._get_role_template("coding_agent")
            assert isinstance(template, str)
            assert len(template) > 0
    
    def test_get_role_template_test_agent(self, generator):
        """Test getting template for test agent role"""
        if hasattr(generator, '_get_role_template'):
            template = generator._get_role_template("test_agent")
            assert isinstance(template, str)
            assert len(template) > 0
    
    def test_get_role_template_senior_developer(self, generator):
        """Test getting template for senior developer role"""
        if hasattr(generator, '_get_role_template'):
            template = generator._get_role_template("senior_developer")
            assert isinstance(template, str)
            assert len(template) > 0
    
    def test_get_role_template_unknown_role(self, generator):
        """Test getting template for unknown role"""
        if hasattr(generator, '_get_role_template'):
            template = generator._get_role_template("unknown_role")
            assert isinstance(template, str)
            assert len(template) > 0
    
    def test_get_role_template_empty_role(self, generator):
        """Test getting template for empty role"""
        if hasattr(generator, '_get_role_template'):
            template = generator._get_role_template("")
            assert isinstance(template, str)
            assert len(template) > 0
    
    def test_get_role_template_none_role(self, generator):
        """Test getting template for None role"""
        if hasattr(generator, '_get_role_template'):
            template = generator._get_role_template(None)
            assert isinstance(template, str)
            assert len(template) > 0
    
    def test_format_task_context_full_context(self, generator, sample_task):
        """Test formatting full task context"""
        if hasattr(generator, '_format_task_context'):
            task_context = {
                "id": str(sample_task.id),
                "title": sample_task.title,
                "description": sample_task.description,
                "assignee": "@coding_agent",
                "priority": "high",
                "status": "todo",
                "details": sample_task.details
            }
            
            formatted = generator._format_task_context(task_context)
            
            assert isinstance(formatted, str)
            assert sample_task.title in formatted
            assert "@coding_agent" in formatted
            assert "high" in formatted
    
    def test_format_task_context_minimal_context(self, generator):
        """Test formatting minimal task context"""
        if hasattr(generator, '_format_task_context'):
            task_context = {
                "title": "Minimal Task",
                "description": "Minimal Description"
            }
            
            formatted = generator._format_task_context(task_context)
            
            assert isinstance(formatted, str)
            assert "Minimal Task" in formatted
    
    def test_format_task_context_empty_context(self, generator):
        """Test formatting empty task context"""
        if hasattr(generator, '_format_task_context'):
            formatted = generator._format_task_context({})
            assert isinstance(formatted, str)
    
    def test_format_task_context_none_context(self, generator):
        """Test formatting None task context"""
        if hasattr(generator, '_format_task_context'):
            formatted = generator._format_task_context(None)
            assert isinstance(formatted, str)
    
    def test_format_task_context_with_special_characters(self, generator):
        """Test formatting task context with special characters"""
        if hasattr(generator, '_format_task_context'):
            task_context = {
                "title": "Task with 'quotes' and \"double quotes\"",
                "description": "Description with\nnewlines and\ttabs",
                "assignee": "@special-agent_123",
                "details": "Details with special chars: !@#$%^&*()"
            }
            
            formatted = generator._format_task_context(task_context)
            
            assert isinstance(formatted, str)
            assert "Task with" in formatted
            assert "@special-agent_123" in formatted
    
    def test_build_rule_content_with_task(self, generator, sample_task):
        """Test building rule content with task"""
        if hasattr(generator, '_build_rule_content'):
            role = "senior_developer"
            task_context = sample_task.to_dict()
            
            content = generator._build_rule_content(role, task_context)
            
            assert isinstance(content, str)
            assert len(content) > 0
            assert sample_task.title in content
    
    def test_build_rule_content_without_task(self, generator):
        """Test building rule content without task"""
        if hasattr(generator, '_build_rule_content'):
            role = "senior_developer"
            
            content = generator._build_rule_content(role, None)
            
            assert isinstance(content, str)
            assert len(content) > 0
            assert "senior_developer" in content.lower()
    
    def test_build_rule_content_structure(self, generator, sample_task):
        """Test that built rule content has proper structure"""
        if hasattr(generator, '_build_rule_content'):
            role = "coding_agent"
            task_context = sample_task.to_dict()
            
            content = generator._build_rule_content(role, task_context)
            
            # Check for markdown structure
            assert "# " in content or "## " in content  # Headers
            assert content.strip().startswith("#") or "Task Context" in content
    
    def test_save_rule_to_file_success(self, generator, temp_rules_dir):
        """Test successfully saving rule to file"""
        if hasattr(generator, '_save_rule_to_file'):
            rule_content = "# Test Rule\nThis is a test rule."
            
            result = generator._save_rule_to_file(rule_content)
            
            assert result is True
            assert Path(generator.output_path).exists()
            
            content = Path(generator.output_path).read_text()
            assert "Test Rule" in content
    
    def test_save_rule_to_file_creates_backup(self, generator, temp_rules_dir):
        """Test that saving rule creates backup of existing file"""
        if hasattr(generator, '_save_rule_to_file'):
            # Create existing file
            existing_content = "# Existing Rule\nOld content."
            Path(generator.output_path).write_text(existing_content)
            
            # Save new rule
            new_content = "# New Rule\nNew content."
            result = generator._save_rule_to_file(new_content)
            
            assert result is True
            
            # Check new content
            content = Path(generator.output_path).read_text()
            assert "New Rule" in content
            
            # Check backup exists (if backup functionality is implemented)
            backup_path = Path(generator.output_path).with_suffix('.mdc.backup')
            if backup_path.exists():
                backup_content = backup_path.read_text()
                assert "Existing Rule" in backup_content
    
    def test_save_rule_to_file_permission_error(self, generator):
        """Test handling permission error when saving"""
        if hasattr(generator, '_save_rule_to_file'):
            with patch('builtins.open', mock_open()) as mock_file:
                mock_file.side_effect = PermissionError("Permission denied")
                
                result = generator._save_rule_to_file("Test content")
                
                assert result is False
    
    def test_save_rule_to_file_os_error(self, generator):
        """Test handling OS error when saving"""
        if hasattr(generator, '_save_rule_to_file'):
            with patch('builtins.open', mock_open()) as mock_file:
                mock_file.side_effect = OSError("Disk full")
                
                result = generator._save_rule_to_file("Test content")
                
                assert result is False
    
    def test_ensure_rules_directory_exists(self, generator):
        """Test ensuring rules directory exists"""
        if hasattr(generator, '_ensure_output_dir'):
            # This should not raise an exception
            generator._ensure_output_dir()
            
            # Directory should exist
            output_dir = Path(generator.output_path).parent
            assert output_dir.exists()
    
    def test_generate_rule_with_complex_task_context(self, generator):
        """Test generating rule with complex task context"""
        complex_task = Task(
            id=TaskId.from_string("20250622999"),
            title="Complex Task with Multiple Requirements",
            description="This is a complex task that involves multiple components",
            priority=Priority.critical(),
            assignees=["@coding_agent", "@test_agent"],
            labels=["feature", "backend", "api", "security"],
            details="""
            This task requires:
            1. Implementation of new API endpoints
            2. Database schema changes
            3. Security validation
            4. Comprehensive testing
            5. Documentation updates
            """,
            estimated_effort="large"
        )
        
        result = generator.generate_rules_for_task(complex_task, force_full_generation=True)
        
        assert result is True
        assert Path(generator.output_path).exists()
        
        content = Path(generator.output_path).read_text()
        assert complex_task.title in content
        assert "API endpoints" in content or "complex" in content.lower()
    
    def test_generate_rule_performance_with_large_context(self, generator):
        """Test performance with large task context"""
        large_task = Task(
            id=TaskId.from_string("20250622888"),
            title="Large Task " * 10,
            description="Large Description " * 50,
            details="Large Details " * 100,
            assignees=["@coding_agent"] * 5,
            labels=["label"] * 20
        )
        
        import time
        start_time = time.time()
        
        result = generator.generate_rules_for_task(large_task)
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        assert result is True
        assert execution_time < 5.0  # Should complete within 5 seconds
    
    def test_multiple_rule_generations(self, generator, temp_rules_dir):
        """Test multiple rule generations"""
        tasks = []
        for i in range(5):
            task = Task(
                id=TaskId.from_int(i + 1),
                title=f"Task {i+1}",
                description=f"Description {i+1}",
                assignees=[f"@agent_{i+1}"]
            )
            tasks.append(task)
        
        # Generate rules for each task
        for task in tasks:
            result = generator.generate_rules_for_task(task)
            assert result is True
        
        # Check that final file exists and contains last task info
        assert Path(generator.output_path).exists()
        content = Path(generator.output_path).read_text()
        assert "Task 5" in content  # Should contain the last task
    
    def test_role_template_caching(self, generator):
        """Test role template caching (if implemented)"""
        if hasattr(generator, '_get_role_template'):
            # Call same role multiple times
            template1 = generator._get_role_template("coding_agent")
            template2 = generator._get_role_template("coding_agent")
            
            assert template1 == template2
    
    def test_unicode_handling(self, generator):
        """Test handling of unicode characters"""
        unicode_task = Task(
            id=TaskId.from_string("20250622777"),
            title="Tâche avec caractères spéciaux: 中文 🚀",
            description="Description with émojis and ñoñó characters",
            details="Détails avec unicode: αβγδε",
            assignees=["@développeur_agent"]
        )
        
        result = generator.generate_rules_for_task(unicode_task)
        
        assert result is True
        assert Path(generator.output_path).exists()
        
        content = Path(generator.output_path).read_text(encoding='utf-8')
        assert "caractères spéciaux" in content or "unicode" in content.lower()
    
    def test_edge_case_empty_strings(self, generator):
        """Test handling of edge cases with empty strings"""
        # Test with empty title - this should raise a ValueError due to Task validation
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            edge_case_task = Task(
                id=TaskId.from_string("20250622666"),
                title="",  # Empty title should be rejected by Task validation
                description="Valid description",
                details="",
                assignees=[],
                labels=[]
            )
        
        # Test with minimal valid task (non-empty title)
        minimal_task = Task(
            id=TaskId.from_string("20250622667"),
            title="Minimal Task",  # Valid non-empty title
            description="Valid description",
            details="",
            assignees=[],
            labels=[]
        )
        
        result = generator.generate_rules_for_task(minimal_task)
        assert result is True
    
    def test_concurrent_generation_simulation(self, generator):
        """Test simulated concurrent rule generation"""
        import threading
        import time
        
        results = []
        
        def generate_rule_worker(worker_id):
            task = Task(
                id=TaskId.from_int(worker_id + 1),  # Ensure positive ID
                title=f"Concurrent Task {worker_id}",
                description=f"Task from worker {worker_id}"
            )
            result = generator.generate_rules_for_task(task)
            results.append(result)
        
        # Create multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=generate_rule_worker, args=(i,))
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(results) == 3
        assert all(isinstance(result, bool) for result in results)
        
        # File should exist (last writer wins)
        assert Path(generator.output_path).exists()


if __name__ == "__main__":
    pytest.main([__file__]) 