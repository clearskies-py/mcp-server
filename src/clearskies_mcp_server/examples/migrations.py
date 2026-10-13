"""
Example of clearskies database migrations using Mygrations.

This module demonstrates how to set up and run database migrations
with clearskies and the mygrations library.
"""

import textwrap


def example_migrations() -> str:
    """Complete example of clearskies database migrations."""
    return textwrap.dedent("""\
        # clearskies Database Migrations Example

        The `Mygrations` endpoint runs the [mygrations](https://github.com/cmancone/mygrations)
        library. Mygrations is stateless: you describe the desired schema as SQL `CREATE TABLE`
        statements, and it compares those files with the live database and plans/applies the
        difference. It does **not** read your clearskies models.

        ## Prerequisites

        ```bash
        pip install clear-skies mygrations
        ```

        ## Project Layout

        ```
        my_app/
        ├── database/
        │   ├── users.sql
        │   └── orders.sql
        ├── models.py
        └── mygrate.py
        ```

        ## 1. Schema Files (source of truth for the database)

        ```sql
        -- database/users.sql
        CREATE TABLE `users` (
          `id` CHAR(36) NOT NULL,
          `name` VARCHAR(255) NOT NULL DEFAULT '',
          `email` VARCHAR(255) NOT NULL DEFAULT '',
          `created_at` DATETIME NULL DEFAULT NULL,
          `updated_at` DATETIME NULL DEFAULT NULL,
          PRIMARY KEY (`id`),
          UNIQUE KEY `users_email` (`email`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ```

        ```sql
        -- database/orders.sql
        CREATE TABLE `orders` (
          `id` CHAR(36) NOT NULL,
          `user_id` CHAR(36) NOT NULL,
          `total` DECIMAL(10,2) NOT NULL DEFAULT 0,
          `status` VARCHAR(50) NOT NULL DEFAULT 'pending',
          `created_at` DATETIME NULL DEFAULT NULL,
          PRIMARY KEY (`id`),
          KEY `orders_user_id` (`user_id`),
          CONSTRAINT `orders_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        ```

        ## 2. Matching Models

        The models must be kept in sync with the SQL by hand: one column per field,
        with matching names and compatible types.

        ```python
        # models.py
        import clearskies
        from clearskies import columns


        class User(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            name = columns.String()
            email = columns.Email()
            created_at = columns.Created()
            updated_at = columns.Updated()


        class Order(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            user_id = columns.BelongsToId(User)
            total = columns.Float()
            status = columns.Select(["pending", "paid", "shipped"])
            created_at = columns.Created()
        ```

        ## 3. Migration Script

        ```python
        #!/usr/bin/env python
        # mygrate.py
        import clearskies

        cli = clearskies.contexts.Cli(
            clearskies.endpoints.Mygrations(
                allow_input=True,       # lets --command / --sql come from the CLI
                sql=["./database/"],    # SQL strings, .sql files, or directories
            )
        )

        if __name__ == "__main__":
            cli()
        ```

        With no `cursor` argument the endpoint uses the default `cursor` dependency,
        a MySQL cursor configured from environment variables:

        ```bash
        export DATABASE_HOST=localhost
        export DATABASE_USERNAME=app
        export DATABASE_PASSWORD=REPLACE_ME
        export DATABASE_NAME=myapp
        export DATABASE_PORT=3306   # optional
        ```

        You can also pass a cursor explicitly, e.g.
        `cursor=clearskies.cursors.from_environment.Mysql()`, or name a different
        DI binding with `cursor_dependency_name="..."`.

        ## 4. Running

        ```bash
        ./mygrate.py --command=check   # validate the SQL files
        ./mygrate.py --command=plan    # show the SQL needed to update the database
        ./mygrate.py --command=apply   # apply those changes
        ```

        Allowed commands: `version` (default), `check`, `plan`, `plan_export`, `apply`.
        Without `allow_input=True`, the command is fixed by the `command=` argument instead.

        ## Changing the Schema

        To add a column, edit both places:

        ```sql
        -- database/users.sql: add inside CREATE TABLE
          `phone` VARCHAR(20) NOT NULL DEFAULT '',
        ```

        ```python
        # models.py: add to User
            phone = columns.Phone()
        ```

        Then run `plan`, review the output, and run `apply`. Removing a column from the
        SQL file makes mygrations drop it, so always review the plan first.

        ## Migrations Shipped by Modules

        A module can ship its own SQL by subclassing `AdditionalMygrationsAutoImport`.
        By default the SQL folder is `sql/` next to the file defining the class:

        ```python
        # my_module/migrations.py
        from clearskies.di import AdditionalMygrationsAutoImport

        class MyModuleMigrations(AdditionalMygrationsAutoImport):
            pass  # or: sql = ["database"]
        ```

        Opt in on the endpoint (modules must be loaded via `add_modules()` / `modules=`):

        ```python
        clearskies.endpoints.Mygrations(
            sql=["./database/"],
            include_module_migrations=True,
            module_migrations=["MyModuleMigrations"],  # optional allow-list of class names
        )
        ```

        ## CI/CD

        ```yaml
        migrate:
          stage: deploy
          script:
            - ./mygrate.py --command=plan
            - ./mygrate.py --command=apply
        ```
    """)
