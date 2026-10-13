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

        The `clearskies.endpoints.Mygrations` endpoint runs the
        [mygrations](https://github.com/cmancone/mygrations) library.

        ## Overview

        Mygrations is a stateless migration tool:
        - You write the desired schema as SQL `CREATE TABLE` statements (files or strings)
        - It compares that SQL with the live database and calculates the changes
        - You review with `plan` and apply with `apply` (like IaC)
        - It does **not** read clearskies models; keep models and SQL in sync by hand
        - Supports MySQL/MariaDB

        ## Installation

        ```bash
        pip install mygrations
        ```

        ## Basic Setup

        ```sql
        -- database/users.sql
        CREATE TABLE `users` (
          `id` CHAR(36) NOT NULL,
          `name` VARCHAR(255) NOT NULL DEFAULT '',
          `email` VARCHAR(255) NOT NULL DEFAULT '',
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ```

        ```python
        # mygrate.py
        import clearskies

        cli = clearskies.contexts.Cli(
            clearskies.endpoints.Mygrations(
                allow_input=True,
                sql=["./database/"],
            )
        )
        cli()
        ```

        The database connection comes from the default `cursor` binding, which reads
        `DATABASE_HOST`, `DATABASE_USERNAME`, `DATABASE_PASSWORD`, `DATABASE_NAME` and
        (optionally) `DATABASE_PORT` from the environment.

        ## Running Migrations

        ```bash
        ./mygrate.py --command=check   # validate the SQL files
        ./mygrate.py --command=plan    # show the changes (dry run)
        ./mygrate.py --command=apply   # apply the changes
        ```

        ## Mygrations Endpoint Configuration

        | Parameter | Type | Description |
        |-----------|------|-------------|
        | `sql` | list[str] | SQL strings, `.sql` file paths, or directories of `.sql` files (default `["./database"]`) |
        | `command` | str | `version` (default), `check`, `plan`, `plan_export`, or `apply` |
        | `allow_input` | bool | Allow `command`/`sql` to come from request data, e.g. `--command=plan` (default `False`) |
        | `cursor` | Cursor | Cursor to use, e.g. `clearskies.cursors.from_environment.Mysql()` (optional) |
        | `cursor_dependency_name` | str | DI name to build the cursor from when `cursor` is not given (default `"cursor"`) |
        | `include_module_migrations` | bool | Also run SQL from `clearskies.di.AdditionalMygrationsAutoImport` subclasses in loaded modules (default `False`) |
        | `module_migrations` | list[str] | Allow-list of those subclass names; empty means all |
        | `url` | str | URL to mount the endpoint at |

        ## Schema Changes

        Edit the `CREATE TABLE` file (and the matching model column), run `plan`, review,
        then `apply`. Removing a column or index from the SQL makes mygrations drop it.

        ## Best Practices

        1. **Always run `plan` first** – Review changes before applying
        2. **Backup before destructive changes** – Column removals, type changes
        3. **Commit SQL files with model changes** – They must stay in sync
        4. **Test in staging** – Before applying to production

        ## Limitations

        - MySQL/MariaDB only
        - Schema only, no data migrations
        - No rollback; revert the SQL files and re-apply instead
        - Requires the mygrations library to be installed separately
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
        # The default `cursor` reads DATABASE_HOST, DATABASE_USERNAME,
        # DATABASE_PASSWORD, DATABASE_NAME (and optional DATABASE_PORT) from the environment
        class User(clearskies.Model):
            backend = clearskies.backends.CursorBackend()
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
