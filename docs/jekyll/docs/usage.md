---
title: Usage Guide
layout: default
nav_order: 2
---

# Usage Guide

This guide covers how to use the clearskies MCP Server effectively with MCP clients like Claude Desktop.

## Available Tools

The MCP server exposes tools for documentation, code generation, and module management.

### Documentation Tools

List and query clearskies framework types:

- `list_available_columns` - List all column types
- `list_available_endpoints` - List all endpoint types
- `list_available_backends` - List all backend types
- `list_available_contexts` - List all context types
- `list_available_authentication` - List authentication types
- `list_available_validators` - List validator types

Get detailed information:

- `get_column_info` - Get details for a specific column type
- `get_endpoint_info` - Get details for a specific endpoint type
- `get_backend_info` - Get details for a specific backend type
- `get_authentication_info` - Get authentication details

Explain concepts:

- `explain_concept` - Get detailed explanation of framework concepts

### Code Generation Tools

Generate clearskies code components:

- `generate_model` - Generate a model class definition
- `generate_endpoint` - Generate an endpoint configuration
- `generate_context` - Generate a context wrapper
- `generate_endpoint_group` - Generate an endpoint group
- `generate_model_with_relationships` - Generate models with relationships

### Scaffolding Tools

Create complete applications:

- `scaffold_restful_api` - Create a complete REST API for a single model
- `scaffold_project` - Create a multi-model project

### Module Tools

Manage clearskies extension modules:

- `list_modules` - List all available extension modules
- `get_module_info` - Get detailed info for a specific module
- `explain_module` - Get usage examples for a module
- `get_module_components` - List components in a module
- `suggest_modules` - Suggest modules for specific component types
- `check_module_compatibility` - Check if a module is installed
- `refresh_module_cache` - Refresh the module discovery cache

## Available Resources

The server provides documentation and examples through MCP resources:

### Documentation Resources

- `clearskies://docs/overview` - Framework overview
- `clearskies://docs/models` - Model documentation
- `clearskies://docs/endpoints` - Endpoint documentation
- `clearskies://docs/columns` - Column types documentation
- `clearskies://docs/backends` - Backend documentation
- `clearskies://docs/contexts` - Context documentation
- `clearskies://docs/di` - Dependency injection documentation
- `clearskies://docs/authentication` - Authentication documentation

And many more...

### Example Resources

- `clearskies://examples/restful-api` - Complete REST API example
- `clearskies://examples/relationships` - Model relationships example
- `clearskies://examples/authentication` - Authentication example
- `clearskies://examples/authorization` - Authorization example
- `clearskies://examples/testing` - Testing example

### Module Resources

- `clearskies://modules/overview` - Overview of extension modules
- `clearskies://modules/aws` - AWS module documentation
- `clearskies://modules/gitlab` - GitLab module documentation
- `clearskies://modules/graphql` - GraphQL module documentation

### Style Resources

- `clearskies://style/docstrings` - Docstring style guide

## Example Workflows

### Creating a New Model

1. Use `list_available_columns` to see available column types
2. Use `get_column_info` to understand specific columns you need
3. Use `generate_model` to create your model definition
4. Use the generated code in your project

### Building a REST API

1. Use `scaffold_restful_api` to generate a complete API
2. The tool will create a model, endpoint, and context
3. Run the generated code to start your API

### Exploring Extension Modules

1. Use `list_modules` to see what's available
2. Use `get_module_info` to see components in a module
3. Use `explain_module` to get usage examples
4. Use `check_module_compatibility` to verify installation

## Tips and Best Practices

- Start with `explain_concept` to understand framework concepts
- Use resources for documentation before generating code
- Leverage `scaffold_restful_api` for quick prototypes
- Check module compatibility before using extension features
- Refresh module cache after installing new packages

## Troubleshooting

### Module Not Found Errors

If you get errors about missing modules, use `check_module_compatibility` to verify the module is installed.

### Cache Issues

If modules or components aren't showing up, use `refresh_module_cache` to force a refresh.

### Generation Errors

When generating code, make sure you understand the required parameters by checking `get_column_info` or `get_endpoint_info` first.
