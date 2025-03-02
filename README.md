# ServiceNow MCP Server

A Model Completion Protocol (MCP) server implementation for ServiceNow, allowing Claude to interact with ServiceNow instances.

## Overview

This project implements an MCP server that enables Claude to connect to ServiceNow instances, retrieve data, and perform actions through the ServiceNow API. It serves as a bridge between Claude and ServiceNow, allowing for seamless integration.

## Features

- Connect to ServiceNow instances using various authentication methods (Basic, OAuth, API Key)
- Query ServiceNow records and tables
- Create, update, and delete ServiceNow records
- Execute ServiceNow scripts and workflows
- Access and query the ServiceNow Service Catalog
- Debug mode for troubleshooting

## Installation

### Prerequisites

- Python 3.11 or higher
- A ServiceNow instance with appropriate access credentials

### Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/servicenow-mcp.git
   cd servicenow-mcp
   ```

2. Create a virtual environment and install the package:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .
   ```

3. Create a `.env` file with your ServiceNow credentials:
   ```
   SERVICENOW_INSTANCE_URL=https://your-instance.service-now.com
   SERVICENOW_USERNAME=your-username
   SERVICENOW_PASSWORD=your-password
   SERVICENOW_AUTH_TYPE=basic  # or oauth, api_key
   ```

## Usage

### Running the Server

To start the MCP server:

```
python -m servicenow_mcp.cli
```

Or with environment variables:

```
SERVICENOW_INSTANCE_URL=https://your-instance.service-now.com SERVICENOW_USERNAME=your-username SERVICENOW_PASSWORD=your-password SERVICENOW_AUTH_TYPE=basic python -m servicenow_mcp.cli
```

### Available Tools

The ServiceNow MCP server provides the following tools:

#### Incident Management Tools

1. **create_incident** - Create a new incident in ServiceNow
   - Parameters: short_description, description, caller_id, category, subcategory, priority, impact, urgency, assigned_to, assignment_group

2. **update_incident** - Update an existing incident in ServiceNow
   - Parameters: incident_id, short_description, description, state, category, subcategory, priority, impact, urgency, assigned_to, assignment_group, work_notes, close_notes, close_code

3. **add_comment** - Add a comment to an incident in ServiceNow
   - Parameters: incident_id, comment, is_work_note

4. **resolve_incident** - Resolve an incident in ServiceNow
   - Parameters: incident_id, resolution_code, resolution_notes

5. **list_incidents** - List incidents from ServiceNow
   - Parameters: limit, offset, state, assigned_to, category, query

#### Service Catalog Tools

1. **list_catalog_items** - List service catalog items from ServiceNow
   - Parameters: limit, offset, category, query, active

2. **get_catalog_item** - Get a specific service catalog item from ServiceNow
   - Parameters: item_id

3. **list_catalog_categories** - List service catalog categories from ServiceNow
   - Parameters: limit, offset, query, active

### Using the MCP CLI

The ServiceNow MCP server can be installed with the MCP CLI, which provides a convenient way to register the server with Claude.

#### Installing the Server with MCP CLI

```bash
# Install the ServiceNow MCP server with environment variables from .env file
mcp install src/servicenow_mcp/server.py -f .env
```

This command will register the ServiceNow MCP server with Claude and configure it to use the environment variables from the .env file.

### Integration with Claude Desktop

To configure the ServiceNow MCP server in Claude Desktop:

1. Edit the Claude Desktop configuration file at `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or the appropriate path for your OS:

```json
{
  "mcpServers": {
    "ServiceNow": {
      "command": "/Users/yourusername/dev/servicenow-mcp/.venv/bin/python",
      "args": [
        "-m",
        "servicenow_mcp.cli"
      ],
      "env": {
        "SERVICENOW_INSTANCE_URL": "https://your-instance.service-now.com",
        "SERVICENOW_USERNAME": "your-username",
        "SERVICENOW_PASSWORD": "your-password",
        "SERVICENOW_AUTH_TYPE": "basic"
      }
    }
  }
}
```

Make sure to replace the paths and credentials with your actual values.

2. Restart Claude Desktop to apply the changes

### Example Usage with Claude

Once the ServiceNow MCP server is configured with Claude Desktop, you can ask Claude to perform actions like:

#### Incident Management Examples
- "Create a new incident for a network outage in the east region"
- "Update the priority of incident INC0010001 to high"
- "Add a comment to incident INC0010001 saying the issue is being investigated"
- "Resolve incident INC0010001 with a note that the server was restarted"
- "List all high priority incidents"
- "Show me the details of incident INC0010001"

#### Service Catalog Examples
- "Show me all items in the service catalog"
- "List all service catalog categories"
- "Get details about the laptop request catalog item"
- "Show me all catalog items in the Hardware category"
- "Search for 'software' in the service catalog"

## Authentication Methods

### Basic Authentication

```
SERVICENOW_AUTH_TYPE=basic
SERVICENOW_USERNAME=your-username
SERVICENOW_PASSWORD=your-password
```

### OAuth Authentication

```
SERVICENOW_AUTH_TYPE=oauth
SERVICENOW_CLIENT_ID=your-client-id
SERVICENOW_CLIENT_SECRET=your-client-secret
SERVICENOW_TOKEN_URL=https://your-instance.service-now.com/oauth_token.do
```

### API Key Authentication

```
SERVICENOW_AUTH_TYPE=api_key
SERVICENOW_API_KEY=your-api-key
```

## Development

### Running Tests

```
pytest
```

### Example Scripts

The repository includes several example scripts to demonstrate how to use the ServiceNow MCP server:

#### Incident Management Demo

The `examples/claude_incident_demo.py` script demonstrates how to use the ServiceNow MCP server with Claude Desktop to manage incidents:

```bash
python examples/claude_incident_demo.py
```

#### Service Catalog Integration Test

The `examples/catalog_integration_test.py` script demonstrates how to use the catalog tools directly to interact with the ServiceNow Service Catalog:

```bash
python examples/catalog_integration_test.py
```

#### Service Catalog Demo

The `examples/claude_catalog_demo.py` script demonstrates how to use the ServiceNow MCP server with Claude Desktop to interact with the ServiceNow Service Catalog:

```bash
python examples/claude_catalog_demo.py
```

### Documentation

Additional documentation is available in the `docs` directory:

- [Catalog Integration](docs/catalog.md) - Detailed information about the Service Catalog integration

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 