"""
Tools module for the ServiceNow MCP server.
"""

# Import tools as they are implemented
from servicenow_mcp.tools.incident_tools import create_incident, update_incident, add_comment, resolve_incident, list_incidents
from servicenow_mcp.tools.catalog_tools import list_catalog_items, get_catalog_item, list_catalog_categories
from servicenow_mcp.tools.change_tools import (
    create_change_request,
    update_change_request,
    list_change_requests,
    get_change_request_details,
    add_change_task,
    submit_change_for_approval,
    approve_change,
    reject_change,
)
from servicenow_mcp.tools.workflow_tools import (
    list_workflows,
    get_workflow_details,
    list_workflow_versions,
    get_workflow_activities,
    create_workflow,
    update_workflow,
    activate_workflow,
    deactivate_workflow,
    add_workflow_activity,
    update_workflow_activity,
    delete_workflow_activity,
    reorder_workflow_activities,
)
# from servicenow_mcp.tools.problem_tools import create_problem, update_problem
# from servicenow_mcp.tools.request_tools import create_request, update_request

__all__ = [
    # Incident tools
    "create_incident",
    "update_incident",
    "add_comment",
    "resolve_incident",
    "list_incidents",
    
    # Catalog tools
    "list_catalog_items",
    "get_catalog_item",
    "list_catalog_categories",
    
    # Change management tools
    "create_change_request",
    "update_change_request",
    "list_change_requests",
    "get_change_request_details",
    "add_change_task",
    "submit_change_for_approval",
    "approve_change",
    "reject_change",
    
    # Workflow management tools
    "list_workflows",
    "get_workflow_details",
    "list_workflow_versions",
    "get_workflow_activities",
    "create_workflow",
    "update_workflow",
    "activate_workflow",
    "deactivate_workflow",
    "add_workflow_activity",
    "update_workflow_activity",
    "delete_workflow_activity",
    "reorder_workflow_activities",
    
    # Future tools
    # "create_problem",
    # "update_problem",
    # "create_request",
    # "update_request",
] 