#!/bin/bash

# Create directory if it doesn't exist
mkdir -p scripts

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing..."
    pip install uv
fi

# Create virtual environment
echo "Creating virtual environment..."
uv venv .venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
uv pip install -e ".[dev]"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOL
# ServiceNow Instance Configuration
SERVICENOW_INSTANCE_URL=https://your-instance.service-now.com
SERVICENOW_USERNAME=your-username
SERVICENOW_PASSWORD=your-password

# OAuth Configuration (if using OAuth)
SERVICENOW_AUTH_TYPE=basic
# SERVICENOW_AUTH_TYPE=oauth
# SERVICENOW_CLIENT_ID=your-client-id
# SERVICENOW_CLIENT_SECRET=your-client-secret
# SERVICENOW_TOKEN_URL=https://your-instance.service-now.com/oauth_token.do

# API Key Configuration (if using API Key)
# SERVICENOW_AUTH_TYPE=api_key
# SERVICENOW_API_KEY=your-api-key
# SERVICENOW_API_KEY_HEADER=X-ServiceNow-API-Key

# Debug Configuration
SERVICENOW_DEBUG=false
SERVICENOW_TIMEOUT=30
EOL
    echo "Please update the .env file with your ServiceNow credentials."
fi

echo "Setup complete! You can now run the server with:"
echo "python examples/basic_server.py"
echo ""
echo "To use with Claude Desktop, copy the configuration from examples/claude_desktop_config.json to your Claude Desktop configuration." 