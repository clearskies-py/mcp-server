"""
Base classes and mixins concept explanations for clearskies framework.

This module contains detailed explanations of the foundational base classes
and mixins that clearskies components inherit from: Injectable, InjectableProperties,
Configurable, and Loggable.
"""

import textwrap

BASE_CLASS_CONCEPTS = {
    "injectable_properties": textwrap.dedent("""\
        # InjectableProperties Mixin

        `clearskies.di.InjectableProperties` is a mixin class that enables property-based
        dependency injection. Instead of receiving dependencies through constructor arguments,
        you can declare them as class properties using `clearskies.di.inject.*` descriptors.

        ## Why Use InjectableProperties?

        This pattern is common in clearskies because it helps create easily reusable classes:
        - Configuration goes in the constructor (developer-controlled)
        - Dependencies are injected as properties (DI-controlled)

        This separation means you can directly instantiate a class with configuration,
        and the DI system will automatically provide the dependencies afterward.

        ## Which Components Use It?

        Many clearskies components inherit from `InjectableProperties`:
        - **Model** - All models can inject dependencies as properties
        - **Endpoint** - All endpoints can inject dependencies
        - **Column** - All column types can inject dependencies
        - **Backend** subclasses - MemoryBackend, CursorBackend, ApiBackend, GraphqlBackend
        - **Authentication** handlers - Jwks, SecretBearer
        - **Cursor** - Database cursor wrappers
        - **Environment** - Environment helper
        - **Secrets** - Secrets management
        - Some **Validators** - Timedelta, InTheFuture, InThePast

        ## How to Use It

        ### Pattern 1: Using clearskies.di.inject.* Descriptors

        ```python
        import clearskies
        from clearskies.di import InjectableProperties, inject

        class MyService(InjectableProperties):
            # Inject dependencies as class properties
            users = inject.ByName("users")           # Inject by binding name
            email_service = inject.ByClass(EmailService)  # Inject by class
            utcnow = inject.Utcnow()                 # Inject current UTC time
            now = inject.Now()                       # Inject current local time
            environment = inject.Environment()       # Inject environment helper
            di_container = inject.Di()              # Inject the DI container itself

            def get_active_users(self):
                return self.users.where("status=active")

            def send_notification(self, user_id: str):
                user = self.users.find(f"id={user_id}")
                if user.exists:
                    self.email_service.send(user.email, "Hello!")
        ```

        ### Pattern 2: Attaching Objects That Also Use InjectableProperties

        ```python
        import clearskies
        from clearskies.di import InjectableProperties, inject

        class DatabaseHelper(InjectableProperties):
            cursor = inject.Cursor()

            def execute(self, query: str):
                return self.cursor.execute(query)

        class MyService(InjectableProperties):
            # Attach another InjectableProperties object
            db = DatabaseHelper()

            def get_data(self):
                return self.db.execute("SELECT * FROM users")
        ```

        ### Combining with Configurable

        A common pattern is to combine `InjectableProperties` with `Configurable`:

        ```python
        import clearskies
        from clearskies import configs, decorators
        from clearskies.di import InjectableProperties, inject

        class ReusableService(clearskies.Configurable, InjectableProperties):
            # Configuration (set via constructor)
            batch_size = configs.Integer(default=100)
            max_retries = configs.Integer(default=3)

            # Dependencies (injected by DI)
            database = inject.ByName("database")
            logger = inject.Logger()

            @decorators.parameters_to_properties
            def __init__(self, batch_size: int = 100, max_retries: int = 3):
                self.finalize_and_validate_configuration()

            def process(self, items: list):
                # Use both config and injected dependencies
                for i in range(0, len(items), self.batch_size):
                    batch = items[i:i + self.batch_size]
                    self.database.insert_many(batch)
        ```

        ## Available Inject Types

        | Class | Description |
        |-------|-------------|
        | `inject.ByClass(SomeClass)` | Build and inject the specified class |
        | `inject.ByName("name")` | Inject the dependency registered with that name |
        | `inject.Cursor()` | Inject the database cursor |
        | `inject.Di()` | Inject the DI container itself |
        | `inject.Environment()` | Inject the Environment helper |
        | `inject.InputOutput()` | Inject the current request's InputOutput |
        | `inject.Now()` | Inject current local datetime |
        | `inject.Requests()` | Inject a requests.Session |
        | `inject.Utcnow()` | Inject current UTC datetime |
        | `inject.Logger()` | Inject a logger |
        | `inject.Secrets()` | Inject the secrets helper |
        | `inject.Uuid()` | Inject a UUID generator |

        ## Important Notes

        1. **Injectables are not available in `__init__`**: The DI system injects properties
           after object creation. Don't try to use injectable properties in your constructor.

        2. **Time values are not cached by default**: `Now()` and `Utcnow()` return the
           current time each time you access them, unless you set `cache=True`.

        3. **Class-level caching**: Injectable properties are resolved at the class level,
           not instance level. This is efficient but means all instances share the same
           injected dependencies.

        ## Error: "injectable hasn't been properly initialized"

        If you see this error, it means you're trying to use an injectable property
        before the DI system has initialized it. Common causes:
        - Using injectable properties in `__init__`
        - Creating objects outside the DI system

        Solution: Defer use of injectable properties until after object creation,
        or ensure objects are created through the DI container.
    """),
    "configurable": textwrap.dedent("""\
        # Configurable Mixin

        `clearskies.Configurable` is a mixin class that enables declarative configuration
        using descriptor-based config properties from the `clearskies.configs` module.

        ## Why Use Configurable?

        The `Configurable` pattern provides:
        - **Type validation** - Configs validate their values automatically
        - **Required/optional** - Mark configs as required or provide defaults
        - **Declarative** - Configuration schema is visible in the class definition
        - **Reusable** - Same class can be instantiated with different configurations

        ## Which Components Use It?

        Most clearskies components inherit from `Configurable`:
        - **Endpoint** and all endpoint subclasses
        - **EndpointGroup**
        - **Backend** base class and all backends
        - **Column** base class and all column types
        - **Authentication** base class and handlers
        - **InputOutput** base class and implementations
        - **Validator** base class and validators
        - **Cursor** base class and implementations
        - **Secrets** base class and implementations
        - **SecurityHeader**
        - **Environment**
        - **GraphqlClient**

        ## How to Use It

        ### Basic Usage

        ```python
        import clearskies
        from clearskies import configs, decorators

        class EmailService(clearskies.Configurable):
            # Declare configuration properties
            smtp_host = configs.String(required=True)
            smtp_port = configs.Integer(default=587)
            use_tls = configs.Boolean(default=True)
            timeout = configs.Float(default=30.0)

            @decorators.parameters_to_properties
            def __init__(self, smtp_host: str, smtp_port: int = 587,
                         use_tls: bool = True, timeout: float = 30.0):
                self.finalize_and_validate_configuration()

            def send(self, to: str, subject: str, body: str):
                # Access config values as properties
                print(f"Connecting to {self.smtp_host}:{self.smtp_port}")
                print(f"TLS: {self.use_tls}, Timeout: {self.timeout}")

        # Usage
        service = EmailService(smtp_host="smtp.example.com")
        service.send("user@example.com", "Hello", "World")
        ```

        ### Available Config Types

        | Config Class | Python Type | Description |
        |--------------|-------------|-------------|
        | `configs.String` | `str` | String values |
        | `configs.Integer` | `int` | Integer values with optional min/max |
        | `configs.Float` | `float` | Float values |
        | `configs.Boolean` | `bool` | Boolean values |
        | `configs.Path` | `pathlib.Path` | File system paths |
        | `configs.Timedelta` | `datetime.timedelta` | Time durations |
        | `configs.SecretCache` | varies | Secret cache storage |

        ### Config Options

        Each config type supports these common options:

        ```python
        class MyClass(clearskies.Configurable):
            # Required config - must be provided
            name = configs.String(required=True)

            # Optional with default
            retries = configs.Integer(default=3)

            # Integer with constraints
            port = configs.Integer(default=8080, minimum=1, maximum=65535)

            # String that can be empty
            description = configs.String(default="")
        ```

        ### The `finalize_and_validate_configuration()` Method

        This method must be called after setting config values (typically at the end
        of `__init__`). It:
        1. Sets default values for configs that weren't provided
        2. Validates that required configs have values
        3. Runs each config's validation logic

        ```python
        @decorators.parameters_to_properties
        def __init__(self, name: str, retries: int = 3):
            # Config values are set by the decorator
            self.finalize_and_validate_configuration()  # Validate them
        ```

        ### The `@parameters_to_properties` Decorator

        This decorator automatically maps constructor parameters to config properties:

        ```python
        from clearskies import decorators

        class MyClass(clearskies.Configurable):
            name = configs.String(required=True)
            age = configs.Integer(default=0)

            @decorators.parameters_to_properties
            def __init__(self, name: str, age: int = 0):
                # The decorator sets self.name and self.age from the parameters
                self.finalize_and_validate_configuration()
        ```

        Without the decorator, you'd need to manually set each config:

        ```python
        def __init__(self, name: str, age: int = 0):
            self.name = name
            self.age = age
            self.finalize_and_validate_configuration()
        ```

        ## Combining with Other Mixins

        `Configurable` is often combined with `InjectableProperties` and `Loggable`:

        ```python
        import clearskies
        from clearskies import configs, decorators
        from clearskies.di import InjectableProperties, inject

        class DataProcessor(
            clearskies.Configurable,
            InjectableProperties,
            clearskies.Loggable
        ):
            # Configuration
            batch_size = configs.Integer(default=100)
            max_retries = configs.Integer(default=3)

            # Dependencies
            database = inject.ByName("database")

            @decorators.parameters_to_properties
            def __init__(self, batch_size: int = 100, max_retries: int = 3):
                self.finalize_and_validate_configuration()

            def process(self, items: list):
                self.logger.info(f"Processing {len(items)} items")
                # Use self.batch_size, self.database, self.logger
        ```

        ## Error Handling

        ### "Missing required configuration property"

        ```python
        class MyClass(clearskies.Configurable):
            name = configs.String(required=True)

            @decorators.parameters_to_properties
            def __init__(self, name: str = None):  # Default is None
                self.finalize_and_validate_configuration()

        MyClass()  # Raises: Missing required configuration property 'name'
        ```

        ### Validation Errors

        Config types validate their values:

        ```python
        class MyClass(clearskies.Configurable):
            port = configs.Integer(minimum=1, maximum=65535)

            @decorators.parameters_to_properties
            def __init__(self, port: int):
                self.finalize_and_validate_configuration()

        MyClass(port=70000)  # Raises validation error: port exceeds maximum
        ```
    """),
    "loggable": textwrap.dedent("""\
        # Loggable Mixin

        `clearskies.Loggable` is a mixin class that automatically injects a Python logger
        into any class that extends it. The logger is named based on the module and class name.

        ## Why Use Loggable?

        - **Zero configuration** - Logger is automatically created when the class is defined
        - **Consistent naming** - Logger name follows `module.ClassName` pattern
        - **Standard logging** - Uses Python's built-in `logging` module

        ## Which Components Use It?

        Many clearskies components inherit from `Loggable`:
        - **Model** - All models have a logger
        - **Column** - All column types have a logger
        - **Backend** base class and all backends
        - **InputOutput** base class and implementations
        - **Query** and **QueryResult**
        - **Cursor** base class and implementations
        - **Secrets** base class and implementations
        - **SecretCache** base class and implementations
        - **Environment**
        - **GraphqlClient**
        - **PortForwarder** base class and implementations

        ## How to Use It

        ### Basic Usage

        ```python
        import clearskies

        class MyService(clearskies.Loggable):
            def process_data(self, data: dict):
                self.logger.info(f"Processing data: {data}")
                try:
                    # Process data
                    result = self._do_processing(data)
                    self.logger.debug(f"Processing complete: {result}")
                    return result
                except Exception as e:
                    self.logger.error(f"Failed to process data: {e}")
                    raise

            def _do_processing(self, data: dict):
                self.logger.debug("Starting internal processing")
                return {"processed": True}
        ```

        ### Logger Naming

        The logger is automatically named `module.ClassName`:

        ```python
        # In file: myapp/services/user_service.py

        import clearskies

        class UserService(clearskies.Loggable):
            def create_user(self, name: str):
                # Logger name is: myapp.services.user_service.UserService
                self.logger.info(f"Creating user: {name}")
        ```

        ### Log Levels

        Use standard Python logging levels:

        ```python
        class MyService(clearskies.Loggable):
            def example(self):
                self.logger.debug("Detailed debugging info")
                self.logger.info("General information")
                self.logger.warning("Warning message")
                self.logger.error("Error occurred")
                self.logger.critical("Critical failure")
        ```

        ### Configuring Logging

        Configure logging at the application level:

        ```python
        import logging

        # Basic configuration
        logging.basicConfig(level=logging.INFO)

        # Or more detailed
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Enable debug for specific clearskies components
        logging.getLogger('clearskies').setLevel(logging.DEBUG)

        # Enable debug for your app
        logging.getLogger('myapp').setLevel(logging.DEBUG)
        ```

        ## How It Works

        `Loggable` uses Python's `__init_subclass__` hook to inject the logger when
        the class is defined (not when it's instantiated):

        ```python
        class Loggable:
            logger: logging.Logger

            def __init_subclass__(cls, **kwargs):
                super().__init_subclass__(**kwargs)
                logger_name = f"{cls.__module__}.{cls.__name__}"
                cls.logger = logging.getLogger(logger_name)
        ```

        This means:
        - Logger is created once per class, not per instance
        - All instances of a class share the same logger
        - Logger is available immediately, even in `__init__`

        ## Combining with Other Mixins

        `Loggable` is often combined with `Configurable` and `InjectableProperties`:

        ```python
        import clearskies
        from clearskies import configs, decorators
        from clearskies.di import InjectableProperties, inject

        class DataProcessor(
            clearskies.Configurable,
            InjectableProperties,
            clearskies.Loggable
        ):
            batch_size = configs.Integer(default=100)
            database = inject.ByName("database")

            @decorators.parameters_to_properties
            def __init__(self, batch_size: int = 100):
                self.finalize_and_validate_configuration()
                self.logger.info(f"DataProcessor initialized with batch_size={batch_size}")

            def process(self, items: list):
                self.logger.info(f"Processing {len(items)} items in batches of {self.batch_size}")
                for i in range(0, len(items), self.batch_size):
                    batch = items[i:i + self.batch_size]
                    self.logger.debug(f"Processing batch {i // self.batch_size + 1}")
                    self.database.insert_many(batch)
                self.logger.info("Processing complete")
        ```

        ## Best Practices

        1. **Use appropriate log levels**:
           - `DEBUG` for detailed diagnostic info
           - `INFO` for general operational messages
           - `WARNING` for unexpected but handled situations
           - `ERROR` for errors that need attention
           - `CRITICAL` for severe failures

        2. **Include context in log messages**:
           ```python
           self.logger.info(f"Processing user {user_id} with status {status}")
           ```

        3. **Log at boundaries**:
           - Log when entering/exiting important methods
           - Log before/after external calls (APIs, databases)

        4. **Don't log sensitive data**:
           ```python
           # Bad
           self.logger.info(f"User password: {password}")

           # Good
           self.logger.info(f"User {user_id} authenticated successfully")
           ```
    """),
    "injectable": textwrap.dedent("""\
        # Injectable Abstract Base Class

        `clearskies.di.Injectable` is an abstract base class that all dependency injection
        descriptors extend. This is an advanced topic - most users will use the concrete
        inject types (`inject.ByClass`, `inject.Utcnow`, etc.) rather than extending this class.

        ## What Is It?

        `Injectable` is the foundation for clearskies' property-based dependency injection.
        It implements Python's descriptor protocol to enable this pattern:

        ```python
        class MyClass(InjectableProperties):
            utcnow = inject.Utcnow()  # This is an Injectable descriptor

            def get_time(self):
                return self.utcnow()  # Accessing the descriptor triggers __get__
        ```

        ## How It Works

        `Injectable` is an abstract class with:
        - `_di` attribute to store the DI container reference
        - `set_di(di)` method to receive the DI container
        - `initiated_guard(instance)` to check proper initialization
        - Abstract `__get__(instance, parent)` method for the descriptor protocol

        When you access an injectable property:
        1. Python calls `__get__` on the descriptor
        2. The descriptor uses `self._di` to resolve the dependency
        3. The resolved value is returned

        ## Built-in Injectable Types

        clearskies provides these injectable descriptors:

        | Class | Purpose |
        |-------|---------|
        | `inject.ByClass(cls)` | Build and return an instance of the class |
        | `inject.ByName(name)` | Return the dependency registered with that name |
        | `inject.Cursor()` | Return the database cursor |
        | `inject.Di()` | Return the DI container itself |
        | `inject.Environment()` | Return the Environment helper |
        | `inject.InputOutput()` | Return the current request's InputOutput |
        | `inject.Now()` | Return current local datetime |
        | `inject.Requests()` | Return a requests.Session |
        | `inject.Utcnow()` | Return current UTC datetime |
        | `inject.Logger()` | Return a logger |
        | `inject.Secrets()` | Return the secrets helper |
        | `inject.Uuid()` | Return a UUID generator |
        | `inject.AkeylessSDK()` | Return the Akeyless SDK |
        | `inject.Socket()` | Return a socket |
        | `inject.Subprocess()` | Return the subprocess module |
        | `inject.ByStandardLib(name)` | Return a standard library module |

        ## Creating Custom Injectables (Advanced)

        You can create custom injectable types by extending `Injectable`:

        ```python
        from clearskies.di.injectable import Injectable

        class MyCustomInjectable(Injectable):
            def __init__(self, some_config: str, cache: bool = True):
                self.some_config = some_config
                self.cache = cache
                self._cached_value = None

            def __get__(self, instance, parent):
                # Guard against uninitialized state
                self.initiated_guard(instance)

                # Return cached value if caching is enabled
                if self.cache and self._cached_value is not None:
                    return self._cached_value

                # Use self._di to resolve dependencies
                some_service = self._di.build(SomeService)
                result = some_service.get_value(self.some_config)

                if self.cache:
                    self._cached_value = result

                return result
        ```

        ## The Caching Pattern

        Most injectable types support a `cache` parameter:

        ```python
        class MyClass(InjectableProperties):
            # Cached (default) - same value returned each time
            service = inject.ByClass(MyService, cache=True)

            # Not cached - new value each time
            current_time = inject.Utcnow(cache=False)
        ```

        ## Error: "injectable hasn't been properly initialized"

        This error occurs when you try to use an injectable before the DI system
        has called `set_di()`. The `initiated_guard()` method checks for this.

        Common causes:
        1. Using injectable properties in `__init__`
        2. Creating objects outside the DI system
        3. Forgetting to include `InjectableProperties` as a parent class

        ## Relationship with InjectableProperties

        - `Injectable` is the **descriptor** (the property definition)
        - `InjectableProperties` is the **mixin** that enables injectable properties on a class

        ```python
        # Injectable = the descriptor type
        class Utcnow(Injectable):
            def __get__(self, instance, parent):
                # Return current UTC time
                ...

        # InjectableProperties = the mixin that enables using Injectable descriptors
        class MyClass(InjectableProperties):
            utcnow = inject.Utcnow()  # Use the Injectable descriptor
        ```

        The DI system:
        1. Finds classes that extend `InjectableProperties`
        2. Scans for `Injectable` descriptors on those classes
        3. Calls `set_di(di)` on each descriptor to provide the DI container
    """),
    "configs_module": textwrap.dedent("""\
        # The configs Module

        The `clearskies.configs` module provides descriptor classes for declarative
        configuration. These work with the `Configurable` mixin to enable type-safe,
        validated configuration properties.

        ## Available Config Types

        ### configs.String

        String configuration values:

        ```python
        from clearskies import configs

        class MyClass(clearskies.Configurable):
            name = configs.String(required=True)
            description = configs.String(default="")
        ```

        ### configs.Integer

        Integer values with optional min/max constraints:

        ```python
        class MyClass(clearskies.Configurable):
            port = configs.Integer(default=8080, minimum=1, maximum=65535)
            retries = configs.Integer(default=3, minimum=0)
            count = configs.Integer(required=True)
        ```

        ### configs.Float

        Floating-point values:

        ```python
        class MyClass(clearskies.Configurable):
            timeout = configs.Float(default=30.0)
            rate = configs.Float(required=True)
        ```

        ### configs.Boolean

        Boolean values:

        ```python
        class MyClass(clearskies.Configurable):
            enabled = configs.Boolean(default=True)
            debug = configs.Boolean(default=False)
        ```

        ### configs.Path

        File system paths (converted to `pathlib.Path`):

        ```python
        from clearskies import configs

        class MyClass(clearskies.Configurable):
            config_file = configs.Path(required=True)
            output_dir = configs.Path(default="./output")
        ```

        ### configs.Timedelta

        Time duration values:

        ```python
        from datetime import timedelta
        from clearskies import configs

        class MyClass(clearskies.Configurable):
            timeout = configs.Timedelta(default=timedelta(seconds=30))
            cache_ttl = configs.Timedelta(default=timedelta(hours=1))
        ```

        ### configs.SecretCache

        Secret cache storage configuration:

        ```python
        from clearskies import configs

        class MySecretsProvider(clearskies.Configurable):
            cache_storage = configs.SecretCache()
        ```

        ## Common Options

        All config types support these options:

        | Option | Type | Description |
        |--------|------|-------------|
        | `required` | `bool` | If True, value must be provided (default: False) |
        | `default` | varies | Default value if not provided |

        ## Usage Pattern

        ```python
        import clearskies
        from clearskies import configs, decorators

        class DatabaseConnection(clearskies.Configurable):
            host = configs.String(required=True)
            port = configs.Integer(default=5432, minimum=1, maximum=65535)
            database = configs.String(required=True)
            username = configs.String(required=True)
            password = configs.String(required=True)
            ssl = configs.Boolean(default=True)
            timeout = configs.Float(default=30.0)

            @decorators.parameters_to_properties
            def __init__(
                self,
                host: str,
                database: str,
                username: str,
                password: str,
                port: int = 5432,
                ssl: bool = True,
                timeout: float = 30.0
            ):
                self.finalize_and_validate_configuration()

            def connect(self):
                print(f"Connecting to {self.host}:{self.port}/{self.database}")
                print(f"SSL: {self.ssl}, Timeout: {self.timeout}s")

        # Usage
        db = DatabaseConnection(
            host="localhost",
            database="myapp",
            username="admin",
            password="secret"
        )
        db.connect()
        ```

        ## Validation

        Configs validate their values when `finalize_and_validate_configuration()` is called:

        ```python
        class MyClass(clearskies.Configurable):
            port = configs.Integer(minimum=1, maximum=65535)

            @decorators.parameters_to_properties
            def __init__(self, port: int):
                self.finalize_and_validate_configuration()

        # This raises a validation error
        MyClass(port=70000)  # Error: port exceeds maximum of 65535
        ```

        ## The @parameters_to_properties Decorator

        This decorator automatically maps constructor parameters to config properties:

        ```python
        from clearskies import decorators

        class MyClass(clearskies.Configurable):
            name = configs.String()
            age = configs.Integer()

            @decorators.parameters_to_properties
            def __init__(self, name: str, age: int):
                # Decorator automatically does:
                # self.name = name
                # self.age = age
                self.finalize_and_validate_configuration()
        ```

        ## Creating Custom Config Types (Advanced)

        You can create custom config types by extending `configs.Config`:

        ```python
        from clearskies.configs.config import Config

        class Email(Config):
            def finalize_and_validate_configuration(self, instance):
                super().finalize_and_validate_configuration(instance)
                value = instance._config.get(instance._descriptor_to_name(self))
                if value and "@" not in value:
                    raise ValueError(f"Invalid email: {value}")
        ```
    """),
    "component_inheritance": textwrap.dedent("""\
        # Component Inheritance Hierarchy

        Understanding which base classes clearskies components inherit from helps you
        understand their capabilities and how to extend them.

        ## Model

        ```python
        class Model(Schema, InjectableProperties, Loggable):
            pass
        ```

        **Capabilities**:
        - `InjectableProperties` → Can inject dependencies as properties
        - `Loggable` → Has `self.logger` available

        **Example**:
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

            # Injectable properties (from InjectableProperties)
            email_service = inject.ByClass(EmailService)
            utcnow = inject.Utcnow()

            def send_welcome_email(self):
                # Use injected dependency
                self.email_service.send(self.email, "Welcome!")
                # Use logger (from Loggable)
                self.logger.info(f"Sent welcome email to {self.email}")
        ```

        ## Endpoint

        ```python
        class Endpoint(End, Configurable, InjectableProperties):
            pass
        ```

        **Capabilities**:
        - `Configurable` → Can be configured via `configs.*` descriptors
        - `InjectableProperties` → Can inject dependencies as properties

        **Example**:
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
                # Use config and injected dependencies
                results = self.model_class.limit(self.max_results)
                return input_output.success({"data": list(results)})
        ```

        ## Backend

        ```python
        # Base class
        class Backend(ABC, Configurable, Loggable):
            pass

        # Concrete implementations add InjectableProperties
        class MemoryBackend(Backend, InjectableProperties):
            pass

        class CursorBackend(Backend, InjectableProperties):
            pass

        class ApiBackend(Backend, InjectableProperties):
            pass
        ```

        **Capabilities**:
        - `Configurable` → Can be configured via `configs.*` descriptors
        - `Loggable` → Has `self.logger` available
        - `InjectableProperties` (concrete backends) → Can inject dependencies

        ## Column

        ```python
        class Column(Configurable, InjectableProperties, Loggable):
            pass
        ```

        **Capabilities**:
        - `Configurable` → Column options are configs
        - `InjectableProperties` → Can inject dependencies
        - `Loggable` → Has `self.logger` available

        All column types (String, Integer, BelongsToId, etc.) inherit these capabilities.

        ## Authentication

        ```python
        # Base class
        class Authentication(Configurable, requests.auth.AuthBase):
            pass

        # Concrete implementations add InjectableProperties
        class SecretBearer(Authentication, InjectableProperties):
            pass

        class Jwks(Authentication, InjectableProperties):
            pass
        ```

        **Capabilities**:
        - `Configurable` → Auth handlers can be configured
        - `InjectableProperties` (concrete handlers) → Can inject dependencies

        ## Validator

        ```python
        class Validator(ABC, Configurable):
            pass
        ```

        **Capabilities**:
        - `Configurable` → Validators can have configuration options

        Some validators also extend `InjectableProperties`:
        ```python
        class InTheFuture(Validator, InjectableProperties):
            utcnow = inject.Utcnow()
        ```

        ## InputOutput

        ```python
        class InputOutput(ABC, Configurable, Loggable):
            pass
        ```

        **Capabilities**:
        - `Configurable` → Can be configured
        - `Loggable` → Has `self.logger` available

        ## Summary Table

        | Component | Configurable | InjectableProperties | Loggable |
        |-----------|--------------|---------------------|----------|
        | Model | ❌ | ✅ | ✅ |
        | Endpoint | ✅ | ✅ | ❌ |
        | Backend (base) | ✅ | ❌ | ✅ |
        | Backend (concrete) | ✅ | ✅ | ✅ |
        | Column | ✅ | ✅ | ✅ |
        | Authentication (base) | ✅ | ❌ | ❌ |
        | Authentication (concrete) | ✅ | ✅ | ❌ |
        | Validator | ✅ | varies | ❌ |
        | InputOutput | ✅ | ❌ | ✅ |
        | Query | ❌ | ❌ | ✅ |
        | Cursor | ✅ | ✅ | ✅ |
        | Secrets | ✅ | ✅ | ✅ |
        | Environment | ✅ | ✅ | ✅ |
    """),
}
