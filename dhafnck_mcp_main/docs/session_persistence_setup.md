# MCP Session Persistence Setup Guide

## Overview

This guide explains how to set up persistent session storage for your dhafnck_mcp_http server to solve connection and session management issues.

## The Problem

Previously, your MCP server was configured with `event_store=None`, which meant:
- Sessions existed only in memory
- Sessions were lost on server restart
- Network interruptions caused permanent session loss
- No session recovery capability

## The Solution

We've implemented a Redis-based EventStore with memory fallback that provides:
- ✅ Persistent session storage across server restarts
- ✅ Automatic fallback to memory if Redis is unavailable
- ✅ Session recovery after network interruptions
- ✅ Configurable TTL and cleanup policies
- ✅ Health monitoring and diagnostics

## Quick Setup

### Option 1: Redis (Recommended)

1. **Install Redis** (if not already installed):
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt install redis-server
   
   # macOS
   brew install redis
   
   # Start Redis
   redis-server
   ```

2. **Configure Environment Variables**:
   Add to your `.env` file or `.cursor/mcp.json`:
   ```bash
   REDIS_URL=redis://localhost:6379/0
   ```

3. **Restart MCP Server**:
   ```bash
   # Your server will automatically use Redis for session persistence
   ```

### Option 2: Memory Fallback (Automatic)

If Redis is not available, the system automatically falls back to memory-based storage:
- Sessions persist during server runtime
- Lost on server restart (but better than no persistence)
- No additional configuration required

## Configuration Options

### Environment Variables

Add these to your `.env` file or MCP configuration:

```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379/0        # Redis connection URL
REDIS_HOST=localhost                      # Redis host (alternative)
REDIS_PORT=6379                          # Redis port (alternative)  
REDIS_DB=0                               # Redis database number
REDIS_PASSWORD=                          # Redis password (if required)

# Session Settings
SESSION_TTL=3600                         # Session TTL in seconds (1 hour)
MAX_EVENTS_PER_SESSION=1000             # Max events per session
SESSION_COMPRESSION=true                 # Enable data compression
```

### Advanced Redis Configuration

For production environments:

```bash
# High availability Redis
REDIS_URL=redis://username:password@redis-cluster.example.com:6379/0

# Redis Sentinel
REDIS_URL=redis-sentinel://sentinel1:26379,sentinel2:26379/mymaster

# Redis Cluster  
REDIS_URL=redis-cluster://node1:7000,node2:7000,node3:7000
```

## Health Monitoring

### Using the Health Check Tool

The server now includes a built-in health check tool:

```bash
# In your MCP client (like Cursor), you can call:
session_health_check
```

This will show:
- ✅ Session store type and connectivity
- ✅ Current session status
- ✅ Redis connection health
- ✅ Storage test results
- ✅ Performance metrics
- ✅ Recommendations for issues

### Example Health Check Output

```
✅ Session Health Status: HEALTHY

Core Information:
- Session Store: RedisEventStore
- Session Active: true
- Current Session ID: mcp_session_abc123
- Total Sessions: 5

Redis Information:
- Redis Available: true
- Redis Connected: true
- Using Fallback: false
- Connected Clients: 2
- Memory Used: 1.2M

Storage Test: ✅ PASS

Recent Session Events:
- connection_established (age: 30.2s)
- tool_call (age: 15.1s)
- health_check (age: 0.1s)

💡 Recommendations:
- Session persistence is working correctly
- Consider setting up Redis backup for production use
```

## Troubleshooting

### Common Issues

1. **"Using memory fallback instead of Redis"**
   ```bash
   # Check if Redis is running
   redis-cli ping
   # Should return: PONG
   
   # Check connection
   redis-cli -u redis://localhost:6379 ping
   ```

2. **"Redis connection unavailable"**
   ```bash
   # Check Redis logs
   sudo journalctl -u redis-server
   
   # Verify port is open
   netstat -tlnp | grep :6379
   ```

3. **"Session storage test failed"**
   ```bash
   # Check Redis permissions
   redis-cli ACL LIST
   
   # Test manual storage
   redis-cli set test_key test_value
   redis-cli get test_key
   ```

### Diagnostic Commands

```bash
# Test Redis connectivity
redis-cli -u $REDIS_URL ping

# Monitor Redis operations
redis-cli -u $REDIS_URL monitor

# Check session keys
redis-cli -u $REDIS_URL keys "mcp:session:*"

# View session data
redis-cli -u $REDIS_URL lrange "mcp:session:your_session_id" 0 -1
```

## Performance Tuning

### Redis Optimization

```bash
# In redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### Session Store Tuning

```bash
# Adjust based on your needs
SESSION_TTL=7200                    # 2 hours for longer sessions
MAX_EVENTS_PER_SESSION=500          # Reduce for memory efficiency
SESSION_COMPRESSION=false           # Disable for faster access
```

## Production Deployment

### Docker Setup

```dockerfile
# docker-compose.yml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes
  
  mcp_server:
    build: .
    environment:
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - redis

volumes:
  redis_data:
```

### Monitoring

```bash
# Monitor session metrics
redis-cli -u $REDIS_URL info stats

# Check memory usage
redis-cli -u $REDIS_URL info memory

# Monitor connected clients
redis-cli -u $REDIS_URL client list
```

## Migration from Memory-Only

If you're upgrading from the previous memory-only setup:

1. **No data migration needed** - old sessions will naturally expire
2. **Restart required** - server needs restart to load new EventStore
3. **Verify health** - use `session_health_check` tool to confirm

## Security Considerations

### Redis Security

```bash
# Enable authentication
requirepass your_secure_password

# Bind to specific interfaces
bind 127.0.0.1 ::1

# Disable dangerous commands
rename-command FLUSHDB ""
rename-command FLUSHALL ""
```

### Network Security

```bash
# Use TLS for Redis connections
REDIS_URL=rediss://username:password@redis.example.com:6380/0

# Firewall rules
sudo ufw allow from 10.0.0.0/8 to any port 6379
```

## Next Steps

1. **Set up Redis** using Option 1 above
2. **Configure environment variables** in your `.env` or MCP config
3. **Restart your MCP server**
4. **Run health check** to verify everything is working
5. **Test session persistence** by restarting server and reconnecting

Your session connection issues should now be resolved! 🎉

## Support

If you encounter any issues:

1. Run the `session_health_check` tool for diagnostics
2. Check server logs for detailed error information
3. Verify Redis connectivity using the troubleshooting commands above
4. Consider starting with memory fallback mode if Redis setup is complex 