"""
ServiceNow MCP Server

This module provides the main implementation of the ServiceNow MCP server.
"""

import os
from typing import Dict, Union

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

from servicenow_mcp.auth.auth_manager import AuthManager
from servicenow_mcp.resources.catalog import (
    CatalogCategoryListParams,
    CatalogListParams,
    CatalogResource,
)
from servicenow_mcp.resources.incidents import IncidentListParams, IncidentResource
from servicenow_mcp.tools.catalog_tools import (
    GetCatalogItemParams,
    ListCatalogCategoriesParams,
    ListCatalogItemsParams,
)
from servicenow_mcp.tools.catalog_tools import (
    get_catalog_item as get_catalog_item_tool,
)
from servicenow_mcp.tools.catalog_tools import (
    list_catalog_categories as list_catalog_categories_tool,
)
from servicenow_mcp.tools.catalog_tools import (
    list_catalog_items as list_catalog_items_tool,
)
from servicenow_mcp.tools.catalog_optimization import (
    OptimizationRecommendationsParams,
    UpdateCatalogItemParams,
    get_optimization_recommendations as get_optimization_recommendations_tool,
    update_catalog_item as update_catalog_item_tool,
)
from servicenow_mcp.tools.incident_tools import (
    AddCommentParams,
    CreateIncidentParams,
    ListIncidentsParams,
    ResolveIncidentParams,
    UpdateIncidentParams,
)
from servicenow_mcp.tools.incident_tools import (
    add_comment as add_comment_tool,
)
from servicenow_mcp.tools.incident_tools import (
    create_incident as create_incident_tool,
)
from servicenow_mcp.tools.incident_tools import (
    list_incidents as list_incidents_tool,
)
from servicenow_mcp.tools.incident_tools import (
    resolve_incident as resolve_incident_tool,
)
from servicenow_mcp.tools.incident_tools import (
    update_incident as update_incident_tool,
)
from servicenow_mcp.utils.config import AuthConfig, AuthType, BasicAuthConfig, ServerConfig

from servicenow_mcp.tools.change_tools import (
    AddChangeTaskParams,
    ApproveChangeParams,
    CreateChangeRequestParams,
    GetChangeRequestDetailsParams,
    ListChangeRequestsParams,
    RejectChangeParams,
    SubmitChangeForApprovalParams,
    UpdateChangeRequestParams,
)
from servicenow_mcp.tools.change_tools import (
    add_change_task as add_change_task_tool,
)
from servicenow_mcp.tools.change_tools import (
    approve_change as approve_change_tool,
)
from servicenow_mcp.tools.change_tools import (
    create_change_request as create_change_request_tool,
)
from servicenow_mcp.tools.change_tools import (
    get_change_request_details as get_change_request_details_tool,
)
from servicenow_mcp.tools.change_tools import (
    list_change_requests as list_change_requests_tool,
)
from servicenow_mcp.tools.change_tools import (
    reject_change as reject_change_tool,
)
from servicenow_mcp.tools.change_tools import (
    submit_change_for_approval as submit_change_for_approval_tool,
)
from servicenow_mcp.tools.change_tools import (
    update_change_request as update_change_request_tool,
)

from servicenow_mcp.tools.workflow_tools import (
    GetWorkflowActivitiesParams,
    GetWorkflowDetailsParams,
    ListWorkflowsParams,
    ListWorkflowVersionsParams,
    CreateWorkflowParams,
    UpdateWorkflowParams,
    ActivateWorkflowParams,
    DeactivateWorkflowParams,
    AddWorkflowActivityParams,
    UpdateWorkflowActivityParams,
    DeleteWorkflowActivityParams,
    ReorderWorkflowActivitiesParams,
)
from servicenow_mcp.tools.workflow_tools import (
    get_workflow_activities as get_workflow_activities_tool,
)
from servicenow_mcp.tools.workflow_tools import (
    get_workflow_details as get_workflow_details_tool,
)
from servicenow_mcp.tools.workflow_tools import (
    list_workflows as list_workflows_tool,
)
from servicenow_mcp.tools.workflow_tools import (
    list_workflow_versions as list_workflow_versions_tool,
)
from servicenow_mcp.tools.workflow_tools import (
    create_workflow as create_workflow_tool,
)
from servicenow_mcp.tools.workflow_tools import (
    update_workflow as update_workflow_tool,
)
from servicenow_mcp.tools.workflow_tools import (
    activate_workflow as activate_workflow_tool,
)
from servicenow_mcp.tools.workflow_tools import (
    deactivate_workflow as deactivate_workflow_tool,
)
from servicenow_mcp.tools.workflow_tools import (
    add_workflow_activity as add_workflow_activity_tool,
)
from servicenow_mcp.tools.workflow_tools import (
    update_workflow_activity as update_workflow_activity_tool,
)
from servicenow_mcp.tools.workflow_tools import (
    delete_workflow_activity as delete_workflow_activity_tool,
)
from servicenow_mcp.tools.workflow_tools import (
    reorder_workflow_activities as reorder_workflow_activities_tool,
)


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
            
        # Register catalog resources
        catalog_resource = CatalogResource(self.config, self.auth_manager)
        
        @self.mcp_server.resource("catalog://items")
        async def list_catalog_items() -> str:
            """List catalog items from ServiceNow"""
            # Since there's no URI parameter, we pass an empty params object
            items = await catalog_resource.list_catalog_items(CatalogListParams())
            return items
            
        @self.mcp_server.resource("catalog://categories")
        async def list_catalog_categories() -> str:
            """List catalog categories from ServiceNow"""
            # Since there's no URI parameter, we pass an empty params object
            categories = await catalog_resource.list_catalog_categories(CatalogCategoryListParams())
            return categories
            
        @self.mcp_server.resource("catalog://{item_id}")
        async def get_catalog_item(item_id: str) -> str:
            """Get a specific catalog item from ServiceNow by ID"""
            return await catalog_resource.get_catalog_item(item_id)

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
            
        # Register catalog tools
        @self.mcp_server.tool()
        def list_catalog_items(params: ListCatalogItemsParams) -> str:
            """List service catalog items from ServiceNow"""
            return list_catalog_items_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def get_catalog_item(params: GetCatalogItemParams) -> str:
            """Get a specific service catalog item from ServiceNow"""
            return get_catalog_item_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def list_catalog_categories(params: ListCatalogCategoriesParams) -> str:
            """List service catalog categories from ServiceNow"""
            return list_catalog_categories_tool(self.config, self.auth_manager, params)
            
        # Register catalog optimization tools
        @self.mcp_server.tool()
        def get_optimization_recommendations(params: OptimizationRecommendationsParams) -> str:
            """Get recommendations for optimizing the service catalog"""
            return get_optimization_recommendations_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def update_catalog_item(params: UpdateCatalogItemParams) -> str:
            """Update a service catalog item"""
            return update_catalog_item_tool(self.config, self.auth_manager, params)

        # Register change management tools
        @self.mcp_server.tool()
        def create_change_request(params: CreateChangeRequestParams) -> str:
            """Create a new change request in ServiceNow"""
            return create_change_request_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def update_change_request(params: UpdateChangeRequestParams) -> str:
            """Update an existing change request in ServiceNow"""
            return update_change_request_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def list_change_requests(params: ListChangeRequestsParams) -> str:
            """List change requests from ServiceNow"""
            return list_change_requests_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def get_change_request_details(params: GetChangeRequestDetailsParams) -> str:
            """Get detailed information about a specific change request"""
            return get_change_request_details_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def add_change_task(params: AddChangeTaskParams) -> str:
            """Add a task to a change request"""
            return add_change_task_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def submit_change_for_approval(params: SubmitChangeForApprovalParams) -> str:
            """Submit a change request for approval"""
            return submit_change_for_approval_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def approve_change(params: ApproveChangeParams) -> str:
            """Approve a change request"""
            return approve_change_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def reject_change(params: RejectChangeParams) -> str:
            """Reject a change request"""
            return reject_change_tool(self.config, self.auth_manager, params)

        # Register workflow management tools
        @self.mcp_server.tool()
        def list_workflows(params: ListWorkflowsParams) -> str:
            """List workflows from ServiceNow"""
            return list_workflows_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def get_workflow_details(params: GetWorkflowDetailsParams) -> str:
            """Get detailed information about a specific workflow"""
            return get_workflow_details_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def list_workflow_versions(params: ListWorkflowVersionsParams) -> str:
            """List workflow versions from ServiceNow"""
            return list_workflow_versions_tool(self.config, self.auth_manager, params)

        @self.mcp_server.tool()
        def get_workflow_activities(params: GetWorkflowActivitiesParams) -> str:
            """Get activities for a specific workflow"""
            return get_workflow_activities_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def create_workflow(params: CreateWorkflowParams) -> str:
            """Create a new workflow in ServiceNow"""
            return create_workflow_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def update_workflow(params: UpdateWorkflowParams) -> str:
            """Update an existing workflow in ServiceNow"""
            return update_workflow_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def activate_workflow(params: ActivateWorkflowParams) -> str:
            """Activate a workflow in ServiceNow"""
            return activate_workflow_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def deactivate_workflow(params: DeactivateWorkflowParams) -> str:
            """Deactivate a workflow in ServiceNow"""
            return deactivate_workflow_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def add_workflow_activity(params: AddWorkflowActivityParams) -> str:
            """Add a new activity to a workflow in ServiceNow"""
            return add_workflow_activity_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def update_workflow_activity(params: UpdateWorkflowActivityParams) -> str:
            """Update an existing activity in a workflow"""
            return update_workflow_activity_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def delete_workflow_activity(params: DeleteWorkflowActivityParams) -> str:
            """Delete an activity from a workflow"""
            return delete_workflow_activity_tool(self.config, self.auth_manager, params)
            
        @self.mcp_server.tool()
        def reorder_workflow_activities(params: ReorderWorkflowActivitiesParams) -> str:
            """Reorder activities in a workflow"""
            return reorder_workflow_activities_tool(self.config, self.auth_manager, params)

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
    server = create_servicenow_mcp(instance_url=instance_url, username=username, password=password)
else:
    # Create a dummy server with default values for MCP CLI to discover
    # The actual configuration will be loaded from environment variables when run
    server = ServiceNowMCP(
        {
            "instance_url": "https://example.service-now.com",
            "auth": {"type": "basic", "basic": {"username": "admin", "password": "password"}},
        }
    )
