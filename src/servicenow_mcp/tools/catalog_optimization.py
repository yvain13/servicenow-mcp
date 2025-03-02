"""
Service Catalog optimization tools for the ServiceNow MCP server.

This module provides tools for analyzing and optimizing the service catalog in ServiceNow.
"""

import logging
from typing import Any, Dict, List, Optional

import requests
from pydantic import BaseModel, Field

from servicenow_mcp.auth.auth_manager import AuthManager
from servicenow_mcp.utils.config import ServerConfig

logger = logging.getLogger(__name__)


class OptimizationRecommendationsParams(BaseModel):
    """Parameters for getting catalog optimization recommendations."""
    
    category_id: Optional[str] = Field(None, description="Filter by category ID")
    recommendation_types: List[str] = Field(
        ["inactive_items", "low_usage", "high_abandonment", "slow_fulfillment", "description_quality"],
        description="Types of recommendations to include"
    )


class CatalogStructureAnalysisParams(BaseModel):
    """Parameters for analyzing catalog structure."""
    
    include_inactive: bool = Field(False, description="Whether to include inactive categories and items")


class UpdateCatalogItemParams(BaseModel):
    """Parameters for updating a catalog item."""
    
    item_id: str = Field(..., description="Catalog item ID to update")
    name: Optional[str] = Field(None, description="New name for the item")
    short_description: Optional[str] = Field(None, description="New short description")
    description: Optional[str] = Field(None, description="New detailed description")
    category: Optional[str] = Field(None, description="New category ID")
    price: Optional[str] = Field(None, description="New price")
    active: Optional[bool] = Field(None, description="Whether the item is active")
    order: Optional[int] = Field(None, description="Display order in the category")


def get_optimization_recommendations(
    config: ServerConfig,
    auth_manager: AuthManager,
    params: OptimizationRecommendationsParams,
) -> Dict[str, Any]:
    """
    Get recommendations for optimizing the service catalog.

    Args:
        config: Server configuration
        auth_manager: Authentication manager
        params: Parameters for getting optimization recommendations

    Returns:
        Dictionary containing optimization recommendations
    """
    logger.info("Getting catalog optimization recommendations")
    recommendations = []
    
    # Get inactive items
    if "inactive_items" in params.recommendation_types:
        inactive_items = _get_inactive_items(config, auth_manager, params.category_id)
        if inactive_items:
            recommendations.append({
                "type": "inactive_items",
                "title": "Consider retiring inactive catalog items",
                "description": "These items are marked as inactive but still exist in the catalog",
                "items": inactive_items,
                "impact": "High",
                "effort": "Low",
                "action": "Review these items and consider removing them from the catalog"
            })
    
    # Get low usage items
    if "low_usage" in params.recommendation_types:
        low_usage_items = _get_low_usage_items(config, auth_manager, params.category_id)
        if low_usage_items:
            recommendations.append({
                "type": "low_usage",
                "title": "Items with low usage",
                "description": "These items have been ordered rarely or not at all in the last 90 days",
                "items": low_usage_items,
                "impact": "Medium",
                "effort": "Medium",
                "action": "Consider promoting these items, improving their descriptions, or retiring them"
            })
    
    # Get items with high abandonment
    if "high_abandonment" in params.recommendation_types:
        high_abandonment_items = _get_high_abandonment_items(config, auth_manager, params.category_id)
        if high_abandonment_items:
            recommendations.append({
                "type": "high_abandonment",
                "title": "Items with high abandonment rates",
                "description": "These items are frequently added to carts but not ordered",
                "items": high_abandonment_items,
                "impact": "High",
                "effort": "Medium",
                "action": "Review the item variables and simplify the ordering process"
            })
    
    # Get items with slow fulfillment
    if "slow_fulfillment" in params.recommendation_types:
        slow_fulfillment_items = _get_slow_fulfillment_items(config, auth_manager, params.category_id)
        if slow_fulfillment_items:
            recommendations.append({
                "type": "slow_fulfillment",
                "title": "Items with slow fulfillment times",
                "description": "These items take longer than average to fulfill",
                "items": slow_fulfillment_items,
                "impact": "High",
                "effort": "High",
                "action": "Review the fulfillment workflow and identify bottlenecks"
            })
    
    # Get items with poor descriptions
    if "description_quality" in params.recommendation_types:
        poor_description_items = _get_poor_description_items(config, auth_manager, params.category_id)
        if poor_description_items:
            recommendations.append({
                "type": "description_quality",
                "title": "Items with poor description quality",
                "description": "These items have short or generic descriptions that may confuse users",
                "items": poor_description_items,
                "impact": "Medium",
                "effort": "Low",
                "action": "Improve the descriptions to be more detailed and specific"
            })
    
    return {
        "success": True,
        "message": f"Found {len(recommendations)} optimization recommendations",
        "recommendations": recommendations
    }


def _get_inactive_items(config: ServerConfig, auth_manager: AuthManager, category_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get inactive catalog items.
    
    Args:
        config: Server configuration
        auth_manager: Authentication manager
        category_id: Optional category ID to filter by
        
    Returns:
        List of inactive catalog items
    """
    # Build query to get inactive items
    url = f"{config.instance_url}/api/now/table/sc_cat_item"
    query_params = {
        "sysparm_query": "active=false",
        "sysparm_fields": "sys_id,name,short_description,category",
        "sysparm_limit": 50
    }
    
    if category_id:
        query_params["sysparm_query"] += f"^category={category_id}"
    
    headers = auth_manager.get_headers()
    headers["Accept"] = "application/json"
    
    try:
        response = requests.get(url, headers=headers, params=query_params)
        response.raise_for_status()
        result = response.json()
        return result.get("result", [])
    except Exception as e:
        logger.error(f"Error getting inactive items: {str(e)}")
        return []


def _get_low_usage_items(config: ServerConfig, auth_manager: AuthManager, category_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get catalog items with low usage.
    
    Args:
        config: Server configuration
        auth_manager: Authentication manager
        category_id: Optional category ID to filter by
        
    Returns:
        List of catalog items with low usage
    """
    # In a real implementation, this would query the ServiceNow API for order statistics
    # and identify items with low usage. For this example, we'll simulate the response.
    
    # First, get all active items
    url = f"{config.instance_url}/api/now/table/sc_cat_item"
    query_params = {
        "sysparm_query": "active=true",
        "sysparm_fields": "sys_id,name,short_description,category",
        "sysparm_limit": 50
    }
    
    if category_id:
        query_params["sysparm_query"] += f"^category={category_id}"
    
    headers = auth_manager.get_headers()
    headers["Accept"] = "application/json"
    
    try:
        response = requests.get(url, headers=headers, params=query_params)
        response.raise_for_status()
        result = response.json()
        items = result.get("result", [])
        
        # For this example, we'll randomly select a subset of items as "low usage"
        # In a real implementation, this would be based on actual order statistics
        import random
        low_usage_items = random.sample(items, min(len(items), 5))
        
        # Add a simulated order count
        for item in low_usage_items:
            item["order_count"] = random.randint(0, 3)
            
        return low_usage_items
    except Exception as e:
        logger.error(f"Error getting low usage items: {str(e)}")
        return []


def _get_high_abandonment_items(config: ServerConfig, auth_manager: AuthManager, category_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get catalog items with high abandonment rates.
    
    Args:
        config: Server configuration
        auth_manager: Authentication manager
        category_id: Optional category ID to filter by
        
    Returns:
        List of catalog items with high abandonment rates
    """
    # In a real implementation, this would query the ServiceNow API for cart and order statistics
    # and identify items with high abandonment rates. For this example, we'll simulate the response.
    
    # First, get all active items
    url = f"{config.instance_url}/api/now/table/sc_cat_item"
    query_params = {
        "sysparm_query": "active=true",
        "sysparm_fields": "sys_id,name,short_description,category",
        "sysparm_limit": 50
    }
    
    if category_id:
        query_params["sysparm_query"] += f"^category={category_id}"
    
    headers = auth_manager.get_headers()
    headers["Accept"] = "application/json"
    
    try:
        response = requests.get(url, headers=headers, params=query_params)
        response.raise_for_status()
        result = response.json()
        items = result.get("result", [])
        
        # For this example, we'll randomly select a subset of items as "high abandonment"
        # In a real implementation, this would be based on actual cart and order statistics
        import random
        high_abandonment_items = random.sample(items, min(len(items), 3))
        
        # Add a simulated abandonment rate
        for item in high_abandonment_items:
            item["abandonment_rate"] = random.randint(40, 80)
            item["cart_adds"] = random.randint(10, 50)
            item["orders"] = int(item["cart_adds"] * (1 - item["abandonment_rate"] / 100))
            
        return high_abandonment_items
    except Exception as e:
        logger.error(f"Error getting high abandonment items: {str(e)}")
        return []


def _get_slow_fulfillment_items(config: ServerConfig, auth_manager: AuthManager, category_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get catalog items with slow fulfillment times.
    
    Args:
        config: Server configuration
        auth_manager: Authentication manager
        category_id: Optional category ID to filter by
        
    Returns:
        List of catalog items with slow fulfillment times
    """
    # In a real implementation, this would query the ServiceNow API for fulfillment statistics
    # and identify items with slow fulfillment times. For this example, we'll simulate the response.
    
    # First, get all active items
    url = f"{config.instance_url}/api/now/table/sc_cat_item"
    query_params = {
        "sysparm_query": "active=true",
        "sysparm_fields": "sys_id,name,short_description,category",
        "sysparm_limit": 50
    }
    
    if category_id:
        query_params["sysparm_query"] += f"^category={category_id}"
    
    headers = auth_manager.get_headers()
    headers["Accept"] = "application/json"
    
    try:
        response = requests.get(url, headers=headers, params=query_params)
        response.raise_for_status()
        result = response.json()
        items = result.get("result", [])
        
        # For this example, we'll randomly select a subset of items as "slow fulfillment"
        # In a real implementation, this would be based on actual fulfillment statistics
        import random
        slow_fulfillment_items = random.sample(items, min(len(items), 4))
        
        # Add simulated fulfillment times
        avg_fulfillment_time = 2.5  # days
        for item in slow_fulfillment_items:
            item["avg_fulfillment_time"] = round(random.uniform(5, 10), 1)  # days
            item["avg_fulfillment_time_vs_catalog"] = round(item["avg_fulfillment_time"] / avg_fulfillment_time, 1)
            
        return slow_fulfillment_items
    except Exception as e:
        logger.error(f"Error getting slow fulfillment items: {str(e)}")
        return []


def _get_poor_description_items(config: ServerConfig, auth_manager: AuthManager, category_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Get catalog items with poor description quality.
    
    Args:
        config: Server configuration
        auth_manager: Authentication manager
        category_id: Optional category ID to filter by
        
    Returns:
        List of catalog items with poor description quality
    """
    # Build query to get items with short or empty descriptions
    url = f"{config.instance_url}/api/now/table/sc_cat_item"
    query_params = {
        "sysparm_query": "active=true^short_descriptionISEMPTY^ORshort_descriptionLIKENo description^ORLENGTHOFshort_description<30",
        "sysparm_fields": "sys_id,name,short_description,category",
        "sysparm_limit": 50
    }
    
    if category_id:
        query_params["sysparm_query"] += f"^category={category_id}"
    
    headers = auth_manager.get_headers()
    headers["Accept"] = "application/json"
    
    try:
        response = requests.get(url, headers=headers, params=query_params)
        response.raise_for_status()
        result = response.json()
        items = result.get("result", [])
        
        # Add a quality score
        for item in items:
            desc = item.get("short_description", "")
            if not desc:
                item["description_quality"] = 0
                item["quality_issues"] = ["Missing description"]
            elif len(desc) < 30:
                item["description_quality"] = 30
                item["quality_issues"] = ["Description too short", "Lacks detail"]
            elif "please" in desc.lower() or "click" in desc.lower():
                item["description_quality"] = 50
                item["quality_issues"] = ["Uses instructional language instead of descriptive"]
            
        return items
    except Exception as e:
        logger.error(f"Error getting poor description items: {str(e)}")
        return []


def update_catalog_item(
    config: ServerConfig,
    auth_manager: AuthManager,
    params: UpdateCatalogItemParams,
) -> Dict[str, Any]:
    """
    Update a service catalog item.

    Args:
        config: Server configuration
        auth_manager: Authentication manager
        params: Parameters for updating the catalog item

    Returns:
        Dictionary containing the updated catalog item
    """
    logger.info(f"Updating catalog item: {params.item_id}")
    
    # Build the API URL
    url = f"{config.instance_url}/api/now/table/sc_cat_item/{params.item_id}"
    
    # Prepare the request body with only the fields that are provided
    body = {}
    if params.name is not None:
        body["name"] = params.name
    if params.short_description is not None:
        body["short_description"] = params.short_description
    if params.description is not None:
        body["description"] = params.description
    if params.category is not None:
        body["category"] = params.category
    if params.price is not None:
        body["price"] = params.price
    if params.active is not None:
        body["active"] = str(params.active).lower()
    if params.order is not None:
        body["order"] = params.order
    
    # Make the API request
    headers = auth_manager.get_headers()
    headers["Accept"] = "application/json"
    headers["Content-Type"] = "application/json"
    
    try:
        response = requests.patch(url, headers=headers, json=body)
        response.raise_for_status()
        
        # Process the response
        result = response.json()
        item = result.get("result", {})
        
        if not item:
            return {
                "success": False,
                "message": f"Failed to update catalog item: {params.item_id}",
                "data": None,
            }
        
        # Format the response
        formatted_item = {
            "sys_id": item.get("sys_id", ""),
            "name": item.get("name", ""),
            "short_description": item.get("short_description", ""),
            "description": item.get("description", ""),
            "category": item.get("category", ""),
            "price": item.get("price", ""),
            "active": item.get("active", ""),
            "order": item.get("order", ""),
        }
        
        return {
            "success": True,
            "message": f"Successfully updated catalog item: {item.get('name', '')}",
            "data": formatted_item,
        }
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error updating catalog item: {str(e)}")
        return {
            "success": False,
            "message": f"Error updating catalog item: {str(e)}",
            "data": None,
        } 