"""
Example of clearskies database migrations using Mygrations.

This module demonstrates how to set up and run database migrations
with clearskies and the mygrations library.
"""

import textwrap


def example_migrations() -> str:
    """Complete example of clearskies database migrations."""
    return textwrap.dedent('''\
        # clearskies Database Migrations Example

        This example demonstrates how to use the Mygrations endpoint for database
        schema evolution in clearskies applications.

        ## Prerequisites

        ```bash
        pip install clear-skies mygrations
        ```

        ## Complete Migration Setup

        ```python
        """
        Database migrations example with clearskies and Mygrations.

        This script demonstrates:
        - Setting up models with CursorBackend
        - Configuring the Mygrations endpoint
        - Running migrations via CLI
        """
        import os
        import clearskies
        from clearskies import columns
        from clearskies.validators import Required, Unique


        # =============================================================================
        # MODEL DEFINITIONS
        # =============================================================================

        class User(clearskies.Model):
            """User model with common fields."""
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            email = columns.Email(max_length=255, validators=[Required(), Unique()])
            name = columns.String(max_length=255, validators=[Required()])
            status = columns.Select(["active", "inactive", "suspended"], default="active")
            created_at = columns.Created()
            updated_at = columns.Updated()


        class Post(clearskies.Model):
            """Blog post model with foreign key to User."""
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            user_id = columns.BelongsToId(parent_model_class=User)
            title = columns.String(max_length=255, validators=[Required()])
            content = columns.String()
            status = columns.Select(["draft", "published", "archived"], default="draft")
            published_at = columns.Datetime()
            created_at = columns.Created()
            updated_at = columns.Updated()


        class Comment(clearskies.Model):
            """Comment model with foreign keys to User and Post."""
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            post_id = columns.BelongsToId(parent_model_class=Post)
            user_id = columns.BelongsToId(parent_model_class=User)
            content = columns.String(validators=[Required()])
            created_at = columns.Created()


        # =============================================================================
        # MIGRATIONS ENDPOINT
        # =============================================================================

        # Create the migrations endpoint with all models
        migrations = clearskies.endpoints.Mygrations(
            models=[User, Post, Comment],
            connection_string_environment_key="DATABASE_URL",
        )

        # Create CLI context for running migrations
        cli = clearskies.contexts.Cli(migrations)


        if __name__ == "__main__":
            cli()
        ```

        ## Running Migrations

        ### Check Mode (Dry Run)

        See what changes would be applied without making them:

        ```bash
        # Set your database connection string
        export DATABASE_URL="mysql://user:password@localhost/myapp"

        # Check what migrations would be applied
        python migrations.py --check
        ```

        Example output:
        ```
        Checking migrations...

        Tables to create:
          - users
          - posts
          - comments

        Columns to add:
          - users.id (uuid, primary key)
          - users.email (varchar(255), unique)
          - users.name (varchar(255))
          - users.status (enum: active, inactive, suspended)
          - users.created_at (datetime)
          - users.updated_at (datetime)
          ...

        No destructive changes detected.
        Run with --apply to apply these changes.
        ```

        ### Apply Mode

        Apply the migrations to the database:

        ```bash
        python migrations.py --apply
        ```

        Example output:
        ```
        Applying migrations...

        Creating table: users
        Creating table: posts
        Creating table: comments

        Migrations applied successfully.
        ```

        ### Status Mode

        Check the current schema status:

        ```bash
        python migrations.py --status
        ```

        ## Schema Evolution Examples

        ### Adding a New Column

        Add a `phone` column to the User model:

        ```python
        class User(clearskies.Model):
            # ... existing columns ...
            phone = columns.Phone(max_length=20)  # New column
        ```

        Run migrations:
        ```bash
        python migrations.py --check   # Review changes
        python migrations.py --apply   # Apply changes
        ```

        ### Adding an Index

        Add an index to improve query performance:

        ```python
        class Post(clearskies.Model):
            # ... existing columns ...
            status = columns.Select(
                ["draft", "published", "archived"],
                default="draft",
                index=True,  # Add index
            )
        ```

        ### Changing Column Properties

        Increase the max_length of a column:

        ```python
        # Before
        title = columns.String(max_length=255)

        # After
        title = columns.String(max_length=500)
        ```

        ### Adding a New Table

        Simply add a new model class:

        ```python
        class Tag(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            name = columns.String(max_length=100, validators=[Required(), Unique()])
            created_at = columns.Created()

        # Update migrations endpoint
        migrations = clearskies.endpoints.Mygrations(
            models=[User, Post, Comment, Tag],  # Add Tag
            connection_string_environment_key="DATABASE_URL",
        )
        ```

        ## CI/CD Integration

        ### GitLab CI Example

        ```yaml
        # .gitlab-ci.yml
        stages:
          - test
          - migrate
          - deploy

        variables:
          DATABASE_URL: $CI_DATABASE_URL

        check-migrations:
          stage: test
          script:
            - pip install -r requirements.txt
            - python migrations.py --check
          only:
            - merge_requests

        apply-migrations:
          stage: migrate
          script:
            - pip install -r requirements.txt
            - python migrations.py --apply
          only:
            - main
          when: manual  # Require manual approval

        deploy:
          stage: deploy
          script:
            - ./deploy.sh
          only:
            - main
          needs:
            - apply-migrations
        ```

        ### GitHub Actions Example

        ```yaml
        # .github/workflows/migrate.yml
        name: Database Migrations

        on:
          push:
            branches: [main]
          pull_request:
            branches: [main]

        jobs:
          check:
            runs-on: ubuntu-latest
            steps:
              - uses: actions/checkout@v3
              - uses: actions/setup-python@v4
                with:
                  python-version: "3.11"
              - run: pip install -r requirements.txt
              - run: python migrations.py --check
                env:
                  DATABASE_URL: ${{ secrets.DATABASE_URL }}

          apply:
            runs-on: ubuntu-latest
            needs: check
            if: github.ref == \'refs/heads/main\'
            steps:
              - uses: actions/checkout@v3
              - uses: actions/setup-python@v4
                with:
                  python-version: "3.11"
              - run: pip install -r requirements.txt
              - run: python migrations.py --apply
                env:
                  DATABASE_URL: ${{ secrets.DATABASE_URL }}
        ```

        ## Best Practices

        1. **Always run --check first** - Review changes before applying
        2. **Backup before destructive changes** - Column removals, type changes
        3. **Use version control** - Track model changes in git
        4. **Test in staging first** - Before applying to production
        5. **Use manual approval in CI/CD** - For production migrations
        6. **Document breaking changes** - In commit messages and changelogs
    ''')
