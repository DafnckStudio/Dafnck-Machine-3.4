#!/usr/bin/env python3
"""
Test script for the call_agent MCP tool using direct HTTP requests
"""

import sys
import json
import os
import requests
from pathlib import Path

def main():
    """Test the call_agent MCP tool using direct HTTP requests"""
    # MCP server URL
    mcp_url = "http://localhost:6274/v1/tools"
    
    # Agent name to test
    agent_name = "mcp_researcher_agent"
    if len(sys.argv) > 1:
        agent_name = sys.argv[1]
    
    print(f"Testing MCP call_agent tool with agent: {agent_name}")
    
    # Request payload
    payload = {
        "name": "call_agent",
        "arguments": {
            "name_agent": agent_name
        }
    }
    
    try:
        # Make the HTTP request
        response = requests.post(mcp_url, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: HTTP {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 