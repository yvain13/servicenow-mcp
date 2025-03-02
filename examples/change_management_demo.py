#!/usr/bin/env python
"""
Change Management Demo

This script demonstrates how to use the ServiceNow MCP server with Claude Desktop
to manage change requests in ServiceNow.
"""

import json
import os
from datetime import datetime, timedelta

from dotenv import load_dotenv

from servicenow_mcp.auth.auth_manager import AuthManager
from servicenow_mcp.tools.change_tools import (
    add_change_task,
    approve_change,
    create_change_request,
    get_change_request_details,
    list_change_requests,
    submit_change_for_approval,
    update_change_request,
)
from servicenow_mcp.utils.config import AuthConfig, AuthType, BasicAuthConfig, ServerConfig


def main():
    """Run the change management demo."""
    # Load environment variables from .env file
    load_dotenv()

    # Create auth configuration
    auth_config = AuthConfig(
        type=AuthType.BASIC,
        basic=BasicAuthConfig(
            username=os.environ.get("SERVICENOW_USERNAME"),
            password=os.environ.get("SERVICENOW_PASSWORD"),
        )
    )

    # Create server configuration with auth
    server_config = ServerConfig(
        instance_url=os.environ.get("SERVICENOW_INSTANCE_URL"),
        debug=os.environ.get("DEBUG", "false").lower() == "true",
        auth=auth_config,
    )

    # Create authentication manager with the auth_config
    auth_manager = AuthManager(auth_config)

    print("ServiceNow Change Management Demo")
    print("=================================")
    print(f"Instance URL: {server_config.instance_url}")
    print(f"Auth Type: {auth_config.type}")
    print()

    # Demo 1: Create a change request
    print("Demo 1: Creating a change request")
    print("---------------------------------")
    
    # Calculate start and end dates for the change (tomorrow)
    tomorrow = datetime.now() + timedelta(days=1)
    start_date = tomorrow.replace(hour=1, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")
    end_date = tomorrow.replace(hour=3, minute=0, second=0).strftime("%Y-%m-%d %H:%M:%S")
    
    create_params = {
        "short_description": "Server maintenance - Apply security patches",
        "description": "Apply the latest security patches to the application servers to address recent vulnerabilities.",
        "type": "normal",
        "risk": "moderate",
        "impact": "medium",
        "category": "Hardware",
        "start_date": start_date,
        "end_date": end_date,
    }
    
    result = create_change_request(auth_manager, server_config, create_params)
    print(json.dumps(result, indent=2))
    
    if not result.get("success"):
        print("Failed to create change request. Exiting demo.")
        return
    
    # Store the change request ID for later use
    change_id = result["change_request"]["sys_id"]
    print(f"Created change request with ID: {change_id}")
    print()
    
    # Demo 2: Add tasks to the change request
    print("Demo 2: Adding tasks to the change request")
    print("-----------------------------------------")
    
    # Task 1: Pre-implementation checks
    task1_params = {
        "change_id": change_id,
        "short_description": "Pre-implementation checks",
        "description": "Verify system backups and confirm all prerequisites are met.",
        "planned_start_date": start_date,
        "planned_end_date": (datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S") + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    task1_result = add_change_task(auth_manager, server_config, task1_params)
    print(json.dumps(task1_result, indent=2))
    
    # Task 2: Apply patches
    task2_params = {
        "change_id": change_id,
        "short_description": "Apply security patches",
        "description": "Apply the latest security patches to all application servers.",
        "planned_start_date": (datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S") + timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S"),
        "planned_end_date": (datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S") + timedelta(minutes=90)).strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    task2_result = add_change_task(auth_manager, server_config, task2_params)
    print(json.dumps(task2_result, indent=2))
    
    # Task 3: Post-implementation verification
    task3_params = {
        "change_id": change_id,
        "short_description": "Post-implementation verification",
        "description": "Verify all systems are functioning correctly after patching.",
        "planned_start_date": (datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S") + timedelta(minutes=90)).strftime("%Y-%m-%d %H:%M:%S"),
        "planned_end_date": (datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S") + timedelta(minutes=120)).strftime("%Y-%m-%d %H:%M:%S"),
    }
    
    task3_result = add_change_task(auth_manager, server_config, task3_params)
    print(json.dumps(task3_result, indent=2))
    print()
    
    # Demo 3: Update the change request
    print("Demo 3: Updating the change request")
    print("----------------------------------")
    
    update_params = {
        "change_id": change_id,
        "work_notes": "Added implementation plan and tasks. Ready for review.",
        "risk": "low",  # Downgrading risk after assessment
    }
    
    update_result = update_change_request(auth_manager, server_config, update_params)
    print(json.dumps(update_result, indent=2))
    print()
    
    # Demo 4: Get change request details
    print("Demo 4: Getting change request details")
    print("-------------------------------------")
    
    details_params = {
        "change_id": change_id,
    }
    
    details_result = get_change_request_details(auth_manager, server_config, details_params)
    print(json.dumps(details_result, indent=2))
    print()
    
    # Demo 5: Submit change for approval
    print("Demo 5: Submitting change for approval")
    print("-------------------------------------")
    
    approval_params = {
        "change_id": change_id,
        "approval_comments": "Implementation plan is complete and ready for review.",
    }
    
    approval_result = submit_change_for_approval(auth_manager, server_config, approval_params)
    print(json.dumps(approval_result, indent=2))
    print()
    
    # Demo 6: List change requests
    print("Demo 6: Listing change requests")
    print("------------------------------")
    
    list_params = {
        "limit": 5,
        "timeframe": "upcoming",
    }
    
    list_result = list_change_requests(auth_manager, server_config, list_params)
    print(json.dumps(list_result, indent=2))
    print()
    
    # Demo 7: Approve the change request
    print("Demo 7: Approving the change request")
    print("-----------------------------------")
    
    approve_params = {
        "change_id": change_id,
        "approval_comments": "Implementation plan looks good. Approved.",
    }
    
    approve_result = approve_change(auth_manager, server_config, approve_params)
    print(json.dumps(approve_result, indent=2))
    print()
    
    print("Change Management Demo Complete")
    print("==============================")
    print(f"Created and managed change request: {change_id}")
    print("You can now view this change request in your ServiceNow instance.")


if __name__ == "__main__":
    main() 