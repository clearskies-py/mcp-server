"""
Framework internals concept explanations for clearskies.

This module contains detailed explanations of clearskies internal mechanisms:
DI advanced patterns, query execution, model lifecycle, and input/output system.
"""

import textwrap

INTERNALS_CONCEPTS = {
    "di_advanced": textwrap.dedent("""\
        # Advanced Dependency Injection Patterns in clearskies

        This guide covers advanced DI patterns beyond the basics, including scoping,
        resolution order, circular dependencies, custom inject types, and testing.

        ## DI Resolution Order

        When clearskies resolves a dependency, it follows this order:

        1. **Explicit bindings** - Values registered via `bindings={...}`
        2. **Class registration** - Classes registered via `classes=[...]`
        3. **Module scanning** - Classes from modules registered via `modules=[...]`
        4. **Type hints** - Resolution by type annotation
        5. **Parameter name** - Resolution by parameter name (snake_case)

        ```python
        # Resolution example
        def my_function(users, email_service: EmailService, config):
            # 'users' - resolved by name (looks for 'users' binding or User model)
            # 'email_service' - resolved by type hint (EmailService class)
            # 'config' - resolved by name (looks for 'config' binding)
            pass

        cli = clearskies.contexts.Cli(
            my_function,
            classes=[User, EmailService],
            bindings={"config": {"api_key": "..."}},
        )
        ```

        ## Dependency Scoping

        clearskies supports different dependency lifetimes:

        ### Singleton Scope (Default for most classes)

        One instance shared across the entire application:

        ```python
        class DatabasePool:
            def __init__(self):
                self.connections = []

        # Same instance used everywhere
        cli = clearskies.contexts.Cli(
            my_function,
            classes=[DatabasePool],  # Singleton by default
        )
        ```

        ### Request Scope

        New instance per request (for web contexts):

        ```python
        class RequestContext:
            def __init__(self, input_output):
                self.user_id = input_output.request_headers.get("X-User-ID")

        # Each request gets a fresh RequestContext
        wsgi = clearskies.contexts.WsgiRef(
            my_endpoint,
            classes=[RequestContext],
        )
        ```

        ### Transient Scope

        New instance every time it's requested:

        ```python
        # Using factory functions for transient dependencies
        def create_uuid():
            return str(uuid.uuid4())

        cli = clearskies.contexts.Cli(
            my_function,
            bindings={"request_id": create_uuid},  # Factory called each time
        )
        ```

        ## Factory Functions

        Use factory functions for complex initialization:

        ```python
        def create_database_connection():
            return pymysql.connect(
                host=os.environ["DB_HOST"],
                user=os.environ["DB_USER"],
                password=os.environ["DB_PASSWORD"],
                database=os.environ["DB_NAME"],
            )

        def create_cursor(connection):
            return connection.cursor()

        cli = clearskies.contexts.Cli(
            my_function,
            bindings={
                "connection": create_database_connection,
                "cursor": create_cursor,
            },
        )
        ```

        ## Circular Dependency Detection

        clearskies detects circular dependencies at resolution time:

        ```python
        # ❌ Circular dependency - will raise error
        class ServiceA:
            def __init__(self, service_b: "ServiceB"):
                self.service_b = service_b

        class ServiceB:
            def __init__(self, service_a: ServiceA):
                self.service_a = service_a

        # Error: Circular dependency detected: ServiceA -> ServiceB -> ServiceA
        ```

        ### Breaking Circular Dependencies

        ```python
        # ✅ Solution 1: Use lazy loading
        class ServiceA:
            def __init__(self, di_container):
                self._di = di_container
                self._service_b = None

            @property
            def service_b(self):
                if self._service_b is None:
                    self._service_b = self._di.build(ServiceB)
                return self._service_b

        # ✅ Solution 2: Restructure to remove cycle
        class ServiceA:
            def __init__(self, shared_data: SharedData):
                self.shared_data = shared_data

        class ServiceB:
            def __init__(self, shared_data: SharedData):
                self.shared_data = shared_data
        ```

        ## Custom Inject Types

        clearskies provides several built-in inject types:

        ### ByClass

        Inject by class type:

        ```python
        class User(clearskies.Model):
            email_service = clearskies.di.inject.ByClass(EmailService)

            def send_welcome_email(self):
                self.email_service.send(self.email, "Welcome!")
        ```

        ### ByName

        Inject by binding name:

        ```python
        class User(clearskies.Model):
            api_key = clearskies.di.inject.ByName("api_key")

            def call_external_api(self):
                headers = {"Authorization": f"Bearer {self.api_key}"}
                # ...
        ```

        ### Utcnow

        Inject current UTC datetime:

        ```python
        class User(clearskies.Model):
            utcnow = clearskies.di.inject.Utcnow()

            def is_expired(self):
                return self.expires_at < self.utcnow()
        ```

        ## Testing with DI

        ### Mocking Dependencies

        ```python
        import pytest
        from unittest.mock import Mock

        class MockEmailService:
            def __init__(self):
                self.sent_emails = []

            def send(self, to, subject, body):
                self.sent_emails.append({"to": to, "subject": subject, "body": body})

        def test_user_registration():
            mock_email = MockEmailService()

            cli = clearskies.contexts.Cli(
                register_user,
                classes=[User],
                bindings={"email_service": mock_email},
            )

            result = cli.run({"name": "Alice", "email": "alice@example.com"})

            assert len(mock_email.sent_emails) == 1
            assert mock_email.sent_emails[0]["to"] == "alice@example.com"
        ```

        ### Overriding Dependencies

        ```python
        def test_with_test_database():
            # Use in-memory database for testing
            test_backend = clearskies.backends.MemoryBackend()

            class TestUser(User):
                backend = test_backend

            cli = clearskies.contexts.Cli(
                my_function,
                classes=[TestUser],  # Override User with TestUser
            )
        ```

        ## DI Container Introspection

        Debug what's registered in the container:

        ```python
        def debug_di(di_container):
            # List all registered bindings
            print("Bindings:", di_container.bindings.keys())

            # Check if a class is registered
            if di_container.has("users"):
                print("Users model is registered")

            # Get a dependency
            users = di_container.build(User)
        ```

        ## Model Injection Patterns

        Models are automatically available in DI:

        ```python
        class User(clearskies.Model):
            # ...
            pass

        # Available as:
        # - 'user' (singular, snake_case)
        # - 'users' (plural, snake_case)
        # - User (by type hint)

        def my_function(users, user: User):
            # 'users' is the model class for querying
            # 'user' is also the model class (same instance)
            all_users = users.where("status=active")
        ```

        ## Performance Considerations

        ### When DI Resolution Occurs

        - **At context creation**: Classes and modules are scanned
        - **At first request**: Dependencies are resolved lazily
        - **Per request**: Request-scoped dependencies are created

        ### Optimizing DI

        ```python
        # ✅ Good - register only needed classes
        cli = clearskies.contexts.Cli(
            my_function,
            classes=[User, Order],  # Only what's needed
        )

        # ❌ Avoid - registering entire modules with many unused classes
        import app.models  # Contains 50 models
        cli = clearskies.contexts.Cli(
            my_function,
            modules=[app.models],  # All 50 models scanned
        )
        ```

        ## Best Practices

        1. **Prefer constructor injection**: Clearer dependencies
        2. **Use type hints**: Better IDE support and clarity
        3. **Keep dependency graphs shallow**: Avoid deep nesting
        4. **Use factories for complex setup**: Don't put logic in constructors
        5. **Test with mocks**: Override dependencies in tests
        6. **Avoid circular dependencies**: Restructure if needed
        7. **Register at context level**: Centralize DI configuration
    """),
    "query_execution": textwrap.dedent("""\
        # Query Execution Model in clearskies

        Understanding how clearskies executes queries is essential for writing
        efficient code and avoiding performance pitfalls.

        ## Lazy Evaluation

        Queries in clearskies are lazily evaluated - they don't execute until
        you actually need the data:

        ```python
        # No query executed yet - just building the query
        query = users.where("status=active").sort_by("name", "asc").limit(10)

        # Query executes when you iterate
        for user in query:
            print(user.name)

        # Or when you call methods that need data
        first_user = query.first()  # Executes query
        count = len(query)          # Executes COUNT query
        all_users = list(query)     # Executes query and loads all
        ```

        ## Query Building

        Each query method returns a new query object:

        ```python
        # Each call creates a new query object
        q1 = users.where("status=active")
        q2 = q1.where("age>=18")
        q3 = q2.sort_by("name", "asc")

        # q1, q2, q3 are different query objects
        # Original query is not modified
        ```

        ## When Queries Execute

        Queries execute when you:

        1. **Iterate** over results
        2. **Call `.first()`** to get one record
        3. **Call `len()`** to count records
        4. **Call `list()`** to convert to list
        5. **Access a record attribute** (for single record queries)

        ```python
        # These trigger query execution:
        for user in users.where("status=active"):  # Iteration
            pass

        user = users.find("email=test@example.com")  # .find() calls .first()

        count = len(users.where("status=active"))  # COUNT query

        all_users = list(users.where("status=active"))  # List conversion
        ```

        ## Result Iteration

        ### Streaming Results

        By default, results are streamed from the database:

        ```python
        # Memory-efficient - one record at a time
        for user in users.where("status=active"):
            process_user(user)
            # Previous user can be garbage collected
        ```

        ### Loading All Results

        Converting to a list loads all records into memory:

        ```python
        # Loads all records into memory
        all_users = list(users.where("status=active"))

        # Be careful with large result sets!
        # This could use a lot of memory
        ```

        ### Batch Processing

        For large datasets, process in batches:

        ```python
        batch_size = 100
        offset = 0

        while True:
            batch = list(
                users.where("status=active")
                .sort_by("id", "asc")
                .limit(batch_size)
                .pagination(start=offset)
            )

            if not batch:
                break

            for user in batch:
                process_user(user)

            offset += batch_size
        ```

        ## Query Caching

        clearskies does NOT cache query results by default:

        ```python
        # Each iteration executes a new query
        query = users.where("status=active")

        for user in query:  # Query 1
            pass

        for user in query:  # Query 2 (same SQL, new execution)
            pass
        ```

        ### Manual Caching

        Cache results yourself when needed:

        ```python
        # Cache results in a list
        active_users = list(users.where("status=active"))

        # Reuse cached results
        for user in active_users:
            pass

        for user in active_users:
            pass
        ```

        ## N+1 Query Problem

        A common performance issue:

        ```python
        # ❌ N+1 queries - one query per order
        orders = list(orders_model.where("status=pending"))
        for order in orders:
            # Each access to order.user triggers a query
            print(f"Order {order.id} by {order.user.name}")

        # ✅ Better - load users upfront
        orders = list(orders_model.where("status=pending"))
        user_ids = [order.user_id for order in orders]
        users_by_id = {
            user.id: user
            for user in users_model.where(f"id in {','.join(user_ids)}")
        }
        for order in orders:
            user = users_by_id.get(order.user_id)
            print(f"Order {order.id} by {user.name if user else 'Unknown'}")
        ```

        ## Query Cloning

        Queries are immutable - each method returns a new query:

        ```python
        base_query = users.where("status=active")

        # Create variations without modifying base
        admins = base_query.where("role=admin")
        recent = base_query.sort_by("created_at", "desc").limit(10)

        # base_query is unchanged
        ```

        ## Count Queries

        `len(query)` executes a separate COUNT query:

        ```python
        # Executes: SELECT COUNT(*) FROM users WHERE status = 'active'
        count = len(users.where("status=active"))

        # More efficient than:
        count = len(list(users.where("status=active")))  # Loads all records!
        ```

        ## Exists Check

        Check if records exist without loading them:

        ```python
        # Efficient existence check
        query = users.where("email=test@example.com")
        user = query.first()
        if user:  # models are truthy when they hold a record
            print("User found")
        else:
            print("User not found")
        ```

        ## Query Debugging

        Enable logging to see generated SQL:

        ```python
        import logging
        logging.getLogger('clearskies').setLevel(logging.DEBUG)

        # Now queries will be logged
        users.where("status=active").first()
        # DEBUG: SELECT * FROM users WHERE status = 'active' LIMIT 1
        ```

        ## Performance Tips

        1. **Use `.limit()`**: Don't load more than needed
        2. **Use `len(query)` for counting**: Don't load records just to count
        3. **Avoid N+1**: Load related data in bulk
        4. **Cache when appropriate**: Store results you'll reuse
        5. **Use pagination**: For large result sets
        6. **Index filtered columns**: In your database schema
        7. **Stream large results**: Don't convert to list unnecessarily
    """),
    "model_lifecycle": textwrap.dedent("""\
        # Model Lifecycle in clearskies

        Understanding the model lifecycle helps you use clearskies correctly
        and avoid common pitfalls.

        ## Model vs Model Instance

        In clearskies, there's an important distinction:

        ```python
        class User(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()
            id = columns.Uuid()
            name = columns.String()

        # Model class - used for queries
        User  # The class itself

        # Model instance - represents a record
        user = User()  # Empty instance (no data)
        user = users.create({"name": "Alice"})  # Instance with data
        ```

        ## Model Instantiation

        ### Empty Model (Query Interface)

        ```python
        # Create an empty model instance for querying
        users = User()

        # This instance is used to build queries
        active_users = users.where("status=active")
        user = users.find("id=123")
        ```

        ### Model with Data (Record)

        ```python
        # Create a new record
        user = users.create({"name": "Alice", "email": "alice@example.com"})

        # user now has data
        print(user.name)  # "Alice"
        print(user.id)    # Generated UUID
        print(bool(user))  # True
        ```

        ### Model from Query

        ```python
        # Find returns a model instance
        user = users.find("email=alice@example.com")

        if user:
            print(user.name)
        else:
            print("Not found")
        ```

        ## Model States

        A model instance can be in different states:

        ### New (Unsaved)

        ```python
        user = User()
        user.name = "Alice"
        # bool(user) is False
        # user.id is None (or empty)
        ```

        ### Persisted (Saved)

        ```python
        user = users.create({"name": "Alice"})
        # bool(user) is True
        # user.id has a value
        ```

        ### Not Found

        ```python
        user = users.find("id=nonexistent")
        # bool(user) is False
        # Accessing user.name would return None/default
        ```

        ### Deleted

        ```python
        user = users.find("id=123")
        user.delete()
        # user still has data in memory
        # but it's no longer in the database
        ```

        ## Save Lifecycle (Detailed)

        When you call `.save()` or `.create()`:

        ### 1. Pre-Save Phase

        ```python
        # Column pre_save hooks run first
        # - Uuid columns generate IDs
        # - Created columns set timestamps
        # - Validators run

        # Then model pre_save hook
        class User(clearskies.Model):
            def pre_save(self, data):
                # Modify data before save
                if "email" in data:
                    data["email"] = data["email"].lower()
                return data
        ```

        ### 2. Backend Operation

        ```python
        # Data is converted for the backend
        # INSERT or UPDATE is executed
        ```

        ### 3. Post-Save Phase

        ```python
        # Column post_save hooks run
        # Then model post_save hook
        class User(clearskies.Model):
            def post_save(self, data, was_created):
                if was_created:
                    # Send welcome email
                    self.email_service.send_welcome(self.email)
        ```

        ### 4. Save Finished Phase

        ```python
        # Final cleanup
        # Model data is refreshed from backend
        class User(clearskies.Model):
            def save_finished(self, data, was_created):
                # Log the save
                self.logger.info(f"User saved: {self.id}")
        ```

        ## Data Refresh

        After save, the model is refreshed:

        ```python
        user = users.create({"name": "Alice"})

        # After create, user has:
        # - Generated ID
        # - Created timestamp
        # - Any default values from the database
        ```

        ## Model Cloning

        Models are not automatically cloned:

        ```python
        user1 = users.find("id=123")
        user2 = user1  # Same instance!

        user2.save({"name": "Bob"})
        print(user1.name)  # "Bob" - same object!
        ```

        ## Memory Management

        ### Query Results

        ```python
        # Streaming - memory efficient
        for user in users.where("status=active"):
            process(user)
            # user can be garbage collected after each iteration

        # List - all in memory
        all_users = list(users.where("status=active"))
        # All users held in memory until list is garbage collected
        ```

        ### Large Datasets

        ```python
        # ❌ Bad - loads all into memory
        all_users = list(users)
        for user in all_users:
            process(user)

        # ✅ Good - streams results
        for user in users:
            process(user)
        ```

        ## Model Destruction

        Python's garbage collector handles model cleanup:

        ```python
        def process_user():
            user = users.find("id=123")
            # ... use user ...
            return user.name
            # user is garbage collected after function returns
        ```

        ## Common Patterns

        ### Factory Pattern

        ```python
        class UserFactory:
            def __init__(self, users: User):
                self.users = users

            def create_admin(self, name, email):
                return self.users.create({
                    "name": name,
                    "email": email,
                    "role": "admin",
                })

            def create_guest(self, name):
                return self.users.create({
                    "name": name,
                    "role": "guest",
                })
        ```

        ### Repository Pattern

        ```python
        class UserRepository:
            def __init__(self, users: User):
                self.users = users

            def find_by_email(self, email):
                return self.users.find(f"email={email}")

            def find_active(self):
                return self.users.where("status=active")

            def find_admins(self):
                return self.users.where("role=admin")
        ```

        ## Best Practices

        1. **Use empty models for queries**: `users = User()`
        2. **Check truthiness after find** (`if user:`): Don't assume record exists
        3. **Don't hold references unnecessarily**: Let GC clean up
        4. **Use streaming for large datasets**: Avoid `list()` when possible
        5. **Understand save lifecycle**: Use hooks appropriately
        6. **Be aware of shared references**: Models aren't cloned
    """),
    "input_output": textwrap.dedent("""\
        # Input/Output System in clearskies

        The input/output system handles request parsing, response building,
        and data flow through endpoints.

        ## InputOutput Object

        Every request is wrapped in an `InputOutput` object. Callables can ask for
        it (`input_output`) or, more commonly, for the individual pieces by name:
        `request_data`, `query_parameters`, `routing_data`, `request_headers`,
        `authorization_data`.

        ```python
        def my_endpoint(request_data, query_parameters, request_headers):
            name = request_data.get("name")              # parsed JSON body
            search = query_parameters.get("search")
            auth = request_headers.get("Authorization")  # case-insensitive
            return {"message": "Hello"}
        ```

        ## Request Data Access

        ### Request Body

        ```python
        def my_endpoint(input_output):
            raw = input_output.get_body()       # raw body string
            data = input_output.request_data    # parsed JSON (dict/list) or None
            has_body = input_output.has_body()
        ```

        ### Query Parameters

        ```python
        def my_endpoint(query_parameters):
            # GET /users?search=alice&limit=10
            search = query_parameters.get("search")      # "alice"
            limit = query_parameters.get("limit")        # "10" (string!)
            page = query_parameters.get("page", "1")     # with default
        ```

        ### Headers

        ```python
        def my_endpoint(request_headers):
            auth = request_headers.get("Authorization")
            content_type = request_headers.content_type  # attribute access works too
        ```

        ### Path Parameters (Routing Data)

        ```python
        # Route: /users/{user_id}/orders/{order_id}

        def my_endpoint(routing_data):
            user_id = routing_data.get("user_id")
            order_id = routing_data.get("order_id")
        ```

        ### Other Request Info

        `input_output.request_method`, `get_full_path()`, `get_client_ip()`,
        `get_protocol()`.

        ## Response Building

        A `Callable` endpoint just returns data. With `return_standard_response=True`
        (the default) clearskies wraps it:

        ```python
        def my_endpoint():
            return {"users": [], "total": 0}

        # {"status": "success", "error": "", "data": {...}, "pagination": {}, "input_errors": {}}
        ```

        Errors are raised as exceptions from `clearskies.exceptions`:

        | Exception | HTTP status | `status` field |
        |-----------|-------------|----------------|
        | `InputErrors({"field": "msg"})` | 200 | `input_errors` |
        | `ClientError("msg")` | 400 | `client_error` |
        | `Authentication("msg")` | 401 | `client_error` |
        | `Authorization("msg")` | 403 | `client_error` |
        | `NotFound("msg")` | 404 | `client_error` |

        Any other exception is not caught and propagates to the context/server.

        ```python
        def my_endpoint(request_data):
            errors = {}
            if not request_data.get("email"):
                errors["email"] = "Email is required"
            if errors:
                raise clearskies.exceptions.InputErrors(errors)
            return {"created": True}
        ```

        A `Callable` cannot pick its own success status code (e.g. 201) or return
        409/5xx: never return `input_output.respond(...)` from it, since the result
        gets wrapped again with status 200. For full control write a custom endpoint
        class whose `handle()` returns `input_output.respond(body, status_code)`.

        ### Response Headers

        ```python
        endpoint = clearskies.endpoints.Callable(
            my_endpoint,
            response_headers=["x-custom-header: value"],  # or a callable returning that list
        )

        # or inside the callable:
        def my_endpoint(input_output):
            input_output.response_headers.add("x-custom-header", "value")
            return {"ok": True}
        ```

        ### Raw / Non-JSON Responses

        ```python
        def export_csv(input_output):
            input_output.response_headers.add("content-type", "text/csv")
            return "name,email\\nAlice,alice@example.com"

        endpoint = clearskies.endpoints.Callable(export_csv, return_standard_response=False)
        ```

        ## Request Context

        ```python
        def my_endpoint(authorization_data):
            # Data from the authentication handler
            user_id = authorization_data.get("user_id")
            roles = authorization_data.get("roles", [])
        ```

        ## Input Validation Flow

        ```python
        # Model-based endpoints validate writeable columns automatically
        endpoint = clearskies.endpoints.RestfulApi(
            model_class=User,
            writeable_column_names=["name", "email"],
        )

        # Callables can validate via writeable_column_names/input_schema,
        # input_validation_callable, or by raising InputErrors themselves.
        ```

        ## CORS

        CORS is a security header on the endpoint (or endpoint group):

        ```python
        endpoint = clearskies.endpoints.Callable(
            my_endpoint,
            security_headers=[
                clearskies.security_headers.Cors(
                    origin="https://example.com",
                    methods=["GET", "POST"],
                    headers=["Authorization", "Content-Type"],
                ),
            ],
        )
        ```

        ## Request Lifecycle

        1. **Context receives request** - HTTP request arrives
        2. **Routing** - Match URL/method to endpoint
        3. **Authentication / authorization**
        4. **Input validation** - Validate request data
        5. **Endpoint execution** - Your code runs
        6. **Response building** - Wrap data, add headers
        7. **Send response**

        ## Best Practices

        1. **Validate early**: Raise `InputErrors` before processing
        2. **Return data, raise errors**: Let clearskies build the response
        3. **Handle missing data**: Use `.get()` with defaults
        4. **Inject what you need**: `request_data`, `query_parameters`, etc.
        5. **Use authorization_data**: For user context
        6. **Don't trust input**: Always validate
    """),
    "routing": textwrap.dedent("""\
        # Routing in clearskies

        clearskies provides flexible routing capabilities to map URLs to endpoints
        and extract path parameters.

        ## Basic Routing

        ### URL Configuration

        ```python
        # Single endpoint with URL
        endpoint = clearskies.endpoints.RestfulApi(
            url="users",
            model_class=User,
        )

        # Accessible at: /users
        ```

        ### URL Prefixes with Contexts

        ```python
        wsgi = clearskies.contexts.WsgiRef(
            clearskies.endpoints.RestfulApi(
                url="api/v1/users",
                model_class=User,
            )
        )

        # Accessible at: /api/v1/users
        ```

        ## Path Parameters

        ### Dynamic URL Segments

        RestfulApi endpoints automatically provide ID-based routing:

        ```python
        endpoint = clearskies.endpoints.RestfulApi(
            url="users",
            model_class=User,
        )

        # Automatically creates routes:
        # GET /users          - List users
        # GET /users/{id}     - Get user by ID
        # POST /users         - Create user
        # PUT /users/{id}     - Update user
        # DELETE /users/{id}  - Delete user
        ```

        ### Custom Path Parameters

        For Callable endpoints, use placeholders:

        ```python
        def my_endpoint(routing_data):
            return {
                "user_id": routing_data.get("user_id"),
                "order_id": routing_data.get("order_id"),
            }

        endpoint = clearskies.endpoints.Callable(
            url="users/{user_id}/orders/{order_id}",
            to_call=my_endpoint,
        )

        # Matches: /users/123/orders/456
        # routing_data = {"user_id": "123", "order_id": "456"}
        ```

        ## Routing Data

        The `routing_data` parameter contains extracted path parameters:

        ```python
        def my_endpoint(input_output, routing_data):
            # Path: /orders/abc-123
            order_id = routing_data.get("id")  # "abc-123"

            # Path: /users/123/posts/456
            user_id = routing_data.get("user_id")    # "123"
            post_id = routing_data.get("post_id")    # "456"
        ```

        ## Nested Resources

        ### Parent-Child Relationships

        ```python
        # Users endpoint
        users_endpoint = clearskies.endpoints.RestfulApi(
            url="users",
            model_class=User,
        )

        # Orders endpoint (nested under users)
        orders_endpoint = clearskies.endpoints.RestfulApi(
            url="users/{user_id}/orders",
            model_class=Order,
        )

        # Routes created:
        # GET /users/{user_id}/orders
        # GET /users/{user_id}/orders/{id}
        # POST /users/{user_id}/orders
        # etc.
        ```

        ### Filtering by Parent

        ```python
        class Order(clearskies.Model):
            def where_for_request(
                self,
                model,
                input_output,
                routing_data,
                authorization_data,
                overrides={},
            ):
                # Filter by parent user_id from URL
                user_id = routing_data.get("user_id")
                if user_id:
                    return model.where(f"user_id={user_id}")
                return model
        ```

        ## HTTP Methods

        ### Method Routing

        RestfulApi automatically routes by HTTP method:

        - GET → List/Get operations
        - POST → Create operation
        - PUT/PATCH → Update operation
        - DELETE → Delete operation

        ### Custom Method Handling

        ```python
        def my_endpoint(input_output):
            method = input_output.request_method

            # request_methods below already rejects anything else with a 404
            if method == "GET":
                return {"action": "read"}
            return {"action": "create"}

        endpoint = clearskies.endpoints.Callable(
            url="custom",
            to_call=my_endpoint,
            request_methods=["GET", "POST"],
        )
        ```

        ## Query Parameters

        Query parameters are separate from routing:

        ```python
        def my_endpoint(query_parameters):
            # URL: /users?search=alice&limit=10
            search = query_parameters.get("search")  # "alice"
            limit = query_parameters.get("limit")    # "10"
        ```

        ## Route Matching Order

        clearskies matches routes in this order:

        1. **Exact matches** - `/users/admin` before `/users/{id}`
        2. **Specific prefixes** - `/api/v2/users` before `/api/v1/users`
        3. **Parameter routes** - Routes with parameters
        4. **Wildcard routes** - Catch-all routes (if configured)

        ## URL Encoding

        Path parameters are automatically URL-decoded:

        ```python
        # URL: /users/alice%40example.com
        # routing_data.get("id") = "alice@example.com"
        ```

        ## Best Practices

        1. **Use semantic URLs**: `/users/{user_id}/orders` not `/get_user_orders`
        2. **Keep URLs lowercase**: `/users` not `/Users`
        3. **Use plural nouns**: `/users` not `/user`
        4. **Use hyphens for multi-word**: `/user-profiles` not `/user_profiles`
        5. **Version your APIs**: `/api/v1/users` not `/users_v1`
        6. **Filter by routing_data**: Use parent IDs from the URL
        7. **Validate path parameters**: Check IDs exist before using
    """),
    "endpoint_groups": textwrap.dedent("""\
        # Endpoint Groups in clearskies

        Endpoint groups allow you to organize multiple related endpoints under
        a common URL prefix with shared configuration like authentication.

        ## Basic EndpointGroup

        ### Creating a Group

        ```python
        import clearskies
        from clearskies import columns

        class User(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()
            id = columns.Uuid()
            name = columns.String()

        class Order(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()
            id = columns.Uuid()
            user_id = columns.BelongsToId(parent_model_class=User)

        # Group multiple endpoints
        api = clearskies.EndpointGroup(
            url="api/v1",
            endpoints=[
                clearskies.endpoints.RestfulApi(
                    url="users",
                    model_class=User,
                ),
                clearskies.endpoints.RestfulApi(
                    url="orders",
                    model_class=Order,
                ),
            ],
        )

        # Creates routes:
        # /api/v1/users
        # /api/v1/users/{id}
        # /api/v1/orders
        # /api/v1/orders/{id}
        ```

        ## Shared Authentication

        Apply authentication to all endpoints in a group:

        ```python
        api = clearskies.EndpointGroup(
            url="api/v1",
            authentication=clearskies.authentication.SecretBearer(
                environment_key="API_SECRET",
            ),
            endpoints=[
                clearskies.endpoints.RestfulApi(url="users", model_class=User),
                clearskies.endpoints.RestfulApi(url="orders", model_class=Order),
            ],
        )

        # All endpoints require authentication
        ```

        ## Mixing Endpoint Types

        Combine different endpoint types:

        ```python
        api = clearskies.EndpointGroup(
            url="api/v1",
            endpoints=[
                # RESTful API endpoints
                clearskies.endpoints.RestfulApi(url="users", model_class=User),

                # Custom callable endpoint
                clearskies.endpoints.Callable(
                    url="health",
                    to_call=lambda: {"status": "ok"},
                ),

                # List-only endpoint
                clearskies.endpoints.List(
                    url="reports",
                    model_class=Report,
                ),
            ],
        )
        ```

        ## Nested Groups

        Create hierarchical endpoint structures:

        ```python
        # v1 API
        v1_api = clearskies.EndpointGroup(
            url="api/v1",
            endpoints=[
                clearskies.endpoints.RestfulApi(url="users", model_class=User),
            ],
        )

        # v2 API with different models
        v2_api = clearskies.EndpointGroup(
            url="api/v2",
            endpoints=[
                clearskies.endpoints.RestfulApi(url="users", model_class=UserV2),
            ],
        )

        # Root group containing both versions
        root = clearskies.EndpointGroup(
            endpoints=[v1_api, v2_api],
        )
        ```

        ## Per-Endpoint Configuration

        Override group settings for specific endpoints:

        ```python
        # Different authentication for different endpoints
        api = clearskies.EndpointGroup(
            url="api/v1",
            authentication=clearskies.authentication.SecretBearer(
                environment_key="API_SECRET",
            ),
            endpoints=[
                # Uses group authentication
                clearskies.endpoints.RestfulApi(url="orders", model_class=Order),

                # Public endpoint - overrides group auth
                clearskies.endpoints.Callable(
                    url="health",
                    to_call=lambda: {"status": "ok"},
                    authentication=clearskies.authentication.Public(),
                ),
            ],
        )
        ```

        ## Organizing Large APIs

        ### By Resource

        ```python
        users_group = clearskies.EndpointGroup(
            url="users",
            endpoints=[
                clearskies.endpoints.List(url="", model_class=User),
                clearskies.endpoints.Get(url="{id}", model_class=User),
                clearskies.endpoints.Create(url="", model_class=User),
            ],
        )

        orders_group = clearskies.EndpointGroup(
            url="orders",
            endpoints=[
                clearskies.endpoints.List(url="", model_class=Order),
                clearskies.endpoints.Get(url="{id}", model_class=Order),
            ],
        )

        api = clearskies.EndpointGroup(
            url="api/v1",
            endpoints=[users_group, orders_group],
        )
        ```

        ### By Feature

        ```python
        admin_api = clearskies.EndpointGroup(
            url="admin",
            authentication=clearskies.authentication.SecretBearer(
                environment_key="ADMIN_SECRET",
            ),
            endpoints=[
                clearskies.endpoints.RestfulApi(url="users", model_class=User),
                clearskies.endpoints.RestfulApi(url="settings", model_class=Settings),
            ],
        )

        public_api = clearskies.EndpointGroup(
            url="public",
            authentication=clearskies.authentication.Public(),
            endpoints=[
                clearskies.endpoints.List(url="products", model_class=Product),
            ],
        )
        ```

        ## EndpointGroup Configuration

        | Parameter | Type | Description |
        |-----------|------|-------------|
        | `url` | str | URL prefix for all endpoints in the group |
        | `endpoints` | list | List of endpoint instances |
        | `authentication` | auth handler | Shared authentication (optional) |
        | `cors` | dict | CORS configuration (optional) |

        ## Complete Example

        ```python
        import clearskies
        from clearskies import columns

        # Models
        class User(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()
            id = columns.Uuid()
            name = columns.String()
            email = columns.Email()

        class Order(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()
            id = columns.Uuid()
            user_id = columns.BelongsToId(parent_model_class=User)
            total = columns.Float()

        class Product(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()
            id = columns.Uuid()
            name = columns.String()
            price = columns.Float()

        # Authentication
        api_auth = clearskies.authentication.SecretBearer(
            environment_key="API_SECRET"
        )

        # API structure
        api = clearskies.EndpointGroup(
            url="api/v1",
            authentication=api_auth,
            endpoints=[
                # User management
                clearskies.endpoints.RestfulApi(
                    url="users",
                    model_class=User,
                    readable_column_names=["id", "name", "email"],
                    writeable_column_names=["name", "email"],
                ),

                # Order management
                clearskies.endpoints.RestfulApi(
                    url="orders",
                    model_class=Order,
                    readable_column_names=["id", "user_id", "total"],
                    writeable_column_names=["user_id", "total"],
                ),

                # Public product catalog
                clearskies.endpoints.List(
                    url="products",
                    model_class=Product,
                    readable_column_names=["id", "name", "price"],
                    authentication=clearskies.authentication.Public(),
                ),

                # Health check
                clearskies.endpoints.Callable(
                    url="health",
                    to_call=lambda: {"status": "ok"},
                    authentication=clearskies.authentication.Public(),
                ),
            ],
        )

        # Deploy with WSGI
        wsgi = clearskies.contexts.WsgiRef(api)
        wsgi()
        ```

        ## Best Practices

        1. **Group related endpoints**: Keep logically related endpoints together
        2. **Use consistent URL prefixes**: `/api/v1`, `/api/v2` for versioning
        3. **Share authentication**: Apply auth at group level when possible
        4. **Override when needed**: Individual endpoints can override group settings
        5. **Keep groups focused**: Don't create overly large groups
        6. **Version your APIs**: Use groups for version management
        7. **Document group structure**: Make API organization clear
    """),
    "responses": textwrap.dedent("""\
        # Response Handling in clearskies

        clearskies builds JSON responses for you; this covers status codes, headers and raw output.

        ## Standard Responses

        Endpoints build responses for you. A `Callable` returns data; errors are
        raised as exceptions from `clearskies.exceptions`.

        ### Success Response

        ```python
        def my_endpoint():
            return {"user": {"id": "123", "name": "Alice"}}

        # HTTP 200
        # {"status": "success", "error": "", "data": {"user": {...}},
        #  "pagination": {}, "input_errors": {}}
        ```

        Returning a model query (with `model_class` and `readable_column_names` set)
        serializes the records and fills `pagination` automatically.

        ### Error Response

        ```python
        def my_endpoint(users, routing_data):
            user = users.find(f"id={routing_data['id']}")
            if not user:
                raise clearskies.exceptions.NotFound("User not found")
            return {"id": user.id}

        # HTTP 404
        # {"status": "client_error", "error": "User not found", ...}
        ```

        ### Input Errors (Validation)

        ```python
        def my_endpoint():
            raise clearskies.exceptions.InputErrors({
                "email": "Email is required",
                "name": "Name must be at least 3 characters",
            })

        # HTTP 200 (yes, 200)
        # {"status": "input_errors", "input_errors": {"email": ..., "name": ...}, ...}
        ```

        ## HTTP Status Codes

        | Status | How |
        |--------|-----|
        | 200 | return data |
        | 400 | `raise clearskies.exceptions.ClientError("Invalid request")` |
        | 401 | `raise clearskies.exceptions.Authentication("Unauthorized")` |
        | 403 | `raise clearskies.exceptions.Authorization("Forbidden")` |
        | 404 | `raise clearskies.exceptions.NotFound("Not found")` |
        | 302 / 307 | `MovedPermanently(url)` / `MovedTemporarily(url)` (the Location header is malformed in 2.1.14; avoid) |
        | other (201, 409, 5xx) | not available from a `Callable`; see below |

        Uncaught exceptions are not converted: they propagate to the context/server.
        Never return `input_output.respond(...)` from a `Callable`: its return value
        is treated as data and wrapped again with status 200.

        ### Custom Status Codes

        Write a small endpoint class and call `respond(body, status_code)` yourself:

        ```python
        class Conflict(clearskies.endpoints.Callable):
            def handle(self, input_output):
                return self.respond_json(
                    input_output, {"status": "client_error", "error": "Email already exists"}, 409
                )
        ```

        ## Response Headers

        `InputOutput.respond()` has no `headers` argument. Set headers on the endpoint:

        ```python
        endpoint = clearskies.endpoints.Callable(
            my_endpoint,
            response_headers=["x-request-id: abc-123", "x-rate-limit-remaining: 99"],
            security_headers=[clearskies.security_headers.CacheControl(public=True, max_age=3600)],
        )
        ```

        `response_headers` may also be a callable returning that list. Inside a
        callable you can add headers directly:

        ```python
        def my_endpoint(input_output):
            input_output.response_headers.add("x-total-count", "42")
            return {"items": []}
        ```

        ### CORS

        ```python
        endpoint = clearskies.endpoints.Callable(
            my_endpoint,
            security_headers=[
                clearskies.security_headers.Cors(
                    origin="https://example.com",
                    methods=["GET", "POST", "PUT", "DELETE"],
                    headers=["Authorization", "Content-Type"],
                    expose_headers=["X-Total-Count"],
                    max_age=3600,
                ),
            ],
        )
        ```

        ## Non-JSON Responses (CSV, text, XML, downloads)

        Use `return_standard_response=False`: the return value is sent as-is with
        status 200. Set the content type via `input_output.response_headers` (the
        endpoint's `response_headers` option is not applied on this path).

        ```python
        def export_users(input_output):
            input_output.response_headers.add("content-type", "text/csv")
            input_output.response_headers.add("content-disposition", 'attachment; filename="users.csv"')
            return "name,email\\nAlice,alice@example.com\\nBob,bob@example.com"

        endpoint = clearskies.endpoints.Callable(export_users, return_standard_response=False)
        ```

        ## Pagination Responses

        ```python
        def list_users(users, query_parameters):
            limit = int(query_parameters.get("limit", "20"))
            start = int(query_parameters.get("start", "0"))
            return users.limit(limit).pagination(start=start)

        endpoint = clearskies.endpoints.Callable(
            list_users,
            model_class=User,
            readable_column_names=["id", "name"],
        )

        # {"status": "success", "data": [...],
        #  "pagination": {"number_results": 100, "limit": 20, "next_page": {"start": 20}}, ...}
        ```

        For built-in list endpoints, prefer `clearskies.endpoints.List` which
        handles pagination, sorting and filtering for you.

        ## Best Practices

        1. **Return data, raise errors**: Keep the standard response format
        2. **Use the right exception**: It picks the status code
        3. **Include helpful messages**: Clear error descriptions
        4. **Set content types** for non-JSON responses
        5. **Paginate lists**: Don't return unbounded data
        6. **Don't expose internal details** in error messages
        7. **Use cache headers**: `security_headers.CacheControl`
    """),
}
