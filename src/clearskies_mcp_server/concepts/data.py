"""
Data-related concept explanations for clearskies framework.

This module contains explanations for queries, validators, schema, and advanced data patterns.
"""

import textwrap

DATA_CONCEPTS = {
    "query": textwrap.dedent("""\
        # clearskies Queries

        Models provide a fluent query interface for fetching records.

        ## Conditions

        ```python
        # String conditions
        users.where("name=Bob")
        users.where("age>=18")
        users.where("status in pending,approved")
        users.where("email is not null")

        # Type-safe conditions via column methods
        users.where(User.name.equals("Bob"))
        users.where(User.age.greater_than(18))
        ```

        ## Supported Operators
        `=`, `!=`, `<=>`, `<=`, `>=`, `>`, `<`, `in`, `is null`, `is not null`, `like`

        ## Chaining

        ```python
        results = (
            users
            .where("status=active")
            .where("age>=18")
            .sort_by("name", "asc")
            .limit(10)
        )
        for user in results:
            print(user.name)
        ```

        ## Single Record

        ```python
        user = users.find("email=test@example.com")
        # or
        user = users.where("email=test@example.com").first()
        ```

        ## Joins

        ```python
        orders.join("join users on users.id=orders.user_id").where("users.name=Jane")
        ```

        ## Pagination

        ```python
        page = users.sort_by("name", "asc").limit(10).pagination(start=20)
        all_records = users.sort_by("name", "asc").limit(10).paginate_all()
        ```
    """),
    "validator": textwrap.dedent("""\
        # clearskies Validators

        Validators enforce constraints on column values during create/update operations.

        ## Built-in Validators

        - **Required** – Value must be provided and non-empty
        - **Unique** – Value must be unique across all records
        - **InTheFuture** – Date/datetime must be in the future
        - **InThePast** – Date/datetime must be in the past
        - **Timedelta** – Date/datetime must be within a time range

        ## Usage

        ```python
        from clearskies.validators import Required, Unique

        class User(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = clearskies.columns.Uuid()
            name = clearskies.columns.String(validators=[Required()])
            email = clearskies.columns.Email(validators=[Required(), Unique()])
        ```

        ## Custom Validators

        You can create custom validators by extending `clearskies.Validator`.
    """),
    "schema": textwrap.dedent("""\
        # clearskies Schema

        The Schema class is the base class for Model. It manages column definitions and provides
        methods for introspecting the data structure.

        Schemas provide:
        - Column management (get_columns, get_column)
        - Type validation
        - Serialization/deserialization

        Models extend Schema to add data persistence (save, delete, query) capabilities.
    """),
    "advanced_columns": textwrap.dedent("""\
        # Advanced Column Types in clearskies

        clearskies provides specialized column types for complex data modeling scenarios
        including hierarchical data, audit trails, and many-to-many relationships with
        pivot data.

        ## Hierarchical Data (Category Trees)

        For tree-structured data (categories, organizational hierarchies, nested comments),
        clearskies provides several column types:

        ### CategoryTree

        The base column for hierarchical relationships:

        ```python
        import clearskies
        from clearskies import columns

        class Category(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            name = columns.String(max_length=255)
            parent_id = columns.BelongsToId(parent_model_class="Category")

            # Tree navigation columns
            ancestors = columns.CategoryTreeAncestors(
                parent_id_column_name="parent_id",
            )
            children = columns.CategoryTreeChildren(
                parent_id_column_name="parent_id",
            )
            descendants = columns.CategoryTreeDescendants(
                parent_id_column_name="parent_id",
            )
        ```

        ### CategoryTreeAncestors

        Returns all ancestor records (parent, grandparent, etc.) up to the root:

        ```python
        category = categories.find("id=some-uuid")
        for ancestor in category.ancestors:
            print(f"Ancestor: {ancestor.name}")
        ```

        ### CategoryTreeChildren

        Returns immediate children of a record:

        ```python
        category = categories.find("id=some-uuid")
        for child in category.children:
            print(f"Child: {child.name}")
        ```

        ### CategoryTreeDescendants

        Returns all descendants (children, grandchildren, etc.):

        ```python
        category = categories.find("id=some-uuid")
        for descendant in category.descendants:
            print(f"Descendant: {descendant.name}")
        ```

        ## Audit Trail

        The Audit column automatically tracks changes to records:

        ```python
        import clearskies
        from clearskies import columns

        class Document(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            title = columns.String(max_length=255)
            content = columns.String()
            status = columns.Select(["draft", "published", "archived"])

            # Audit trail - tracks all changes
            audit = columns.Audit(
                audit_columns=["title", "content", "status"],
            )
        ```

        ### Audit Column Configuration

        | Parameter | Type | Description |
        |-----------|------|-------------|
        | `audit_columns` | list | Column names to track changes for |
        | `audit_model_class` | class | Custom audit record model (optional) |

        ### Accessing Audit History

        ```python
        document = documents.find("id=some-uuid")
        for audit_record in document.audit:
            print(f"Changed at: {audit_record.created_at}")
            print(f"Changed by: {audit_record.changed_by}")
            print(f"Old value: {audit_record.old_value}")
            print(f"New value: {audit_record.new_value}")
        ```

        ## Many-to-Many with Pivot Data

        For many-to-many relationships that need additional data on the relationship
        itself (e.g., quantity, role, permissions):

        ### ManyToManyIdsWithData

        Returns IDs along with pivot table data:

        ```python
        import clearskies
        from clearskies import columns

        class Product(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            name = columns.String(max_length=255)
            price = columns.Float()

        class Order(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            customer_name = columns.String(max_length=255)

            # Many-to-many with quantity data
            product_ids_with_data = columns.ManyToManyIdsWithData(
                related_model_class=Product,
                pivot_table="order_products",
                pivot_data_columns=["quantity", "unit_price"],
            )
        ```

        ### ManyToManyPivots

        Access the pivot records directly:

        ```python
        class Order(clearskies.Model):
            # ... other columns ...

            # Access pivot records
            order_products = columns.ManyToManyPivots(
                pivot_model_class=OrderProduct,
            )
        ```

        ### Working with Pivot Data

        ```python
        # Creating with pivot data
        order = orders.create({
            "customer_name": "John Doe",
            "product_ids_with_data": [
                {"id": product1.id, "quantity": 2, "unit_price": 29.99},
                {"id": product2.id, "quantity": 1, "unit_price": 49.99},
            ],
        })

        # Reading pivot data
        for item in order.product_ids_with_data:
            print(f"Product: {item['id']}, Qty: {item['quantity']}")
        ```

        ## Best Practices

        1. **Use CategoryTree for true hierarchies** – Not for simple parent-child
        2. **Audit only important columns** – Don't audit auto-updated timestamps
        3. **Define pivot models explicitly** – For complex pivot data
        4. **Index foreign keys** – Especially for tree traversal queries
        5. **Consider query performance** – Deep trees can be expensive to traverse
    """),
    "advanced_queries": textwrap.dedent("""\
        # Advanced Queries in clearskies

        Beyond basic filtering, clearskies supports complex query patterns including
        joins, aggregations, pagination strategies, and query optimization.

        ## Complex Joins

        ### Basic Join Syntax

        ```python
        # Join orders with users
        orders = order_model.join(
            "join users on users.id = orders.user_id"
        ).where("users.status = active")

        for order in orders:
            print(f"Order {order.id} by user {order.user_id}")
        ```

        ### Multiple Joins

        ```python
        results = orders.join(
            "join users on users.id = orders.user_id"
        ).join(
            "join products on products.id = orders.product_id"
        ).where("users.country = US").where("products.category = electronics")
        ```

        ### Left Joins

        ```python
        # Include users even without orders
        users = user_model.join(
            "left join orders on orders.user_id = users.id"
        ).where("orders.id is null")  # Users with no orders
        ```

        ## Aggregations

        ### Count

        ```python
        # Count all records
        total = users.count()

        # Count with conditions
        active_count = users.where("status = active").count()
        ```

        ### Sum, Avg, Min, Max

        ```python
        # Using raw SQL through the backend
        cursor = backend.cursor()
        cursor.execute("SELECT SUM(amount) FROM orders WHERE status = 'completed'")
        total_revenue = cursor.fetchone()[0]
        ```

        ### Group By (via raw queries)

        For complex aggregations, use the cursor directly:

        ```python
        cursor = backend.cursor()
        cursor.execute('''
            SELECT user_id, COUNT(*) as order_count, SUM(amount) as total
            FROM orders
            GROUP BY user_id
            HAVING COUNT(*) > 5
        ''')
        for row in cursor.fetchall():
            print(f"User {row[0]}: {row[1]} orders, ${row[2]} total")
        ```

        ## Pagination Strategies

        ### Offset-Based Pagination

        Traditional pagination using LIMIT and OFFSET:

        ```python
        # Page 1 (items 1-10)
        page1 = users.sort_by("created_at", "desc").limit(10).pagination(start=0)

        # Page 2 (items 11-20)
        page2 = users.sort_by("created_at", "desc").limit(10).pagination(start=10)

        # Get all pages
        all_users = users.sort_by("created_at", "desc").limit(10).paginate_all()
        ```

        **Pros:** Simple, supports random page access
        **Cons:** Performance degrades with large offsets, inconsistent with concurrent writes

        ### Cursor-Based Pagination

        More efficient for large datasets:

        ```python
        # First page
        results = users.sort_by("id", "asc").limit(10)
        last_id = results[-1].id if results else None

        # Next page (using cursor)
        if last_id:
            next_page = users.where(f"id > {last_id}").sort_by("id", "asc").limit(10)
        ```

        **Pros:** Consistent performance, handles concurrent writes
        **Cons:** No random page access, requires sortable unique column

        ### Keyset Pagination

        For multi-column sorting:

        ```python
        # Sort by created_at, then id for uniqueness
        results = users.sort_by("created_at", "desc").sort_by("id", "desc").limit(10)

        # Next page cursor
        last = results[-1]
        next_page = users.where(
            f"(created_at < '{last.created_at}') OR "
            f"(created_at = '{last.created_at}' AND id < '{last.id}')"
        ).sort_by("created_at", "desc").sort_by("id", "desc").limit(10)
        ```

        ## Query Optimization Tips

        ### 1. Use Indexes

        Ensure columns used in WHERE clauses are indexed:

        ```python
        email = columns.Email(max_length=255, index=True)
        status = columns.Select(["active", "inactive"], index=True)
        ```

        ### 2. Limit Selected Columns

        When you only need specific columns:

        ```python
        # The endpoint's readable_column_names limits what's returned
        endpoint = clearskies.endpoints.List(
            model_class=User,
            readable_column_names=["id", "name"],  # Only fetch these
        )
        ```

        ### 3. Eager Loading for Relationships

        Avoid N+1 queries by loading relationships upfront:

        ```python
        # Instead of loading each user's orders separately
        orders = order_model.where(f"user_id in {','.join(user_ids)}")
        orders_by_user = {}
        for order in orders:
            orders_by_user.setdefault(order.user_id, []).append(order)
        ```

        ### 4. Use Appropriate Pagination

        - Small datasets (< 10,000): Offset pagination is fine
        - Large datasets: Use cursor-based pagination
        - Real-time data: Always use cursor-based

        ### 5. Batch Operations

        For bulk updates/deletes:

        ```python
        # Update multiple records efficiently
        cursor = backend.cursor()
        cursor.execute(
            "UPDATE users SET status = 'inactive' WHERE last_login < %s",
            [cutoff_date]
        )
        ```

        ## Subqueries

        For complex filtering with subqueries, use raw SQL:

        ```python
        cursor = backend.cursor()
        cursor.execute('''
            SELECT * FROM users
            WHERE id IN (
                SELECT user_id FROM orders
                WHERE amount > 1000
                GROUP BY user_id
                HAVING COUNT(*) > 3
            )
        ''')
        ```

        ## Query Debugging

        Enable query logging to see generated SQL:

        ```python
        import logging
        logging.getLogger('clearskies').setLevel(logging.DEBUG)
        ```

        This helps identify slow queries and optimization opportunities.
    """),
}
