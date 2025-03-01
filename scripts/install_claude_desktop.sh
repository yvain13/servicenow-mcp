#!/bin/bash

# Check if Claude Desktop config file exists
CONFIG_FILE="$HOME/.config/claude/claude_desktop_config.json"
BACKUP_FILE="$HOME/.config/claude/claude_desktop_config.json.bak"

# Create config directory if it doesn't exist
mkdir -p "$HOME/.config/claude"

# Backup existing config if it exists
if [ -f "$CONFIG_FILE" ]; then
    echo "Backing up existing Claude Desktop configuration..."
    cp "$CONFIG_FILE" "$BACKUP_FILE"
fi

# Get the absolute path to the current directory
CURRENT_DIR=$(pwd)

# Create or update the Claude Desktop config
echo "Creating Claude Desktop configuration..."
cat > "$CONFIG_FILE" << EOL
{
  "mcpServers": {
    "servicenow": {
      "command": "$CURRENT_DIR/.venv/bin/python",
      "args": [
        "-m",
        "servicenow_mcp.cli"
      ],
      "env": {
        "SERVICENOW_INSTANCE_URL": "$(grep SERVICENOW_INSTANCE_URL .env | cut -d '=' -f2)",
        "SERVICENOW_USERNAME": "$(grep SERVICENOW_USERNAME .env | cut -d '=' -f2)",
        "SERVICENOW_PASSWORD": "$(grep SERVICENOW_PASSWORD .env | cut -d '=' -f2)",
        "SERVICENOW_AUTH_TYPE": "$(grep SERVICENOW_AUTH_TYPE .env | head -1 | cut -d '=' -f2)"
      }
    }
  }
}
EOL

echo "ServiceNow MCP server installed in Claude Desktop!"
echo "You can now use it by opening Claude Desktop and selecting the ServiceNow MCP server."
echo ""
echo "If you need to update your ServiceNow credentials, edit the .env file and run this script again." 