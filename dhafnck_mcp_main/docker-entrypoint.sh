#!/bin/bash
set -e

# DhafnckMCP Docker Entrypoint Script
# Handles initialization, environment setup, and graceful startup

echo "🚀 Starting DhafnckMCP Server..."
echo "================================"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to validate environment
validate_environment() {
    log "🔍 Validating environment..."
    
    # Check if data directory exists and is writable
    if [ ! -d "/data" ]; then
        log "❌ ERROR: /data directory not found"
        exit 1
    fi
    
    if [ ! -w "/data" ]; then
        log "❌ ERROR: /data directory not writable"
        exit 1
    fi
    
    # Create subdirectories if they don't exist
    mkdir -p /data/tasks /data/projects /data/contexts /data/rules
    
    log "✅ Environment validation passed"
}

# Function to set up default environment variables
setup_environment() {
    log "⚙️  Setting up environment variables..."
    
    # Set default paths if not provided
    export TASKS_JSON_PATH="${TASKS_JSON_PATH:-/data/tasks}"
    export PROJECTS_FILE_PATH="${PROJECTS_FILE_PATH:-/data/projects/projects.json}"
    export CURSOR_RULES_DIR="${CURSOR_RULES_DIR:-/data/rules}"
    export CURSOR_AGENT_DIR_PATH="${CURSOR_AGENT_DIR_PATH:-/app/src/fastmcp}"
    
    # Create projects.json if it doesn't exist
    if [ ! -f "$PROJECTS_FILE_PATH" ]; then
        mkdir -p "$(dirname "$PROJECTS_FILE_PATH")"
        echo '{}' > "$PROJECTS_FILE_PATH"
        log "📁 Created default projects.json"
    fi
    
    log "✅ Environment setup complete"
}

# Function to validate Supabase configuration (if provided)
validate_supabase() {
    if [ -n "$SUPABASE_URL" ] && [ -n "$SUPABASE_ANON_KEY" ]; then
        log "🔐 Supabase configuration detected"
        
        # Validate URL format
        if [[ ! "$SUPABASE_URL" =~ ^https://[a-zA-Z0-9-]+\.supabase\.co$ ]]; then
            log "⚠️  WARNING: SUPABASE_URL format may be invalid"
        fi
        
        # Validate key format (basic check)
        if [ ${#SUPABASE_ANON_KEY} -lt 100 ]; then
            log "⚠️  WARNING: SUPABASE_ANON_KEY appears to be too short"
        fi
        
        log "✅ Supabase validation complete"
    else
        log "ℹ️  No Supabase configuration provided (optional for MVP)"
    fi
}

# Function to perform health check
health_check() {
    log "🏥 Performing startup health check..."
    
    # Test Python import
    if ! python -c "from src.fastmcp.server.mcp_entry_point import create_dhafnck_mcp_server" 2>/dev/null; then
        log "❌ ERROR: Failed to import DhafnckMCP server"
        exit 1
    fi
    
    log "✅ Health check passed"
}

# Function to handle graceful shutdown
cleanup() {
    log "🛑 Received shutdown signal, cleaning up..."
    # Kill any background processes
    jobs -p | xargs -r kill
    log "👋 Shutdown complete"
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Main initialization
main() {
    log "🎯 DhafnckMCP Server v2.0.0"
    log "📍 Working directory: $(pwd)"
    log "👤 Running as user: $(whoami)"
    
    # Run validation steps
    validate_environment
    setup_environment
    validate_supabase
    health_check
    
    # Display configuration
    log "📊 Configuration:"
    log "   - TASKS_JSON_PATH: $TASKS_JSON_PATH"
    log "   - PROJECTS_FILE_PATH: $PROJECTS_FILE_PATH"
    log "   - CURSOR_RULES_DIR: $CURSOR_RULES_DIR"
    log "   - PYTHONPATH: $PYTHONPATH"
    
    if [ -n "$SUPABASE_URL" ]; then
        log "   - SUPABASE_URL: $SUPABASE_URL"
        log "   - SUPABASE_ANON_KEY: [CONFIGURED]"
    fi
    
    log "🚀 Starting server with command: $*"
    log "================================"
    
    # Execute the main command
    exec "$@"
}

# Run main function
main "$@" 