# Docker Rebuild Guide - Redis Session Persistence

This guide explains how to rebuild your MCP server Docker containers with Redis session persistence to fix connection issues.

## 🎯 What This Fixes

Your MCP server was experiencing session connection issues because:
- ❌ Sessions were stored only in memory
- ❌ Sessions were lost on server restart or network interruptions
- ❌ No session recovery capability

After rebuild:
- ✅ **Persistent sessions** with Redis storage
- ✅ **Automatic session recovery** after network interruptions
- ✅ **Memory fallback** if Redis becomes unavailable
- ✅ **Enhanced health monitoring**

## 🚀 Quick Rebuild (Automated)

### Option 1: Use the Automated Script

```bash
cd dhafnck_mcp_main
./docker/rebuild_with_redis.sh
```

This script will:
- ✅ Stop existing containers
- ✅ Clean up old images
- ✅ Rebuild with Redis support
- ✅ Start services with health checks
- ✅ Verify session persistence is working
- ✅ Provide connection information

## 🔧 Manual Rebuild (Step by Step)

### Step 1: Stop Existing Containers

```bash
cd dhafnck_mcp_main/docker
docker-compose -f docker-compose.yml down --remove-orphans
```

### Step 2: Clean Up Old Images

```bash
# Remove old MCP server image to force rebuild
docker rmi dhafnck/mcp-server:latest || true
docker image prune -f
```

### Step 3: Build New Image with Redis Support

```bash
# Build with Redis dependencies included
docker-compose -f docker-compose.yml build --no-cache
```

### Step 4: Start with Redis Session Persistence

```bash
# Start MCP server + Redis
docker-compose -f docker-compose.yml -f docker-compose.redis.yml up -d
```

### Step 5: Verify Services

```bash
# Check service status
docker-compose -f docker-compose.yml -f docker-compose.redis.yml ps

# Test Redis connection
docker exec dhafnck-redis redis-cli ping
# Should return: PONG

# Test session store
docker exec dhafnck-mcp-server python -c "
import sys; sys.path.insert(0, '/app/src')
from fastmcp.server.session_store import get_global_event_store
import asyncio
store = asyncio.run(get_global_event_store())
print('Session store:', type(store).__name__)
"
```

## 📁 New Files Added

### 1. **`docker/docker-compose.redis.yml`**
- Redis service configuration
- Enhanced MCP server environment variables
- Network configuration for service communication

### 2. **`docker/rebuild_with_redis.sh`**
- Automated rebuild script
- Health checks and verification
- Step-by-step progress reporting

### 3. **Updated `pyproject.toml`**
- Added `redis>=5.0.0` dependency
- Session persistence support

## 🔗 Services After Rebuild

| Service | Container | Port | Purpose |
|---------|-----------|------|---------|
| **dhafnck-mcp** | dhafnck-mcp-server | 8000 | MCP server with session persistence |
| **redis** | dhafnck-redis | 6379 | Session storage and caching |

## 🌐 Connection Information

### MCP Server
- **URL**: `http://localhost:8000`
- **Transport**: `streamable-http`
- **Session Store**: `RedisEventStore`

### Redis Server
- **URL**: `redis://localhost:6379/0`
- **Container**: `dhafnck-redis`
- **Data**: Persistent volume `dhafnck_redis_data`

## 🔧 Configuration

### Environment Variables (Automatically Set)

```bash
# Session Persistence
REDIS_URL=redis://redis:6379/0
SESSION_TTL=3600
MAX_EVENTS_PER_SESSION=1000
SESSION_COMPRESSION=true

# Health & Monitoring
SESSION_PERSISTENCE_ENABLED=true
FALLBACK_TO_MEMORY=true
```

### Cursor MCP Configuration

Update your `.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "dhafnck_mcp_http": {
      "command": "python",
      "args": ["-m", "fastmcp.server"],
      "env": {
        "REDIS_URL": "redis://localhost:6379/0",
        "OPENAI_API_KEY": "your-actual-api-key-here",
        "ANTHROPIC_API_KEY": "your-actual-api-key-here",
        "MCP_DEBUG": "true",
        "MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

## 🧪 Testing Your Rebuild

### 1. Health Check

```bash
# Check service health
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.redis.yml ps
```

### 2. Redis Connection Test

```bash
# Test Redis directly
docker exec dhafnck-redis redis-cli ping

# Check Redis data
docker exec dhafnck-redis redis-cli info memory
```

### 3. Session Store Test

```bash
# Test session store integration
docker exec dhafnck-mcp-server python -c "
import sys, asyncio
sys.path.insert(0, '/app/src')
from fastmcp.server.session_store import get_global_event_store

async def test():
    store = await get_global_event_store()
    print('✅ Store type:', type(store).__name__)
    if hasattr(store, 'health_check'):
        health = await store.health_check()
        print('✅ Redis connected:', health.get('redis_connected'))
        print('✅ Session count:', health.get('session_count'))

asyncio.run(test())
"
```

### 4. MCP Session Health (After Cursor Connection)

In Cursor, use the health check tool:
```bash
session_health_check
```

Expected output:
```
✅ Session Health Status: HEALTHY
- Session Store: RedisEventStore
- Redis Connected: true
- Using Fallback: false
- Session Count: 1
```

## 🛠️ Management Commands

### Monitor Logs

```bash
# All services
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.redis.yml logs -f

# MCP server only
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.redis.yml logs -f dhafnck-mcp

# Redis only
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.redis.yml logs -f redis
```

### Restart Services

```bash
# Restart all
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.redis.yml restart

# Restart MCP server only
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.redis.yml restart dhafnck-mcp

# Restart Redis only
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.redis.yml restart redis
```

### Stop Services

```bash
# Stop all
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.redis.yml down

# Stop and remove volumes (⚠️ This deletes session data)
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.redis.yml down -v
```

### Check Session Data

```bash
# List active sessions
docker exec dhafnck-redis redis-cli keys "mcp:session:*"

# View session details
docker exec dhafnck-redis redis-cli lrange "mcp:session:your-session-id" 0 -1

# Monitor Redis activity
docker exec dhafnck-redis redis-cli monitor
```

## 🐛 Troubleshooting

### Redis Connection Issues

```bash
# Check if Redis is running
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.redis.yml ps redis

# Check Redis logs
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.redis.yml logs redis

# Test Redis connection
docker exec dhafnck-redis redis-cli ping
```

### MCP Server Issues

```bash
# Check MCP server logs
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.redis.yml logs dhafnck-mcp

# Check if server is responding
curl -X GET http://localhost:8000/health

# Test session store manually
docker exec dhafnck-mcp-server python -c "
import sys; sys.path.insert(0, '/app/src')
from fastmcp.server.session_store import create_event_store
store = create_event_store()
print('Store created:', type(store).__name__)
"
```

### Build Issues

```bash
# Force complete rebuild
docker-compose -f docker/docker-compose.yml build --no-cache --pull

# Check build logs
docker-compose -f docker/docker-compose.yml build --progress=plain

# Clean Docker system
docker system prune -a
```

## 🔄 Rollback (If Needed)

If you need to rollback to the previous setup:

```bash
# Stop Redis setup
docker-compose -f docker/docker-compose.yml -f docker/docker-compose.redis.yml down

# Start without Redis
docker-compose -f docker/docker-compose.yml up -d
```

Note: This will use memory-only sessions (original behavior).

## 🎉 Success Indicators

After successful rebuild, you should see:

1. **✅ Both services running**: `dhafnck-mcp-server` and `dhafnck-redis`
2. **✅ Health checks passing**: Both containers show "healthy" status
3. **✅ Redis responding**: `redis-cli ping` returns `PONG`
4. **✅ Session store working**: `session_health_check` shows Redis connected
5. **✅ Stable connections**: No more automatic disconnections in Cursor

## 📞 Support

If you encounter issues:

1. **Check logs**: Use the log commands above to identify errors
2. **Verify network**: Ensure containers can communicate
3. **Test components**: Use the individual test commands
4. **Rebuild clean**: Use `--no-cache` flag for complete rebuild

Your MCP server session connection issues should now be completely resolved! 🚀 