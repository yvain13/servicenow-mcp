#!/usr/bin/env python
"""
ServiceNow MCP Demo Script

This script demonstrates how to use the ServiceNow MCP server with Claude.
It simulates a conversation where Claude requests information from ServiceNow.

Usage:
    python examples/claude_servicenow_demo.py
"""

import json
import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from servicenow_mcp.server import ServiceNowMCPServer
from servicenow_mcp.auth import get_auth_handler

def simulate_claude_request(server, request):
    """Simulate a request from Claude to the MCP server."""
    print(f"\n--- Claude Request ---\n{request}\n")
    response = server.handle_request(json.loads(request))
    print(f"--- MCP Response ---\n{json.dumps(response, indent=2)}\n")
    return response

def main():
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Check if required environment variables are set
    required_vars = ["SERVICENOW_INSTANCE_URL", "SERVICENOW_USERNAME", "SERVICENOW_PASSWORD"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables in your .env file or environment.")
        sys.exit(1)
    
    # Create auth handler
    auth_type = os.getenv("SERVICENOW_AUTH_TYPE", "basic")
    auth_handler = get_auth_handler(auth_type)
    
    # Create MCP server
    server = ServiceNowMCPServer(auth_handler=auth_handler)
    
    print("=== ServiceNow MCP Demo ===")
    print(f"Connected to: {os.getenv('SERVICENOW_INSTANCE_URL')}")
    print(f"Authentication: {auth_type}")
    
    # Simulate a conversation with Claude
    
    # 1. Claude asks for server capabilities
    capabilities_request = """
    {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getCapabilities"
    }
    """
    simulate_claude_request(server, capabilities_request)
    
    # 2. Claude asks for incident information
    incident_request = """
    {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "executeQuery",
        "params": {
            "table": "incident",
            "query": "state=1^priority=1",
            "limit": 3
        }
    }
    """
    simulate_claude_request(server, incident_request)
    
    # 3. Claude asks for user information
    user_request = """
    {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "executeQuery",
        "params": {
            "table": "sys_user",
            "query": "active=true",
            "limit": 2
        }
    }
    """
    simulate_claude_request(server, user_request)
    
    print("Demo completed successfully!")

if __name__ == "__main__":
    main() 