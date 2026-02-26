"""
Developer experience concept explanations for clearskies framework.

This module contains troubleshooting guides, best practices, exception reference,
and authentication flow documentation.
"""

import textwrap

DEVEX_CONCEPTS = {
    "troubleshooting": textwrap.dedent("""\
        # Troubleshooting Guide for clearskies

        This guide helps you diagnose and fix common issues when working with clearskies.

        ## Common Issues and Solutions

        ### 1. Model Not Found / Import Errors

        **Symptom:** `ImportError` or model not available in DI

        **Causes:**
        - Model not registered with context
        - Circular import issues
        - Typo in model name

        **Solutions:**
        ```python
        # ✅ Register models explicitly
        cli = clearskies.contexts.Cli(
            my_function,
            classes=[User, Order],  # Register all needed models
        )

        # ✅ Or register entire modules
        import app.models
        cli = clearskies.contexts.Cli(
            my_function,
            modules=[app.models],
        )
        ```

        ### 2. Backend Not Connected

        **Symptom:** `AttributeError: 'NoneType' object has no attribute 'cursor'`

        **Causes:**
        - Cursor not injected into context
        - Connection not established

        **Solutions:**
        ```python
        # ✅ Ensure cursor is provided
        import pymysql

        connection = pymysql.connect(...)
        cursor = connection.cursor()

        cli = clearskies.contexts.Cli(
            my_function,
            bindings={"cursor": cursor},
        )
        ```

        ### 3. Query Returns No Results

        **Symptom:** Empty results when data should exist

        **Causes:**
        - Wrong condition syntax
        - Case sensitivity issues
        - Data not committed

        **Solutions:**
        ```python
        # Check condition syntax
        users.where("status=active")      # ✅ Correct
        users.where("status = active")    # ✅ Also correct
        users.where("status='active'")    # ❌ Don't quote values

        # Check case sensitivity
        users.where("email=Alice@Example.com")  # Case-sensitive!

        # Ensure data is committed
        connection.commit()  # Don't forget!
        ```

        ### 4. Validation Errors Not Showing

        **Symptom:** Validation fails silently or with generic error

        **Causes:**
        - Validators not configured on columns
        - Wrong validator import

        **Solutions:**
        ```python
        from clearskies.validators import Required, Unique

        class User(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            name = columns.String(validators=[Required()])  # ✅ Add validators
            email = columns.Email(validators=[Required(), Unique()])
        ```

        ### 5. Circular Import Errors

        **Symptom:** `ImportError: cannot import name 'X' from partially initialized module`

        **Causes:**
        - Models importing each other
        - Relationship columns with direct class references

        **Solutions:**
        ```python
        # ❌ Circular import
        # models/user.py
        from models.order import Order
        class User(clearskies.Model):
            orders = columns.HasMany(related_model_class=Order)

        # models/order.py
        from models.user import User  # Circular!
        class Order(clearskies.Model):
            user_id = columns.BelongsToId(parent_model_class=User)

        # ✅ Use string references
        class User(clearskies.Model):
            orders = columns.HasMany(related_model_class="Order")

        class Order(clearskies.Model):
            user_id = columns.BelongsToId(parent_model_class="User")
        ```

        ### 6. Authentication Not Working

        **Symptom:** 401 Unauthorized or auth data not available

        **Causes:**
        - Authentication not configured on endpoint
        - Wrong header name
        - Token format incorrect

        **Solutions:**
        ```python
        # ✅ Configure authentication
        endpoint = clearskies.endpoints.RestfulApi(
            model_class=User,
            authentication=clearskies.authentication.SecretBearer(
                environment_key="API_SECRET",
            ),
        )

        # ✅ Check header format
        # Header should be: Authorization: Bearer <token>
        ```

        ### 7. Save Hooks Not Running

        **Symptom:** `pre_save` or `post_save` not called

        **Causes:**
        - Hook method name typo
        - Hook not returning data (for pre_save)

        **Solutions:**
        ```python
        class User(clearskies.Model):
            # ✅ Correct hook names
            def pre_save(self, data):
                # Must return data!
                data["updated_at"] = datetime.utcnow()
                return data  # ✅ Don't forget this!

            def post_save(self, data, was_created):
                # No return needed
                if was_created:
                    send_welcome_email(self.email)
        ```

        ### 8. N+1 Query Performance Issues

        **Symptom:** Slow performance with many database queries

        **Causes:**
        - Accessing relationships in a loop
        - Not batching queries

        **Solutions:**
        ```python
        # ❌ N+1 queries
        for order in orders:
            print(order.user.name)  # Query per order!

        # ✅ Batch load relationships
        orders = list(orders_model.where("status=pending"))
        user_ids = [o.user_id for o in orders]
        users = {u.id: u for u in users_model.where(f"id in {','.join(user_ids)}")}

        for order in orders:
            user = users.get(order.user_id)
            print(user.name if user else "Unknown")
        ```

        ## Debugging Techniques

        ### Enable Query Logging

        ```python
        import logging
        logging.getLogger('clearskies').setLevel(logging.DEBUG)

        # Now queries will be logged
        users.where("status=active").first()
        # DEBUG: SELECT * FROM users WHERE status = 'active' LIMIT 1
        ```

        ### Inspect Model State

        ```python
        user = users.find("id=123")

        # Check if record exists
        print(f"Exists: {user.exists}")

        # Check model data
        print(f"Data: {user.__data__}")

        # Check column values
        for col_name in user.columns():
            print(f"{col_name}: {getattr(user, col_name)}")
        ```

        ### Test in Isolation

        ```python
        # Use MemoryBackend for isolated testing
        class TestUser(User):
            backend = clearskies.backends.MemoryBackend()

        # Test without database
        test_users = TestUser()
        user = test_users.create({"name": "Test"})
        assert user.name == "Test"
        ```

        ## Getting Help

        1. **Check the documentation**: Use `explain_concept()` tool
        2. **Review examples**: Check `clearskies://examples/*` resources
        3. **Enable debug logging**: See queries and operations
        4. **Isolate the issue**: Use MemoryBackend for testing
        5. **Check GitHub issues**: Search for similar problems
    """),
    "best_practices": textwrap.dedent("""\
        # Best Practices for clearskies Development

        This guide covers recommended patterns and practices for building
        maintainable clearskies applications.

        ## Project Structure

        ### Recommended Layout

        ```
        myapp/
        ├── models/
        │   ├── __init__.py
        │   ├── user.py
        │   ├── order.py
        │   └── product.py
        ├── endpoints/
        │   ├── __init__.py
        │   ├── users.py
        │   └── orders.py
        ├── services/
        │   ├── __init__.py
        │   ├── email_service.py
        │   └── payment_service.py
        ├── config/
        │   ├── __init__.py
        │   └── settings.py
        ├── tests/
        │   ├── __init__.py
        │   ├── test_models.py
        │   └── test_endpoints.py
        ├── app.py
        └── requirements.txt
        ```

        ## Model Design

        ### Keep Models Focused

        ```python
        # ✅ Good - focused model
        class User(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            name = columns.String(max_length=255)
            email = columns.Email(max_length=255)
            created_at = columns.Created()
            updated_at = columns.Updated()

        # ❌ Bad - too many responsibilities
        class User(clearskies.Model):
            # ... 50 columns ...
            # ... complex business logic ...
            # ... external API calls ...
        ```

        ### Use Appropriate Column Types

        ```python
        # ✅ Use specific column types
        email = columns.Email()      # Validates email format
        phone = columns.Phone()      # Validates phone format
        status = columns.Select(["active", "inactive"])  # Enum values

        # ❌ Don't use String for everything
        email = columns.String()     # No validation
        ```

        ### Define Relationships Clearly

        ```python
        class Order(clearskies.Model):
            # ✅ Clear relationship definitions
            user_id = columns.BelongsToId(parent_model_class=User)
            user = columns.BelongsToModel(parent_model_class=User)

            # ✅ Use string references to avoid circular imports
            items = columns.HasMany(related_model_class="OrderItem")
        ```

        ## Endpoint Design

        ### Use Declarative Configuration

        ```python
        # ✅ Good - declarative
        endpoint = clearskies.endpoints.RestfulApi(
            model_class=User,
            readable_column_names=["id", "name", "email"],
            writeable_column_names=["name", "email"],
            searchable_column_names=["name", "email"],
            default_sort_column_name="name",
        )

        # ❌ Avoid - imperative controller logic
        def get_users(request):
            users = User.query().all()
            return [u.to_dict() for u in users]
        ```

        ### Limit Exposed Columns

        ```python
        # ✅ Only expose what's needed
        endpoint = clearskies.endpoints.RestfulApi(
            model_class=User,
            readable_column_names=["id", "name", "email"],  # No password!
            writeable_column_names=["name", "email"],       # No id!
        )
        ```

        ### Use Endpoint Groups

        ```python
        # ✅ Organize related endpoints
        api = clearskies.endpoints.EndpointGroup(
            url="api/v1",
            endpoints=[
                clearskies.endpoints.RestfulApi(url="users", model_class=User),
                clearskies.endpoints.RestfulApi(url="orders", model_class=Order),
            ],
            authentication=clearskies.authentication.SecretBearer(...),
        )
        ```

        ## Error Handling

        ### Use Appropriate Error Responses

        ```python
        def my_endpoint(input_output, users):
            user_id = input_output.get_query_parameter("user_id")

            if not user_id:
                return input_output.input_errors({"user_id": "Required"})

            user = users.find(f"id={user_id}")
            if not user.exists:
                return input_output.error("User not found", 404)

            return input_output.success({"user": user.to_dict()})
        ```

        ### Validate Early

        ```python
        # ✅ Validate at the start
        def create_order(input_output, orders, products):
            body = input_output.get_body()

            # Validate first
            errors = {}
            if not body.get("product_id"):
                errors["product_id"] = "Required"
            if not body.get("quantity"):
                errors["quantity"] = "Required"

            if errors:
                return input_output.input_errors(errors)

            # Then process
            product = products.find(f"id={body['product_id']}")
            if not product.exists:
                return input_output.error("Product not found", 404)

            # Create order...
        ```

        ## Testing

        ### Use MemoryBackend for Unit Tests

        ```python
        import pytest

        class TestUser(User):
            backend = clearskies.backends.MemoryBackend()

        def test_create_user():
            users = TestUser()
            user = users.create({"name": "Alice", "email": "alice@example.com"})
            assert user.name == "Alice"
        ```

        ### Test Business Logic Separately

        ```python
        # ✅ Test model logic in isolation
        def test_user_full_name():
            user = TestUser()
            user.first_name = "Alice"
            user.last_name = "Smith"
            assert user.full_name == "Alice Smith"

        # ✅ Test endpoints separately
        def test_user_endpoint():
            # Use test context with mocked dependencies
            pass
        ```

        ## Performance

        ### Use Pagination

        ```python
        # ✅ Always paginate large result sets
        endpoint = clearskies.endpoints.List(
            model_class=User,
            default_limit=20,
            max_limit=100,
        )
        ```

        ### Limit Query Results

        ```python
        # ✅ Use limit()
        recent_users = users.sort_by("created_at", "desc").limit(10)

        # ❌ Don't load all records
        all_users = list(users)  # Could be millions!
        ```

        ### Index Database Columns

        ```sql
        -- Add indexes for frequently queried columns
        CREATE INDEX idx_users_email ON users(email);
        CREATE INDEX idx_users_status ON users(status);
        CREATE INDEX idx_orders_user_id ON orders(user_id);
        ```

        ## Security

        ### Never Trust User Input

        ```python
        # ✅ clearskies uses parameterized queries automatically
        users.where(f"email={user_input}")  # Safe!

        # ❌ Don't build raw SQL with user input
        cursor.execute(f"SELECT * FROM users WHERE email = '{user_input}'")  # SQL injection!
        ```

        ### Use Authentication

        ```python
        # ✅ Always authenticate API endpoints
        endpoint = clearskies.endpoints.RestfulApi(
            model_class=User,
            authentication=clearskies.authentication.SecretBearer(
                environment_key="API_SECRET",
            ),
        )
        ```

        ### Protect Sensitive Data

        ```python
        # ✅ Don't expose sensitive columns
        endpoint = clearskies.endpoints.RestfulApi(
            model_class=User,
            readable_column_names=["id", "name", "email"],  # No password_hash!
        )
        ```

        ## Code Organization

        ### Use Services for Complex Logic

        ```python
        # ✅ Extract complex logic to services
        class OrderService:
            def __init__(self, orders, products, email_service):
                self.orders = orders
                self.products = products
                self.email_service = email_service

            def create_order(self, user, items):
                # Complex order creation logic
                order = self.orders.create({...})
                self.email_service.send_confirmation(user.email, order)
                return order
        ```

        ### Keep Endpoints Thin

        ```python
        # ✅ Endpoints delegate to services
        def create_order_endpoint(input_output, order_service, authorization_data):
            body = input_output.get_body()
            user_id = authorization_data.get("user_id")

            try:
                order = order_service.create_order(user_id, body["items"])
                return input_output.success({"order_id": order.id})
            except ValidationError as e:
                return input_output.input_errors(e.errors)
        ```
    """),
    "exceptions": textwrap.dedent("""\
        # Exception Hierarchy in clearskies

        Understanding clearskies exceptions helps you handle errors appropriately
        and provide meaningful feedback to users.

        ## Base Exceptions

        ### clearskies.ClearskiesException

        Base exception for all clearskies errors:

        ```python
        try:
            # clearskies operation
            pass
        except clearskies.ClearskiesException as e:
            # Catch any clearskies error
            print(f"clearskies error: {e}")
        ```

        ## Validation Exceptions

        ### ValidationError

        Raised when data validation fails:

        ```python
        from clearskies.exceptions import ValidationError

        try:
            user = users.create({"email": "invalid"})
        except ValidationError as e:
            print(f"Validation failed: {e.errors}")
            # e.errors = {"email": "Invalid email format"}
        ```

        ### InputError

        Raised for invalid input data:

        ```python
        from clearskies.exceptions import InputError

        try:
            # Process input
            pass
        except InputError as e:
            print(f"Input error: {e.message}")
            print(f"Field: {e.field}")
        ```

        ## Backend Exceptions

        ### BackendException

        Base exception for backend errors:

        ```python
        from clearskies.exceptions import BackendException

        try:
            users.create({"name": "Alice"})
        except BackendException as e:
            print(f"Backend error: {e}")
        ```

        ### RecordNotFound

        Raised when a required record doesn't exist:

        ```python
        from clearskies.exceptions import RecordNotFound

        try:
            user = users.find_or_fail("id=nonexistent")
        except RecordNotFound as e:
            print(f"Record not found: {e}")
        ```

        ### DuplicateRecord

        Raised for unique constraint violations:

        ```python
        from clearskies.exceptions import DuplicateRecord

        try:
            users.create({"email": "existing@example.com"})
        except DuplicateRecord as e:
            print(f"Duplicate: {e}")
        ```

        ## Authentication Exceptions

        ### AuthenticationError

        Raised when authentication fails:

        ```python
        from clearskies.exceptions import AuthenticationError

        try:
            # Authenticate request
            pass
        except AuthenticationError as e:
            print(f"Auth failed: {e}")
            # Return 401 response
        ```

        ### AuthorizationError

        Raised when authorization fails:

        ```python
        from clearskies.exceptions import AuthorizationError

        try:
            # Check permissions
            pass
        except AuthorizationError as e:
            print(f"Not authorized: {e}")
            # Return 403 response
        ```

        ## Configuration Exceptions

        ### ConfigurationError

        Raised for configuration issues:

        ```python
        from clearskies.exceptions import ConfigurationError

        try:
            # Load configuration
            pass
        except ConfigurationError as e:
            print(f"Config error: {e}")
        ```

        ## Handling Exceptions in Endpoints

        ### Callable Endpoints

        ```python
        def my_endpoint(input_output, users):
            try:
                user = users.create(input_output.get_body())
                return input_output.success({"user_id": user.id})

            except ValidationError as e:
                return input_output.input_errors(e.errors)

            except DuplicateRecord:
                return input_output.input_errors({
                    "email": "Email already exists"
                })

            except BackendException as e:
                # Log the error
                logging.error(f"Database error: {e}")
                return input_output.error("Internal server error", 500)
        ```

        ### Global Error Handler

        ```python
        def error_handler(exception, input_output):
            if isinstance(exception, ValidationError):
                return input_output.input_errors(exception.errors)

            if isinstance(exception, AuthenticationError):
                return input_output.error("Unauthorized", 401)

            if isinstance(exception, AuthorizationError):
                return input_output.error("Forbidden", 403)

            # Log unexpected errors
            logging.exception("Unexpected error")
            return input_output.error("Internal server error", 500)
        ```

        ## Database-Specific Exceptions

        When using CursorBackend, you may also encounter database-specific exceptions:

        ### MySQL (pymysql)

        ```python
        import pymysql

        try:
            users.create({"email": "test@example.com"})
        except pymysql.IntegrityError as e:
            # Duplicate key, foreign key violation
            print(f"Integrity error: {e}")
        except pymysql.OperationalError as e:
            # Connection issues, deadlocks
            print(f"Operational error: {e}")
        except pymysql.ProgrammingError as e:
            # SQL syntax errors
            print(f"Programming error: {e}")
        ```

        ### PostgreSQL (psycopg2)

        ```python
        import psycopg2

        try:
            users.create({"email": "test@example.com"})
        except psycopg2.IntegrityError as e:
            print(f"Integrity error: {e}")
        except psycopg2.OperationalError as e:
            print(f"Operational error: {e}")
        ```

        ## Best Practices

        1. **Catch specific exceptions**: Don't catch `Exception` broadly
        2. **Log unexpected errors**: For debugging
        3. **Return appropriate HTTP status codes**: 400, 401, 403, 404, 500
        4. **Don't expose internal details**: Generic messages for 500 errors
        5. **Use input_errors for validation**: Structured error responses
    """),
    "auth_flow": textwrap.dedent("""\
        # Authentication and Authorization Flow in clearskies

        This guide explains how authentication and authorization work together
        in clearskies and how data flows through the system.

        ## Overview

        ```
        Request → Authentication → Authorization → Endpoint → Response
                      ↓                  ↓
               authorization_data   where_for_request
        ```

        ## Authentication

        Authentication verifies **who** the user is.

        ### Configuration

        ```python
        endpoint = clearskies.endpoints.RestfulApi(
            model_class=User,
            authentication=clearskies.authentication.SecretBearer(
                environment_key="API_SECRET",
            ),
        )
        ```

        ### Available Authentication Methods

        1. **SecretBearer** - Simple bearer token
        2. **JWKS** - JSON Web Key Set (JWT)
        3. **Public** - No authentication required
        4. **Custom** - Your own authentication handler

        ### Authentication Data Flow

        ```python
        # 1. Request arrives with Authorization header
        # Authorization: Bearer my-secret-token

        # 2. Authentication handler validates token
        # 3. Handler returns authorization_data dict
        authorization_data = {
            "user_id": "123",
            "roles": ["admin", "user"],
            "tenant_id": "456",
        }

        # 4. authorization_data is available in endpoints
        def my_endpoint(input_output, authorization_data):
            user_id = authorization_data.get("user_id")
            roles = authorization_data.get("roles", [])
        ```

        ### Custom Authentication

        ```python
        class MyAuthentication(clearskies.authentication.Authentication):
            def authenticate(self, input_output):
                token = input_output.get_header("Authorization")
                if not token:
                    return None  # Authentication failed

                # Validate token and return authorization data
                user = self.validate_token(token)
                if not user:
                    return None

                return {
                    "user_id": user.id,
                    "roles": user.roles,
                }

        endpoint = clearskies.endpoints.RestfulApi(
            model_class=Order,
            authentication=MyAuthentication(),
        )
        ```

        ## Authorization

        Authorization determines **what** the user can do.

        ### Model-Level Authorization

        Use `where_for_request` to filter data based on the user:

        ```python
        class Order(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            user_id = columns.BelongsToId(parent_model_class=User)
            total = columns.Float()

            def where_for_request(
                self,
                model,
                input_output,
                routing_data,
                authorization_data,
                overrides={},
            ):
                # Users can only see their own orders
                user_id = authorization_data.get("user_id")
                return model.where(f"user_id={user_id}")
        ```

        ### Role-Based Authorization

        ```python
        class Document(clearskies.Model):
            def where_for_request(
                self,
                model,
                input_output,
                routing_data,
                authorization_data,
                overrides={},
            ):
                roles = authorization_data.get("roles", [])

                # Admins see everything
                if "admin" in roles:
                    return model

                # Regular users see only published
                return model.where("status=published")
        ```

        ### Endpoint-Level Authorization

        ```python
        def admin_only_endpoint(input_output, authorization_data):
            roles = authorization_data.get("roles", [])

            if "admin" not in roles:
                return input_output.error("Forbidden", 403)

            # Admin-only logic
            return input_output.success({"admin": True})
        ```

        ## Data Flow Diagram

        ```
        1. HTTP Request
           └── Headers: Authorization: Bearer <token>
           └── Body: {"name": "New Order"}

        2. Context (Wsgi/WsgiRef)
           └── Parses request
           └── Creates input_output object

        3. Authentication Handler
           └── Extracts token from header
           └── Validates token
           └── Returns authorization_data: {"user_id": "123", "roles": [...]}

        4. Routing
           └── Matches URL to endpoint
           └── Extracts routing_data: {"id": "456"}

        5. Endpoint
           └── Receives: input_output, authorization_data, routing_data
           └── Calls model methods

        6. Model (where_for_request)
           └── Filters data based on authorization_data
           └── Returns filtered query

        7. Response
           └── Endpoint returns data
           └── Context sends HTTP response
        ```

        ## Multi-Tenant Applications

        Common pattern for SaaS applications:

        ```python
        class TenantModel(clearskies.Model):
            '''Base model for multi-tenant data.'''

            tenant_id = columns.String()

            def where_for_request(
                self,
                model,
                input_output,
                routing_data,
                authorization_data,
                overrides={},
            ):
                tenant_id = authorization_data.get("tenant_id")
                if not tenant_id:
                    raise AuthorizationError("No tenant context")
                return model.where(f"tenant_id={tenant_id}")

        class User(TenantModel):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            name = columns.String()
            # tenant_id inherited from TenantModel

        class Order(TenantModel):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            user_id = columns.BelongsToId(parent_model_class=User)
            # tenant_id inherited from TenantModel
        ```

        ## Combining Authentication and Authorization

        ```python
        # 1. Define authentication
        auth = clearskies.authentication.JWKS(
            jwks_url="https://auth.example.com/.well-known/jwks.json",
            claims_to_authorization_data={
                "sub": "user_id",
                "tenant": "tenant_id",
                "roles": "roles",
            },
        )

        # 2. Define model with authorization
        class Order(clearskies.Model):
            def where_for_request(self, model, input_output, routing_data, authorization_data, overrides={}):
                # Filter by tenant and user
                tenant_id = authorization_data.get("tenant_id")
                user_id = authorization_data.get("user_id")
                roles = authorization_data.get("roles", [])

                query = model.where(f"tenant_id={tenant_id}")

                # Admins see all tenant orders
                if "admin" in roles:
                    return query

                # Users see only their orders
                return query.where(f"user_id={user_id}")

        # 3. Create endpoint with authentication
        endpoint = clearskies.endpoints.RestfulApi(
            model_class=Order,
            authentication=auth,
            readable_column_names=["id", "total", "status"],
            writeable_column_names=["status"],
        )
        ```

        ## Best Practices

        1. **Always authenticate API endpoints**: Use appropriate auth method
        2. **Implement where_for_request**: For data-level authorization
        3. **Check roles in endpoints**: For action-level authorization
        4. **Use tenant isolation**: For multi-tenant apps
        5. **Don't trust client data**: Always verify server-side
        6. **Log authentication failures**: For security monitoring
        7. **Use HTTPS**: Protect tokens in transit
    """),
}
