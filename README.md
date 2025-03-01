# ServiceNow MCP Server

A Model Completion Protocol (MCP) server implementation for ServiceNow, allowing Claude to interact with ServiceNow instances.

## Overview

This project implements an MCP server that enables Claude to connect to ServiceNow instances, retrieve data, and perform actions through the ServiceNow API. It serves as a bridge between Claude and ServiceNow, allowing for seamless integration.

## Features

- Connect to ServiceNow instances using various authentication methods (Basic, OAuth, API Key)
- Query ServiceNow records and tables
- Create, update, and delete ServiceNow records
- Execute ServiceNow scripts and workflows
- Debug mode for troubleshooting

## Installation

### Prerequisites

- Python 3.8 or higher
- A ServiceNow instance with appropriate access credentials

### Setup

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/servicenow-mcp.git
   cd servicenow-mcp
   ```

2. Run the setup script:
   ```
   ./scripts/setup.sh
   ```

3. Update the `.env` file with your ServiceNow credentials:
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

### Integration with Claude Desktop

To install the ServiceNow MCP server in Claude Desktop:

```
./scripts/install_claude_desktop.sh
```

This will:
1. Create or update the Claude Desktop configuration
2. Configure the ServiceNow MCP server with your credentials
3. Make the server available in Claude Desktop

### Example Usage

See the `examples` directory for sample scripts:

- `examples/basic_server.py`: Basic server implementation
- `examples/claude_desktop_config.json`: Sample Claude Desktop configuration

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

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 