"""
Tests for the configuration module.
"""

from servicenow_mcp.utils.config import (
    ApiKeyConfig,
    AuthConfig,
    AuthType,
    BasicAuthConfig,
    OAuthConfig,
    ServerConfig,
)


def test_auth_type_enum():
    """Test the AuthType enum."""
    assert AuthType.BASIC == "basic"
    assert AuthType.OAUTH == "oauth"
    assert AuthType.API_KEY == "api_key"


def test_basic_auth_config():
    """Test the BasicAuthConfig class."""
    config = BasicAuthConfig(username="user", password="pass")
    assert config.username == "user"
    assert config.password == "pass"


def test_oauth_config():
    """Test the OAuthConfig class."""
    config = OAuthConfig(
        client_id="client_id",
        client_secret="client_secret",
        username="user",
        password="pass",
    )
    assert config.client_id == "client_id"
    assert config.client_secret == "client_secret"
    assert config.username == "user"
    assert config.password == "pass"
    assert config.token_url is None
    
    config = OAuthConfig(
        client_id="client_id",
        client_secret="client_secret",
        username="user",
        password="pass",
        token_url="https://example.com/token",
    )
    assert config.token_url == "https://example.com/token"


def test_api_key_config():
    """Test the ApiKeyConfig class."""
    config = ApiKeyConfig(api_key="api_key")
    assert config.api_key == "api_key"
    assert config.header_name == "X-ServiceNow-API-Key"
    
    config = ApiKeyConfig(api_key="api_key", header_name="Custom-Header")
    assert config.header_name == "Custom-Header"


def test_auth_config():
    """Test the AuthConfig class."""
    # Basic auth
    config = AuthConfig(
        type=AuthType.BASIC,
        basic=BasicAuthConfig(username="user", password="pass"),
    )
    assert config.type == AuthType.BASIC
    assert config.basic is not None
    assert config.basic.username == "user"
    assert config.basic.password == "pass"
    assert config.oauth is None
    assert config.api_key is None
    
    # OAuth
    config = AuthConfig(
        type=AuthType.OAUTH,
        oauth=OAuthConfig(
            client_id="client_id",
            client_secret="client_secret",
            username="user",
            password="pass",
        ),
    )
    assert config.type == AuthType.OAUTH
    assert config.oauth is not None
    assert config.oauth.client_id == "client_id"
    assert config.basic is None
    assert config.api_key is None
    
    # API key
    config = AuthConfig(
        type=AuthType.API_KEY,
        api_key=ApiKeyConfig(api_key="api_key"),
    )
    assert config.type == AuthType.API_KEY
    assert config.api_key is not None
    assert config.api_key.api_key == "api_key"
    assert config.basic is None
    assert config.oauth is None


def test_server_config():
    """Test the ServerConfig class."""
    config = ServerConfig(
        instance_url="https://example.service-now.com",
        auth=AuthConfig(
            type=AuthType.BASIC,
            basic=BasicAuthConfig(username="user", password="pass"),
        ),
    )
    assert config.instance_url == "https://example.service-now.com"
    assert config.auth.type == AuthType.BASIC
    assert config.debug is False
    assert config.timeout == 30
    assert config.api_url == "https://example.service-now.com/api/now"
    
    config = ServerConfig(
        instance_url="https://example.service-now.com",
        auth=AuthConfig(
            type=AuthType.BASIC,
            basic=BasicAuthConfig(username="user", password="pass"),
        ),
        debug=True,
        timeout=60,
    )
    assert config.debug is True
    assert config.timeout == 60 