"""
Example resources for clearskies framework.

This module provides resource functions that return example code snippets.
It delegates to the examples/ module for the actual content.
"""

from ..examples import (
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
    example_restful_api,
    example_secrets_backend,
    example_state_machine_advanced,
    example_testing,
)

__all__ = [
    "example_restful_api",
    "example_relationships",
    "example_authentication",
    "example_cli_app",
    "example_api_backend",
    "example_testing",
    "example_authorization",
    "example_error_handling",
    "example_endpoint_group",
    "example_migrations",
    "example_hierarchical_data",
    "example_audit_trail",
    "example_pivot_data",
    "example_advanced_queries",
    "example_configuration",
    "example_state_machine_advanced",
    "example_secrets_backend",
]
