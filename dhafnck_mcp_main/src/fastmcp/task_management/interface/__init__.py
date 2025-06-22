"""Interface Layer"""

from .consolidated_mcp_tools_v2 import ConsolidatedMCPToolsV2
from .ddd_mcp_server import create_mcp_server

# Backward compatibility alias for tests
MCPTaskTools = ConsolidatedMCPToolsV2

__all__ = [
    "ConsolidatedMCPToolsV2",
    "MCPTaskTools",  # Backward compatibility
    "create_mcp_server"
] 