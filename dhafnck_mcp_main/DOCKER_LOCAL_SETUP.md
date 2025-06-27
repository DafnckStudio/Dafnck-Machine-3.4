# DhafnckMCP Local Docker Setup (No Authentication)

This guide shows you how to run the DhafnckMCP server locally using Docker **without authentication** for development purposes.

## 🚀 Quick Start

### Option 1: Use the Startup Script (Recommended)

```bash
cd dhafnck_mcp_main
./run-local.sh
```

### Option 2: Manual Docker Compose

```bash
cd dhafnck_mcp_main
docker-compose -f docker-compose.yml -f docker-compose.local.yml up --build
```

### Option 3: Set Environment Variable

If you prefer to modify the main docker-compose.yml:

```bash
cd dhafnck_mcp_main
export DHAFNCK_AUTH_ENABLED=false
docker-compose up --build
```

## 🔓 Authentication Status

- **Authentication**: DISABLED
- **Tokens**: Not required
- **All MCP operations**: Allowed without authentication
- **Supabase**: Not needed

## 🌐 Server Endpoints

Once running, your server will be available at:

- **Main Server**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **Server Capabilities**: http://localhost:8000/capabilities
- **Debug Port**: http://localhost:8001 (if needed)

## 📁 Data Persistence

The following directories are created automatically:

- `./data/tasks/` - Task management data
- `./data/projects/` - Project data
- `./data/rules/` - Cursor rules
- `./logs/` - Server logs

## 🛠️ Development Features

The local setup includes:

- **No Authentication**: All requests allowed
- **Enhanced Logging**: Rich tracebacks enabled
- **Development Mode**: Additional debugging features
- **Live Reload**: Source code mounting (optional)
- **Verbose Logging**: Detailed logs for debugging

## 🔧 Configuration

The local setup uses `docker-compose.local.yml` which overrides:

- `DHAFNCK_AUTH_ENABLED=false`
- `DHAFNCK_MVP_MODE=false`
- `FASTMCP_LOG_LEVEL=INFO`
- `FASTMCP_ENABLE_RICH_TRACEBACKS=1`
- Clears Supabase configuration

## 🧪 Testing the Server

Test that authentication is disabled:

```bash
# Health check (should work without token)
curl http://localhost:8000/health

# Get server capabilities (should work without token)
curl http://localhost:8000/capabilities

# Test MCP tools (should work without token)
curl -X POST http://localhost:8000/tools \
  -H "Content-Type: application/json" \
  -d '{"name": "health_check"}'
```

## 🛑 Stopping the Server

```bash
# If using the script or docker-compose
Ctrl+C

# Or force stop
docker-compose -f docker-compose.yml -f docker-compose.local.yml down
```

## 📝 Logs

View server logs:

```bash
# Real-time logs
docker-compose -f docker-compose.yml -f docker-compose.local.yml logs -f

# Or check log files
tail -f logs/dhafnck-mcp.log
```

## 🔄 Switching Back to Production

To re-enable authentication for production:

1. Remove the `-f docker-compose.local.yml` from your command
2. Set environment variables:
   ```bash
   export DHAFNCK_AUTH_ENABLED=true
   export SUPABASE_URL=your-supabase-url
   export SUPABASE_ANON_KEY=your-supabase-key
   ```
3. Run: `docker-compose up --build`

## 🐛 Troubleshooting

### Port Already in Use

```bash
# Find what's using port 8000
sudo lsof -i :8000

# Stop and remove containers
docker-compose down
```

### Permission Issues

```bash
# Fix data directory permissions
sudo chown -R $USER:$USER data logs
chmod -R 755 data logs
```

### Container Won't Start

```bash
# Check logs
docker-compose logs dhafnck-mcp

# Rebuild from scratch
docker-compose down --volumes
docker-compose up --build
```

## ✅ Success Indicators

You'll know the server is working when you see:

1. ✅ Server starts without authentication errors
2. ✅ Health check returns 200 OK
3. ✅ MCP tools work without tokens
4. ✅ No Supabase connection errors
5. ✅ Logs show "Authentication is DISABLED" 