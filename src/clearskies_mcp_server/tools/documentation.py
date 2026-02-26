"""
Documentation tools for clearskies MCP server.

This module contains tools for listing and documenting clearskies types.
"""

from ..concepts import CONCEPT_EXPLANATIONS
from ..introspection import (
    AUTHENTICATION_TYPES,
    BACKEND_TYPES,
    CLIENT_TYPES,
    COLUMN_TYPES,
    CONFIG_TYPES,
    CONTEXT_TYPES,
    CURSOR_TYPES,
    DI_INJECT_TYPES,
    ENDPOINT_TYPES,
    EXCEPTION_TYPES,
    FUNCTIONAL_ITEMS,
    INPUT_OUTPUT_TYPES,
    QUERY_RESULT_TYPES,
    QUERY_TYPES,
    SECRET_TYPES,
    SECURITY_HEADER_TYPES,
    VALIDATOR_TYPES,
    get_class_info,
    get_docstring,
    get_init_params,
    list_types_formatted,
)

# ---------------------------------------------------------------------------
# Core type listing functions (existing)
# ---------------------------------------------------------------------------


def list_available_columns() -> str:
    """List all available clearskies column types with a short description of each."""
    return list_types_formatted(COLUMN_TYPES)


def list_available_endpoints() -> str:
    """List all available clearskies endpoint types with a short description of each."""
    return list_types_formatted(ENDPOINT_TYPES)


def list_available_backends() -> str:
    """List all available clearskies backend types with a short description of each."""
    return list_types_formatted(BACKEND_TYPES)


def list_available_contexts() -> str:
    """List all available clearskies context types with a short description of each."""
    return list_types_formatted(CONTEXT_TYPES)


# ---------------------------------------------------------------------------
# New type listing functions
# ---------------------------------------------------------------------------


def list_available_authentication() -> str:
    """List all available clearskies authentication types with a short description of each.

    Authentication types are used to secure endpoints. They can be attached to endpoints
    via the authentication parameter.

    Example:
        clearskies.endpoints.RestfulApi(
            model_class=User,
            authentication=clearskies.authentication.SecretBearer(
                environment_key="API_SECRET"
            )
        )
    """
    if not AUTHENTICATION_TYPES:
        return "(no authentication types available - module may not be installed)"
    return list_types_formatted(AUTHENTICATION_TYPES)


def list_available_validators() -> str:
    """List all available clearskies validator types with a short description of each.

    Validators are used to validate model data before saving. They can be attached
    to columns via the validators parameter.

    Example:
        name = columns.String(validators=[Required(), MinLength(3)])
    """
    if not VALIDATOR_TYPES:
        return "(no validator types available - module may not be installed)"
    return list_types_formatted(VALIDATOR_TYPES)


def list_available_exceptions() -> str:
    """List all available clearskies exception types with a short description of each.

    These are the exceptions that clearskies may raise during operation. Understanding
    these helps with proper error handling in your application.
    """
    if not EXCEPTION_TYPES:
        return "(no exception types available - module may not be installed)"
    return list_types_formatted(EXCEPTION_TYPES)


def list_available_di_inject() -> str:
    """List all available clearskies DI inject helpers with a short description of each.

    DI inject helpers are used to inject dependencies into your classes. They provide
    special injection behaviors beyond simple class instantiation.

    Example:
        class MyService:
            def __init__(self, utcnow: clearskies.di.inject.Utcnow):
                self.utcnow = utcnow
    """
    if not DI_INJECT_TYPES:
        return "(no DI inject types available - module may not be installed)"
    return list_types_formatted(DI_INJECT_TYPES)


def list_available_cursors() -> str:
    """List all available clearskies cursor types with a short description of each.

    Cursors are used internally by backends to execute database queries. Understanding
    these is useful for advanced backend customization.
    """
    if not CURSOR_TYPES:
        return "(no cursor types available - module may not be installed)"
    return list_types_formatted(CURSOR_TYPES)


def list_available_input_outputs() -> str:
    """List all available clearskies input/output handlers with a short description of each.

    Input/output handlers define how data is read from requests and written to responses.
    They handle serialization formats like JSON, form data, etc.
    """
    if not INPUT_OUTPUT_TYPES:
        return "(no input/output types available - module may not be installed)"
    return list_types_formatted(INPUT_OUTPUT_TYPES)


def list_available_configs() -> str:
    """List all available clearskies configuration types with a short description of each.

    Configuration types are used to configure various aspects of clearskies behavior.
    """
    if not CONFIG_TYPES:
        return "(no config types available - module may not be installed)"
    return list_types_formatted(CONFIG_TYPES)


def list_available_clients() -> str:
    """List all available clearskies client types with a short description of each.

    Client types are used for making HTTP/API requests to external services.
    """
    if not CLIENT_TYPES:
        return "(no client types available - module may not be installed)"
    return list_types_formatted(CLIENT_TYPES)


def list_available_secrets() -> str:
    """List all available clearskies secrets handlers with a short description of each.

    Secrets handlers provide secure access to sensitive configuration values like
    API keys, database passwords, etc.
    """
    if not SECRET_TYPES:
        return "(no secret types available - module may not be installed)"
    return list_types_formatted(SECRET_TYPES)


def list_available_security_headers() -> str:
    """List all available clearskies security header handlers with a short description of each.

    Security header handlers add security-related HTTP headers to responses,
    such as CORS headers, CSP, etc.
    """
    if not SECURITY_HEADER_TYPES:
        return "(no security header types available - module may not be installed)"
    return list_types_formatted(SECURITY_HEADER_TYPES)


def list_available_query() -> str:
    """List all available clearskies query builder types with a short description of each.

    Query builders are used to construct database queries programmatically.
    """
    if not QUERY_TYPES:
        return "(no query types available - module may not be installed)"
    return list_types_formatted(QUERY_TYPES)


def list_available_query_results() -> str:
    """List all available clearskies query result types with a short description of each.

    Query result types handle the results returned from database queries.
    """
    if not QUERY_RESULT_TYPES:
        return "(no query result types available - module may not be installed)"
    return list_types_formatted(QUERY_RESULT_TYPES)


def list_available_functional() -> str:
    """List all available clearskies functional utilities with a short description of each.

    Functional utilities provide helper functions and decorators for common patterns.
    """
    if not FUNCTIONAL_ITEMS:
        return "(no functional utilities available - module may not be installed)"
    lines = []
    for name, item in sorted(FUNCTIONAL_ITEMS.items()):
        doc = get_docstring(item) if hasattr(item, "__doc__") else ""
        first_line = doc.split("\n")[0] if doc else "(no description)"
        lines.append(f"- **{name}**: {first_line}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Core type info functions (existing)
# ---------------------------------------------------------------------------


def get_column_info(column_type: str) -> str:
    """Get detailed documentation and constructor parameters for a specific clearskies column type.

    Args:
        column_type: The name of the column type (e.g. "String", "Integer", "BelongsToId").
    """
    cls = COLUMN_TYPES.get(column_type)
    if cls is None:
        available = ", ".join(sorted(COLUMN_TYPES))
        return f"Unknown column type '{column_type}'. Available types: {available}"
    return get_class_info(cls, "Column")


def get_endpoint_info(endpoint_type: str) -> str:
    """Get detailed documentation and configuration options for a specific clearskies endpoint type.

    Args:
        endpoint_type: The name of the endpoint type (e.g. "RestfulApi", "Create", "List").
    """
    cls = ENDPOINT_TYPES.get(endpoint_type)
    if cls is None:
        available = ", ".join(sorted(ENDPOINT_TYPES))
        return f"Unknown endpoint type '{endpoint_type}'. Available types: {available}"
    return get_class_info(cls, "Endpoint")


def get_backend_info(backend_type: str) -> str:
    """Get detailed documentation for a specific clearskies backend type.

    Args:
        backend_type: The name of the backend type (e.g. "MemoryBackend", "CursorBackend", "ApiBackend").
    """
    cls = BACKEND_TYPES.get(backend_type)
    if cls is None:
        available = ", ".join(sorted(BACKEND_TYPES))
        return f"Unknown backend type '{backend_type}'. Available types: {available}"
    return get_class_info(cls, "Backend")


def get_context_info(context_type: str) -> str:
    """Get detailed documentation for a specific clearskies context type.

    Args:
        context_type: The name of the context type (e.g. "Cli", "WsgiRef", "Wsgi").
    """
    cls = CONTEXT_TYPES.get(context_type)
    if cls is None:
        available = ", ".join(sorted(CONTEXT_TYPES))
        return f"Unknown context type '{context_type}'. Available types: {available}"
    return get_class_info(cls, "Context")


# ---------------------------------------------------------------------------
# New type info functions
# ---------------------------------------------------------------------------


def get_authentication_info(auth_type: str) -> str:
    """Get detailed documentation for a specific clearskies authentication type.

    Args:
        auth_type: The auth type name (e.g. "SecretBearer", "JWKS", "SecretBasic").
    """
    if not AUTHENTICATION_TYPES:
        return "Authentication module not available in this clearskies installation."
    cls = AUTHENTICATION_TYPES.get(auth_type)
    if cls is None:
        available = ", ".join(sorted(AUTHENTICATION_TYPES))
        return f"Unknown authentication type '{auth_type}'. Available types: {available}"
    return get_class_info(cls, "Authentication")


def get_validator_info(validator_type: str) -> str:
    """Get detailed documentation for a specific clearskies validator type.

    Args:
        validator_type: The validator type name (e.g. "Required", "Unique", "Email").
    """
    if not VALIDATOR_TYPES:
        return "Validators module not available in this clearskies installation."
    cls = VALIDATOR_TYPES.get(validator_type)
    if cls is None:
        available = ", ".join(sorted(VALIDATOR_TYPES))
        return f"Unknown validator type '{validator_type}'. Available types: {available}"
    return get_class_info(cls, "Validator")


def get_exception_info(exception_type: str) -> str:
    """Get detailed documentation for a specific clearskies exception type.

    Args:
        exception_type: The exception type name (e.g. "InputError", "AuthenticationError").
    """
    if not EXCEPTION_TYPES:
        return "Exceptions module not available in this clearskies installation."
    cls = EXCEPTION_TYPES.get(exception_type)
    if cls is None:
        available = ", ".join(sorted(EXCEPTION_TYPES))
        return f"Unknown exception type '{exception_type}'. Available types: {available}"
    return get_class_info(cls, "Exception")


def get_di_inject_info(inject_type: str) -> str:
    """Get detailed documentation for a specific clearskies DI inject helper.

    Args:
        inject_type: The inject type name (e.g. "ByClass", "Utcnow").
    """
    if not DI_INJECT_TYPES:
        return "DI inject module not available in this clearskies installation."
    cls = DI_INJECT_TYPES.get(inject_type)
    if cls is None:
        available = ", ".join(sorted(DI_INJECT_TYPES))
        return f"Unknown DI inject type '{inject_type}'. Available types: {available}"
    return get_class_info(cls, "DI Inject")


def get_cursor_info(cursor_type: str) -> str:
    """Get detailed documentation for a specific clearskies cursor type.

    Args:
        cursor_type: The cursor type name.
    """
    if not CURSOR_TYPES:
        return "Cursors module not available in this clearskies installation."
    cls = CURSOR_TYPES.get(cursor_type)
    if cls is None:
        available = ", ".join(sorted(CURSOR_TYPES))
        return f"Unknown cursor type '{cursor_type}'. Available types: {available}"
    return get_class_info(cls, "Cursor")


def get_input_output_info(io_type: str) -> str:
    """Get detailed documentation for a specific clearskies input/output handler.

    Args:
        io_type: The input/output type name.
    """
    if not INPUT_OUTPUT_TYPES:
        return "Input/outputs module not available in this clearskies installation."
    cls = INPUT_OUTPUT_TYPES.get(io_type)
    if cls is None:
        available = ", ".join(sorted(INPUT_OUTPUT_TYPES))
        return f"Unknown input/output type '{io_type}'. Available types: {available}"
    return get_class_info(cls, "Input/Output")


def get_config_info(config_type: str) -> str:
    """Get detailed documentation for a specific clearskies configuration type.

    Args:
        config_type: The config type name.
    """
    if not CONFIG_TYPES:
        return "Configs module not available in this clearskies installation."
    cls = CONFIG_TYPES.get(config_type)
    if cls is None:
        available = ", ".join(sorted(CONFIG_TYPES))
        return f"Unknown config type '{config_type}'. Available types: {available}"
    return get_class_info(cls, "Config")


def get_client_info(client_type: str) -> str:
    """Get detailed documentation for a specific clearskies client type.

    Args:
        client_type: The client type name.
    """
    if not CLIENT_TYPES:
        return "Clients module not available in this clearskies installation."
    cls = CLIENT_TYPES.get(client_type)
    if cls is None:
        available = ", ".join(sorted(CLIENT_TYPES))
        return f"Unknown client type '{client_type}'. Available types: {available}"
    return get_class_info(cls, "Client")


def get_secret_info(secret_type: str) -> str:
    """Get detailed documentation for a specific clearskies secrets handler.

    Args:
        secret_type: The secret type name.
    """
    if not SECRET_TYPES:
        return "Secrets module not available in this clearskies installation."
    cls = SECRET_TYPES.get(secret_type)
    if cls is None:
        available = ", ".join(sorted(SECRET_TYPES))
        return f"Unknown secret type '{secret_type}'. Available types: {available}"
    return get_class_info(cls, "Secret")


def get_security_header_info(header_type: str) -> str:
    """Get detailed documentation for a specific clearskies security header handler.

    Args:
        header_type: The security header type name.
    """
    if not SECURITY_HEADER_TYPES:
        return "Security headers module not available in this clearskies installation."
    cls = SECURITY_HEADER_TYPES.get(header_type)
    if cls is None:
        available = ", ".join(sorted(SECURITY_HEADER_TYPES))
        return f"Unknown security header type '{header_type}'. Available types: {available}"
    return get_class_info(cls, "Security Header")


def get_query_info(query_type: str) -> str:
    """Get detailed documentation for a specific clearskies query builder type.

    Args:
        query_type: The query type name.
    """
    if not QUERY_TYPES:
        return "Query module not available in this clearskies installation."
    cls = QUERY_TYPES.get(query_type)
    if cls is None:
        available = ", ".join(sorted(QUERY_TYPES))
        return f"Unknown query type '{query_type}'. Available types: {available}"
    return get_class_info(cls, "Query")


def get_query_result_info(result_type: str) -> str:
    """Get detailed documentation for a specific clearskies query result type.

    Args:
        result_type: The query result type name.
    """
    if not QUERY_RESULT_TYPES:
        return "Query results module not available in this clearskies installation."
    cls = QUERY_RESULT_TYPES.get(result_type)
    if cls is None:
        available = ", ".join(sorted(QUERY_RESULT_TYPES))
        return f"Unknown query result type '{result_type}'. Available types: {available}"
    return get_class_info(cls, "Query Result")


def get_functional_info(func_name: str) -> str:
    """Get detailed documentation for a specific clearskies functional utility.

    Args:
        func_name: The functional utility name.
    """
    if not FUNCTIONAL_ITEMS:
        return "Functional module not available in this clearskies installation."
    item = FUNCTIONAL_ITEMS.get(func_name)
    if item is None:
        available = ", ".join(sorted(FUNCTIONAL_ITEMS))
        return f"Unknown functional utility '{func_name}'. Available utilities: {available}"

    doc = get_docstring(item) if hasattr(item, "__doc__") else ""
    parts = [f"# Functional: {func_name}\n"]
    if doc:
        parts.append(doc)

    # Try to get signature if it's callable
    if callable(item):
        try:
            import inspect

            sig = inspect.signature(item)
            parts.append(f"\n## Signature\n")
            parts.append(f"`{func_name}{sig}`")
        except (ValueError, TypeError):
            pass

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Concept explanation (existing)
# ---------------------------------------------------------------------------


def explain_concept(concept: str) -> str:
    """Explain a clearskies framework concept in detail.

    Args:
        concept: The concept to explain. One of: model, endpoint, backend, column, context, di,
                 authentication, autodoc, query, validator, schema, save_lifecycle, state_machine,
                 declarative_programming, infrastructure_neutral, testing, authorization, error_handling,
                 input_handling, endpoint_groups, routing, responses, migrations, advanced_columns,
                 advanced_queries, configuration, logging, caching, async, state_machine_advanced,
                 secrets_backend.
    """
    concept_lower = concept.lower().replace(" ", "_").replace("-", "_")
    if concept_lower in CONCEPT_EXPLANATIONS:
        return CONCEPT_EXPLANATIONS[concept_lower]
    available = ", ".join(sorted(CONCEPT_EXPLANATIONS.keys()))
    return f"Unknown concept '{concept}'. Available concepts: {available}"
