"""Interface Layer"""

from .consolidated_mcp_tools import ConsolidatedMCPTools
from .consolidated_mcp_server import create_consolidated_mcp_server

# Backward compatibility alias for tests
MCPTaskTools = ConsolidatedMCPTools

__all__ = [
    "ConsolidatedMCPTools",
    "MCPTaskTools",  # Backward compatibility
    "create_consolidated_mcp_server"
] 