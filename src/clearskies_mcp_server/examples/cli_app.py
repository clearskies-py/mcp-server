"""CLI application example for clearskies."""

import textwrap


def example_cli_app() -> str:
    """Return example of a clearskies CLI application."""
    return textwrap.dedent("""\
        # Example: CLI Application

        ```python
        #!/usr/bin/env python
        import clearskies
        from clearskies import columns

        class User(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            name = columns.String()
            email = columns.Email()

        def seed_users(users: User):
            users.create({"name": "Alice", "email": "alice@example.com"})
            users.create({"name": "Bob", "email": "bob@example.com"})
            return [{"id": u.id, "name": u.name, "email": u.email} for u in users.sort_by("name", "asc")]

        cli = clearskies.contexts.Cli(
            clearskies.endpoints.Callable(
                seed_users,
                model_class=User,
                return_records=True,
            ),
            classes=[User],
        )

        if __name__ == "__main__":
            cli()
        ```

        ## Usage

        ```bash
        python cli_app.py
        ```
    """)
