"""
ServiceNow MCP Server

This module provides the main implementation of the ServiceNow MCP server.
"""

from typing import Dict, Optional, Union

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel

from servicenow_mcp.auth.auth_manager import AuthManager
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
        # This will be implemented in Phase 2-5
        pass
    
    def _register_tools(self):
        """Register all ServiceNow tools with the MCP server."""
        # This will be implemented in Phase 2-5
        pass
    
    def start(self):
        """Start the MCP server."""
        self.mcp_server.run()
    
    def stop(self):
        """Stop the MCP server."""
        # Cleanup resources if needed
        pass 