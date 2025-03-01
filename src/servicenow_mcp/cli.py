"""
Command-line interface for the ServiceNow MCP server.
"""

import argparse
import logging
import os
import sys
from typing import Dict, Optional

from dotenv import load_dotenv

from servicenow_mcp.server import ServiceNowMCP
from servicenow_mcp.utils.config import (
    ApiKeyConfig,
    AuthConfig,
    AuthType,
    BasicAuthConfig,
    OAuthConfig,
    ServerConfig,
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="ServiceNow MCP Server")
    
    # Server configuration
    parser.add_argument(
        "--instance-url",
        help="ServiceNow instance URL (e.g., https://instance.service-now.com)",
        default=os.environ.get("SERVICENOW_INSTANCE_URL"),
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
        default=os.environ.get("SERVICENOW_DEBUG", "false").lower() == "true",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        help="Request timeout in seconds",
        default=int(os.environ.get("SERVICENOW_TIMEOUT", "30")),
    )
    
    # Authentication
    auth_group = parser.add_argument_group("Authentication")
    auth_group.add_argument(
        "--auth-type",
        choices=["basic", "oauth", "api_key"],
        help="Authentication type",
        default=os.environ.get("SERVICENOW_AUTH_TYPE", "basic"),
    )
    
    # Basic auth
    basic_group = parser.add_argument_group("Basic Authentication")
    basic_group.add_argument(
        "--username",
        help="ServiceNow username",
        default=os.environ.get("SERVICENOW_USERNAME"),
    )
    basic_group.add_argument(
        "--password",
        help="ServiceNow password",
        default=os.environ.get("SERVICENOW_PASSWORD"),
    )
    
    # OAuth
    oauth_group = parser.add_argument_group("OAuth Authentication")
    oauth_group.add_argument(
        "--client-id",
        help="OAuth client ID",
        default=os.environ.get("SERVICENOW_CLIENT_ID"),
    )
    oauth_group.add_argument(
        "--client-secret",
        help="OAuth client secret",
        default=os.environ.get("SERVICENOW_CLIENT_SECRET"),
    )
    oauth_group.add_argument(
        "--token-url",
        help="OAuth token URL",
        default=os.environ.get("SERVICENOW_TOKEN_URL"),
    )
    
    # API Key
    api_key_group = parser.add_argument_group("API Key Authentication")
    api_key_group.add_argument(
        "--api-key",
        help="ServiceNow API key",
        default=os.environ.get("SERVICENOW_API_KEY"),
    )
    api_key_group.add_argument(
        "--api-key-header",
        help="API key header name",
        default=os.environ.get("SERVICENOW_API_KEY_HEADER", "X-ServiceNow-API-Key"),
    )
    
    return parser.parse_args()


def create_config(args) -> ServerConfig:
    """
    Create server configuration from command-line arguments.
    
    Args:
        args: Command-line arguments.
        
    Returns:
        ServerConfig: Server configuration.
        
    Raises:
        ValueError: If required configuration is missing.
    """
    if not args.instance_url:
        raise ValueError("ServiceNow instance URL is required")
    
    # Create authentication configuration
    auth_type = AuthType(args.auth_type)
    auth_config = AuthConfig(type=auth_type)
    
    if auth_type == AuthType.BASIC:
        if not args.username or not args.password:
            raise ValueError("Username and password are required for basic authentication")
        
        auth_config.basic = BasicAuthConfig(
            username=args.username,
            password=args.password,
        )
    
    elif auth_type == AuthType.OAUTH:
        if not args.client_id or not args.client_secret or not args.username or not args.password:
            raise ValueError(
                "Client ID, client secret, username, and password are required for OAuth authentication"
            )
        
        auth_config.oauth = OAuthConfig(
            client_id=args.client_id,
            client_secret=args.client_secret,
            username=args.username,
            password=args.password,
            token_url=args.token_url,
        )
    
    elif auth_type == AuthType.API_KEY:
        if not args.api_key:
            raise ValueError("API key is required for API key authentication")
        
        auth_config.api_key = ApiKeyConfig(
            api_key=args.api_key,
            header_name=args.api_key_header,
        )
    
    # Create server configuration
    return ServerConfig(
        instance_url=args.instance_url,
        auth=auth_config,
        debug=args.debug,
        timeout=args.timeout,
    )


def main():
    """Main entry point for the CLI."""
    # Load environment variables from .env file
    load_dotenv()
    
    try:
        # Parse command-line arguments
        args = parse_args()
        
        # Create server configuration
        config = create_config(args)
        
        # Create and start server
        server = ServiceNowMCP(config)
        logger.info(f"Starting ServiceNow MCP server for {config.instance_url}")
        server.start()
    
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    except Exception as e:
        logger.exception(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 