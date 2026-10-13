"""
Secrets example for clearskies framework.

This module contains a complete example demonstrating how to read secrets through the
`secrets` dependency and how to authenticate with `SecretBearer` backed by a secret manager.
"""


def example_secrets_backend() -> str:
    """Complete example of using secrets in clearskies."""
    return '''\
# Secrets Example

clearskies 2.x has no "secrets backend" for models. Secrets are a dependency named
`secrets` that you bind to a secret manager (for example `clearskies.secrets.Akeyless`)
and then use from callables, classes, and `SecretBearer` authentication.

## Runnable Example (fake secret manager)

This runs without any external service. Swap `FakeSecrets()` for a real secret
manager in production (see below).

```python
import json

import clearskies
from clearskies.di import inject


class FakeSecrets(clearskies.secrets.Secrets):
    """In-memory stand-in for a secret manager (tests / local development)."""

    values = {
        "/path/to/api-key": "<YOUR_API_KEY>",
        "/path/to/service-credentials": json.dumps({"credentials": {"api_key": "<SERVICE_KEY>"}}),
    }

    # SecretBearer calls get(path, refresh=..., json_path=..., kind=...), so accept them all
    def get(self, path, silent_if_not_found=False, refresh=False, json_path=None, kind=None):
        value = self.values.get(path)
        if value is None:
            if silent_if_not_found:
                return ""
            raise KeyError(f"Secret '{path}' not found")
        if json_path:
            for part in json_path.split("."):
                value = json.loads(value) if isinstance(value, str) else value
                value = value[part]
        return value


class ServiceClient(clearskies.di.InjectableProperties):
    # Property injection: resolved lazily from the `secrets` binding
    secrets = inject.Secrets()

    def api_key(self) -> str:
        return self.secrets.get("/path/to/service-credentials", json_path="credentials.api_key")


# Callable injection: an argument named `secrets` receives the bound secret manager
def show(secrets, service_client: ServiceClient):
    return {
        "direct": secrets.get("/path/to/api-key"),
        "via_class": service_client.api_key(),
    }


app = clearskies.contexts.Context(
    clearskies.endpoints.Callable(
        show,
        # Incoming requests must send the value stored at /path/to/api-key
        authentication=clearskies.authentication.SecretBearer(secret_key="/path/to/api-key"),
    ),
    classes=[ServiceClient],
    bindings={"secrets": FakeSecrets()},
)

print(app(request_headers={"Authorization": "<YOUR_API_KEY>"}))  # 200, success
print(app(request_headers={"Authorization": "wrong"}))  # 401, Not Authenticated
```

## Production: Akeyless

Requires the `akeyless` Python SDK to be installed.

```python
import clearskies
from clearskies.secrets.cache_storage import MemoryCache

secrets = clearskies.secrets.Akeyless(
    access_id="p-abc123",           # must match ^p-[0-9a-zA-Z]+$
    access_type="aws_iam",          # "aws_iam", "saml", or "jwt"
    # jwt_env_key="AKEYLESS_JWT",   # required when access_type="jwt"
    # auto_guess_type=True,         # call describe_secret to detect the secret kind
    cache_storage=MemoryCache(default_ttl=300),  # optional
)

# Static secret (default kind)
api_key = secrets.get("/path/to/api-key")

# Dynamic secret: pass kind= to skip describe_secret, json_path= to pick one field
db_password = secrets.get(
    "/path/to/db-credentials",
    kind="dynamic_secret",
    json_path="password",
)

# Bypass the cache
api_key = secrets.get("/path/to/api-key", refresh=True)

app = clearskies.contexts.WsgiRef(
    clearskies.endpoints.Callable(
        lambda: {"hello": "world"},
        authentication=clearskies.authentication.SecretBearer(secret_key="/path/to/api-key"),
    ),
    bindings={"secrets": secrets},
)
```

## SecretBearer with Dynamic / JSON Secrets (2.1.8+)

```python
import clearskies

# Outgoing API authentication with a short-lived dynamic secret stored as JSON
backend = clearskies.backends.ApiBackend(
    base_url="https://api.example.com",
    authentication=clearskies.authentication.SecretBearer(
        secret_key="/path/to/service-token",
        secret_kind="dynamic_secret",    # static_secret | dynamic_secret | rotated_secret
        json_path="credentials.token",   # dot-notation into the JSON value
        refresh=True,                    # re-fetch from the secret manager
        header_prefix="Bearer ",
    ),
)
```

`secret_kind`, `json_path`, and `refresh` are passed to `secrets.get()` and only apply
with `secret_key`, not `environment_key`. Calling `auth.headers(retry_auth=True)` clears
the cached value and re-fetches once (useful after a 401 from the remote API).

## Key Points

1. **Bind a real manager** - the default `secrets` dependency is the base
   `clearskies.secrets.Secrets`, which raises `NotImplementedError` on every call
2. **Inject, don't import** - take `secrets` as a callable argument or use `inject.Secrets()`
3. **Custom managers** - subclass `clearskies.secrets.Secrets` and accept
   `refresh`, `json_path`, and `kind` in `get()` if used with `SecretBearer`
4. **Rotation** - use `alternate_secret_key` on `SecretBearer` to accept old and new secrets
5. **Never hardcode or log secret values**
'''
