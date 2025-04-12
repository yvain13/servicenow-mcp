"""
Client Script tools for the ServiceNow MCP server.

This module provides tools for managing client scripts in ServiceNow.
"""

import logging
from typing import Any, Dict, Optional, List

import requests
from pydantic import BaseModel, Field

from servicenow_mcp.auth.auth_manager import AuthManager
from servicenow_mcp.utils.config import ServerConfig

logger = logging.getLogger(__name__)


class ListClientScriptsParams(BaseModel):
    """Parameters for listing client scripts."""
    
    limit: int = Field(10, description="Maximum number of client scripts to return")
    offset: int = Field(0, description="Offset for pagination")
    active: Optional[bool] = Field(None, description="Filter by active status")
    table: Optional[str] = Field(None, description="Filter by table name")
    type: Optional[str] = Field(None, description="Filter by client script type")
    query: Optional[str] = Field(None, description="Search query for client scripts")


class GetClientScriptParams(BaseModel):
    """Parameters for getting a client script."""
    
    client_script_id: str = Field(..., description="Client script ID or name")


class CreateClientScriptParams(BaseModel):
    """Parameters for creating a client script."""
    
    name: str = Field(..., description="Name of the client script")
    table: str = Field(..., description="Table name this client script applies to")
    script: str = Field(..., description="Script content")
    type: str = Field(..., description="Type of client script (onLoad, onChange, onSubmit, etc.)")
    field_name: Optional[str] = Field(None, description="Field name (required for onChange and onDisplay)")
    description: Optional[str] = Field(None, description="Description of the client script")
    active: bool = Field(True, description="Whether the client script is active")
    global_scope: bool = Field(False, description="Whether the script runs in global scope")


class UpdateClientScriptParams(BaseModel):
    """Parameters for updating a client script."""
    
    client_script_id: str = Field(..., description="Client script ID or name")
    name: Optional[str] = Field(None, description="Name of the client script")
    table: Optional[str] = Field(None, description="Table name this client script applies to")
    script: Optional[str] = Field(None, description="Script content")
    type: Optional[str] = Field(None, description="Type of client script (onLoad, onChange, onSubmit, etc.)")
    field_name: Optional[str] = Field(None, description="Field name (required for onChange and onDisplay)")
    description: Optional[str] = Field(None, description="Description of the client script")
    active: Optional[bool] = Field(None, description="Whether the client script is active")
    global_scope: Optional[bool] = Field(None, description="Whether the script runs in global scope")


class DeleteClientScriptParams(BaseModel):
    """Parameters for deleting a client script."""
    
    client_script_id: str = Field(..., description="Client script ID or name")


class ClientScriptResponse(BaseModel):
    """Response from client script operations."""
    
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Message describing the result")
    client_script_id: Optional[str] = Field(None, description="ID of the affected client script")
    client_script_name: Optional[str] = Field(None, description="Name of the affected client script")


def list_client_scripts(
    config: ServerConfig,
    auth_manager: AuthManager,
    params: ListClientScriptsParams,
) -> Dict[str, Any]:
    """List client scripts from ServiceNow.
    
    Args:
        config: The server configuration.
        auth_manager: The authentication manager.
        params: The parameters for the request.
        
    Returns:
        A dictionary containing the list of client scripts.
    """
    try:
        # Build the URL
        url = f"{config.instance_url}/api/now/table/sys_script_client"
        
        # Build query parameters
        query_params = {
            "sysparm_limit": params.limit,
            "sysparm_offset": params.offset,
            "sysparm_display_value": "true",
            "sysparm_exclude_reference_link": "true",
            "sysparm_fields": "sys_id,name,table,script,type,field_name,description,active,global,sys_created_on,sys_updated_on,sys_created_by,sys_updated_by"
        }
        
        # Add filters if provided
        query_parts = []
        
        if params.active is not None:
            query_parts.append(f"active={str(params.active).lower()}")
            
        if params.table:
            query_parts.append(f"table={params.table}")
            
        if params.type:
            query_parts.append(f"type={params.type}")
            
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
        client_scripts = []
        
        for item in data.get("result", []):
            client_script = {
                "sys_id": item.get("sys_id"),
                "name": item.get("name"),
                "table": item.get("table"),
                "type": item.get("type"),
                "field_name": item.get("field_name"),
                "description": item.get("description"),
                "active": item.get("active") == "true",
                "global_scope": item.get("global") == "true",
                "created_on": item.get("sys_created_on"),
                "updated_on": item.get("sys_updated_on"),
                "created_by": item.get("sys_created_by", {}).get("display_value"),
                "updated_by": item.get("sys_updated_by", {}).get("display_value"),
            }
            client_scripts.append(client_script)
            
        return {
            "success": True,
            "message": f"Found {len(client_scripts)} client scripts",
            "client_scripts": client_scripts,
            "total": len(client_scripts),
            "limit": params.limit,
            "offset": params.offset,
        }
        
    except Exception as e:
        logger.error(f"Error listing client scripts: {e}")
        return {
            "success": False,
            "message": f"Error listing client scripts: {str(e)}",
            "client_scripts": [],
            "total": 0,
            "limit": params.limit,
            "offset": params.offset,
        }


def get_client_script(
    config: ServerConfig,
    auth_manager: AuthManager,
    params: GetClientScriptParams,
) -> Dict[str, Any]:
    """Get a specific client script from ServiceNow.
    
    Args:
        config: The server configuration.
        auth_manager: The authentication manager.
        params: The parameters for the request.
        
    Returns:
        A dictionary containing the client script data.
    """
    try:
        # Build query parameters
        query_params = {
            "sysparm_display_value": "true",
            "sysparm_exclude_reference_link": "true",
            "sysparm_fields": "sys_id,name,table,script,type,field_name,description,active,global,sys_created_on,sys_updated_on,sys_created_by,sys_updated_by"
        }
        
        # Determine if we're querying by sys_id or name
        if params.client_script_id.startswith("sys_id:"):
            sys_id = params.client_script_id.replace("sys_id:", "")
            url = f"{config.instance_url}/api/now/table/sys_script_client/{sys_id}"
        else:
            # Query by name
            url = f"{config.instance_url}/api/now/table/sys_script_client"
            query_params["sysparm_query"] = f"name={params.client_script_id}"
            
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
                "message": f"Client script '{params.client_script_id}' not found",
                "client_script": None,
            }
            
        # Handle single result or list with one item
        result = data["result"]
        if isinstance(result, list):
            if len(result) == 0:
                return {
                    "success": False,
                    "message": f"Client script '{params.client_script_id}' not found",
                    "client_script": None,
                }
            item = result[0]
        else:
            item = result
            
        client_script = {
            "sys_id": item.get("sys_id"),
            "name": item.get("name"),
            "table": item.get("table"),
            "script": item.get("script"),
            "type": item.get("type"),
            "field_name": item.get("field_name"),
            "description": item.get("description"),
            "active": item.get("active") == "true",
            "global_scope": item.get("global") == "true",
            "created_on": item.get("sys_created_on"),
            "updated_on": item.get("sys_updated_on"),
            "created_by": item.get("sys_created_by", {}).get("display_value"),
            "updated_by": item.get("sys_updated_by", {}).get("display_value"),
        }
            
        return {
            "success": True,
            "message": f"Found client script '{client_script['name']}'",
            "client_script": client_script,
        }
        
    except Exception as e:
        logger.error(f"Error getting client script: {e}")
        return {
            "success": False,
            "message": f"Error getting client script: {str(e)}",
            "client_script": None,
        }


def create_client_script(
    config: ServerConfig,
    auth_manager: AuthManager,
    params: CreateClientScriptParams,
) -> ClientScriptResponse:
    """Create a new client script in ServiceNow.
    
    Args:
        config: The server configuration.
        auth_manager: The authentication manager.
        params: The parameters for the request.
        
    Returns:
        A response indicating the result of the operation.
    """
    try:
        # Check if a client script with this name already exists
        check_params = GetClientScriptParams(client_script_id=params.name)
        result = get_client_script(config, auth_manager, check_params)
        
        if result.get("success") and result.get("client_script"):
            return ClientScriptResponse(
                success=False,
                message=f"Client script with name '{params.name}' already exists",
                client_script_id=result["client_script"]["sys_id"],
                client_script_name=params.name,
            )
            
        # Build the URL
        url = f"{config.instance_url}/api/now/table/sys_script_client"
        
        # Build the payload
        payload = {
            "name": params.name,
            "table": params.table,
            "script": params.script,
            "type": params.type,
            "active": str(params.active).lower(),
            "global": str(params.global_scope).lower(),
        }
        
        if params.field_name:
            payload["field_name"] = params.field_name
            
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
        
        return ClientScriptResponse(
            success=True,
            message=f"Created client script '{params.name}'",
            client_script_id=result.get("sys_id"),
            client_script_name=params.name,
        )
        
    except Exception as e:
        logger.error(f"Error creating client script: {e}")
        return ClientScriptResponse(
            success=False,
            message=f"Error creating client script: {str(e)}",
        )


def update_client_script(
    config: ServerConfig,
    auth_manager: AuthManager,
    params: UpdateClientScriptParams,
) -> ClientScriptResponse:
    """Update an existing client script in ServiceNow.
    
    Args:
        config: The server configuration.
        auth_manager: The authentication manager.
        params: The parameters for the request.
        
    Returns:
        A response indicating the result of the operation.
    """
    try:
        # Find the client script first
        get_params = GetClientScriptParams(client_script_id=params.client_script_id)
        result = get_client_script(config, auth_manager, get_params)
        
        if not result.get("success") or not result.get("client_script"):
            return ClientScriptResponse(
                success=False,
                message=f"Client script '{params.client_script_id}' not found",
            )
            
        client_script = result["client_script"]
        sys_id = client_script["sys_id"]
        
        # Build the URL
        url = f"{config.instance_url}/api/now/table/sys_script_client/{sys_id}"
        
        # Build the payload
        payload = {}
        
        if params.name is not None:
            payload["name"] = params.name
            
        if params.table is not None:
            payload["table"] = params.table
            
        if params.script is not None:
            payload["script"] = params.script
            
        if params.type is not None:
            payload["type"] = params.type
            
        if params.field_name is not None:
            payload["field_name"] = params.field_name
            
        if params.description is not None:
            payload["description"] = params.description
            
        if params.active is not None:
            payload["active"] = str(params.active).lower()
            
        if params.global_scope is not None:
            payload["global"] = str(params.global_scope).lower()
            
        # Check if there are any changes
        if not payload:
            return ClientScriptResponse(
                success=True,
                message=f"No changes to update for client script '{client_script['name']}'",
                client_script_id=sys_id,
                client_script_name=client_script["name"],
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
        updated_name = params.name if params.name is not None else client_script["name"]
        
        return ClientScriptResponse(
            success=True,
            message=f"Updated client script '{updated_name}'",
            client_script_id=sys_id,
            client_script_name=updated_name,
        )
        
    except Exception as e:
        logger.error(f"Error updating client script: {e}")
        return ClientScriptResponse(
            success=False,
            message=f"Error updating client script: {str(e)}",
        )


def delete_client_script(
    config: ServerConfig,
    auth_manager: AuthManager,
    params: DeleteClientScriptParams,
) -> ClientScriptResponse:
    """Delete a client script from ServiceNow.
    
    Args:
        config: The server configuration.
        auth_manager: The authentication manager.
        params: The parameters for the request.
        
    Returns:
        A response indicating the result of the operation.
    """
    try:
        # Find the client script first
        get_params = GetClientScriptParams(client_script_id=params.client_script_id)
        result = get_client_script(config, auth_manager, get_params)
        
        if not result.get("success") or not result.get("client_script"):
            return ClientScriptResponse(
                success=False,
                message=f"Client script '{params.client_script_id}' not found",
            )
            
        client_script = result["client_script"]
        sys_id = client_script["sys_id"]
        name = client_script["name"]
        
        # Build the URL
        url = f"{config.instance_url}/api/now/table/sys_script_client/{sys_id}"
        
        # Make the request
        headers = auth_manager.get_headers()
        
        response = requests.delete(
            url,
            headers=headers,
            timeout=30,
        )
        response.raise_for_status()
        
        return ClientScriptResponse(
            success=True,
            message=f"Deleted client script '{name}'",
            client_script_id=sys_id,
            client_script_name=name,
        )
        
    except Exception as e:
        logger.error(f"Error deleting client script: {e}")
        return ClientScriptResponse(
            success=False,
            message=f"Error deleting client script: {str(e)}",
        )
