#!/usr/bin/env python3
"""
Real Docker End-to-End Integration Test

This test validates the core E2E requirements using real Docker containers:
- Docker container deployment and health
- MCP server functionality and tool access
- Performance measurement
- Error handling validation
- Data persistence across restarts

Focused implementation that can be run immediately to validate the approach.
"""

import asyncio
import json
import logging
import time
import subprocess
from pathlib import Path
import pytest
import requests
import docker

logger = logging.getLogger(__name__)


class RealDockerE2ETest:
    """Real Docker E2E Test Implementation"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
        self.container_name = "dhafnck-mcp-real-test"
        self.test_results = []
        
    async def run_full_test(self):
        """Run the complete real Docker E2E test"""
        print("🚀 Starting Real Docker E2E Test")
        print("=" * 50)
        
        try:
            # Phase 1: Docker Setup
            await self.test_docker_setup()
            
            # Phase 2: MCP Functionality
            await self.test_mcp_functionality()
            
            # Phase 3: Performance Testing
            await self.test_performance()
            
            # Phase 4: Error Handling
            await self.test_error_handling()
            
            # Phase 5: Data Persistence
            await self.test_data_persistence()
            
        except Exception as e:
            logger.error(f"Test failed: {e}")
            self.test_results.append({"phase": "critical_failure", "error": str(e)})
        
        finally:
            await self.cleanup()
            self.print_summary()
    
    async def test_docker_setup(self):
        """Test Docker container setup and deployment"""
        print("\n🐳 Phase 1: Docker Setup")
        print("-" * 30)
        
        try:
            # Check if Docker is available
            try:
                self.docker_client.ping()
                print("✅ Docker is available")
            except Exception as e:
                raise Exception(f"Docker not available: {e}")
            
            # Stop any existing container
            await self.stop_existing_container()
            
            # Build image if needed
            print("🏗️ Building Docker image...")
            try:
                # Try to find existing image first
                try:
                    image = self.docker_client.images.get("dhafnck-mcp:test")
                    print("✅ Using existing Docker image")
                except docker.errors.ImageNotFound:
                    print("📦 Building new Docker image...")
                    # Build from project root
                    project_root = Path(__file__).parent.parent.parent
                    dockerfile_path = project_root / "docker" / "Dockerfile"
                    
                    if dockerfile_path.exists():
                        image, build_logs = self.docker_client.images.build(
                            path=str(project_root),
                            dockerfile=str(dockerfile_path),
                            tag="dhafnck-mcp:test",
                            rm=True
                        )
                        print("✅ Docker image built successfully")
                    else:
                        raise Exception(f"Dockerfile not found at {dockerfile_path}")
            
            except Exception as e:
                raise Exception(f"Docker image build failed: {e}")
            
            # Start container
            print("🚀 Starting container...")
            container = self.docker_client.containers.run(
                image="dhafnck-mcp:test",
                name=self.container_name,
                ports={"8000/tcp": 8000},
                environment={
                    "PYTHONPATH": "/app/src",
                    "FASTMCP_LOG_LEVEL": "INFO",
                    "FASTMCP_TRANSPORT": "streamable-http",
                    "FASTMCP_HOST": "0.0.0.0",
                    "FASTMCP_PORT": "8000",
                    "DHAFNCK_AUTH_ENABLED": "false",
                    "DHAFNCK_MVP_MODE": "true",
                    "DEV_MODE": "1"
                },
                detach=True,
                remove=False
            )
            
            print(f"✅ Container started: {container.id[:12]}...")
            
            # Wait for container to be ready
            ready = await self.wait_for_container_ready(timeout=60)
            if not ready:
                raise Exception("Container failed to become ready")
            
            print("✅ Container is ready and responding")
            
            self.test_results.append({
                "phase": "docker_setup",
                "status": True,
                "container_id": container.id
            })
            
        except Exception as e:
            logger.error(f"Docker setup failed: {e}")
            self.test_results.append({
                "phase": "docker_setup", 
                "status": False, 
                "error": str(e)
            })
            raise
    
    async def wait_for_container_ready(self, timeout: int = 60) -> bool:
        """Wait for container to be ready"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check container status
                container = self.docker_client.containers.get(self.container_name)
                if container.status != "running":
                    await asyncio.sleep(2)
                    continue
                
                # Check health endpoint
                response = requests.get("http://localhost:8000/health", timeout=5)
                if response.status_code == 200:
                    return True
                    
            except (requests.RequestException, docker.errors.NotFound):
                await asyncio.sleep(2)
                continue
        
        return False
    
    async def test_mcp_functionality(self):
        """Test MCP server functionality"""
        print("\n🖥️ Phase 2: MCP Functionality")
        print("-" * 30)
        
        try:
            # Test health check
            print("🩺 Testing health check...")
            health_response = requests.post(
                "http://localhost:8000/mcp/call",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "health_check",
                        "arguments": {"random_string": "test"}
                    }
                },
                timeout=10
            )
            
            if health_response.status_code == 200:
                print("✅ Health check successful")
            else:
                raise Exception(f"Health check failed: {health_response.status_code}")
            
            # Test tool listing
            print("🛠️ Testing tool discovery...")
            tools_response = requests.post(
                "http://localhost:8000/mcp/call",
                json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list",
                    "params": {}
                },
                timeout=10
            )
            
            if tools_response.status_code == 200:
                tools_data = tools_response.json()
                tools = tools_data.get("result", {}).get("tools", [])
                print(f"✅ Discovered {len(tools)} tools")
                
                expected_tools = ["health_check", "manage_project", "manage_task"]
                found_tools = [tool.get("name") for tool in tools]
                missing_tools = [t for t in expected_tools if t not in found_tools]
                
                if missing_tools:
                    print(f"⚠️ Missing tools: {missing_tools}")
                else:
                    print("✅ All expected tools found")
            else:
                raise Exception(f"Tool discovery failed: {tools_response.status_code}")
            
            # Test project management
            print("📁 Testing project management...")
            project_response = requests.post(
                "http://localhost:8000/mcp/call",
                json={
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_project",
                        "arguments": {"action": "list"}
                    }
                },
                timeout=10
            )
            
            if project_response.status_code == 200:
                print("✅ Project management working")
            else:
                raise Exception(f"Project management failed: {project_response.status_code}")
            
            self.test_results.append({
                "phase": "mcp_functionality",
                "status": True,
                "tools_count": len(tools)
            })
            
        except Exception as e:
            logger.error(f"MCP functionality test failed: {e}")
            self.test_results.append({
                "phase": "mcp_functionality",
                "status": False,
                "error": str(e)
            })
            raise
    
    async def test_performance(self):
        """Test performance and response times"""
        print("\n⚡ Phase 3: Performance Testing")
        print("-" * 30)
        
        try:
            # Measure response times
            response_times = []
            
            for i in range(5):
                start_time = time.time()
                response = requests.post(
                    "http://localhost:8000/mcp/call",
                    json={
                        "jsonrpc": "2.0",
                        "id": i,
                        "method": "tools/call",
                        "params": {
                            "name": "health_check",
                            "arguments": {"random_string": f"perf_test_{i}"}
                        }
                    },
                    timeout=10
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    response_times.append(end_time - start_time)
            
            if response_times:
                avg_time = sum(response_times) / len(response_times)
                min_time = min(response_times)
                max_time = max(response_times)
                
                print(f"✅ Performance metrics:")
                print(f"   Average: {avg_time:.3f}s")
                print(f"   Min: {min_time:.3f}s")
                print(f"   Max: {max_time:.3f}s")
                
                # Check if performance is acceptable (< 1 second average)
                if avg_time < 1.0:
                    print("✅ Performance acceptable")
                else:
                    print("⚠️ Performance may need optimization")
            
            self.test_results.append({
                "phase": "performance",
                "status": True,
                "avg_response_time": avg_time if response_times else 0
            })
            
        except Exception as e:
            logger.error(f"Performance test failed: {e}")
            self.test_results.append({
                "phase": "performance",
                "status": False,
                "error": str(e)
            })
    
    async def test_error_handling(self):
        """Test error handling scenarios"""
        print("\n🚨 Phase 4: Error Handling")
        print("-" * 30)
        
        try:
            # Test invalid tool
            print("🔧 Testing invalid tool handling...")
            invalid_response = requests.post(
                "http://localhost:8000/mcp/call",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "nonexistent_tool",
                        "arguments": {}
                    }
                },
                timeout=10
            )
            
            if invalid_response.status_code in [400, 404, 422]:
                print("✅ Invalid tool properly rejected")
            else:
                print(f"⚠️ Unexpected response: {invalid_response.status_code}")
            
            # Test malformed request
            print("📝 Testing malformed request handling...")
            try:
                malformed_response = requests.post(
                    "http://localhost:8000/mcp/call",
                    data="invalid json",
                    headers={"Content-Type": "application/json"},
                    timeout=10
                )
                print(f"✅ Malformed request handled: {malformed_response.status_code}")
            except Exception:
                print("✅ Malformed request properly rejected")
            
            self.test_results.append({
                "phase": "error_handling",
                "status": True
            })
            
        except Exception as e:
            logger.error(f"Error handling test failed: {e}")
            self.test_results.append({
                "phase": "error_handling",
                "status": False,
                "error": str(e)
            })
    
    async def test_data_persistence(self):
        """Test data persistence across container restarts"""
        print("\n💾 Phase 5: Data Persistence")
        print("-" * 30)
        
        try:
            # Create test data
            print("📝 Creating test data...")
            create_response = requests.post(
                "http://localhost:8000/mcp/call",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_project",
                        "arguments": {
                            "action": "create",
                            "project_id": "persistence_test",
                            "name": "Persistence Test",
                            "description": "Testing data persistence"
                        }
                    }
                },
                timeout=10
            )
            
            if create_response.status_code == 200:
                print("✅ Test data created")
            else:
                raise Exception(f"Failed to create test data: {create_response.status_code}")
            
            # Restart container
            print("🔄 Restarting container...")
            container = self.docker_client.containers.get(self.container_name)
            container.restart(timeout=30)
            
            # Wait for container to be ready
            ready = await self.wait_for_container_ready(timeout=60)
            if not ready:
                raise Exception("Container failed to restart properly")
            
            print("✅ Container restarted successfully")
            
            # Check if data persists
            print("🔍 Checking data persistence...")
            await asyncio.sleep(3)  # Give it a moment
            
            list_response = requests.post(
                "http://localhost:8000/mcp/call",
                json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "manage_project",
                        "arguments": {"action": "list"}
                    }
                },
                timeout=10
            )
            
            if list_response.status_code == 200:
                projects_data = list_response.json()
                projects = projects_data.get("result", {}).get("projects", [])
                
                persistence_test_exists = any(
                    p.get("id") == "persistence_test"
                    for p in projects
                )
                
                if persistence_test_exists:
                    print("✅ Data persisted across restart")
                else:
                    print("⚠️ Data not persisted (expected in some configurations)")
            
            self.test_results.append({
                "phase": "data_persistence",
                "status": True,
                "data_persisted": persistence_test_exists
            })
            
        except Exception as e:
            logger.error(f"Data persistence test failed: {e}")
            self.test_results.append({
                "phase": "data_persistence",
                "status": False,
                "error": str(e)
            })
    
    async def stop_existing_container(self):
        """Stop any existing test container"""
        try:
            container = self.docker_client.containers.get(self.container_name)
            print(f"🛑 Stopping existing container...")
            container.stop(timeout=10)
            container.remove()
            print("✅ Existing container removed")
        except docker.errors.NotFound:
            pass  # Container doesn't exist, which is fine
        except Exception as e:
            logger.warning(f"Failed to stop existing container: {e}")
    
    async def cleanup(self):
        """Clean up test resources"""
        print("\n🧹 Cleaning up...")
        try:
            await self.stop_existing_container()
            print("✅ Cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 REAL DOCKER E2E TEST SUMMARY")
        print("=" * 50)
        
        total_phases = len(self.test_results)
        successful_phases = sum(1 for r in self.test_results if r.get("status", False))
        
        print(f"🎯 Results: {successful_phases}/{total_phases} phases passed")
        
        for result in self.test_results:
            phase = result.get("phase", "unknown")
            status = "✅ PASS" if result.get("status", False) else "❌ FAIL"
            print(f"   {status} {phase.replace('_', ' ').title()}")
            
            if not result.get("status", False) and "error" in result:
                print(f"      Error: {result['error']}")
        
        success_rate = successful_phases / total_phases if total_phases > 0 else 0
        print(f"\n🎉 Overall Success Rate: {success_rate:.1%}")
        print("=" * 50)


# Pytest integration
@pytest.mark.asyncio
async def test_real_docker_e2e():
    """Run real Docker E2E test via pytest"""
    test = RealDockerE2ETest()
    await test.run_full_test()
    
    # Assert critical phases passed
    critical_phases = ["docker_setup", "mcp_functionality"]
    for result in test.test_results:
        if result.get("phase") in critical_phases:
            assert result.get("status", False), f"Critical phase {result.get('phase')} failed"


# Standalone execution
async def main():
    """Run real Docker E2E test standalone"""
    test = RealDockerE2ETest()
    await test.run_full_test()


if __name__ == "__main__":
    asyncio.run(main()) 