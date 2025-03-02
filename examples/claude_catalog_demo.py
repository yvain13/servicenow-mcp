#!/usr/bin/env python
"""
Claude Desktop Service Catalog Demo

This script demonstrates how to use the ServiceNow MCP server with Claude Desktop
to interact with the ServiceNow Service Catalog.

Prerequisites:
1. Claude Desktop installed
2. ServiceNow MCP server configured in Claude Desktop
3. Valid ServiceNow credentials with access to the Service Catalog

Usage:
    python examples/claude_catalog_demo.py [--dry-run]
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv

# Parse command line arguments
parser = argparse.ArgumentParser(description="Claude Desktop Service Catalog Demo")
parser.add_argument("--dry-run", action="store_true", help="Skip launching Claude Desktop")
args = parser.parse_args()

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
            "args": ["-m", "servicenow_mcp.cli"],
            "env": {
                "SERVICENOW_INSTANCE_URL": instance_url,
                "SERVICENOW_USERNAME": username,
                "SERVICENOW_PASSWORD": password,
                "SERVICENOW_AUTH_TYPE": "basic",
            },
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

print("\n=== Example Prompts for Service Catalog ===")
print("\n1. List catalog categories:")
print("   Can you list the available service catalog categories in ServiceNow?")

print("\n2. List catalog items:")
print("   Can you show me the available items in the ServiceNow service catalog?")

print("\n3. List items in a specific category:")
print("   Can you list the catalog items in the Hardware category?")

print("\n4. Get catalog item details:")
print("   Can you show me the details of the 'New Laptop' catalog item?")

print("\n5. Find items by keyword:")
print("   Can you find catalog items related to 'software' in ServiceNow?")

print("\n6. Compare catalog items:")
print("   Can you compare the different laptop options available in the service catalog?")

print("\n7. Explain catalog item variables:")
print("   What information do I need to provide when ordering a new laptop?")

if args.dry_run:
    print("\n=== Dry Run Mode ===")
    print("Skipping Claude Desktop launch. Start Claude Desktop manually to use the configuration.")
    sys.exit(0)

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
