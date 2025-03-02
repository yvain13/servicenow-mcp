"""
Service Catalog resources for the ServiceNow MCP server.

This module provides resources for accessing service catalog data from ServiceNow.
"""

import logging
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp.resources import Resource
from pydantic import BaseModel, Field

from servicenow_mcp.auth.auth_manager import AuthManager
from servicenow_mcp.utils.config import ServerConfig

logger = logging.getLogger(__name__)


class CatalogItemModel(BaseModel):
    """Model representing a ServiceNow catalog item."""
    
    sys_id: str = Field(..., description="Unique identifier for the catalog item")
    name: str = Field(..., description="Name of the catalog item")
    short_description: Optional[str] = Field(None, description="Short description of the catalog item")
    description: Optional[str] = Field(None, description="Detailed description of the catalog item")
    category: Optional[str] = Field(None, description="Category of the catalog item")
    price: Optional[str] = Field(None, description="Price of the catalog item")
    picture: Optional[str] = Field(None, description="Picture URL of the catalog item")
    active: Optional[bool] = Field(None, description="Whether the catalog item is active")
    order: Optional[int] = Field(None, description="Order of the catalog item in its category")


class CatalogCategoryModel(BaseModel):
    """Model representing a ServiceNow catalog category."""
    
    sys_id: str = Field(..., description="Unique identifier for the category")
    title: str = Field(..., description="Title of the category")
    description: Optional[str] = Field(None, description="Description of the category")
    parent: Optional[str] = Field(None, description="Parent category ID")
    icon: Optional[str] = Field(None, description="Icon of the category")
    active: Optional[bool] = Field(None, description="Whether the category is active")
    order: Optional[int] = Field(None, description="Order of the category")


class CatalogItemVariableModel(BaseModel):
    """Model representing a ServiceNow catalog item variable."""
    
    sys_id: str = Field(..., description="Unique identifier for the variable")
    name: str = Field(..., description="Name of the variable")
    label: str = Field(..., description="Label of the variable")
    type: str = Field(..., description="Type of the variable")
    mandatory: Optional[bool] = Field(None, description="Whether the variable is mandatory")
    default_value: Optional[str] = Field(None, description="Default value of the variable")
    help_text: Optional[str] = Field(None, description="Help text for the variable")
    order: Optional[int] = Field(None, description="Order of the variable")


class CatalogListParams(BaseModel):
    """Parameters for listing catalog items."""
    
    limit: int = Field(10, description="Maximum number of items to return")
    offset: int = Field(0, description="Offset for pagination")
    category: Optional[str] = Field(None, description="Filter by category")
    query: Optional[str] = Field(None, description="Search query for items")


class CatalogCategoryListParams(BaseModel):
    """Parameters for listing catalog categories."""
    
    limit: int = Field(10, description="Maximum number of categories to return")
    offset: int = Field(0, description="Offset for pagination")
    query: Optional[str] = Field(None, description="Search query for categories")


class CatalogResource:
    """Resource for accessing ServiceNow service catalog."""

    def __init__(self, config: ServerConfig, auth_manager: AuthManager):
        """
        Initialize the catalog resource.

        Args:
            config: Server configuration
            auth_manager: Authentication manager
        """
        self.config = config
        self.auth_manager = auth_manager

    async def read(self, params: dict = None) -> dict:
        """
        Read a catalog item.

        Args:
            params: Parameters for reading a catalog item

        Returns:
            Dictionary containing the catalog item
        """
        if not params or "item_id" not in params:
            return {"error": "Missing item_id parameter"}

        item_id = params["item_id"]
        return await self.get_catalog_item(item_id)

    async def list_catalog_items(self, params: CatalogListParams) -> List[CatalogItemModel]:
        """
        List catalog items.

        Args:
            params: Parameters for listing catalog items

        Returns:
            List of catalog items
        """
        logger.info("Listing catalog items")
        
        # Build the API URL
        url = f"{self.config.instance_url}/api/now/table/sc_cat_item"
        
        # Prepare query parameters
        query_params = {
            "sysparm_limit": params.limit,
            "sysparm_offset": params.offset,
            "sysparm_display_value": "true",
            "sysparm_exclude_reference_link": "true",
        }
        
        # Add filters
        filters = ["active=true"]
        if params.category:
            filters.append(f"category={params.category}")
        if params.query:
            filters.append(f"short_descriptionLIKE{params.query}^ORnameLIKE{params.query}")
        
        if filters:
            query_params["sysparm_query"] = "^".join(filters)
        
        # Make the API request
        headers = self.auth_manager.get_headers()
        headers["Accept"] = "application/json"
        
        try:
            import requests
            response = requests.get(url, headers=headers, params=query_params)
            response.raise_for_status()
            
            # Process the response
            result = response.json()
            items = result.get("result", [])
            
            # Format the response
            catalog_items = []
            for item in items:
                catalog_items.append(
                    CatalogItemModel(
                        sys_id=item.get("sys_id", ""),
                        name=item.get("name", ""),
                        short_description=item.get("short_description", ""),
                        category=item.get("category", ""),
                        price=item.get("price", ""),
                        picture=item.get("picture", ""),
                        active=item.get("active", "") == "true",
                        order=int(item.get("order", "0")) if item.get("order") else None,
                    )
                )
            
            return catalog_items
        
        except Exception as e:
            logger.error(f"Error listing catalog items: {str(e)}")
            return []

    async def get_catalog_item(self, item_id: str) -> Dict[str, Any]:
        """
        Get a specific catalog item.

        Args:
            item_id: Catalog item ID or sys_id

        Returns:
            Dictionary containing the catalog item details
        """
        logger.info(f"Getting catalog item: {item_id}")
        
        # Build the API URL
        url = f"{self.config.instance_url}/api/now/table/sc_cat_item/{item_id}"
        
        # Prepare query parameters
        query_params = {
            "sysparm_display_value": "true",
            "sysparm_exclude_reference_link": "true",
        }
        
        # Make the API request
        headers = self.auth_manager.get_headers()
        headers["Accept"] = "application/json"
        
        try:
            import requests
            response = requests.get(url, headers=headers, params=query_params)
            response.raise_for_status()
            
            # Process the response
            result = response.json()
            item = result.get("result", {})
            
            if not item:
                return {"error": f"Catalog item not found: {item_id}"}
            
            # Get variables for the catalog item
            variables = await self.get_catalog_item_variables(item_id)
            
            # Format the response
            catalog_item = {
                "sys_id": item.get("sys_id", ""),
                "name": item.get("name", ""),
                "short_description": item.get("short_description", ""),
                "description": item.get("description", ""),
                "category": item.get("category", ""),
                "price": item.get("price", ""),
                "picture": item.get("picture", ""),
                "active": item.get("active", "") == "true",
                "order": int(item.get("order", "0")) if item.get("order") else None,
                "delivery_time": item.get("delivery_time", ""),
                "availability": item.get("availability", ""),
                "variables": variables,
            }
            
            return catalog_item
        
        except Exception as e:
            logger.error(f"Error getting catalog item: {str(e)}")
            return {"error": f"Error getting catalog item: {str(e)}"}

    async def get_catalog_item_variables(self, item_id: str) -> List[CatalogItemVariableModel]:
        """
        Get variables for a specific catalog item.

        Args:
            item_id: Catalog item ID or sys_id

        Returns:
            List of variables for the catalog item
        """
        logger.info(f"Getting variables for catalog item: {item_id}")
        
        # Build the API URL
        url = f"{self.config.instance_url}/api/now/table/item_option_new"
        
        # Prepare query parameters
        query_params = {
            "sysparm_query": f"cat_item={item_id}^ORDERBYorder",
            "sysparm_display_value": "true",
            "sysparm_exclude_reference_link": "true",
        }
        
        # Make the API request
        headers = self.auth_manager.get_headers()
        headers["Accept"] = "application/json"
        
        try:
            import requests
            response = requests.get(url, headers=headers, params=query_params)
            response.raise_for_status()
            
            # Process the response
            result = response.json()
            variables = result.get("result", [])
            
            # Format the response
            catalog_variables = []
            for variable in variables:
                catalog_variables.append(
                    CatalogItemVariableModel(
                        sys_id=variable.get("sys_id", ""),
                        name=variable.get("name", ""),
                        label=variable.get("question_text", ""),
                        type=variable.get("type", ""),
                        mandatory=variable.get("mandatory", "") == "true",
                        default_value=variable.get("default_value", ""),
                        help_text=variable.get("help_text", ""),
                        order=int(variable.get("order", "0")) if variable.get("order") else None,
                    )
                )
            
            return catalog_variables
        
        except Exception as e:
            logger.error(f"Error getting catalog item variables: {str(e)}")
            return []

    async def list_catalog_categories(self, params: CatalogCategoryListParams) -> List[CatalogCategoryModel]:
        """
        List catalog categories.

        Args:
            params: Parameters for listing catalog categories

        Returns:
            List of catalog categories
        """
        logger.info("Listing catalog categories")
        
        # Build the API URL
        url = f"{self.config.instance_url}/api/now/table/sc_category"
        
        # Prepare query parameters
        query_params = {
            "sysparm_limit": params.limit,
            "sysparm_offset": params.offset,
            "sysparm_display_value": "true",
            "sysparm_exclude_reference_link": "true",
        }
        
        # Add filters
        filters = ["active=true"]
        if params.query:
            filters.append(f"titleLIKE{params.query}^ORdescriptionLIKE{params.query}")
        
        if filters:
            query_params["sysparm_query"] = "^".join(filters)
        
        # Make the API request
        headers = self.auth_manager.get_headers()
        headers["Accept"] = "application/json"
        
        try:
            import requests
            response = requests.get(url, headers=headers, params=query_params)
            response.raise_for_status()
            
            # Process the response
            result = response.json()
            categories = result.get("result", [])
            
            # Format the response
            catalog_categories = []
            for category in categories:
                catalog_categories.append(
                    CatalogCategoryModel(
                        sys_id=category.get("sys_id", ""),
                        title=category.get("title", ""),
                        description=category.get("description", ""),
                        parent=category.get("parent", ""),
                        icon=category.get("icon", ""),
                        active=category.get("active", "") == "true",
                        order=int(category.get("order", "0")) if category.get("order") else None,
                    )
                )
            
            return catalog_categories
        
        except Exception as e:
            logger.error(f"Error listing catalog categories: {str(e)}")
            return [] 