# Environment Setup for MCP Server

This directory contains comprehensive environment configuration files for your MCP server with session persistence support.

## 📁 Files

- **`env.example`** - Comprehensive environment variables template
- **`setup_env.sh`** - Interactive setup script
- **`ENV_SETUP_README.md`** - This file

## 🚀 Quick Setup

### Option 1: Interactive Setup (Recommended)

Run the interactive setup script:

```bash
cd dhafnck_mcp_main
./setup_env.sh
```

This script will:
- ✅ Create your `.env` file from the template
- ✅ Guide you through basic configuration
- ✅ Help configure AI provider API keys
- ✅ Set up session persistence options
- ✅ Validate your configuration
- ✅ Provide Cursor MCP integration examples

### Option 2: Manual Setup

1. **Copy the template**:
   ```bash
   cp env.example .env
   ```

2. **Edit the `.env` file**:
   ```bash
   nano .env  # or your preferred editor
   ```

3. **Configure the essential variables**:
   ```bash
   # Session Persistence (Redis recommended, memory fallback available)
   REDIS_URL=redis://localhost:6379/0
   
   # At least one AI provider
   OPENAI_API_KEY=sk-your-actual-openai-key-here
   # OR
   ANTHROPIC_API_KEY=sk-ant-your-actual-anthropic-key-here
   
   # Basic server settings
   MCP_ENVIRONMENT=development
   MCP_DEBUG=true
   MCP_LOG_LEVEL=INFO
   ```

## 🔧 Key Configuration Sections

### 🔄 Session Persistence
```bash
# Essential for fixing connection issues
REDIS_URL=redis://localhost:6379/0      # Redis for persistence
SESSION_TTL=3600                        # 1 hour session lifetime
MAX_EVENTS_PER_SESSION=1000            # Max events per session
SESSION_COMPRESSION=true               # Enable compression
```

### 🤖 AI Providers
```bash
# Configure at least one provider
OPENAI_API_KEY=sk-your-key-here        # OpenAI GPT models
ANTHROPIC_API_KEY=sk-ant-your-key-here # Claude models
GOOGLE_API_KEY=your-key-here           # Gemini models
PERPLEXITY_API_KEY=pplx-your-key-here  # Perplexity AI
```

### 🖥️ Server Settings
```bash
MCP_HOST=localhost                     # Server host
MCP_PORT=8000                         # Server port
MCP_ENVIRONMENT=development           # Environment mode
MCP_DEBUG=true                        # Debug logging
MCP_LOG_LEVEL=INFO                    # Log level
```

## 🔗 Cursor Integration

After setting up your `.env` file, update your `.cursor/mcp.json`:

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
        "MCP_LOG_LEVEL": "INFO",
        "SESSION_TTL": "3600",
        "MAX_EVENTS_PER_SESSION": "1000"
      }
    }
  }
}
```

## 🧪 Testing Your Setup

### Test Session Store
```bash
cd dhafnck_mcp_main
python -c "
from src.fastmcp.server.session_store import get_global_event_store
import asyncio
store = asyncio.run(get_global_event_store())
print('✅ Session store initialized:', type(store).__name__)
"
```

### Test Health Check
```bash
# After starting your MCP server, use the health check tool in Cursor:
session_health_check
```

## 🛠️ Environment Examples

### Minimal Setup (Memory Only)
```bash
# No Redis, basic functionality
REDIS_URL=
OPENAI_API_KEY=sk-your-key-here
MCP_DEBUG=true
```

### Development Setup
```bash
# Full development environment
REDIS_URL=redis://localhost:6379/0
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key-here
MCP_ENVIRONMENT=development
MCP_DEBUG=true
DEV_MODE=true
HOT_RELOAD=true
```

### Production Setup
```bash
# Production environment
REDIS_URL=redis://production-redis:6379/0
OPENAI_API_KEY=sk-your-production-key
MCP_ENVIRONMENT=production
MCP_DEBUG=false
MCP_LOG_LEVEL=WARNING
HTTPS_ENABLED=true
RATE_LIMIT_ENABLED=true
```

## 🔐 Security Notes

- ✅ **Never commit `.env` files** - They're automatically added to `.gitignore`
- ✅ **Use different API keys** for development and production
- ✅ **Rotate API keys regularly**
- ✅ **Use environment-specific Redis instances**
- ✅ **Enable rate limiting in production**

## 🐛 Troubleshooting

### Redis Connection Issues
```bash
# Test Redis connection
redis-cli ping
# Should return: PONG

# If Redis isn't running:
sudo systemctl start redis  # Linux
brew services start redis   # macOS
```

### API Key Issues
```bash
# Test OpenAI key
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models

# Test Anthropic key  
curl -H "x-api-key: $ANTHROPIC_API_KEY" \
     https://api.anthropic.com/v1/messages
```

### Session Store Issues
```bash
# Check if session store is working
python -c "
import asyncio
from src.fastmcp.server.session_store import create_event_store

async def test():
    store = create_event_store()
    if hasattr(store, 'connect'):
        connected = await store.connect()
        print('✅ Connected:', connected)
    print('✅ Store type:', type(store).__name__)

asyncio.run(test())
"
```

## 📞 Support

If you encounter issues:

1. **Check the logs**: Look for error messages in your MCP server logs
2. **Verify configuration**: Run `./setup_env.sh` again to validate settings
3. **Test components**: Use the test commands above to isolate issues
4. **Use health check**: The `session_health_check` tool provides detailed diagnostics

## 🎉 Next Steps

After setup:
1. ✅ Restart your MCP server
2. ✅ Test connection from Cursor
3. ✅ Run `session_health_check` to verify everything works
4. ✅ Enjoy persistent MCP sessions! 🚀 