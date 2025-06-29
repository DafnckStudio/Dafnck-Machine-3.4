#!/bin/bash

# =============================================================================
# MCP Server Environment Setup Script
# =============================================================================
# This script helps you set up your environment configuration quickly
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "\n${PURPLE}==============================================================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}==============================================================================${NC}\n"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "\n${CYAN}▶ $1${NC}"
}

print_header "MCP Server Environment Setup"

print_info "This script will help you set up your MCP server environment configuration."
print_info "You can run this script multiple times to update your configuration."

# Check if we're in the right directory
if [ ! -f "env.example" ]; then
    print_error "env.example file not found. Please run this script from the dhafnck_mcp_main directory."
    exit 1
fi

print_step "Step 1: Setting up .env file"

# Copy env.example to .env if it doesn't exist
if [ ! -f ".env" ]; then
    cp env.example .env
    print_success "Created .env file from env.example"
else
    print_warning ".env file already exists. Backing up to .env.backup"
    cp .env .env.backup
    print_info "You can compare your existing .env with env.example for new variables"
fi

print_step "Step 2: Basic Configuration"

# Function to prompt for input with default
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local var_name="$3"
    
    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " input
        value="${input:-$default}"
    else
        read -p "$prompt: " value
    fi
    
    if [ -n "$value" ]; then
        # Update the .env file
        if grep -q "^${var_name}=" .env; then
            sed -i "s|^${var_name}=.*|${var_name}=${value}|" .env
        else
            echo "${var_name}=${value}" >> .env
        fi
    fi
}

# Get current values from .env if they exist
get_current_value() {
    local var_name="$1"
    grep "^${var_name}=" .env 2>/dev/null | cut -d'=' -f2- | tr -d '"' || echo ""
}

print_info "Configuring basic settings..."

# Redis URL
current_redis=$(get_current_value "REDIS_URL")
prompt_with_default "Redis URL (leave empty for memory-only mode)" "$current_redis" "REDIS_URL"

# Environment
current_env=$(get_current_value "MCP_ENVIRONMENT")
prompt_with_default "Environment (development/staging/production)" "${current_env:-development}" "MCP_ENVIRONMENT"

# Debug mode
current_debug=$(get_current_value "MCP_DEBUG")
prompt_with_default "Enable debug mode? (true/false)" "${current_debug:-true}" "MCP_DEBUG"

# Log level
current_log=$(get_current_value "MCP_LOG_LEVEL")
prompt_with_default "Log level (DEBUG/INFO/WARNING/ERROR)" "${current_log:-INFO}" "MCP_LOG_LEVEL"

print_step "Step 3: AI Provider Configuration"

print_info "Configure API keys for AI providers you want to use (press Enter to skip):"

# OpenAI
current_openai=$(get_current_value "OPENAI_API_KEY")
if [ "$current_openai" = "sk-your-openai-api-key-here" ]; then
    current_openai=""
fi
prompt_with_default "OpenAI API Key" "$current_openai" "OPENAI_API_KEY"

# Anthropic
current_anthropic=$(get_current_value "ANTHROPIC_API_KEY")
if [ "$current_anthropic" = "sk-ant-your-anthropic-api-key-here" ]; then
    current_anthropic=""
fi
prompt_with_default "Anthropic API Key (Claude)" "$current_anthropic" "ANTHROPIC_API_KEY"

# Google
current_google=$(get_current_value "GOOGLE_API_KEY")
if [ "$current_google" = "your-google-ai-api-key-here" ]; then
    current_google=""
fi
prompt_with_default "Google AI API Key (Gemini)" "$current_google" "GOOGLE_API_KEY"

print_step "Step 4: Session Persistence Configuration"

# Session TTL
current_ttl=$(get_current_value "SESSION_TTL")
prompt_with_default "Session TTL in seconds" "${current_ttl:-3600}" "SESSION_TTL"

# Max events per session
current_max_events=$(get_current_value "MAX_EVENTS_PER_SESSION")
prompt_with_default "Max events per session" "${current_max_events:-1000}" "MAX_EVENTS_PER_SESSION"

print_step "Step 5: Validation"

print_info "Validating configuration..."

# Check if Redis URL is set and test connection
redis_url=$(get_current_value "REDIS_URL")
if [ -n "$redis_url" ] && [ "$redis_url" != "redis://localhost:6379/0" ]; then
    print_info "Testing Redis connection..."
    if command -v redis-cli &> /dev/null; then
        if redis-cli -u "$redis_url" ping &> /dev/null; then
            print_success "Redis connection successful"
        else
            print_warning "Could not connect to Redis. The system will fallback to memory storage."
        fi
    else
        print_warning "redis-cli not found. Cannot test Redis connection."
    fi
elif [ -z "$redis_url" ]; then
    print_info "Redis URL not set. Using memory-only mode."
else
    print_info "Using default Redis URL. Make sure Redis is running on localhost:6379"
fi

# Check for at least one AI provider
has_ai_key=false
for provider in OPENAI_API_KEY ANTHROPIC_API_KEY GOOGLE_API_KEY PERPLEXITY_API_KEY; do
    value=$(get_current_value "$provider")
    if [ -n "$value" ] && [[ "$value" != *"your-"* ]] && [[ "$value" != *"sk-your-"* ]]; then
        has_ai_key=true
        break
    fi
done

if [ "$has_ai_key" = true ]; then
    print_success "At least one AI provider is configured"
else
    print_warning "No AI providers configured. Some features may not work."
fi

print_step "Step 6: Cursor MCP Configuration"

print_info "For Cursor integration, you need to add these environment variables to your .cursor/mcp.json file:"
print_info ""
print_info "Example .cursor/mcp.json configuration:"
echo -e "${YELLOW}"
cat << 'EOF'
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
EOF
echo -e "${NC}"

print_step "Step 7: Final Steps"

print_success "Environment configuration completed!"
print_info ""
print_info "Next steps:"
print_info "1. Review your .env file: cat .env"
print_info "2. Update your .cursor/mcp.json with the environment variables"
print_info "3. Restart your MCP server"
print_info "4. Test the connection with: python -c \"from fastmcp.server.session_store import get_global_event_store; import asyncio; print('Session store test:', asyncio.run(get_global_event_store()))\""
print_info ""
print_success "Your MCP server is now configured with persistent session support!"

# Create .gitignore entry for .env if it doesn't exist
if [ ! -f ".gitignore" ]; then
    echo ".env" > .gitignore
    print_success "Created .gitignore with .env entry"
elif ! grep -q "^\.env$" .gitignore; then
    echo ".env" >> .gitignore
    print_success "Added .env to .gitignore"
fi

print_info ""
print_info "Environment setup complete! 🚀" 