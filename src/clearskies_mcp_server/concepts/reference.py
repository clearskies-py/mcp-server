"""
Reference material concept explanations for clearskies framework.

This module contains detailed reference documentation including column parameters,
endpoint parameters, performance guide, and common patterns cookbook.
"""

import textwrap

REFERENCE_CONCEPTS = {
    "column_reference": textwrap.dedent("""\
        # Column Parameter Reference

        Reference for clearskies v2 column types and their constructor parameters.

        ## Common Parameters (Most Columns)

        | Parameter | Type | Default | Description |
        |-----------|------|---------|-------------|
        | `default` | any | `None` | Value used on create when none is provided |
        | `setable` | value/callable | `None` | Value always set on save (overrides user input) |
        | `is_readable` | bool | `True` | Include in API responses |
        | `is_writeable` | bool | `True` | Allow setting via API |
        | `is_searchable` | bool | `True` | Allow searching by this column |
        | `is_temporary` | bool | `False` | Accept/use the value but never persist it |
        | `validators` | validator/list | `[]` | Validator instances |
        | `on_change_pre_save` / `on_change_post_save` / `on_change_save_finished` | action/list | `[]` | Actions run when the value changes |
        | `created_by_source_type` / `created_by_source_key` | str | `""` | Populate from request data (e.g. authorization data) on create |

        There are no `is_required`, `is_sortable`, `max_length`, `min_value`, etc. column
        arguments in v2. Use validators instead:

        ```python
        name = columns.String(validators=[
            clearskies.validators.Required(),
            clearskies.validators.MinimumLength(2),
            clearskies.validators.MaximumLength(255),
        ])
        age = columns.Integer(validators=[
            clearskies.validators.MinimumValue(0),
            clearskies.validators.MaximumValue(150),
        ])
        ```

        Available validators: `Required`, `Unique`, `MinimumLength`, `MaximumLength`,
        `MinimumValue`, `MaximumValue`, `Regexp`, `AfterColumn`, `BeforeColumn`,
        `InTheFuture`, `InThePast` (plus `AtLeast`/`AtMost` variants), `Timedelta`.

        ## String Columns

        ### String

        ```python
        columns.String(validators=[clearskies.validators.MaximumLength(255)])
        ```

        ### Email

        Email format is validated automatically:

        ```python
        columns.Email(validators=[clearskies.validators.Unique()])
        ```

        ### Phone

        Phone format is validated automatically; non-digits are stripped:

        ```python
        columns.Phone(
            usa_only=True,         # Only accept US numbers (default True)
        )
        ```

        ## Numeric Columns

        ### Integer / Float

        Value limits are validators:

        ```python
        columns.Integer(validators=[clearskies.validators.MinimumValue(0)])
        columns.Float(validators=[clearskies.validators.MaximumValue(100.0)])
        ```

        ## Boolean Column

        ```python
        columns.Boolean(
            default=False,
            on_true=[],            # Actions when the value changes to True
            on_false=[],           # Actions when the value changes to False
        )
        ```

        ## Date/Time Columns

        ### Datetime

        ```python
        columns.Datetime(
            date_format="%Y-%m-%d %H:%M:%S",    # Format used by the backend
            backend_default="0000-00-00 00:00:00",
            timezone_aware=True,
            timezone=datetime.timezone.utc,
        )
        ```

        ### Date

        ```python
        columns.Date(
            date_format="%Y-%m-%d",
            backend_default="0000-00-00",
        )
        ```

        ### Timestamp

        Unix timestamp in the backend, datetime in Python:

        ```python
        columns.Timestamp(
            include_microseconds=False,
        )
        ```

        ### Created / Updated

        Auto-set on create / on every save (not writeable):

        ```python
        columns.Created(date_format="%Y-%m-%d %H:%M:%S", in_utc=True)
        columns.Updated(date_format="%Y-%m-%d %H:%M:%S", in_utc=True)
        ```

        ## ID Columns

        ### Uuid

        Auto-generates a UUID on create:

        ```python
        columns.Uuid()
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
            allowed_values=["option1", "option2", "option3"],  # Required
            default="option1",
        )
        ```

        ## Relationship Columns

        Use `clearskies.model.ModelClassReference` subclasses when model classes would
        otherwise cause circular imports.

        ### BelongsToId

        Foreign key to a parent model (the column name should end in `_id`):

        ```python
        user_id = columns.BelongsToId(
            User,                              # parent_model_class (or a ModelClassReference)
            readable_parent_columns=["id", "name"],  # Parent columns returned in API output
            join_type=None,                    # "LEFT" or "INNER" for joins
            where=[],                          # Conditions restricting allowed parents
        )
        ```

        ### BelongsToModel

        Access the parent model instance via an existing BelongsToId column:

        ```python
        user = columns.BelongsToModel("user_id")   # belongs_to_column_name
        ```

        ### HasMany

        One-to-many relationship:

        ```python
        orders = columns.HasMany(
            Order,                             # child_model_class
            foreign_column_name="user_id",     # FK in child (default: <own model>_id)
            readable_child_column_names=["id", "total"],
            where=[],
        )
        ```

        ### HasOne

        One-to-one relationship (same parameters as HasMany):

        ```python
        profile = columns.HasOne(
            Profile,                           # child_model_class
            foreign_column_name="user_id",
            readable_child_column_names=["id", "bio"],
        )
        ```

        ### ManyToManyIds

        Many-to-many relationship via a pivot model, returning related IDs:

        ```python
        tag_ids = columns.ManyToManyIds(
            related_model_class=Tag,
            pivot_model_class=ArticleTag,
            own_column_name_in_pivot="article_id",   # Default derived from model name
            related_column_name_in_pivot="tag_id",   # Default derived from model name
            readable_related_column_names=["id", "name"],
        )
        ```

        ### ManyToManyModels / ManyToManyPivots

        Access the related models or the pivot records via an existing many-to-many column:

        ```python
        tags = columns.ManyToManyModels("tag_ids")          # many_to_many_column_name
        article_tags = columns.ManyToManyPivots("tag_ids")  # many_to_many_column_name
        ```

        ### ManyToManyIdsWithData

        Many-to-many relationship with extra data stored in the pivot model:

        ```python
        product_ids = columns.ManyToManyIdsWithData(
            related_model_class=Product,
            pivot_model_class=OrderProduct,          # Pivot has quantity/price columns
            readable_pivot_column_names=["id", "product_id", "quantity", "price"],
            setable_column_names=["product_id", "quantity", "price"],
        )
        ```

        ## JSON Columns

        ### Json

        ```python
        columns.Json(default={})
        ```

        ## Special Columns

        ### Audit

        Records create/update/delete actions in an audit model (which must have
        `class_name`, `resource_id`, `action`, `data`, and `created_at` columns):

        ```python
        history = columns.Audit(
            audit_model_class=PersonHistory,
            exclude_columns=["updated_at"],    # Columns not recorded
            mask_columns=["password"],         # Recorded but masked
        )
        ```

        ### CategoryTree

        Replacement for a self-referencing BelongsToId that maintains a tree model
        (with `parent_id`, `child_id`, `is_parent`, `level` columns) for fast lookups:

        ```python
        parent_id = columns.CategoryTree(
            CategoryTreeModel,                 # tree_model_class
            tree_parent_id_column_name="parent_id",
            tree_child_id_column_name="child_id",
            tree_is_parent_column_name="is_parent",
            tree_level_column_name="level",
        )
        ```

        ### CategoryTreeChildren / CategoryTreeAncestors / CategoryTreeDescendants

        Read relatives via an existing CategoryTree column:

        ```python
        children = columns.CategoryTreeChildren("parent_id")        # category_tree_column_name
        ancestors = columns.CategoryTreeAncestors("parent_id")
        descendants = columns.CategoryTreeDescendants("parent_id")
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
            readable_column_names=["id", "name", "email"],  # Required: columns in responses
            writeable_column_names=["name", "email"],       # Required: columns client can set
            searchable_column_names=["name", "email"],      # Required: columns for search
            sortable_column_names=["name", "created_at"],   # Required: columns for sorting
            default_sort_column_name="name",     # Required: default sort column
            default_sort_direction="ASC",        # "ASC" or "DESC"
            default_limit=20,                    # Default page size
            maximum_limit=100,                   # Maximum page size
            id_column_name="id",                 # ID column for routes
            authentication=clearskies.authentication.Public(),  # Authentication handler
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
            maximum_limit=100,
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
            return {"result": "ok"}

        clearskies.endpoints.Callable(
            to_call=my_handler,
            url="custom",
            request_methods=["POST"],                  # HTTP methods
            authentication=None,
        )
        ```

        **Generated Routes:**
        - `POST /custom` - Custom handler

        ## EndpointGroup

        Group multiple endpoints:

        ```python
        clearskies.EndpointGroup(
            url="api/v1",                        # Base URL for group
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
                    writeable_column_names=["user_id", "total", "status"],
                    searchable_column_names=["user_id", "status"],
                    sortable_column_names=["total"],
                    default_sort_column_name="total",
                ),
            ],
            authentication=clearskies.authentication.Public(),  # Shared authentication
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
            sql=["./database/"],                 # CREATE TABLE files/dirs (source of truth)
            command="plan",                      # version, check, plan, plan_export, apply
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
            readable_column_names=["id", "name", "email"],  # Minimal,
            writeable_column_names=["name", "email"],
            searchable_column_names=["name", "email"],
            sortable_column_names=["name"],
            default_sort_column_name="name",
        )

        # ❌ Don't return everything
        endpoint = clearskies.endpoints.RestfulApi(
            model_class=User,
            readable_column_names=["id", "name", "email", "bio", "avatar", ...],
            writeable_column_names=["name", "email"],
            searchable_column_names=["name", "email"],
            sortable_column_names=["name"],
            default_sort_column_name="name",
        )
        ```

        ### Use Pagination

        ```python
        endpoint = clearskies.endpoints.List(
            model_class=User,
            default_limit=20,    # Reasonable default
            maximum_limit=100,   # Prevent abuse
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

            return {"users": list(result)}
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
                if not self:
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
                if self:
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
                allowed_values=[
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
                return {"users": []}

            # Search multiple fields
            query = users.where(
                f"name LIKE '%{search}%' OR email LIKE '%{search}%'"
            ).limit(20)

            return {
                "users": [u.to_dict() for u in query]
            }
        ```

        ## Bulk Operations

        ```python
        def bulk_update_status(input_output, orders):
            body = input_output.get_body()
            order_ids = body.get("order_ids", [])
            new_status = body.get("status")

            if not order_ids or not new_status:
                raise clearskies.exceptions.InputErrors({
                    "order_ids": "Required",
                    "status": "Required",
                })

            updated = 0
            for order_id in order_ids:
                order = orders.find(f"id={order_id}")
                if order:
                    order.save({"status": new_status})
                    updated += 1

            return {"updated": updated}
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
                raise clearskies.exceptions.ClientError("Rate limit exceeded")

            # Your logic here
            return {"message": "OK"}
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
                raise clearskies.exceptions.Authentication("Invalid signature")

            # Process webhook
            data = input_output.get_body()
            event_type = data.get("type")

            if event_type == "order.created":
                handle_order_created(data)
            elif event_type == "order.updated":
                handle_order_updated(data)

            return {"received": True}
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
            if user:
                cache.set(cache_key, user)
            return user
        ```
    """),
}
