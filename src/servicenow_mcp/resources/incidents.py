"""
Incident resources for the ServiceNow MCP server.

This module provides resources for accessing incident data from ServiceNow.
"""

import logging
from typing import Dict, List, Optional

from mcp.server.fastmcp.resources import Resource
from pydantic import BaseModel, Field

from servicenow_mcp.auth.auth_manager import AuthManager
from servicenow_mcp.utils.config import ServerConfig


logger = logging.getLogger(__name__)


class IncidentModel(BaseModel):
    """Model representing a ServiceNow incident."""
    
    sys_id: str = Field(..., description="Unique identifier for the incident")
    number: str = Field(..., description="Incident number (e.g., INC0010001)")
    short_description: str = Field(..., description="Short description of the incident")
    description: Optional[str] = Field(None, description="Detailed description of the incident")
    state: str = Field(..., description="Current state of the incident")
    priority: Optional[str] = Field(None, description="Priority of the incident")
    assigned_to: Optional[str] = Field(None, description="User assigned to the incident")
    category: Optional[str] = Field(None, description="Category of the incident")
    subcategory: Optional[str] = Field(None, description="Subcategory of the incident")
    created_on: str = Field(..., description="Date and time when the incident was created")
    updated_on: str = Field(..., description="Date and time when the incident was last updated")
    resolved_on: Optional[str] = Field(None, description="Date and time when the incident was resolved")
    closed_on: Optional[str] = Field(None, description="Date and time when the incident was closed")


class IncidentListParams(BaseModel):
    """Parameters for listing incidents."""
    
    limit: int = Field(10, description="Maximum number of incidents to return")
    offset: int = Field(0, description="Offset for pagination")
    state: Optional[str] = Field(None, description="Filter by incident state")
    assigned_to: Optional[str] = Field(None, description="Filter by assigned user")
    category: Optional[str] = Field(None, description="Filter by category")
    query: Optional[str] = Field(None, description="Search query for incidents")


class IncidentResource(Resource):
    """Resource for accessing ServiceNow incidents."""
    
    def __init__(self, config: ServerConfig, auth_manager: AuthManager):
        """
        Initialize the incident resource.
        
        Args:
            config: Server configuration.
            auth_manager: Authentication manager.
        """
        # Use the instance URL from the configuration for the uri
        uri = f"{config.instance_url}/api/now/incidents"
        super().__init__(name="incidents", uri=uri)
        # Store config and auth_manager as private attributes
        self._config = config
        self._auth_manager = auth_manager
        self._api_url = f"{config.api_url}/table/incident"
    
    async def read(self, params: dict = None) -> dict:
        """
        Read incidents from ServiceNow.
        
        This is the required method for the Resource abstract class.
        
        Args:
            params: Parameters for reading incidents.
            
        Returns:
            Dictionary with incidents data.
        """
        list_params = IncidentListParams(**(params or {}))
        incidents = await self.list_incidents(list_params)
        return {"incidents": [incident.dict() for incident in incidents]}
    
    async def list_incidents(self, params: IncidentListParams) -> List[IncidentModel]:
        """
        List incidents from ServiceNow.
        
        Args:
            params: Parameters for listing incidents.
            
        Returns:
            List of incidents.
        """
        import requests
        
        # Build query parameters
        query_params = {
            "sysparm_limit": params.limit,
            "sysparm_offset": params.offset,
            "sysparm_display_value": "true",
            "sysparm_exclude_reference_link": "true",
        }
        
        # Add filters
        filters = []
        if params.state:
            filters.append(f"state={params.state}")
        if params.assigned_to:
            filters.append(f"assigned_to={params.assigned_to}")
        if params.category:
            filters.append(f"category={params.category}")
        if params.query:
            filters.append(f"short_descriptionLIKE{params.query}^ORdescriptionLIKE{params.query}")
        
        if filters:
            query_params["sysparm_query"] = "^".join(filters)
        
        # Make request
        try:
            response = requests.get(
                self._api_url,
                params=query_params,
                headers=self._auth_manager.get_headers(),
                timeout=self._config.timeout,
            )
            response.raise_for_status()
            
            data = response.json()
            incidents = []
            
            for incident_data in data.get("result", []):
                # Handle assigned_to field which could be a string or a dictionary
                assigned_to = incident_data.get("assigned_to")
                if isinstance(assigned_to, dict):
                    assigned_to = assigned_to.get("display_value")
                
                incident = IncidentModel(
                    sys_id=incident_data.get("sys_id"),
                    number=incident_data.get("number"),
                    short_description=incident_data.get("short_description"),
                    description=incident_data.get("description"),
                    state=incident_data.get("state"),
                    priority=incident_data.get("priority"),
                    assigned_to=assigned_to,
                    category=incident_data.get("category"),
                    subcategory=incident_data.get("subcategory"),
                    created_on=incident_data.get("sys_created_on"),
                    updated_on=incident_data.get("sys_updated_on"),
                    resolved_on=incident_data.get("resolved_at"),
                    closed_on=incident_data.get("closed_at"),
                )
                incidents.append(incident)
            
            return incidents
            
        except requests.RequestException as e:
            logger.error(f"Failed to list incidents: {e}")
            raise ValueError(f"Failed to list incidents: {e}")
    
    async def get_incident(self, incident_id: str) -> IncidentModel:
        """
        Get a specific incident from ServiceNow.
        
        Args:
            incident_id: Incident ID or sys_id.
            
        Returns:
            Incident details.
        """
        import requests
        
        # Determine if incident_id is a number or sys_id
        query_param = "sysparm_query=number=" + incident_id
        if len(incident_id) == 32 and all(c in "0123456789abcdef" for c in incident_id):
            # This is likely a sys_id
            url = f"{self._api_url}/{incident_id}"
            query_param = None
        else:
            # This is likely an incident number
            url = self._api_url
        
        # Make request
        try:
            params = {
                "sysparm_display_value": "true",
                "sysparm_exclude_reference_link": "true",
            }
            
            if query_param:
                params["sysparm_query"] = query_param
            
            response = requests.get(
                url,
                params=params,
                headers=self._auth_manager.get_headers(),
                timeout=self._config.timeout,
            )
            response.raise_for_status()
            
            data = response.json()
            
            if query_param:
                # If we queried by number, we need to get the first result
                if not data.get("result"):
                    raise ValueError(f"Incident not found: {incident_id}")
                incident_data = data["result"][0]
            else:
                # If we queried by sys_id, we get a single result
                incident_data = data["result"]
            
            # Handle assigned_to field which could be a string or a dictionary
            assigned_to = incident_data.get("assigned_to")
            if isinstance(assigned_to, dict):
                assigned_to = assigned_to.get("display_value")
            
            incident = IncidentModel(
                sys_id=incident_data.get("sys_id"),
                number=incident_data.get("number"),
                short_description=incident_data.get("short_description"),
                description=incident_data.get("description"),
                state=incident_data.get("state"),
                priority=incident_data.get("priority"),
                assigned_to=assigned_to,
                category=incident_data.get("category"),
                subcategory=incident_data.get("subcategory"),
                created_on=incident_data.get("sys_created_on"),
                updated_on=incident_data.get("sys_updated_on"),
                resolved_on=incident_data.get("resolved_at"),
                closed_on=incident_data.get("closed_at"),
            )
            
            return incident
            
        except requests.RequestException as e:
            logger.error(f"Failed to get incident: {e}")
            raise ValueError(f"Failed to get incident: {e}") 