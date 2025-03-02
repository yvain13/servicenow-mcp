"""
Tests for the ServiceNow MCP catalog resources.
"""

import unittest
from unittest.mock import MagicMock, patch

from servicenow_mcp.auth.auth_manager import AuthManager
from servicenow_mcp.resources.catalog import (
    CatalogCategoryListParams,
    CatalogItemVariableModel,
    CatalogListParams,
    CatalogResource,
)
from servicenow_mcp.utils.config import AuthConfig, AuthType, BasicAuthConfig, ServerConfig


class TestCatalogResource(unittest.TestCase):
    """Test cases for the catalog resource."""

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

        # Create the resource
        self.resource = CatalogResource(self.config, self.auth_manager)

    @patch("servicenow_mcp.resources.catalog.requests.get")
    async def test_list_catalog_items(self, mock_get):
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

        # Call the method
        params = CatalogListParams(
            limit=10,
            offset=0,
            category="Hardware",
            query="laptop",
        )
        result = await self.resource.list_catalog_items(params)

        # Check the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "Laptop")
        self.assertEqual(result[0].category, "Hardware")
        self.assertTrue(result[0].active)

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

    @patch("servicenow_mcp.resources.catalog.requests.get")
    async def test_list_catalog_items_error(self, mock_get):
        """Test listing catalog items with an error."""
        # Mock the response from ServiceNow
        mock_get.side_effect = Exception("Error")

        # Call the method
        params = CatalogListParams(
            limit=10,
            offset=0,
        )
        result = await self.resource.list_catalog_items(params)

        # Check the result
        self.assertEqual(len(result), 0)

    @patch("servicenow_mcp.resources.catalog.CatalogResource.get_catalog_item_variables")
    @patch("servicenow_mcp.resources.catalog.requests.get")
    async def test_get_catalog_item(self, mock_get, mock_get_variables):
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
            CatalogItemVariableModel(
                sys_id="var1",
                name="model",
                label="Laptop Model",
                type="string",
                mandatory=True,
                default_value="MacBook Pro",
                help_text="Select the laptop model",
                order=100,
            )
        ]

        # Call the method
        result = await self.resource.get_catalog_item("item1")

        # Check the result
        self.assertEqual(result["sys_id"], "item1")
        self.assertEqual(result["name"], "Laptop")
        self.assertEqual(result["category"], "Hardware")
        self.assertTrue(result["active"])
        self.assertEqual(len(result["variables"]), 1)
        self.assertEqual(result["variables"][0].name, "model")

        # Check that the correct URL and parameters were used
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://example.service-now.com/api/now/table/sc_cat_item/item1")

    @patch("servicenow_mcp.resources.catalog.requests.get")
    async def test_get_catalog_item_not_found(self, mock_get):
        """Test getting a catalog item that doesn't exist."""
        # Mock the response from ServiceNow
        mock_response = MagicMock()
        mock_response.json.return_value = {"result": {}}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the method
        result = await self.resource.get_catalog_item("nonexistent")

        # Check the result
        self.assertIn("error", result)
        self.assertIn("not found", result["error"])

    @patch("servicenow_mcp.resources.catalog.requests.get")
    async def test_get_catalog_item_error(self, mock_get):
        """Test getting a catalog item with an error."""
        # Mock the response from ServiceNow
        mock_get.side_effect = Exception("Error")

        # Call the method
        result = await self.resource.get_catalog_item("item1")

        # Check the result
        self.assertIn("error", result)
        self.assertIn("Error", result["error"])

    @patch("servicenow_mcp.resources.catalog.requests.get")
    async def test_get_catalog_item_variables(self, mock_get):
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

        # Call the method
        result = await self.resource.get_catalog_item_variables("item1")

        # Check the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].name, "model")
        self.assertEqual(result[0].label, "Laptop Model")
        self.assertEqual(result[0].type, "string")
        self.assertTrue(result[0].mandatory)

        # Check that the correct URL and parameters were used
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://example.service-now.com/api/now/table/item_option_new")
        self.assertEqual(kwargs["params"]["sysparm_query"], "cat_item=item1^ORDERBYorder")

    @patch("servicenow_mcp.resources.catalog.requests.get")
    async def test_get_catalog_item_variables_error(self, mock_get):
        """Test getting variables for a catalog item with an error."""
        # Mock the response from ServiceNow
        mock_get.side_effect = Exception("Error")

        # Call the method
        result = await self.resource.get_catalog_item_variables("item1")

        # Check the result
        self.assertEqual(len(result), 0)

    @patch("servicenow_mcp.resources.catalog.requests.get")
    async def test_list_catalog_categories(self, mock_get):
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

        # Call the method
        params = CatalogCategoryListParams(
            limit=10,
            offset=0,
            query="hardware",
        )
        result = await self.resource.list_catalog_categories(params)

        # Check the result
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "Hardware")
        self.assertEqual(result[0].description, "Hardware requests")
        self.assertTrue(result[0].active)

        # Check that the correct URL and parameters were used
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "https://example.service-now.com/api/now/table/sc_category")
        self.assertEqual(kwargs["params"]["sysparm_limit"], 10)
        self.assertEqual(kwargs["params"]["sysparm_offset"], 0)
        self.assertIn("sysparm_query", kwargs["params"])
        self.assertIn("active=true", kwargs["params"]["sysparm_query"])
        self.assertIn("titleLIKEhardware^ORdescriptionLIKEhardware", kwargs["params"]["sysparm_query"])

    @patch("servicenow_mcp.resources.catalog.requests.get")
    async def test_list_catalog_categories_error(self, mock_get):
        """Test listing catalog categories with an error."""
        # Mock the response from ServiceNow
        mock_get.side_effect = Exception("Error")

        # Call the method
        params = CatalogCategoryListParams(
            limit=10,
            offset=0,
        )
        result = await self.resource.list_catalog_categories(params)

        # Check the result
        self.assertEqual(len(result), 0)

    @patch("servicenow_mcp.resources.catalog.CatalogResource.get_catalog_item")
    async def test_read(self, mock_get_catalog_item):
        """Test reading a catalog item."""
        # Mock the get_catalog_item method
        mock_get_catalog_item.return_value = {
            "sys_id": "item1",
            "name": "Laptop",
        }

        # Call the method
        result = await self.resource.read({"item_id": "item1"})

        # Check the result
        self.assertEqual(result["sys_id"], "item1")
        self.assertEqual(result["name"], "Laptop")

        # Check that the correct method was called
        mock_get_catalog_item.assert_called_once_with("item1")

    async def test_read_missing_param(self):
        """Test reading a catalog item with missing parameter."""
        # Call the method
        result = await self.resource.read({})

        # Check the result
        self.assertIn("error", result)
        self.assertIn("Missing item_id parameter", result["error"])


if __name__ == "__main__":
    unittest.main() 