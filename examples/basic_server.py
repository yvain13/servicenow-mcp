"""
Basic example of using the ServiceNow MCP server.
"""

import os
from dotenv import load_dotenv

from servicenow_mcp import ServiceNowMCP
from servicenow_mcp.utils.config import (
    AuthConfig,
    AuthType,
    BasicAuthConfig,
    ServerConfig,
)


def main():
    """Run the example."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get configuration from environment variables
    instance_url = os.environ.get("SERVICENOW_INSTANCE_URL")
    username = os.environ.get("SERVICENOW_USERNAME")
    password = os.environ.get("SERVICENOW_PASSWORD")
    
    if not instance_url or not username or not password:
        print("Please set SERVICENOW_INSTANCE_URL, SERVICENOW_USERNAME, and SERVICENOW_PASSWORD environment variables")
        return
    
    # Create server configuration
    config = ServerConfig(
        instance_url=instance_url,
        auth=AuthConfig(
            type=AuthType.BASIC,
            basic=BasicAuthConfig(
                username=username,
                password=password,
            ),
        ),
    )
    
    # Create and start server
    server = ServiceNowMCP(config)
    print(f"Starting ServiceNow MCP server for {config.instance_url}")
    server.start()


if __name__ == "__main__":
    main() 