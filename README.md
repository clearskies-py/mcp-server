# clearskies MCP Server

An MCP (Model Context Protocol) server for the [clearskies](https://clearskies.io/) Python framework. This server provides AI assistants with tools for code generation, documentation, and project scaffolding when building applications with clearskies.

## Installation

```bash
pip install clear-skies-mcp-server
```

Or with uv:

```bash
uv pip install clear-skies-mcp-server
```

## Features

### Documentation Tools

#### Core Type Discovery

| Tool                       | Description                                    |
| -------------------------- | ---------------------------------------------- |
| `list_available_columns`   | List all available clearskies column types     |
| `list_available_endpoints` | List all available endpoint types              |
| `list_available_backends`  | List all available backend types               |
| `list_available_contexts`  | List all available context types               |
| `get_column_info`          | Get detailed docs for a specific column type   |
| `get_endpoint_info`        | Get detailed docs for a specific endpoint type |
| `get_backend_info`         | Get detailed docs for a specific backend type  |
| `get_context_info`         | Get detailed docs for a specific context type  |

#### Extended Type Discovery

| Tool                              | Description                                              |
| --------------------------------- | -------------------------------------------------------- |
| `list_available_authentication`   | List all authentication types (SecretBearer, JWKS, etc.) |
| `list_available_validators`       | List all validator types (Required, Unique, etc.)        |
| `list_available_exceptions`       | List all exception types                                 |
| `list_available_di_inject`        | List all DI inject helpers                               |
| `list_available_cursors`          | List all cursor types                                    |
| `list_available_input_outputs`    | List all input/output handlers                           |
| `list_available_configs`          | List all configuration types                             |
| `list_available_clients`          | List all client types                                    |
| `list_available_secrets`          | List all secrets handlers                                |
| `list_available_security_headers` | List all security header handlers                        |
| `list_available_query`            | List all query builder types                             |
| `list_available_query_results`    | List all query result types                              |
| `list_available_functional`       | List all functional utilities                            |

#### Extended Type Info

| Tool                       | Description                                              |
| -------------------------- | -------------------------------------------------------- |
| `get_authentication_info`  | Get detailed docs for a specific authentication type     |
| `get_validator_info`       | Get detailed docs for a specific validator type          |
| `get_exception_info`       | Get detailed docs for a specific exception type          |
| `get_di_inject_info`       | Get detailed docs for a specific DI inject helper        |
| `get_cursor_info`          | Get detailed docs for a specific cursor type             |
| `get_input_output_info`    | Get detailed docs for a specific input/output handler    |
| `get_config_info`          | Get detailed docs for a specific configuration type      |
| `get_client_info`          | Get detailed docs for a specific client type             |
| `get_secret_info`          | Get detailed docs for a specific secrets handler         |
| `get_security_header_info` | Get detailed docs for a specific security header handler |
| `get_query_info`           | Get detailed docs for a specific query builder type      |
| `get_query_result_info`    | Get detailed docs for a specific query result type       |
| `get_functional_info`      | Get detailed docs for a specific functional utility      |

#### Concept Explanation

| Tool              | Description                              |
| ----------------- | ---------------------------------------- |
| `explain_concept` | Explain any clearskies concept in detail |

### Code Generation Tools

| Tool                      | Description                                  |
| ------------------------- | -------------------------------------------- |
| `generate_model`          | Generate a clearskies Model class definition |
| `generate_endpoint`       | Generate an endpoint configuration           |
| `generate_context`        | Generate a context wrapping an endpoint      |
| `generate_endpoint_group` | Generate an endpoint group configuration     |

### Scaffolding Tools

| Tool                                | Description                                                 |
| ----------------------------------- | ----------------------------------------------------------- |
| `scaffold_project`                  | Generate a complete clearskies project with multiple models |
| `scaffold_restful_api`              | Generate a complete REST API application for a single model |
| `generate_model_with_relationships` | Generate multiple related models with relationships         |

### Documentation Resources

#### Core Documentation

| Resource URI                       | Description                |
| ---------------------------------- | -------------------------- |
| `clearskies://docs/overview`       | Framework overview         |
| `clearskies://docs/models`         | Model documentation        |
| `clearskies://docs/endpoints`      | Endpoint documentation     |
| `clearskies://docs/columns`        | Column types documentation |
| `clearskies://docs/backends`       | Backend documentation      |
| `clearskies://docs/contexts`       | Context documentation      |
| `clearskies://docs/di`             | Dependency injection docs  |
| `clearskies://docs/authentication` | Authentication docs        |
| `clearskies://docs/save-lifecycle` | Save lifecycle docs        |
| `clearskies://docs/queries`        | Query documentation        |
| `clearskies://docs/validators`     | Validator documentation    |

#### Extended Documentation

| Resource URI                               | Description                      |
| ------------------------------------------ | -------------------------------- |
| `clearskies://docs/testing`                | Testing clearskies applications  |
| `clearskies://docs/authorization`          | Authorization patterns           |
| `clearskies://docs/error-handling`         | Error handling                   |
| `clearskies://docs/input-handling`         | Input handling                   |
| `clearskies://docs/endpoint-groups`        | Endpoint groups                  |
| `clearskies://docs/routing`                | Routing documentation            |
| `clearskies://docs/responses`              | Response customization           |
| `clearskies://docs/migrations`             | Database migrations (Mygrations) |
| `clearskies://docs/advanced-columns`       | Advanced column types            |
| `clearskies://docs/advanced-queries`       | Advanced query patterns          |
| `clearskies://docs/configuration`          | Configuration management         |
| `clearskies://docs/logging`                | Logging and observability        |
| `clearskies://docs/caching`                | Caching patterns                 |
| `clearskies://docs/async`                  | Async patterns                   |
| `clearskies://docs/state-machine-advanced` | Advanced state machine patterns  |
| `clearskies://docs/secrets-backend`        | Secrets backend                  |

#### Backend Deep Dives

| Resource URI                       | Description             |
| ---------------------------------- | ----------------------- |
| `clearskies://docs/backend-memory` | MemoryBackend deep dive |
| `clearskies://docs/backend-cursor` | CursorBackend deep dive |
| `clearskies://docs/cursors`        | Cursors and raw SQL     |
| `clearskies://docs/transactions`   | Transaction management  |

#### Framework Internals

| Resource URI                        | Description           |
| ----------------------------------- | --------------------- |
| `clearskies://docs/di-advanced`     | Advanced DI patterns  |
| `clearskies://docs/query-execution` | Query execution model |
| `clearskies://docs/model-lifecycle` | Model lifecycle       |
| `clearskies://docs/input-output`    | Input/output system   |

#### Developer Experience

| Resource URI                        | Description                   |
| ----------------------------------- | ----------------------------- |
| `clearskies://docs/troubleshooting` | Troubleshooting guide         |
| `clearskies://docs/best-practices`  | Best practices                |
| `clearskies://docs/exceptions`      | Exception hierarchy reference |
| `clearskies://docs/auth-flow`       | Auth flow documentation       |

#### Reference Material

| Resource URI                           | Description                           |
| -------------------------------------- | ------------------------------------- |
| `clearskies://docs/column-reference`   | Complete column parameter reference   |
| `clearskies://docs/endpoint-reference` | Complete endpoint parameter reference |
| `clearskies://docs/performance`        | Performance guide                     |
| `clearskies://docs/patterns`           | Common patterns cookbook              |

### Example Resources

| Resource URI                                   | Description                              |
| ---------------------------------------------- | ---------------------------------------- |
| `clearskies://examples/restful-api`            | Complete REST API example                |
| `clearskies://examples/relationships`          | Model relationships example              |
| `clearskies://examples/authentication`         | Authenticated API example                |
| `clearskies://examples/cli-app`                | CLI application example                  |
| `clearskies://examples/api-backend`            | API client (ApiBackend) example          |
| `clearskies://examples/testing`                | Testing example                          |
| `clearskies://examples/authorization`          | Authorization patterns example           |
| `clearskies://examples/error-handling`         | Error handling example                   |
| `clearskies://examples/endpoint-group`         | Endpoint groups example                  |
| `clearskies://examples/migrations`             | Database migrations example              |
| `clearskies://examples/hierarchical-data`      | Hierarchical data (CategoryTree) example |
| `clearskies://examples/audit-trail`            | Audit trail tracking example             |
| `clearskies://examples/pivot-data`             | Many-to-many with pivot data example     |
| `clearskies://examples/advanced-queries`       | Advanced query patterns example          |
| `clearskies://examples/configuration`          | Configuration management example         |
| `clearskies://examples/state-machine-advanced` | Advanced state machine example           |
| `clearskies://examples/secrets-backend`        | Secrets backend example                  |

### Module Resources

| Resource URI                    | Description                                |
| ------------------------------- | ------------------------------------------ |
| `clearskies://modules/overview` | Overview of all extension modules          |
| `clearskies://modules/aws`      | clearskies-aws module                      |
| `clearskies://modules/graphql`  | clearskies-graphql module                  |
| `clearskies://modules/gitlab`   | clearskies-gitlab module                   |
| `clearskies://modules/cortex`   | clearskies-cortex module                   |
| `clearskies://modules/snyk`     | clearskies-snyk module                     |
| `clearskies://modules/akeyless` | clearskies-akeyless-custom-producer module |

### Style Resources

| Resource URI                    | Description           |
| ------------------------------- | --------------------- |
| `clearskies://style/docstrings` | Docstring style guide |

## MCP Configuration

Add this to your MCP settings (e.g. in Kilo Code, Claude Desktop, etc.):

```json
{
    "mcpServers": {
        "clearskies": {
            "command": "clear-skies-mcp-server",
            "args": []
        }
    }
}
```

Or if using uv/uvx:

```json
{
    "mcpServers": {
        "clearskies": {
            "command": "uvx",
            "args": ["clear-skies-mcp-server"]
        }
    }
}
```

## Development

```bash
# Clone the repo
git clone https://github.com/clearskies-py/mcp-server.git
cd mcp-server

# Create venv and install dependencies
uv sync all-extras --all-groups

# Run the server
clear-skies-mcp-server
```

## License

MIT
