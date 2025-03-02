#!/usr/bin/env python3
"""
Example script demonstrating how to use the ServiceNow MCP catalog optimization tools.

This script shows how to:
1. Get optimization recommendations for a ServiceNow Service Catalog
2. Update catalog items with improved descriptions

Usage:
    python catalog_optimization_example.py [--update-descriptions]

Options:
    --update-descriptions    Automatically update items with poor descriptions
"""

import argparse
import logging
import sys
from typing import Dict

from servicenow_mcp.server import ServiceNowMCP
from servicenow_mcp.tools.catalog_optimization import (
    OptimizationRecommendationsParams,
    UpdateCatalogItemParams,
)
from servicenow_mcp.utils.config import load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_optimization_recommendations(server: ServiceNowMCP) -> Dict:
    """
    Get optimization recommendations for the ServiceNow Service Catalog.
    
    Args:
        server: The ServiceNowMCP server instance
        
    Returns:
        Dict containing the optimization recommendations
    """
    logger.info("Getting catalog optimization recommendations...")
    
    # Create parameters for all recommendation types
    params = OptimizationRecommendationsParams(
        recommendation_types=[
            "inactive_items",
            "low_usage",
            "high_abandonment",
            "slow_fulfillment",
            "description_quality",
        ]
    )
    
    # Call the tool
    result = server.tools["get_optimization_recommendations"](params)
    
    if not result["success"]:
        logger.error(f"Failed to get optimization recommendations: {result.get('message', 'Unknown error')}")
        return {}
    
    return result


def print_recommendations(recommendations: Dict) -> None:
    """
    Print the optimization recommendations in a readable format.
    
    Args:
        recommendations: The optimization recommendations dictionary
    """
    if not recommendations or "recommendations" not in recommendations:
        logger.warning("No recommendations available")
        return
    
    print("\n" + "=" * 80)
    print("SERVICENOW CATALOG OPTIMIZATION RECOMMENDATIONS")
    print("=" * 80)
    
    for rec in recommendations["recommendations"]:
        print(f"\n{rec['title']} ({rec['type']})")
        print("-" * len(rec['title']))
        print(f"Description: {rec['description']}")
        print(f"Impact: {rec['impact'].upper()}")
        print(f"Effort: {rec['effort'].upper()}")
        print(f"Recommended Action: {rec['action']}")
        
        if rec["items"]:
            print("\nAffected Items:")
            for i, item in enumerate(rec["items"], 1):
                print(f"  {i}. {item['name']}")
                print(f"     ID: {item['sys_id']}")
                print(f"     Description: {item['short_description'] or '(No description)'}")
                
                # Print additional details based on recommendation type
                if rec["type"] == "low_usage":
                    print(f"     Order Count: {item['order_count']}")
                elif rec["type"] == "high_abandonment":
                    print(f"     Abandonment Rate: {item['abandonment_rate']}%")
                    print(f"     Cart Adds: {item['cart_adds']}")
                    print(f"     Completed Orders: {item['orders']}")
                elif rec["type"] == "slow_fulfillment":
                    print(f"     Avg. Fulfillment Time: {item['avg_fulfillment_time']} days")
                    print(f"     Compared to Catalog Avg: {item['avg_fulfillment_time_vs_catalog']}x slower")
                elif rec["type"] == "description_quality":
                    print(f"     Description Quality Score: {item['description_quality']}/100")
                    print(f"     Issues: {', '.join(item['quality_issues'])}")
                
                print()
        else:
            print("\nNo items found in this category.")
    
    print("=" * 80)


def update_poor_descriptions(server: ServiceNowMCP, recommendations: Dict) -> None:
    """
    Update catalog items with poor descriptions.
    
    Args:
        server: The ServiceNowMCP server instance
        recommendations: The optimization recommendations dictionary
    """
    # Find the description quality recommendation
    description_rec = None
    for rec in recommendations.get("recommendations", []):
        if rec["type"] == "description_quality":
            description_rec = rec
            break
    
    if not description_rec or not description_rec.get("items"):
        logger.warning("No items with poor descriptions found")
        return
    
    logger.info(f"Found {len(description_rec['items'])} items with poor descriptions")
    
    # Update each item with a better description
    for item in description_rec["items"]:
        # Generate an improved description based on the item name and category
        improved_description = generate_improved_description(item)
        
        logger.info(f"Updating description for item: {item['name']} (ID: {item['sys_id']})")
        logger.info(f"  Original: {item['short_description'] or '(No description)'}")
        logger.info(f"  Improved: {improved_description}")
        
        # Create parameters for updating the item
        params = UpdateCatalogItemParams(
            item_id=item["sys_id"],
            short_description=improved_description,
        )
        
        # Call the tool
        result = server.tools["update_catalog_item"](params)
        
        if result["success"]:
            logger.info(f"Successfully updated description for {item['name']}")
        else:
            logger.error(f"Failed to update description: {result.get('message', 'Unknown error')}")


def generate_improved_description(item: Dict) -> str:
    """
    Generate an improved description for a catalog item.
    
    In a real implementation, this could use AI to generate better descriptions,
    but for this example we'll use a simple template-based approach.
    
    Args:
        item: The catalog item dictionary
        
    Returns:
        An improved description string
    """
    name = item["name"]
    category = item.get("category", "").lower()
    
    # Simple templates based on category
    if "hardware" in category:
        return f"Enterprise-grade {name.lower()} for professional use. Includes standard warranty and IT support."
    elif "software" in category:
        return f"Licensed {name.lower()} application with full feature set. Includes installation support."
    elif "service" in category:
        return f"Professional {name.lower()} service delivered by our expert team. Includes consultation and implementation."
    else:
        return f"High-quality {name.lower()} available through IT self-service. Contact the service desk for assistance."


def main():
    """Main function to run the example."""
    parser = argparse.ArgumentParser(description="ServiceNow Catalog Optimization Example")
    parser.add_argument(
        "--update-descriptions",
        action="store_true",
        help="Automatically update items with poor descriptions",
    )
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_config()
        
        # Initialize the ServiceNow MCP server
        server = ServiceNowMCP(config)
        
        # Get optimization recommendations
        recommendations = get_optimization_recommendations(server)
        
        # Print the recommendations
        print_recommendations(recommendations)
        
        # Update poor descriptions if requested
        if args.update_descriptions and recommendations:
            update_poor_descriptions(server, recommendations)
    
    except Exception as e:
        logger.exception(f"Error running catalog optimization example: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 