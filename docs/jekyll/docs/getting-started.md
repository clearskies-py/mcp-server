---
title: Getting Started
layout: default
nav_order: 1
---

# Getting Started with clearskies MCP Server

The clearskies MCP Server provides code generation, documentation, and scaffolding tools for the clearskies Python framework through the Model Context Protocol (MCP).

## Installation

Install the MCP server using pip or uv:

```bash
pip install clear-skies-mcp-server

# Or with uv
uv pip install clear-skies-mcp-server
```

## Quick Start

### Using with Claude Desktop

Add to your Claude Desktop configuration (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "clearskies": {
      "command": "clearskies-mcp"
    }
  }
}
```

### Using Programmatically

The server can also be used directly from Python:

```python
from clearskies_mcp_server import main

# Run the server
main()
```

## Features

### Documentation Access

Access comprehensive clearskies framework documentation through MCP resources:

- Framework overview and concepts
- Model, Endpoint, Backend, and Context documentation
- Column types and validators reference
- Example code and tutorials
- Extension module documentation

### Code Generation

Generate clearskies code using MCP tools:

- **Models** - Create model classes with columns and relationships
- **Endpoints** - Generate REST API endpoints
- **Contexts** - Configure application contexts
- **Complete Projects** - Scaffold full applications

### Module Discovery

Discover and explore clearskies extension modules:

- List available modules
- Check installation status
- View components and capabilities
- Get usage examples

## Next Steps

- [Usage Guide](usage) - Detailed usage documentation
- [Tools Reference](tools) - Available MCP tools
- [Resources Reference](resources) - Available MCP resources
- [Source Code](https://github.com/clearskies-py/mcp-server) - View on GitHub
