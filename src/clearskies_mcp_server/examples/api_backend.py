"""API backend example for clearskies."""

import textwrap


def example_api_backend() -> str:
    """Return example of using clearskies as an API client with ApiBackend."""
    return textwrap.dedent("""\
        # Example: Using ApiBackend as an API Client

        The ApiBackend lets you use clearskies models to interact with a REST API,
        turning your model into an SDK for that API.

        ```python
        import clearskies
        from clearskies import columns

        class RemoteUser(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.ApiBackend(
                base_url="https://api.example.com",
                authentication=clearskies.authentication.SecretBearer(
                    environment_key="API_TOKEN"
                ),
            )

            id = columns.String()
            name = columns.String()
            email = columns.String()

        def fetch_users(remote_users: RemoteUser):
            # Query the remote API using the model
            for user in remote_users.where("status=active"):
                print(f"{user.name}: {user.email}")

            # Create a new user via the API
            new_user = remote_users.create({"name": "New User", "email": "new@example.com"})

        cli = clearskies.contexts.Cli(
            clearskies.endpoints.Callable(fetch_users, model_class=RemoteUser),
            classes=[RemoteUser],
        )
        cli()
        ```
    """)
