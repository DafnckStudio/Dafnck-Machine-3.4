"""
Token validation and rate limiting for DhafnckMCP server.

Provides comprehensive token validation, rate limiting, and security monitoring
for the MCP server MVP implementation.
"""

import asyncio
import logging
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from dataclasses import dataclass

from .supabase_client import SupabaseTokenClient, TokenInfo


logger = logging.getLogger(__name__)


class TokenValidationError(Exception):
    """Raised when token validation fails."""
    pass


class RateLimitError(Exception):
    """Raised when rate limit is exceeded."""
    pass


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    requests_per_minute: int = 100
    requests_per_hour: int = 1000
    burst_limit: int = 20  # Maximum burst requests
    window_size: int = 60  # Window size in seconds


class TokenValidator:
    """
    Token validation and rate limiting system.
    
    Features:
    - Secure token validation via Supabase
    - Rate limiting per token
    - Security event logging
    - Token caching for performance
    """
    
    def __init__(self, rate_limit_config: Optional[RateLimitConfig] = None):
        """
        Initialize token validator.
        
        Args:
            rate_limit_config: Rate limiting configuration
        """
        self.supabase_client = SupabaseTokenClient()
        self.rate_config = rate_limit_config or RateLimitConfig()
        
        # Rate limiting storage: token_hash -> deque of request timestamps
        self._rate_limits: Dict[str, deque] = defaultdict(lambda: deque(maxlen=self.rate_config.requests_per_hour))
        
        # Token cache: token_hash -> (TokenInfo, cache_time)
        self._token_cache: Dict[str, Tuple[TokenInfo, float]] = {}
        self._cache_ttl = 300  # 5 minutes cache TTL
        
        # Security monitoring
        self._failed_attempts: Dict[str, deque] = defaultdict(lambda: deque(maxlen=10))
        
        logger.info(f"Token validator initialized with rate limit: {self.rate_config.requests_per_minute}/min")
    
    async def validate_token(self, token: str, client_info: Optional[Dict] = None) -> TokenInfo:
        """
        Validate a token and check rate limits.
        
        Args:
            token: The token to validate
            client_info: Optional client information for logging
            
        Returns:
            TokenInfo if valid
            
        Raises:
            TokenValidationError: If token is invalid
            RateLimitError: If rate limit is exceeded
        """
        if not token:
            raise TokenValidationError("Token is required")
        
        # Clean token (remove whitespace, prefixes)
        token = token.strip()
        if token.startswith("Bearer "):
            token = token[7:]
        
        token_hash = self.supabase_client._hash_token(token)
        
        try:
            # Check rate limits first
            await self._check_rate_limit(token_hash)
            
            # Validate token
            token_info = await self._get_token_info(token)
            
            if not token_info:
                await self._log_failed_attempt(token_hash, "invalid_token", client_info)
                raise TokenValidationError("Invalid or expired token")
            
            # Log successful validation
            await self.supabase_client.log_security_event(
                "token_validated",
                token_hash,
                {
                    "user_id": token_info.user_id,
                    "client_info": client_info or {},
                    "usage_count": token_info.usage_count
                }
            )
            
            return token_info
            
        except RateLimitError:
            await self._log_failed_attempt(token_hash, "rate_limit_exceeded", client_info)
            raise
        except TokenValidationError:
            await self._log_failed_attempt(token_hash, "validation_failed", client_info)
            raise
        except Exception as e:
            logger.error(f"Unexpected error during token validation: {e}")
            await self._log_failed_attempt(token_hash, "validation_error", client_info)
            raise TokenValidationError("Token validation failed")
    
    async def _get_token_info(self, token: str) -> Optional[TokenInfo]:
        """
        Get token information with caching.
        
        Args:
            token: The token to validate
            
        Returns:
            TokenInfo if valid, None otherwise
        """
        token_hash = self.supabase_client._hash_token(token)
        current_time = time.time()
        
        # Check cache first
        if token_hash in self._token_cache:
            cached_info, cache_time = self._token_cache[token_hash]
            if current_time - cache_time < self._cache_ttl:
                logger.debug("Token found in cache")
                return cached_info
            else:
                # Remove expired cache entry
                del self._token_cache[token_hash]
        
        # Validate with Supabase
        token_info = await self.supabase_client.validate_token(token)
        
        # Cache valid tokens
        if token_info:
            self._token_cache[token_hash] = (token_info, current_time)
        
        return token_info
    
    async def _check_rate_limit(self, token_hash: str) -> None:
        """
        Check if token has exceeded rate limits.
        
        Args:
            token_hash: Hash of the token
            
        Raises:
            RateLimitError: If rate limit is exceeded
        """
        current_time = time.time()
        requests = self._rate_limits[token_hash]
        
        # Remove old requests (older than 1 hour)
        cutoff_time = current_time - 3600  # 1 hour
        while requests and requests[0] < cutoff_time:
            requests.popleft()
        
        # Check minute-based rate limit
        minute_cutoff = current_time - 60
        recent_requests = sum(1 for req_time in requests if req_time > minute_cutoff)
        
        if recent_requests >= self.rate_config.requests_per_minute:
            logger.warning(f"Rate limit exceeded for token: {recent_requests}/min")
            raise RateLimitError(f"Rate limit exceeded: {recent_requests}/{self.rate_config.requests_per_minute} requests per minute")
        
        # Check burst limit (last 10 seconds)
        burst_cutoff = current_time - 10
        burst_requests = sum(1 for req_time in requests if req_time > burst_cutoff)
        
        if burst_requests >= self.rate_config.burst_limit:
            logger.warning(f"Burst limit exceeded for token: {burst_requests}/10s")
            raise RateLimitError(f"Burst limit exceeded: {burst_requests}/{self.rate_config.burst_limit} requests per 10 seconds")
        
        # Record this request
        requests.append(current_time)
    
    async def _log_failed_attempt(self, token_hash: str, reason: str, client_info: Optional[Dict] = None) -> None:
        """
        Log failed validation attempts for security monitoring.
        
        Args:
            token_hash: Hash of the token
            reason: Reason for failure
            client_info: Optional client information
        """
        current_time = time.time()
        failures = self._failed_attempts[token_hash]
        
        # Remove old failures (older than 1 hour)
        cutoff_time = current_time - 3600
        while failures and failures[0] < cutoff_time:
            failures.popleft()
        
        # Add current failure
        failures.append(current_time)
        
        # Log security event
        await self.supabase_client.log_security_event(
            "validation_failed",
            token_hash,
            {
                "reason": reason,
                "failure_count": len(failures),
                "client_info": client_info or {},
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Alert on repeated failures
        if len(failures) >= 5:
            logger.warning(f"Multiple failed attempts for token: {len(failures)} failures in last hour")
    
    async def revoke_token(self, token: str) -> bool:
        """
        Revoke a token and clear it from cache.
        
        Args:
            token: The token to revoke
            
        Returns:
            True if revoked successfully
        """
        token_hash = self.supabase_client._hash_token(token)
        
        # Remove from cache
        if token_hash in self._token_cache:
            del self._token_cache[token_hash]
        
        # Revoke in Supabase
        success = await self.supabase_client.revoke_token(token)
        
        if success:
            await self.supabase_client.log_security_event(
                "token_revoked",
                token_hash,
                {"revoked_at": datetime.utcnow().isoformat()}
            )
        
        return success
    
    def get_rate_limit_status(self, token: str) -> Dict[str, int]:
        """
        Get current rate limit status for a token.
        
        Args:
            token: The token to check
            
        Returns:
            Dictionary with rate limit status
        """
        token_hash = self.supabase_client._hash_token(token)
        requests = self._rate_limits[token_hash]
        current_time = time.time()
        
        # Count requests in different time windows
        minute_cutoff = current_time - 60
        hour_cutoff = current_time - 3600
        
        minute_requests = sum(1 for req_time in requests if req_time > minute_cutoff)
        hour_requests = sum(1 for req_time in requests if req_time > hour_cutoff)
        
        return {
            "requests_per_minute": minute_requests,
            "minute_limit": self.rate_config.requests_per_minute,
            "requests_per_hour": hour_requests,
            "hour_limit": self.rate_config.requests_per_hour,
            "remaining_minute": max(0, self.rate_config.requests_per_minute - minute_requests),
            "remaining_hour": max(0, self.rate_config.requests_per_hour - hour_requests)
        }
    
    def clear_cache(self) -> None:
        """Clear the token cache."""
        self._token_cache.clear()
        logger.info("Token cache cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        return {
            "cached_tokens": len(self._token_cache),
            "rate_limited_tokens": len(self._rate_limits),
            "failed_attempt_records": len(self._failed_attempts)
        } 