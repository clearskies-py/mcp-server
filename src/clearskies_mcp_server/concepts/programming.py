"""
Programming paradigm concept explanations for clearskies framework.

This module contains explanations for declarative programming and infrastructure neutrality.
"""

import textwrap

PROGRAMMING_CONCEPTS = {
    "declarative_programming": textwrap.dedent("""\
        # Declarative Programming in clearskies

        clearskies uses declarative programming principles: you tell clearskies **what** you want
        rather than **how** to do it.

        ## Traditional Approach (Imperative)
        - Write controllers with input validation logic
        - Build queries manually with pagination
        - Handle error responses explicitly
        - Write serialization/deserialization code

        ## clearskies Approach (Declarative)
        - Declare your data schema via Model columns
        - Configure endpoints with what columns are readable/writeable/searchable/sortable
        - clearskies handles validation, queries, pagination, error responses automatically

        ## Example

        A full CRUD REST API with search, sort, pagination, and validation in ~20 lines:

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
            age = columns.Integer(validators=[Required()])
            created_at = columns.Created()
            updated_at = columns.Updated()

        wsgi = clearskies.contexts.WsgiRef(
            clearskies.endpoints.RestfulApi(
                url="users",
                model_class=User,
                readable_column_names=["id", "name", "username", "age", "created_at", "updated_at"],
                writeable_column_names=["name", "username", "age"],
                sortable_column_names=["name", "age"],
                searchable_column_names=["name", "username"],
                default_sort_column_name="name",
            )
        )
        wsgi()
        ```
    """),
    "infrastructure_neutral": textwrap.dedent("""\
        # Infrastructure Neutrality in clearskies

        clearskies separates your business logic from infrastructure concerns through two
        abstraction layers:

        1. **Contexts** – Abstract the hosting environment (CLI, WSGI, Lambda, etc.)
        2. **Backends** – Abstract the data storage (SQL, API, Memory, Secrets Manager, etc.)

        This means the same business logic can run:
        - As a CLI tool during development
        - Behind a WSGI server in production
        - In a serverless function
        - Using an in-memory backend for tests and a SQL backend in production

        ## Switching Contexts

        ```python
        # Development
        cli = clearskies.contexts.Cli(my_endpoint, classes=[User])
        cli()

        # Production
        wsgi = clearskies.contexts.Wsgi(my_endpoint, classes=[User])
        def application(env, start_response):
            return wsgi(env, start_response)
        ```

        ## Switching Backends

        Your model code stays the same – just change the backend attribute.
    """),
}
