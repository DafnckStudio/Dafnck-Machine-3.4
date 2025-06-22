"""
Backward compatibility module for MCPTaskTools
This module provides backward compatibility for tests and legacy code
that imports MCPTaskTools from task_mcp.interface.mcp_tools
"""

from .consolidated_mcp_tools_v2 import ConsolidatedMCPToolsV2

# Backward compatibility alias
MCPTaskTools = ConsolidatedMCPToolsV2

__all__ = ["MCPTaskTools"]
