#!/usr/bin/env python
"""
Debug script for ServiceNow workflow API calls.
This script helps diagnose issues with the ServiceNow API by making direct calls
and printing detailed information about the requests and responses.
"""

import json
import logging
import os

import requests
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# ServiceNow instance details
instance_url = os.getenv("SERVICENOW_INSTANCE_URL")
username = os.getenv("SERVICENOW_USERNAME")
password = os.getenv("SERVICENOW_PASSWORD")

if not all([instance_url, username, password]):
    logger.error("Missing required environment variables. Please set SERVICENOW_INSTANCE_URL, SERVICENOW_USERNAME, and SERVICENOW_PASSWORD.")
    exit(1)

# Basic auth headers
auth = (username, password)

def debug_request(url, params=None, method="GET"):
    """Make a request to ServiceNow and print detailed debug information."""
    logger.info(f"Making {method} request to: {url}")
    logger.info(f"Parameters: {params}")
    
    try:
        if method == "GET":
            response = requests.get(url, auth=auth, params=params)
        elif method == "POST":
            response = requests.post(url, auth=auth, json=params)
        else:
            logger.error(f"Unsupported method: {method}")
            return
        
        logger.info(f"Status code: {response.status_code}")
        logger.info(f"Response headers: {response.headers}")
        
        # Try to parse as JSON
        try:
            json_response = response.json()
            logger.info(f"JSON response: {json.dumps(json_response, indent=2)}")
        except json.JSONDecodeError:
            logger.warning("Response is not valid JSON")
            logger.info(f"Raw response content: {response.content}")
        
        return response
    
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}")
        return None

def test_list_workflows():
    """Test listing workflows."""
    logger.info("=== Testing list_workflows ===")
    url = f"{instance_url}/api/now/table/wf_workflow"
    params = {
        "sysparm_limit": 10,
    }
    return debug_request(url, params)

def test_list_workflows_active():
    """Test listing active workflows."""
    logger.info("=== Testing list_workflows with active=true ===")
    url = f"{instance_url}/api/now/table/wf_workflow"
    params = {
        "sysparm_limit": 10,
        "sysparm_query": "active=true",
    }
    return debug_request(url, params)

def test_get_workflow_details(workflow_id):
    """Test getting workflow details."""
    logger.info(f"=== Testing get_workflow_details for {workflow_id} ===")
    url = f"{instance_url}/api/now/table/wf_workflow/{workflow_id}"
    return debug_request(url)

def test_list_tables():
    """Test listing available tables to check API access."""
    logger.info("=== Testing list_tables ===")
    url = f"{instance_url}/api/now/table/sys_db_object"
    params = {
        "sysparm_limit": 5,
        "sysparm_fields": "name,label",
    }
    return debug_request(url, params)

def test_get_user_info():
    """Test getting current user info to verify authentication."""
    logger.info("=== Testing get_user_info ===")
    url = f"{instance_url}/api/now/table/sys_user"
    params = {
        "sysparm_query": "user_name=" + username,
        "sysparm_fields": "user_name,name,email,roles",
    }
    return debug_request(url, params)

if __name__ == "__main__":
    logger.info(f"Testing ServiceNow API at {instance_url}")
    
    # First, verify authentication and basic API access
    user_response = test_get_user_info()
    if not user_response or user_response.status_code != 200:
        logger.error("Authentication failed or user not found. Please check your credentials.")
        exit(1)
    
    # Test listing tables to verify API access
    tables_response = test_list_tables()
    if not tables_response or tables_response.status_code != 200:
        logger.error("Failed to list tables. API access may be restricted.")
        exit(1)
    
    # Test workflow API calls
    list_response = test_list_workflows()
    active_response = test_list_workflows_active()
    
    # If we got any workflows, test getting details for the first one
    if list_response and list_response.status_code == 200:
        try:
            workflows = list_response.json().get("result", [])
            if workflows:
                workflow_id = workflows[0]["sys_id"]
                test_get_workflow_details(workflow_id)
            else:
                logger.warning("No workflows found in the instance.")
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error processing workflow list response: {e}")
    
    logger.info("Debug tests completed.") 