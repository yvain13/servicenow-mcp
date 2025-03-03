# Changeset Management in ServiceNow MCP

This document provides detailed information about the Changeset Management tools available in the ServiceNow MCP server.

## Overview

Changesets in ServiceNow (also known as Update Sets) are collections of customizations and configurations that can be moved between ServiceNow instances. They allow developers to track changes, collaborate on development, and promote changes through different environments (development, test, production).

The ServiceNow MCP server provides tools for managing changesets, allowing Claude to help with:

- Tracking development changes
- Creating and managing changesets
- Committing and publishing changesets
- Adding files to changesets
- Analyzing changeset contents

## Available Tools

### 1. list_changesets

Lists changesets from ServiceNow with various filtering options.

**Parameters:**
- `limit` (optional, default: 10) - Maximum number of records to return
- `offset` (optional, default: 0) - Offset to start from
- `state` (optional) - Filter by state (e.g., "in_progress", "complete", "published")
- `application` (optional) - Filter by application
- `developer` (optional) - Filter by developer
- `timeframe` (optional) - Filter by timeframe ("recent", "last_week", "last_month")
- `query` (optional) - Additional query string

**Example:**
```python
result = list_changesets({
    "limit": 20,
    "state": "in_progress",
    "developer": "john.doe",
    "timeframe": "recent"
})
```

### 2. get_changeset_details

Gets detailed information about a specific changeset, including all changes contained within it.

**Parameters:**
- `changeset_id` (required) - Changeset ID or sys_id

**Example:**
```python
result = get_changeset_details({
    "changeset_id": "sys_update_set_123"
})
```

### 3. create_changeset

Creates a new changeset in ServiceNow.

**Parameters:**
- `name` (required) - Name of the changeset
- `description` (optional) - Description of the changeset
- `application` (required) - Application the changeset belongs to
- `developer` (optional) - Developer responsible for the changeset

**Example:**
```python
result = create_changeset({
    "name": "HR Portal Login Fix",
    "description": "Fixes the login issue on the HR Portal",
    "application": "HR Portal",
    "developer": "john.doe"
})
```

### 4. update_changeset

Updates an existing changeset in ServiceNow.

**Parameters:**
- `changeset_id` (required) - Changeset ID or sys_id
- `name` (optional) - Name of the changeset
- `description` (optional) - Description of the changeset
- `state` (optional) - State of the changeset
- `developer` (optional) - Developer responsible for the changeset

**Example:**
```python
result = update_changeset({
    "changeset_id": "sys_update_set_123",
    "name": "HR Portal Login Fix - Updated",
    "description": "Updated description for the login fix",
    "state": "in_progress"
})
```

### 5. commit_changeset

Commits a changeset in ServiceNow, marking it as complete.

**Parameters:**
- `changeset_id` (required) - Changeset ID or sys_id
- `commit_message` (optional) - Commit message

**Example:**
```python
result = commit_changeset({
    "changeset_id": "sys_update_set_123",
    "commit_message": "Completed the login fix with all necessary changes"
})
```

### 6. publish_changeset

Publishes a changeset in ServiceNow, making it available for deployment to other environments.

**Parameters:**
- `changeset_id` (required) - Changeset ID or sys_id
- `publish_notes` (optional) - Notes for publishing

**Example:**
```python
result = publish_changeset({
    "changeset_id": "sys_update_set_123",
    "publish_notes": "Ready for deployment to test environment"
})
```

### 7. add_file_to_changeset

Adds a file to a changeset in ServiceNow.

**Parameters:**
- `changeset_id` (required) - Changeset ID or sys_id
- `file_path` (required) - Path of the file to add
- `file_content` (required) - Content of the file

**Example:**
```python
result = add_file_to_changeset({
    "changeset_id": "sys_update_set_123",
    "file_path": "scripts/login_fix.js",
    "file_content": "function fixLogin() { ... }"
})
```

## Resources

The ServiceNow MCP server also provides the following resources for accessing changesets:

### 1. changesets://list

URI for listing changesets from ServiceNow.

**Example:**
```
changesets://list
```

### 2. changeset://{changeset_id}

URI for getting a specific changeset from ServiceNow by ID.

**Example:**
```
changeset://sys_update_set_123
```

## Changeset States

Changesets in ServiceNow typically go through the following states:

1. **in_progress** - The changeset is being actively worked on
2. **complete** - The changeset has been completed and is ready for review
3. **published** - The changeset has been published and is ready for deployment
4. **deployed** - The changeset has been deployed to another environment

## Best Practices

1. **Naming Convention**: Use a consistent naming convention for changesets that includes the application name, feature/fix description, and optionally a ticket number.

2. **Scope**: Keep changesets focused on a single feature, fix, or improvement to make them easier to review and deploy.

3. **Documentation**: Include detailed descriptions for changesets to help reviewers understand the purpose and impact of the changes.

4. **Testing**: Test all changes thoroughly before committing and publishing a changeset.

5. **Review**: Have changesets reviewed by another developer before publishing to catch potential issues.

6. **Backup**: Always back up important configurations before deploying changesets to production.

## Example Workflow

1. Create a new changeset for a specific feature or fix
2. Make the necessary changes in ServiceNow
3. Add any required files to the changeset
4. Test the changes thoroughly
5. Commit the changeset with a detailed message
6. Have the changeset reviewed
7. Publish the changeset
8. Deploy the changeset to the target environment

## Troubleshooting

### Common Issues

1. **Changeset Conflicts**: When multiple developers modify the same configuration item, conflicts can occur. Resolve these by carefully reviewing and merging the changes.

2. **Missing Dependencies**: Changesets may depend on other configurations that aren't included. Ensure all dependencies are identified and included.

3. **Deployment Failures**: If a changeset fails to deploy, check the deployment logs for specific errors and address them before retrying.

4. **Permission Issues**: Ensure the user has the necessary permissions to create, commit, and publish changesets.

### Error Messages

- **"Cannot find changeset"**: The specified changeset ID does not exist or is not accessible.
- **"Missing required fields"**: One or more required parameters are missing.
- **"Invalid state transition"**: Attempting to change the state of a changeset in an invalid way (e.g., from "in_progress" directly to "published").
- **"Application not found"**: The specified application does not exist or is not accessible. 