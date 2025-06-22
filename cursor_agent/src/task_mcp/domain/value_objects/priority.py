"""Priority Value Object"""

from dataclasses import dataclass
from enum import Enum


class PriorityLevel(Enum):
    """Enumeration of priority levels with numeric values for ordering"""

    LOW = ("low", 1)
    MEDIUM = ("medium", 2)
    HIGH = ("high", 3)
    URGENT = ("urgent", 4)
    CRITICAL = ("critical", 5)

    def __init__(self, label: str, level: int):
        self.label = label
        self.level = level


@dataclass(frozen=True)
class Priority:
    """Value object for Task Priority with validation and ordering"""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Priority cannot be empty")

        valid_priorities = {priority.label for priority in PriorityLevel}
        if self.value not in valid_priorities:
            raise ValueError(
                f"Invalid priority: {self.value}. Valid priorities: {', '.join(valid_priorities)}"
            )

    def __str__(self) -> str:
        return self.value

    def __lt__(self, other: "Priority") -> bool:
        return self._get_level() < other._get_level()

    def __le__(self, other: "Priority") -> bool:
        return self._get_level() <= other._get_level()

    def __gt__(self, other: "Priority") -> bool:
        return self._get_level() > other._get_level()

    def __ge__(self, other: "Priority") -> bool:
        return self._get_level() >= other._get_level()

    def _get_level(self) -> int:
        """Get numeric level for comparison"""
        for priority in PriorityLevel:
            if priority.label == self.value:
                return priority.level
        return 0

    @property
    def order(self) -> int:
        """Get the numeric order/level of this priority"""
        return self._get_level()

    @classmethod
    def low(cls) -> "Priority":
        return cls(PriorityLevel.LOW.label)

    @classmethod
    def medium(cls) -> "Priority":
        return cls(PriorityLevel.MEDIUM.label)

    @classmethod
    def high(cls) -> "Priority":
        return cls(PriorityLevel.HIGH.label)

    @classmethod
    def urgent(cls) -> "Priority":
        return cls(PriorityLevel.URGENT.label)

    @classmethod
    def critical(cls) -> "Priority":
        return cls(PriorityLevel.CRITICAL.label)

    def is_critical(self) -> bool:
        return self.value == PriorityLevel.CRITICAL.label

    def is_high_or_critical(self) -> bool:
        return self.value in {PriorityLevel.HIGH.label, PriorityLevel.CRITICAL.label}
