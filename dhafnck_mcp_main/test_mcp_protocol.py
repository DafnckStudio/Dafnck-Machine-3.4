#!/usr/bin/env python3
"""
Test MCP Protocol Communication

This script tests the MCP protocol communication with the new FastMCP server entry point.
"""

import json
import subprocess
import sys
import os
import time
from pathlib import Path

def test_mcp_protocol():
    """Test the MCP protocol communication."""
    
    print("🧪 Testing MCP Protocol Communication...")
    
    # Set up environment
    env = os.environ.copy()
    env.update({
        "PYTHONPATH": "src",
        "TASKS_JSON_PATH": "../.cursor/rules/tasks/tasks.json",
        "PROJECTS_FILE_PATH": "../.cursor/rules/brain/projects.json", 
        "CURSOR_AGENT_DIR_PATH": "yaml-lib"
    })
    
    # Start the MCP server process
    cmd = [sys.executable, "-m", "fastmcp.server.mcp_entry_point"]
    
    try:
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            text=True,
            bufsize=0
        )
        
        # Test sequence of MCP protocol messages
        test_messages = [
            # 1. Initialize the server
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            },
            # 2. Send initialized notification
            {
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {}
            },
            # 3. List available tools
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
        ]
        
        responses = []
        
        for i, message in enumerate(test_messages):
            print(f"📤 Sending message {i+1}: {message['method']}")
            
            # Send the message
            message_str = json.dumps(message) + "\n"
            process.stdin.write(message_str)
            process.stdin.flush()
            
            # For notifications, we don't expect a response
            if message.get("method") == "notifications/initialized":
                time.sleep(0.1)  # Small delay
                continue
            
            # Read response
            try:
                response_line = process.stdout.readline()
                if response_line:
                    response = json.loads(response_line.strip())
                    responses.append(response)
                    print(f"📥 Received response {i+1}: {response.get('result', {}).get('tools', 'N/A') if 'result' in response else 'Error' if 'error' in response else 'OK'}")
                else:
                    print(f"❌ No response for message {i+1}")
                    break
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse response for message {i+1}: {e}")
                break
            except Exception as e:
                print(f"❌ Error reading response for message {i+1}: {e}")
                break
        
        # Terminate the process
        process.terminate()
        process.wait(timeout=5)
        
        # Analyze results
        print("\n📊 Test Results:")
        
        # Use assertions instead of return
        assert len(responses) >= 2, "Should receive at least 2 responses (initialize + tools/list)"
        
        init_response = responses[0]
        tools_response = responses[1] if len(responses) > 1 else None
        
        # Check initialization
        if "result" in init_response:
            print("✅ Server initialization: SUCCESS")
            capabilities = init_response["result"].get("capabilities", {})
            print(f"   Server capabilities: {list(capabilities.keys())}")
        else:
            print("❌ Server initialization: FAILED")
            print(f"   Error: {init_response.get('error', 'Unknown error')}")
            assert False, f"Server initialization failed: {init_response.get('error', 'Unknown error')}"
        
        # Check tools listing
        if tools_response and "result" in tools_response:
            tools = tools_response["result"].get("tools", [])
            print(f"✅ Tools listing: SUCCESS ({len(tools)} tools)")
            
            # List some key tools
            tool_names = [tool.get("name", "unnamed") for tool in tools]
            task_tools = [name for name in tool_names if any(keyword in name.lower() for keyword in ["task", "project", "agent"])]
            print(f"   Task management tools: {task_tools[:5]}{'...' if len(task_tools) > 5 else ''}")
            
            assert len(tools) > 0, "Should have at least some tools available"
        else:
            print("❌ Tools listing: FAILED")
            if tools_response:
                print(f"   Error: {tools_response.get('error', 'Unknown error')}")
                assert False, f"Tools listing failed: {tools_response.get('error', 'Unknown error')}"
            else:
                assert False, "No tools response received"
        
        # Final assertion - all responses should have results
        assert all("result" in resp for resp in responses), "All responses should contain results"
        
    except subprocess.TimeoutExpired:
        print("❌ Process timed out")
        process.kill()
        assert False, "Process timed out"
    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        if process:
            process.terminate()
        assert False, f"Test failed with exception: {e}"


def main():
    """Main test function."""
    print("🚀 Starting MCP Protocol Test for FastMCP Server")
    
    # Change to the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    success = test_mcp_protocol()
    
    if success:
        print("\n🎉 MCP Protocol test completed successfully!")
        print("✅ The FastMCP server with consolidated tools is working correctly.")
        return 0
    else:
        print("\n💥 MCP Protocol test failed!")
        print("❌ There may be issues with the server configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 