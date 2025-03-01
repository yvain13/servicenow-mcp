"""
ServiceNow MCP Server

This module provides the main implementation of the ServiceNow MCP server.
"""

import os
from typing import Dict, Union

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from servicenow_mcp.auth.auth_manager import AuthManager
from servicenow_mcp.resources.incidents import IncidentListParams, IncidentResource
from servicenow_mcp.tools.incident_tools import (
    AddCommentParams,
    CreateIncidentParams,
    ResolveIncidentParams,
    UpdateIncidentParams,
    ListIncidentsParams,
)
from servicenow_mcp.tools.incident_tools import (
    add_comment as add_comment_tool,
)
from servicenow_mcp.tools.incident_tools import (
    create_incident as create_incident_tool,
)
from servicenow_mcp.tools.incident_tools import (
    resolve_incident as resolve_incident_tool,
)
from servicenow_mcp.tools.incident_tools import (
    update_incident as update_incident_tool,
)
from servicenow_mcp.tools.incident_tools import (
    list_incidents as list_incidents_tool,
)
from servicenow_mcp.utils.config import AuthConfig, AuthType, BasicAuthConfig, ServerConfig


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
        # Add name attribute for MCP CLI
        self.name = "ServiceNow"

        # Register resources and tools
        self._register_resources()
        self._register_tools()

    def _register_resources(self):
        """Register all ServiceNow resources with the MCP server."""
        # Register incident resources
        incident_resource = IncidentResource(self.config, self.auth_manager)

        # Use decorator pattern for resources
        @self.mcp_server.resource("incidents://list")
        async def list_incidents() -> str:
            """List incidents from ServiceNow"""
            # Since there's no URI parameter, we pass an empty params object
            incidents = await incident_resource.list_incidents(IncidentListParams())
            return incidents

        @self.mcp_server.resource("incident://{incident_id}")
        def get_incident(incident_id: str) -> str:
            """Get a specific incident from ServiceNow by ID or number"""
            return incident_resource.get_incident(incident_id)

    def _register_tools(self):
        """Register all ServiceNow tools with the MCP server."""

        # Register incident tools
        @self.mcp_server.tool()
        def create_incident(params: CreateIncidentParams) -> str:
            """Create a new incident in ServiceNow"""
            return create_incident_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def update_incident(params: UpdateIncidentParams) -> str:
            """Update an existing incident in ServiceNow"""
            return update_incident_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def add_comment(params: AddCommentParams) -> str:
            """Add a comment to an incident in ServiceNow"""
            return add_comment_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def resolve_incident(params: ResolveIncidentParams) -> str:
            """Resolve an incident in ServiceNow"""
            return resolve_incident_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def list_incidents(params: ListIncidentsParams) -> str:
            """List incidents from ServiceNow"""
            return list_incidents_tool(self.config, self.auth_manager, params)

    def start(self):
        """Start the MCP server."""
        self.mcp_server.run()

    def stop(self):
        """Stop the MCP server."""
        # Cleanup resources if needed
        pass


def create_servicenow_mcp(instance_url: str, username: str, password: str):
    """
    Create a ServiceNow MCP server with minimal configuration.

    This is a simplified factory function that creates a pre-configured
    ServiceNow MCP server with basic authentication.

    Args:
        instance_url: ServiceNow instance URL
        username: ServiceNow username
        password: ServiceNow password

    Returns:
        A configured ServiceNowMCP instance ready to use

    Example:
        ```python
        from servicenow_mcp.server import create_servicenow_mcp

        # Create an MCP server for ServiceNow
        mcp = create_servicenow_mcp(
            instance_url="https://instance.service-now.com",
            username="admin",
            password="password"
        )

        # Start the server
        mcp.start()
        ```
    """

    # Create basic auth config
    auth_config = AuthConfig(
        type=AuthType.BASIC, basic=BasicAuthConfig(username=username, password=password)
    )

    # Create server config
    config = ServerConfig(instance_url=instance_url, auth=auth_config)

    # Create and return server
    return ServiceNowMCP(config)


# Create a standard variable that MCP CLI can recognize
# This will be used when running `mcp install src/servicenow_mcp/server.py`
# The actual configuration will be loaded from environment variables

# Load environment variables
load_dotenv()

# Get configuration from environment variables
instance_url = os.getenv("SERVICENOW_INSTANCE_URL")
username = os.getenv("SERVICENOW_USERNAME")
password = os.getenv("SERVICENOW_PASSWORD")

# Create the server instance with a standard variable name
# This is the variable that MCP CLI will look for
if instance_url and username and password:
    server = create_servicenow_mcp(
        instance_url=instance_url,
        username=username,
        password=password
    )
else:
    # Create a dummy server with default values for MCP CLI to discover
    # The actual configuration will be loaded from environment variables when run
    server = ServiceNowMCP({
        "instance_url": "https://example.service-now.com",
        "auth": {
            "type": "basic",
            "basic": {
                "username": "admin",
                "password": "password"
            }
        }
    })
