"""
Example code snippets for clearskies framework.

This module contains complete, runnable examples demonstrating various
clearskies features and patterns.
"""

from .advanced_queries import example_advanced_queries
from .api_backend import example_api_backend
from .audit_trail import example_audit_trail
from .authentication import example_authentication
from .authorization import example_authorization
from .cli_app import example_cli_app
from .configuration import example_configuration
from .endpoint_group import example_endpoint_group
from .error_handling import example_error_handling
from .hierarchical_data import example_hierarchical_data
from .migrations import example_migrations
from .pivot_data import example_pivot_data
from .relationships import example_relationships
from .restful_api import example_restful_api
from .secrets_backend import example_secrets_backend
from .state_machine_advanced import example_state_machine_advanced
from .testing import example_testing

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
