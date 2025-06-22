"""
Cursor Agent - AI-Powered Development Assistant

A lightweight, practical solution that transforms Cursor into a sophisticated
multi-role AI assistant.
"""

__version__ = "1.0.0"
__author__ = "Cursor Agent Team"

# Main exports - only import what exists
from .task_mcp.infrastructure.services.legacy.models import AgentRole, TaskContext

__all__ = ["TaskContext", "AgentRole"]
