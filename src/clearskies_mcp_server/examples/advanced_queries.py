"""
Example of advanced query patterns in clearskies.

This module demonstrates complex queries including joins, aggregations,
pagination strategies, and query optimization.
"""

import textwrap


def example_advanced_queries() -> str:
    """Complete example of advanced query patterns in clearskies."""
    return textwrap.dedent('''\
        # clearskies Advanced Queries Example

        This example demonstrates advanced query patterns including joins,
        aggregations, pagination strategies, and query optimization.

        ## Complete Example

        ```python
        """
        Advanced queries example with clearskies.

        This script demonstrates:
        - Complex filtering and conditions
        - Joins across multiple tables
        - Pagination strategies (offset vs cursor)
        - Aggregations and grouping
        - Query optimization techniques
        """
        import clearskies
        from clearskies import columns
        from clearskies.validators import Required
        from datetime import datetime, timedelta


        # =============================================================================
        # MODEL DEFINITIONS
        # =============================================================================

        class User(clearskies.Model):
            """User model for query examples."""
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            email = columns.Email(max_length=255, validators=[Required()])
            name = columns.String(max_length=255, validators=[Required()])
            status = columns.Select(["active", "inactive", "suspended"], default="active")
            country = columns.String(max_length=100)
            created_at = columns.Created()
            last_login = columns.Datetime()


        class Order(clearskies.Model):
            """Order model for query examples."""
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            user_id = columns.BelongsToId(parent_model_class=User)
            order_number = columns.String(max_length=50, validators=[Required()])
            amount = columns.Float(validators=[Required()])
            status = columns.Select(
                ["pending", "confirmed", "shipped", "delivered", "cancelled"],
                default="pending",
            )
            created_at = columns.Created()

            # Relationship
            user = columns.BelongsToModel(
                parent_model_class=User,
                parent_id_column_name="user_id",
            )


        class Product(clearskies.Model):
            """Product model for query examples."""
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            name = columns.String(max_length=255, validators=[Required()])
            category = columns.String(max_length=100)
            price = columns.Float(validators=[Required()])
            stock = columns.Integer(default=0)
            created_at = columns.Created()


        # =============================================================================
        # BASIC QUERY PATTERNS
        # =============================================================================

        def basic_queries():
            """Demonstrate basic query patterns."""
            users = User()

            print("=== Basic Queries ===")

            # Simple equality
            active_users = users.where("status=active")
            print(f"Active users: {active_users.count()}")

            # Comparison operators
            recent_users = users.where("created_at>2024-01-01")
            print(f"Users created in 2024: {recent_users.count()}")

            # IN operator
            target_countries = users.where("country in US,CA,UK")
            print(f"Users in US/CA/UK: {target_countries.count()}")

            # NULL checks
            never_logged_in = users.where("last_login is null")
            print(f"Never logged in: {never_logged_in.count()}")

            has_logged_in = users.where("last_login is not null")
            print(f"Has logged in: {has_logged_in.count()}")

            # LIKE operator
            gmail_users = users.where("email like %@gmail.com")
            print(f"Gmail users: {gmail_users.count()}")

            # Chaining conditions (AND)
            active_us_users = users.where("status=active").where("country=US")
            print(f"Active US users: {active_us_users.count()}")


        # =============================================================================
        # SORTING AND LIMITING
        # =============================================================================

        def sorting_queries():
            """Demonstrate sorting and limiting."""
            users = User()
            orders = Order()

            print("\\n=== Sorting and Limiting ===")

            # Sort ascending
            users_by_name = users.sort_by("name", "asc")
            print("Users sorted by name (A-Z):")
            for user in users_by_name.limit(5):
                print(f"  - {user.name}")

            # Sort descending
            recent_orders = orders.sort_by("created_at", "desc").limit(10)
            print("\\n10 most recent orders:")
            for order in recent_orders:
                print(f"  - {order.order_number}: ${order.amount:.2f}")

            # Multiple sort columns
            users_sorted = users.sort_by("country", "asc").sort_by("name", "asc")
            print("\\nUsers sorted by country, then name:")
            for user in users_sorted.limit(10):
                print(f"  - {user.country}: {user.name}")


        # =============================================================================
        # PAGINATION STRATEGIES
        # =============================================================================

        def offset_pagination():
            """Demonstrate offset-based pagination."""
            users = User()

            print("\\n=== Offset Pagination ===")

            page_size = 10

            # Page 1
            page1 = users.sort_by("created_at", "desc").limit(page_size).pagination(start=0)
            print(f"Page 1: {len(list(page1))} users")

            # Page 2
            page2 = users.sort_by("created_at", "desc").limit(page_size).pagination(start=10)
            print(f"Page 2: {len(list(page2))} users")

            # Page 3
            page3 = users.sort_by("created_at", "desc").limit(page_size).pagination(start=20)
            print(f"Page 3: {len(list(page3))} users")

            # Get all pages at once
            all_users = users.sort_by("created_at", "desc").limit(page_size).paginate_all()
            print(f"Total users (all pages): {len(list(all_users))}")


        def cursor_pagination():
            """Demonstrate cursor-based pagination."""
            users = User()

            print("\\n=== Cursor Pagination ===")

            page_size = 10

            # First page
            results = list(users.sort_by("id", "asc").limit(page_size))
            print(f"First page: {len(results)} users")

            if results:
                # Get cursor (last ID)
                last_id = results[-1].id
                print(f"Cursor: {last_id}")

                # Next page using cursor
                next_page = list(
                    users.where(f"id>{last_id}").sort_by("id", "asc").limit(page_size)
                )
                print(f"Next page: {len(next_page)} users")


        def keyset_pagination():
            """Demonstrate keyset pagination for multi-column sorting."""
            orders = Order()

            print("\\n=== Keyset Pagination ===")

            page_size = 10

            # First page: sort by created_at desc, then id desc for uniqueness
            results = list(
                orders.sort_by("created_at", "desc").sort_by("id", "desc").limit(page_size)
            )
            print(f"First page: {len(results)} orders")

            if results:
                last = results[-1]
                print(f"Last item: created_at={last.created_at}, id={last.id}")

                # Next page: items "before" the last item in sort order
                # This requires a compound condition
                next_page = list(
                    orders.where(
                        f"(created_at<\'{last.created_at}\') OR "
                        f"(created_at=\'{last.created_at}\' AND id<\'{last.id}\')"
                    ).sort_by("created_at", "desc").sort_by("id", "desc").limit(page_size)
                )
                print(f"Next page: {len(next_page)} orders")


        # =============================================================================
        # JOINS
        # =============================================================================

        def join_queries():
            """Demonstrate join queries."""
            orders = Order()

            print("\\n=== Join Queries ===")

            # Join orders with users
            orders_with_users = orders.join(
                "join users on users.id = orders.user_id"
            ).where("users.status=active")

            print("Orders from active users:")
            for order in orders_with_users.limit(5):
                print(f"  - {order.order_number}: ${order.amount:.2f}")

            # Multiple joins
            # orders.join(
            #     "join users on users.id = orders.user_id"
            # ).join(
            #     "join order_items on order_items.order_id = orders.id"
            # ).join(
            #     "join products on products.id = order_items.product_id"
            # ).where("products.category=electronics")

            # Left join to find users without orders
            users = User()
            users_without_orders = users.join(
                "left join orders on orders.user_id = users.id"
            ).where("orders.id is null")

            print("\\nUsers without orders:")
            for user in users_without_orders.limit(5):
                print(f"  - {user.name} ({user.email})")


        # =============================================================================
        # AGGREGATIONS (via backend cursor)
        # =============================================================================

        def aggregation_queries():
            """Demonstrate aggregation queries using raw SQL."""
            print("\\n=== Aggregations ===")

            # Note: For complex aggregations, use the backend cursor directly
            # This example shows the pattern for SQL backends

            # Count
            orders = Order()
            total_orders = orders.count()
            print(f"Total orders: {total_orders}")

            pending_orders = orders.where("status=pending").count()
            print(f"Pending orders: {pending_orders}")

            # For sum, avg, etc. with SQL backends:
            # cursor = backend.cursor()
            # cursor.execute("SELECT SUM(amount) FROM orders WHERE status = \'delivered\'")
            # total_revenue = cursor.fetchone()[0]

            # cursor.execute("SELECT AVG(amount) FROM orders")
            # avg_order_value = cursor.fetchone()[0]

            # cursor.execute("""
            #     SELECT user_id, COUNT(*) as order_count, SUM(amount) as total
            #     FROM orders
            #     GROUP BY user_id
            #     HAVING COUNT(*) > 5
            #     ORDER BY total DESC
            # """)
            # top_customers = cursor.fetchall()


        # =============================================================================
        # QUERY OPTIMIZATION
        # =============================================================================

        def optimized_queries():
            """Demonstrate query optimization techniques."""
            print("\\n=== Query Optimization ===")

            users = User()
            orders = Order()

            # 1. Use specific conditions instead of fetching all
            # Bad: all_users = list(users)
            #      active = [u for u in all_users if u.status == "active"]
            # Good:
            active_users = users.where("status=active")

            # 2. Limit results when you only need a few
            # Bad: all_orders = list(orders)
            #      recent = all_orders[:10]
            # Good:
            recent_orders = orders.sort_by("created_at", "desc").limit(10)

            # 3. Use count() instead of len(list())
            # Bad: count = len(list(users.where("status=active")))
            # Good:
            count = users.where("status=active").count()

            # 4. Batch load related records to avoid N+1
            # Bad:
            # for order in orders:
            #     user = users.find(f"id={order.user_id}")  # N+1 queries!

            # Good: Load all users at once
            order_list = list(orders.limit(100))
            user_ids = [o.user_id for o in order_list]
            if user_ids:
                user_map = {
                    u.id: u
                    for u in users.where(f"id in {','.join(user_ids)}")
                }
                for order in order_list:
                    user = user_map.get(order.user_id)

            # 5. Use exists check instead of count for boolean checks
            # Bad: has_orders = orders.where(f"user_id={user_id}").count() > 0
            # Good:
            # has_orders = orders.where(f"user_id={user_id}").first() is not None

            print("Optimization patterns demonstrated")


        # =============================================================================
        # MAIN
        # =============================================================================

        def main():
            """Run all query examples."""
            # Seed some test data
            seed_test_data()

            # Run examples
            basic_queries()
            sorting_queries()
            offset_pagination()
            cursor_pagination()
            keyset_pagination()
            join_queries()
            aggregation_queries()
            optimized_queries()


        def seed_test_data():
            """Create test data for examples."""
            users = User()
            orders = Order()

            # Create users
            for i in range(50):
                users.create({
                    "email": f"user{i}@example.com",
                    "name": f"User {i}",
                    "status": ["active", "inactive", "suspended"][i % 3],
                    "country": ["US", "CA", "UK", "DE", "FR"][i % 5],
                })

            # Create orders
            user_list = list(users)
            for i in range(100):
                user = user_list[i % len(user_list)]
                orders.create({
                    "user_id": user.id,
                    "order_number": f"ORD-{i:04d}",
                    "amount": 50 + (i * 10) % 500,
                    "status": ["pending", "confirmed", "shipped", "delivered"][i % 4],
                })


        if __name__ == "__main__":
            main()
        ```

        ## Query Patterns Summary

        | Pattern | Use Case | Example |
        |---------|----------|---------|
        | `where("col=val")` | Exact match | `users.where("status=active")` |
        | `where("col>val")` | Comparison | `orders.where("amount>100")` |
        | `where("col in a,b,c")` | Multiple values | `users.where("country in US,CA")` |
        | `where("col is null")` | NULL check | `users.where("last_login is null")` |
        | `where("col like %x")` | Pattern match | `users.where("email like %@gmail.com")` |
        | `sort_by("col", "asc")` | Sorting | `users.sort_by("name", "asc")` |
        | `limit(n)` | Limit results | `orders.limit(10)` |
        | `pagination(start=n)` | Offset pagination | `users.limit(10).pagination(start=20)` |
        | `join("...")` | Table joins | `orders.join("join users on ...")` |
        | `count()` | Count records | `users.where("status=active").count()` |
        | `first()` | Single record | `users.where("email=x").first()` |
        | `find("condition")` | Find one | `users.find("id=uuid")` |

        ## Best Practices

        1. **Index frequently queried columns** - status, foreign keys, dates
        2. **Use cursor pagination for large datasets** - Better performance
        3. **Avoid N+1 queries** - Batch load related records
        4. **Use count() for counting** - Don\'t fetch all records
        5. **Limit results** - Always use limit() when possible
        6. **Profile slow queries** - Enable query logging in development
    ''')
