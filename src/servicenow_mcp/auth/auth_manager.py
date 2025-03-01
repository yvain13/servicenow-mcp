"""
Authentication manager for the ServiceNow MCP server.
"""

import base64
import logging
from typing import Dict, Optional

import requests
from requests.auth import HTTPBasicAuth

from servicenow_mcp.utils.config import AuthConfig, AuthType


logger = logging.getLogger(__name__)


class AuthManager:
    """
    Authentication manager for ServiceNow API.
    
    This class handles authentication with the ServiceNow API using
    different authentication methods.
    """
    
    def __init__(self, config: AuthConfig):
        """
        Initialize the authentication manager.
        
        Args:
            config: Authentication configuration.
        """
        self.config = config
        self.token: Optional[str] = None
        self.token_type: Optional[str] = None
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get the authentication headers for API requests.
        
        Returns:
            Dict[str, str]: Headers to include in API requests.
        """
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        
        if self.config.type == AuthType.BASIC:
            if not self.config.basic:
                raise ValueError("Basic auth configuration is required")
            
            auth_str = f"{self.config.basic.username}:{self.config.basic.password}"
            encoded = base64.b64encode(auth_str.encode()).decode()
            headers["Authorization"] = f"Basic {encoded}"
        
        elif self.config.type == AuthType.OAUTH:
            if not self.token:
                self._get_oauth_token()
            
            headers["Authorization"] = f"{self.token_type} {self.token}"
        
        elif self.config.type == AuthType.API_KEY:
            if not self.config.api_key:
                raise ValueError("API key configuration is required")
            
            headers[self.config.api_key.header_name] = self.config.api_key.api_key
        
        return headers
    
    def _get_oauth_token(self):
        """
        Get an OAuth token from ServiceNow.
        
        Raises:
            ValueError: If OAuth configuration is missing or token request fails.
        """
        if not self.config.oauth:
            raise ValueError("OAuth configuration is required")
        
        oauth_config = self.config.oauth
        
        # Determine token URL
        token_url = oauth_config.token_url
        if not token_url:
            # Extract instance name from instance URL
            instance_parts = oauth_config.instance_url.split(".")
            if len(instance_parts) < 2:
                raise ValueError(f"Invalid instance URL: {oauth_config.instance_url}")
            
            instance_name = instance_parts[0].split("//")[-1]
            token_url = f"https://{instance_name}.service-now.com/oauth_token.do"
        
        # Request token
        data = {
            "grant_type": "password",
            "client_id": oauth_config.client_id,
            "client_secret": oauth_config.client_secret,
            "username": oauth_config.username,
            "password": oauth_config.password,
        }
        
        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.token = token_data.get("access_token")
            self.token_type = token_data.get("token_type", "Bearer")
            
            if not self.token:
                raise ValueError("No access token in response")
            
        except requests.RequestException as e:
            logger.error(f"Failed to get OAuth token: {e}")
            raise ValueError(f"Failed to get OAuth token: {e}")
    
    def refresh_token(self):
        """Refresh the OAuth token if using OAuth authentication."""
        if self.config.type == AuthType.OAUTH:
            self._get_oauth_token() 