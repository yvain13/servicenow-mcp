"""
Resources module for the ServiceNow MCP server.
"""

# Import resources as they are implemented
from servicenow_mcp.resources.incidents import IncidentResource
from servicenow_mcp.resources.catalog import CatalogResource
# from servicenow_mcp.resources.problems import ProblemResource
# from servicenow_mcp.resources.changes import ChangeResource
# from servicenow_mcp.resources.requests import RequestResource

__all__ = [
    # Incident resources
    "IncidentResource",
    
    # Catalog resources
    "CatalogResource",
    
    # Future resources
    # "ProblemResource",
    # "ChangeResource",
    # "RequestResource",
] 