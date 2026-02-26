"""
Core concept explanations for clearskies framework.

This module contains explanations for the fundamental building blocks:
model, endpoint, backend, column, and context.
"""

import textwrap

CORE_CONCEPTS = {
    "model": textwrap.dedent("""\
        # clearskies Models

        A clearskies model represents your data schema and provides an interface for interacting with
        backend data stores. Every model needs four things:

        1. **id_column_name** - The name of the column that uniquely identifies each record
        2. **backend** - An object that handles data persistence (MemoryBackend, CursorBackend, ApiBackend, etc.)
        3. **destination_name** - Equivalent to a table name (auto-generated from class name by default)
        4. **columns** - Class attributes that extend `clearskies.Column`

        ## Inheritance

        Models inherit from `InjectableProperties` and `Loggable`:
        ```python
        class Model(Schema, InjectableProperties, Loggable):
            pass
        ```

        This means every model:
        - Can inject dependencies as class properties via `clearskies.di.inject.*`
        - Has `self.logger` available for logging

        ## Example

        ```python
        import clearskies
        from clearskies import columns
        from clearskies.di import inject

        class User(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            # Columns
            id = columns.Uuid()
            name = columns.String()
            email = columns.Email()
            age = columns.Integer()
            created_at = columns.Created()
            updated_at = columns.Updated()

            # Injectable properties (from InjectableProperties)
            email_service = inject.ByClass(EmailService)
            utcnow = inject.Utcnow()

            def send_welcome_email(self):
                self.email_service.send(self.email, "Welcome!")
                self.logger.info(f"Sent welcome email to {self.email}")  # From Loggable
        ```

        ## Key Methods
        - `model.save(data)` – Create or update a record
        - `model.create(data)` – Create a new record and return a new model instance
        - `model.delete()` – Delete a record
        - `model.where(condition)` – Query records with conditions
        - `model.find(condition)` – Find a single record
        - `model.sort_by(column, direction)` – Sort query results
        - `model.limit(n)` – Limit query results
        - `model.first()` – Get the first result from a query

        ## Save Lifecycle
        1. `pre_save` hooks (columns, then model)
        2. `to_backend` conversion
        3. Backend create/update
        4. `post_save` hooks (columns, then model)
        5. Model data updated
        6. `save_finished` hooks (columns, then model)

        ## Dependency Injection

        Models support property-based dependency injection via `clearskies.di.inject`:
        - `clearskies.di.inject.ByClass(SomeClass)` – Inject by class
        - `clearskies.di.inject.ByName("name")` – Inject by binding name
        - `clearskies.di.inject.Utcnow()` – Inject current UTC time
        - `clearskies.di.inject.Now()` – Inject current local time
        - `clearskies.di.inject.Environment()` – Inject environment helper
        - `clearskies.di.inject.Secrets()` – Inject secrets helper

        See the `injectable_properties` concept for more details.
    """),
    "endpoint": textwrap.dedent("""\
        # clearskies Endpoints

        Endpoints encapsulate common HTTP API behavior via declarative configuration rather than
        imperative code. Instead of writing controllers, you configure endpoints that handle input
        validation, query building, pagination, searching, etc.

        ## Inheritance

        Endpoints inherit from `Configurable` and `InjectableProperties`:
        ```python
        class Endpoint(End, Configurable, InjectableProperties):
            pass
        ```

        This means every endpoint:
        - Can be configured via `clearskies.configs.*` descriptors
        - Can inject dependencies as class properties via `clearskies.di.inject.*`

        ## Available Endpoint Types

        - **RestfulApi** – Full CRUD REST API with list, get, create, update, delete
        - **List** – List records with sorting, pagination, and simple search
        - **Get** – Get a single record by id
        - **Create** – Create a new record with validation
        - **Update** – Update an existing record
        - **Delete** – Delete a record
        - **SimpleSearch** – Search with simple query parameter conditions
        - **AdvancedSearch** – Search with complex conditions via POST body
        - **Callable** – Wrap a Python function as an endpoint
        - **Schema** – Return the schema/documentation for an endpoint
        - **HealthCheck** – A simple health check endpoint
        - **Mygrations** – Run database migrations

        ## Example

        ```python
        import clearskies

        wsgi = clearskies.contexts.WsgiRef(
            clearskies.endpoints.RestfulApi(
                url="users",
                model_class=User,
                readable_column_names=["id", "name", "email", "age"],
                writeable_column_names=["name", "email", "age"],
                sortable_column_names=["name", "age"],
                searchable_column_names=["name", "email"],
                default_sort_column_name="name",
            )
        )
        wsgi()
        ```

        ## Custom Endpoints with Configuration

        You can create custom endpoints using `Configurable` and `InjectableProperties`:

        ```python
        import clearskies
        from clearskies import configs
        from clearskies.di import inject

        class CustomEndpoint(clearskies.Endpoint):
            # Configuration (from Configurable)
            model_class = configs.Class(required=True)
            max_results = configs.Integer(default=100)

            # Injectable properties (from InjectableProperties)
            cache = inject.ByClass(CacheService)

            def handle(self, input_output):
                results = self.model_class.limit(self.max_results)
                return input_output.success({"data": list(results)})
        ```

        See the `configurable` and `injectable_properties` concepts for more details.
    """),
    "backend": textwrap.dedent("""\
        # clearskies Backends

        Backends provide a layer of abstraction between models and data storage. They normalize
        how you interact with databases, APIs, cloud resources, etc.

        ## Inheritance

        The base `Backend` class inherits from `Configurable` and `Loggable`:
        ```python
        class Backend(ABC, Configurable, Loggable):
            pass
        ```

        Concrete backend implementations also inherit from `InjectableProperties`:
        ```python
        class MemoryBackend(Backend, InjectableProperties):
            pass
        class CursorBackend(Backend, InjectableProperties):
            pass
        class ApiBackend(Backend, InjectableProperties):
            pass
        ```

        This means backends:
        - Can be configured via `clearskies.configs.*` descriptors
        - Have `self.logger` available for logging
        - Can inject dependencies as class properties (concrete implementations)

        ## Available Backends

        - **MemoryBackend** – Stores data in-memory (great for testing/prototyping)
        - **CursorBackend** – SQL databases (MySQL, PostgreSQL) via cursor objects
        - **ApiBackend** – REST API integration (your model becomes an API client)
        - **GraphqlBackend** – GraphQL API integration
        - **SecretsBackend** – Store data in a secrets manager

        ## Example

        ```python
        import clearskies

        # Memory backend (no external dependencies)
        class User(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()
            id = clearskies.columns.Uuid()
            name = clearskies.columns.String()

        # API backend (connects to a REST API)
        class RemoteUser(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.ApiBackend(
                base_url="https://api.example.com",
                authentication=clearskies.authentication.SecretBearer(
                    environment_key="API_SECRET"
                ),
            )
            id = clearskies.columns.String()
            name = clearskies.columns.String()
        ```

        See the `configurable`, `loggable`, and `injectable_properties` concepts for more details.
    """),
    "column": textwrap.dedent("""\
        # clearskies Columns

        Columns define the data schema for models. They provide type validation, serialization,
        and various lifecycle hooks.

        ## Inheritance

        The base `Column` class inherits from `Configurable`, `InjectableProperties`, and `Loggable`:
        ```python
        class Column(Configurable, InjectableProperties, Loggable):
            pass
        ```

        This means every column type:
        - Can be configured via `clearskies.configs.*` descriptors (column options)
        - Can inject dependencies as class properties via `clearskies.di.inject.*`
        - Has `self.logger` available for logging

        ## Basic Columns
        - **String** – Text data
        - **Integer** – Whole numbers
        - **Float** – Decimal numbers
        - **Boolean** – True/False values
        - **Uuid** – Auto-generated UUIDs
        - **Email** – Email addresses with validation
        - **Phone** – Phone numbers with validation
        - **Select** – Enumerated values
        - **Json** – JSON data
        - **Date** – Date values
        - **Datetime** – Date and time values
        - **Timestamp** – Unix timestamps

        ## Auto-populated Columns
        - **Created** – Auto-set on record creation
        - **Updated** – Auto-set on record update
        - **CreatedByIp** – Records the creator's IP
        - **CreatedByHeader** – Records a specific HTTP header
        - **CreatedByAuthorizationData** – Records authorization data
        - **CreatedByRoutingData** – Records routing data
        - **CreatedByUserAgent** – Records the user agent

        ## Relationship Columns
        - **BelongsToId** – Foreign key to a parent model
        - **BelongsToModel** – Auto-loads the parent model from a BelongsToId
        - **BelongsToSelf** – Self-referencing relationship
        - **HasMany** – One-to-many relationship
        - **HasManySelf** – Self-referencing one-to-many
        - **HasOne** – One-to-one relationship
        - **ManyToManyIds** – Many-to-many (returns ids)
        - **ManyToManyModels** – Many-to-many (returns models)
        - **ManyToManyIdsWithData** – Many-to-many with pivot data
        - **ManyToManyPivots** – Access to pivot table data

        ## Other Columns
        - **Audit** – Audit trail tracking
        - **CategoryTree** / **CategoryTreeAncestors** / **CategoryTreeChildren** / **CategoryTreeDescendants** – Hierarchical data

        ## Validators
        Columns support validators:
        ```python
        from clearskies.validators import Required, Unique

        name = columns.String(validators=[Required()])
        email = columns.Email(validators=[Required(), Unique()])
        ```

        See the `configurable`, `loggable`, and `injectable_properties` concepts for more details.
    """),
    "context": textwrap.dedent("""\
        # clearskies Contexts

        Contexts connect your clearskies application to the hosting environment. They abstract
        away how input is received and how responses are sent.

        ## Available Contexts

        - **Cli** – Run as a CLI command
        - **Wsgi** – Connect to any WSGI server (uWSGI, Gunicorn, etc.)
        - **WsgiRef** – Use Python's built-in WSGI server (for development/testing)

        ## Example: CLI

        ```python
        import clearskies

        def my_function():
            return "Hello World!"

        cli = clearskies.contexts.Cli(my_function)
        cli()
        ```

        ## Example: WSGI

        ```python
        import clearskies

        def hello_world():
            return "Hello World!"

        wsgi = clearskies.contexts.Wsgi(hello_world)

        def application(environment, start_response):
            return wsgi(environment, start_response)
        ```

        ## Dependency Injection via Contexts

        Contexts accept several parameters for configuring dependency injection:
        - `classes` – List of classes to register with the DI container
        - `modules` – List of modules to register
        - `bindings` – Dictionary of name → value bindings
    """),
}
