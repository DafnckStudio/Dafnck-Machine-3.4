#!/bin/bash
set -e

# DhafnckMCP Container Management Script
# Ensures consistent container lifecycle management

CONTAINER_NAME="dhafnck-mcp-server"
IMAGE_NAME="dhafnck/mcp-server:latest"
COMPOSE_FILE="docker-compose.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
log() {
    echo -e "${GREEN}[$(date '+%H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date '+%H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date '+%H:%M:%S')] ERROR:${NC} $1"
}

# Function to check if container exists
container_exists() {
    docker ps -a --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"
}

# Function to check if container is running
container_running() {
    docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"
}

# Function to start the container
start_container() {
    log "🚀 Starting DhafnckMCP container..."
    
    if container_running; then
        log "✅ Container is already running"
        return 0
    fi
    
    if container_exists; then
        log "📦 Starting existing container..."
        docker start "$CONTAINER_NAME"
    else
        log "🏗️  Creating and starting new container with Docker Compose..."
        docker-compose -f "$COMPOSE_FILE" up -d
    fi
    
    # Wait for container to be ready
    log "⏳ Waiting for container to be ready..."
    sleep 3
    
    if container_running; then
        log "✅ Container started successfully"
        show_status
    else
        error "❌ Failed to start container"
        return 1
    fi
}

# Function to stop the container
stop_container() {
    log "🛑 Stopping DhafnckMCP container..."
    
    if container_running; then
        docker-compose -f "$COMPOSE_FILE" stop
        log "✅ Container stopped successfully"
    else
        warn "Container is not running"
    fi
}

# Function to restart the container
restart_container() {
    log "🔄 Restarting DhafnckMCP container..."
    stop_container
    sleep 2
    start_container
}

# Function to show container status
show_status() {
    log "📊 Container Status:"
    
    if container_running; then
        echo -e "${GREEN}✅ Status: RUNNING${NC}"
        
        # Show container details
        docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        
        # Show resource usage
        echo ""
        log "💾 Resource Usage:"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" "$CONTAINER_NAME"
        
    elif container_exists; then
        echo -e "${YELLOW}⏸️  Status: STOPPED${NC}"
        docker ps -a --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}"
    else
        echo -e "${RED}❌ Status: NOT FOUND${NC}"
    fi
}

# Function to view logs
show_logs() {
    if container_exists; then
        log "📋 Showing container logs (last 50 lines):"
        docker logs -f --tail 50 "$CONTAINER_NAME"
    else
        error "Container does not exist"
        return 1
    fi
}

# Function to clean up multiple containers
cleanup_duplicates() {
    log "🧹 Cleaning up duplicate containers..."
    
    # Find all containers with dhafnck in the name
    DUPLICATE_CONTAINERS=$(docker ps -a --filter "name=dhafnck" --format "{{.Names}}" | grep -v "^${CONTAINER_NAME}$" || true)
    
    if [ -n "$DUPLICATE_CONTAINERS" ]; then
        warn "Found duplicate containers:"
        echo "$DUPLICATE_CONTAINERS"
        
        read -p "Do you want to remove these containers? (y/N): " -n 1 -r
        echo
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "$DUPLICATE_CONTAINERS" | xargs -r docker rm -f
            log "✅ Duplicate containers removed"
        else
            log "Cleanup cancelled"
        fi
    else
        log "✅ No duplicate containers found"
    fi
}

# Function to reset everything
reset_container() {
    log "🔄 Resetting DhafnckMCP container..."
    
    warn "This will stop and remove the container, but keep data volumes"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose -f "$COMPOSE_FILE" down
        log "✅ Container reset complete"
        log "💡 Run 'start' to create a fresh container"
    else
        log "Reset cancelled"
    fi
}

# Function to show help
show_help() {
    echo "DhafnckMCP Container Management"
    echo "================================"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start the container (create if needed)"
    echo "  stop        Stop the container"
    echo "  restart     Restart the container"
    echo "  status      Show container status and resource usage"
    echo "  logs        Show container logs (follow mode)"
    echo "  cleanup     Remove duplicate containers"
    echo "  reset       Stop and remove container (keeps data)"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start     # Start the container"
    echo "  $0 status    # Check if running"
    echo "  $0 cleanup   # Remove duplicates"
}

# Main script logic
case "${1:-}" in
    start)
        start_container
        ;;
    stop)
        stop_container
        ;;
    restart)
        restart_container
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    cleanup)
        cleanup_duplicates
        ;;
    reset)
        reset_container
        ;;
    help|--help|-h)
        show_help
        ;;
    "")
        warn "No command specified"
        show_help
        exit 1
        ;;
    *)
        error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac 