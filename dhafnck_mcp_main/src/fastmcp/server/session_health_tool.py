"""
Session Health Check Tool for MCP Server

This module provides a tool to check the health and status of the session store,
helping diagnose connection and persistence issues.

Author: System Architect Agent
Date: 2025-01-27
Purpose: Monitor and diagnose session persistence health
"""

import logging
from typing import Dict, Any, Optional

from fastmcp.server.context import Context

logger = logging.getLogger(__name__)


async def session_health_check(ctx: Context) -> Dict[str, Any]:
    """
    Check the health status of the MCP session persistence system
    
    Returns comprehensive information about:
    - Session store connectivity
    - Current session count
    - Redis connection status
    - Memory fallback status
    - Performance metrics
    """
    try:
        from .session_store import get_global_event_store
        
        # Get the global event store
        event_store = await get_global_event_store()
        
        # Basic health info
        health_info = {
            "session_store_type": type(event_store).__name__,
            "current_session_id": ctx.session_id,
            "timestamp": ctx.request_context.session.created_at.isoformat() if hasattr(ctx.request_context.session, 'created_at') else "unknown"
        }
        
        # Get detailed health from event store if available
        if hasattr(event_store, 'health_check'):
            store_health = await event_store.health_check()
            health_info.update(store_health)
        
        # Add session context information
        if ctx.session_id:
            health_info["session_active"] = True
            health_info["session_id_length"] = len(ctx.session_id)
            
            # Try to get events for current session if possible
            if hasattr(event_store, 'get_events'):
                try:
                    events = await event_store.get_events(ctx.session_id, limit=5)
                    health_info["recent_events_count"] = len(events)
                    health_info["recent_events"] = [
                        {
                            "type": event.event_type,
                            "timestamp": event.timestamp,
                            "age_seconds": event.timestamp - event.timestamp if hasattr(event, 'timestamp') else 0
                        }
                        for event in events[:3]  # Show last 3 events
                    ]
                except Exception as e:
                    health_info["events_error"] = str(e)
        else:
            health_info["session_active"] = False
            health_info["session_warning"] = "No session ID available - this may indicate session persistence issues"
        
        # Check if we can store a test event
        if hasattr(event_store, 'store_event') and ctx.session_id:
            try:
                test_success = await event_store.store_event(
                    session_id=ctx.session_id,
                    event_type="health_check",
                    event_data={"test": True, "timestamp": health_info.get("timestamp", "unknown")},
                    ttl=60  # 1 minute TTL for test event
                )
                health_info["test_store_success"] = test_success
            except Exception as e:
                health_info["test_store_error"] = str(e)
                health_info["test_store_success"] = False
        
        # Overall health assessment
        health_info["overall_status"] = "healthy"
        
        # Check for warning conditions
        warnings = []
        if not health_info.get("session_active"):
            warnings.append("No active session detected")
        
        if health_info.get("using_fallback"):
            warnings.append("Using memory fallback instead of Redis")
        
        if not health_info.get("redis_connected", True):
            warnings.append("Redis connection unavailable")
        
        if not health_info.get("test_store_success", True):
            warnings.append("Session storage test failed")
        
        if warnings:
            health_info["warnings"] = warnings
            health_info["overall_status"] = "degraded" if len(warnings) <= 2 else "unhealthy"
        
        health_info["recommendations"] = []
        
        # Add recommendations based on status
        if health_info.get("using_fallback"):
            health_info["recommendations"].append(
                "Consider setting up Redis for persistent session storage. "
                "Set REDIS_URL environment variable or check Redis connectivity."
            )
        
        if not health_info.get("session_active"):
            health_info["recommendations"].append(
                "Session persistence may not be working correctly. "
                "Check MCP client connection and server configuration."
            )
        
        if health_info.get("session_count", 0) > 1000:
            health_info["recommendations"].append(
                "High session count detected. Consider implementing session cleanup policies."
            )
        
        logger.info(f"Session health check completed: {health_info['overall_status']}")
        
        return health_info
        
    except Exception as e:
        logger.error(f"Session health check failed: {e}")
        return {
            "overall_status": "error",
            "error": str(e),
            "session_active": False,
            "recommendations": [
                "Session health check failed. Check server logs for detailed error information.",
                "Verify that session store dependencies are properly installed.",
                "Consider restarting the MCP server if issues persist."
            ]
        }


def register_session_health_tool(server):
    """Register the session health check tool with the FastMCP server"""
    
    @server.tool(
        name="session_health_check",
        description="Check the health and status of MCP session persistence system"
    )
    async def session_health_tool(ctx: Context) -> str:
        """
        Check MCP session persistence health
        
        Returns detailed information about:
        - Session store connectivity and type
        - Current session status
        - Redis connection health
        - Storage test results
        - Performance metrics
        - Recommendations for issues
        """
        health_info = await session_health_check(ctx)
        
        # Format the response for better readability
        status_emoji = {
            "healthy": "✅",
            "degraded": "⚠️", 
            "unhealthy": "❌",
            "error": "🚨"
        }
        
        emoji = status_emoji.get(health_info.get("overall_status", "error"), "❓")
        
        response = f"{emoji} **Session Health Status: {health_info.get('overall_status', 'unknown').upper()}**\n\n"
        
        # Core information
        response += "**Core Information:**\n"
        response += f"- Session Store: {health_info.get('session_store_type', 'unknown')}\n"
        response += f"- Session Active: {health_info.get('session_active', False)}\n"
        response += f"- Current Session ID: {health_info.get('current_session_id', 'none')}\n"
        
        if health_info.get('session_count') is not None:
            response += f"- Total Sessions: {health_info.get('session_count', 0)}\n"
        
        # Redis information
        if 'redis_available' in health_info:
            response += f"\n**Redis Information:**\n"
            response += f"- Redis Available: {health_info.get('redis_available', False)}\n"
            response += f"- Redis Connected: {health_info.get('redis_connected', False)}\n"
            response += f"- Using Fallback: {health_info.get('using_fallback', False)}\n"
            
            if health_info.get('redis_info'):
                redis_info = health_info['redis_info']
                response += f"- Connected Clients: {redis_info.get('connected_clients', 'unknown')}\n"
                response += f"- Memory Used: {redis_info.get('used_memory', 'unknown')}\n"
        
        # Test results
        if 'test_store_success' in health_info:
            test_status = "✅ PASS" if health_info['test_store_success'] else "❌ FAIL"
            response += f"\n**Storage Test:** {test_status}\n"
        
        # Recent events
        if health_info.get('recent_events'):
            response += f"\n**Recent Session Events:**\n"
            for event in health_info['recent_events']:
                response += f"- {event.get('type', 'unknown')} (age: {event.get('age_seconds', 0):.1f}s)\n"
        
        # Warnings
        if health_info.get('warnings'):
            response += f"\n**⚠️ Warnings:**\n"
            for warning in health_info['warnings']:
                response += f"- {warning}\n"
        
        # Recommendations
        if health_info.get('recommendations'):
            response += f"\n**💡 Recommendations:**\n"
            for rec in health_info['recommendations']:
                response += f"- {rec}\n"
        
        # Error details
        if health_info.get('error'):
            response += f"\n**🚨 Error Details:**\n{health_info['error']}\n"
        
        return response
    
    logger.info("Session health check tool registered successfully")
    return session_health_tool 