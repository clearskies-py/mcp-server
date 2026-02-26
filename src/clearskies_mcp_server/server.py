"""
clearskies MCP Server - Main entry point.

This module provides the FastMCP server that exposes clearskies framework
documentation, code generation tools, and examples as MCP resources and tools.
"""

from mcp.server.fastmcp import FastMCP

# Import resources from the resources package
from .resources import (
    breaking_changes,
    docs_advanced_columns,
    docs_advanced_queries,
    docs_async,
    docs_auth_flow,
    docs_authentication,
    docs_authorization,
    docs_backend_cursor,
    # Phase 6.1: Backend Foundations
    docs_backend_memory,
    docs_backends,
    docs_best_practices,
    docs_caching,
    # Phase 6.4: Reference Material
    docs_column_reference,
    docs_columns,
    docs_component_inheritance,
    docs_configs_module,
    docs_configurable,
    docs_configuration,
    docs_contexts,
    docs_cursors,
    docs_di,
    # Phase 6.2: Framework Internals
    docs_di_advanced,
    docs_endpoint_groups,
    docs_endpoint_reference,
    docs_endpoints,
    docs_error_handling,
    docs_exceptions,
    docs_injectable,
    docs_injectable_properties,
    docs_input_handling,
    docs_input_output,
    docs_loggable,
    docs_logging,
    docs_migrations,
    docs_model_lifecycle,
    docs_models,
    # Documentation resources
    docs_overview,
    docs_patterns,
    docs_performance,
    docs_queries,
    docs_query_execution,
    docs_responses,
    docs_routing,
    docs_save_lifecycle,
    docs_secrets_backend,
    docs_state_machine_advanced,
    docs_testing,
    docs_transactions,
    # Phase 6.3: Developer Experience
    docs_troubleshooting,
    docs_validators,
    example_advanced_queries,
    example_api_backend,
    example_audit_trail,
    example_authentication,
    example_authorization,
    example_cli_app,
    example_configuration,
    example_endpoint_group,
    example_error_handling,
    example_hierarchical_data,
    example_migrations,
    example_pivot_data,
    example_relationships,
    # Example resources
    example_restful_api,
    example_secrets_backend,
    example_state_machine_advanced,
    example_testing,
    migration_guide,
    migration_patterns,
    module_akeyless,
    module_aws,
    module_cortex,
    module_gitlab,
    module_graphql,
    module_snyk,
    # Module resources
    modules_overview,
    # Style resources
    style_docstrings,
)

# Import tools from the tools package
from .tools import (
    analyze_v1_project,
    check_module_compatibility,
    # Concept explanation
    explain_concept,
    explain_module,
    explain_v1_v2_difference,
    generate_context,
    generate_endpoint,
    generate_endpoint_group,
    # Generation tools
    generate_model,
    generate_model_with_relationships,
    generate_v2_migration,
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
    get_migration_checklist,
    get_module_components,
    get_module_info,
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
    # Module tools (with dynamic discovery)
    list_modules,
    map_v1_to_v2,
    refresh_module_cache,
    # Scaffolding tools
    scaffold_project,
    scaffold_restful_api,
    suggest_modules,
)

# Create the FastMCP server instance
mcp = FastMCP(
    "clearskies",
    instructions="MCP server for the clearskies Python framework – code generation, documentation, and scaffolding.",
)

# =============================================================================
# TOOL REGISTRATION
# =============================================================================

# Core type listing tools
mcp.tool()(list_available_columns)
mcp.tool()(list_available_endpoints)
mcp.tool()(list_available_backends)
mcp.tool()(list_available_contexts)

# Extended type listing tools
mcp.tool()(list_available_authentication)
mcp.tool()(list_available_validators)
mcp.tool()(list_available_exceptions)
mcp.tool()(list_available_di_inject)
mcp.tool()(list_available_cursors)
mcp.tool()(list_available_input_outputs)
mcp.tool()(list_available_configs)
mcp.tool()(list_available_clients)
mcp.tool()(list_available_secrets)
mcp.tool()(list_available_security_headers)
mcp.tool()(list_available_query)
mcp.tool()(list_available_query_results)
mcp.tool()(list_available_functional)

# Core type info tools
mcp.tool()(get_column_info)
mcp.tool()(get_endpoint_info)
mcp.tool()(get_backend_info)
mcp.tool()(get_context_info)

# Extended type info tools
mcp.tool()(get_authentication_info)
mcp.tool()(get_validator_info)
mcp.tool()(get_exception_info)
mcp.tool()(get_di_inject_info)
mcp.tool()(get_cursor_info)
mcp.tool()(get_input_output_info)
mcp.tool()(get_config_info)
mcp.tool()(get_client_info)
mcp.tool()(get_secret_info)
mcp.tool()(get_security_header_info)
mcp.tool()(get_query_info)
mcp.tool()(get_query_result_info)
mcp.tool()(get_functional_info)

# Concept explanation tool
mcp.tool()(explain_concept)

# Generation tools
mcp.tool()(generate_model)
mcp.tool()(generate_endpoint)
mcp.tool()(generate_context)
mcp.tool()(generate_endpoint_group)

# Scaffolding tools
mcp.tool()(scaffold_project)
mcp.tool()(scaffold_restful_api)
mcp.tool()(generate_model_with_relationships)

# Module tools (with dynamic discovery)
mcp.tool()(list_modules)
mcp.tool()(get_module_info)
mcp.tool()(explain_module)
mcp.tool()(get_module_components)
mcp.tool()(suggest_modules)
mcp.tool()(check_module_compatibility)
mcp.tool()(refresh_module_cache)

# Migration tools (v1 → v2)
mcp.tool()(analyze_v1_project)
mcp.tool()(generate_v2_migration)
mcp.tool()(map_v1_to_v2)
mcp.tool()(explain_v1_v2_difference)
mcp.tool()(get_migration_checklist)

# =============================================================================
# RESOURCE REGISTRATION
# =============================================================================

# Documentation resources
mcp.resource("clearskies://docs/overview", name="docs_overview", description="Overview of the clearskies framework.")(
    docs_overview
)
mcp.resource(
    "clearskies://docs/models", name="docs_models", description="Detailed documentation about clearskies Models."
)(docs_models)
mcp.resource(
    "clearskies://docs/endpoints", name="docs_endpoints", description="Documentation about clearskies Endpoints."
)(docs_endpoints)
mcp.resource(
    "clearskies://docs/columns", name="docs_columns", description="Documentation about clearskies Column types."
)(docs_columns)
mcp.resource(
    "clearskies://docs/backends", name="docs_backends", description="Documentation about clearskies Backends."
)(docs_backends)
mcp.resource(
    "clearskies://docs/contexts", name="docs_contexts", description="Documentation about clearskies Contexts."
)(docs_contexts)
mcp.resource(
    "clearskies://docs/di", name="docs_di", description="Documentation about clearskies Dependency Injection."
)(docs_di)
mcp.resource(
    "clearskies://docs/authentication",
    name="docs_authentication",
    description="Documentation about clearskies Authentication.",
)(docs_authentication)
mcp.resource(
    "clearskies://docs/save-lifecycle",
    name="docs_save_lifecycle",
    description="Documentation about the clearskies save lifecycle.",
)(docs_save_lifecycle)
mcp.resource("clearskies://docs/queries", name="docs_queries", description="Documentation about clearskies queries.")(
    docs_queries
)
mcp.resource(
    "clearskies://docs/validators", name="docs_validators", description="Documentation about clearskies validators."
)(docs_validators)
mcp.resource(
    "clearskies://docs/testing", name="docs_testing", description="Documentation about testing clearskies applications."
)(docs_testing)
mcp.resource(
    "clearskies://docs/authorization",
    name="docs_authorization",
    description="Documentation about clearskies authorization patterns.",
)(docs_authorization)
mcp.resource(
    "clearskies://docs/error-handling",
    name="docs_error_handling",
    description="Documentation about clearskies error handling.",
)(docs_error_handling)
mcp.resource(
    "clearskies://docs/input-handling",
    name="docs_input_handling",
    description="Documentation about clearskies input handling.",
)(docs_input_handling)
mcp.resource(
    "clearskies://docs/endpoint-groups",
    name="docs_endpoint_groups",
    description="Documentation about clearskies endpoint groups.",
)(docs_endpoint_groups)
mcp.resource("clearskies://docs/routing", name="docs_routing", description="Documentation about clearskies routing.")(
    docs_routing
)
mcp.resource(
    "clearskies://docs/responses",
    name="docs_responses",
    description="Documentation about clearskies response customization.",
)(docs_responses)
mcp.resource(
    "clearskies://docs/migrations",
    name="docs_migrations",
    description="Documentation about clearskies database migrations (Mygrations).",
)(docs_migrations)
mcp.resource(
    "clearskies://docs/advanced-columns",
    name="docs_advanced_columns",
    description="Documentation about advanced clearskies column types.",
)(docs_advanced_columns)
mcp.resource(
    "clearskies://docs/advanced-queries",
    name="docs_advanced_queries",
    description="Documentation about advanced clearskies query patterns.",
)(docs_advanced_queries)
mcp.resource(
    "clearskies://docs/configuration",
    name="docs_configuration",
    description="Documentation about clearskies configuration management.",
)(docs_configuration)
mcp.resource(
    "clearskies://docs/logging",
    name="docs_logging",
    description="Documentation about logging and observability in clearskies.",
)(docs_logging)
mcp.resource(
    "clearskies://docs/caching", name="docs_caching", description="Documentation about caching patterns in clearskies."
)(docs_caching)
mcp.resource(
    "clearskies://docs/async", name="docs_async", description="Documentation about async patterns in clearskies."
)(docs_async)
mcp.resource(
    "clearskies://docs/state-machine-advanced",
    name="docs_state_machine_advanced",
    description="Documentation about advanced state machine patterns in clearskies.",
)(docs_state_machine_advanced)
mcp.resource(
    "clearskies://docs/secrets-backend",
    name="docs_secrets_backend",
    description="Documentation about the secrets backend in clearskies.",
)(docs_secrets_backend)

# Phase 6.1: Backend Foundations
mcp.resource(
    "clearskies://docs/backend-memory",
    name="docs_backend_memory",
    description="Deep dive documentation about MemoryBackend.",
)(docs_backend_memory)
mcp.resource(
    "clearskies://docs/backend-cursor",
    name="docs_backend_cursor",
    description="Deep dive documentation about CursorBackend.",
)(docs_backend_cursor)
mcp.resource(
    "clearskies://docs/cursors",
    name="docs_cursors",
    description="Documentation about cursors and raw SQL in clearskies.",
)(docs_cursors)
mcp.resource(
    "clearskies://docs/transactions",
    name="docs_transactions",
    description="Documentation about transaction management in clearskies.",
)(docs_transactions)

# Phase 6.2: Framework Internals
mcp.resource(
    "clearskies://docs/di-advanced",
    name="docs_di_advanced",
    description="Advanced DI patterns and troubleshooting in clearskies.",
)(docs_di_advanced)
mcp.resource(
    "clearskies://docs/query-execution",
    name="docs_query_execution",
    description="Documentation about query execution model in clearskies.",
)(docs_query_execution)
mcp.resource(
    "clearskies://docs/model-lifecycle",
    name="docs_model_lifecycle",
    description="Documentation about model lifecycle in clearskies.",
)(docs_model_lifecycle)
mcp.resource(
    "clearskies://docs/input-output",
    name="docs_input_output",
    description="Documentation about the input/output system in clearskies.",
)(docs_input_output)

# Phase 6.3: Developer Experience
mcp.resource(
    "clearskies://docs/troubleshooting",
    name="docs_troubleshooting",
    description="Troubleshooting guide for clearskies applications.",
)(docs_troubleshooting)
mcp.resource(
    "clearskies://docs/best-practices",
    name="docs_best_practices",
    description="Best practices for clearskies development.",
)(docs_best_practices)
mcp.resource(
    "clearskies://docs/exceptions", name="docs_exceptions", description="Exception hierarchy reference for clearskies."
)(docs_exceptions)
mcp.resource(
    "clearskies://docs/auth-flow",
    name="docs_auth_flow",
    description="Authentication and authorization flow documentation.",
)(docs_auth_flow)

# Phase 6.4: Reference Material
mcp.resource(
    "clearskies://docs/column-reference",
    name="docs_column_reference",
    description="Complete column parameter reference for clearskies.",
)(docs_column_reference)
mcp.resource(
    "clearskies://docs/endpoint-reference",
    name="docs_endpoint_reference",
    description="Complete endpoint parameter reference for clearskies.",
)(docs_endpoint_reference)
mcp.resource(
    "clearskies://docs/performance",
    name="docs_performance",
    description="Performance guide for clearskies applications.",
)(docs_performance)
mcp.resource(
    "clearskies://docs/patterns", name="docs_patterns", description="Common patterns cookbook for clearskies."
)(docs_patterns)

# Base class concepts
mcp.resource(
    "clearskies://docs/injectable-properties",
    name="docs_injectable_properties",
    description="Documentation about the InjectableProperties mixin.",
)(docs_injectable_properties)
mcp.resource(
    "clearskies://docs/configurable",
    name="docs_configurable",
    description="Documentation about the Configurable mixin.",
)(docs_configurable)
mcp.resource("clearskies://docs/loggable", name="docs_loggable", description="Documentation about the Loggable mixin.")(
    docs_loggable
)
mcp.resource(
    "clearskies://docs/injectable",
    name="docs_injectable",
    description="Documentation about the Injectable abstract base class.",
)(docs_injectable)
mcp.resource(
    "clearskies://docs/configs-module",
    name="docs_configs_module",
    description="Documentation about the configs module.",
)(docs_configs_module)
mcp.resource(
    "clearskies://docs/component-inheritance",
    name="docs_component_inheritance",
    description="Documentation about component inheritance hierarchy.",
)(docs_component_inheritance)

# Example resources
mcp.resource(
    "clearskies://examples/restful-api",
    name="example_restful_api",
    description="Complete example of a clearskies RESTful API.",
)(example_restful_api)
mcp.resource(
    "clearskies://examples/relationships",
    name="example_relationships",
    description="Example of clearskies models with relationships.",
)(example_relationships)
mcp.resource(
    "clearskies://examples/authentication",
    name="example_authentication",
    description="Example of clearskies authentication.",
)(example_authentication)
mcp.resource(
    "clearskies://examples/cli-app", name="example_cli_app", description="Example of a clearskies CLI application."
)(example_cli_app)
mcp.resource(
    "clearskies://examples/api-backend",
    name="example_api_backend",
    description="Example of using clearskies as an API client with ApiBackend.",
)(example_api_backend)
mcp.resource(
    "clearskies://examples/testing", name="example_testing", description="Example of testing clearskies applications."
)(example_testing)
mcp.resource(
    "clearskies://examples/authorization",
    name="example_authorization",
    description="Example of clearskies authorization patterns.",
)(example_authorization)
mcp.resource(
    "clearskies://examples/error-handling",
    name="example_error_handling",
    description="Example of clearskies error handling.",
)(example_error_handling)
mcp.resource(
    "clearskies://examples/endpoint-group",
    name="example_endpoint_group",
    description="Example of clearskies endpoint groups.",
)(example_endpoint_group)
mcp.resource(
    "clearskies://examples/migrations",
    name="example_migrations",
    description="Example of clearskies database migrations.",
)(example_migrations)
mcp.resource(
    "clearskies://examples/hierarchical-data",
    name="example_hierarchical_data",
    description="Example of hierarchical data with CategoryTree columns.",
)(example_hierarchical_data)
mcp.resource(
    "clearskies://examples/audit-trail",
    name="example_audit_trail",
    description="Example of audit trail tracking with the Audit column.",
)(example_audit_trail)
mcp.resource(
    "clearskies://examples/pivot-data",
    name="example_pivot_data",
    description="Example of many-to-many relationships with pivot data.",
)(example_pivot_data)
mcp.resource(
    "clearskies://examples/advanced-queries",
    name="example_advanced_queries",
    description="Example of advanced query patterns in clearskies.",
)(example_advanced_queries)
mcp.resource(
    "clearskies://examples/configuration",
    name="example_configuration",
    description="Example of configuration management in clearskies.",
)(example_configuration)
mcp.resource(
    "clearskies://examples/state-machine-advanced",
    name="example_state_machine_advanced",
    description="Example of advanced state machine patterns in clearskies.",
)(example_state_machine_advanced)
mcp.resource(
    "clearskies://examples/secrets-backend",
    name="example_secrets_backend",
    description="Example of using the secrets backend in clearskies.",
)(example_secrets_backend)

# Module resources
mcp.resource(
    "clearskies://modules/overview",
    name="modules_overview",
    description="Overview of all clearskies extension modules.",
)(modules_overview)
mcp.resource("clearskies://modules/aws", name="module_aws", description="Documentation for the clearskies-aws module.")(
    module_aws
)
mcp.resource(
    "clearskies://modules/graphql",
    name="module_graphql",
    description="Documentation for the clearskies-graphql module.",
)(module_graphql)
mcp.resource(
    "clearskies://modules/gitlab", name="module_gitlab", description="Documentation for the clearskies-gitlab module."
)(module_gitlab)
mcp.resource(
    "clearskies://modules/cortex", name="module_cortex", description="Documentation for the clearskies-cortex module."
)(module_cortex)
mcp.resource(
    "clearskies://modules/snyk", name="module_snyk", description="Documentation for the clearskies-snyk module."
)(module_snyk)
mcp.resource(
    "clearskies://modules/akeyless",
    name="module_akeyless",
    description="Documentation for the clearskies-akeyless-custom-producer module.",
)(module_akeyless)

# Style resources
mcp.resource(
    "clearskies://style/docstrings",
    name="style_docstrings",
    description="Docstring style guide for clearskies framework code.",
)(style_docstrings)

# Migration resources (v1 → v2)
mcp.resource(
    "clearskies://migration/guide",
    name="migration_guide",
    description="Complete guide for migrating from clearskies v1 to v2.",
)(migration_guide)
mcp.resource(
    "clearskies://migration/breaking-changes",
    name="breaking_changes",
    description="Complete list of breaking changes between v1 and v2.",
)(breaking_changes)
mcp.resource(
    "clearskies://migration/patterns",
    name="migration_patterns",
    description="Common v1 patterns and their v2 equivalents.",
)(migration_patterns)


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
