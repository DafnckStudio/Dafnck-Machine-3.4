"""Task ID Value Object"""

import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Union


# Global counter to ensure unique task IDs within the same millisecond
_task_id_counter = 0


@dataclass(frozen=True)
class TaskId:
    """Value object for Task ID with YYYYMMDDXXX format validation"""
    
    value: str
    
    def __post_init__(self):
        if self.value is None:
            raise ValueError("Task ID cannot be None")
        
        if not isinstance(self.value, str):
            # Convert legacy numeric IDs to string for backward compatibility
            object.__setattr__(self, 'value', str(self.value))
        
        value_str = str(self.value).strip()
        if not value_str:
            raise ValueError("Task ID cannot be empty string")
        
        # Validate YYYYMMDDXXX format (main task) or YYYYMMDDXXX.XXX format (subtask)
        if not self._is_valid_format(value_str):
            raise ValueError(f"Task ID must be in YYYYMMDDXXX or YYYYMMDDXXX.XXX format, got: {value_str}")
        
        object.__setattr__(self, 'value', value_str)
    
    def _is_valid_format(self, value: str) -> bool:
        """Validate task ID format: YYYYMMDDXXX or YYYYMMDDXXX.XXX"""
        # Main task format: YYYYMMDDXXX (11 digits)
        main_task_pattern = r'^\d{8}\d{3}$'  # YYYYMMDD + XXX
        # Subtask format: YYYYMMDDXXX.XXX
        subtask_pattern = r'^\d{8}\d{3}\.\d{3}$'  # YYYYMMDDXXX.XXX
        
        if re.match(main_task_pattern, value):
            # Validate date part
            date_part = value[:8]
            try:
                datetime.strptime(date_part, '%Y%m%d')
                return True
            except ValueError:
                return False
        elif re.match(subtask_pattern, value):
            # Validate date part of subtask
            date_part = value[:8]
            try:
                datetime.strptime(date_part, '%Y%m%d')
                return True
            except ValueError:
                return False
        
        return False
    
    def __str__(self) -> str:
        return self.value
    
    def __int__(self) -> int:
        """Convert to integer for backward compatibility (uses sequence number)"""
        try:
            if '.' in self.value:
                # For subtasks, combine main and sub sequence numbers
                main_part, sub_part = self.value.split('.')
                return int(main_part[-3:]) * 1000 + int(sub_part)
            else:
                # For main tasks, use the last 3 digits
                return int(self.value[-3:])
        except ValueError:
            raise ValueError(f"Cannot convert task ID '{self.value}' to integer")
    
    @property
    def date_part(self) -> str:
        """Get the date part (YYYYMMDD) of the task ID"""
        return self.value[:8]
    
    @property
    def sequence_part(self) -> str:
        """Get the sequence part (XXX) of the task ID"""
        if '.' in self.value:
            return self.value[8:11]  # Main task sequence for subtasks
        return self.value[8:11]
    
    @property
    def subtask_sequence(self) -> str:
        """Get the subtask sequence part (XXX after dot), returns None for main tasks"""
        if '.' in self.value:
            return self.value.split('.')[1]
        return None
    
    @property
    def is_subtask(self) -> bool:
        """Check if this is a subtask ID"""
        return '.' in self.value
    
    @property
    def parent_task_id(self) -> 'TaskId':
        """Get parent task ID for subtasks"""
        if not self.is_subtask:
            raise ValueError("Cannot get parent task ID for main task")
        return TaskId(self.value.split('.')[0])
    
    @classmethod
    def from_string(cls, value: str) -> 'TaskId':
        """Create TaskId from string"""
        return cls(value.strip())
    
    @classmethod
    def from_int(cls, value: int) -> 'TaskId':
        """Create TaskId from integer (legacy support)"""
        if not isinstance(value, int):
            raise ValueError("Value must be an integer")
        if value <= 0:
            raise ValueError("Task ID must be a positive integer")
        if value > 999:
            raise ValueError("Task ID sequence cannot exceed 999")
        
        # Convert legacy integer IDs to new format using current date
        current_date = datetime.now().strftime('%Y%m%d')
        sequence = f"{value:03d}"
        return cls(f"{current_date}{sequence}")
    
    @classmethod
    def generate_new(cls, existing_ids: list = None) -> 'TaskId':
        """Generate a new task ID in YYYYMMDDXXX format"""
        global _task_id_counter
        
        if existing_ids is None:
            existing_ids = []
        
        # Convert existing_ids to strings for consistency
        existing_id_strings = []
        for task_id in existing_ids:
            try:
                if hasattr(task_id, 'value'):
                    existing_id_strings.append(str(task_id.value))
                else:
                    existing_id_strings.append(str(task_id))
            except (ValueError, AttributeError):
                continue
        
        # Use current date
        target_date = datetime.now().strftime('%Y%m%d')
        
        # Find the highest sequence number for the target date
        max_sequence = 0
        for task_id_str in existing_id_strings:
            try:
                if len(task_id_str) >= 11 and task_id_str[:8] == target_date and '.' not in task_id_str:
                    sequence_num = int(task_id_str[8:11])
                    max_sequence = max(max_sequence, sequence_num)
            except (ValueError, IndexError):
                continue
        
        # Generate next sequence number with counter to ensure uniqueness
        _task_id_counter += 1
        next_sequence = max(max_sequence + 1, _task_id_counter)
        
        if next_sequence > 999:
            # Reset counter and try next day if we exceed 999 tasks per day
            _task_id_counter = 1
            next_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            next_day = next_day.replace(day=next_day.day + 1)
            target_date = next_day.strftime('%Y%m%d')
            next_sequence = 1
        
        new_id = f"{target_date}{next_sequence:03d}"
        
        # Double-check for uniqueness to prevent duplicates
        while new_id in existing_id_strings:
            _task_id_counter += 1
            next_sequence += 1
            if next_sequence > 999:
                raise ValueError(f"Maximum tasks per day (999) exceeded for date {target_date}")
            new_id = f"{target_date}{next_sequence:03d}"
        
        return cls(new_id)
    
    @classmethod
    def generate_subtask(cls, parent_id: 'TaskId', existing_subtask_ids: list = None) -> 'TaskId':
        """Generate a new subtask ID in YYYYMMDDXXX.XXX format"""
        if parent_id.is_subtask:
            raise ValueError("Cannot create subtask of a subtask")
        
        if existing_subtask_ids is None:
            existing_subtask_ids = []
        
        # Find the highest subtask sequence number for this parent
        max_sequence = 0
        for subtask_id in existing_subtask_ids:
            try:
                tid = cls(str(subtask_id))
                if tid.is_subtask and tid.parent_task_id.value == parent_id.value:
                    sequence_num = int(tid.subtask_sequence)
                    max_sequence = max(max_sequence, sequence_num)
            except (ValueError, AttributeError):
                continue
        
        # Generate next sequence number
        next_sequence = max_sequence + 1
        if next_sequence > 999:
            raise ValueError(f"Maximum subtasks per task (999) exceeded for task {parent_id}")
        
        return cls(f"{parent_id.value}.{next_sequence:03d}") 