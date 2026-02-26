"""Authentication example for clearskies."""

import textwrap


def example_authentication() -> str:
    """Return example of clearskies authentication."""
    return textwrap.dedent("""\
        # Example: Authenticated API

        ```python
        import os
        import clearskies
        from clearskies import columns
        from clearskies.validators import Required

        os.environ["MY_SECRET"] = "my-super-secret-token"

        class Widget(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            name = columns.String(validators=[Required()])
            category = columns.String()
            cost = columns.Float()
            created_at = columns.Created()
            updated_at = columns.Updated()

        wsgi = clearskies.contexts.WsgiRef(
            clearskies.endpoints.RestfulApi(
                url="widgets",
                model_class=Widget,
                authentication=clearskies.authentication.SecretBearer(
                    environment_key="MY_SECRET"
                ),
                readable_column_names=["id", "name", "category", "cost", "created_at", "updated_at"],
                writeable_column_names=["name", "category", "cost"],
                sortable_column_names=["name", "category", "cost"],
                searchable_column_names=["id", "name", "category", "cost"],
                default_sort_column_name="name",
            ),
            classes=[Widget],
        )

        if __name__ == "__main__":
            wsgi()
        ```

        ## Usage

        ```bash
        # Without auth (returns 401)
        curl 'http://localhost:8080/widgets'

        # With auth
        curl 'http://localhost:8080/widgets' -H 'Authorization: Bearer my-super-secret-token'
        ```
    """)
