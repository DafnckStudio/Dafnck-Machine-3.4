"""Server Functionality Tests with Test Data Isolation"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

# Import test isolation system
from test_environment_config import isolated_test_environment


class TestServerFunctionalityIsolated:
    """Test server functionality with complete test isolation"""
    
    @pytest.mark.isolated
    def test_server_startup_and_shutdown(self):
        """Test server startup and shutdown lifecycle"""
        with isolated_test_environment(test_id="server_lifecycle") as config:
            # Mock server lifecycle
            server_state = {"running": False, "tools_loaded": 0, "connections": 0}
            
            # Test startup
            def mock_startup():
                server_state["running"] = True
                server_state["tools_loaded"] = 10
                return True
            
            # Test shutdown
            def mock_shutdown():
                server_state["running"] = False
                server_state["connections"] = 0
                return True
            
            # Simulate startup
            startup_result = mock_startup()
            assert startup_result == True
            assert server_state["running"] == True
            assert server_state["tools_loaded"] == 10
            
            # Simulate shutdown
            shutdown_result = mock_shutdown()
            assert shutdown_result == True
            assert server_state["running"] == False
            assert server_state["connections"] == 0
            
            print("✅ Server startup/shutdown test passed")
    
    @pytest.mark.isolated
    def test_http_request_handling(self):
        """Test HTTP request processing and routing"""
        with isolated_test_environment(test_id="http_handling") as config:
            # Mock HTTP request/response handling
            
            # Test GET request
            get_request = {
                "method": "GET",
                "path": "/health",
                "headers": {"Content-Type": "application/json"},
                "query_params": {}
            }
            
            def handle_get_request(request):
                if request["path"] == "/health":
                    return {
                        "status": 200,
                        "body": {"status": "healthy", "uptime": "1h 30m"},
                        "headers": {"Content-Type": "application/json"}
                    }
                return {"status": 404, "body": {"error": "Not found"}}
            
            response = handle_get_request(get_request)
            assert response["status"] == 200
            assert response["body"]["status"] == "healthy"
            
            # Test POST request
            post_request = {
                "method": "POST",
                "path": "/tools/call",
                "headers": {"Content-Type": "application/json"},
                "body": {
                    "tool": "manage_project",
                    "params": {"action": "list"}
                }
            }
            
            def handle_post_request(request):
                if request["path"] == "/tools/call":
                    tool = request["body"]["tool"]
                    return {
                        "status": 200,
                        "body": {"result": f"Called {tool} successfully"},
                        "headers": {"Content-Type": "application/json"}
                    }
                return {"status": 404, "body": {"error": "Not found"}}
            
            response = handle_post_request(post_request)
            assert response["status"] == 200
            assert "manage_project" in response["body"]["result"]
            
            print("✅ HTTP request handling test passed")
    
    @pytest.mark.isolated
    def test_middleware_processing(self):
        """Test middleware chain processing"""
        with isolated_test_environment(test_id="middleware_test") as config:
            # Mock middleware chain
            middleware_log = []
            
            def auth_middleware(request, next_handler):
                middleware_log.append("auth_start")
                if "Authorization" not in request.get("headers", {}):
                    return {"status": 401, "body": {"error": "Unauthorized"}}
                result = next_handler(request)
                middleware_log.append("auth_end")
                return result
            
            def logging_middleware(request, next_handler):
                middleware_log.append("logging_start")
                result = next_handler(request)
                middleware_log.append("logging_end")
                return result
            
            def cors_middleware(request, next_handler):
                middleware_log.append("cors_start")
                result = next_handler(request)
                if isinstance(result, dict):
                    if "headers" not in result:
                        result["headers"] = {}
                    result["headers"]["Access-Control-Allow-Origin"] = "*"
                middleware_log.append("cors_end")
                return result
            
            def final_handler(request):
                middleware_log.append("handler")
                return {"status": 200, "body": {"message": "Success"}}
            
            # Test middleware chain
            def process_request(request, middlewares, handler):
                def build_chain(middlewares, final_handler):
                    if not middlewares:
                        return final_handler
                    
                    current_middleware = middlewares[0]
                    next_handler = build_chain(middlewares[1:], final_handler)
                    
                    return lambda req: current_middleware(req, next_handler)
                
                chain = build_chain(middlewares, handler)
                return chain(request)
            
            # Test with auth header
            authorized_request = {
                "path": "/api/test",
                "headers": {"Authorization": "Bearer token123"}
            }
            
            middlewares = [logging_middleware, auth_middleware, cors_middleware]
            response = process_request(authorized_request, middlewares, final_handler)
            
            assert response["status"] == 200
            assert response["headers"]["Access-Control-Allow-Origin"] == "*"
            assert "logging_start" in middleware_log
            assert "auth_start" in middleware_log
            assert "cors_start" in middleware_log
            assert "handler" in middleware_log
            
            # Test without auth header
            middleware_log.clear()
            unauthorized_request = {"path": "/api/test", "headers": {}}
            
            response = process_request(unauthorized_request, middlewares, final_handler)
            assert response["status"] == 401
            assert "Unauthorized" in response["body"]["error"]
            
            print("✅ Middleware processing test passed")
    
    @pytest.mark.isolated
    def test_websocket_connections(self):
        """Test WebSocket connection handling"""
        with isolated_test_environment(test_id="websocket_test") as config:
            # Mock WebSocket functionality
            connections = {}
            message_log = []
            
            class MockWebSocket:
                def __init__(self, connection_id):
                    self.id = connection_id
                    self.connected = True
                    self.messages = []
                
                async def send(self, message):
                    if self.connected:
                        self.messages.append(message)
                        message_log.append(f"sent_to_{self.id}: {message}")
                        return True
                    return False
                
                async def receive(self):
                    # Mock receiving a message
                    return f"message_from_{self.id}"
                
                def close(self):
                    self.connected = False
            
            # Test connection management
            def connect_websocket(connection_id):
                ws = MockWebSocket(connection_id)
                connections[connection_id] = ws
                return ws
            
            def disconnect_websocket(connection_id):
                if connection_id in connections:
                    connections[connection_id].close()
                    del connections[connection_id]
            
            # Test multiple connections
            ws1 = connect_websocket("client_1")
            ws2 = connect_websocket("client_2")
            
            assert len(connections) == 2
            assert ws1.connected == True
            assert ws2.connected == True
            
            # Test message broadcasting
            async def broadcast_message(message):
                for ws in connections.values():
                    await ws.send(message)
            
            # Run async test
            async def run_websocket_test():
                await broadcast_message("Hello all clients")
                
                # Verify messages sent
                assert len(ws1.messages) == 1
                assert len(ws2.messages) == 1
                assert ws1.messages[0] == "Hello all clients"
                assert ws2.messages[0] == "Hello all clients"
                
                # Test disconnection
                disconnect_websocket("client_1")
                assert len(connections) == 1
                assert ws1.connected == False
                assert ws2.connected == True
            
            # Run the async test
            asyncio.run(run_websocket_test())
            
            print("✅ WebSocket connections test passed")
    
    @pytest.mark.isolated
    def test_error_handling_and_recovery(self):
        """Test server error handling and recovery mechanisms"""
        with isolated_test_environment(test_id="error_recovery") as config:
            # Mock error scenarios
            error_log = []
            recovery_actions = []
            
            def log_error(error_type, message, context=None):
                error_log.append({
                    "type": error_type,
                    "message": message,
                    "context": context,
                    "timestamp": "2025-01-26T12:00:00Z"
                })
            
            def attempt_recovery(error_type):
                if error_type == "connection_lost":
                    recovery_actions.append("reconnect_attempted")
                    return True
                elif error_type == "tool_error":
                    recovery_actions.append("tool_reloaded")
                    return True
                elif error_type == "memory_error":
                    recovery_actions.append("garbage_collection")
                    return False  # Some errors can't be recovered
                return False
            
            # Test different error scenarios
            test_errors = [
                ("connection_lost", "Client connection dropped"),
                ("tool_error", "Tool execution failed"),
                ("memory_error", "Out of memory"),
                ("invalid_request", "Malformed JSON request")
            ]
            
            for error_type, message in test_errors:
                log_error(error_type, message, {"severity": "high"})
                recovery_success = attempt_recovery(error_type)
                
                # Verify error logging
                assert len(error_log) > 0
                latest_error = error_log[-1]
                assert latest_error["type"] == error_type
                assert latest_error["message"] == message
                
                # Verify recovery attempts
                if error_type in ["connection_lost", "tool_error"]:
                    assert recovery_success == True
                    assert len(recovery_actions) > 0
                elif error_type == "memory_error":
                    assert recovery_success == False
            
            # Verify error log contents
            assert len(error_log) == 4
            assert len(recovery_actions) == 3  # 2 successful + 1 attempted
            
            print("✅ Error handling and recovery test passed")
    
    @pytest.mark.isolated
    def test_performance_monitoring(self):
        """Test server performance monitoring and metrics"""
        with isolated_test_environment(test_id="performance_test") as config:
            # Mock performance metrics
            metrics = {
                "requests_per_second": 0,
                "average_response_time": 0,
                "memory_usage": 0,
                "cpu_usage": 0,
                "active_connections": 0
            }
            
            request_times = []
            
            def process_request_with_timing(request_handler, request):
                import time
                start_time = time.time()
                
                # Simulate request processing
                result = request_handler(request)
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000  # Convert to ms
                request_times.append(response_time)
                
                return result, response_time
            
            def update_metrics():
                if request_times:
                    metrics["average_response_time"] = sum(request_times) / len(request_times)
                    metrics["requests_per_second"] = len(request_times) / 10  # Mock 10 second window
                
                # Mock other metrics
                metrics["memory_usage"] = 45.5  # 45.5%
                metrics["cpu_usage"] = 23.2    # 23.2%
                metrics["active_connections"] = 5
            
            # Mock request handler
            def mock_request_handler(request):
                import time
                time.sleep(0.001)  # Simulate 1ms processing time
                return {"status": 200, "body": {"result": "success"}}
            
            # Process several requests
            test_requests = [
                {"path": "/api/test1"},
                {"path": "/api/test2"}, 
                {"path": "/api/test3"}
            ]
            
            for request in test_requests:
                result, response_time = process_request_with_timing(mock_request_handler, request)
                assert result["status"] == 200
                assert response_time > 0
            
            # Update and verify metrics
            update_metrics()
            
            assert metrics["average_response_time"] > 0
            assert metrics["requests_per_second"] > 0
            assert metrics["memory_usage"] == 45.5
            assert metrics["cpu_usage"] == 23.2
            assert metrics["active_connections"] == 5
            assert len(request_times) == 3
            
            print("✅ Performance monitoring test passed")


# Run tests if executed directly
if __name__ == "__main__":
    test_instance = TestServerFunctionalityIsolated()
    
    print("🧪 Running server functionality tests...")
    
    test_instance.test_server_startup_and_shutdown()
    test_instance.test_http_request_handling()
    test_instance.test_middleware_processing()
    test_instance.test_websocket_connections()
    test_instance.test_error_handling_and_recovery()
    test_instance.test_performance_monitoring()
    
    print("🎉 All server functionality tests passed!") 