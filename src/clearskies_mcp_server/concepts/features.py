"""
Feature concept explanations for clearskies framework.

This module contains explanations for autodoc, migrations, and configuration.
"""

import textwrap

FEATURES_CONCEPTS = {
    "autodoc": textwrap.dedent("""\
        # clearskies Autodoc

        clearskies can automatically generate API documentation from your endpoint configurations.

        ## OpenAPI 3.0 (OAI3)

        clearskies includes an OpenAPI 3.0 JSON formatter that can produce complete API specs:

        ```python
        from clearskies.autodoc.formats.oai3_json import Oai3Json

        # Generate OpenAPI spec from your endpoints
        schema_endpoint = clearskies.endpoints.Schema(
            endpoint=my_restful_api,
            format=Oai3Json,
        )
        ```

        This automatically documents:
        - Request/response schemas
        - URL parameters and query parameters
        - Request bodies
        - Authentication requirements
        - Pagination details
    """),
    "migrations": textwrap.dedent("""\
        # clearskies Migrations (Mygrations)

        clearskies provides database migration support through the Mygrations endpoint, which
        integrates with the mygrations library for schema evolution.

        ## Overview

        Mygrations is a database migration tool that:
        - Automatically detects schema changes from your model definitions
        - Generates migration SQL based on differences
        - Supports MySQL/MariaDB databases
        - Can run in "check" mode to validate without applying changes

        ## Installation

        ```bash
        pip install mygrations
        ```

        ## Basic Setup

        ```python
        import clearskies
        from clearskies import columns

        class User(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            name = columns.String(max_length=255)
            email = columns.Email(max_length=255)
            created_at = columns.Created()
            updated_at = columns.Updated()

        # Create a migrations endpoint
        migrations_endpoint = clearskies.endpoints.Mygrations(
            models=[User],
            connection_string_environment_key="DATABASE_URL",
        )

        # Run as CLI
        cli = clearskies.contexts.Cli(migrations_endpoint)
        cli()
        ```

        ## Running Migrations

        ```bash
        # Check what migrations would be applied (dry run)
        python app.py --check

        # Apply migrations
        python app.py --apply

        # Show current schema status
        python app.py --status
        ```

        ## Mygrations Endpoint Configuration

        | Parameter | Type | Description |
        |-----------|------|-------------|
        | `models` | list | List of model classes to include in migrations |
        | `connection_string_environment_key` | str | Environment variable containing database connection string |
        | `cursor_backend_class` | class | Custom cursor backend class (optional) |

        ## Schema Evolution Strategies

        ### Adding Columns

        Simply add a new column to your model:

        ```python
        class User(clearskies.Model):
            # ... existing columns ...
            phone = columns.Phone(max_length=20)  # New column
        ```

        Run migrations to apply the change.

        ### Removing Columns

        Remove the column from your model definition. Mygrations will detect the removal
        and generate the appropriate DROP COLUMN statement.

        **Warning:** Removing columns is destructive. Always backup data before applying.

        ### Modifying Columns

        Change the column definition (e.g., max_length, type):

        ```python
        # Before
        name = columns.String(max_length=100)

        # After
        name = columns.String(max_length=255)
        ```

        ### Adding Indexes

        Use the `index` parameter on columns:

        ```python
        email = columns.Email(max_length=255, index=True)
        ```

        ### Adding Unique Constraints

        Use validators or column parameters:

        ```python
        from clearskies.validators import Unique

        email = columns.Email(validators=[Unique()])
        ```

        ## Best Practices

        1. **Always run --check first** – Review changes before applying
        2. **Backup before destructive changes** – Column removals, type changes
        3. **Use version control** – Track model changes alongside migrations
        4. **Test migrations in staging** – Before applying to production
        5. **Keep models and database in sync** – Don't manually modify the database

        ## Integration with CI/CD

        ```yaml
        # Example GitLab CI job
        migrate:
          stage: deploy
          script:
            - python app.py --check  # Validate first
            - python app.py --apply  # Apply if check passes
          only:
            - main
        ```

        ## Rollback Strategies

        Mygrations doesn't provide automatic rollback. For rollback:

        1. **Revert code changes** – Return to previous model definitions
        2. **Run migrations again** – Mygrations will generate reverse changes
        3. **Manual intervention** – For data migrations, manual SQL may be needed

        ## Limitations

        - Currently supports MySQL/MariaDB only
        - No automatic data migrations (schema only)
        - No built-in rollback mechanism
        - Requires mygrations library to be installed separately
    """),
    "configuration": textwrap.dedent("""\
        # Configuration Management in clearskies

        clearskies provides flexible configuration management through environment variables,
        dependency injection bindings, and secrets management integration.

        ## Environment Variables

        The primary configuration method in clearskies is environment variables:

        ### Accessing Environment Variables

        ```python
        import os

        # Direct access
        database_url = os.environ.get("DATABASE_URL")
        api_key = os.environ.get("API_KEY")

        # With defaults
        debug_mode = os.environ.get("DEBUG", "false").lower() == "true"
        port = int(os.environ.get("PORT", "8080"))
        ```

        ### Environment Variables in Authentication

        ```python
        import clearskies

        # SecretBearer reads from environment
        endpoint = clearskies.endpoints.RestfulApi(
            model_class=User,
            authentication=clearskies.authentication.SecretBearer(
                environment_key="API_SECRET",  # Reads from API_SECRET env var
            ),
        )
        ```

        ### Environment Variables in Backends

        ```python
        # Database connection string from environment
        class User(clearskies.Model):
            backend = clearskies.backends.CursorBackend(
                connection_string_environment_key="DATABASE_URL",
            )
        ```

        ## Dependency Injection Bindings

        Use DI bindings for configuration values:

        ```python
        import clearskies

        def my_service(api_base_url: str, timeout: int):
            # These are injected from bindings
            return f"Connecting to {api_base_url} with timeout {timeout}"

        cli = clearskies.contexts.Cli(
            my_service,
            bindings={
                "api_base_url": os.environ.get("API_BASE_URL", "https://api.example.com"),
                "timeout": int(os.environ.get("TIMEOUT", "30")),
            },
        )
        ```

        ## Configuration Classes

        For complex configuration, create a configuration class:

        ```python
        import os
        from dataclasses import dataclass

        @dataclass
        class AppConfig:
            database_url: str
            api_key: str
            debug: bool
            max_connections: int

            @classmethod
            def from_environment(cls) -> "AppConfig":
                return cls(
                    database_url=os.environ["DATABASE_URL"],
                    api_key=os.environ["API_KEY"],
                    debug=os.environ.get("DEBUG", "false").lower() == "true",
                    max_connections=int(os.environ.get("MAX_CONNECTIONS", "10")),
                )

        # Register with DI
        config = AppConfig.from_environment()

        cli = clearskies.contexts.Cli(
            my_endpoint,
            bindings={"config": config},
        )
        ```

        ## Secrets Management

        ### Using clearskies-aws for Secrets

        ```python
        import clearskies
        import clearskies_aws

        # Secrets are automatically fetched from AWS Secrets Manager
        class User(clearskies.Model):
            backend = clearskies.backends.CursorBackend()

        # The cursor backend can use secrets for connection strings
        cli = clearskies_aws.contexts.LambdaHttp(
            my_endpoint,
            secrets={
                "database": "arn:aws:secretsmanager:us-east-1:123456789:secret:db-creds",
            },
        )
        ```

        ### Using clearskies-akeyless

        ```python
        import clearskies
        import clearskies_akeyless_custom_producer

        # Fetch secrets from Akeyless
        cli = clearskies.contexts.Cli(
            my_endpoint,
            bindings={
                "akeyless_access_id": os.environ["AKEYLESS_ACCESS_ID"],
                "akeyless_access_key": os.environ["AKEYLESS_ACCESS_KEY"],
            },
        )
        ```

        ## Development vs Production Configuration

        ### Using .env Files (Development)

        ```bash
        # .env file (not committed to version control)
        DATABASE_URL=mysql://localhost/myapp_dev
        API_KEY=dev-key-12345
        DEBUG=true
        ```

        ```python
        # Load .env in development
        from dotenv import load_dotenv
        load_dotenv()

        # Then use os.environ as normal
        ```

        ### Production Configuration

        In production, set environment variables through:
        - Container orchestration (Kubernetes, ECS)
        - Serverless configuration (Lambda environment)
        - CI/CD pipelines
        - Cloud provider secret managers

        ## Configuration Validation

        Validate configuration at startup:

        ```python
        import os
        import sys

        REQUIRED_ENV_VARS = [
            "DATABASE_URL",
            "API_KEY",
        ]

        def validate_config():
            missing = [var for var in REQUIRED_ENV_VARS if var not in os.environ]
            if missing:
                print(f"Missing required environment variables: {', '.join(missing)}")
                sys.exit(1)

        # Call at application startup
        validate_config()
        ```

        ## Configuration Best Practices

        1. **Never hardcode secrets** – Always use environment variables or secret managers
        2. **Use sensible defaults** – For non-sensitive configuration
        3. **Validate early** – Check configuration at startup, not runtime
        4. **Document required variables** – In README or deployment docs
        5. **Use typed configuration** – Dataclasses or similar for type safety
        6. **Separate environments** – Different configs for dev/staging/prod
        7. **Use secret managers in production** – AWS Secrets Manager, Akeyless, etc.

        ## Example: Complete Configuration Setup

        ```python
        import os
        import sys
        from dataclasses import dataclass
        from typing import Optional

        import clearskies
        from clearskies import columns

        @dataclass
        class Config:
            database_url: str
            api_secret: str
            debug: bool = False
            log_level: str = "INFO"

            @classmethod
            def from_environment(cls) -> "Config":
                required = ["DATABASE_URL", "API_SECRET"]
                missing = [v for v in required if v not in os.environ]
                if missing:
                    raise ValueError(f"Missing: {', '.join(missing)}")

                return cls(
                    database_url=os.environ["DATABASE_URL"],
                    api_secret=os.environ["API_SECRET"],
                    debug=os.environ.get("DEBUG", "false").lower() == "true",
                    log_level=os.environ.get("LOG_LEVEL", "INFO"),
                )

        # Load and validate configuration
        try:
            config = Config.from_environment()
        except ValueError as e:
            print(f"Configuration error: {e}")
            sys.exit(1)

        class User(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            name = columns.String()

        wsgi = clearskies.contexts.WsgiRef(
            clearskies.endpoints.RestfulApi(
                url="users",
                model_class=User,
                authentication=clearskies.authentication.SecretBearer(
                    environment_key="API_SECRET",
                ),
                readable_column_names=["id", "name"],
                writeable_column_names=["name"],
                default_sort_column_name="name",
            ),
            bindings={"config": config},
        )

        if __name__ == "__main__":
            if config.debug:
                print("Running in debug mode")
            wsgi()
        ```
    """),
}
