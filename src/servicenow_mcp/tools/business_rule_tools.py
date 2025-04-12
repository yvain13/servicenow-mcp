"""
Business Rule tools for the ServiceNow MCP server.

This module provides tools for managing business rules in ServiceNow.
"""

import logging
from typing import Any, Dict, Optional, List

import requests
from pydantic import BaseModel, Field

from servicenow_mcp.auth.auth_manager import AuthManager
from servicenow_mcp.utils.config import ServerConfig

logger = logging.getLogger(__name__)


class ListBusinessRulesParams(BaseModel):
    """Parameters for listing business rules."""
    
    limit: int = Field(10, description="Maximum number of business rules to return")
    offset: int = Field(0, description="Offset for pagination")
    active: Optional[bool] = Field(None, description="Filter by active status")
    collection: Optional[str] = Field(None, description="Filter by table name")
    query: Optional[str] = Field(None, description="Search query for business rules")


class GetBusinessRuleParams(BaseModel):
    """Parameters for getting a business rule."""
    
    business_rule_id: str = Field(..., description="Business rule ID or name")


class CreateBusinessRuleParams(BaseModel):
    """Parameters for creating a business rule."""
    
    name: str = Field(..., description="Name of the business rule")
    collection: str = Field(..., description="Table name this business rule applies to")
    script: str = Field(..., description="Script content")
    description: Optional[str] = Field(None, description="Description of the business rule")
    active: bool = Field(True, description="Whether the business rule is active")
    advanced: bool = Field(False, description="Whether this is an advanced business rule")
    action_insert: bool = Field(False, description="Whether the business rule runs on insert")
    action_update: bool = Field(False, description="Whether the business rule runs on update")
    action_delete: bool = Field(False, description="Whether the business rule runs on delete")
    action_query: bool = Field(False, description="Whether the business rule runs on query")
    order: int = Field(100, description="Execution order of the business rule")
    priority: str = Field("100", description="Priority of the business rule")


class UpdateBusinessRuleParams(BaseModel):
    """Parameters for updating a business rule."""
    
    business_rule_id: str = Field(..., description="Business rule ID or name")
    name: Optional[str] = Field(None, description="Name of the business rule")
    collection: Optional[str] = Field(None, description="Table name this business rule applies to")
    script: Optional[str] = Field(None, description="Script content")
    description: Optional[str] = Field(None, description="Description of the business rule")
    active: Optional[bool] = Field(None, description="Whether the business rule is active")
    advanced: Optional[bool] = Field(None, description="Whether this is an advanced business rule")
    action_insert: Optional[bool] = Field(None, description="Whether the business rule runs on insert")
    action_update: Optional[bool] = Field(None, description="Whether the business rule runs on update")
    action_delete: Optional[bool] = Field(None, description="Whether the business rule runs on delete")
    action_query: Optional[bool] = Field(None, description="Whether the business rule runs on query")
    order: Optional[int] = Field(None, description="Execution order of the business rule")
    priority: Optional[str] = Field(None, description="Priority of the business rule")


class DeleteBusinessRuleParams(BaseModel):
    """Parameters for deleting a business rule."""
    
    business_rule_id: str = Field(..., description="Business rule ID or name")


class BusinessRuleResponse(BaseModel):
    """Response from business rule operations."""
    
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Message describing the result")
    business_rule_id: Optional[str] = Field(None, description="ID of the affected business rule")
    business_rule_name: Optional[str] = Field(None, description="Name of the affected business rule")


def list_business_rules(
    config: ServerConfig,
    auth_manager: AuthManager,
    params: ListBusinessRulesParams,
) -> Dict[str, Any]:
    """List business rules from ServiceNow.
    
    Args:
        config: The server configuration.
        auth_manager: The authentication manager.
        params: The parameters for the request.
        
    Returns:
        A dictionary containing the list of business rules.
    """
    try:
        # Build the URL
        url = f"{config.instance_url}/api/now/table/sys_script"
        
        # Build query parameters
        query_params = {
            "sysparm_limit": params.limit,
            "sysparm_offset": params.offset,
            "sysparm_display_value": "true",
            "sysparm_exclude_reference_link": "true",
            "sysparm_fields": "sys_id,name,collection,script,description,active,advanced,action_insert,action_update,action_delete,action_query,order,priority,sys_created_on,sys_updated_on,sys_created_by,sys_updated_by"
        }
        
        # Add filters if provided
        query_parts = []
        
        if params.active is not None:
            query_parts.append(f"active={str(params.active).lower()}")
            
        if params.collection:
            query_parts.append(f"collection={params.collection}")
            
        if params.query:
            query_parts.append(f"nameLIKE{params.query}")
            
        if query_parts:
            query_params["sysparm_query"] = "^".join(query_parts)
            
        # Make the request
        headers = auth_manager.get_headers()
        
        response = requests.get(
            url,
            params=query_params,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        business_rules = []
        
        for item in data.get("result", []):
            business_rule = {
                "sys_id": item.get("sys_id"),
                "name": item.get("name"),
                "collection": item.get("collection"),
                "description": item.get("description"),
                "active": item.get("active") == "true",
                "advanced": item.get("advanced") == "true",
                "action_insert": item.get("action_insert") == "true",
                "action_update": item.get("action_update") == "true",
                "action_delete": item.get("action_delete") == "true",
                "action_query": item.get("action_query") == "true",
                "order": item.get("order"),
                "priority": item.get("priority"),
                "created_on": item.get("sys_created_on"),
                "updated_on": item.get("sys_updated_on"),
                "created_by": item.get("sys_created_by", {}).get("display_value"),
                "updated_by": item.get("sys_updated_by", {}).get("display_value"),
            }
            business_rules.append(business_rule)
            
        return {
            "success": True,
            "message": f"Found {len(business_rules)} business rules",
            "business_rules": business_rules,
            "total": len(business_rules),
            "limit": params.limit,
            "offset": params.offset,
        }
        
    except Exception as e:
        logger.error(f"Error listing business rules: {e}")
        return {
            "success": False,
            "message": f"Error listing business rules: {str(e)}",
            "business_rules": [],
            "total": 0,
            "limit": params.limit,
            "offset": params.offset,
        }


def get_business_rule(
    config: ServerConfig,
    auth_manager: AuthManager,
    params: GetBusinessRuleParams,
) -> Dict[str, Any]:
    """Get a specific business rule from ServiceNow.
    
    Args:
        config: The server configuration.
        auth_manager: The authentication manager.
        params: The parameters for the request.
        
    Returns:
        A dictionary containing the business rule data.
    """
    try:
        # Build query parameters
        query_params = {
            "sysparm_display_value": "true",
            "sysparm_exclude_reference_link": "true",
            "sysparm_fields": "sys_id,name,collection,script,description,active,advanced,action_insert,action_update,action_delete,action_query,order,priority,sys_created_on,sys_updated_on,sys_created_by,sys_updated_by"
        }
        
        # Determine if we're querying by sys_id or name
        if params.business_rule_id.startswith("sys_id:"):
            sys_id = params.business_rule_id.replace("sys_id:", "")
            url = f"{config.instance_url}/api/now/table/sys_script/{sys_id}"
        else:
            # Query by name
            url = f"{config.instance_url}/api/now/table/sys_script"
            query_params["sysparm_query"] = f"name={params.business_rule_id}"
            
        # Make the request
        headers = auth_manager.get_headers()
        
        response = requests.get(
            url,
            params=query_params,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        
        if "result" not in data or (isinstance(data["result"], list) and len(data["result"]) == 0):
            return {
                "success": False,
                "message": f"Business rule '{params.business_rule_id}' not found",
                "business_rule": None,
            }
            
        # Handle single result or list with one item
        result = data["result"]
        if isinstance(result, list):
            if len(result) == 0:
                return {
                    "success": False,
                    "message": f"Business rule '{params.business_rule_id}' not found",
                    "business_rule": None,
                }
            item = result[0]
        else:
            item = result
            
        business_rule = {
            "sys_id": item.get("sys_id"),
            "name": item.get("name"),
            "collection": item.get("collection"),
            "script": item.get("script"),
            "description": item.get("description"),
            "active": item.get("active") == "true",
            "advanced": item.get("advanced") == "true",
            "action_insert": item.get("action_insert") == "true",
            "action_update": item.get("action_update") == "true",
            "action_delete": item.get("action_delete") == "true",
            "action_query": item.get("action_query") == "true",
            "order": item.get("order"),
            "priority": item.get("priority"),
            "created_on": item.get("sys_created_on"),
            "updated_on": item.get("sys_updated_on"),
            "created_by": item.get("sys_created_by", {}).get("display_value"),
            "updated_by": item.get("sys_updated_by", {}).get("display_value"),
        }
            
        return {
            "success": True,
            "message": f"Found business rule '{business_rule['name']}'",
            "business_rule": business_rule,
        }
        
    except Exception as e:
        logger.error(f"Error getting business rule: {e}")
        return {
            "success": False,
            "message": f"Error getting business rule: {str(e)}",
            "business_rule": None,
        }


def create_business_rule(
    config: ServerConfig,
    auth_manager: AuthManager,
    params: CreateBusinessRuleParams,
) -> BusinessRuleResponse:
    """Create a new business rule in ServiceNow.
    
    Args:
        config: The server configuration.
        auth_manager: The authentication manager.
        params: The parameters for the request.
        
    Returns:
        A response indicating the result of the operation.
    """
    try:
        # Check if a business rule with this name already exists
        check_params = GetBusinessRuleParams(business_rule_id=params.name)
        result = get_business_rule(config, auth_manager, check_params)
        
        if result.get("success") and result.get("business_rule"):
            return BusinessRuleResponse(
                success=False,
                message=f"Business rule with name '{params.name}' already exists",
                business_rule_id=result["business_rule"]["sys_id"],
                business_rule_name=params.name,
            )
            
        # Build the URL
        url = f"{config.instance_url}/api/now/table/sys_script"
        
        # Build the payload
        payload = {
            "name": params.name,
            "collection": params.collection,
            "script": params.script,
            "active": str(params.active).lower(),
            "advanced": str(params.advanced).lower(),
            "action_insert": str(params.action_insert).lower(),
            "action_update": str(params.action_update).lower(),
            "action_delete": str(params.action_delete).lower(),
            "action_query": str(params.action_query).lower(),
            "order": params.order,
            "priority": params.priority,
        }
        
        if params.description:
            payload["description"] = params.description
            
        # Make the request
        headers = auth_manager.get_headers()
        
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        
        # Parse the response
        data = response.json()
        result = data.get("result", {})
        
        return BusinessRuleResponse(
            success=True,
            message=f"Created business rule '{params.name}'",
            business_rule_id=result.get("sys_id"),
            business_rule_name=params.name,
        )
        
    except Exception as e:
        logger.error(f"Error creating business rule: {e}")
        return BusinessRuleResponse(
            success=False,
            message=f"Error creating business rule: {str(e)}",
        )


def update_business_rule(
    config: ServerConfig,
    auth_manager: AuthManager,
    params: UpdateBusinessRuleParams,
) -> BusinessRuleResponse:
    """Update an existing business rule in ServiceNow.
    
    Args:
        config: The server configuration.
        auth_manager: The authentication manager.
        params: The parameters for the request.
        
    Returns:
        A response indicating the result of the operation.
    """
    try:
        # Find the business rule first
        get_params = GetBusinessRuleParams(business_rule_id=params.business_rule_id)
        result = get_business_rule(config, auth_manager, get_params)
        
        if not result.get("success") or not result.get("business_rule"):
            return BusinessRuleResponse(
                success=False,
                message=f"Business rule '{params.business_rule_id}' not found",
            )
            
        business_rule = result["business_rule"]
        sys_id = business_rule["sys_id"]
        
        # Build the URL
        url = f"{config.instance_url}/api/now/table/sys_script/{sys_id}"
        
        # Build the payload
        payload = {}
        
        if params.name is not None:
            payload["name"] = params.name
            
        if params.collection is not None:
            payload["collection"] = params.collection
            
        if params.script is not None:
            payload["script"] = params.script
            
        if params.description is not None:
            payload["description"] = params.description
            
        if params.active is not None:
            payload["active"] = str(params.active).lower()
            
        if params.advanced is not None:
            payload["advanced"] = str(params.advanced).lower()
            
        if params.action_insert is not None:
            payload["action_insert"] = str(params.action_insert).lower()
            
        if params.action_update is not None:
            payload["action_update"] = str(params.action_update).lower()
            
        if params.action_delete is not None:
            payload["action_delete"] = str(params.action_delete).lower()
            
        if params.action_query is not None:
            payload["action_query"] = str(params.action_query).lower()
            
        if params.order is not None:
            payload["order"] = params.order
            
        if params.priority is not None:
            payload["priority"] = params.priority
            
        # Check if there are any changes
        if not payload:
            return BusinessRuleResponse(
                success=True,
                message=f"No changes to update for business rule '{business_rule['name']}'",
                business_rule_id=sys_id,
                business_rule_name=business_rule["name"],
            )
            
        # Make the request
        headers = auth_manager.get_headers()
        
        response = requests.patch(
            url,
            json=payload,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        
        # Get the updated name
        updated_name = params.name if params.name is not None else business_rule["name"]
        
        return BusinessRuleResponse(
            success=True,
            message=f"Updated business rule '{updated_name}'",
            business_rule_id=sys_id,
            business_rule_name=updated_name,
        )
        
    except Exception as e:
        logger.error(f"Error updating business rule: {e}")
        return BusinessRuleResponse(
            success=False,
            message=f"Error updating business rule: {str(e)}",
        )


def delete_business_rule(
    config: ServerConfig,
    auth_manager: AuthManager,
    params: DeleteBusinessRuleParams,
) -> BusinessRuleResponse:
    """Delete a business rule from ServiceNow.
    
    Args:
        config: The server configuration.
        auth_manager: The authentication manager.
        params: The parameters for the request.
        
    Returns:
        A response indicating the result of the operation.
    """
    try:
        # Find the business rule first
        get_params = GetBusinessRuleParams(business_rule_id=params.business_rule_id)
        result = get_business_rule(config, auth_manager, get_params)
        
        if not result.get("success") or not result.get("business_rule"):
            return BusinessRuleResponse(
                success=False,
                message=f"Business rule '{params.business_rule_id}' not found",
            )
            
        business_rule = result["business_rule"]
        sys_id = business_rule["sys_id"]
        name = business_rule["name"]
        
        # Build the URL
        url = f"{config.instance_url}/api/now/table/sys_script/{sys_id}"
        
        # Make the request
        headers = auth_manager.get_headers()
        
        response = requests.delete(
            url,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        
        return BusinessRuleResponse(
            success=True,
            message=f"Deleted business rule '{name}'",
            business_rule_id=sys_id,
            business_rule_name=name,
        )
        
    except Exception as e:
        logger.error(f"Error deleting business rule: {e}")
        return BusinessRuleResponse(
            success=False,
            message=f"Error deleting business rule: {str(e)}",
        )
