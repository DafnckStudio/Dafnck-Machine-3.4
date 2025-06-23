"""
This is the canonical and only maintained unit test suite for the TaskId value object.
All unit tests for TaskId should be added here.
Redundant or duplicate tests in other files have been removed.
"""

import pytest
from datetime import datetime

from fastmcp.dhafnck_mcp.domain.value_objects.task_id import TaskId


class TestTaskIdCreation:
    """Test TaskId creation and validation"""
    
    def test_create_valid_task_id(self):
        """Test creating a valid task ID"""
        task_id = TaskId("20250101001")
        assert task_id.value == "20250101001"
        assert str(task_id) == "20250101001"
    
    def test_create_valid_subtask_id(self):
        """Test creating a valid subtask ID"""
        subtask_id = TaskId("20250101001.001")
        assert subtask_id.value == "20250101001.001"
        assert subtask_id.is_subtask is True
    
    def test_invalid_format_raises_error(self):
        """Test that invalid format raises ValueError"""
        with pytest.raises(ValueError, match="Task ID must be in YYYYMMDDXXX"):
            TaskId("invalid")
    
    def test_empty_id_raises_error(self):
        """Test that empty ID raises ValueError"""
        with pytest.raises(ValueError, match="Task ID cannot be empty"):
            TaskId("")
    
    def test_none_id_raises_error(self):
        """Test that None ID raises ValueError"""
        with pytest.raises(ValueError, match="Task ID cannot be None"):
            TaskId(None)


class TestTaskIdProperties:
    """Test TaskId properties"""
    
    def test_date_part(self):
        """Test getting date part"""
        task_id = TaskId("20250101001")
        assert task_id.date_part == "20250101"
    
    def test_sequence_part(self):
        """Test getting sequence part"""
        task_id = TaskId("20250101001")
        assert task_id.sequence_part == "001"
    
    def test_subtask_sequence(self):
        """Test getting subtask sequence"""
        subtask_id = TaskId("20250101001.002")
        assert subtask_id.subtask_sequence == "002"
        
        main_task_id = TaskId("20250101001")
        assert main_task_id.subtask_sequence is None
    
    def test_parent_task_id(self):
        """Test getting parent task ID"""
        subtask_id = TaskId("20250101001.002")
        parent_id = subtask_id.parent_task_id
        assert parent_id.value == "20250101001"
        
        main_task_id = TaskId("20250101001")
        with pytest.raises(ValueError, match="Cannot get parent task ID for main task"):
            main_task_id.parent_task_id


class TestTaskIdGeneration:
    """Test TaskId generation methods"""
    
    def setup_method(self, method):
        """Reset counter before each test"""
        TaskId.reset_counter()
    
    def test_generate_new_with_no_existing(self):
        """Test generating new task ID with no existing IDs"""
        task_id = TaskId.generate_new([])
        assert len(task_id.value) == 11
        assert task_id.sequence_part == "001"
    
    def test_generate_new_with_existing(self):
        """Test generating new task ID with existing IDs"""
        current_date_str = datetime.now().strftime('%Y%m%d')
        existing = [f"{current_date_str}001", f"{current_date_str}002"]
        task_id = TaskId.generate_new(existing)
        assert task_id.sequence_part == "003"
    
    def test_generate_subtask(self):
        """Test generating subtask ID"""
        parent_id = TaskId("20250101001")
        subtask_id = TaskId.generate_subtask(parent_id, [])
        assert subtask_id.value == "20250101001.001"
        assert subtask_id.is_subtask is True
    
    def test_generate_subtask_with_existing(self):
        """Test generating subtask ID with existing subtasks"""
        parent_id = TaskId("20250101001")
        existing = ["20250101001.001", "20250101001.002"]
        subtask_id = TaskId.generate_subtask(parent_id, existing)
        assert subtask_id.value == "20250101001.003"


class TestTaskIdConversion:
    """Test TaskId conversion methods"""
    
    def test_from_string(self):
        """Test creating TaskId from string"""
        task_id = TaskId.from_string("20250101001")
        assert task_id.value == "20250101001"
    
    def test_from_int(self):
        """Test creating TaskId from integer (legacy support)"""
        task_id = TaskId.from_int(1)
        assert task_id.sequence_part == "001"
        assert len(task_id.value) == 11
    
    def test_to_int(self):
        """Test converting TaskId to integer"""
        task_id = TaskId("20250101001")
        assert int(task_id) == 1
        
        subtask_id = TaskId("20250101001.002")
        assert int(subtask_id) == 1002
