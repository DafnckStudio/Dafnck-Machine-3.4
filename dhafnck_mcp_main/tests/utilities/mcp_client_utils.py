#!/usr/bin/env python3
"""
MCP Client Test Utilities for DhafnckMCP E2E Testing

Provides utilities for testing actual MCP protocol communication including:
- MCP client creation and connection
- Tool discovery and execution
- Protocol compliance testing
- Connection failure scenarios
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Optional, Any
import httpx
from pathlib import Path

logger = logging.getLogger(__name__)


class MCPTestClient:
    """Test client for MCP protocol communication"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip("/")
        self.session_id = None
        self.client = httpx.AsyncClient(timeout=30.0)
        
    async def connect(self) -> Dict:
        """Establish connection to MCP server"""
        try:
            # Test basic connectivity
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code != 200:
                raise Exception(f"Health check failed: {response.status_code}")
            
            # Initialize MCP session
            init_response = await self.client.post(
                f"{self.base_url}/mcp/initialize",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "clientInfo": {
                            "name": "dhafnck-mcp-test-client",
                            "version": "1.0.0"
                        }
                    }
                }
            )
            
            if init_response.status_code == 200:
                init_data = init_response.json()
                self.session_id = init_data.get("id")
                
                return {
                    "success": True,
                    "session_id": self.session_id,
                    "server_capabilities": init_data.get("result", {}).get("capabilities", {}),
                    "server_info": init_data.get("result", {}).get("serverInfo", {})
                }
            else:
                raise Exception(f"MCP initialization failed: {init_response.status_code}")
                
        except Exception as e:
            logger.error(f"MCP connection failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def list_tools(self) -> Dict:
        """List available tools from MCP server"""
        try:
            response = await self.client.post(
                f"{self.base_url}/mcp/call",
                json={
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list",
                    "params": {}
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                tools = data.get("result", {}).get("tools", [])
                
                return {
                    "success": True,
                    "tools": tools,
                    "tool_count": len(tools),
                    "tool_names": [tool.get("name") for tool in tools]
                }
            else:
                raise Exception(f"Tools list failed: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
            return {"success": False, "error": str(e)}
    
    async def call_tool(self, tool_name: str, arguments: Dict = None) -> Dict:
        """Call a specific MCP tool"""
        try:
            if arguments is None:
                arguments = {}
            
            start_time = time.time()
            
            response = await self.client.post(
                f"{self.base_url}/mcp/call",
                json={
                    "jsonrpc": "2.0",
                    "id": 3,
                    "method": "tools/call",
                    "params": {
                        "name": tool_name,
                        "arguments": arguments
                    }
                }
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            if response.status_code == 200:
                data = response.json()
                result = data.get("result", {})
                
                return {
                    "success": True,
                    "tool_name": tool_name,
                    "result": result,
                    "response_time": response_time,
                    "status_code": response.status_code
                }
            else:
                return {
                    "success": False,
                    "tool_name": tool_name,
                    "error": f"Tool call failed: {response.status_code}",
                    "response_time": response_time,
                    "status_code": response.status_code
                }
                
        except Exception as e:
            logger.error(f"Failed to call tool {tool_name}: {e}")
            return {"success": False, "tool_name": tool_name, "error": str(e)}
    
    async def test_tool_suite(self) -> Dict:
        """Test all available tools with basic operations"""
        try:
            # First get list of tools
            tools_result = await self.list_tools()
            if not tools_result["success"]:
                return {"success": False, "error": "Failed to get tool list"}
            
            test_results = {}
            
            # Test each tool with appropriate arguments
            for tool_name in tools_result["tool_names"]:
                if tool_name == "health_check":
                    result = await self.call_tool("health_check", {"random_string": "test"})
                
                elif tool_name == "get_server_capabilities":
                    result = await self.call_tool("get_server_capabilities", {"random_string": "test"})
                
                elif tool_name == "manage_project":
                    result = await self.call_tool("manage_project", {"action": "list"})
                
                elif tool_name == "manage_task":
                    result = await self.call_tool("manage_task", {
                        "action": "list", 
                        "project_id": "test_project"
                    })
                
                elif tool_name == "manage_agent":
                    result = await self.call_tool("manage_agent", {
                        "action": "list",
                        "project_id": "test_project"
                    })
                
                elif tool_name == "call_agent":
                    result = await self.call_tool("call_agent", {"name_agent": "test_agent"})
                
                else:
                    # Generic test for unknown tools
                    result = await self.call_tool(tool_name, {})
                
                test_results[tool_name] = result
            
            # Calculate overall success rate
            successful_tools = sum(1 for r in test_results.values() if r.get("success", False))
            total_tools = len(test_results)
            success_rate = successful_tools / total_tools if total_tools > 0 else 0
            
            return {
                "success": True,
                "test_results": test_results,
                "successful_tools": successful_tools,
                "total_tools": total_tools,
                "success_rate": success_rate,
                "avg_response_time": sum(
                    r.get("response_time", 0) for r in test_results.values()
                ) / total_tools if total_tools > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Tool suite test failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_project_workflow(self) -> Dict:
        """Test complete project management workflow"""
        try:
            workflow_results = []
            
            # Step 1: Create a test project
            create_result = await self.call_tool("manage_project", {
                "action": "create",
                "project_id": "mcp_test_project",
                "name": "MCP Test Project",
                "description": "Project created for MCP testing"
            })
            workflow_results.append(("create_project", create_result))
            
            # Step 2: List projects to verify creation
            list_result = await self.call_tool("manage_project", {"action": "list"})
            workflow_results.append(("list_projects", list_result))
            
            # Step 3: Create a task in the project
            task_result = await self.call_tool("manage_task", {
                "action": "create",
                "project_id": "mcp_test_project",
                "title": "Test Task",
                "description": "Task created for MCP testing",
                "priority": "medium"
            })
            workflow_results.append(("create_task", task_result))
            
            # Step 4: List tasks to verify creation
            task_list_result = await self.call_tool("manage_task", {
                "action": "list",
                "project_id": "mcp_test_project"
            })
            workflow_results.append(("list_tasks", task_list_result))
            
            # Step 5: Get next task
            next_task_result = await self.call_tool("manage_task", {
                "action": "next",
                "project_id": "mcp_test_project"
            })
            workflow_results.append(("next_task", next_task_result))
            
            # Calculate workflow success
            successful_steps = sum(1 for _, r in workflow_results if r.get("success", False))
            total_steps = len(workflow_results)
            
            return {
                "success": successful_steps == total_steps,
                "workflow_results": workflow_results,
                "successful_steps": successful_steps,
                "total_steps": total_steps,
                "workflow_success_rate": successful_steps / total_steps
            }
            
        except Exception as e:
            logger.error(f"Project workflow test failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_error_scenarios(self) -> Dict:
        """Test error handling and edge cases"""
        try:
            error_tests = []
            
            # Test 1: Invalid tool name
            invalid_tool_result = await self.call_tool("nonexistent_tool", {})
            error_tests.append(("invalid_tool", invalid_tool_result))
            
            # Test 2: Invalid parameters
            invalid_params_result = await self.call_tool("manage_project", {
                "action": "invalid_action"
            })
            error_tests.append(("invalid_params", invalid_params_result))
            
            # Test 3: Missing required parameters
            missing_params_result = await self.call_tool("manage_task", {
                "action": "create"
                # Missing required fields
            })
            error_tests.append(("missing_params", missing_params_result))
            
            # Test 4: Malformed JSON (simulate network issue)
            try:
                malformed_response = await self.client.post(
                    f"{self.base_url}/mcp/call",
                    content="invalid json"
                )
                error_tests.append(("malformed_json", {
                    "success": False,
                    "status_code": malformed_response.status_code
                }))
            except Exception as e:
                error_tests.append(("malformed_json", {
                    "success": False,
                    "error": str(e)
                }))
            
            return {
                "success": True,
                "error_tests": error_tests,
                "message": "Error scenario testing completed"
            }
            
        except Exception as e:
            logger.error(f"Error scenario testing failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_performance_under_load(self, num_requests: int = 10) -> Dict:
        """Test performance under concurrent load"""
        try:
            start_time = time.time()
            
            # Create concurrent tasks
            tasks = []
            for i in range(num_requests):
                task = self.call_tool("health_check", {"random_string": f"load_test_{i}"})
                tasks.append(task)
            
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            # Analyze results
            successful_requests = 0
            failed_requests = 0
            response_times = []
            
            for result in results:
                if isinstance(result, Exception):
                    failed_requests += 1
                elif result.get("success", False):
                    successful_requests += 1
                    response_times.append(result.get("response_time", 0))
                else:
                    failed_requests += 1
            
            return {
                "success": True,
                "total_requests": num_requests,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate": successful_requests / num_requests,
                "total_time": total_time,
                "requests_per_second": num_requests / total_time,
                "avg_response_time": sum(response_times) / len(response_times) if response_times else 0,
                "min_response_time": min(response_times) if response_times else 0,
                "max_response_time": max(response_times) if response_times else 0
            }
            
        except Exception as e:
            logger.error(f"Load testing failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def generate_cursor_config(self, output_path: Path = None) -> Dict:
        """Generate Cursor MCP configuration file"""
        try:
            if output_path is None:
                output_path = Path.cwd() / "cursor_mcp_config.json"
            
            # Get server capabilities
            tools_result = await self.list_tools()
            if not tools_result["success"]:
                raise Exception("Failed to get server tools")
            
            config = {
                "mcpServers": {
                    "dhafnck-mcp": {
                        "command": "docker",
                        "args": [
                            "run",
                            "--rm",
                            "-p", "8000:8000",
                            "-e", "DHAFNCK_AUTH_ENABLED=false",
                            "-e", "DHAFNCK_MVP_MODE=true",
                            "dhafnck-mcp:latest"
                        ],
                        "env": {
                            "DHAFNCK_AUTH_ENABLED": "false",
                            "DHAFNCK_MVP_MODE": "true"
                        }
                    }
                }
            }
            
            # Write config file
            with open(output_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            return {
                "success": True,
                "config_path": str(output_path),
                "available_tools": tools_result["tool_names"],
                "tool_count": tools_result["tool_count"]
            }
            
        except Exception as e:
            logger.error(f"Failed to generate Cursor config: {e}")
            return {"success": False, "error": str(e)}
    
    async def disconnect(self):
        """Clean up and close connections"""
        try:
            await self.client.aclose()
            logger.info("MCP test client disconnected")
        except Exception as e:
            logger.error(f"Error during disconnect: {e}")


class MCPProtocolValidator:
    """Validates MCP protocol compliance"""
    
    @staticmethod
    def validate_tool_response(response: Dict) -> Dict:
        """Validate that a tool response follows MCP protocol"""
        errors = []
        
        # Check for required fields
        if "success" not in response:
            errors.append("Missing 'success' field")
        
        if "tool_name" not in response:
            errors.append("Missing 'tool_name' field")
        
        # Check response structure
        if response.get("success") and "result" not in response:
            errors.append("Successful response missing 'result' field")
        
        if not response.get("success") and "error" not in response:
            errors.append("Failed response missing 'error' field")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "response": response
        }
    
    @staticmethod
    def validate_tool_list(tools: List[Dict]) -> Dict:
        """Validate tool list structure"""
        errors = []
        
        for i, tool in enumerate(tools):
            if "name" not in tool:
                errors.append(f"Tool {i}: Missing 'name' field")
            
            if "description" not in tool:
                errors.append(f"Tool {i}: Missing 'description' field")
            
            if "inputSchema" not in tool:
                errors.append(f"Tool {i}: Missing 'inputSchema' field")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "tool_count": len(tools)
        } 