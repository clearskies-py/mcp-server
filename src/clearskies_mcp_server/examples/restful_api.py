"""RESTful API example for clearskies."""

import textwrap


def example_restful_api() -> str:
    """Complete example of a clearskies RESTful API."""
    return textwrap.dedent("""\
        # Example: RESTful API with clearskies

        ```python
        import clearskies
        from clearskies import columns
        from clearskies.validators import Required, Unique

        class User(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            name = columns.String(validators=[Required()])
            username = columns.String(validators=[Required(), Unique()])
            email = columns.Email(validators=[Required()])
            age = columns.Integer(validators=[Required()])
            created_at = columns.Created()
            updated_at = columns.Updated()

        wsgi = clearskies.contexts.WsgiRef(
            clearskies.endpoints.RestfulApi(
                url="users",
                model_class=User,
                readable_column_names=["id", "name", "username", "email", "age", "created_at", "updated_at"],
                writeable_column_names=["name", "username", "email", "age"],
                sortable_column_names=["name", "username", "age", "created_at"],
                searchable_column_names=["name", "username", "email"],
                default_sort_column_name="name",
            ),
            classes=[User],
        )

        if __name__ == "__main__":
            wsgi()
        ```

        ## Usage

        ```bash
        # Create a user
        curl 'http://localhost:8080/users' -d '{"name": "Jane", "username": "jane_doe", "email": "jane@example.com", "age": 28}'

        # List users
        curl 'http://localhost:8080/users'

        # Search
        curl 'http://localhost:8080/users?name=Jane'

        # Get by id
        curl 'http://localhost:8080/users/<uuid>'

        # Update
        curl -X PUT 'http://localhost:8080/users/<uuid>' -d '{"age": 29}'

        # Delete
        curl -X DELETE 'http://localhost:8080/users/<uuid>'
        ```
    """)
