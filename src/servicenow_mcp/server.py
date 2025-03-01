"""
ServiceNow MCP Server

This module provides the main implementation of the ServiceNow MCP server.
"""

from typing import Dict, Optional, Union

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from servicenow_mcp.auth.auth_manager import AuthManager
from servicenow_mcp.resources.incidents import IncidentResource, IncidentListParams
from servicenow_mcp.tools.incident_tools import (
    create_incident, 
    update_incident, 
    add_comment, 
    resolve_incident,
    CreateIncidentParams,
    UpdateIncidentParams,
    AddCommentParams,
    ResolveIncidentParams,
)
from servicenow_mcp.utils.config import ServerConfig


class ServiceNowMCP:
    """
    ServiceNow MCP Server implementation.
    
    This class provides a Model Context Protocol (MCP) server for ServiceNow,
    allowing LLMs to interact with ServiceNow data and functionality.
    """
    
    def __init__(self, config: Union[Dict, ServerConfig]):
        """
        Initialize the ServiceNow MCP server.
        
        Args:
            config: Server configuration, either as a dictionary or ServerConfig object.
        """
        if isinstance(config, dict):
            self.config = ServerConfig(**config)
        else:
            self.config = config
            
        self.auth_manager = AuthManager(self.config.auth)
        self.mcp_server = FastMCP("ServiceNow")
        
        # Register resources and tools
        self._register_resources()
        self._register_tools()
    
    def _register_resources(self):
        """Register all ServiceNow resources with the MCP server."""
        # Register incident resources
        incident_resource = IncidentResource(self.config, self.auth_manager)
        
        self.mcp_server.register_resource(
            "incidents",
            incident_resource.list_incidents,
            IncidentListParams,
            "List incidents from ServiceNow",
        )
        
        self.mcp_server.register_resource(
            "incident",
            incident_resource.get_incident,
            str,
            "Get a specific incident from ServiceNow by ID or number",
        )
    
    def _register_tools(self):
        """Register all ServiceNow tools with the MCP server."""
        # Register incident tools
        self.mcp_server.register_tool(
            "create_incident",
            lambda params: create_incident(self.config, self.auth_manager, params),
            CreateIncidentParams,
            "Create a new incident in ServiceNow",
        )
        
        self.mcp_server.register_tool(
            "update_incident",
            lambda params: update_incident(self.config, self.auth_manager, params),
            UpdateIncidentParams,
            "Update an existing incident in ServiceNow",
        )
        
        self.mcp_server.register_tool(
            "add_comment",
            lambda params: add_comment(self.config, self.auth_manager, params),
            AddCommentParams,
            "Add a comment to an incident in ServiceNow",
        )
        
        self.mcp_server.register_tool(
            "resolve_incident",
            lambda params: resolve_incident(self.config, self.auth_manager, params),
            ResolveIncidentParams,
            "Resolve an incident in ServiceNow",
        )
    
    def start(self):
        """Start the MCP server."""
        self.mcp_server.run()
    
    def stop(self):
        """Stop the MCP server."""
        # Cleanup resources if needed
        pass 