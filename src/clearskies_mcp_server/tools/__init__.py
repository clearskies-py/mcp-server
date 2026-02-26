"""
Tools package for clearskies MCP server.

This package contains the implementation of all MCP tools organized by category.
"""

from .documentation import (
    # Concept explanation
    explain_concept,
    # Extended type info
    get_authentication_info,
    get_backend_info,
    get_client_info,
    # Core type info
    get_column_info,
    get_config_info,
    get_context_info,
    get_cursor_info,
    get_di_inject_info,
    get_endpoint_info,
    get_exception_info,
    get_functional_info,
    get_input_output_info,
    get_query_info,
    get_query_result_info,
    get_secret_info,
    get_security_header_info,
    get_validator_info,
    # Extended type listing
    list_available_authentication,
    list_available_backends,
    list_available_clients,
    # Core type listing
    list_available_columns,
    list_available_configs,
    list_available_contexts,
    list_available_cursors,
    list_available_di_inject,
    list_available_endpoints,
    list_available_exceptions,
    list_available_functional,
    list_available_input_outputs,
    list_available_query,
    list_available_query_results,
    list_available_secrets,
    list_available_security_headers,
    list_available_validators,
)
from .generation import (
    generate_context,
    generate_endpoint,
    generate_endpoint_group,
    generate_model,
)
from .modules import (
    check_module_compatibility,
    explain_module,
    get_module_components,
    get_module_info,
    list_modules,
    refresh_module_cache,
    suggest_modules,
)
from .scaffolding import (
    generate_model_with_relationships,
    scaffold_project,
    scaffold_restful_api,
)

__all__ = [
    # Core type listing
    "list_available_columns",
    "list_available_endpoints",
    "list_available_backends",
    "list_available_contexts",
    # Extended type listing
    "list_available_authentication",
    "list_available_validators",
    "list_available_exceptions",
    "list_available_di_inject",
    "list_available_cursors",
    "list_available_input_outputs",
    "list_available_configs",
    "list_available_clients",
    "list_available_secrets",
    "list_available_security_headers",
    "list_available_query",
    "list_available_query_results",
    "list_available_functional",
    # Core type info
    "get_column_info",
    "get_endpoint_info",
    "get_backend_info",
    "get_context_info",
    # Extended type info
    "get_authentication_info",
    "get_validator_info",
    "get_exception_info",
    "get_di_inject_info",
    "get_cursor_info",
    "get_input_output_info",
    "get_config_info",
    "get_client_info",
    "get_secret_info",
    "get_security_header_info",
    "get_query_info",
    "get_query_result_info",
    "get_functional_info",
    # Concept explanation
    "explain_concept",
    # Generation tools
    "generate_model",
    "generate_endpoint",
    "generate_context",
    "generate_endpoint_group",
    # Scaffolding tools
    "scaffold_project",
    "scaffold_restful_api",
    "generate_model_with_relationships",
    # Module tools
    "list_modules",
    "get_module_info",
    "explain_module",
    "get_module_components",
    "suggest_modules",
    "check_module_compatibility",
    "refresh_module_cache",
]
