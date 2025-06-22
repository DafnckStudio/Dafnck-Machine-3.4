"""Estimated Effort Value Object"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class EffortLevel(Enum):
    """Enumeration of standardized effort levels"""
    QUICK = ("quick", "15m", 0.25)           # 15 minutes
    SHORT = ("short", "30m", 0.5)            # 30 minutes  
    SMALL = ("small", "1h", 1.0)             # 1 hour
    MEDIUM = ("medium", "2h", 2.0)           # 2 hours
    LARGE = ("large", "4h", 4.0)             # 4 hours
    XLARGE = ("xlarge", "8h", 8.0)           # 8 hours (full day)
    EPIC = ("epic", "16h", 16.0)             # 2 days
    MASSIVE = ("massive", "40h", 40.0)       # 1 week
    
    def __init__(self, label: str, display: str, hours: float):
        self.label = label
        self.display = display
        self.hours = hours


@dataclass(frozen=True)
class EstimatedEffort:
    """Value object for Task Estimated Effort with validation"""
    
    value: str
    
    def __post_init__(self):
        if not self.value:
            # Empty effort is allowed
            return
        
        # Check if it's a valid enum value
        valid_efforts = {effort.label for effort in EffortLevel}
        valid_displays = {effort.display for effort in EffortLevel}
        
        if self.value not in valid_efforts and self.value not in valid_displays:
            # Allow custom values but validate they look like time estimates
            if not self._is_valid_custom_effort(self.value):
                raise ValueError(f"Invalid effort estimate: {self.value}. Use standard levels or valid time format (e.g., '3h', '45m')")
    
    def _is_valid_custom_effort(self, value: str) -> bool:
        """Validate custom effort format"""
        import re
        # Allow formats like: 1h, 30m, 2.5h, 1h 30m, etc.
        pattern = r'^(\d+(?:\.\d+)?[hm](?:\s+\d+(?:\.\d+)?[hm])*|\d+(?:\.\d+)?\s*(?:hours?|hrs?|minutes?|mins?))$'
        return bool(re.match(pattern, value.lower().strip()))
    
    def __str__(self) -> str:
        return self.value
    
    def get_hours(self) -> Optional[float]:
        """Get estimated hours for this effort"""
        # Check if it's a standard level
        for effort in EffortLevel:
            if self.value == effort.label or self.value == effort.display:
                return effort.hours
        
        # Try to parse custom format
        return self._parse_custom_hours()
    
    def _parse_custom_hours(self) -> Optional[float]:
        """Parse custom effort format to hours"""
        import re
        if not self.value:
            return None
            
        total_hours = 0.0
        
        # Extract hours
        hour_match = re.search(r'(\d+(?:\.\d+)?)\s*h', self.value.lower())
        if hour_match:
            total_hours += float(hour_match.group(1))
        
        # Extract minutes
        minute_match = re.search(r'(\d+(?:\.\d+)?)\s*m', self.value.lower())
        if minute_match:
            total_hours += float(minute_match.group(1)) / 60
        
        return total_hours if total_hours > 0 else None
    
    @classmethod
    def quick(cls) -> 'EstimatedEffort':
        return cls(EffortLevel.QUICK.label)
    
    @classmethod
    def short(cls) -> 'EstimatedEffort':
        return cls(EffortLevel.SHORT.label)
    
    @classmethod
    def small(cls) -> 'EstimatedEffort':
        return cls(EffortLevel.SMALL.label)
    
    @classmethod
    def medium(cls) -> 'EstimatedEffort':
        return cls(EffortLevel.MEDIUM.label)
    
    @classmethod
    def large(cls) -> 'EstimatedEffort':
        return cls(EffortLevel.LARGE.label)
    
    @classmethod
    def xlarge(cls) -> 'EstimatedEffort':
        return cls(EffortLevel.XLARGE.label)
    
    @classmethod
    def epic(cls) -> 'EstimatedEffort':
        return cls(EffortLevel.EPIC.label)
    
    @classmethod
    def massive(cls) -> 'EstimatedEffort':
        return cls(EffortLevel.MASSIVE.label)
    
    @classmethod
    def from_hours(cls, hours: float) -> 'EstimatedEffort':
        """Create effort estimate from hours"""
        # Find closest standard level
        best_match = min(EffortLevel, key=lambda x: abs(x.hours - hours))
        return cls(best_match.label)
    
    def is_quick(self) -> bool:
        return self.value == EffortLevel.QUICK.label
    
    def is_large_effort(self) -> bool:
        """Check if this is a large effort (4+ hours)"""
        hours = self.get_hours()
        return hours is not None and hours >= 4.0
    
    def get_level(self) -> str:
        """Get the effort level category for this effort"""
        # Check if it's a standard level first
        for effort in EffortLevel:
            if self.value == effort.label or self.value == effort.display:
                return effort.label
        
        # For custom values, categorize by hours
        hours = self.get_hours()
        if hours is None:
            return "medium"  # Default fallback
        
        # Categorize based on hours
        if hours <= 0.25:
            return EffortLevel.QUICK.label
        elif hours <= 0.5:
            return EffortLevel.SHORT.label
        elif hours <= 1.0:
            return EffortLevel.SMALL.label
        elif hours <= 2.0:
            return EffortLevel.MEDIUM.label
        elif hours <= 4.0:
            return EffortLevel.LARGE.label
        elif hours <= 8.0:
            return EffortLevel.XLARGE.label
        elif hours <= 16.0:
            return EffortLevel.EPIC.label
        else:
            return EffortLevel.MASSIVE.label 