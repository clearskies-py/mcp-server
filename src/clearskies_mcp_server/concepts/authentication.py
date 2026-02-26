"""
Authentication concept explanations for clearskies framework.

This module contains explanations for authentication mechanisms.
"""

import textwrap

AUTH_CONCEPTS = {
    "authentication": textwrap.dedent("""\
        # clearskies Authentication

        clearskies provides authentication mechanisms that can be attached to endpoints.

        ## Available Authentication Types

        - **Public** – No authentication required
        - **SecretBearer** – Bearer token authentication using a secret
        - **Jwks** – JSON Web Key Set (JWKS) authentication

        ## Example: Secret Bearer

        ```python
        import clearskies

        wsgi = clearskies.contexts.WsgiRef(
            clearskies.endpoints.RestfulApi(
                url="users",
                model_class=User,
                authentication=clearskies.authentication.SecretBearer(
                    environment_key="MY_SECRET"
                ),
                readable_column_names=["id", "name"],
                writeable_column_names=["name"],
                default_sort_column_name="name",
            )
        )
        ```

        ## Example: JWKS Authentication

        ```python
        import clearskies

        wsgi = clearskies.contexts.WsgiRef(
            clearskies.endpoints.RestfulApi(
                url="users",
                model_class=User,
                authentication=clearskies.authentication.Jwks(
                    jwks_url="https://your-auth-provider.com/.well-known/jwks.json",
                    audience="your-api-audience",
                    issuer="https://your-auth-provider.com/",
                ),
                readable_column_names=["id", "name"],
                writeable_column_names=["name"],
                default_sort_column_name="name",
            )
        )
        ```

        ## Authorization Data

        Authentication handlers can provide authorization data that's accessible in your code:

        ```python
        def my_endpoint(authorization_data: dict):
            user_id = authorization_data.get("user_id")
            roles = authorization_data.get("roles", [])
            return {"user_id": user_id, "roles": roles}
        ```

        ## Custom Authentication

        You can create custom authentication by extending `clearskies.authentication.Authentication`
        and implementing the `authenticate` method:

        ```python
        import clearskies

        class CustomAuth(clearskies.authentication.Authentication):
            def authenticate(self, input_output):
                # Get the authorization header
                auth_header = input_output.get_header("Authorization")
                if not auth_header:
                    return self.error("Missing Authorization header", 401)

                # Validate the token
                token = auth_header.replace("Bearer ", "")
                user_data = validate_token(token)  # Your validation logic

                if not user_data:
                    return self.error("Invalid token", 401)

                # Return authorization data
                return {
                    "user_id": user_data["id"],
                    "roles": user_data["roles"],
                }
        ```

        ## Combining Authentication with Authorization

        Authentication verifies identity; authorization controls access:

        ```python
        class Order(clearskies.Model):
            def where_for_request(self, model, input_output, routing_data, authorization_data, overrides={}):
                # Only show orders belonging to the authenticated user
                user_id = authorization_data.get("user_id")
                return model.where(f"user_id={user_id}")
        ```

        ## Best Practices

        1. **Use environment variables for secrets** – Never hardcode tokens
        2. **Use JWKS for production** – More secure than shared secrets
        3. **Validate tokens on every request** – Don't cache authentication
        4. **Use HTTPS** – Always encrypt authentication headers
        5. **Implement proper error handling** – Return appropriate HTTP status codes
    """),
}
