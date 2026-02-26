---
title: API Reference
layout: default
nav_order: 10
---

# API Reference

The clearskies MCP server exposes its functionality through MCP tools and resources. For implementation details, see the [source code on GitHub](https://github.com/clearskies-py/mcp-server/tree/main/src/clearskies_mcp_server).

## Key Modules

### Server
[`server.py`](https://github.com/clearskies-py/mcp-server/blob/main/src/clearskies_mcp_server/server.py) - Main MCP server entry point with tool and resource registration.

### Introspection
[`introspection.py`](https://github.com/clearskies-py/mcp-server/blob/main/src/clearskies_mcp_server/introspection.py) - Framework introspection utilities for discovering and documenting clearskies types.

### Module Discovery
[`module_discovery.py`](https://github.com/clearskies-py/mcp-server/blob/main/src/clearskies_mcp_server/module_discovery.py) - Dynamic discovery and introspection of clearskies extension modules.

### Tools
- [`documentation.py`](https://github.com/clearskies-py/mcp-server/blob/main/src/clearskies_mcp_server/tools/documentation.py) - MCP tools for framework documentation
- [`generation.py`](https://github.com/clearskies-py/mcp-server/blob/main/src/clearskies_mcp_server/tools/generation.py) - Code generation tools
- [`scaffolding.py`](https://github.com/clearskies-py/mcp-server/blob/main/src/clearskies_mcp_server/tools/scaffolding.py) - Project scaffolding tools
- [`modules.py`](https://github.com/clearskies-py/mcp-server/blob/main/src/clearskies_mcp_server/ tools/modules.py) - Module management tools

### Resources
- [`docs.py`](https://github.com/clearskies-py/mcp-server/blob/main/src/clearskies_mcp_server/resources/docs.py) - Documentation resources
- [`examples.py`](https://github.com/clearskies-py/mcp-server/blob/main/src/clearskies_mcp_server/resources/examples.py) - Example code resources
- [`modules.py`](https://github.com/clearskies-py/mcp-server/blob/main/src/clearskies_mcp_server/resources/modules.py) - Module documentation resources

### Concepts
The [`concepts/`](https://github.com/clearskies-py/mcp-server/tree/main/src/clearskies_mcp_server/concepts) directory contains detailed explanations of clearskies framework concepts.

### Examples
The [`examples/`](https://github.com/clearskies-py/mcp-server/tree/main/src/clearskies_mcp_server/examples) directory contains code examples demonstrating framework features.

## Source Code Documentation

All modules include comprehensive docstrings with:
- Module-level documentation
- Function and class docstrings
- Parameter and return type documentation
- Type hints throughout

Browse the source code on GitHub for detailed API documentation.
