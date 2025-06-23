"""
This is the canonical and only maintained unit test suite for the Priority value object.
All unit tests for Priority should be added here.
Redundant or duplicate tests in other files have been removed.
"""

import pytest
from fastmcp.dhafnck_mcp.domain.value_objects.priority import Priority


def test_create_valid_priority():
    """Test creating a valid priority"""
    priority = Priority("high")
    assert priority.value == "high"
    assert str(priority) == "high"


def test_invalid_priority_raises_error():
    """Test that invalid priority raises ValueError"""
    with pytest.raises(ValueError, match="Invalid priority"):
        Priority("invalid")


def test_priority_comparison():
    """Test priority comparison"""
    low = Priority.low()
    high = Priority.high()
    critical = Priority.critical()
    
    assert low < high
    assert high < critical
    assert critical > low


def test_priority_factory_methods():
    """Test priority factory methods"""
    assert Priority.low().value == "low"
    assert Priority.medium().value == "medium"
    assert Priority.high().value == "high"
    assert Priority.urgent().value == "urgent"
    assert Priority.critical().value == "critical"


def test_priority_order():
    """Test priority order property"""
    assert Priority.low().order == 1
    assert Priority.medium().order == 2
    assert Priority.high().order == 3
    assert Priority.urgent().order == 4
    assert Priority.critical().order == 5


def test_priority_helper_methods():
    """Test priority helper methods"""
    critical = Priority.critical()
    high = Priority.high()
    medium = Priority.medium()
    
    assert critical.is_critical() is True
    assert high.is_critical() is False
    
    assert critical.is_high_or_critical() is True
    assert high.is_high_or_critical() is True
    assert medium.is_high_or_critical() is False
