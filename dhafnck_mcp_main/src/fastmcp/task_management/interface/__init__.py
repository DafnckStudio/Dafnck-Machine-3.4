"""Interface Layer"""

from .consolidated_mcp_tools import ConsolidatedMCPTools

# Backward compatibility alias for tests
MCPTaskTools = ConsolidatedMCPTools

# Note: create_consolidated_mcp_server is not imported here to avoid circular imports
# Import it directly when needed: from .consolidated_mcp_server import create_consolidated_mcp_server

__all__ = [
    "ConsolidatedMCPTools",
    "MCPTaskTools",  # Backward compatibility
] 