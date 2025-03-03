#!/usr/bin/env python3
"""
Changeset Management Demo

This script demonstrates how to use the ServiceNow MCP server to manage changesets.
It shows how to create, update, commit, and publish changesets, as well as how to
add files to changesets and retrieve changeset details.
"""

import json
import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path so we can import the servicenow_mcp package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from servicenow_mcp.auth.auth_manager import AuthManager
from servicenow_mcp.tools.changeset_tools import (
    add_file_to_changeset,
    commit_changeset,
    create_changeset,
    get_changeset_details,
    list_changesets,
    publish_changeset,
    update_changeset,
)
from servicenow_mcp.utils.config import AuthConfig, AuthType, BasicAuthConfig, ServerConfig

# Load environment variables from .env file
load_dotenv()

# Get ServiceNow credentials from environment variables
instance_url = os.getenv("SERVICENOW_INSTANCE_URL")
username = os.getenv("SERVICENOW_USERNAME")
password = os.getenv("SERVICENOW_PASSWORD")

if not all([instance_url, username, password]):
    print("Error: Missing required environment variables.")
    print("Please set SERVICENOW_INSTANCE_URL, SERVICENOW_USERNAME, and SERVICENOW_PASSWORD.")
    sys.exit(1)

# Create server configuration
auth_config = AuthConfig(
    auth_type=AuthType.BASIC,
    basic=BasicAuthConfig(
        username=username,
        password=password,
    ),
)

server_config = ServerConfig(
    instance_url=instance_url,
    auth=auth_config,
)

# Create authentication manager
auth_manager = AuthManager(auth_config)
auth_manager.instance_url = instance_url


def print_json(data):
    """Print JSON data in a readable format."""
    print(json.dumps(data, indent=2))


def main():
    """Run the changeset management demo."""
    print("\n=== Changeset Management Demo ===\n")

    # Step 1: List existing changesets
    print("Step 1: Listing existing changesets...")
    result = list_changesets(auth_manager, server_config, {
        "limit": 5,
        "timeframe": "recent",
    })
    print_json(result)
    print("\n")

    # Step 2: Create a new changeset
    print("Step 2: Creating a new changeset...")
    create_result = create_changeset(auth_manager, server_config, {
        "name": "Demo Changeset",
        "description": "A demonstration changeset created by the MCP demo script",
        "application": "Global",  # Use a valid application name for your instance
        "developer": username,
    })
    print_json(create_result)
    print("\n")

    if not create_result.get("success"):
        print("Failed to create changeset. Exiting.")
        sys.exit(1)

    # Get the changeset ID from the create result
    changeset_id = create_result["changeset"]["sys_id"]
    print(f"Created changeset with ID: {changeset_id}")
    print("\n")

    # Step 3: Update the changeset
    print("Step 3: Updating the changeset...")
    update_result = update_changeset(auth_manager, server_config, {
        "changeset_id": changeset_id,
        "name": "Demo Changeset - Updated",
        "description": "An updated demonstration changeset",
    })
    print_json(update_result)
    print("\n")

    # Step 4: Add a file to the changeset
    print("Step 4: Adding a file to the changeset...")
    file_content = """
function demoFunction() {
    // This is a demonstration function
    gs.info('Hello from the demo changeset!');
    return 'Demo function executed successfully';
}
"""
    add_file_result = add_file_to_changeset(auth_manager, server_config, {
        "changeset_id": changeset_id,
        "file_path": "scripts/demo_function.js",
        "file_content": file_content,
    })
    print_json(add_file_result)
    print("\n")

    # Step 5: Get changeset details
    print("Step 5: Getting changeset details...")
    details_result = get_changeset_details(auth_manager, server_config, {
        "changeset_id": changeset_id,
    })
    print_json(details_result)
    print("\n")

    # Step 6: Commit the changeset
    print("Step 6: Committing the changeset...")
    commit_result = commit_changeset(auth_manager, server_config, {
        "changeset_id": changeset_id,
        "commit_message": "Completed the demo changeset",
    })
    print_json(commit_result)
    print("\n")

    # Step 7: Publish the changeset
    print("Step 7: Publishing the changeset...")
    publish_result = publish_changeset(auth_manager, server_config, {
        "changeset_id": changeset_id,
        "publish_notes": "Demo changeset ready for deployment",
    })
    print_json(publish_result)
    print("\n")

    # Step 8: Get final changeset details
    print("Step 8: Getting final changeset details...")
    final_details_result = get_changeset_details(auth_manager, server_config, {
        "changeset_id": changeset_id,
    })
    print_json(final_details_result)
    print("\n")

    print("=== Changeset Management Demo Completed ===")


if __name__ == "__main__":
    main() 