"""
Documentation resources for clearskies framework.

This module contains resource functions that provide documentation content
for various clearskies concepts.
"""

import textwrap

from ..tools.documentation import explain_concept


def docs_overview() -> str:
    """Overview of the clearskies framework."""
    return textwrap.dedent("""\
        # clearskies Framework Overview

        clearskies is a very opinionated Python framework intended for developing microservices in the cloud
        via declarative programming principles. It is mainly intended for backend services: RESTful API
        endpoints, queue listeners, scheduled tasks, and the like.

        ## Key Principles

        1. **Declarative Programming** – Configure endpoints instead of writing controllers
        2. **Infrastructure Neutral** – Same code runs in CLI, WSGI, serverless, etc.
        3. **State Machine Business Logic** – Organize logic around state transitions
        4. **Dependency Injection** – Automatic DI with type-hint resolution
        5. **Secrets Management** – Built-in secrets management support
        6. **Sideloading** – Flexible dependency injection system

        ## Quick Start

        ```python
        import clearskies
        from clearskies import columns

        class User(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            name = columns.String()
            email = columns.Email()

        wsgi = clearskies.contexts.WsgiRef(
            clearskies.endpoints.RestfulApi(
                url="users",
                model_class=User,
                readable_column_names=["id", "name", "email"],
                writeable_column_names=["name", "email"],
                default_sort_column_name="name",
            )
        )
        wsgi()
        ```

        ## Installation

        ```bash
        pip install clear-skies
        ```

        ## Components

        - **Models** – Data schema and business logic
        - **Endpoints** – Declarative API behavior
        - **Backends** – Data storage abstraction
        - **Columns** – Type definitions and validation
        - **Contexts** – Hosting environment abstraction
        - **Authentication** – Bearer token, JWKS, custom auth
        - **Validators** – Data validation rules
    """)


def docs_models() -> str:
    """Detailed documentation about clearskies Models."""
    return explain_concept("model")


def docs_endpoints() -> str:
    """Documentation about clearskies Endpoints."""
    return explain_concept("endpoint")


def docs_columns() -> str:
    """Documentation about clearskies Column types."""
    return explain_concept("column")


def docs_backends() -> str:
    """Documentation about clearskies Backends."""
    return explain_concept("backend")


def docs_contexts() -> str:
    """Documentation about clearskies Contexts."""
    return explain_concept("context")


def docs_di() -> str:
    """Documentation about clearskies Dependency Injection."""
    return explain_concept("di")


def docs_authentication() -> str:
    """Documentation about clearskies Authentication."""
    return explain_concept("authentication")


def docs_save_lifecycle() -> str:
    """Documentation about the clearskies save lifecycle."""
    return explain_concept("save_lifecycle")


def docs_queries() -> str:
    """Documentation about clearskies queries."""
    return explain_concept("query")


def docs_validators() -> str:
    """Documentation about clearskies validators."""
    return explain_concept("validator")


def docs_testing() -> str:
    """Documentation about testing clearskies applications."""
    return explain_concept("testing")


def docs_authorization() -> str:
    """Documentation about clearskies authorization patterns."""
    return explain_concept("authorization")


def docs_error_handling() -> str:
    """Documentation about clearskies error handling."""
    return explain_concept("error_handling")


def docs_input_handling() -> str:
    """Documentation about clearskies input handling."""
    return explain_concept("input_handling")


def docs_endpoint_groups() -> str:
    """Documentation about clearskies endpoint groups."""
    return explain_concept("endpoint_groups")


def docs_routing() -> str:
    """Documentation about clearskies routing."""
    return explain_concept("routing")


def docs_responses() -> str:
    """Documentation about clearskies response customization."""
    return explain_concept("responses")


def docs_migrations() -> str:
    """Documentation about clearskies database migrations (Mygrations)."""
    return explain_concept("migrations")


def docs_advanced_columns() -> str:
    """Documentation about advanced clearskies column types."""
    return explain_concept("advanced_columns")


def docs_advanced_queries() -> str:
    """Documentation about advanced clearskies query patterns."""
    return explain_concept("advanced_queries")


def docs_configuration() -> str:
    """Documentation about clearskies configuration management."""
    return explain_concept("configuration")


def docs_logging() -> str:
    """Documentation about logging and observability in clearskies."""
    return explain_concept("logging")


def docs_caching() -> str:
    """Documentation about caching patterns in clearskies."""
    return explain_concept("caching")


def docs_async() -> str:
    """Documentation about async patterns in clearskies."""
    return explain_concept("async")


def docs_state_machine_advanced() -> str:
    """Documentation about advanced state machine patterns in clearskies."""
    return explain_concept("state_machine_advanced")


def docs_secrets_backend() -> str:
    """Documentation about the secrets backend in clearskies."""
    return explain_concept("secrets_backend")


# Phase 6.1: Backend Foundations
def docs_backend_memory() -> str:
    """Deep dive documentation about MemoryBackend."""
    return explain_concept("backend_memory")


def docs_backend_cursor() -> str:
    """Deep dive documentation about CursorBackend."""
    return explain_concept("backend_cursor")


def docs_cursors() -> str:
    """Documentation about cursors and raw SQL in clearskies."""
    return explain_concept("cursors")


def docs_transactions() -> str:
    """Documentation about transaction management in clearskies."""
    return explain_concept("transactions")


# Phase 6.2: Framework Internals
def docs_di_advanced() -> str:
    """Advanced DI patterns and troubleshooting in clearskies."""
    return explain_concept("di_advanced")


def docs_query_execution() -> str:
    """Documentation about query execution model in clearskies."""
    return explain_concept("query_execution")


def docs_model_lifecycle() -> str:
    """Documentation about model lifecycle in clearskies."""
    return explain_concept("model_lifecycle")


def docs_input_output() -> str:
    """Documentation about the input/output system in clearskies."""
    return explain_concept("input_output")


# Phase 6.3: Developer Experience
def docs_troubleshooting() -> str:
    """Troubleshooting guide for clearskies applications."""
    return explain_concept("troubleshooting")


def docs_best_practices() -> str:
    """Best practices for clearskies development."""
    return explain_concept("best_practices")


def docs_exceptions() -> str:
    """Exception hierarchy reference for clearskies."""
    return explain_concept("exceptions")


def docs_auth_flow() -> str:
    """Return authentication and authorization flow documentation."""
    return explain_concept("auth_flow")


# Phase 6.4: Reference Material
def docs_column_reference() -> str:
    """Return complete column parameter reference for clearskies."""
    return explain_concept("column_reference")


def docs_endpoint_reference() -> str:
    """Return complete endpoint parameter reference for clearskies."""
    return explain_concept("endpoint_reference")


def docs_performance() -> str:
    """Return performance guide for clearskies applications."""
    return explain_concept("performance")


def docs_patterns() -> str:
    """Return common patterns cookbook for clearskies."""
    return explain_concept("patterns")
