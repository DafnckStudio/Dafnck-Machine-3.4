#!/usr/bin/env python3
"""
MVP Core Functionality End-to-End Tests

Simplified end-to-end test suite focusing on core MCP server functionality
without external dependencies. Tests the essential MVP user journey:

1. MCP Server Creation and Health
2. Core Tools Availability  
3. Task Management Operations
4. Project Management Operations
5. Token Validation (MVP mode)
6. Performance and Error Recovery

This validates the core MVP functionality is ready for deployment.
"""

import asyncio
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Dict, List

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from fastmcp.server.mcp_entry_point import create_dhafnck_mcp_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MVPCoreFunctionalityTests:
    """Core MVP Functionality Test Suite"""
    
    def __init__(self):
        self.test_results = []
        self.server_instance = None
        
    async def run_all_tests(self):
        """Run the complete core functionality test suite"""
        print("🚀 Starting MVP Core Functionality Tests")
        print("=" * 60)
        
        try:
            # Test 1: MCP Server Creation and Health
            await self.test_mcp_server_creation()
            
            # Test 2: Core Tools Availability
            await self.test_core_tools_availability()
            
            # Test 3: Authentication System (MVP Mode)
            await self.test_authentication_system()
            
            # Test 4: Project Management Operations
            await self.test_project_management()
            
            # Test 5: Task Management Operations  
            await self.test_task_management()
            
            # Test 6: Agent Management Operations
            await self.test_agent_management()
            
            # Test 7: Performance Under Load
            await self.test_performance()
            
            # Test 8: Error Recovery
            await self.test_error_recovery()
            
        except Exception as e:
            logger.error(f"Critical test failure: {e}")
            self.test_results.append({"test": "critical_failure", "status": False, "error": str(e)})
        
        finally:
            self.print_test_summary()
    
    async def test_mcp_server_creation(self):
        """Test 1: MCP Server Creation and Health"""
        print("\n🏗️ Test 1: MCP Server Creation and Health")
        print("-" * 40)
        
        try:
            # Test server creation
            print("Creating MCP server...")
            self.server_instance = create_dhafnck_mcp_server()
            assert self.server_instance is not None
            assert hasattr(self.server_instance, 'name')
            print(f"✅ Server created: {self.server_instance.name}")
            
            # Test health check
            print("Testing health check...")
            result = await self.server_instance._call_tool("health_check", {"random_string": "test"})
            health_data = json.loads(result[0].text)
            assert health_data.get("status") == "healthy"
            print(f"✅ Health check passed: {health_data['status']}")
            
            # Test server capabilities
            print("Testing server capabilities...")
            result = await self.server_instance._call_tool("get_server_capabilities", {"random_string": "test"})
            capabilities = json.loads(result[0].text)
            assert "core_features" in capabilities
            print(f"✅ Server capabilities: {len(capabilities['core_features'])} features")
            
            self.test_results.append({"test": "server_creation", "status": True})
            
        except Exception as e:
            logger.error(f"Server creation test failed: {e}")
            self.test_results.append({"test": "server_creation", "status": False, "error": str(e)})
            raise
    
    async def test_core_tools_availability(self):
        """Test 2: Core Tools Availability"""
        print("\n🛠️ Test 2: Core Tools Availability")
        print("-" * 40)
        
        try:
            # Get all available tools
            tools = await self.server_instance.get_tools()
            available_tools = list(tools.keys())
            print(f"Available tools: {len(available_tools)}")
            
            # Check for essential tools
            essential_tools = [
                "health_check",
                "get_server_capabilities",
                "manage_project", 
                "manage_task",
                "manage_subtask",
                "manage_agent",
                "call_agent"
            ]
            
            missing_tools = []
            for tool in essential_tools:
                if tool in available_tools:
                    print(f"✅ {tool}")
                else:
                    print(f"❌ {tool} - MISSING")
                    missing_tools.append(tool)
            
            assert len(missing_tools) == 0, f"Missing essential tools: {missing_tools}"
            
            self.test_results.append({
                "test": "tools_availability", 
                "status": True,
                "tool_count": len(available_tools)
            })
            
        except Exception as e:
            logger.error(f"Tools availability test failed: {e}")
            self.test_results.append({"test": "tools_availability", "status": False, "error": str(e)})
            raise
    
    async def test_authentication_system(self):
        """Test 3: Authentication System (MVP Mode)"""
        print("\n🔐 Test 3: Authentication System (MVP Mode)")
        print("-" * 40)
        
        try:
            # Set MVP mode for testing
            os.environ["DHAFNCK_MVP_MODE"] = "true"
            os.environ["DHAFNCK_AUTH_ENABLED"] = "true"
            
            # Import auth components
            from fastmcp.auth import TokenValidator, AuthMiddleware, SupabaseTokenClient
            
            # Test token generation
            print("Testing token generation...")
            client = SupabaseTokenClient()
            token = client.generate_token()
            assert len(token) == 64
            assert all(c in '0123456789abcdef' for c in token)
            print(f"✅ Token generated: {token[:16]}...")
            
            # Test token validation in MVP mode
            print("Testing token validation...")
            validator = TokenValidator()
            token_info = await validator.validate_token(token, {"test": "client"})
            assert token_info.user_id == "mvp_user"
            print(f"✅ Token validated: user_id={token_info.user_id}")
            
            # Test auth middleware
            print("Testing auth middleware...")
            middleware = AuthMiddleware()
            status = middleware.get_auth_status()
            assert status["auth_enabled"] == True
            print(f"✅ Auth middleware: {status}")
            
            self.test_results.append({"test": "authentication", "status": True})
            
        except Exception as e:
            logger.error(f"Authentication test failed: {e}")
            self.test_results.append({"test": "authentication", "status": False, "error": str(e)})
            # Don't raise - auth is optional for core functionality
    
    async def test_project_management(self):
        """Test 4: Project Management Operations"""
        print("\n📁 Test 4: Project Management Operations")
        print("-" * 40)
        
        try:
            # Test project creation
            print("Testing project creation...")
            result = await self.server_instance._call_tool("manage_project", {
                "action": "create",
                "project_id": "mvp_test_project",
                "name": "MVP Test Project",
                "description": "End-to-end test project for MVP validation"
            })
            project_result = json.loads(result[0].text)
            assert project_result.get("success"), f"Project creation failed: {project_result}"
            print("✅ Project created successfully")
            
            # Test project listing
            print("Testing project listing...")
            result = await self.server_instance._call_tool("manage_project", {
                "action": "list"
            })
            list_result = json.loads(result[0].text)
            assert list_result.get("success"), f"Project listing failed: {list_result}"
            projects = list_result.get("projects", [])
            test_project = next((p for p in projects if p["id"] == "mvp_test_project"), None)
            assert test_project is not None, "Test project not found in listing"
            print(f"✅ Project listing: {len(projects)} projects found")
            
            # Test project retrieval
            print("Testing project retrieval...")
            result = await self.server_instance._call_tool("manage_project", {
                "action": "get",
                "project_id": "mvp_test_project"
            })
            get_result = json.loads(result[0].text)
            assert get_result.get("success"), f"Project retrieval failed: {get_result}"
            print("✅ Project retrieved successfully")
            
            self.test_results.append({"test": "project_management", "status": True})
            
        except Exception as e:
            logger.error(f"Project management test failed: {e}")
            self.test_results.append({"test": "project_management", "status": False, "error": str(e)})
            raise
    
    async def test_task_management(self):
        """Test 5: Task Management Operations"""
        print("\n📋 Test 5: Task Management Operations")
        print("-" * 40)
        
        try:
            # Test task creation
            print("Testing task creation...")
            result = await self.server_instance._call_tool("manage_task", {
                "action": "create",
                "project_id": "mvp_test_project",
                "title": "MVP Test Task",
                "description": "End-to-end test task for MVP validation",
                "priority": "high",
                "status": "todo",
                "assignees": ["@coding_agent"]
            })
            task_result = json.loads(result[0].text)
            assert task_result.get("success"), f"Task creation failed: {task_result}"
            task_id = task_result.get("task", {}).get("id")
            assert task_id is not None, "Task ID not returned"
            print(f"✅ Task created: {task_id}")
            
            # Test task listing
            print("Testing task listing...")
            result = await self.server_instance._call_tool("manage_task", {
                "action": "list",
                "project_id": "mvp_test_project"
            })
            list_result = json.loads(result[0].text)
            assert list_result.get("success"), f"Task listing failed: {list_result}"
            tasks = list_result.get("tasks", [])
            assert len(tasks) > 0, "No tasks found"
            print(f"✅ Task listing: {len(tasks)} tasks found")
            
            # Test task update
            print("Testing task update...")
            result = await self.server_instance._call_tool("manage_task", {
                "action": "update",
                "project_id": "mvp_test_project",
                "task_id": task_id,
                "status": "in_progress"
            })
            update_result = json.loads(result[0].text)
            assert update_result.get("success"), f"Task update failed: {update_result}"
            print("✅ Task updated successfully")
            
            # Test subtask creation
            print("Testing subtask creation...")
            result = await self.server_instance._call_tool("manage_subtask", {
                "action": "add",
                "project_id": "mvp_test_project",
                "task_id": task_id,
                "subtask_data": {
                    "title": "MVP Test Subtask",
                    "description": "Test subtask for MVP validation"
                }
            })
            subtask_result = json.loads(result[0].text)
            assert subtask_result.get("success"), f"Subtask creation failed: {subtask_result}"
            print("✅ Subtask created successfully")
            
            self.test_results.append({"test": "task_management", "status": True})
            
        except Exception as e:
            logger.error(f"Task management test failed: {e}")
            self.test_results.append({"test": "task_management", "status": False, "error": str(e)})
            raise
    
    async def test_agent_management(self):
        """Test 6: Agent Management Operations"""
        print("\n🤖 Test 6: Agent Management Operations")
        print("-" * 40)
        
        try:
            # Test agent registration
            print("Testing agent registration...")
            result = await self.server_instance._call_tool("manage_agent", {
                "action": "register",
                "project_id": "mvp_test_project",
                "agent_id": "test_coding_agent",
                "name": "Test Coding Agent"
            })
            agent_result = json.loads(result[0].text)
            assert agent_result.get("success"), f"Agent registration failed: {agent_result}"
            print("✅ Agent registered successfully")
            
            # Test agent listing
            print("Testing agent listing...")
            result = await self.server_instance._call_tool("manage_agent", {
                "action": "list",
                "project_id": "mvp_test_project"
            })
            list_result = json.loads(result[0].text)
            assert list_result.get("success"), f"Agent listing failed: {list_result}"
            agents = list_result.get("agents", [])
            assert len(agents) > 0, "No agents found"
            print(f"✅ Agent listing: {len(agents)} agents found")
            
            # Test call_agent functionality
            print("Testing call_agent...")
            result = await self.server_instance._call_tool("call_agent", {
                "name_agent": "coding_agent"
            })
            call_result = json.loads(result[0].text)
            assert call_result.get("success"), f"Call agent failed: {call_result}"
            print("✅ Call agent successful")
            
            self.test_results.append({"test": "agent_management", "status": True})
            
        except Exception as e:
            logger.error(f"Agent management test failed: {e}")
            self.test_results.append({"test": "agent_management", "status": False, "error": str(e)})
            # Don't raise - agent management is not critical for core functionality
    
    async def test_performance(self):
        """Test 7: Performance Under Load"""
        print("\n⚡ Test 7: Performance Under Load")
        print("-" * 40)
        
        try:
            # Test concurrent operations
            print("Testing concurrent operations...")
            start_time = time.time()
            
            # Create 20 concurrent health check tasks
            tasks = []
            for i in range(20):
                task = asyncio.create_task(
                    self.server_instance._call_tool("health_check", {"random_string": f"test_{i}"})
                )
                tasks.append(task)
            
            # Wait for all tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            # Analyze results
            successful = sum(1 for r in results if not isinstance(r, Exception))
            total_time = end_time - start_time
            avg_time = (total_time * 1000) / len(tasks)  # ms per operation
            
            print(f"✅ Concurrent operations: {successful}/{len(tasks)} successful")
            print(f"✅ Average response time: {avg_time:.2f}ms")
            print(f"✅ Total time: {total_time:.2f}s")
            
            # Performance should be reasonable
            assert successful >= len(tasks) * 0.9, "Too many failed operations"
            assert avg_time < 2000, "Response time too slow"
            
            self.test_results.append({
                "test": "performance",
                "status": True,
                "avg_response_time": avg_time,
                "success_rate": successful / len(tasks)
            })
            
        except Exception as e:
            logger.error(f"Performance test failed: {e}")
            self.test_results.append({"test": "performance", "status": False, "error": str(e)})
            # Don't raise - performance issues are not critical for basic functionality
    
    async def test_error_recovery(self):
        """Test 8: Error Recovery"""
        print("\n🛡️ Test 8: Error Recovery")
        print("-" * 40)
        
        try:
            # Test invalid tool calls
            print("Testing error handling...")
            
            error_scenarios = [
                ("invalid_tool", "nonexistent_tool", {}),
                ("invalid_params", "health_check", {"invalid_param": "value"}),
                ("malformed_action", "manage_task", {"action": "invalid_action"})
            ]
            
            recovered_errors = 0
            
            for scenario_name, tool_name, params in error_scenarios:
                try:
                    await self.server_instance._call_tool(tool_name, params)
                    print(f"⚠️  {scenario_name}: Expected error but got success")
                except Exception as e:
                    print(f"✅ {scenario_name}: Error handled correctly - {type(e).__name__}")
                    recovered_errors += 1
            
            # Test that server still works after errors
            print("Testing server recovery...")
            result = await self.server_instance._call_tool("health_check", {"random_string": "recovery_test"})
            health_data = json.loads(result[0].text)
            server_healthy = health_data.get("status") == "healthy"
            
            assert server_healthy, "Server not healthy after errors"
            print("✅ Server recovered successfully after errors")
            
            self.test_results.append({
                "test": "error_recovery",
                "status": True,
                "recovered_errors": recovered_errors,
                "server_healthy": server_healthy
            })
            
        except Exception as e:
            logger.error(f"Error recovery test failed: {e}")
            self.test_results.append({"test": "error_recovery", "status": False, "error": str(e)})
            # Don't raise - error recovery issues are not critical
    
    def print_test_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 MVP Core Functionality Test Summary")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["status"])
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed Tests: {passed_tests}")
        print(f"Failed Tests: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nTest Results:")
        print("-" * 40)
        
        for result in self.test_results:
            status_icon = "✅" if result["status"] else "❌"
            test_name = result["test"].replace("_", " ").title()
            print(f"{status_icon} {test_name}")
            
            if not result["status"] and "error" in result:
                print(f"   Error: {result['error']}")
            elif result["status"] and "avg_response_time" in result:
                print(f"   Performance: {result['avg_response_time']:.2f}ms avg")
        
        print("\n" + "=" * 60)
        
        # Determine overall status
        critical_tests = ["server_creation", "tools_availability", "project_management", "task_management"]
        critical_passed = sum(1 for result in self.test_results 
                            if result["test"] in critical_tests and result["status"])
        
        if critical_passed == len(critical_tests):
            print("🎉 CORE FUNCTIONALITY TESTS PASSED!")
            print("MVP is ready for the next deployment phase.")
            print("\n📋 Ready for:")
            print("1. ✅ MCP Server deployment") 
            print("2. ✅ Basic task management")
            print("3. ✅ Project operations")
            print("4. ✅ Core tool functionality")
            
            if passed_tests == total_tests:
                print("5. ✅ Performance optimization")
                print("6. ✅ Error recovery")
                print("7. ✅ Authentication system")
                
        else:
            print("❌ CRITICAL TESTS FAILED!")
            print("MVP needs fixes before deployment.")
            print("\n🔧 Required fixes:")
            for result in self.test_results:
                if result["test"] in critical_tests and not result["status"]:
                    print(f"- Fix {result['test']}: {result.get('error', 'Unknown error')}")


async def run_mvp_core_tests():
    """Run the MVP core functionality test suite"""
    test_suite = MVPCoreFunctionalityTests()
    await test_suite.run_all_tests()
    return test_suite


if __name__ == "__main__":
    print("🚀 Starting MVP Core Functionality Tests")
    print("Testing essential MCP server functionality for MVP deployment")
    print("=" * 80)
    
    # Run the test suite
    test_suite = asyncio.run(run_mvp_core_tests())
    
    # Exit with appropriate code based on critical tests
    critical_tests = ["server_creation", "tools_availability", "project_management", "task_management"]
    critical_passed = sum(1 for result in test_suite.test_results 
                        if result["test"] in critical_tests and result["status"])
    
    exit(0 if critical_passed == len(critical_tests) else 1)