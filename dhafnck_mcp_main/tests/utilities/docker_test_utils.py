#!/usr/bin/env python3
"""
Docker Test Utilities for DhafnckMCP E2E Testing

Provides utilities for real Docker container testing including:
- Container lifecycle management
- Health checking and monitoring
- Network connectivity testing
- Data persistence validation
- Performance measurement
"""

import asyncio
import json
import logging
import socket
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import docker
import requests
import psutil

logger = logging.getLogger(__name__)


def parse_sse_response(text: str) -> dict:
    """Parse Server-Sent Events response to extract JSON data"""
    lines = text.strip().split('\n')
    data_line = None
    
    for line in lines:
        if line.startswith('data: '):
            data_line = line[6:]  # Remove 'data: ' prefix
            break
    
    if data_line:
        try:
            return json.loads(data_line)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse SSE data as JSON: {e}")
            logger.error(f"Raw data: {data_line}")
            raise
    else:
        raise ValueError(f"No data line found in SSE response: {text}")


def find_free_port(start_port: int = 8002, max_attempts: int = 100) -> int:
    """Find a free port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No free port found in range {start_port}-{start_port + max_attempts}")


class DockerTestManager:
    """Manages Docker containers for testing purposes"""
    
    def __init__(self, project_root: Path = None):
        # More robust path resolution for project root
        if project_root:
            self.project_root = project_root
        else:
            # Try multiple path resolution strategies
            current_file_path = Path(__file__).resolve()
            
            # Strategy 1: Standard parent.parent.parent from test utilities
            candidate1 = current_file_path.parent.parent.parent
            
            # Strategy 2: Look for pyproject.toml to find project root
            candidate2 = current_file_path
            while candidate2.parent != candidate2:  # Stop at filesystem root
                if (candidate2 / "pyproject.toml").exists():
                    break
                candidate2 = candidate2.parent
            
            # Strategy 3: Use current working directory if it has pyproject.toml
            candidate3 = Path.cwd()
            
            # Choose the best candidate
            for candidate in [candidate1, candidate2, candidate3]:
                if (candidate / "pyproject.toml").exists() and (candidate / "docker" / "Dockerfile").exists():
                    self.project_root = candidate
                    break
            else:
                # Fallback to the original strategy
                self.project_root = candidate1
        self.docker_client = docker.from_env()
        self.test_containers = []
        self.test_networks = []
        self.test_volumes = []
        self.test_port = None  # Will be dynamically assigned
        
    async def build_test_image(self, force_rebuild: bool = False) -> Dict:
        """Build the DhafnckMCP Docker image for testing"""
        try:
            dockerfile_path = self.project_root / "docker" / "Dockerfile"
            
            # Enhanced debugging information
            logger.info(f"🏗️ Building DhafnckMCP test image...")
            logger.info(f"Project root: {self.project_root}")
            logger.info(f"Dockerfile path: {dockerfile_path}")
            logger.info(f"Project root exists: {self.project_root.exists()}")
            logger.info(f"Docker directory exists: {(self.project_root / 'docker').exists()}")
            logger.info(f"Dockerfile exists: {dockerfile_path.exists()}")
            
            if not dockerfile_path.exists():
                # Try to find Dockerfile in alternative locations
                alternative_paths = [
                    self.project_root / "Dockerfile",
                    Path.cwd() / "docker" / "Dockerfile",
                    Path.cwd() / "Dockerfile"
                ]
                
                for alt_path in alternative_paths:
                    logger.info(f"Checking alternative path: {alt_path}")
                    if alt_path.exists():
                        dockerfile_path = alt_path
                        logger.info(f"Found Dockerfile at alternative location: {dockerfile_path}")
                        break
                else:
                    raise FileNotFoundError(
                        f"Dockerfile not found at {dockerfile_path}. "
                        f"Project root: {self.project_root}, "
                        f"Current working directory: {Path.cwd()}, "
                        f"Checked alternatives: {alternative_paths}"
                    )
            
            # Ensure we have the correct build context
            build_context = dockerfile_path.parent.parent if dockerfile_path.name == "Dockerfile" and dockerfile_path.parent.name == "docker" else dockerfile_path.parent
            
            logger.info(f"Using build context: {build_context}")
            logger.info(f"Using dockerfile: {dockerfile_path}")
            
            # Build the image
            image, build_logs = self.docker_client.images.build(
                path=str(build_context),
                dockerfile=str(dockerfile_path),
                tag="dhafnck-mcp:test",
                rm=True,
                forcerm=True,
                nocache=force_rebuild
            )
            
            return {
                "success": True,
                "image_id": image.id,
                "image_tags": image.tags,
                "size": image.attrs.get("Size", 0),
                "project_root": str(self.project_root),
                "dockerfile_path": str(dockerfile_path),
                "build_context": str(build_context)
            }
            
        except Exception as e:
            error_msg = f"Docker image build failed: {e}"
            logger.error(error_msg)
            logger.error(f"Project root: {self.project_root}")
            logger.error(f"Current working directory: {Path.cwd()}")
            return {"success": False, "error": error_msg}
    
    async def start_test_container(self, 
                                 container_name: str = "dhafnck-mcp-test",
                                 ports: Dict[str, int] = None,
                                 environment: Dict[str, str] = None,
                                 volumes: Dict[str, Dict] = None) -> Dict:
        """Start a test container with specified configuration"""
        try:
            # Find a free port if not specified
            if ports is None:
                self.test_port = find_free_port()
                ports = {"8000/tcp": self.test_port}
                logger.info(f"🔍 Using free port {self.test_port} for test container")
            else:
                # Extract the host port from the provided ports config
                self.test_port = list(ports.values())[0]
            
            if environment is None:
                environment = {
                    "PYTHONPATH": "/app/src",
                    "FASTMCP_LOG_LEVEL": "INFO",
                    "FASTMCP_TRANSPORT": "streamable-http",
                    "FASTMCP_HOST": "0.0.0.0",
                    "FASTMCP_PORT": "8000",  # Internal container port stays 8000
                    "DHAFNCK_AUTH_ENABLED": "false",
                    "DHAFNCK_MVP_MODE": "true",
                    "DEV_MODE": "1"
                }
            
            if volumes is None:
                volumes = {}
            
            # Remove existing container if it exists
            await self.stop_test_container(container_name)
            
            logger.info(f"🚀 Starting test container: {container_name} on port {self.test_port}")
            
            container = self.docker_client.containers.run(
                image="dhafnck-mcp:test",
                name=container_name,
                ports=ports,
                environment=environment,
                volumes=volumes,
                detach=True,
                remove=False,
                auto_remove=False
            )
            
            self.test_containers.append(container_name)
            
            # Wait for container to be ready
            ready = await self.wait_for_container_ready(container_name, timeout=60)
            
            if not ready:
                raise Exception("Container failed to become ready within timeout")
            
            return {
                "success": True,
                "container_id": container.id,
                "container_name": container_name,
                "status": container.status,
                "ports": ports,
                "test_port": self.test_port
            }
            
        except Exception as e:
            logger.error(f"Failed to start test container: {e}")
            return {"success": False, "error": str(e)}
    
    async def wait_for_container_ready(self, container_name: str, timeout: int = 60) -> bool:
        """Wait for container to be ready and responding to health checks"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                container = self.docker_client.containers.get(container_name)
                
                # Check if container is running
                if container.status != "running":
                    await asyncio.sleep(2)
                    continue
                
                # Check health endpoint using the dynamic port
                test_port = self.test_port or 8000
                response = requests.get(f"http://localhost:{test_port}/health", timeout=5)
                if response.status_code == 200:
                    logger.info(f"✅ Container {container_name} is ready on port {test_port}")
                    return True
                    
            except (requests.RequestException, docker.errors.NotFound):
                await asyncio.sleep(2)
                continue
        
        logger.error(f"❌ Container {container_name} failed to become ready within {timeout}s")
        return False
    
    async def stop_test_container(self, container_name: str) -> Dict:
        """Stop and remove a test container"""
        try:
            try:
                container = self.docker_client.containers.get(container_name)
                logger.info(f"🛑 Stopping container: {container_name}")
                container.stop(timeout=10)
                container.remove()
                
                if container_name in self.test_containers:
                    self.test_containers.remove(container_name)
                    
                return {"success": True, "message": f"Container {container_name} stopped and removed"}
                
            except docker.errors.NotFound:
                return {"success": True, "message": f"Container {container_name} not found (already removed)"}
                
        except Exception as e:
            logger.error(f"Failed to stop container {container_name}: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_container_health(self, container_name: str) -> Dict:
        """Test container health and connectivity"""
        try:
            container = self.docker_client.containers.get(container_name)
            
            # Get container stats
            stats = container.stats(stream=False)
            
            # Test HTTP connectivity using the dynamic port
            test_port = self.test_port or 8000
            health_response = requests.get(f"http://localhost:{test_port}/health", timeout=10)
            mcp_response = requests.get(f"http://localhost:{test_port}/mcp/", timeout=10)
            
            return {
                "success": True,
                "container_status": container.status,
                "test_port": test_port,
                "health_endpoint": {
                    "status_code": health_response.status_code,
                    "response_time": health_response.elapsed.total_seconds()
                },
                "mcp_endpoint": {
                    "status_code": mcp_response.status_code, 
                    "response_time": mcp_response.elapsed.total_seconds()
                },
                "resource_usage": {
                    "cpu_usage": stats.get("cpu_stats", {}),
                    "memory_usage": stats.get("memory_stats", {})
                }
            }
            
        except Exception as e:
            logger.error(f"Container health check failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_mcp_functionality(self, base_url: str = None) -> Dict:
        """Test MCP server functionality through HTTP endpoints"""
        try:
            # Use dynamic port if base_url not provided
            if base_url is None:
                test_port = self.test_port or 8000
                base_url = f"http://localhost:{test_port}"
            
            results = {}
            
            # Proper headers for FastMCP streamable-http transport
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
            
            # Test session initialization first
            init_response = requests.post(
                f"{base_url}/mcp/initialize",
                headers=headers,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "test-client",
                            "version": "1.0.0"
                        }
                    }
                },
                timeout=10
            )
            results["session_init"] = {
                "status_code": init_response.status_code,
                "response_time": init_response.elapsed.total_seconds(),
                "success": init_response.status_code == 200
            }
            
            # If session initialization failed, return early
            if not results["session_init"]["success"]:
                return {
                    "success": False,
                    "error": f"Session initialization failed: {init_response.status_code}",
                    "test_results": results,
                    "overall_success": False
                }
            
            # Extract session ID from response headers
            session_id = init_response.headers.get("mcp-session-id")
            if not session_id:
                return {
                    "success": False,
                    "error": "No session ID returned from initialization",
                    "test_results": results,
                    "overall_success": False
                }
            
            # Add session ID to headers for subsequent requests
            headers_with_session = headers.copy()
            headers_with_session["mcp-session-id"] = session_id
            
            # Give the server a moment to complete initialization
            await asyncio.sleep(0.1)
            
            # Test health check
            health_response = requests.post(
                f"{base_url}/mcp/call",
                headers=headers_with_session,
                json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "health_check",
                        "arguments": {"random_string": "test"}
                    }
                },
                timeout=10
            )
            results["health_check"] = {
                "status_code": health_response.status_code,
                "response_time": health_response.elapsed.total_seconds(),
                "success": health_response.status_code == 200
            }
            
            # Test project management
            project_response = requests.post(
                f"{base_url}/mcp/call",
                headers=headers_with_session,
                json={
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_project",
                        "arguments": {
                            "action": "list"
                        }
                    }
                },
                timeout=10
            )
            results["manage_project"] = {
                "status_code": project_response.status_code,
                "response_time": project_response.elapsed.total_seconds(),
                "success": project_response.status_code == 200
            }
            
            # Test task management
            task_response = requests.post(
                f"{base_url}/mcp/call",
                headers=headers_with_session,
                json={
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_task",
                        "arguments": {
                            "action": "list",
                            "project_id": "test_project"
                        }
                    }
                },
                timeout=10
            )
            results["manage_task"] = {
                "status_code": task_response.status_code,
                "response_time": task_response.elapsed.total_seconds(),
                "success": task_response.status_code == 200
            }
            
            return {
                "success": True,
                "test_results": results,
                "overall_success": all(r["success"] for r in results.values()),
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"MCP functionality test failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_container_persistence(self, container_name: str) -> Dict:
        """Test data persistence across container restarts"""
        try:
            # Use dynamic port
            test_port = self.test_port or 8000
            base_url = f"http://localhost:{test_port}"
            
            # Proper headers for FastMCP streamable-http transport
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream"
            }
            
            # Initialize session first
            init_response = requests.post(
                f"{base_url}/mcp/initialize",
                headers=headers,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "persistence-test-client",
                            "version": "1.0.0"
                        }
                    }
                },
                timeout=10
            )
            
            if init_response.status_code != 200:
                raise Exception("Failed to initialize MCP session")
            
            # Create test data
            create_response = requests.post(
                f"{base_url}/mcp/call",
                headers=headers,
                json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_project",
                        "arguments": {
                            "action": "create",
                            "project_id": "persistence_test",
                            "name": "Persistence Test Project",
                            "description": "Testing data persistence"
                        }
                    }
                },
                timeout=10
            )
            
            if create_response.status_code != 200:
                raise Exception("Failed to create test project")
            
            # Restart container
            restart_result = await self.restart_test_container(container_name)
            if not restart_result["success"]:
                raise Exception("Failed to restart container")
            
            # Re-initialize session after restart
            init_response2 = requests.post(
                f"{base_url}/mcp/initialize",
                headers=headers,
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {},
                        "clientInfo": {
                            "name": "persistence-test-client",
                            "version": "1.0.0"
                        }
                    }
                },
                timeout=10
            )
            
            if init_response2.status_code != 200:
                raise Exception("Failed to re-initialize MCP session after restart")
            
            # Check if data persists
            list_response = requests.post(
                f"{base_url}/mcp/call",
                headers=headers,
                json={
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_project",
                        "arguments": {
                            "action": "list"
                        }
                    }
                },
                timeout=10
            )
            
            if list_response.status_code == 200:
                # Parse response (handle both JSON and SSE formats)
                try:
                    projects_data = list_response.json()
                except json.JSONDecodeError:
                    projects_data = parse_sse_response(list_response.text)
                
                persistence_test_exists = any(
                    p.get("id") == "persistence_test" 
                    for p in projects_data.get("projects", [])
                )
            else:
                persistence_test_exists = False
            
            return {
                "success": True,
                "data_persisted": persistence_test_exists,
                "restart_successful": restart_result["success"]
            }
            
        except Exception as e:
            logger.error(f"Persistence test failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def restart_test_container(self, container_name: str) -> Dict:
        """Restart a test container"""
        try:
            container = self.docker_client.containers.get(container_name)
            logger.info(f"🔄 Restarting container: {container_name}")
            
            container.restart(timeout=30)
            
            # Wait for container to be ready again
            ready = await self.wait_for_container_ready(container_name, timeout=60)
            
            return {
                "success": ready,
                "message": f"Container {container_name} restarted successfully" if ready else "Container restart failed"
            }
            
        except Exception as e:
            logger.error(f"Failed to restart container: {e}")
            return {"success": False, "error": str(e)}
    
    async def cleanup_all_test_resources(self):
        """Clean up all test containers, networks, and volumes"""
        logger.info("🧹 Cleaning up test resources...")
        
        # Stop and remove test containers
        for container_name in self.test_containers.copy():
            await self.stop_test_container(container_name)
        
        # Remove test networks
        for network_name in self.test_networks:
            try:
                network = self.docker_client.networks.get(network_name)
                network.remove()
                logger.info(f"Removed test network: {network_name}")
            except docker.errors.NotFound:
                pass
            except Exception as e:
                logger.error(f"Failed to remove network {network_name}: {e}")
        
        # Remove test volumes
        for volume_name in self.test_volumes:
            try:
                volume = self.docker_client.volumes.get(volume_name)
                volume.remove()
                logger.info(f"Removed test volume: {volume_name}")
            except docker.errors.NotFound:
                pass
            except Exception as e:
                logger.error(f"Failed to remove volume {volume_name}: {e}")
        
        self.test_containers.clear()
        self.test_networks.clear()
        self.test_volumes.clear()


class PerformanceMonitor:
    """Monitor performance metrics during testing"""
    
    def __init__(self):
        self.metrics = []
    
    async def measure_response_time(self, func, *args, **kwargs) -> Tuple[any, float]:
        """Measure execution time of a function"""
        start_time = time.time()
        result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
        end_time = time.time()
        
        response_time = end_time - start_time
        self.metrics.append({
            "function": func.__name__,
            "response_time": response_time,
            "timestamp": start_time
        })
        
        return result, response_time
    
    def get_performance_summary(self) -> Dict:
        """Get summary of performance metrics"""
        if not self.metrics:
            return {"message": "No metrics collected"}
        
        response_times = [m["response_time"] for m in self.metrics]
        
        return {
            "total_requests": len(self.metrics),
            "avg_response_time": sum(response_times) / len(response_times),
            "min_response_time": min(response_times),
            "max_response_time": max(response_times),
            "metrics": self.metrics
        } 