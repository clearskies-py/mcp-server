"""
Reference material concept explanations for clearskies framework.

This module contains detailed reference documentation including column parameters,
endpoint parameters, performance guide, and common patterns cookbook.
"""

import textwrap

REFERENCE_CONCEPTS = {
    "column_reference": textwrap.dedent("""\
        # Column Parameter Reference

        Complete reference for all clearskies column types and their parameters.

        ## Common Parameters (All Columns)

        | Parameter | Type | Default | Description |
        |-----------|------|---------|-------------|
        | `validators` | list | `[]` | List of validator instances |
        | `is_readable` | bool | `True` | Include in API responses |
        | `is_writeable` | bool | `True` | Allow setting via API |
        | `is_searchable` | bool | `False` | Allow searching by this column |
        | `is_sortable` | bool | `False` | Allow sorting by this column |
        | `is_required` | bool | `False` | Require value on create |
        | `default` | any | `None` | Default value if not provided |

        ## String Columns

        ### String

        ```python
        columns.String(
            max_length=255,        # Maximum string length
            min_length=0,          # Minimum string length
            validators=[],         # Additional validators
        )
        ```

        ### Email

        ```python
        columns.Email(
            max_length=255,        # Maximum length
            validators=[],         # Additional validators (email format auto-validated)
        )
        ```

        ### Phone

        ```python
        columns.Phone(
            max_length=50,         # Maximum length
            validators=[],         # Phone format auto-validated
        )
        ```

        ## Numeric Columns

        ### Integer

        ```python
        columns.Integer(
            min_value=None,        # Minimum allowed value
            max_value=None,        # Maximum allowed value
            validators=[],
        )
        ```

        ### Float

        ```python
        columns.Float(
            min_value=None,        # Minimum allowed value
            max_value=None,        # Maximum allowed value
            precision=None,        # Decimal precision
            validators=[],
        )
        ```

        ## Boolean Column

        ```python
        columns.Boolean(
            default=False,         # Default value
            validators=[],
        )
        ```

        ## Date/Time Columns

        ### Datetime

        ```python
        columns.Datetime(
            format="%Y-%m-%d %H:%M:%S",  # Date format
            validators=[],
        )
        ```

        ### Date

        ```python
        columns.Date(
            format="%Y-%m-%d",     # Date format
            validators=[],
        )
        ```

        ### Timestamp

        ```python
        columns.Timestamp(
            # Unix timestamp (automatically converted to/from datetime)
        )
        ```

        ### Created

        Auto-set to current UTC time on create:

        ```python
        columns.Created(
            # No parameters - automatically set on create
        )
        ```

        ### Updated

        Auto-set to current UTC time on every save:

        ```python
        columns.Updated(
            # No parameters - automatically set on save
        )
        ```

        ## ID Columns

        ### Uuid

        ```python
        columns.Uuid(
            # Auto-generates UUID on create
        )
        ```

        ### Integer (for auto-increment)

        For auto-incrementing integer IDs, use `columns.Integer` with your database's
        auto-increment feature. clearskies will automatically detect and use the
        database-generated ID.

        ```python
        id = columns.Integer()
        # Table should have AUTO_INCREMENT (MySQL) or SERIAL (PostgreSQL)
        ```

        ## Selection Columns

        ### Select

        ```python
        columns.Select(
            values=["option1", "option2", "option3"],  # Allowed values
            validators=[],
        )
        ```

        ## Relationship Columns

        ### BelongsToId

        Foreign key to parent model:

        ```python
        columns.BelongsToId(
            parent_model_class=User,       # Parent model class or string
            parent_column_name="id",       # Parent's ID column
            readable_name="user_id",       # API field name
        )
        ```

        ### BelongsToModel

        Access parent model instance:

        ```python
        columns.BelongsToModel(
            parent_model_class=User,       # Parent model class or string
            readable_name="user",          # API field name
        )
        ```

        ### HasMany

        One-to-many relationship:

        ```python
        columns.HasMany(
            related_model_class=Order,     # Related model class or string
            foreign_key_column_name="user_id",  # FK column in related model
            readable_name="orders",        # API field name
        )
        ```

        ### HasOne

        One-to-one relationship:

        ```python
        columns.HasOne(
            related_model_class=Profile,   # Related model class or string
            foreign_key_column_name="user_id",  # FK column in related model
            readable_name="profile",       # API field name
        )
        ```

        ### ManyToManyIds

        Many-to-many relationship returning IDs:

        ```python
        columns.ManyToManyIds(
            related_model_class=Tag,
            pivot_table="article_tags",    # Pivot table name
            local_key="article_id",        # Local FK in pivot
            foreign_key="tag_id",          # Foreign FK in pivot
            readable_name="tag_ids",
        )
        ```

        ### ManyToManyModels

        Many-to-many relationship returning model instances:

        ```python
        columns.ManyToManyModels(
            related_model_class=Tag,
            pivot_table="article_tags",    # Pivot table name
            local_key="article_id",        # Local FK in pivot
            foreign_key="tag_id",          # Foreign FK in pivot
            readable_name="tags",
        )
        ```

        ### ManyToManyPivots

        Many-to-many relationship with full pivot table access:

        ```python
        columns.ManyToManyPivots(
            related_model_class=Tag,
            pivot_table="article_tags",    # Pivot table name
            local_key="article_id",        # Local FK in pivot
            foreign_key="tag_id",          # Foreign FK in pivot
            readable_name="article_tags",
        )
        ```

        ### ManyToManyIdsWithData

        Many-to-many relationship with pivot data:

        ```python
        columns.ManyToManyIdsWithData(
            related_model_class=Product,
            pivot_table="order_products",
            local_key="order_id",
            foreign_key="product_id",
            pivot_columns=["quantity", "price"],  # Extra pivot columns
            readable_name="products",
        )
        ```

        ## JSON Columns

        ### Json

        ```python
        columns.Json(
            schema=None,           # Optional JSON schema for validation
            validators=[],
        )
        ```

        ## Special Columns

        ### Audit

        Track changes to model:

        ```python
        columns.Audit(
            tracked_columns=["name", "email", "status"],  # Columns to track
        )
        ```

        ### CategoryTree

        Hierarchical data (parent reference):

        ```python
        columns.CategoryTree(
            parent_column_name="parent_id",  # Column storing parent ID
        )
        ```

        ### CategoryTreeAncestors

        Get all ancestors:

        ```python
        columns.CategoryTreeAncestors(
            parent_column_name="parent_id",
        )
        ```

        ### CategoryTreeDescendants

        Get all descendants:

        ```python
        columns.CategoryTreeDescendants(
            parent_column_name="parent_id",
        )
        ```
    """),
    "endpoint_reference": textwrap.dedent("""\
        # Endpoint Parameter Reference

        Complete reference for all clearskies endpoint types and their parameters.

        ## Common Parameters (All Endpoints)

        | Parameter | Type | Default | Description |
        |-----------|------|---------|-------------|
        | `url` | str | `""` | URL path for the endpoint |
        | `authentication` | Authentication | `None` | Authentication handler |
        | `authorization` | Authorization | `None` | Authorization handler |

        ## RestfulApi

        Full CRUD REST API for a model:

        ```python
        clearskies.endpoints.RestfulApi(
            model_class=User,                    # Required: Model class
            url="users",                         # URL path
            readable_column_names=["id", "name", "email"],  # Columns in responses
            writeable_column_names=["name", "email"],       # Columns client can set
            searchable_column_names=["name", "email"],      # Columns for search
            sortable_column_names=["name", "created_at"],   # Columns for sorting
            default_sort_column_name="name",     # Default sort column
            default_sort_direction="asc",        # "asc" or "desc"
            default_limit=20,                    # Default page size
            max_limit=100,                       # Maximum page size
            id_column_name="id",                 # ID column for routes
            authentication=None,                 # Authentication handler
        )
        ```

        **Generated Routes:**
        - `GET /users` - List all users
        - `GET /users/{id}` - Get single user
        - `POST /users` - Create user
        - `PUT /users/{id}` - Update user
        - `DELETE /users/{id}` - Delete user

        ## List

        Read-only list endpoint:

        ```python
        clearskies.endpoints.List(
            model_class=User,
            url="users",
            readable_column_names=["id", "name", "email"],
            searchable_column_names=["name", "email"],
            sortable_column_names=["name", "created_at"],
            default_sort_column_name="name",
            default_sort_direction="asc",
            default_limit=20,
            max_limit=100,
            authentication=None,
        )
        ```

        **Generated Routes:**
        - `GET /users` - List all users

        ## Get

        Single record retrieval:

        ```python
        clearskies.endpoints.Get(
            model_class=User,
            url="users/{id}",
            readable_column_names=["id", "name", "email"],
            id_column_name="id",
            authentication=None,
        )
        ```

        **Generated Routes:**
        - `GET /users/{id}` - Get single user

        ## Create

        Create new records:

        ```python
        clearskies.endpoints.Create(
            model_class=User,
            url="users",
            readable_column_names=["id", "name", "email"],
            writeable_column_names=["name", "email"],
            authentication=None,
        )
        ```

        **Generated Routes:**
        - `POST /users` - Create user

        ## Update

        Update existing records:

        ```python
        clearskies.endpoints.Update(
            model_class=User,
            url="users/{id}",
            readable_column_names=["id", "name", "email"],
            writeable_column_names=["name", "email"],
            id_column_name="id",
            authentication=None,
        )
        ```

        **Generated Routes:**
        - `PUT /users/{id}` - Update user

        ## Delete

        Delete records:

        ```python
        clearskies.endpoints.Delete(
            model_class=User,
            url="users/{id}",
            id_column_name="id",
            authentication=None,
        )
        ```

        **Generated Routes:**
        - `DELETE /users/{id}` - Delete user

        ## Callable

        Custom function endpoint:

        ```python
        def my_handler(input_output, users, authorization_data):
            body = input_output.get_body()
            # Custom logic
            return input_output.success({"result": "ok"})

        clearskies.endpoints.Callable(
            handler=my_handler,
            url="custom",
            methods=["POST"],                    # HTTP methods
            authentication=None,
        )
        ```

        **Generated Routes:**
        - `POST /custom` - Custom handler

        ## EndpointGroup

        Group multiple endpoints:

        ```python
        clearskies.endpoints.EndpointGroup(
            url="api/v1",                        # Base URL for group
            endpoints=[
                clearskies.endpoints.RestfulApi(url="users", model_class=User),
                clearskies.endpoints.RestfulApi(url="orders", model_class=Order),
            ],
            authentication=None,                 # Shared authentication
        )
        ```

        **Generated Routes:**
        - `GET /api/v1/users` - List users
        - `GET /api/v1/orders` - List orders
        - etc.

        ## Mygrations

        Database migration endpoint:

        ```python
        clearskies.endpoints.Mygrations(
            url="migrate",
            models=[User, Order, Product],       # Models to migrate
            authentication=None,
        )
        ```

        ## Query Parameters

        Standard query parameters for list endpoints:

        | Parameter | Description | Example |
        |-----------|-------------|---------|
        | `search` | Search term | `?search=alice` |
        | `sort` | Sort column | `?sort=name` |
        | `direction` | Sort direction | `?direction=desc` |
        | `limit` | Page size | `?limit=20` |
        | `start` | Offset | `?start=40` |
        | `{column}` | Filter by column | `?status=active` |
    """),
    "performance": textwrap.dedent("""\
        # Performance Guide for clearskies

        Best practices for building high-performance clearskies applications.

        ## Database Performance

        ### Use Indexes

        Add indexes for frequently queried columns:

        ```sql
        -- Index for filtering
        CREATE INDEX idx_users_status ON users(status);

        -- Index for sorting
        CREATE INDEX idx_users_created_at ON users(created_at);

        -- Composite index for common queries
        CREATE INDEX idx_orders_user_status ON orders(user_id, status);

        -- Index for foreign keys
        CREATE INDEX idx_orders_user_id ON orders(user_id);
        ```

        ### Limit Query Results

        Always use pagination:

        ```python
        # ✅ Good - limited results
        users = users_model.where("status=active").limit(20)

        # ❌ Bad - loads all records
        users = list(users_model.where("status=active"))
        ```

        ### Use Count Efficiently

        ```python
        # ✅ Efficient count
        count = users_model.where("status=active").count()

        # ❌ Inefficient - loads all records
        count = len(list(users_model.where("status=active")))
        ```

        ### Avoid N+1 Queries

        ```python
        # ❌ N+1 queries
        orders = list(orders_model.where("status=pending"))
        for order in orders:
            print(order.user.name)  # Query per order!

        # ✅ Batch load
        orders = list(orders_model.where("status=pending"))
        user_ids = [o.user_id for o in orders]
        users = {u.id: u for u in users_model.where(f"id in {','.join(user_ids)}")}
        for order in orders:
            print(users.get(order.user_id).name)
        ```

        ### Use Streaming for Large Results

        ```python
        # ✅ Memory efficient - streaming
        for user in users_model.where("status=active"):
            process(user)

        # ❌ Memory intensive - loads all
        all_users = list(users_model.where("status=active"))
        for user in all_users:
            process(user)
        ```

        ## API Performance

        ### Limit Response Size

        ```python
        # ✅ Only return needed columns
        endpoint = clearskies.endpoints.RestfulApi(
            model_class=User,
            readable_column_names=["id", "name", "email"],  # Minimal
        )

        # ❌ Don't return everything
        endpoint = clearskies.endpoints.RestfulApi(
            model_class=User,
            readable_column_names=["id", "name", "email", "bio", "avatar", ...],
        )
        ```

        ### Use Pagination

        ```python
        endpoint = clearskies.endpoints.List(
            model_class=User,
            default_limit=20,    # Reasonable default
            max_limit=100,       # Prevent abuse
        )
        ```

        ### Cache Expensive Operations

        ```python
        import functools

        @functools.lru_cache(maxsize=100)
        def get_user_stats(user_id):
            # Expensive calculation
            return calculate_stats(user_id)
        ```

        ## Memory Management

        ### Don't Hold References

        ```python
        # ✅ Process and discard
        for user in users_model:
            process(user)
            # user can be garbage collected

        # ❌ Holding all references
        all_users = list(users_model)
        for user in all_users:
            process(user)
        # all_users still in memory
        ```

        ### Use Generators

        ```python
        # ✅ Generator - memory efficient
        def process_users():
            for user in users_model.where("status=active"):
                yield process(user)

        # ❌ List - memory intensive
        def process_users():
            return [process(user) for user in users_model.where("status=active")]
        ```

        ## Connection Management

        ### Reuse Connections

        ```python
        # ✅ Connection pool
        pool = create_connection_pool(max_connections=10)

        def get_cursor():
            return pool.get_connection().cursor()

        # ❌ New connection per request
        def get_cursor():
            return pymysql.connect(...).cursor()
        ```

        ### Close Connections

        ```python
        # ✅ Properly close
        connection = pymysql.connect(...)
        try:
            cursor = connection.cursor()
            # ... use cursor ...
        finally:
            connection.close()

        # Or use context manager
        with pymysql.connect(...) as connection:
            cursor = connection.cursor()
            # ... use cursor ...
        ```

        ## Profiling

        ### Enable Query Logging

        ```python
        import logging
        import time

        logging.getLogger('clearskies').setLevel(logging.DEBUG)

        # Log slow queries
        class SlowQueryLogger:
            def __init__(self, threshold_ms=100):
                self.threshold = threshold_ms

            def log_query(self, sql, duration_ms):
                if duration_ms > self.threshold:
                    logging.warning(f"Slow query ({duration_ms}ms): {sql}")
        ```

        ### Measure Endpoint Performance

        ```python
        import time

        def timed_endpoint(input_output, users):
            start = time.time()

            # Your logic
            result = users.where("status=active").limit(20)

            duration = (time.time() - start) * 1000
            logging.info(f"Endpoint took {duration:.2f}ms")

            return input_output.success({"users": list(result)})
        ```

        ## Checklist

        - [ ] Add database indexes for filtered/sorted columns
        - [ ] Use pagination for all list endpoints
        - [ ] Limit readable columns to what's needed
        - [ ] Avoid N+1 queries with batch loading
        - [ ] Use streaming for large result sets
        - [ ] Implement connection pooling
        - [ ] Monitor slow queries
        - [ ] Profile endpoint performance
    """),
    "patterns": textwrap.dedent("""\
        # Common Patterns Cookbook

        Ready-to-use patterns for common clearskies use cases.

        ## Multi-Tenant Application

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
            email = columns.Email()
        ```

        ## Soft Delete

        ```python
        class SoftDeleteModel(clearskies.Model):
            '''Base model with soft delete support.'''

            deleted_at = columns.Datetime(is_readable=False)

            def where_for_request(
                self,
                model,
                input_output,
                routing_data,
                authorization_data,
                overrides={},
            ):
                # Only show non-deleted records
                return model.where("deleted_at IS NULL")

            def soft_delete(self):
                self.save({"deleted_at": datetime.utcnow()})

        class User(SoftDeleteModel):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            name = columns.String()
        ```

        ## Audit Trail

        ```python
        class AuditedModel(clearskies.Model):
            '''Base model with audit trail.'''

            created_at = columns.Created()
            created_by = columns.String()
            updated_at = columns.Updated()
            updated_by = columns.String()

            def pre_save(self, data):
                user_id = self._get_current_user_id()
                if not self.exists:
                    data["created_by"] = user_id
                data["updated_by"] = user_id
                return data

            def _get_current_user_id(self):
                # Get from request context
                return "system"
        ```

        ## Slug Generation

        ```python
        import re

        class SlugModel(clearskies.Model):
            '''Base model with automatic slug generation.'''

            name = columns.String()
            slug = columns.String()

            def pre_save(self, data):
                if "name" in data and not data.get("slug"):
                    data["slug"] = self._generate_slug(data["name"])
                return data

            def _generate_slug(self, name):
                slug = name.lower()
                slug = re.sub(r'[^a-z0-9]+', '-', slug)
                slug = slug.strip('-')
                return slug
        ```

        ## Versioned Records

        ```python
        class VersionedModel(clearskies.Model):
            '''Base model with version tracking.'''

            version = columns.Integer(default=1)

            def pre_save(self, data):
                if self.exists:
                    data["version"] = self.version + 1
                return data

            def save_with_optimistic_lock(self, data, expected_version):
                if self.version != expected_version:
                    raise ConcurrencyError("Record was modified")
                return self.save(data)
        ```

        ## Status State Machine

        ```python
        class OrderStatus:
            PENDING = "pending"
            PROCESSING = "processing"
            SHIPPED = "shipped"
            DELIVERED = "delivered"
            CANCELLED = "cancelled"

        class Order(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            status = columns.Select(
                values=[
                    OrderStatus.PENDING,
                    OrderStatus.PROCESSING,
                    OrderStatus.SHIPPED,
                    OrderStatus.DELIVERED,
                    OrderStatus.CANCELLED,
                ],
                default=OrderStatus.PENDING,
            )

            TRANSITIONS = {
                OrderStatus.PENDING: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
                OrderStatus.PROCESSING: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
                OrderStatus.SHIPPED: [OrderStatus.DELIVERED],
                OrderStatus.DELIVERED: [],
                OrderStatus.CANCELLED: [],
            }

            def transition_to(self, new_status):
                allowed = self.TRANSITIONS.get(self.status, [])
                if new_status not in allowed:
                    raise ValueError(f"Cannot transition from {self.status} to {new_status}")
                self.save({"status": new_status})
        ```

        ## Search with Multiple Fields

        ```python
        def search_users(input_output, users):
            search = input_output.get_query_parameter("q", "")

            if not search:
                return input_output.success({"users": []})

            # Search multiple fields
            query = users.where(
                f"name LIKE '%{search}%' OR email LIKE '%{search}%'"
            ).limit(20)

            return input_output.success({
                "users": [u.to_dict() for u in query]
            })
        ```

        ## Bulk Operations

        ```python
        def bulk_update_status(input_output, orders):
            body = input_output.get_body()
            order_ids = body.get("order_ids", [])
            new_status = body.get("status")

            if not order_ids or not new_status:
                return input_output.input_errors({
                    "order_ids": "Required",
                    "status": "Required",
                })

            updated = 0
            for order_id in order_ids:
                order = orders.find(f"id={order_id}")
                if order.exists:
                    order.save({"status": new_status})
                    updated += 1

            return input_output.success({"updated": updated})
        ```

        ## Rate Limiting

        ```python
        from collections import defaultdict
        import time

        class RateLimiter:
            def __init__(self, max_requests=100, window_seconds=60):
                self.max_requests = max_requests
                self.window = window_seconds
                self.requests = defaultdict(list)

            def is_allowed(self, client_id):
                now = time.time()
                # Clean old requests
                self.requests[client_id] = [
                    t for t in self.requests[client_id]
                    if now - t < self.window
                ]
                # Check limit
                if len(self.requests[client_id]) >= self.max_requests:
                    return False
                self.requests[client_id].append(now)
                return True

        rate_limiter = RateLimiter()

        def rate_limited_endpoint(input_output, authorization_data):
            client_id = authorization_data.get("user_id", "anonymous")

            if not rate_limiter.is_allowed(client_id):
                return input_output.error("Rate limit exceeded", 429)

            # Your logic here
            return input_output.success({"message": "OK"})
        ```

        ## Webhook Handler

        ```python
        import hmac
        import hashlib

        def webhook_handler(input_output):
            # Verify signature
            signature = input_output.get_header("X-Webhook-Signature")
            body = input_output.get_raw_body()
            secret = os.environ.get("WEBHOOK_SECRET")

            expected = hmac.new(
                secret.encode(),
                body.encode(),
                hashlib.sha256
            ).hexdigest()

            if not hmac.compare_digest(signature, expected):
                return input_output.error("Invalid signature", 401)

            # Process webhook
            data = input_output.get_body()
            event_type = data.get("type")

            if event_type == "order.created":
                handle_order_created(data)
            elif event_type == "order.updated":
                handle_order_updated(data)

            return input_output.success({"received": True})
        ```

        ## Caching Pattern

        ```python
        import functools
        import time

        class SimpleCache:
            def __init__(self, ttl_seconds=300):
                self.cache = {}
                self.ttl = ttl_seconds

            def get(self, key):
                if key in self.cache:
                    value, timestamp = self.cache[key]
                    if time.time() - timestamp < self.ttl:
                        return value
                    del self.cache[key]
                return None

            def set(self, key, value):
                self.cache[key] = (value, time.time())

        cache = SimpleCache(ttl_seconds=60)

        def get_user_with_cache(users, user_id):
            cache_key = f"user:{user_id}"
            cached = cache.get(cache_key)
            if cached:
                return cached

            user = users.find(f"id={user_id}")
            if user.exists:
                cache.set(cache_key, user)
            return user
        ```
    """),
}
