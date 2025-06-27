"""
Authentication middleware for DhafnckMCP server.

Provides request-level authentication and authorization for MCP operations.
"""

import logging
import os
from typing import Optional, Dict, Any, Callable
from functools import wraps

from .token_validator import TokenValidator, TokenValidationError, RateLimitError
from .supabase_client import TokenInfo


logger = logging.getLogger(__name__)


class AuthMiddleware:
    """
    Authentication middleware for MCP server.
    
    Handles token validation, rate limiting, and security for all MCP operations.
    """
    
    def __init__(self, enabled: bool = None):
        """
        Initialize authentication middleware.
        
        Args:
            enabled: Whether authentication is enabled. If None, uses environment variable.
        """
        if enabled is None:
            # Check environment variable
            enabled = os.environ.get("DHAFNCK_AUTH_ENABLED", "true").lower() == "true"
        
        self.enabled = enabled
        self.token_validator = TokenValidator() if enabled else None
        
        # Bypass token for MVP mode
        self.mvp_mode = os.environ.get("DHAFNCK_MVP_MODE", "false").lower() == "true"
        
        if not enabled:
            logger.warning("Authentication is DISABLED - all requests will be allowed")
        elif self.mvp_mode:
            logger.info("MVP mode enabled - simplified authentication")
        else:
            logger.info("Authentication middleware initialized")
    
    async def authenticate_request(self, token: Optional[str], client_info: Optional[Dict] = None) -> Optional[TokenInfo]:
        """
        Authenticate a request using the provided token.
        
        Args:
            token: Authentication token
            client_info: Optional client information for logging
            
        Returns:
            TokenInfo if authenticated, None if authentication disabled
            
        Raises:
            TokenValidationError: If authentication fails
            RateLimitError: If rate limit exceeded
        """
        if not self.enabled:
            logger.debug("Authentication disabled, allowing request")
            return None
        
        if self.mvp_mode and not token:
            # MVP mode: allow requests without tokens
            logger.debug("MVP mode: allowing request without token")
            return None
        
        if not token:
            raise TokenValidationError("Authentication token required")
        
        # Validate token
        token_info = await self.token_validator.validate_token(token, client_info)
        logger.debug(f"Request authenticated for user: {token_info.user_id}")
        
        return token_info
    
    def require_auth(self, func: Callable) -> Callable:
        """
        Decorator to require authentication for a function.
        
        Args:
            func: Function to protect
            
        Returns:
            Decorated function
        """
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract token from various sources
            token = self._extract_token(kwargs)
            
            # Extract client info
            client_info = self._extract_client_info(kwargs)
            
            try:
                # Authenticate request
                token_info = await self.authenticate_request(token, client_info)
                
                # Add token info to kwargs for the function
                kwargs['_auth_token_info'] = token_info
                
                # Call original function
                return await func(*args, **kwargs)
                
            except (TokenValidationError, RateLimitError) as e:
                logger.warning(f"Authentication failed: {e}")
                raise
            
        return wrapper
    
    def _extract_token(self, kwargs: Dict[str, Any]) -> Optional[str]:
        """
        Extract authentication token from request.
        
        Args:
            kwargs: Function keyword arguments
            
        Returns:
            Token if found, None otherwise
        """
        # Check various token sources
        token_sources = [
            kwargs.get('token'),
            kwargs.get('auth_token'),
            kwargs.get('authorization'),
            os.environ.get('DHAFNCK_TOKEN'),
        ]
        
        for token in token_sources:
            if token:
                return str(token).strip()
        
        return None
    
    def _extract_client_info(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract client information for logging.
        
        Args:
            kwargs: Function keyword arguments
            
        Returns:
            Client information dictionary
        """
        return {
            "function": kwargs.get('__name__', 'unknown'),
            "args_count": len(kwargs),
            "timestamp": logger.handlers[0].formatter.formatTime(logger.makeRecord(
                logger.name, logging.INFO, __file__, 0, "", (), None
            )) if logger.handlers else None
        }
    
    async def get_rate_limit_status(self, token: str) -> Dict[str, Any]:
        """
        Get rate limit status for a token.
        
        Args:
            token: Authentication token
            
        Returns:
            Rate limit status
        """
        if not self.enabled or not self.token_validator:
            return {"enabled": False}
        
        status = self.token_validator.get_rate_limit_status(token)
        status["enabled"] = True
        return status
    
    async def revoke_token(self, token: str) -> bool:
        """
        Revoke an authentication token.
        
        Args:
            token: Token to revoke
            
        Returns:
            True if revoked successfully
        """
        if not self.enabled or not self.token_validator:
            logger.warning("Cannot revoke token: authentication disabled")
            return False
        
        return await self.token_validator.revoke_token(token)
    
    def get_auth_status(self) -> Dict[str, Any]:
        """
        Get authentication system status.
        
        Returns:
            Authentication status information
        """
        status = {
            "enabled": self.enabled,
            "mvp_mode": self.mvp_mode,
            "supabase_enabled": False,
            "cache_stats": {}
        }
        
        if self.token_validator:
            status["supabase_enabled"] = self.token_validator.supabase_client.enabled
            status["cache_stats"] = self.token_validator.get_cache_stats()
        
        return status


# Global middleware instance
auth_middleware = AuthMiddleware()


def require_auth(func: Callable) -> Callable:
    """
    Global decorator for requiring authentication.
    
    Usage:
        @require_auth
        async def my_protected_function(arg1, arg2, token=None):
            # Function implementation
            pass
    """
    return auth_middleware.require_auth(func)


async def authenticate_request(token: Optional[str], client_info: Optional[Dict] = None) -> Optional[TokenInfo]:
    """
    Global function for authenticating requests.
    
    Args:
        token: Authentication token
        client_info: Optional client information
        
    Returns:
        TokenInfo if authenticated
    """
    return await auth_middleware.authenticate_request(token, client_info) 