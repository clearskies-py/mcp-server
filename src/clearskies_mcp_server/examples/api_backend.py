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

        ## Pluggable URL, pagination and count adapters

        URL building, pagination and counting are delegated to adapters from
        `clearskies.backends.adapters`. Each `ApiBackend` option accepts an adapter
        instance or a plain callable. If you leave it unset, clearskies looks up a DI
        dependency named by `url_adapter_dependency_name` / `pagination_adapter_dependency_name`
        / `count_adapter_dependency_name` (defaults: `url_adapter`, `pagination_adapter`,
        `count_adapter`). If there is no such dependency, it uses the built-in default.

        | Option | Base class | Built-ins (default first) |
        |--------|------------|---------------------------|
        | `url_adapter` | `UrlAdapter` | `UrlAdapter` (REST: `/users`, `/users/{id}`) |
        | `pagination_adapter` | `PaginationAdapter` | `LinkHeaderPaginationAdapter` (RFC 5988 `Link: rel="next"`), `ParameterPaginationAdapter` |
        | `count_adapter` | `CountAdapter` | `HeaderCountAdapter` (`X-Total-Count` / `X-Total` / `X-Total-Pages`), `BodyCountAdapter` |

        `can_count=True` (default `False`) makes `len(model)` / `bool(model)` send a `HEAD`
        request and read the count via the count adapter. It also adds `number_results`
        to endpoint pagination. With `can_count=False`, `len()` raises `NotImplementedError`.

        ```python
        from clearskies.backends import adapters

        # GitHub-style API: Link header pagination + X-Total-Count header
        github_style = clearskies.backends.ApiBackend(
            base_url="https://api.example.com",
            authentication=clearskies.authentication.SecretBearer(environment_key="API_TOKEN"),
            pagination_parameter_name="page",
            pagination_adapter=adapters.LinkHeaderPaginationAdapter(pagination_parameter_name="page"),
            count_adapter=adapters.HeaderCountAdapter(),
            can_count=True,
        )

        class V2UrlAdapter(adapters.UrlAdapter):
            def records_url(self, query):
                return (f"/api/v2/{query.model_class.destination_name()}", [])

        # Offset pagination (?offset=0, 50, 100...) with the total in the body: {"meta": {"total": 123}}
        offset_style = clearskies.backends.ApiBackend(
            base_url="https://api.example.com",
            pagination_parameter_name="offset",
            pagination_adapter=adapters.ParameterPaginationAdapter(
                pagination_parameter_name="offset", start_value=0, use_limit_as_step=True
            ),
            count_adapter=adapters.BodyCountAdapter(count_path="meta.total"),
            url_adapter=V2UrlAdapter(),
        )
        ```

        For custom behaviour, subclass and override: `PaginationAdapter.extract_next_page_data(response, query)`
        returns the next-page params as a dict (`{}` means there are no more pages).
        `CountAdapter.extract_count(response_data, response_headers, query=None)` returns
        `(total_count, total_pages)`. `UrlAdapter` methods such as `records_url(query)` and
        `create_url(data, model)` return `(url, used_routing_parameters)`. A callable
        `url_adapter` gets different arguments for each operation: records `(query)`, create
        `(data, model)`, update `(model, id, data)`, delete `(model, id)`. It returns a URL
        or `(url, used_routing_parameters)`, so prefer a subclass when you need more than one operation.

        Note (2.1.14+): boolean query parameters are sent as lowercase `true` / `false`,
        not as Python's `True` / `False`.
    """)
