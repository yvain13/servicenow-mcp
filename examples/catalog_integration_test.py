#!/usr/bin/env python
"""
ServiceNow Catalog Integration Test

This script demonstrates how to use the ServiceNow MCP server to interact with
the ServiceNow Service Catalog. It serves as an integration test to verify that
the catalog functionality works correctly with a real ServiceNow instance.

Prerequisites:
1. Valid ServiceNow credentials with access to the Service Catalog
2. ServiceNow MCP package installed

Usage:
    python examples/catalog_integration_test.py
"""

import os
import sys

from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from servicenow_mcp.auth.auth_manager import AuthManager
from servicenow_mcp.tools.catalog_tools import (
    GetCatalogItemParams,
    ListCatalogCategoriesParams,
    ListCatalogItemsParams,
    get_catalog_item,
    list_catalog_categories,
    list_catalog_items,
)
from servicenow_mcp.utils.config import AuthConfig, AuthType, BasicAuthConfig, ServerConfig


def main():
    """Run the catalog integration test."""
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

    print(f"Connecting to ServiceNow instance: {instance_url}")

    # Create the server config
    config = ServerConfig(
        instance_url=instance_url,
        auth=AuthConfig(
            type=AuthType.BASIC,
            basic=BasicAuthConfig(username=username, password=password),
        ),
    )
    
    # Create the auth manager
    auth_manager = AuthManager(config.auth)

    # Test listing catalog categories
    print("\n=== Testing List Catalog Categories ===")
    category_id = test_list_catalog_categories(config, auth_manager)

    # Test listing catalog items
    print("\n=== Testing List Catalog Items ===")
    item_id = test_list_catalog_items(config, auth_manager, category_id)

    # Test getting a specific catalog item
    if item_id:
        print("\n=== Testing Get Catalog Item ===")
        test_get_catalog_item(config, auth_manager, item_id)


def test_list_catalog_categories(config, auth_manager):
    """Test listing catalog categories."""
    print("Fetching catalog categories...")
    
    # Create the parameters
    params = ListCatalogCategoriesParams(
        limit=5,
        offset=0,
        query="",
        active=True,
    )

    # Call the tool function directly
    result = list_catalog_categories(config, auth_manager, params)
    
    # Print the result
    print(f"Found {result.get('total', 0)} catalog categories:")
    for i, category in enumerate(result.get("categories", []), 1):
        print(f"{i}. {category.get('title')} (ID: {category.get('sys_id')})")
        print(f"   Description: {category.get('description', 'N/A')}")
        print()
    
    # Save the first category ID for later use
    if result.get("categories"):
        return result["categories"][0]["sys_id"]
    return None


def test_list_catalog_items(config, auth_manager, category_id=None):
    """Test listing catalog items."""
    print("Fetching catalog items...")
    
    # Create the parameters
    params = ListCatalogItemsParams(
        limit=5,
        offset=0,
        query="",
        category=category_id,  # Filter by category if provided
        active=True,
    )

    # Call the tool function directly
    result = list_catalog_items(config, auth_manager, params)
    
    # Print the result
    print(f"Found {result.get('total', 0)} catalog items:")
    for i, item in enumerate(result.get("items", []), 1):
        print(f"{i}. {item.get('name')} (ID: {item.get('sys_id')})")
        print(f"   Description: {item.get('short_description', 'N/A')}")
        print(f"   Category: {item.get('category', 'N/A')}")
        print(f"   Price: {item.get('price', 'N/A')}")
        print()
    
    # Save the first item ID for later use
    if result.get("items"):
        return result["items"][0]["sys_id"]
    return None


def test_get_catalog_item(config, auth_manager, item_id):
    """Test getting a specific catalog item."""
    print(f"Fetching details for catalog item: {item_id}")
    
    # Create the parameters
    params = GetCatalogItemParams(
        item_id=item_id,
    )

    # Call the tool function directly
    result = get_catalog_item(config, auth_manager, params)
    
    # Print the result
    if result.success:
        print(f"Retrieved catalog item: {result.data.get('name')} (ID: {result.data.get('sys_id')})")
        print(f"Description: {result.data.get('description', 'N/A')}")
        print(f"Category: {result.data.get('category', 'N/A')}")
        print(f"Price: {result.data.get('price', 'N/A')}")
        print(f"Delivery Time: {result.data.get('delivery_time', 'N/A')}")
        print(f"Availability: {result.data.get('availability', 'N/A')}")
        
        # Print variables
        variables = result.data.get("variables", [])
        if variables:
            print("\nVariables:")
            for i, variable in enumerate(variables, 1):
                print(f"{i}. {variable.get('label')} ({variable.get('name')})")
                print(f"   Type: {variable.get('type')}")
                print(f"   Mandatory: {variable.get('mandatory')}")
                print(f"   Default Value: {variable.get('default_value', 'N/A')}")
                print()
    else:
        print(f"Error: {result.message}")


if __name__ == "__main__":
    main() 