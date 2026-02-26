"""
Secrets backend example for clearskies framework.

This module contains a complete example demonstrating how to use the SecretsBackend
to store sensitive configuration data in a secrets manager.
"""


def example_secrets_backend() -> str:
    """Complete example of using the SecretsBackend in clearskies."""
    return '''\
# Secrets Backend Example

This example demonstrates how to use clearskies SecretsBackend to store and manage
sensitive configuration data like API keys, database credentials, and service tokens.

## Basic Secrets Backend Usage

```python
import clearskies
from clearskies import columns
from datetime import datetime

# =============================================================================
# API CREDENTIALS MODEL
# =============================================================================

class ApiCredential(clearskies.Model):
    """Store API credentials in a secrets manager."""
    id_column_name = "id"
    backend = clearskies.backends.SecretsBackend(
        secret_prefix="api-credentials/",
    )

    id = columns.String()  # e.g., "stripe-production"
    provider = columns.String()  # e.g., "stripe", "twilio", "sendgrid"
    environment = columns.Select(["development", "staging", "production"])
    api_key = columns.String()
    api_secret = columns.String()
    webhook_secret = columns.String()
    created_at = columns.Created()
    updated_at = columns.Updated()
    last_rotated_at = columns.Datetime()

    def rotate_key(self, new_api_key: str, new_api_secret: str = None):
        """Rotate the API credentials."""
        data = {
            "api_key": new_api_key,
            "last_rotated_at": datetime.utcnow(),
        }
        if new_api_secret:
            data["api_secret"] = new_api_secret
        self.save(data)


# =============================================================================
# DATABASE CREDENTIALS MODEL
# =============================================================================

class DatabaseCredential(clearskies.Model):
    """Store database connection credentials."""
    id_column_name = "id"
    backend = clearskies.backends.SecretsBackend(
        secret_prefix="database-credentials/",
    )

    id = columns.String()  # e.g., "main-db-production"
    name = columns.String()
    engine = columns.Select(["mysql", "postgresql", "mongodb", "redis"])
    host = columns.String()
    port = columns.Integer()
    database = columns.String()
    username = columns.String()
    password = columns.String()
    ssl_enabled = columns.Boolean(default=True)
    ssl_ca_cert = columns.String()  # Base64 encoded certificate
    created_at = columns.Created()
    updated_at = columns.Updated()

    def get_connection_string(self) -> str:
        """Generate a connection string for this database."""
        if self.engine == "mysql":
            ssl = "?ssl=true" if self.ssl_enabled else ""
            return f"mysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}{ssl}"
        elif self.engine == "postgresql":
            ssl = "?sslmode=require" if self.ssl_enabled else ""
            return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}{ssl}"
        elif self.engine == "mongodb":
            ssl = "?ssl=true" if self.ssl_enabled else ""
            return f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}{ssl}"
        elif self.engine == "redis":
            return f"redis://:{self.password}@{self.host}:{self.port}"
        else:
            raise ValueError(f"Unsupported engine: {self.engine}")

    def get_connection_dict(self) -> dict:
        """Get connection parameters as a dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "database": self.database,
            "user": self.username,
            "password": self.password,
            "ssl": self.ssl_enabled,
        }


# =============================================================================
# SERVICE TOKEN MODEL WITH ROTATION
# =============================================================================

class ServiceToken(clearskies.Model):
    """Store service-to-service authentication tokens with rotation support."""
    id_column_name = "id"
    backend = clearskies.backends.SecretsBackend(
        secret_prefix="service-tokens/",
    )

    id = columns.String()  # e.g., "auth-service-token"
    service_name = columns.String()
    description = columns.String()

    # Current and previous tokens for zero-downtime rotation
    current_token = columns.String()
    previous_token = columns.String()

    # Rotation tracking
    rotated_at = columns.Datetime()
    rotation_count = columns.Integer(default=0)

    created_at = columns.Created()
    updated_at = columns.Updated()

    def rotate(self, new_token: str):
        """Rotate to a new token while keeping the previous one valid."""
        self.save({
            "previous_token": self.current_token,
            "current_token": new_token,
            "rotated_at": datetime.utcnow(),
            "rotation_count": self.rotation_count + 1,
        })

    def validate_token(self, token: str) -> bool:
        """Check if a token is valid (current or previous)."""
        return token in [self.current_token, self.previous_token]

    def invalidate_previous(self):
        """Invalidate the previous token after rotation grace period."""
        self.save({"previous_token": None})


# =============================================================================
# USAGE WITH AWS SECRETS MANAGER
# =============================================================================

# Using clearskies-aws for AWS Secrets Manager integration:

"""
import clearskies
import clearskies_aws
from clearskies import columns

class AwsApiCredential(clearskies.Model):
    id_column_name = "id"
    backend = clearskies_aws.backends.SecretsManagerBackend(
        secret_prefix="myapp/api-credentials/",
        region="us-east-1",
        # Optional: Use a specific KMS key for encryption
        kms_key_id="arn:aws:kms:us-east-1:123456789:key/12345678-1234-1234-1234-123456789012",
    )

    id = columns.String()
    api_key = columns.String()
    api_secret = columns.String()
"""


# =============================================================================
# USAGE WITH AKEYLESS
# =============================================================================

# Using clearskies-akeyless for Akeyless integration:

"""
import clearskies
import clearskies_akeyless_custom_producer
from clearskies import columns

class AkeylessCredential(clearskies.Model):
    id_column_name = "id"
    backend = clearskies_akeyless_custom_producer.backends.AkeylessBackend(
        secret_path="/myapp/credentials/",
    )

    id = columns.String()
    username = columns.String()
    password = columns.String()
"""


# =============================================================================
# CREDENTIAL MANAGER SERVICE
# =============================================================================

class CredentialManager:
    """Service for managing credentials across the application."""

    def __init__(self):
        self.api_credentials = ApiCredential()
        self.db_credentials = DatabaseCredential()
        self.service_tokens = ServiceToken()

    def get_api_key(self, provider: str, environment: str) -> str:
        """Get API key for a provider and environment."""
        cred = self.api_credentials.find(f"provider={provider}").find(f"environment={environment}")
        if not cred.exists:
            raise ValueError(f"No API credential found for {provider}/{environment}")
        return cred.api_key

    def get_database_connection(self, name: str) -> str:
        """Get database connection string by name."""
        cred = self.db_credentials.find(f"name={name}")
        if not cred.exists:
            raise ValueError(f"No database credential found for {name}")
        return cred.get_connection_string()

    def validate_service_token(self, service: str, token: str) -> bool:
        """Validate a service token."""
        svc_token = self.service_tokens.find(f"service_name={service}")
        if not svc_token.exists:
            return False
        return svc_token.validate_token(token)


# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # Create API credentials
    api_creds = ApiCredential()
    stripe_cred = api_creds.create({
        "id": "stripe-production",
        "provider": "stripe",
        "environment": "production",
        "api_key": "sk_live_...",
        "api_secret": "whsec_...",
        "webhook_secret": "whsec_...",
    })
    print(f"Created Stripe credential: {stripe_cred.id}")

    # Create database credentials
    db_creds = DatabaseCredential()
    main_db = db_creds.create({
        "id": "main-db-production",
        "name": "main-database",
        "engine": "postgresql",
        "host": "db.example.com",
        "port": 5432,
        "database": "myapp",
        "username": "app_user",
        "password": "super-secret-password",
        "ssl_enabled": True,
    })
    print(f"Created database credential: {main_db.id}")
    print(f"Connection string: {main_db.get_connection_string()}")

    # Create service token with rotation
    tokens = ServiceToken()
    auth_token = tokens.create({
        "id": "auth-service-token",
        "service_name": "auth-service",
        "description": "Token for auth service communication",
        "current_token": "initial-token-abc123",
    })
    print(f"Created service token: {auth_token.id}")

    # Rotate the token
    auth_token.rotate("new-token-xyz789")
    print(f"Rotated token. Current: {auth_token.current_token[:10]}...")
    print(f"Previous still valid: {auth_token.validate_token('initial-token-abc123')}")

    # Use credential manager
    manager = CredentialManager()
    try:
        stripe_key = manager.get_api_key("stripe", "production")
        print(f"Retrieved Stripe key: {stripe_key[:10]}...")
    except ValueError as e:
        print(f"Error: {e}")
```

## Best Practices

1. **Use meaningful IDs** - Make secrets easy to identify (e.g., "stripe-production")
2. **Implement rotation** - Support zero-downtime credential rotation
3. **Separate by environment** - Don't mix dev/staging/prod credentials
4. **Use KMS encryption** - Enable encryption at rest for sensitive data
5. **Audit access** - Enable logging for secret access
6. **Limit permissions** - Use IAM policies to restrict who can read secrets
7. **Don't log secrets** - Never log credential values
8. **Validate on startup** - Check that required credentials exist at app startup
'''
