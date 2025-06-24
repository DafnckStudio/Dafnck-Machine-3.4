"""Interface Layer"""

from .consolidated_mcp_tools import ConsolidatedMCPTools
from .ddd_mcp_server import create_mcp_server

# Backward compatibility alias for tests
MCPTaskTools = ConsolidatedMCPTools

__all__ = [
    "ConsolidatedMCPTools",
    "MCPTaskTools",  # Backward compatibility
    "create_mcp_server"
] 