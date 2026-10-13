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
            orders = columns.HasMany(Order)

        # models/order.py
        from models.user import User  # Circular!
        class Order(clearskies.Model):
            user_id = columns.BelongsToId(parent_model_class=User)

        # ✅ Use model class references (import inside the method)
        # models/order_reference.py
        class OrderReference(clearskies.model.ModelClassReference):
            def get_model_class(self):
                from models.order import Order
                return Order

        # models/user.py
        from models.order_reference import OrderReference
        class User(clearskies.Model):
            orders = columns.HasMany(OrderReference)
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
            readable_column_names=["id", "name", "email"],
            writeable_column_names=["name", "email"],
            searchable_column_names=["name", "email"],
            sortable_column_names=["name"],
            default_sort_column_name="name",
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
        print(f"Exists: {bool(user)}")

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
            name = columns.String()
            email = columns.Email()
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
            user_id = columns.BelongsToId(User)
            user = columns.BelongsToModel("user_id")

            # ✅ Use a ModelClassReference to avoid circular imports
            items = columns.HasMany(OrderItemReference)
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
            sortable_column_names=["name"],
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
            searchable_column_names=["name", "email"],
            sortable_column_names=["name"],
            default_sort_column_name="name",
        )
        ```

        ### Use Endpoint Groups

        ```python
        # ✅ Organize related endpoints
        api = clearskies.EndpointGroup(
            url="api/v1",
            endpoints=[
                clearskies.endpoints.RestfulApi(
                    url="users",
                    model_class=User,
                    readable_column_names=["id", "name", "email"],
                    writeable_column_names=["name", "email"],
                    searchable_column_names=["name", "email"],
                    sortable_column_names=["name"],
                    default_sort_column_name="name",
                ),
                clearskies.endpoints.RestfulApi(
                    url="orders",
                    model_class=Order,
                    readable_column_names=["id", "user_id", "total", "status"],
                    writeable_column_names=["user_id", "status"],
                    searchable_column_names=["user_id", "status"],
                    sortable_column_names=["total"],
                    default_sort_column_name="total",
                ),
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
                raise clearskies.exceptions.InputErrors({"user_id": "Required"})

            user = users.find(f"id={user_id}")
            if not user:
                raise clearskies.exceptions.NotFound("User not found")

            return {"user": user.to_dict()}
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
                raise clearskies.exceptions.InputErrors(errors)

            # Then process
            product = products.find(f"id={body['product_id']}")
            if not product:
                raise clearskies.exceptions.NotFound("Product not found")

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
            maximum_limit=100,
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
            readable_column_names=["id", "name", "email"],
            writeable_column_names=["name", "email"],
            searchable_column_names=["name", "email"],
            sortable_column_names=["name"],
            default_sort_column_name="name",
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
            writeable_column_names=["name", "email"],
            searchable_column_names=["name", "email"],
            sortable_column_names=["name"],
            default_sort_column_name="name",
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

            # exceptions.InputErrors raised by the service become an input_errors response
            order = order_service.create_order(user_id, body["items"])
            return {"order_id": order.id}
        ```
    """),
    "exceptions": textwrap.dedent("""\
        # Exception Hierarchy in clearskies

        clearskies defines a small set of exceptions in `clearskies.exceptions`.
        Raise them from your code and the endpoint turns them into HTTP responses.

        **There is no common base class**: every one subclasses plain `Exception`.

        ## Available Exceptions

        | Exception | Raise it when | Endpoint response |
        |-----------|---------------|-------------------|
        | `ClientError` | The request is bad | 400, `status: "client_error"`, `error: str(e)` |
        | `InputErrors(errors)` | Fields are invalid | **200**, `status: "input_errors"`, `input_errors: errors` |
        | `Authentication` | The caller is not authenticated | 401, `status: "client_error"` |
        | `Authorization` | The caller may not do this | 403, `status: "client_error"` |
        | `NotFound` | A record or resource is missing | 404, `status: "client_error"` |
        | `MovedPermanently(location)` | The resource moved | 302, `status: "redirect"` |
        | `MovedTemporarily(location)` | The resource moved for now | 307, `status: "redirect"` |
        | `MissingDependency` | (Raised by the DI container) | Not caught: propagates |

        Notes:

        - `InputErrors` takes a dict of `{field_name: message}`, stored on `e.errors`.
        - Endpoints catch `ClientError` and `InputErrors` only around request handling;
          the other five are also caught during the authentication/authorization step.
        - In 2.1.14 the redirect response body does not include the location, and
          no `Location` header is set.
        - `MissingDependency` is raised when the DI container cannot build a
          requested name (no class, binding, or dependency is configured).
        - Contexts also catch everything above except `InputErrors` and
          `MissingDependency`, with plain-text responses and the same status codes.

        ## Raising Exceptions in Endpoints

        ```python
        from clearskies import exceptions

        def create_user(request_data, users):
            if not request_data.get("email"):
                raise exceptions.InputErrors({"email": "Email is required"})

            if users.find(f"email={request_data['email']}"):
                raise exceptions.ClientError("A user with that email already exists")

            user = users.create(request_data)
            return {"id": user.id}

        def get_user(routing_data, users):
            user = users.find(f"id={routing_data['id']}")
            if not user:
                raise exceptions.NotFound("User not found")
            return {"id": user.id, "email": user.email}
        ```

        ## Catching Exceptions in Your Own Code

        ```python
        from clearskies import exceptions

        try:
            user_service.deactivate(user_id)
        except exceptions.NotFound:
            ...  # record already gone
        except (exceptions.Authentication, exceptions.Authorization):
            ...  # auth problem
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
            readable_column_names=["id", "name", "email"],
            writeable_column_names=["name", "email"],
            searchable_column_names=["name", "email"],
            sortable_column_names=["name"],
            default_sort_column_name="name",
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
            readable_column_names=["id", "user_id", "total", "status"],
            writeable_column_names=["status"],
            searchable_column_names=["user_id", "status"],
            sortable_column_names=["total"],
            default_sort_column_name="total",
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
                raise clearskies.exceptions.Authorization("Forbidden")

            # Admin-only logic
            return {"admin": True}
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
                    raise clearskies.exceptions.Authorization("No tenant context")
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
        auth = clearskies.authentication.Jwks(
            jwks_url="https://auth.example.com/.well-known/jwks.json",
        )

        # 2. Define model with authorization
        class Order(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = clearskies.columns.Uuid()
            user_id = clearskies.columns.String()
            total = clearskies.columns.Float()
            status = clearskies.columns.String()

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
            searchable_column_names=["status"],
            sortable_column_names=["total"],
            default_sort_column_name="total",
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
