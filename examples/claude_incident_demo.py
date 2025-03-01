#!/usr/bin/env python
"""
Claude Desktop Incident Management Demo

This script demonstrates how to use the ServiceNow MCP server with Claude Desktop
to manage incidents.

Prerequisites:
1. Claude Desktop installed
2. ServiceNow MCP server configured in Claude Desktop
3. Valid ServiceNow credentials
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get configuration from environment variables
instance_url = os.getenv("SERVICENOW_INSTANCE_URL")
username = os.getenv("SERVICENOW_USERNAME")
password = os.getenv("SERVICENOW_PASSWORD")

if not instance_url or not username or not password:
    print("Error: Missing required environment variables.")
    print("Please set SERVICENOW_INSTANCE_URL, SERVICENOW_USERNAME, and SERVICENOW_PASSWORD.")
    sys.exit(1)

# Create Claude Desktop configuration
claude_config = {
    "mcpServers": {
        "servicenow": {
            "command": "python",
            "args": [
                "-m",
                "servicenow_mcp.cli"
            ],
            "env": {
                "SERVICENOW_INSTANCE_URL": instance_url,
                "SERVICENOW_USERNAME": username,
                "SERVICENOW_PASSWORD": password,
                "SERVICENOW_AUTH_TYPE": "basic"
            }
        }
    }
}

# Save configuration to a temporary file
config_path = Path.home() / ".claude-desktop" / "config.json"
config_path.parent.mkdir(parents=True, exist_ok=True)

with open(config_path, "w") as f:
    json.dump(claude_config, f, indent=2)

print(f"Claude Desktop configuration saved to {config_path}")
print("You can now start Claude Desktop and use the following prompts:")

print("\n=== Example Prompts ===")
print("\n1. List recent incidents:")
print("   Can you list the 5 most recent incidents in ServiceNow?")

print("\n2. Get incident details:")
print("   Can you show me the details of incident INC0010001?")

print("\n3. Create a new incident:")
print("   Please create a new incident in ServiceNow with the following details:")
print("   - Short description: Email service is down")
print("   - Description: Users are unable to send or receive emails")
print("   - Category: Software")
print("   - Priority: 1")

print("\n4. Update an incident:")
print("   Please update incident INC0010001 with the following changes:")
print("   - Priority: 2")
print("   - Assigned to: admin")
print("   - Add work note: Investigating the issue")

print("\n5. Resolve an incident:")
print("   Please resolve incident INC0010001 with the following details:")
print("   - Resolution code: Solved (Permanently)")
print("   - Resolution notes: The email service has been restored")

print("\n=== Starting Claude Desktop ===")
print("Press Ctrl+C to exit this script and continue using Claude Desktop.")

try:
    # Try to start Claude Desktop
    subprocess.run(["claude"], check=True)
except KeyboardInterrupt:
    print("\nExiting script. Claude Desktop should be running.")
except Exception as e:
    print(f"\nFailed to start Claude Desktop: {e}")
    print("Please start Claude Desktop manually.") 