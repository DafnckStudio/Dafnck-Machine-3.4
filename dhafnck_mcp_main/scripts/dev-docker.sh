#!/bin/bash
#
# Development Docker Management Script
# Manages Docker containers with live code reloading for development
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DOCKER_DIR="$PROJECT_ROOT/docker"

# Docker compose files
COMPOSE_BASE="$DOCKER_DIR/docker-compose.yml"
COMPOSE_DEV="$DOCKER_DIR/docker-compose.dev.yml"

print_usage() {
    echo "Development Docker Management"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start development container with live reload"
    echo "  stop      Stop development container"
    echo "  restart   Restart development container"
    echo "  logs      Show container logs"
    echo "  shell     Open shell in development container"
    echo "  test      Run tests in development container"
    echo "  status    Show container status"
    echo "  clean     Clean up development containers and volumes"
    echo ""
    echo "Examples:"
    echo "  $0 start      # Start dev container with live reload"
    echo "  $0 logs -f    # Follow logs in real-time"
    echo "  $0 test       # Run test suite in container"
    echo "  $0 shell      # Interactive shell in container"
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}Error: Docker is not installed${NC}"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}Error: Docker Compose is not installed${NC}"
        exit 1
    fi
}

check_files() {
    if [ ! -f "$COMPOSE_BASE" ]; then
        echo -e "${RED}Error: Base docker-compose.yml not found at $COMPOSE_BASE${NC}"
        exit 1
    fi
    
    if [ ! -f "$COMPOSE_DEV" ]; then
        echo -e "${RED}Error: Development docker-compose.dev.yml not found at $COMPOSE_DEV${NC}"
        exit 1
    fi
}

start_dev() {
    echo -e "${BLUE}Starting development container with live reload...${NC}"
    
    cd "$DOCKER_DIR"
    
    # Stop existing container if running
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml down 2>/dev/null || true
    
    # Start in development mode
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d
    
    echo -e "${GREEN}Development container started!${NC}"
    echo -e "${YELLOW}Container: dhafnck-mcp-server${NC}"
    echo -e "${YELLOW}Port: http://localhost:8000${NC}"
    echo -e "${YELLOW}Debug Port: http://localhost:8001${NC}"
    echo ""
    echo "View logs: $0 logs"
    echo "Open shell: $0 shell"
    echo "Run tests: $0 test"
}

stop_dev() {
    echo -e "${BLUE}Stopping development container...${NC}"
    cd "$DOCKER_DIR"
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml down
    echo -e "${GREEN}Development container stopped.${NC}"
}

restart_dev() {
    echo -e "${BLUE}Restarting development container...${NC}"
    stop_dev
    sleep 2
    start_dev
}

show_logs() {
    cd "$DOCKER_DIR"
    # Pass any additional arguments to docker-compose logs
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs "$@"
}

open_shell() {
    echo -e "${BLUE}Opening shell in development container...${NC}"
    docker exec -it dhafnck-mcp-server /bin/bash
}

run_tests() {
    echo -e "${BLUE}Running tests in development container...${NC}"
    
    # Run the simple test that works without complex dependencies
    docker exec dhafnck-mcp-server python3 /app/tests/task_management/interface/test_dual_mode_simple.py
    
    echo ""
    echo -e "${GREEN}Development tests completed!${NC}"
    echo ""
    echo "To run full test suite (requires dependencies):"
    echo "  docker exec dhafnck-mcp-server python3 -m pytest /app/tests/ -v"
}

show_status() {
    echo -e "${BLUE}Container status:${NC}"
    docker ps | grep dhafnck || echo "No dhafnck containers running"
    
    echo ""
    echo -e "${BLUE}Volume status:${NC}"
    docker volume ls | grep dhafnck || echo "No dhafnck volumes found"
    
    echo ""
    echo -e "${BLUE}Health check:${NC}"
    if docker exec dhafnck-mcp-server python3 -c "
import sys
sys.path.insert(0, '/app/src')
try:
    from fastmcp.dual_mode_config import get_runtime_mode, get_rules_directory
    print(f'✅ Server healthy - Mode: {get_runtime_mode()}, Rules: {get_rules_directory()}')
except Exception as e:
    print(f'❌ Server unhealthy: {e}')
    exit(1)
" 2>/dev/null; then
        echo -e "${GREEN}Server is healthy${NC}"
    else
        echo -e "${RED}Server is unhealthy${NC}"
    fi
}

clean_dev() {
    echo -e "${BLUE}Cleaning up development environment...${NC}"
    cd "$DOCKER_DIR"
    
    # Stop and remove containers
    docker-compose -f docker-compose.yml -f docker-compose.dev.yml down -v
    
    # Remove development volumes
    docker volume rm dhafnck_data dhafnck_logs 2>/dev/null || true
    
    # Remove development images (optional)
    read -p "Remove development Docker images? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker rmi dhafnck/mcp-server:latest 2>/dev/null || true
        echo -e "${GREEN}Development images removed.${NC}"
    fi
    
    echo -e "${GREEN}Development environment cleaned up.${NC}"
}

# Main script logic
main() {
    check_docker
    check_files
    
    case "${1:-}" in
        start)
            start_dev
            ;;
        stop)
            stop_dev
            ;;
        restart)
            restart_dev
            ;;
        logs)
            shift  # Remove 'logs' from arguments
            show_logs "$@"
            ;;
        shell)
            open_shell
            ;;
        test)
            run_tests
            ;;
        status)
            show_status
            ;;
        clean)
            clean_dev
            ;;
        help|--help|-h)
            print_usage
            ;;
        "")
            echo -e "${RED}Error: No command specified${NC}"
            echo ""
            print_usage
            exit 1
            ;;
        *)
            echo -e "${RED}Error: Unknown command '$1'${NC}"
            echo ""
            print_usage
            exit 1
            ;;
    esac
}

main "$@"