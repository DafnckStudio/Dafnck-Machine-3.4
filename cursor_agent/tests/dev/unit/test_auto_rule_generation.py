"""Unit Tests for Auto Rule Generation System"""

import pytest
import os
import sys
import tempfile
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import shutil

# Import domain and infrastructure classes
from task_mcp.domain.entities.task import Task
from task_mcp.domain.value_objects.task_id import TaskId
from task_mcp.domain.value_objects.task_status import TaskStatus
from task_mcp.domain.value_objects.priority import Priority
from task_mcp.domain.events.task_events import TaskRetrieved
from task_mcp.infrastructure.services.file_auto_rule_generator import FileAutoRuleGenerator
from task_mcp.application.use_cases.get_task import GetTaskUseCase
from task_mcp.domain.exceptions import TaskNotFoundError


class TestAutoRuleGeneration:
    """Test suite for auto rule generation system"""

    def setup_method(self):
        """Set up test fixtures"""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.test_output_path = os.path.join(self.test_dir, "test_auto_rule.mdc")
        
        # Create mock task for testing
        self.mock_task = Task(
            id=TaskId.from_int(123),
            title="Test Auto Rule Generation",
            description="Testing the auto rule generation system",
            status=TaskStatus.todo(),
            priority=Priority.high(),
            details="Test that auto_rule.mdc is generated when get_task is called",
            estimated_effort="1h",
            assignees=["context_engineer"],
            labels=["auto-generation", "testing", "rules"],
            dependencies=[],
            subtasks=[],
            due_date="2025-01-23"
        )

    def teardown_method(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.test_dir)

    def test_file_auto_rule_generator_initialization(self):
        """Test FileAutoRuleGenerator initialization"""
        generator = FileAutoRuleGenerator(self.test_output_path)
        assert generator._output_path == self.test_output_path
        assert os.path.exists(os.path.dirname(self.test_output_path))

    def test_file_auto_rule_generator_default_path(self):
        """Test FileAutoRuleGenerator with default output path"""
        generator = FileAutoRuleGenerator()
        # Check that the path ends with the expected pattern (now using absolute paths)
        assert generator._output_path.endswith(".cursor/rules/auto_rule.mdc")
        # Also verify it's an absolute path
        assert os.path.isabs(generator._output_path)

    def test_validate_task_data_valid(self):
        """Test task data validation with valid data"""
        generator = FileAutoRuleGenerator(self.test_output_path)
        task_data = {
            "id": 123,
            "title": "Test Task",
            "description": "Test description",
            "status": "todo",
            "priority": "high"
        }
        assert generator.validate_task_data(task_data) == True

    def test_validate_task_data_invalid(self):
        """Test task data validation with invalid data"""
        generator = FileAutoRuleGenerator(self.test_output_path)
        task_data = {
            "id": 123,
            "title": "Test Task"
            # Missing required fields
        }
        assert generator.validate_task_data(task_data) == False

    def test_get_supported_roles(self):
        """Test getting supported roles"""
        generator = FileAutoRuleGenerator(self.test_output_path)
        roles = generator.get_supported_roles()
        
        # Should return all available roles from AgentRole enum
        assert isinstance(roles, list)
        assert len(roles) > 60  # Should have many roles (currently 68)
        
        # Check that some key roles are included
        key_roles = [
            "coding_agent", "devops_agent", "functional_tester_agent",
            "code_reviewer_agent", "security_auditor_agent", "documentation_agent",
            "task_planning_agent", "core_concept_agent"
        ]
        
        for role in key_roles:
            assert role in roles

    def test_generate_rules_for_task_with_forced_fallback(self):
        """Test rule generation with forced fallback to simple generation"""
        generator = FileAutoRuleGenerator(self.test_output_path)
        
        # In test environment, it should automatically use simple generation
        result = generator.generate_rules_for_task(self.mock_task)
        
        assert result == True
        assert os.path.exists(self.test_output_path)
        
        with open(self.test_output_path, 'r') as f:
            content = f.read()
            # Check for fallback content (should contain task ID and basic info)
            task_id = str(self.mock_task.id.value)
            # The content should contain the task ID in some form
            assert task_id in content or "Context & State Management Engineer" in content

    def test_generate_rules_for_task_fallback(self):
        """Test fallback rule generation when complex generation fails"""
        generator = FileAutoRuleGenerator(self.test_output_path)
        
        # This should use fallback generation in test environment
        result = generator.generate_rules_for_task(self.mock_task)
        
        assert result == True
        assert os.path.exists(self.test_output_path)
        
        with open(self.test_output_path, 'r') as f:
            content = f.read()
            task_id = str(self.mock_task.id.value)
            # The content should contain the task ID in some form
            assert task_id in content or "Auto-Generated Rules" in content

    def test_generate_simple_rules_content(self):
        """Test simple rule generation content structure"""
        generator = FileAutoRuleGenerator(self.test_output_path)
        
        # Generate simple rules by calling the actual method
        generator._generate_simple_rules(self.mock_task)
        
        # Check that the file was created and has content
        assert os.path.exists(self.test_output_path)
        
        with open(self.test_output_path, 'r') as f:
            result = f.read()
        
        assert result is not None
        assert len(result) > 50  # Should have reasonable content
        
        task_id = str(self.mock_task.id.value)
        # The content should contain the task ID in some form
        assert task_id in result or "Auto-Generated Rules" in result

    def test_task_retrieved_event_generation(self):
        """Test that TaskRetrieved event is generated when task is marked as retrieved"""
        task = self.mock_task
        
        # Initially no events
        assert len(task.get_events()) == 0
        
        # Mark as retrieved
        task.mark_as_retrieved()
        
        # Check event was generated
        events = task.get_events()
        assert len(events) == 1
        assert isinstance(events[0], TaskRetrieved)
        assert events[0].task_id == task.id

    def test_get_task_use_case_triggers_auto_rule_generation(self):
        """Test that GetTaskUseCase triggers auto rule generation"""
        # Create mocks
        mock_repository = Mock()
        mock_auto_rule_generator = Mock()
        
        # Setup repository to return our test task
        mock_repository.find_by_id.return_value = self.mock_task
        
        # Create use case
        use_case = GetTaskUseCase(mock_repository, mock_auto_rule_generator)
        
        # Execute use case
        result = use_case.execute(123)
        
        # Verify task was found
        mock_repository.find_by_id.assert_called_once()
        
        # Verify auto rule generation was triggered
        mock_auto_rule_generator.generate_rules_for_task.assert_called_once_with(
            self.mock_task,
            force_full_generation=False
        )
        
        # Verify result
        assert result is not None
        assert str(result.id).endswith("123")

    def test_get_task_use_case_task_not_found(self):
        """Test GetTaskUseCase when task is not found"""
        # Create mocks
        mock_repository = Mock()
        mock_auto_rule_generator = Mock()
        
        # Setup repository to return None (task not found)
        mock_repository.find_by_id.return_value = None
        
        # Create use case
        use_case = GetTaskUseCase(mock_repository, mock_auto_rule_generator)
        
        # Execute use case - should raise TaskNotFoundError
        with pytest.raises(TaskNotFoundError):
            use_case.execute(999)
        
        # Verify task was searched for
        mock_repository.find_by_id.assert_called_once()
        
        # Verify auto rule generation was NOT triggered
        mock_auto_rule_generator.generate_rules_for_task.assert_not_called()

    def test_auto_rule_generation_with_different_roles(self):
        """Test auto rule generation with different assignee roles"""
        # Updated to use AgentRole enum values (slug format)
        roles_to_test = [
            "coding-agent",
            "qa-engineer", 
            "devops-engineer",
            "security-engineer",
            "technical-writer"
        ]
        
        for role in roles_to_test:
            # Create task with specific role
            task = Task(
                id=TaskId.from_int(200 + hash(role) % 100),
                title=f"Test Task for {role}",
                description=f"Testing auto rule generation for {role} role",
                status=TaskStatus.todo(),
                priority=Priority.medium(),
                assignees=[role],
                labels=["auto-generation", "testing", "rules"],
                dependencies=[],
                subtasks=[],
                due_date="2025-01-23"
            )
            
            # Generate rules
            test_path = os.path.join(self.test_dir, f"test_auto_rule_{role}.mdc")
            generator = FileAutoRuleGenerator(test_path)
            result = generator.generate_rules_for_task(task)
            
            # Verify generation succeeded
            assert result == True
            assert os.path.exists(test_path)
            
            # Verify role-specific content
            with open(test_path, 'r') as f:
                content = f.read()
                assert role in content
                
            # Clean up
            os.unlink(test_path)

    def test_auto_rule_generation_error_handling(self):
        """Test error handling in auto rule generation"""
        # Test with invalid output path (read-only directory)
        if os.name != 'nt':  # Skip on Windows due to permission handling differences
            readonly_dir = os.path.join(self.test_dir, "readonly")
            os.makedirs(readonly_dir)
            os.chmod(readonly_dir, 0o444)  # Read-only
            
            readonly_path = os.path.join(readonly_dir, "auto_rule.mdc")
            generator = FileAutoRuleGenerator(readonly_path)
            
            # Should still return True due to improved error handling and fallback
            result = generator.generate_rules_for_task(self.mock_task)
            assert result == True
            
            # Check that a fallback file was created in temp directory
            import tempfile
            fallback_dir = tempfile.gettempdir()
            fallback_file_found = False
            for f in os.listdir(fallback_dir):
                if f.startswith("auto_rule_") and f.endswith(".mdc"):
                    fallback_file_found = True
                    # Clean up the created temp file
                    os.unlink(os.path.join(fallback_dir, f))
                    break
            
            assert fallback_file_found, "Fallback file was not created in temp directory"
            
            # Clean up
            os.chmod(readonly_dir, 0o755)
            shutil.rmtree(readonly_dir)

    def test_auto_rule_generation_file_permissions(self):
        """Test that generated files have correct permissions"""
        generator = FileAutoRuleGenerator(self.test_output_path)
        result = generator.generate_rules_for_task(self.mock_task)
        
        assert result == True
        assert os.path.exists(self.test_output_path)
        
        # Check file is readable and writable
        assert os.access(self.test_output_path, os.R_OK)
        assert os.access(self.test_output_path, os.W_OK)

    def test_auto_rule_generation_content_quality(self):
        """Test the quality and completeness of generated content"""
        generator = FileAutoRuleGenerator(self.test_output_path)
        result = generator.generate_rules_for_task(self.mock_task)
        
        assert result == True
        
        with open(self.test_output_path, 'r') as f:
            content = f.read()
        
        # Content quality checks
        assert len(content) > 0
        
        # Task context checks
        assert str(self.mock_task.id.value) in content
        assert self.mock_task.title in content
        assert self.mock_task.assignees[0].upper() in content
        assert self.mock_task.priority.value.upper() in content
        
        # Structure checks
        assert "TASK CONTEXT" in content
        assert "ROLE" in content
        assert "OPERATING RULES" in content

    def test_generate_rules_for_task_success_simplified(self):
        """Test successful rule generation with simplified approach"""
        generator = FileAutoRuleGenerator(self.test_output_path)
        
        # This will test the actual working system or fallback
        result = generator.generate_rules_for_task(self.mock_task)
        
        assert result == True
        assert os.path.exists(self.test_output_path)
        
        with open(self.test_output_path, 'r') as f:
            content = f.read()
            # Check that some content was generated (either complex or simple)
            assert len(content) > 100
            assert "123" in content  # Task ID should be present
            assert "CONTEXT_ENGINEER" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 