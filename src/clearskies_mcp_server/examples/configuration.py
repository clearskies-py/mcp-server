"""
Example of configuration management in clearskies.

This module demonstrates how to manage configuration through environment
variables, dependency injection, and secrets management.
"""

import textwrap


def example_configuration() -> str:
    """Complete example of configuration management in clearskies."""
    return textwrap.dedent('''\
        # clearskies Configuration Management Example

        This example demonstrates how to manage application configuration through
        environment variables, dependency injection bindings, and secrets management.

        ## Complete Example

        ```python
        """
        Configuration management example with clearskies.

        This script demonstrates:
        - Environment variable configuration
        - Configuration classes with validation
        - Dependency injection bindings
        - Development vs production configuration
        - Secrets management integration
        """
        import os
        import sys
        from dataclasses import dataclass, field
        from typing import Optional, List

        import clearskies
        from clearskies import columns
        from clearskies.validators import Required


        # =============================================================================
        # CONFIGURATION CLASS
        # =============================================================================

        @dataclass
        class AppConfig:
            """
            Application configuration with validation.

            All configuration is loaded from environment variables with sensible defaults.
            """
            # Required settings (no defaults)
            database_url: str
            api_secret: str

            # Optional settings with defaults
            debug: bool = False
            log_level: str = "INFO"
            max_connections: int = 10
            request_timeout: int = 30
            allowed_origins: List[str] = field(default_factory=lambda: ["*"])

            # Feature flags
            enable_caching: bool = True
            enable_metrics: bool = False

            @classmethod
            def from_environment(cls) -> "AppConfig":
                """
                Load configuration from environment variables.

                Raises ValueError if required variables are missing.
                """
                # Check required variables
                required = ["DATABASE_URL", "API_SECRET"]
                missing = [var for var in required if var not in os.environ]
                if missing:
                    raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

                # Parse allowed origins (comma-separated)
                origins_str = os.environ.get("ALLOWED_ORIGINS", "*")
                allowed_origins = [o.strip() for o in origins_str.split(",")]

                return cls(
                    # Required
                    database_url=os.environ["DATABASE_URL"],
                    api_secret=os.environ["API_SECRET"],
                    # Optional with defaults
                    debug=os.environ.get("DEBUG", "false").lower() == "true",
                    log_level=os.environ.get("LOG_LEVEL", "INFO").upper(),
                    max_connections=int(os.environ.get("MAX_CONNECTIONS", "10")),
                    request_timeout=int(os.environ.get("REQUEST_TIMEOUT", "30")),
                    allowed_origins=allowed_origins,
                    # Feature flags
                    enable_caching=os.environ.get("ENABLE_CACHING", "true").lower() == "true",
                    enable_metrics=os.environ.get("ENABLE_METRICS", "false").lower() == "true",
                )

            def validate(self) -> None:
                """Validate configuration values."""
                if self.max_connections < 1:
                    raise ValueError("MAX_CONNECTIONS must be at least 1")
                if self.request_timeout < 1:
                    raise ValueError("REQUEST_TIMEOUT must be at least 1")
                if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
                    raise ValueError(f"Invalid LOG_LEVEL: {self.log_level}")


        # =============================================================================
        # MODEL WITH CONFIGURATION
        # =============================================================================

        class User(clearskies.Model):
            """User model using configuration for backend."""
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            email = columns.Email(max_length=255, validators=[Required()])
            name = columns.String(max_length=255, validators=[Required()])
            created_at = columns.Created()


        # =============================================================================
        # SERVICE WITH INJECTED CONFIGURATION
        # =============================================================================

        class UserService:
            """Service that uses injected configuration."""

            def __init__(self, config: AppConfig, users: User):
                self.config = config
                self.users = users

            def get_active_users(self, limit: int = None):
                """Get active users with configurable limit."""
                limit = limit or self.config.max_connections
                return self.users.where("status=active").limit(limit)

            def is_debug_mode(self) -> bool:
                """Check if running in debug mode."""
                return self.config.debug


        # =============================================================================
        # APPLICATION SETUP
        # =============================================================================

        def create_app():
            """Create and configure the application."""
            # Load and validate configuration
            try:
                config = AppConfig.from_environment()
                config.validate()
            except ValueError as e:
                print(f"Configuration error: {e}", file=sys.stderr)
                sys.exit(1)

            # Configure logging based on config
            import logging
            logging.basicConfig(level=getattr(logging, config.log_level))
            logger = logging.getLogger(__name__)

            if config.debug:
                logger.info("Running in DEBUG mode")

            # Create endpoint
            endpoint = clearskies.endpoints.RestfulApi(
                url="users",
                model_class=User,
                authentication=clearskies.authentication.SecretBearer(
                    environment_key="API_SECRET",
                ),
                readable_column_names=["id", "email", "name", "created_at"],
                writeable_column_names=["email", "name"],
                default_sort_column_name="created_at",
            )

            # Create context with configuration bindings
            wsgi = clearskies.contexts.WsgiRef(
                endpoint,
                bindings={
                    "config": config,
                    "debug": config.debug,
                    "log_level": config.log_level,
                },
                classes=[User, UserService],
            )

            return wsgi


        if __name__ == "__main__":
            app = create_app()
            app()
        ```

        ## Environment Variables Reference

        Create a `.env` file for local development:

        ```bash
        # .env - Development configuration
        # DO NOT commit this file to version control!

        # Required
        DATABASE_URL=mysql://user:password@localhost/myapp_dev
        API_SECRET=dev-secret-key-12345

        # Optional
        DEBUG=true
        LOG_LEVEL=DEBUG
        MAX_CONNECTIONS=5
        REQUEST_TIMEOUT=60
        ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080

        # Feature flags
        ENABLE_CACHING=false
        ENABLE_METRICS=true
        ```

        ## Loading .env Files

        ```python
        """
        Load .env file in development.
        """
        import os

        def load_dotenv():
            """Load .env file if it exists."""
            env_file = ".env"
            if os.path.exists(env_file):
                with open(env_file) as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            os.environ.setdefault(key.strip(), value.strip())

        # Or use python-dotenv package
        # pip install python-dotenv
        # from dotenv import load_dotenv
        # load_dotenv()
        ```

        ## Multi-Environment Configuration

        ```python
        """
        Configuration for multiple environments.
        """
        import os
        from dataclasses import dataclass


        @dataclass
        class BaseConfig:
            """Base configuration shared across environments."""
            app_name: str = "MyApp"
            api_version: str = "v1"


        @dataclass
        class DevelopmentConfig(BaseConfig):
            """Development environment configuration."""
            debug: bool = True
            log_level: str = "DEBUG"
            database_url: str = "mysql://localhost/myapp_dev"


        @dataclass
        class StagingConfig(BaseConfig):
            """Staging environment configuration."""
            debug: bool = False
            log_level: str = "INFO"
            database_url: str = os.environ.get("DATABASE_URL", "")


        @dataclass
        class ProductionConfig(BaseConfig):
            """Production environment configuration."""
            debug: bool = False
            log_level: str = "WARNING"
            database_url: str = os.environ.get("DATABASE_URL", "")


        def get_config():
            """Get configuration based on environment."""
            env = os.environ.get("ENVIRONMENT", "development").lower()

            configs = {
                "development": DevelopmentConfig,
                "staging": StagingConfig,
                "production": ProductionConfig,
            }

            config_class = configs.get(env, DevelopmentConfig)
            return config_class()
        ```

        ## Secrets Management with AWS

        ```python
        """
        Configuration with AWS Secrets Manager.
        """
        import clearskies
        import clearskies_aws

        # Secrets are fetched from AWS Secrets Manager
        lambda_handler = clearskies_aws.contexts.LambdaHttp(
            my_endpoint,
            secrets={
                # Map local names to AWS secret ARNs
                "database": "arn:aws:secretsmanager:us-east-1:123456789:secret:prod/db",
                "api_keys": "arn:aws:secretsmanager:us-east-1:123456789:secret:prod/api",
            },
        )

        # Secrets are available in the DI container
        def my_handler(database: dict, api_keys: dict):
            db_url = database["url"]
            api_key = api_keys["primary"]
            # ...
        ```

        ## Configuration Validation at Startup

        ```python
        """
        Validate all configuration at application startup.
        """
        import os
        import sys


        def validate_environment():
            """Validate environment configuration at startup."""
            errors = []

            # Required variables
            required = ["DATABASE_URL", "API_SECRET"]
            for var in required:
                if var not in os.environ:
                    errors.append(f"Missing required: {var}")

            # Validate formats
            if "DATABASE_URL" in os.environ:
                url = os.environ["DATABASE_URL"]
                if not url.startswith(("mysql://", "postgresql://")):
                    errors.append("DATABASE_URL must be a valid database URL")

            # Validate numeric values
            if "MAX_CONNECTIONS" in os.environ:
                try:
                    val = int(os.environ["MAX_CONNECTIONS"])
                    if val < 1:
                        errors.append("MAX_CONNECTIONS must be positive")
                except ValueError:
                    errors.append("MAX_CONNECTIONS must be a number")

            # Report errors
            if errors:
                print("Configuration errors:", file=sys.stderr)
                for error in errors:
                    print(f"  - {error}", file=sys.stderr)
                sys.exit(1)

            print("Configuration validated successfully")


        if __name__ == "__main__":
            validate_environment()
            # Continue with application startup...
        ```

        ## Best Practices

        1. **Never hardcode secrets** - Always use environment variables
        2. **Validate early** - Check configuration at startup
        3. **Use typed configuration** - Dataclasses provide type safety
        4. **Document all variables** - In README or deployment docs
        5. **Use sensible defaults** - For non-sensitive settings
        6. **Separate environments** - Different configs for dev/staging/prod
        7. **Use secret managers** - In production (AWS, Akeyless, etc.)
        8. **Don\'t commit .env files** - Add to .gitignore
    ''')
