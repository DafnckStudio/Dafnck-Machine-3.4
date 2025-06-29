"""
Dual Mode Configuration for MCP Server
Handles both stdio (local Python) and HTTP (Docker) modes transparently
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional


class DualModeConfig:
    """Configuration manager that adapts to runtime environment"""
    
    def __init__(self):
        self.runtime_mode = self._detect_runtime_mode()
        self.project_root = self._get_project_root()
    
    def _detect_runtime_mode(self) -> str:
        """Detect if running in stdio mode (local Python) or HTTP mode (Docker)"""
        # Check for Docker-specific environment variables
        if "CURSOR_RULES_DIR" in os.environ:
            return "http"
        
        # Check if we're running in a container
        if os.path.exists("/.dockerenv"):
            return "http"
        
        # Check for HTTP transport configuration
        if os.environ.get("FASTMCP_TRANSPORT") == "streamable-http":
            return "http"
        
        # Check if we're in Docker environment by looking for container-specific paths
        if os.path.exists("/app") and not os.path.exists("/home"):
            return "http"
        
        # Default to stdio mode
        return "stdio"
    
    def _get_project_root(self) -> Path:
        """Get project root based on runtime mode"""
        if self.runtime_mode == "http":
            # In Docker, use /app as project root
            return Path("/app")
        else:
            # In stdio mode, find project root from current location
            current = Path.cwd()
            
            # Look for project indicators
            project_indicators = [
                "pyproject.toml",
                ".git",
                "src",
                "dhafnck_mcp_main"
            ]
            
            # Check current directory and parents
            for path in [current] + list(current.parents):
                if any((path / indicator).exists() for indicator in project_indicators):
                    return path
            
            # Fallback to current directory
            return current
    
    def get_rules_directory(self) -> Path:
        """Get rules directory with automatic mode detection"""
        if self.runtime_mode == "http":
            # Docker HTTP mode: use /data/rules
            return Path("/data/rules")
        else:
            # Stdio mode: use project structure
            return self.project_root / "00_RULES"
    
    def get_data_directory(self) -> Path:
        """Get data directory for tasks, projects, etc."""
        if self.runtime_mode == "http":
            return Path("/data")
        else:
            return self.project_root / "data"
    
    def get_config_directory(self) -> Path:
        """Get configuration directory"""
        if self.runtime_mode == "http":
            return Path("/app/config")
        else:
            return self.project_root / "config"
    
    def get_logs_directory(self) -> Path:
        """Get logs directory"""
        if self.runtime_mode == "http":
            return Path("/app/logs")
        else:
            return self.project_root / "logs"
    
    def get_environment_config(self) -> Dict[str, Any]:
        """Get environment-specific configuration"""
        base_config = {
            "runtime_mode": self.runtime_mode,
            "project_root": str(self.project_root),
            "rules_directory": str(self.get_rules_directory()),
            "data_directory": str(self.get_data_directory()),
            "config_directory": str(self.get_config_directory()),
            "logs_directory": str(self.get_logs_directory())
        }
        
        if self.runtime_mode == "http":
            base_config.update({
                "transport": "streamable-http",
                "host": "0.0.0.0",
                "port": 8000,
                "container_mode": True,
                "auth_enabled": os.environ.get("DHAFNCK_AUTH_ENABLED", "true").lower() == "true"
            })
        else:
            base_config.update({
                "transport": "stdio",
                "container_mode": False,
                "auth_enabled": False
            })
        
        return base_config
    
    def resolve_path(self, path: str, base_type: str = "project") -> Path:
        """Resolve a path based on runtime mode and base type
        
        Args:
            path: The path to resolve (can be relative or absolute)
            base_type: Base directory type ("project", "rules", "data", "config", "logs")
        """
        if os.path.isabs(path):
            return Path(path)
        
        base_map = {
            "project": self.project_root,
            "rules": self.get_rules_directory(),
            "data": self.get_data_directory(),
            "config": self.get_config_directory(),
            "logs": self.get_logs_directory()
        }
        
        base_dir = base_map.get(base_type, self.project_root)
        return base_dir / path


# Global instance for easy import
dual_mode_config = DualModeConfig()


# Convenience functions
def get_runtime_mode() -> str:
    """Get current runtime mode (with live reload test)"""
    return dual_mode_config.runtime_mode


def get_rules_directory() -> Path:
    """Get rules directory for current mode"""
    return dual_mode_config.get_rules_directory()


def get_data_directory() -> Path:
    """Get data directory for current mode"""
    return dual_mode_config.get_data_directory()


def resolve_path(path: str, base_type: str = "project") -> Path:
    """Resolve path for current mode"""
    return dual_mode_config.resolve_path(path, base_type)


def is_http_mode() -> bool:
    """Check if running in HTTP (Docker) mode"""
    return dual_mode_config.runtime_mode == "http"


def is_stdio_mode() -> bool:
    """Check if running in stdio (local) mode"""
    return dual_mode_config.runtime_mode == "stdio"