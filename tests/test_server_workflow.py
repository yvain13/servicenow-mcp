"""
Tests for the ServiceNow MCP server workflow management integration.
"""

import unittest
from unittest.mock import MagicMock, patch

from servicenow_mcp.server import ServiceNowMCP
from servicenow_mcp.utils.config import AuthConfig, AuthType, BasicAuthConfig, ServerConfig


class TestServerWorkflow(unittest.TestCase):
    """Tests for the ServiceNow MCP server workflow management integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.auth_config = AuthConfig(
            type=AuthType.BASIC,
            basic=BasicAuthConfig(username="test_user", password="test_password"),
        )
        self.server_config = ServerConfig(
            instance_url="https://test.service-now.com",
            auth=self.auth_config,
        )
        
        # Create a mock FastMCP instance
        self.mock_mcp = MagicMock()
        
        # Patch the FastMCP class
        self.patcher = patch("servicenow_mcp.server.FastMCP", return_value=self.mock_mcp)
        self.mock_fastmcp = self.patcher.start()
        
        # Create the server instance
        self.server = ServiceNowMCP(self.server_config)
        
    def tearDown(self):
        """Tear down test fixtures."""
        self.patcher.stop()

    def test_register_workflow_tools(self):
        """Test that workflow tools are registered with the MCP server."""
        # Get all the tool decorator calls
        tool_decorator_calls = self.mock_mcp.tool.call_count
        
        # Verify that the tool decorator was called at least 12 times (for all workflow tools)
        self.assertGreaterEqual(tool_decorator_calls, 12, 
                               "Expected at least 12 tool registrations for workflow tools")
        
        # Check that the workflow tools are registered by examining the decorated functions
        decorated_functions = []
        for call in self.mock_mcp.tool.call_args_list:
            # Each call to tool() returns a decorator function
            decorator = call[0][0] if call[0] else call[1].get('return_value', None)
            if decorator:
                decorated_functions.append(decorator.__name__)
        
        # Check for workflow tool registrations
        workflow_tools = [
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
        ]
        
        # Print the decorated functions for debugging
        print(f"Decorated functions: {decorated_functions}")
        
        # Check that all workflow tools are registered
        for tool in workflow_tools:
            self.assertIn(tool, str(self.mock_mcp.mock_calls), 
                         f"Expected {tool} to be registered")


if __name__ == "__main__":
    unittest.main() 