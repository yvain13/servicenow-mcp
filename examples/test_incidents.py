#!/usr/bin/env python
"""
Test script for incident management functionality.

This script demonstrates how to use the ServiceNow MCP server to manage incidents.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from servicenow_mcp.utils.config import ServerConfig, AuthConfig, AuthType, BasicAuthConfig
from servicenow_mcp.auth.auth_manager import AuthManager
from servicenow_mcp.resources.incidents import IncidentResource, IncidentListParams
from servicenow_mcp.tools.incident_tools import (
    create_incident, 
    update_incident, 
    add_comment, 
    resolve_incident,
    CreateIncidentParams,
    UpdateIncidentParams,
    AddCommentParams,
    ResolveIncidentParams,
)


async def run_tests():
    """Run the incident management test."""
    # Load environment variables
    load_dotenv()
    
    # Get configuration from environment variables
    instance_url = os.getenv("SERVICENOW_INSTANCE_URL")
    username = os.getenv("SERVICENOW_USERNAME")
    password = os.getenv("SERVICENOW_PASSWORD")
    auth_type = os.getenv("SERVICENOW_AUTH_TYPE", "basic")
    
    if not instance_url or not username or not password:
        print("Error: Missing required environment variables.")
        print("Please set SERVICENOW_INSTANCE_URL, SERVICENOW_USERNAME, and SERVICENOW_PASSWORD.")
        sys.exit(1)
    
    # Create configuration
    auth_config = AuthConfig(
        type=AuthType.BASIC,
        basic=BasicAuthConfig(
            username=username,
            password=password,
        ),
    )
    
    config = ServerConfig(
        instance_url=instance_url,
        auth=auth_config,
        debug=True,
    )
    
    # Create authentication manager
    auth_manager = AuthManager(config.auth)
    
    # Test incident creation
    print("\n=== Creating a test incident ===")
    create_params = CreateIncidentParams(
        short_description="Test incident from MCP",
        description="This is a test incident created by the ServiceNow MCP server.",
        category="Software",
        priority="3",
    )
    
    create_result = create_incident(config, auth_manager, create_params)
    print(f"Result: {create_result.success}")
    print(f"Message: {create_result.message}")
    print(f"Incident ID: {create_result.incident_id}")
    print(f"Incident Number: {create_result.incident_number}")
    
    if not create_result.success:
        print("Failed to create incident. Exiting.")
        sys.exit(1)
    
    incident_id = create_result.incident_number
    
    # Test incident retrieval
    print("\n=== Retrieving the created incident ===")
    incident_resource = IncidentResource(config, auth_manager)
    incident = await incident_resource.get_incident(incident_id)
    print(f"Incident Number: {incident.number}")
    print(f"Short Description: {incident.short_description}")
    print(f"State: {incident.state}")
    
    # Test adding a comment
    print("\n=== Adding a comment to the incident ===")
    comment_params = AddCommentParams(
        incident_id=incident_id,
        comment="This is a test comment added by the ServiceNow MCP server.",
        is_work_note=False,
    )
    
    comment_result = add_comment(config, auth_manager, comment_params)
    print(f"Result: {comment_result.success}")
    print(f"Message: {comment_result.message}")
    
    # Test updating the incident
    print("\n=== Updating the incident ===")
    update_params = UpdateIncidentParams(
        incident_id=incident_id,
        short_description="Updated test incident from MCP",
        priority="2",
    )
    
    update_result = update_incident(config, auth_manager, update_params)
    print(f"Result: {update_result.success}")
    print(f"Message: {update_result.message}")
    
    # Test resolving the incident
    print("\n=== Resolving the incident ===")
    resolve_params = ResolveIncidentParams(
        incident_id=incident_id,
        resolution_code="Solved (Permanently)",
        resolution_notes="This test incident has been resolved.",
    )
    
    resolve_result = resolve_incident(config, auth_manager, resolve_params)
    print(f"Result: {resolve_result.success}")
    print(f"Message: {resolve_result.message}")
    
    # Test listing incidents
    print("\n=== Listing recent incidents ===")
    list_params = IncidentListParams(
        limit=5,
        offset=0,
    )
    
    incidents = await incident_resource.list_incidents(list_params)
    print(f"Found {len(incidents)} incidents:")
    for inc in incidents:
        print(f"- {inc.number}: {inc.short_description} (State: {inc.state})")


def main():
    """Run the async tests."""
    asyncio.run(run_tests())


if __name__ == "__main__":
    main() 