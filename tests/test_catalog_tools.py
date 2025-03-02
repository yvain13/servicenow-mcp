"""
Tests for the ServiceNow MCP catalog tools.
"""

import unittest
from unittest.mock import MagicMock, patch

import requests

from servicenow_mcp.auth.auth_manager import AuthManager
from servicenow_mcp.tools.catalog_tools import (
    GetCatalogItemParams,
    ListCatalogCategoriesParams,
    ListCatalogItemsParams,
    get_catalog_item,
    get_catalog_item_variables,
    list_catalog_categories,
    list_catalog_items,
)
from servicenow_mcp.utils.config import AuthConfig, AuthType, BasicAuthConfig, ServerConfig


class TestCatalogTools(unittest.TestCase):
    """Test cases for the catalog tools."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a mock server config
        self.config = ServerConfig(
            instance_url="https://example.service-now.com",
            auth=AuthConfig(
                type=AuthType.BASIC,
                basic=BasicAuthConfig(username="admin", password="password"),
            ),
        )

        # Create a mock auth manager
        self.auth_manager = MagicMock(spec=AuthManager)
        self.auth_manager.get_headers.return_value = {"Authorization": "Basic YWRtaW46cGFzc3dvcmQ="}

    @patch("servicenow_mcp.tools.catalog_tools.requests.get")
    def test_list_catalog_items(self, mock_get):
        """Test listing catalog items."""
        # Mock the response from ServiceNow
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": [
                {
                    "sys_id": "item1",
                    "name": "Laptop",
                    "short_description": "Request a new laptop",
                    "category": "Hardware",
                    "price": "1000",
                    "picture": "laptop.jpg",
                    "active": "true",
                    "order": "100",
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the function
        params = ListCatalogItemsParams(
            limit=10,
            offset=0,
            category="Hardware",
            query="laptop",
            active=True,
        )
        result = list_catalog_items(self.config, self.auth_manager, params)

        # Check the result
        self.assertTrue(result["success"])
        self.assertEqual(len(result["items"]), 1)
        self.assertEqual(result["items"][0]["name"], "Laptop")
        self.assertEqual(result["items"][0]["category"], "Hardware")

        # Check that the correct URL and parameters were used
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://example.service-now.com/api/now/table/sc_cat_item")
        self.assertEqual(kwargs["params"]["sysparm_limit"], 10)
        self.assertEqual(kwargs["params"]["sysparm_offset"], 0)
        self.assertIn("sysparm_query", kwargs["params"])
        self.assertIn("active=true", kwargs["params"]["sysparm_query"])
        self.assertIn("category=Hardware", kwargs["params"]["sysparm_query"])
        self.assertIn("short_descriptionLIKElaptop^ORnameLIKElaptop", kwargs["params"]["sysparm_query"])

    @patch("servicenow_mcp.tools.catalog_tools.requests.get")
    def test_list_catalog_items_error(self, mock_get):
        """Test listing catalog items with an error."""
        # Mock the response from ServiceNow
        mock_get.side_effect = requests.exceptions.RequestException("Error")

        # Call the function
        params = ListCatalogItemsParams(
            limit=10,
            offset=0,
        )
        result = list_catalog_items(self.config, self.auth_manager, params)

        # Check the result
        self.assertFalse(result["success"])
        self.assertEqual(len(result["items"]), 0)
        self.assertIn("Error", result["message"])

    @patch("servicenow_mcp.tools.catalog_tools.get_catalog_item_variables")
    @patch("servicenow_mcp.tools.catalog_tools.requests.get")
    def test_get_catalog_item(self, mock_get, mock_get_variables):
        """Test getting a specific catalog item."""
        # Mock the response from ServiceNow
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": {
                "sys_id": "item1",
                "name": "Laptop",
                "short_description": "Request a new laptop",
                "description": "Request a new laptop for work",
                "category": "Hardware",
                "price": "1000",
                "picture": "laptop.jpg",
                "active": "true",
                "order": "100",
                "delivery_time": "3 days",
                "availability": "In Stock",
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Mock the variables
        mock_get_variables.return_value = [
            {
                "sys_id": "var1",
                "name": "model",
                "label": "Laptop Model",
                "type": "string",
                "mandatory": "true",
                "default_value": "MacBook Pro",
                "help_text": "Select the laptop model",
                "order": "100",
            }
        ]

        # Call the function
        params = GetCatalogItemParams(item_id="item1")
        result = get_catalog_item(self.config, self.auth_manager, params)

        # Check the result
        self.assertTrue(result.success)
        self.assertEqual(result.data["name"], "Laptop")
        self.assertEqual(result.data["category"], "Hardware")
        self.assertEqual(len(result.data["variables"]), 1)
        self.assertEqual(result.data["variables"][0]["name"], "model")

        # Check that the correct URL and parameters were used
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://example.service-now.com/api/now/table/sc_cat_item/item1")

    @patch("servicenow_mcp.tools.catalog_tools.requests.get")
    def test_get_catalog_item_not_found(self, mock_get):
        """Test getting a catalog item that doesn't exist."""
        # Mock the response from ServiceNow
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": {}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the function
        params = GetCatalogItemParams(item_id="nonexistent")
        result = get_catalog_item(self.config, self.auth_manager, params)

        # Check the result
        self.assertFalse(result.success)
        self.assertIn("not found", result.message)
        self.assertIsNone(result.data)

    @patch("servicenow_mcp.tools.catalog_tools.requests.get")
    def test_get_catalog_item_error(self, mock_get):
        """Test getting a catalog item with an error."""
        # Mock the response from ServiceNow
        mock_get.side_effect = requests.exceptions.RequestException("Error")

        # Call the function
        params = GetCatalogItemParams(item_id="item1")
        result = get_catalog_item(self.config, self.auth_manager, params)

        # Check the result
        self.assertFalse(result.success)
        self.assertIn("Error", result.message)
        self.assertIsNone(result.data)

    @patch("servicenow_mcp.tools.catalog_tools.requests.get")
    def test_get_catalog_item_variables(self, mock_get):
        """Test getting variables for a catalog item."""
        # Mock the response from ServiceNow
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": [
                {
                    "sys_id": "var1",
                    "name": "model",
                    "question_text": "Laptop Model",
                    "type": "string",
                    "mandatory": "true",
                    "default_value": "MacBook Pro",
                    "help_text": "Select the laptop model",
                    "order": "100",
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the function
        result = get_catalog_item_variables(self.config, self.auth_manager, "item1")

        # Check the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["name"], "model")
        self.assertEqual(result[0]["label"], "Laptop Model")
        self.assertEqual(result[0]["type"], "string")

        # Check that the correct URL and parameters were used
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://example.service-now.com/api/now/table/item_option_new")
        self.assertEqual(kwargs["params"]["sysparm_query"], "cat_item=item1^ORDERBYorder")

    @patch("servicenow_mcp.tools.catalog_tools.requests.get")
    def test_get_catalog_item_variables_error(self, mock_get):
        """Test getting variables for a catalog item with an error."""
        # Mock the response from ServiceNow
        mock_get.side_effect = requests.exceptions.RequestException("Error")

        # Call the function
        result = get_catalog_item_variables(self.config, self.auth_manager, "item1")

        # Check the result
        self.assertEqual(len(result), 0)

    @patch("servicenow_mcp.tools.catalog_tools.requests.get")
    def test_list_catalog_categories(self, mock_get):
        """Test listing catalog categories."""
        # Mock the response from ServiceNow
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "result": [
                {
                    "sys_id": "cat1",
                    "title": "Hardware",
                    "description": "Hardware requests",
                    "parent": "",
                    "icon": "hardware.png",
                    "active": "true",
                    "order": "100",
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the function
        params = ListCatalogCategoriesParams(
            limit=10,
            offset=0,
            query="hardware",
            active=True,
        )
        result = list_catalog_categories(self.config, self.auth_manager, params)

        # Check the result
        self.assertTrue(result["success"])
        self.assertEqual(len(result["categories"]), 1)
        self.assertEqual(result["categories"][0]["title"], "Hardware")
        self.assertEqual(result["categories"][0]["description"], "Hardware requests")

        # Check that the correct URL and parameters were used
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://example.service-now.com/api/now/table/sc_category")
        self.assertEqual(kwargs["params"]["sysparm_limit"], 10)
        self.assertEqual(kwargs["params"]["sysparm_offset"], 0)
        self.assertIn("sysparm_query", kwargs["params"])
        self.assertIn("active=true", kwargs["params"]["sysparm_query"])
        self.assertIn("titleLIKEhardware^ORdescriptionLIKEhardware", kwargs["params"]["sysparm_query"])

    @patch("servicenow_mcp.tools.catalog_tools.requests.get")
    def test_list_catalog_categories_error(self, mock_get):
        """Test listing catalog categories with an error."""
        # Mock the response from ServiceNow
        mock_get.side_effect = requests.exceptions.RequestException("Error")

        # Call the function
        params = ListCatalogCategoriesParams(
            limit=10,
            offset=0,
        )
        result = list_catalog_categories(self.config, self.auth_manager, params)

        # Check the result
        self.assertFalse(result["success"])
        self.assertEqual(len(result["categories"]), 0)
        self.assertIn("Error", result["message"])


if __name__ == "__main__":
    unittest.main() 