"""
Incident tools for the ServiceNow MCP server.

This module provides tools for managing incidents in ServiceNow.
"""

import logging
from typing import Dict, List, Optional

import requests
from mcp.server.fastmcp.tools import Tool
from pydantic import BaseModel, Field

from servicenow_mcp.auth.auth_manager import AuthManager
from servicenow_mcp.utils.config import ServerConfig


logger = logging.getLogger(__name__)


class CreateIncidentParams(BaseModel):
    """Parameters for creating an incident."""
    
    short_description: str = Field(..., description="Short description of the incident")
    description: Optional[str] = Field(None, description="Detailed description of the incident")
    caller_id: Optional[str] = Field(None, description="User who reported the incident")
    category: Optional[str] = Field(None, description="Category of the incident")
    subcategory: Optional[str] = Field(None, description="Subcategory of the incident")
    priority: Optional[str] = Field(None, description="Priority of the incident")
    impact: Optional[str] = Field(None, description="Impact of the incident")
    urgency: Optional[str] = Field(None, description="Urgency of the incident")
    assigned_to: Optional[str] = Field(None, description="User assigned to the incident")
    assignment_group: Optional[str] = Field(None, description="Group assigned to the incident")


class UpdateIncidentParams(BaseModel):
    """Parameters for updating an incident."""
    
    incident_id: str = Field(..., description="Incident ID or sys_id")
    short_description: Optional[str] = Field(None, description="Short description of the incident")
    description: Optional[str] = Field(None, description="Detailed description of the incident")
    state: Optional[str] = Field(None, description="State of the incident")
    category: Optional[str] = Field(None, description="Category of the incident")
    subcategory: Optional[str] = Field(None, description="Subcategory of the incident")
    priority: Optional[str] = Field(None, description="Priority of the incident")
    impact: Optional[str] = Field(None, description="Impact of the incident")
    urgency: Optional[str] = Field(None, description="Urgency of the incident")
    assigned_to: Optional[str] = Field(None, description="User assigned to the incident")
    assignment_group: Optional[str] = Field(None, description="Group assigned to the incident")
    work_notes: Optional[str] = Field(None, description="Work notes to add to the incident")
    close_notes: Optional[str] = Field(None, description="Close notes to add to the incident")
    close_code: Optional[str] = Field(None, description="Close code for the incident")


class AddCommentParams(BaseModel):
    """Parameters for adding a comment to an incident."""
    
    incident_id: str = Field(..., description="Incident ID or sys_id")
    comment: str = Field(..., description="Comment to add to the incident")
    is_work_note: bool = Field(False, description="Whether the comment is a work note")


class ResolveIncidentParams(BaseModel):
    """Parameters for resolving an incident."""
    
    incident_id: str = Field(..., description="Incident ID or sys_id")
    resolution_code: str = Field(..., description="Resolution code for the incident")
    resolution_notes: str = Field(..., description="Resolution notes for the incident")


class IncidentResponse(BaseModel):
    """Response from incident operations."""
    
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Message describing the result")
    incident_id: Optional[str] = Field(None, description="ID of the affected incident")
    incident_number: Optional[str] = Field(None, description="Number of the affected incident")


def create_incident(
    config: ServerConfig,
    auth_manager: AuthManager,
    params: CreateIncidentParams,
) -> IncidentResponse:
    """
    Create a new incident in ServiceNow.
    
    Args:
        config: Server configuration.
        auth_manager: Authentication manager.
        params: Parameters for creating the incident.
        
    Returns:
        Response with the created incident details.
    """
    api_url = f"{config.api_url}/table/incident"
    
    # Build request data
    data = {
        "short_description": params.short_description,
    }
    
    if params.description:
        data["description"] = params.description
    if params.caller_id:
        data["caller_id"] = params.caller_id
    if params.category:
        data["category"] = params.category
    if params.subcategory:
        data["subcategory"] = params.subcategory
    if params.priority:
        data["priority"] = params.priority
    if params.impact:
        data["impact"] = params.impact
    if params.urgency:
        data["urgency"] = params.urgency
    if params.assigned_to:
        data["assigned_to"] = params.assigned_to
    if params.assignment_group:
        data["assignment_group"] = params.assignment_group
    
    # Make request
    try:
        response = requests.post(
            api_url,
            json=data,
            headers=auth_manager.get_headers(),
            timeout=config.timeout,
        )
        response.raise_for_status()
        
        result = response.json().get("result", {})
        
        return IncidentResponse(
            success=True,
            message="Incident created successfully",
            incident_id=result.get("sys_id"),
            incident_number=result.get("number"),
        )
        
    except requests.RequestException as e:
        logger.error(f"Failed to create incident: {e}")
        return IncidentResponse(
            success=False,
            message=f"Failed to create incident: {str(e)}",
        )


def update_incident(
    config: ServerConfig,
    auth_manager: AuthManager,
    params: UpdateIncidentParams,
) -> IncidentResponse:
    """
    Update an existing incident in ServiceNow.
    
    Args:
        config: Server configuration.
        auth_manager: Authentication manager.
        params: Parameters for updating the incident.
        
    Returns:
        Response with the updated incident details.
    """
    # Determine if incident_id is a number or sys_id
    incident_id = params.incident_id
    if len(incident_id) == 32 and all(c in "0123456789abcdef" for c in incident_id):
        # This is likely a sys_id
        api_url = f"{config.api_url}/table/incident/{incident_id}"
    else:
        # This is likely an incident number
        # First, we need to get the sys_id
        try:
            query_url = f"{config.api_url}/table/incident"
            query_params = {
                "sysparm_query": f"number={incident_id}",
                "sysparm_limit": 1,
            }
            
            response = requests.get(
                query_url,
                params=query_params,
                headers=auth_manager.get_headers(),
                timeout=config.timeout,
            )
            response.raise_for_status()
            
            result = response.json().get("result", [])
            if not result:
                return IncidentResponse(
                    success=False,
                    message=f"Incident not found: {incident_id}",
                )
            
            incident_id = result[0].get("sys_id")
            api_url = f"{config.api_url}/table/incident/{incident_id}"
            
        except requests.RequestException as e:
            logger.error(f"Failed to find incident: {e}")
            return IncidentResponse(
                success=False,
                message=f"Failed to find incident: {str(e)}",
            )
    
    # Build request data
    data = {}
    
    if params.short_description:
        data["short_description"] = params.short_description
    if params.description:
        data["description"] = params.description
    if params.state:
        data["state"] = params.state
    if params.category:
        data["category"] = params.category
    if params.subcategory:
        data["subcategory"] = params.subcategory
    if params.priority:
        data["priority"] = params.priority
    if params.impact:
        data["impact"] = params.impact
    if params.urgency:
        data["urgency"] = params.urgency
    if params.assigned_to:
        data["assigned_to"] = params.assigned_to
    if params.assignment_group:
        data["assignment_group"] = params.assignment_group
    if params.work_notes:
        data["work_notes"] = params.work_notes
    if params.close_notes:
        data["close_notes"] = params.close_notes
    if params.close_code:
        data["close_code"] = params.close_code
    
    # Make request
    try:
        response = requests.put(
            api_url,
            json=data,
            headers=auth_manager.get_headers(),
            timeout=config.timeout,
        )
        response.raise_for_status()
        
        result = response.json().get("result", {})
        
        return IncidentResponse(
            success=True,
            message="Incident updated successfully",
            incident_id=result.get("sys_id"),
            incident_number=result.get("number"),
        )
        
    except requests.RequestException as e:
        logger.error(f"Failed to update incident: {e}")
        return IncidentResponse(
            success=False,
            message=f"Failed to update incident: {str(e)}",
        )


def add_comment(
    config: ServerConfig,
    auth_manager: AuthManager,
    params: AddCommentParams,
) -> IncidentResponse:
    """
    Add a comment to an incident in ServiceNow.
    
    Args:
        config: Server configuration.
        auth_manager: Authentication manager.
        params: Parameters for adding the comment.
        
    Returns:
        Response with the result of the operation.
    """
    # Determine if incident_id is a number or sys_id
    incident_id = params.incident_id
    if len(incident_id) == 32 and all(c in "0123456789abcdef" for c in incident_id):
        # This is likely a sys_id
        api_url = f"{config.api_url}/table/incident/{incident_id}"
    else:
        # This is likely an incident number
        # First, we need to get the sys_id
        try:
            query_url = f"{config.api_url}/table/incident"
            query_params = {
                "sysparm_query": f"number={incident_id}",
                "sysparm_limit": 1,
            }
            
            response = requests.get(
                query_url,
                params=query_params,
                headers=auth_manager.get_headers(),
                timeout=config.timeout,
            )
            response.raise_for_status()
            
            result = response.json().get("result", [])
            if not result:
                return IncidentResponse(
                    success=False,
                    message=f"Incident not found: {incident_id}",
                )
            
            incident_id = result[0].get("sys_id")
            api_url = f"{config.api_url}/table/incident/{incident_id}"
            
        except requests.RequestException as e:
            logger.error(f"Failed to find incident: {e}")
            return IncidentResponse(
                success=False,
                message=f"Failed to find incident: {str(e)}",
            )
    
    # Build request data
    data = {}
    
    if params.is_work_note:
        data["work_notes"] = params.comment
    else:
        data["comments"] = params.comment
    
    # Make request
    try:
        response = requests.put(
            api_url,
            json=data,
            headers=auth_manager.get_headers(),
            timeout=config.timeout,
        )
        response.raise_for_status()
        
        result = response.json().get("result", {})
        
        return IncidentResponse(
            success=True,
            message="Comment added successfully",
            incident_id=result.get("sys_id"),
            incident_number=result.get("number"),
        )
        
    except requests.RequestException as e:
        logger.error(f"Failed to add comment: {e}")
        return IncidentResponse(
            success=False,
            message=f"Failed to add comment: {str(e)}",
        )


def resolve_incident(
    config: ServerConfig,
    auth_manager: AuthManager,
    params: ResolveIncidentParams,
) -> IncidentResponse:
    """
    Resolve an incident in ServiceNow.
    
    Args:
        config: Server configuration.
        auth_manager: Authentication manager.
        params: Parameters for resolving the incident.
        
    Returns:
        Response with the result of the operation.
    """
    # Determine if incident_id is a number or sys_id
    incident_id = params.incident_id
    if len(incident_id) == 32 and all(c in "0123456789abcdef" for c in incident_id):
        # This is likely a sys_id
        api_url = f"{config.api_url}/table/incident/{incident_id}"
    else:
        # This is likely an incident number
        # First, we need to get the sys_id
        try:
            query_url = f"{config.api_url}/table/incident"
            query_params = {
                "sysparm_query": f"number={incident_id}",
                "sysparm_limit": 1,
            }
            
            response = requests.get(
                query_url,
                params=query_params,
                headers=auth_manager.get_headers(),
                timeout=config.timeout,
            )
            response.raise_for_status()
            
            result = response.json().get("result", [])
            if not result:
                return IncidentResponse(
                    success=False,
                    message=f"Incident not found: {incident_id}",
                )
            
            incident_id = result[0].get("sys_id")
            api_url = f"{config.api_url}/table/incident/{incident_id}"
            
        except requests.RequestException as e:
            logger.error(f"Failed to find incident: {e}")
            return IncidentResponse(
                success=False,
                message=f"Failed to find incident: {str(e)}",
            )
    
    # Build request data
    data = {
        "state": "6",  # Resolved
        "close_code": params.resolution_code,
        "close_notes": params.resolution_notes,
        "resolved_at": "now",
    }
    
    # Make request
    try:
        response = requests.put(
            api_url,
            json=data,
            headers=auth_manager.get_headers(),
            timeout=config.timeout,
        )
        response.raise_for_status()
        
        result = response.json().get("result", {})
        
        return IncidentResponse(
            success=True,
            message="Incident resolved successfully",
            incident_id=result.get("sys_id"),
            incident_number=result.get("number"),
        )
        
    except requests.RequestException as e:
        logger.error(f"Failed to resolve incident: {e}")
        return IncidentResponse(
            success=False,
            message=f"Failed to resolve incident: {str(e)}",
        ) 