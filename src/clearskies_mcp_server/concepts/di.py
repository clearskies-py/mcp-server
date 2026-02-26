"""
Dependency Injection concept explanations for clearskies framework.

This module contains detailed explanations of the clearskies DI system.
"""

import textwrap

DI_CONCEPTS = {
    "di": textwrap.dedent("""\
        # clearskies Dependency Injection

        clearskies has a built-in dependency injection system that automatically resolves
        dependencies for your functions and classes.

        ## Two DI Patterns

        clearskies supports two complementary DI patterns:

        ### 1. Constructor Injection (Functions and Classes)

        Dependencies are resolved based on parameter names and type hints:

        ```python
        def my_endpoint(users: User, config: AppConfig):
            # users and config are automatically injected
            return users.where("status=active").limit(10)
        ```

        ### 2. Property Injection (InjectableProperties)

        Dependencies are declared as class properties using `clearskies.di.inject.*`:

        ```python
        class MyService(clearskies.di.InjectableProperties):
            users = clearskies.di.inject.ByName("users")
            utcnow = clearskies.di.inject.Utcnow()

            def get_active_users(self):
                return self.users.where("status=active")
        ```

        ## Model Injection

        Models are available in the DI container by:
        - **snake_case name**: `User` → `user`
        - **pluralized name**: `User` → `users`
        - **type hint**: `def my_func(users: User)`

        ## Injectable Properties

        Many clearskies components inherit from `InjectableProperties`, including:
        - Models
        - Endpoints
        - Backends (concrete implementations)
        - Columns
        - Authentication handlers

        This allows them to use property-based injection:

        ```python
        class User(clearskies.Model):
            utcnow = clearskies.di.inject.Utcnow()
            email_service = clearskies.di.inject.ByClass(EmailService)

            def send_welcome_email(self):
                self.email_service.send(self.email, "Welcome!")
        ```

        See the `injectable_properties` concept for detailed documentation.

        ## Registering Dependencies

        ```python
        cli = clearskies.contexts.Cli(
            my_function,
            classes=[User, Order],           # Register classes
            modules=[app.models],            # Register entire modules
            bindings={"api_key": "abc123"},   # Register values by name
        )
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

        ## Function Injection

        Functions receive dependencies automatically based on parameter names:

        ```python
        def my_endpoint(users: User, config: AppConfig):
            # users and config are automatically injected
            return users.where("status=active").limit(10)

        cli = clearskies.contexts.Cli(
            my_endpoint,
            classes=[User],
            bindings={"config": AppConfig()},
        )
        ```

        ## Service Classes

        Create service classes that receive dependencies:

        ```python
        class UserService:
            def __init__(self, users: User, email_service: EmailService):
                self.users = users
                self.email_service = email_service

            def create_user(self, data: dict):
                user = self.users.create(data)
                self.email_service.send_welcome(user.email)
                return user

        # Register the service
        cli = clearskies.contexts.Cli(
            my_endpoint,
            classes=[User, UserService, EmailService],
        )
        ```

        ## Scoped Dependencies

        Dependencies can be scoped to different lifetimes:
        - **Singleton** – One instance for the entire application
        - **Request** – New instance per request
        - **Transient** – New instance every time

        ## Best Practices

        1. **Use type hints** – Clearer code and better IDE support
        2. **Keep dependencies explicit** – Don't hide dependencies
        3. **Prefer constructor injection** – For classes
        4. **Use property injection** – For clearskies components (Models, Endpoints)
        5. **Use bindings for configuration** – Not hardcoded values
        6. **Register at the context level** – Keep DI configuration centralized

        ## Related Concepts

        - `injectable_properties` – Detailed documentation on property-based injection
        - `injectable` – Advanced: The abstract base class for inject types
        - `di_advanced` – Advanced DI patterns and techniques
    """),
}
