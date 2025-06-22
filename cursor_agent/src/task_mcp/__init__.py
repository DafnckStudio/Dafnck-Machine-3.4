"""MCP Package with Domain-Driven Design Architecture"""

# Core layers (always available)
from .application import TaskApplicationService
from .domain import Priority, Task, TaskId, TaskStatus
from .infrastructure import FileAutoRuleGenerator, JsonTaskRepository

__all__ = [
    # Application Layer
    "TaskApplicationService",
    # Infrastructure Layer
    "JsonTaskRepository",
    "FileAutoRuleGenerator",
    # Domain Layer
    "Task",
    "TaskId",
    "TaskStatus",
    "Priority",
]

# Interface Layer (optional - only if FastMCP is available)
try:
    pass

    __all__.extend(["create_mcp_server"])
except ImportError:
    # FastMCP not available, interface layer disabled
    pass
