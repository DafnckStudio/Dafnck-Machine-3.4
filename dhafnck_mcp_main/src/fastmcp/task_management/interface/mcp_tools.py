"""
Backward compatibility module for MCPTaskTools
This module provides backward compatibility for tests and legacy code
that imports MCPTaskTools from task_mcp.interface.mcp_tools
"""

from .consolidated_mcp_tools import ConsolidatedMCPTools

# Backward compatibility alias
MCPTaskTools = ConsolidatedMCPTools

__all__ = ["MCPTaskTools"] 