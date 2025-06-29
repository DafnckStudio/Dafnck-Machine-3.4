#!/bin/bash

# MCP Session Persistence Setup Script
# This script sets up Redis and configures session persistence for dhafnck_mcp_http

set -e  # Exit on any error

echo "🚀 MCP Session Persistence Setup"
echo "================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
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

# Check if running as root for system package installation
check_sudo() {
    if [[ $EUID -eq 0 ]]; then
        print_warning "Running as root. This is not recommended for development."
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Detect OS and package manager
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            OS="ubuntu"
            PACKAGE_MANAGER="apt"
        elif command -v yum &> /dev/null; then
            OS="centos"
            PACKAGE_MANAGER="yum"
        elif command -v pacman &> /dev/null; then
            OS="arch"
            PACKAGE_MANAGER="pacman"
        else
            OS="linux"
            PACKAGE_MANAGER="unknown"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        PACKAGE_MANAGER="brew"
    else
        OS="unknown"
        PACKAGE_MANAGER="unknown"
    fi
    
    print_status "Detected OS: $OS with package manager: $PACKAGE_MANAGER"
}

# Install Redis based on OS
install_redis() {
    print_status "Installing Redis..."
    
    case $PACKAGE_MANAGER in
        "apt")
            sudo apt update
            sudo apt install -y redis-server
            ;;
        "yum")
            sudo yum install -y redis
            ;;
        "pacman")
            sudo pacman -S --noconfirm redis
            ;;
        "brew")
            if ! command -v brew &> /dev/null; then
                print_error "Homebrew not found. Please install Homebrew first:"
                print_error "https://brew.sh/"
                exit 1
            fi
            brew install redis
            ;;
        *)
            print_error "Unsupported package manager: $PACKAGE_MANAGER"
            print_error "Please install Redis manually and re-run this script."
            exit 1
            ;;
    esac
    
    print_success "Redis installed successfully"
}

# Check if Redis is already installed
check_redis_installed() {
    if command -v redis-server &> /dev/null; then
        print_success "Redis is already installed"
        return 0
    else
        print_status "Redis not found, installing..."
        return 1
    fi
}

# Start Redis service
start_redis() {
    print_status "Starting Redis service..."
    
    case $OS in
        "ubuntu"|"centos")
            if systemctl is-active --quiet redis-server; then
                print_success "Redis service is already running"
            elif systemctl is-active --quiet redis; then
                print_success "Redis service is already running"
            else
                # Try different service names
                if systemctl list-unit-files | grep -q redis-server; then
                    sudo systemctl start redis-server
                    sudo systemctl enable redis-server
                elif systemctl list-unit-files | grep -q redis; then
                    sudo systemctl start redis
                    sudo systemctl enable redis
                else
                    print_warning "Could not start Redis service automatically"
                    print_status "Please start Redis manually: redis-server"
                fi
            fi
            ;;
        "macos")
            if pgrep -f redis-server > /dev/null; then
                print_success "Redis is already running"
            else
                print_status "Starting Redis with brew services..."
                brew services start redis
            fi
            ;;
        *)
            print_warning "Please start Redis manually: redis-server"
            ;;
    esac
}

# Test Redis connection
test_redis() {
    print_status "Testing Redis connection..."
    
    if redis-cli ping > /dev/null 2>&1; then
        print_success "Redis connection test passed"
        return 0
    else
        print_error "Redis connection test failed"
        print_status "Trying to start Redis server..."
        
        # Try to start Redis in background
        if command -v redis-server &> /dev/null; then
            redis-server --daemonize yes --port 6379
            sleep 2
            
            if redis-cli ping > /dev/null 2>&1; then
                print_success "Redis started and connection test passed"
                return 0
            fi
        fi
        
        print_error "Could not establish Redis connection"
        return 1
    fi
}

# Configure environment variables
configure_env() {
    print_status "Configuring environment variables..."
    
    ENV_FILE=".env"
    MCP_CONFIG=".cursor/mcp.json"
    
    # Create .env file if it doesn't exist
    if [[ ! -f "$ENV_FILE" ]]; then
        print_status "Creating .env file..."
        cat > "$ENV_FILE" << EOF
# MCP Session Persistence Configuration
REDIS_URL=redis://localhost:6379/0
SESSION_TTL=3600
MAX_EVENTS_PER_SESSION=1000
SESSION_COMPRESSION=true

# Add your other environment variables below...
EOF
        print_success "Created .env file with Redis configuration"
    else
        # Check if Redis configuration already exists
        if grep -q "REDIS_URL" "$ENV_FILE"; then
            print_success "Redis configuration already exists in .env"
        else
            print_status "Adding Redis configuration to existing .env file..."
            cat >> "$ENV_FILE" << EOF

# MCP Session Persistence Configuration (added by setup script)
REDIS_URL=redis://localhost:6379/0
SESSION_TTL=3600
MAX_EVENTS_PER_SESSION=1000
SESSION_COMPRESSION=true
EOF
            print_success "Added Redis configuration to .env file"
        fi
    fi
    
    # Configure MCP config if it exists
    if [[ -f "$MCP_CONFIG" ]]; then
        print_status "Found MCP configuration file"
        print_warning "Please manually add REDIS_URL to the 'env' section of .cursor/mcp.json:"
        print_warning '  "env": {'
        print_warning '    "REDIS_URL": "redis://localhost:6379/0"'
        print_warning '  }'
    fi
}

# Install Python Redis dependency
install_python_redis() {
    print_status "Checking Python Redis dependency..."
    
    # Check if we're in a virtual environment
    if [[ -n "$VIRTUAL_ENV" ]]; then
        print_status "Virtual environment detected: $VIRTUAL_ENV"
        pip install redis
        print_success "Installed Redis Python package in virtual environment"
    elif [[ -f "dhafnck_mcp_main/.venv/bin/activate" ]]; then
        print_status "Found project virtual environment"
        source dhafnck_mcp_main/.venv/bin/activate
        pip install redis
        print_success "Installed Redis Python package in project virtual environment"
    elif [[ -f ".venv/bin/activate" ]]; then
        print_status "Found local virtual environment"
        source .venv/bin/activate
        pip install redis
        print_success "Installed Redis Python package in local virtual environment"
    else
        print_warning "No virtual environment detected"
        print_status "Installing Redis Python package globally..."
        pip install redis --user
        print_success "Installed Redis Python package for user"
    fi
}

# Run health check
run_health_check() {
    print_status "Running session persistence health check..."
    
    # Create a simple test script
    cat > /tmp/test_session_store.py << 'EOF'
import sys
import asyncio
import os

# Add the project path
sys.path.insert(0, 'dhafnck_mcp_main/src')

async def test_session_store():
    try:
        from fastmcp.server.session_store import create_event_store
        
        # Create event store
        event_store = create_event_store()
        
        # Test basic functionality
        if hasattr(event_store, 'connect'):
            connected = await event_store.connect()
            print(f"Connection successful: {connected}")
        
        # Test storing an event
        if hasattr(event_store, 'store_event'):
            success = await event_store.store_event(
                session_id="test_session",
                event_type="setup_test",
                event_data={"test": True}
            )
            print(f"Store test successful: {success}")
        
        # Test retrieving events
        if hasattr(event_store, 'get_events'):
            events = await event_store.get_events("test_session")
            print(f"Retrieved {len(events)} events")
        
        # Health check
        if hasattr(event_store, 'health_check'):
            health = await event_store.health_check()
            print(f"Health check: {health.get('overall_status', 'unknown')}")
            if health.get('redis_connected'):
                print("✅ Redis connection working")
            else:
                print("⚠️  Using memory fallback")
        
        # Cleanup
        if hasattr(event_store, 'disconnect'):
            await event_store.disconnect()
        
        print("✅ Session store test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Session store test failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_session_store())
    sys.exit(0 if result else 1)
EOF
    
    if python3 /tmp/test_session_store.py; then
        print_success "Session persistence health check passed"
    else
        print_warning "Session persistence health check failed"
        print_status "This may be normal if the MCP server is not running"
    fi
    
    # Cleanup
    rm -f /tmp/test_session_store.py
}

# Main installation process
main() {
    echo
    print_status "Starting MCP session persistence setup..."
    
    # Detect system
    detect_os
    
    # Check for sudo if needed
    if [[ "$PACKAGE_MANAGER" != "brew" ]] && [[ "$PACKAGE_MANAGER" != "unknown" ]]; then
        check_sudo
    fi
    
    # Install Redis if not present
    if ! check_redis_installed; then
        install_redis
    fi
    
    # Start Redis service
    start_redis
    
    # Test Redis connection
    if ! test_redis; then
        print_error "Redis setup failed. Please check the installation and try again."
        exit 1
    fi
    
    # Install Python dependencies
    install_python_redis
    
    # Configure environment
    configure_env
    
    # Run health check
    run_health_check
    
    echo
    print_success "🎉 MCP Session Persistence Setup Complete!"
    echo
    print_status "Next steps:"
    echo "  1. Restart your MCP server"
    echo "  2. Test the connection from your MCP client"
    echo "  3. Run 'session_health_check' tool to verify everything is working"
    echo
    print_status "If you encounter issues:"
    echo "  - Check the documentation: dhafnck_mcp_main/docs/session_persistence_setup.md"
    echo "  - Run: redis-cli ping (should return PONG)"
    echo "  - Check server logs for detailed error information"
    echo
    print_success "Your session connection issues should now be resolved!"
}

# Run main function
main "$@" 