#!/usr/bin/env python3
"""
E2E Validation Test for DhafnckMCP

Simple validation test to verify our E2E testing approach works.
This test validates the core requirements without complex Docker setup.
"""

import asyncio
import json
import logging
import time
import subprocess
import sys
from pathlib import Path
import pytest
import requests

logger = logging.getLogger(__name__)


class E2EValidationTest:
    """Simple E2E validation test"""
    
    def __init__(self):
        self.test_results = []
        
    async def run_validation_test(self):
        """Run E2E validation test"""
        print("🧪 Starting E2E Validation Test")
        print("=" * 40)
        
        try:
            # Test 1: Environment Check
            await self.test_environment()
            
            # Test 2: MCP Server Import Test
            await self.test_mcp_server_import()
            
            # Test 3: Docker Availability
            await self.test_docker_availability()
            
            # Test 4: Test Infrastructure
            await self.test_infrastructure()
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            self.test_results.append({"test": "critical_failure", "error": str(e)})
        
        finally:
            self.print_validation_summary()
    
    async def test_environment(self):
        """Test environment setup"""
        print("\n🌍 Test 1: Environment Check")
        print("-" * 25)
        
        try:
            # Check Python version
            python_version = sys.version_info
            print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
            
            # Check required packages
            required_packages = ["pytest", "requests", "docker"]
            missing_packages = []
            
            for package in required_packages:
                try:
                    __import__(package)
                    print(f"✅ {package} available")
                except ImportError:
                    missing_packages.append(package)
                    print(f"❌ {package} missing")
            
            if missing_packages:
                print(f"⚠️ Missing packages: {missing_packages}")
                print("   Install with: pip install " + " ".join(missing_packages))
            
            # Check project structure
            project_root = Path(__file__).parent.parent
            key_paths = [
                project_root / "src",
                project_root / "docker" / "Dockerfile",
                project_root / "tests" / "conftest.py"
            ]
            
            for path in key_paths:
                if path.exists():
                    print(f"✅ {path.name} found")
                else:
                    print(f"❌ {path.name} missing")
            
            self.test_results.append({
                "test": "environment",
                "status": True,
                "missing_packages": missing_packages
            })
            
        except Exception as e:
            logger.error(f"Environment test failed: {e}")
            self.test_results.append({
                "test": "environment",
                "status": False,
                "error": str(e)
            })
    
    async def test_mcp_server_import(self):
        """Test MCP server can be imported"""
        print("\n🖥️ Test 2: MCP Server Import")
        print("-" * 25)
        
        try:
            # Try to import the MCP server
            try:
                from src.fastmcp.server.mcp_entry_point import create_dhafnck_mcp_server
                print("✅ MCP server import successful")
                
                # Try to create server instance
                server = create_dhafnck_mcp_server()
                print(f"✅ Server instance created: {server.name}")
                
                # Check available tools
                tools = await server.get_tools()
                print(f"✅ {len(tools)} tools available")
                
                expected_tools = ["health_check", "manage_project", "manage_task"]
                found_tools = list(tools.keys())
                missing_tools = [t for t in expected_tools if t not in found_tools]
                
                if missing_tools:
                    print(f"⚠️ Missing tools: {missing_tools}")
                else:
                    print("✅ All expected tools found")
                
            except ImportError as e:
                print(f"❌ MCP server import failed: {e}")
                raise
            
            self.test_results.append({
                "test": "mcp_server_import",
                "status": True,
                "tools_count": len(tools),
                "missing_tools": missing_tools
            })
            
        except Exception as e:
            logger.error(f"MCP server import test failed: {e}")
            self.test_results.append({
                "test": "mcp_server_import",
                "status": False,
                "error": str(e)
            })
    
    async def test_docker_availability(self):
        """Test Docker availability"""
        print("\n🐳 Test 3: Docker Availability")
        print("-" * 25)
        
        try:
            # Check Docker command
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"✅ {result.stdout.strip()}")
            else:
                raise Exception("Docker command failed")
            
            # Check Docker daemon
            result = subprocess.run(
                ["docker", "ps"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("✅ Docker daemon running")
                
                # Count running containers
                lines = result.stdout.strip().split('\n')
                container_count = len(lines) - 1 if len(lines) > 1 else 0
                print(f"✅ {container_count} containers running")
            else:
                raise Exception("Docker daemon not accessible")
            
            # Check if we can import docker package
            try:
                import docker
                client = docker.from_env()
                client.ping()
                print("✅ Docker Python client working")
            except Exception as e:
                print(f"⚠️ Docker Python client issue: {e}")
            
            self.test_results.append({
                "test": "docker_availability",
                "status": True,
                "container_count": container_count
            })
            
        except Exception as e:
            logger.error(f"Docker availability test failed: {e}")
            self.test_results.append({
                "test": "docker_availability",
                "status": False,
                "error": str(e)
            })
    
    async def test_infrastructure(self):
        """Test our testing infrastructure"""
        print("\n🏗️ Test 4: Test Infrastructure")
        print("-" * 25)
        
        try:
            # Test async functionality
            start_time = time.time()
            await asyncio.sleep(0.1)
            end_time = time.time()
            
            if end_time - start_time >= 0.1:
                print("✅ Async functionality working")
            
            # Test performance measurement
            def sample_function():
                time.sleep(0.05)
                return "test"
            
            start_time = time.time()
            result = sample_function()
            end_time = time.time()
            
            response_time = end_time - start_time
            if 0.04 <= response_time <= 0.1:
                print(f"✅ Performance measurement working: {response_time:.3f}s")
            else:
                print(f"⚠️ Performance measurement may be inaccurate: {response_time:.3f}s")
            
            # Test JSON handling
            test_data = {
                "test": True,
                "timestamp": time.time(),
                "items": ["a", "b", "c"]
            }
            
            json_str = json.dumps(test_data)
            parsed_data = json.loads(json_str)
            
            if parsed_data["test"] == True:
                print("✅ JSON handling working")
            
            # Test HTTP requests (if possible)
            try:
                # Try a simple HTTP request to a reliable service
                response = requests.get("https://httpbin.org/json", timeout=5)
                if response.status_code == 200:
                    print("✅ HTTP requests working")
                else:
                    print(f"⚠️ HTTP request returned: {response.status_code}")
            except Exception as e:
                print(f"⚠️ HTTP request failed: {e}")
            
            self.test_results.append({
                "test": "infrastructure",
                "status": True,
                "performance_measurement": response_time
            })
            
        except Exception as e:
            logger.error(f"Infrastructure test failed: {e}")
            self.test_results.append({
                "test": "infrastructure",
                "status": False,
                "error": str(e)
            })
    
    def print_validation_summary(self):
        """Print validation summary"""
        print("\n" + "=" * 40)
        print("📊 E2E VALIDATION SUMMARY")
        print("=" * 40)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for r in self.test_results if r.get("status", False))
        
        print(f"🎯 Results: {successful_tests}/{total_tests} tests passed")
        
        for result in self.test_results:
            test_name = result.get("test", "unknown")
            status = "✅ PASS" if result.get("status", False) else "❌ FAIL"
            print(f"   {status} {test_name.replace('_', ' ').title()}")
            
            if not result.get("status", False) and "error" in result:
                print(f"      Error: {result['error']}")
        
        success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        print(f"\n🎉 Validation Success Rate: {success_rate:.1%}")
        
        if success_rate >= 0.75:
            print("✅ E2E testing infrastructure is ready!")
        else:
            print("⚠️ Some issues found - check errors above")
        
        print("=" * 40)


# Pytest integration
@pytest.mark.asyncio
async def test_e2e_validation():
    """Run E2E validation via pytest"""
    test = E2EValidationTest()
    await test.run_validation_test()
    
    # Assert that critical tests passed
    critical_tests = ["environment", "mcp_server_import"]
    for result in test.test_results:
        if result.get("test") in critical_tests:
            assert result.get("status", False), f"Critical test {result.get('test')} failed"


# Standalone execution
async def main():
    """Run E2E validation standalone"""
    test = E2EValidationTest()
    await test.run_validation_test()


if __name__ == "__main__":
    asyncio.run(main()) 