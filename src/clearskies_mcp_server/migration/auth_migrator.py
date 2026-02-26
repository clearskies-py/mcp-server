"""
Authentication migration from v1 to v2.

Handles conversion of v1 authentication configurations to v2 equivalents.
"""

import ast
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .models import AuthConfig


class AuthenticationParser:
    """Parse v1 authentication configurations."""

    def parse_auth_config(self, handler_config: dict[str, Any]) -> "AuthConfig":
        """
        Extract authentication configuration from handler_config.

        Args:
            handler_config: Dictionary of handler configuration

        Returns:
            AuthConfig object with detected settings
        """
        from .models import AuthConfig

        auth_config = AuthConfig()

        if "authentication" in handler_config:
            auth_class = handler_config["authentication"]
            if isinstance(auth_class, str):
                auth_config.auth_type = auth_class.split(".")[-1]
            # Extract additional config if available
            if "authentication_config" in handler_config:
                auth_config.config = handler_config["authentication_config"]

        return auth_config

    def parse_auth_from_code(self, code: str) -> "AuthConfig | None":
        """
        Parse authentication from code string.

        Args:
            code: Source code to analyze

        Returns:
            AuthConfig or None if no auth found
        """
        from .models import AuthConfig

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    for kw in node.keywords:
                        if kw.arg == "authentication":
                            auth_config = AuthConfig()
                            # Extract auth type
                            if isinstance(kw.value, ast.Attribute):
                                auth_config.auth_type = kw.value.attr
                            elif isinstance(kw.value, ast.Call):
                                if isinstance(kw.value.func, ast.Attribute):
                                    auth_config.auth_type = kw.value.func.attr
                                    # Extract config from call
                                    auth_config.config = self._extract_call_config(kw.value)
                            return auth_config
        except SyntaxError:
            pass

        return None

    def _extract_call_config(self, call_node: ast.Call) -> dict[str, Any]:
        """Extract configuration from authentication call."""
        config = {}
        for kw in call_node.keywords:
            if kw.arg:
                config[kw.arg] = self._extract_value(kw.value)
        return config

    def _extract_value(self, node: ast.AST) -> Any:
        """Extract value from AST node."""
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.List):
            return [self._extract_value(elt) for elt in node.elts]
        if isinstance(node, ast.Dict):
            return {
                self._extract_value(k): self._extract_value(v) for k, v in zip(node.keys, node.values) if k is not None
            }
        return None


class AuthenticationGenerator:
    """Generate v2 authentication configurations."""

    # Authentication type mappings
    AUTH_MAPPINGS = {
        "SecretBearer": "clearskies.authentication.SecretBearer",
        "SecretBasic": "clearskies.authentication.SecretBasic",
        "JWKS": "clearskies.authentication.JWKS",
        "JWT": "clearskies.authentication.JWT",
        "Public": "clearskies.authentication.Public",
        "OAuth2": "clearskies.authentication.OAuth2",
    }

    def generate_auth(self, auth_config: "AuthConfig") -> str:
        """
        Generate v2 authentication instantiation.

        Args:
            auth_config: Authentication configuration

        Returns:
            Generated authentication code
        """
        if not auth_config.auth_type:
            return "# TODO: Configure authentication"

        auth_type = auth_config.auth_type

        if auth_type == "SecretBearer":
            return self._generate_secret_bearer(auth_config)
        elif auth_type == "SecretBasic":
            return self._generate_secret_basic(auth_config)
        elif auth_type == "JWKS":
            return self._generate_jwks(auth_config)
        elif auth_type == "JWT":
            return self._generate_jwt(auth_config)
        elif auth_type == "Public":
            return "authentication=clearskies.authentication.Public()"
        elif auth_type == "OAuth2":
            return self._generate_oauth2(auth_config)
        else:
            return f"# TODO: Configure {auth_type} authentication"

    def _generate_secret_bearer(self, auth_config: "AuthConfig") -> str:
        """Generate SecretBearer authentication."""
        env_key = auth_config.config.get("environment_key", "API_SECRET")
        return f"""authentication=clearskies.authentication.SecretBearer(
        environment_key="{env_key}"
    )"""

    def _generate_secret_basic(self, auth_config: "AuthConfig") -> str:
        """Generate SecretBasic authentication."""
        username_key = auth_config.config.get("username_key", "API_USERNAME")
        password_key = auth_config.config.get("password_key", "API_PASSWORD")
        return f"""authentication=clearskies.authentication.SecretBasic(
        username_key="{username_key}",
        password_key="{password_key}"
    )"""

    def _generate_jwks(self, auth_config: "AuthConfig") -> str:
        """Generate JWKS authentication."""
        jwks_url = auth_config.config.get("jwks_url", "https://example.com/.well-known/jwks.json")
        audience = auth_config.config.get("audience", "your-audience")

        lines = [
            "authentication=clearskies.authentication.JWKS(",
            f'        jwks_url="{jwks_url}",',
            f'        audience="{audience}"',
        ]

        # Add optional parameters
        if "issuer" in auth_config.config:
            lines.append(f'        issuer="{auth_config.config["issuer"]}",')

        lines.append("    )")
        return "\n".join(lines)

    def _generate_jwt(self, auth_config: "AuthConfig") -> str:
        """Generate JWT authentication."""
        secret_key = auth_config.config.get("secret_key", "JWT_SECRET")
        algorithm = auth_config.config.get("algorithm", "HS256")

        return f"""authentication=clearskies.authentication.JWT(
        secret_key="{secret_key}",
        algorithm="{algorithm}"
    )"""

    def _generate_oauth2(self, auth_config: "AuthConfig") -> str:
        """Generate OAuth2 authentication."""
        return """authentication=clearskies.authentication.OAuth2(
        # TODO: Configure OAuth2 parameters
        client_id="your-client-id",
        client_secret="your-client-secret",
        authorization_url="https://provider.com/oauth/authorize",
        token_url="https://provider.com/oauth/token"
    )"""

    def generate_auth_imports(self, auth_type: str) -> list[str]:
        """
        Generate required imports for authentication type.

        Args:
            auth_type: Type of authentication

        Returns:
            List of import statements
        """
        if auth_type == "Public":
            return ["import clearskies"]

        if auth_type in self.AUTH_MAPPINGS:
            return ["import clearskies"]

        return ["import clearskies"]


class AuthMigrationHelper:
    """Helper for migrating authentication patterns."""

    def __init__(self):
        """Initialize helpers."""
        self.parser = AuthenticationParser()
        self.generator = AuthenticationGenerator()

    def migrate_auth(self, v1_config: dict[str, Any]) -> tuple[str, list[str]]:
        """
        Migrate authentication configuration from v1 to v2.

        Args:
            v1_config: V1 handler configuration

        Returns:
            Tuple of (generated auth code, required imports)
        """
        # Parse v1 auth config
        auth_config = self.parser.parse_auth_config(v1_config)

        # Generate v2 auth code
        auth_code = self.generator.generate_auth(auth_config)

        # Get required imports
        imports = self.generator.generate_auth_imports(auth_config.auth_type)

        return auth_code, imports

    def detect_decorator_auth(self, func_def: ast.FunctionDef) -> str | None:
        """
        Detect authentication from decorators like @secret_bearer.

        Args:
            func_def: Function definition with decorators

        Returns:
            Authentication type or None
        """
        for decorator in func_def.decorator_list:
            if isinstance(decorator, ast.Name):
                if decorator.id in ["secret_bearer", "public", "jwks"]:
                    return decorator.id
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    if decorator.func.id in ["secret_bearer", "public", "jwks"]:
                        return decorator.func.id

        return None

    def convert_decorator_to_param(self, decorator_auth: str) -> str:
        """
        Convert decorator-based auth to parameter-based auth.

        Args:
            decorator_auth: Authentication type from decorator

        Returns:
            Generated authentication parameter code
        """
        from .models import AuthConfig

        auth_config = AuthConfig(auth_type=decorator_auth.title().replace("_", ""))
        return self.generator.generate_auth(auth_config)
