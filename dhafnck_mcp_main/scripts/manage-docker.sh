#!/bin/bash

# DhafnckMCP Docker Management Script
# Provides easy management of the DhafnckMCP Docker container

set -e

CONTAINER_NAME="dhafnck-mcp-server"
SERVICE_NAME="dhafnck-mcp"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Function to show usage
show_usage() {
    echo "🐳 DhafnckMCP Docker Management"
    echo "================================"
    echo ""
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  start     - Start the container (or create if doesn't exist)"
    echo "  stop      - Stop the running container"
    echo "  restart   - Restart the container"
    echo "  logs      - Show container logs (follow mode)"
    echo "  status    - Show container status"
    echo "  health    - Check server health"
    echo "  shell     - Open shell inside container"
    echo "  remove    - Stop and remove container (preserves volumes)"
    echo "  cleanup   - Remove container and rebuild from scratch"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start     # Start the server"
    echo "  $0 logs      # View live logs"
    echo "  $0 health    # Check if server is healthy"
    echo "  $0 shell     # Debug inside container"
}

# Function to check if container exists
check_container_exists() {
    if docker ps -a --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        return 0
    else
        return 1
    fi
}

# Function to check if container is running
check_container_running() {
    if docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
        return 0
    else
        return 1
    fi
}

# Function to start container
start_container() {
    cd "$PROJECT_DIR"
    
    if check_container_running; then
        echo "✅ Container is already running!"
        echo "🌐 Server URL: http://localhost:8000"
        return 0
    elif check_container_exists; then
        echo "🔄 Starting existing container..."
        docker start ${CONTAINER_NAME}
        echo "✅ Container started!"
    else
        echo "🆕 Creating and starting new container..."
        docker-compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml up -d
        echo "✅ Container created and started!"
    fi
    
    echo "🌐 Server URL: http://localhost:8000"
    echo "🔍 Health Check: http://localhost:8000/health"
}

# Function to stop container
stop_container() {
    if check_container_running; then
        echo "🛑 Stopping container..."
        docker stop ${CONTAINER_NAME}
        echo "✅ Container stopped!"
    else
        echo "ℹ️  Container is not running"
    fi
}

# Function to restart container
restart_container() {
    if check_container_exists; then
        echo "🔄 Restarting container..."
        docker restart ${CONTAINER_NAME}
        echo "✅ Container restarted!"
        echo "🌐 Server URL: http://localhost:8000"
    else
        echo "❌ Container doesn't exist. Use 'start' command to create it."
        exit 1
    fi
}

# Function to show logs
show_logs() {
    if check_container_exists; then
        echo "📋 Showing container logs (Press Ctrl+C to exit)..."
        docker logs -f ${CONTAINER_NAME}
    else
        echo "❌ Container doesn't exist"
        exit 1
    fi
}

# Function to show status
show_status() {
    echo "📊 Container Status:"
    echo "==================="
    
    if check_container_exists; then
        if check_container_running; then
            echo "🟢 Status: RUNNING"
            echo "🌐 Server URL: http://localhost:8000"
            
            # Show container details
            echo ""
            echo "📦 Container Details:"
            docker ps --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
            
            # Show resource usage
            echo ""
            echo "💾 Resource Usage:"
            docker stats ${CONTAINER_NAME} --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}"
        else
            echo "🔴 Status: STOPPED"
            docker ps -a --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}"
        fi
    else
        echo "⚫ Status: NOT CREATED"
        echo "💡 Use 'start' command to create and start the container"
    fi
}

# Function to check health
check_health() {
    if check_container_running; then
        echo "🏥 Checking server health..."
        # Check if port 8000 is responding (MCP server)
        if nc -z localhost 8000 2>/dev/null; then
            echo "✅ Server is healthy!"
            echo "🌐 MCP Server URL: http://localhost:8000/mcp/"
            echo "📋 Server Logs: $0 logs"
            echo "📊 Container Status: $0 status"
            echo ""
            echo "💡 The MCP server is running and ready for connections"
            echo "💡 Use this URL in your MCP client: http://localhost:8000/mcp/"
        else
            echo "❌ Server health check failed - port 8000 not responding"
            echo "💡 Check logs with: $0 logs"
            exit 1
        fi
    else
        echo "❌ Container is not running"
        exit 1
    fi
}

# Function to open shell
open_shell() {
    if check_container_running; then
        echo "🐚 Opening shell in container..."
        docker exec -it ${CONTAINER_NAME} /bin/bash
    else
        echo "❌ Container is not running"
        exit 1
    fi
}

# Function to remove container
remove_container() {
    if check_container_exists; then
        echo "🗑️  Removing container (preserving data volumes)..."
        docker stop ${CONTAINER_NAME} 2>/dev/null || true
        docker rm ${CONTAINER_NAME}
        echo "✅ Container removed! Data volumes preserved."
        echo "💡 Use 'start' command to recreate container"
    else
        echo "ℹ️  Container doesn't exist"
    fi
}

# Function to cleanup everything
cleanup_container() {
    cd "$PROJECT_DIR"
    echo "🧹 Cleaning up container and rebuilding..."
    echo "⚠️  This will remove the container but preserve data volumes"
    
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose -f docker/docker-compose.yml -f docker/docker-compose.local.yml down
        echo "✅ Cleanup complete!"
        echo "💡 Use 'start' command to rebuild and start fresh"
    else
        echo "❌ Cleanup cancelled"
    fi
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
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    health)
        check_health
        ;;
    shell)
        open_shell
        ;;
    remove)
        remove_container
        ;;
    cleanup)
        cleanup_container
        ;;
    help|--help|-h)
        show_usage
        ;;
    "")
        echo "❌ No command specified"
        echo ""
        show_usage
        exit 1
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_usage
        exit 1
        ;;
esac 