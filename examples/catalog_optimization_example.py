#!/usr/bin/env python3
"""
Catalog Optimization Example

This script demonstrates how to use the catalog optimization tools to analyze
and optimize a ServiceNow service catalog.
"""

import argparse
import os
import sys

from dotenv import load_dotenv

# Add the src directory to the path so we can import the modules
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from servicenow_mcp.auth.auth_manager import AuthManager
from servicenow_mcp.tools.catalog_optimization import (
    OptimizationRecommendationsParams,
    UpdateCatalogItemParams,
    get_optimization_recommendations,
    update_catalog_item,
)
from servicenow_mcp.utils.config import AuthConfig, AuthType, BasicAuthConfig, ServerConfig


def main():
    """Run the catalog optimization example."""
    parser = argparse.ArgumentParser(description="Catalog Optimization Example")
    parser.add_argument(
        "--instance-url",
        help="ServiceNow instance URL",
        default=os.getenv("SERVICENOW_INSTANCE_URL"),
    )
    parser.add_argument(
        "--username",
        help="ServiceNow username",
        default=os.getenv("SERVICENOW_USERNAME"),
    )
    parser.add_argument(
        "--password",
        help="ServiceNow password",
        default=os.getenv("SERVICENOW_PASSWORD"),
    )
    parser.add_argument(
        "--category",
        help="Filter by category ID",
        default=None,
    )
    parser.add_argument(
        "--recommendation-types",
        help="Types of recommendations to include (comma-separated)",
        default="inactive_items,low_usage,high_abandonment,slow_fulfillment,description_quality",
    )
    parser.add_argument(
        "--update-descriptions",
        help="Automatically update poor descriptions",
        action="store_true",
    )
    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Check for required arguments
    if not args.instance_url:
        print("Error: ServiceNow instance URL is required")
        sys.exit(1)
    if not args.username:
        print("Error: ServiceNow username is required")
        sys.exit(1)
    if not args.password:
        print("Error: ServiceNow password is required")
        sys.exit(1)

    # Create server configuration
    auth_config = AuthConfig(
        type=AuthType.BASIC,
        basic=BasicAuthConfig(username=args.username, password=args.password),
    )
    config = ServerConfig(instance_url=args.instance_url, auth=auth_config)
    auth_manager = AuthManager(config.auth)

    # Parse recommendation types
    recommendation_types = args.recommendation_types.split(",")

    # Get optimization recommendations
    print("\n=== Getting Catalog Optimization Recommendations ===\n")
    params = OptimizationRecommendationsParams(
        category_id=args.category,
        recommendation_types=recommendation_types,
    )
    result = get_optimization_recommendations(config, auth_manager, params)

    if not result["success"]:
        print(f"Error: {result['message']}")
        sys.exit(1)

    # Print the recommendations
    recommendations = result["recommendations"]
    print(f"Found {len(recommendations)} optimization recommendations:\n")

    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['title']}")
        print(f"   Impact: {rec['impact']}, Effort: {rec['effort']}")
        print(f"   {rec['description']}")
        print(f"   Recommended Action: {rec['action']}")
        print(f"   Affected Items: {len(rec['items'])}")

        # Print a few example items
        for j, item in enumerate(rec["items"][:3], 1):
            print(f"     {j}. {item.get('name', 'Unknown')} - {item.get('short_description', 'No description')}")
            
            # Print additional details based on recommendation type
            if rec["type"] == "low_usage":
                print(f"        Order Count: {item.get('order_count', 'Unknown')}")
            elif rec["type"] == "high_abandonment":
                print(f"        Abandonment Rate: {item.get('abandonment_rate', 'Unknown')}%")
                print(f"        Cart Adds: {item.get('cart_adds', 'Unknown')}, Orders: {item.get('orders', 'Unknown')}")
            elif rec["type"] == "slow_fulfillment":
                print(f"        Avg. Fulfillment Time: {item.get('avg_fulfillment_time', 'Unknown')} days")
                print(f"        vs. Catalog Avg: {item.get('avg_fulfillment_time_vs_catalog', 'Unknown')}x slower")
            elif rec["type"] == "description_quality":
                print(f"        Quality Score: {item.get('description_quality', 'Unknown')}/100")
                print(f"        Issues: {', '.join(item.get('quality_issues', ['Unknown']))}")
                
        if len(rec["items"]) > 3:
            print(f"     ... and {len(rec['items']) - 3} more items")
        print()

    # Automatically update poor descriptions if requested
    if args.update_descriptions and any(rec["type"] == "description_quality" for rec in recommendations):
        print("\n=== Automatically Updating Poor Descriptions ===\n")
        
        # Find the description quality recommendation
        for rec in recommendations:
            if rec["type"] == "description_quality":
                poor_description_items = rec["items"]
                break
        
        # Update each item with a poor description
        for item in poor_description_items:
            item_id = item.get("sys_id")
            name = item.get("name", "Unknown")
            old_description = item.get("short_description", "")
            
            # Generate an improved description
            if not old_description:
                new_description = f"A {name} service that provides users with the ability to request {name.lower()} related services."
            elif len(old_description) < 30:
                new_description = f"{old_description} This service provides comprehensive {name.lower()} functionality for users."
            else:
                # Just make it longer by adding more context
                new_description = f"{old_description} This service is designed to meet organizational needs for {name.lower()}."
            
            print(f"Updating description for '{name}':")
            print(f"  Old: {old_description}")
            print(f"  New: {new_description}")
            
            # Update the item
            update_params = UpdateCatalogItemParams(
                item_id=item_id,
                short_description=new_description,
            )
            update_result = update_catalog_item(config, auth_manager, update_params)
            
            if update_result["success"]:
                print(f"  Result: Success\n")
            else:
                print(f"  Result: Failed - {update_result['message']}\n")


if __name__ == "__main__":
    main() 