"""
Supabase client for token validation and management.

Handles communication with Supabase for token verification, user authentication,
and security logging.
"""

import os
import logging
import hashlib
import secrets
from datetime import datetime, timedelta, UTC
from typing import Optional, Dict, Any
import httpx
from pydantic import BaseModel


logger = logging.getLogger(__name__)


class TokenInfo(BaseModel):
    """Token information from Supabase."""
    token_hash: str
    user_id: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    is_active: bool = True
    usage_count: int = 0
    last_used: Optional[datetime] = None


class SupabaseTokenClient:
    """Client for Supabase token operations."""
    
    def __init__(self):
        """Initialize Supabase client with environment variables."""
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_anon_key = os.environ.get("SUPABASE_ANON_KEY")
        self.supabase_service_key = os.environ.get("SUPABASE_SERVICE_KEY")
        
        # Use service key if available, otherwise anon key
        self.api_key = self.supabase_service_key or self.supabase_anon_key
        
        if not self.supabase_url or not self.api_key:
            logger.warning("Supabase configuration not found. Token validation will be disabled.")
            self.enabled = False
        else:
            self.enabled = True
            logger.info("Supabase token client initialized")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Supabase API requests."""
        return {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal"
        }
    
    def _hash_token(self, token: str) -> str:
        """Create a secure hash of the token for storage."""
        return hashlib.sha256(token.encode()).hexdigest()
    
    async def validate_token(self, token: str) -> Optional[TokenInfo]:
        """
        Validate a token against Supabase database.
        
        Args:
            token: The token to validate
            
        Returns:
            TokenInfo if valid, None if invalid
        """
        if not self.enabled:
            # For MVP without Supabase, accept any token
            logger.debug("Supabase disabled, accepting token for MVP mode")
            return TokenInfo(
                token_hash=self._hash_token(token),
                user_id="mvp_user",
                created_at=datetime.now(UTC),
                is_active=True
            )
        
        try:
            token_hash = self._hash_token(token)
            
            # Query Supabase for token
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.supabase_url}/rest/v1/api_tokens",
                    headers=self._get_headers(),
                    params={
                        "token_hash": f"eq.{token_hash}",
                        "is_active": "eq.true"
                    }
                )
                
                if response.status_code != 200:
                    logger.warning(f"Supabase API error: {response.status_code}")
                    return None
                
                tokens = response.json()
                
                if not tokens:
                    logger.debug("Token not found in database")
                    return None
                
                token_data = tokens[0]
                
                # Check expiration
                if token_data.get("expires_at"):
                    expires_at = datetime.fromisoformat(token_data["expires_at"].replace("Z", "+00:00"))
                    if expires_at < datetime.now(UTC):
                        logger.debug("Token has expired")
                        return None
                
                # Update last used timestamp
                await self._update_token_usage(token_hash)
                
                return TokenInfo(
                    token_hash=token_hash,
                    user_id=token_data["user_id"],
                    created_at=datetime.fromisoformat(token_data["created_at"].replace("Z", "+00:00")),
                    expires_at=datetime.fromisoformat(token_data["expires_at"].replace("Z", "+00:00")) if token_data.get("expires_at") else None,
                    is_active=token_data["is_active"],
                    usage_count=token_data.get("usage_count", 0),
                    last_used=datetime.fromisoformat(token_data["last_used"].replace("Z", "+00:00")) if token_data.get("last_used") else None
                )
                
        except Exception as e:
            logger.error(f"Error validating token: {e}")
            return None
    
    async def _update_token_usage(self, token_hash: str) -> None:
        """Update token usage statistics."""
        if not self.enabled:
            return
        
        try:
            async with httpx.AsyncClient() as client:
                await client.patch(
                    f"{self.supabase_url}/rest/v1/api_tokens",
                    headers=self._get_headers(),
                    params={"token_hash": f"eq.{token_hash}"},
                    json={
                        "last_used": datetime.now(UTC).isoformat(),
                        "usage_count": "usage_count + 1"  # PostgreSQL expression
                    }
                )
        except Exception as e:
            logger.error(f"Error updating token usage: {e}")
    
    async def revoke_token(self, token: str) -> bool:
        """
        Revoke a token by marking it as inactive.
        
        Args:
            token: The token to revoke
            
        Returns:
            True if revoked successfully, False otherwise
        """
        if not self.enabled:
            logger.debug("Supabase disabled, cannot revoke token")
            return False
        
        try:
            token_hash = self._hash_token(token)
            
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.supabase_url}/rest/v1/api_tokens",
                    headers=self._get_headers(),
                    params={"token_hash": f"eq.{token_hash}"},
                    json={"is_active": False}
                )
                
                return response.status_code == 204
                
        except Exception as e:
            logger.error(f"Error revoking token: {e}")
            return False
    
    async def log_security_event(self, event_type: str, token_hash: str, details: Dict[str, Any]) -> None:
        """
        Log security events to Supabase.
        
        Args:
            event_type: Type of security event
            token_hash: Hash of the token involved
            details: Additional event details
        """
        if not self.enabled:
            logger.info(f"Security event: {event_type} - {details}")
            return
        
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"{self.supabase_url}/rest/v1/security_logs",
                    headers=self._get_headers(),
                    json={
                        "event_type": event_type,
                        "token_hash": token_hash,
                        "details": details,
                        "timestamp": datetime.now(UTC).isoformat()
                    }
                )
        except Exception as e:
            logger.error(f"Error logging security event: {e}")
    
    def generate_token(self) -> str:
        """
        Generate a secure 32-byte random token.
        
        Returns:
            Hex-encoded secure random token
        """
        return secrets.token_hex(32)  # 32 bytes = 64 hex characters 