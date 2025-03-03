"""
Tests for the changeset resources.

This module contains tests for the changeset resources in the ServiceNow MCP server.
"""

import json
import unittest
import requests
from unittest.mock import MagicMock, patch

from servicenow_mcp.auth.auth_manager import AuthManager
from servicenow_mcp.resources.changesets import ChangesetListParams, ChangesetResource
from servicenow_mcp.utils.config import ServerConfig, AuthConfig, AuthType, BasicAuthConfig


class TestChangesetResource(unittest.IsolatedAsyncioTestCase):
    """Tests for the changeset resource."""

    def setUp(self):
        """Set up test fixtures."""
        auth_config = AuthConfig(
            type=AuthType.BASIC,
            basic=BasicAuthConfig(
                username="test_user",
                password="test_password"
            )
        )
        self.server_config = ServerConfig(
            instance_url="https://test.service-now.com",
            auth=auth_config,
        )
        self.auth_manager = MagicMock(spec=AuthManager)
        self.auth_manager.get_headers.return_value = {"Authorization": "Bearer test"}
        self.changeset_resource = ChangesetResource(self.server_config, self.auth_manager)

    @patch("servicenow_mcp.resources.changesets.requests.get")
    async def test_list_changesets(self, mock_get):
        """Test listing changesets."""
        # Mock response
        mock_response = MagicMock()
        mock_response.text = json.dumps({
            "result": [
                {
                    "sys_id": "123",
                    "name": "Test Changeset",
                    "state": "in_progress",
                    "application": "Test App",
                    "developer": "test.user",
                }
            ]
        })
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        # Call the function
        params = ChangesetListParams(
            limit=10,
            offset=0,
            state="in_progress",
            application="Test App",
            developer="test.user",
        )
        result = await self.changeset_resource.list_changesets(params)

        # Verify the result
        result_json = json.loads(result)
        self.assertEqual(len(result_json["result"]), 1)
        self.assertEqual(result_json["result"][0]["sys_id"], "123")
        self.assertEqual(result_json["result"][0]["name"], "Test Changeset")

        # Verify the API call
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://test.service-now.com/api/now/table/sys_update_set")
        self.assertEqual(kwargs["headers"], {"Authorization": "Bearer test"})
        self.assertEqual(kwargs["params"]["sysparm_limit"], 10)
        self.assertEqual(kwargs["params"]["sysparm_offset"], 0)
        self.assertIn("sysparm_query", kwargs["params"])
        self.assertIn("state=in_progress", kwargs["params"]["sysparm_query"])
        self.assertIn("application=Test App", kwargs["params"]["sysparm_query"])
        self.assertIn("developer=test.user", kwargs["params"]["sysparm_query"])

    @patch("servicenow_mcp.resources.changesets.requests.get")
    async def test_get_changeset(self, mock_get):
        """Test getting a changeset."""
        # Mock responses
        mock_changeset_response = MagicMock()
        mock_changeset_response.json.return_value = {
            "result": {
                "sys_id": "123",
                "name": "Test Changeset",
                "state": "in_progress",
                "application": "Test App",
                "developer": "test.user",
            }
        }
        mock_changeset_response.raise_for_status.return_value = None

        mock_changes_response = MagicMock()
        mock_changes_response.json.return_value = {
            "result": [
                {
                    "sys_id": "456",
                    "name": "test_file.py",
                    "type": "file",
                    "update_set": "123",
                }
            ]
        }
        mock_changes_response.raise_for_status.return_value = None

        # Set up the mock to return different responses for different URLs
        def side_effect(*args, **kwargs):
            url = args[0]
            if "sys_update_set" in url:
                return mock_changeset_response
            elif "sys_update_xml" in url:
                return mock_changes_response
            return None

        mock_get.side_effect = side_effect

        # Call the function
        result = await self.changeset_resource.get_changeset("123")

        # Verify the result
        result_json = json.loads(result)
        self.assertEqual(result_json["changeset"]["sys_id"], "123")
        self.assertEqual(result_json["changeset"]["name"], "Test Changeset")
        self.assertEqual(len(result_json["changes"]), 1)
        self.assertEqual(result_json["changes"][0]["sys_id"], "456")
        self.assertEqual(result_json["changes"][0]["name"], "test_file.py")
        self.assertEqual(result_json["change_count"], 1)

        # Verify the API calls
        self.assertEqual(mock_get.call_count, 2)
        first_call_args, first_call_kwargs = mock_get.call_args_list[0]
        self.assertEqual(
            first_call_args[0], "https://test.service-now.com/api/now/table/sys_update_set/123"
        )
        self.assertEqual(first_call_kwargs["headers"], {"Authorization": "Bearer test"})

        second_call_args, second_call_kwargs = mock_get.call_args_list[1]
        self.assertEqual(
            second_call_args[0], "https://test.service-now.com/api/now/table/sys_update_xml"
        )
        self.assertEqual(second_call_kwargs["headers"], {"Authorization": "Bearer test"})
        self.assertEqual(second_call_kwargs["params"]["sysparm_query"], "update_set=123")

    @patch("servicenow_mcp.resources.changesets.requests.get")
    async def test_list_changesets_error(self, mock_get):
        """Test listing changesets with an error."""
        # Mock response
        mock_get.side_effect = requests.exceptions.RequestException("Test error")

        # Call the function
        params = ChangesetListParams()
        result = await self.changeset_resource.list_changesets(params)

        # Verify the result
        result_json = json.loads(result)
        self.assertIn("error", result_json)
        self.assertIn("Test error", result_json["error"])

    @patch("servicenow_mcp.resources.changesets.requests.get")
    async def test_get_changeset_error(self, mock_get):
        """Test getting a changeset with an error."""
        # Mock response
        mock_get.side_effect = requests.exceptions.RequestException("Test error")

        # Call the function
        result = await self.changeset_resource.get_changeset("123")

        # Verify the result
        result_json = json.loads(result)
        self.assertIn("error", result_json)
        self.assertIn("Test error", result_json["error"])


class TestChangesetListParams(unittest.TestCase):
    """Tests for the ChangesetListParams class."""

    def test_changeset_list_params(self):
        """Test ChangesetListParams."""
        params = ChangesetListParams(
            limit=20,
            offset=10,
            state="in_progress",
            application="Test App",
            developer="test.user",
        )
        self.assertEqual(params.limit, 20)
        self.assertEqual(params.offset, 10)
        self.assertEqual(params.state, "in_progress")
        self.assertEqual(params.application, "Test App")
        self.assertEqual(params.developer, "test.user")

    def test_changeset_list_params_defaults(self):
        """Test ChangesetListParams defaults."""
        params = ChangesetListParams()
        self.assertEqual(params.limit, 10)
        self.assertEqual(params.offset, 0)
        self.assertIsNone(params.state)
        self.assertIsNone(params.application)
        self.assertIsNone(params.developer)


if __name__ == "__main__":
    unittest.main() 