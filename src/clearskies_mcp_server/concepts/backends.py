"""
Backend concept explanations for clearskies framework.

This module contains detailed explanations of the clearskies backend system,
including MemoryBackend, CursorBackend, cursors, and transactions.
"""

import textwrap

BACKEND_CONCEPTS = {
    "backend_memory": textwrap.dedent("""\
        # MemoryBackend Deep Dive

        The MemoryBackend stores data entirely in memory, making it perfect for testing,
        prototyping, and development. It provides a complete backend implementation without
        requiring any external dependencies.

        ## How It Works

        MemoryBackend maintains an in-memory dictionary structure:
        - Each model class gets its own storage namespace (based on `destination_name`)
        - Records are stored as dictionaries keyed by their ID
        - All operations (create, read, update, delete) work on this dictionary

        ## Basic Usage

        ```python
        import clearskies
        from clearskies import columns

        class User(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            name = columns.String()
            email = columns.Email()
            created_at = columns.Created()
        ```

        ## Key Characteristics

        ### Data Persistence
        - **Non-persistent**: Data exists only for the lifetime of the process
        - **Process-isolated**: Each process has its own data store
        - **No disk I/O**: All operations are in-memory

        ### Thread Safety
        - MemoryBackend is **not thread-safe** by default
        - For multi-threaded applications, use proper synchronization
        - For production multi-threaded apps, use CursorBackend instead

        ### Performance
        - **O(1)** lookups by ID
        - **O(n)** for queries with conditions (scans all records)
        - No indexing support (all queries are full scans)
        - Excellent for small datasets and testing

        ## When to Use MemoryBackend

        ✅ **Good for:**
        - Unit testing models and business logic
        - Prototyping and development
        - Small datasets that fit in memory
        - CLI tools with ephemeral data
        - Examples and documentation

        ❌ **Not suitable for:**
        - Production applications with persistent data
        - Large datasets (memory constraints)
        - Multi-process applications (data not shared)
        - Applications requiring data durability

        ## Testing with MemoryBackend

        MemoryBackend is ideal for testing because it requires no setup:

        ```python
        import pytest
        import clearskies
        from clearskies import columns

        class User(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            name = columns.String()
            email = columns.Email()

        def test_create_user():
            # Each test gets a fresh MemoryBackend
            users = User()

            # Create a user
            user = users.create({"name": "Alice", "email": "alice@example.com"})

            # Verify
            assert user.name == "Alice"
            assert user.email == "alice@example.com"
            assert user.id is not None

        def test_query_users():
            users = User()

            # Create test data
            users.create({"name": "Alice", "email": "alice@example.com"})
            users.create({"name": "Bob", "email": "bob@example.com"})

            # Query
            results = list(users.where("name=Alice"))
            assert len(results) == 1
            assert results[0].name == "Alice"

        def test_update_user():
            users = User()
            user = users.create({"name": "Alice", "email": "alice@example.com"})

            # Update
            user.save({"name": "Alice Smith"})

            # Verify
            updated = users.find(f"id={user.id}")
            assert updated.name == "Alice Smith"

        def test_delete_user():
            users = User()
            user = users.create({"name": "Alice", "email": "alice@example.com"})
            user_id = user.id

            # Delete
            user.delete()

            # Verify
            result = users.find(f"id={user_id}")
            assert result.exists is False
        ```

        ## Clearing Data Between Tests

        For test isolation, you can clear the backend:

        ```python
        import pytest

        @pytest.fixture(autouse=True)
        def clear_memory_backend():
            # Setup: nothing needed
            yield
            # Teardown: clear the backend
            User.backend.clear()
        ```

        ## Sharing Data Across Models

        Multiple models can share the same MemoryBackend instance:

        ```python
        # Shared backend instance
        shared_backend = clearskies.backends.MemoryBackend()

        class User(clearskies.Model):
            id_column_name = "id"
            backend = shared_backend
            id = columns.Uuid()
            name = columns.String()

        class Order(clearskies.Model):
            id_column_name = "id"
            backend = shared_backend
            id = columns.Uuid()
            user_id = columns.BelongsToId(parent_model_class=User)
            total = columns.Float()
        ```

        ## Limitations

        1. **No SQL support**: Cannot use raw SQL queries
        2. **No transactions**: All operations are immediate
        3. **No constraints**: Foreign keys not enforced at backend level
        4. **No indexes**: All queries scan all records
        5. **No persistence**: Data lost on process exit

        ## Memory Considerations

        For large datasets, be aware of memory usage:

        ```python
        # Each record consumes memory
        users = User()
        for i in range(100000):
            users.create({"name": f"User {i}", "email": f"user{i}@example.com"})

        # Memory usage grows linearly with record count
        # Consider using CursorBackend for large datasets
        ```

        ## Best Practices

        1. **Use for testing**: MemoryBackend is perfect for unit tests
        2. **Clear between tests**: Ensure test isolation
        3. **Don't use in production**: Use CursorBackend or ApiBackend
        4. **Keep datasets small**: Memory is limited
        5. **Share backends carefully**: Consider isolation requirements
    """),
    "backend_cursor": textwrap.dedent("""\
        # CursorBackend Deep Dive

        The CursorBackend connects clearskies models to SQL databases (MySQL, PostgreSQL,
        SQLite, etc.) using Python's DB-API 2.0 cursor interface. It's the primary backend
        for production applications.

        ## How It Works

        CursorBackend:
        1. Receives a database cursor (or connection) via dependency injection
        2. Translates model operations into SQL queries
        3. Executes queries through the cursor
        4. Maps results back to model instances

        ## Basic Usage

        ```python
        import clearskies
        from clearskies import columns

        class User(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            name = columns.String(max_length=255)
            email = columns.Email(max_length=255)
            created_at = columns.Created()
            updated_at = columns.Updated()
        ```

        ## Connection Configuration

        ### Via Environment Variable

        ```python
        class User(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend(
                connection_string_environment_key="DATABASE_URL",
            )
            # ...
        ```

        ### Via Dependency Injection

        The cursor is typically injected via the context:

        ```python
        import clearskies
        import pymysql

        # Create connection
        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="password",
            database="myapp",
            cursorclass=pymysql.cursors.DictCursor,
        )

        # Register with context
        wsgi = clearskies.contexts.WsgiRef(
            clearskies.endpoints.RestfulApi(
                model_class=User,
                # ...
            ),
            bindings={
                "cursor": connection.cursor(),
            },
        )
        ```

        ### Via Connection Pool

        For production, use connection pooling:

        ```python
        import clearskies
        from sqlalchemy import create_engine
        from sqlalchemy.pool import QueuePool

        # Create engine with connection pool
        engine = create_engine(
            "mysql+pymysql://user:pass@localhost/myapp",
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
        )

        # Get connection from pool
        def get_cursor():
            connection = engine.connect()
            return connection

        wsgi = clearskies.contexts.WsgiRef(
            my_endpoint,
            bindings={
                "cursor": get_cursor,  # Factory function
            },
        )
        ```

        ## SQL Generation

        CursorBackend generates SQL for all operations:

        ### SELECT Queries

        ```python
        # Simple query
        users.where("status=active")
        # SQL: SELECT * FROM users WHERE status = 'active'

        # Multiple conditions
        users.where("status=active").where("age>=18")
        # SQL: SELECT * FROM users WHERE status = 'active' AND age >= 18

        # Sorting and limiting
        users.sort_by("name", "asc").limit(10)
        # SQL: SELECT * FROM users ORDER BY name ASC LIMIT 10

        # Pagination
        users.sort_by("name", "asc").limit(10).pagination(start=20)
        # SQL: SELECT * FROM users ORDER BY name ASC LIMIT 10 OFFSET 20
        ```

        ### INSERT Queries

        ```python
        users.create({"name": "Alice", "email": "alice@example.com"})
        # SQL: INSERT INTO users (id, name, email, created_at) VALUES (?, ?, ?, ?)
        ```

        ### UPDATE Queries

        ```python
        user.save({"name": "Alice Smith"})
        # SQL: UPDATE users SET name = ?, updated_at = ? WHERE id = ?
        ```

        ### DELETE Queries

        ```python
        user.delete()
        # SQL: DELETE FROM users WHERE id = ?
        ```

        ## Parameterized Queries

        CursorBackend always uses parameterized queries to prevent SQL injection:

        ```python
        # Safe - uses parameterized query
        users.where("email=alice@example.com")
        # SQL: SELECT * FROM users WHERE email = ?
        # Params: ['alice@example.com']

        # The value is never interpolated into the SQL string
        ```

        ## Table Naming

        By default, the table name is derived from the model class name:

        ```python
        class User(clearskies.Model):
            # Table name: "users" (lowercase, pluralized)
            pass

        class OrderProduct(clearskies.Model):
            # Table name: "order_products" (snake_case, pluralized)
            pass
        ```

        Override with `destination_name`:

        ```python
        class User(clearskies.Model):
            destination_name = "app_users"  # Custom table name
            # ...
        ```

        ## Column Mapping

        Column names map directly to database columns:

        ```python
        class User(clearskies.Model):
            id = columns.Uuid()           # Column: id
            first_name = columns.String() # Column: first_name
            lastName = columns.String()   # Column: lastName (not recommended)
        ```

        ## Database-Specific Features

        ### MySQL

        ```python
        # MySQL-specific connection
        import pymysql

        connection = pymysql.connect(
            host="localhost",
            user="root",
            password="password",
            database="myapp",
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
        ```

        ### PostgreSQL

        ```python
        # PostgreSQL-specific connection
        import psycopg2
        import psycopg2.extras

        connection = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="password",
            database="myapp",
        )
        cursor = connection.cursor(cursor_factory=psycopg2.extras.DictCursor)
        ```

        ### SQLite

        ```python
        # SQLite connection
        import sqlite3

        connection = sqlite3.connect("myapp.db")
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        ```

        ## Error Handling

        CursorBackend propagates database errors:

        ```python
        try:
            users.create({"name": "Alice", "email": "alice@example.com"})
        except pymysql.IntegrityError as e:
            # Handle duplicate key, foreign key violation, etc.
            print(f"Database error: {e}")
        except pymysql.OperationalError as e:
            # Handle connection issues
            print(f"Connection error: {e}")
        ```

        ## Best Practices

        1. **Use connection pooling**: Don't create connections per request
        2. **Use parameterized queries**: CursorBackend does this automatically
        3. **Handle errors gracefully**: Catch database-specific exceptions
        4. **Use transactions**: For multi-step operations (see transactions concept)
        5. **Index frequently queried columns**: Add indexes to your schema
        6. **Use appropriate column types**: Match Python types to SQL types
        7. **Close connections properly**: Use context managers or finally blocks

        ## Performance Tips

        1. **Limit result sets**: Use `.limit()` to avoid loading too many records
        2. **Use pagination**: For large datasets, paginate results
        3. **Index WHERE columns**: Add database indexes for filtered columns
        4. **Avoid N+1 queries**: Load related data efficiently
        5. **Use connection pooling**: Reuse connections across requests
    """),
    "cursors": textwrap.dedent("""\
        # Cursors and Raw SQL in clearskies

        While clearskies provides a high-level query interface, sometimes you need direct
        database access for complex queries, aggregations, or database-specific features.
        This is where cursors come in.

        ## What is a Cursor?

        A cursor is a database object that allows you to:
        - Execute raw SQL queries
        - Iterate over result sets
        - Access database metadata
        - Perform operations not supported by the ORM

        In clearskies, cursors follow Python's DB-API 2.0 specification.

        ## Accessing the Cursor

        ### From the Backend

        ```python
        import clearskies
        from clearskies import columns

        class User(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            name = columns.String()

        # Access cursor from the backend
        cursor = User.backend.cursor()
        ```

        ### Via Dependency Injection

        ```python
        def my_function(cursor):
            # Cursor is injected automatically
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            return {"user_count": count}

        cli = clearskies.contexts.Cli(
            my_function,
            bindings={"cursor": db_cursor},
        )
        ```

        ## Executing Raw SQL

        ### Simple Queries

        ```python
        # Execute a query
        cursor.execute("SELECT * FROM users WHERE status = 'active'")

        # Fetch all results
        rows = cursor.fetchall()
        for row in rows:
            print(row)
        ```

        ### Parameterized Queries (IMPORTANT!)

        Always use parameterized queries to prevent SQL injection:

        ```python
        # ✅ SAFE - Parameterized query
        cursor.execute(
            "SELECT * FROM users WHERE email = %s AND status = %s",
            ["alice@example.com", "active"]
        )

        # ❌ DANGEROUS - String interpolation (SQL injection risk!)
        email = "alice@example.com"
        cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")  # DON'T DO THIS!
        ```

        ### Different Parameter Styles

        Different database drivers use different parameter styles:

        ```python
        # MySQL (pymysql) - %s style
        cursor.execute("SELECT * FROM users WHERE id = %s", [user_id])

        # PostgreSQL (psycopg2) - %s style
        cursor.execute("SELECT * FROM users WHERE id = %s", [user_id])

        # SQLite - ? style
        cursor.execute("SELECT * FROM users WHERE id = ?", [user_id])

        # Named parameters (some drivers)
        cursor.execute(
            "SELECT * FROM users WHERE id = :id",
            {"id": user_id}
        )
        ```

        ## Fetching Results

        ### fetchone()

        Returns a single row or None:

        ```python
        cursor.execute("SELECT * FROM users WHERE id = %s", [user_id])
        row = cursor.fetchone()
        if row:
            print(f"Found user: {row['name']}")
        else:
            print("User not found")
        ```

        ### fetchall()

        Returns all rows as a list:

        ```python
        cursor.execute("SELECT * FROM users WHERE status = 'active'")
        rows = cursor.fetchall()
        print(f"Found {len(rows)} active users")
        ```

        ### fetchmany(size)

        Returns a batch of rows:

        ```python
        cursor.execute("SELECT * FROM users")
        while True:
            batch = cursor.fetchmany(100)
            if not batch:
                break
            for row in batch:
                process_user(row)
        ```

        ### Iterating Over Results

        Cursors are iterable:

        ```python
        cursor.execute("SELECT * FROM users")
        for row in cursor:
            print(row['name'])
        ```

        ## Aggregations

        Use raw SQL for aggregations:

        ```python
        # Count
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE status = 'active'")
        count = cursor.fetchone()['count']

        # Sum
        cursor.execute("SELECT SUM(amount) as total FROM orders WHERE status = 'completed'")
        total = cursor.fetchone()['total']

        # Average
        cursor.execute("SELECT AVG(age) as avg_age FROM users")
        avg_age = cursor.fetchone()['avg_age']

        # Group By
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM users
            GROUP BY status
            ORDER BY count DESC
        ''')
        for row in cursor:
            print(f"{row['status']}: {row['count']} users")
        ```

        ## Complex Queries

        ### Joins

        ```python
        cursor.execute('''
            SELECT
                u.name as user_name,
                COUNT(o.id) as order_count,
                SUM(o.amount) as total_spent
            FROM users u
            LEFT JOIN orders o ON o.user_id = u.id
            WHERE u.status = 'active'
            GROUP BY u.id, u.name
            HAVING COUNT(o.id) > 0
            ORDER BY total_spent DESC
            LIMIT 10
        ''')
        for row in cursor:
            print(f"{row['user_name']}: {row['order_count']} orders, ${row['total_spent']}")
        ```

        ### Subqueries

        ```python
        cursor.execute('''
            SELECT * FROM users
            WHERE id IN (
                SELECT user_id FROM orders
                WHERE amount > 1000
                GROUP BY user_id
                HAVING COUNT(*) >= 3
            )
        ''')
        vip_users = cursor.fetchall()
        ```

        ### CTEs (Common Table Expressions)

        ```python
        cursor.execute('''
            WITH monthly_totals AS (
                SELECT
                    user_id,
                    DATE_FORMAT(created_at, '%%Y-%%m') as month,
                    SUM(amount) as total
                FROM orders
                GROUP BY user_id, DATE_FORMAT(created_at, '%%Y-%%m')
            )
            SELECT
                u.name,
                mt.month,
                mt.total
            FROM monthly_totals mt
            JOIN users u ON u.id = mt.user_id
            ORDER BY mt.month DESC, mt.total DESC
        ''')
        ```

        ## Modifying Data

        ### INSERT

        ```python
        cursor.execute(
            "INSERT INTO users (id, name, email) VALUES (%s, %s, %s)",
            [uuid.uuid4().hex, "Alice", "alice@example.com"]
        )
        # Don't forget to commit!
        connection.commit()
        ```

        ### UPDATE

        ```python
        cursor.execute(
            "UPDATE users SET status = %s WHERE last_login < %s",
            ["inactive", cutoff_date]
        )
        print(f"Updated {cursor.rowcount} users")
        connection.commit()
        ```

        ### DELETE

        ```python
        cursor.execute(
            "DELETE FROM sessions WHERE expires_at < %s",
            [datetime.utcnow()]
        )
        print(f"Deleted {cursor.rowcount} expired sessions")
        connection.commit()
        ```

        ### Batch Operations

        ```python
        # executemany for batch inserts
        users_data = [
            (uuid.uuid4().hex, "Alice", "alice@example.com"),
            (uuid.uuid4().hex, "Bob", "bob@example.com"),
            (uuid.uuid4().hex, "Charlie", "charlie@example.com"),
        ]
        cursor.executemany(
            "INSERT INTO users (id, name, email) VALUES (%s, %s, %s)",
            users_data
        )
        connection.commit()
        ```

        ## Cursor Lifecycle

        ### Proper Cleanup

        Always close cursors when done:

        ```python
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
        finally:
            cursor.close()
        ```

        ### Context Manager

        Use context managers for automatic cleanup:

        ```python
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
        # Cursor automatically closed
        ```

        ## Best Practices

        1. **Always use parameterized queries**: Prevent SQL injection
        2. **Close cursors**: Use try/finally or context managers
        3. **Commit changes**: Don't forget to commit after modifications
        4. **Handle errors**: Catch and handle database exceptions
        5. **Use appropriate fetch method**: fetchone vs fetchall vs fetchmany
        6. **Limit result sets**: Use LIMIT for large tables
        7. **Use indexes**: Ensure queries use indexes efficiently

        ## When to Use Raw SQL vs Model Queries

        **Use Model Queries for:**
        - Simple CRUD operations
        - Basic filtering and sorting
        - Type-safe operations
        - Automatic serialization

        **Use Raw SQL for:**
        - Complex aggregations (GROUP BY, HAVING)
        - Joins across many tables
        - Database-specific features
        - Performance-critical queries
        - Bulk operations
    """),
    "transactions": textwrap.dedent("""\
        # Transaction Management in clearskies

        Transactions ensure data consistency by grouping multiple database operations
        into atomic units. Either all operations succeed, or none do.

        ## Why Transactions Matter

        Without transactions:
        ```python
        # Dangerous - partial failure possible
        order = orders.create({"user_id": user.id, "total": 100})
        user.save({"balance": user.balance - 100})  # What if this fails?
        inventory.save({"quantity": inventory.quantity - 1})  # Data inconsistent!
        ```

        With transactions:
        ```python
        # Safe - all or nothing
        with transaction:
            order = orders.create({"user_id": user.id, "total": 100})
            user.save({"balance": user.balance - 100})
            inventory.save({"quantity": inventory.quantity - 1})
        # Either all succeed or all are rolled back
        ```

        ## Basic Transaction Usage

        ### Using the Connection

        ```python
        import clearskies

        def process_order(cursor, users, orders, products):
            connection = cursor.connection

            try:
                # Start transaction
                connection.begin()

                # Perform operations
                order = orders.create({
                    "user_id": user.id,
                    "status": "pending",
                })

                for item in cart_items:
                    product = products.find(f"id={item['product_id']}")
                    product.save({"stock": product.stock - item['quantity']})

                order.save({"status": "completed"})

                # Commit if all successful
                connection.commit()

            except Exception as e:
                # Rollback on any error
                connection.rollback()
                raise e
        ```

        ### Using Context Manager

        ```python
        def process_order(cursor, users, orders):
            connection = cursor.connection

            with connection:
                # Transaction automatically started
                order = orders.create({"user_id": user.id})
                user.save({"order_count": user.order_count + 1})
                # Automatically committed on success
                # Automatically rolled back on exception
        ```

        ## Transaction Patterns

        ### Try/Except/Finally Pattern

        ```python
        def transfer_funds(cursor, accounts):
            connection = cursor.connection

            try:
                connection.begin()

                from_account = accounts.find(f"id={from_id}")
                to_account = accounts.find(f"id={to_id}")

                if from_account.balance < amount:
                    raise ValueError("Insufficient funds")

                from_account.save({"balance": from_account.balance - amount})
                to_account.save({"balance": to_account.balance + amount})

                connection.commit()
                return {"success": True}

            except Exception as e:
                connection.rollback()
                return {"success": False, "error": str(e)}
        ```

        ### Decorator Pattern

        ```python
        from functools import wraps

        def transactional(func):
            @wraps(func)
            def wrapper(cursor, *args, **kwargs):
                connection = cursor.connection
                try:
                    connection.begin()
                    result = func(cursor, *args, **kwargs)
                    connection.commit()
                    return result
                except Exception:
                    connection.rollback()
                    raise
            return wrapper

        @transactional
        def create_user_with_profile(cursor, users, profiles, data):
            user = users.create({"name": data["name"], "email": data["email"]})
            profiles.create({"user_id": user.id, "bio": data.get("bio", "")})
            return user
        ```

        ## Savepoints

        Savepoints allow partial rollbacks within a transaction:

        ```python
        def complex_operation(cursor, users, orders, notifications):
            connection = cursor.connection

            try:
                connection.begin()

                # Create user
                user = users.create({"name": "Alice"})

                # Create savepoint before optional operations
                cursor.execute("SAVEPOINT before_notifications")

                try:
                    # Try to send notification (might fail)
                    notifications.create({
                        "user_id": user.id,
                        "message": "Welcome!",
                    })
                except Exception:
                    # Rollback only the notification, keep the user
                    cursor.execute("ROLLBACK TO SAVEPOINT before_notifications")

                # Continue with other operations
                orders.create({"user_id": user.id, "status": "pending"})

                connection.commit()

            except Exception:
                connection.rollback()
                raise
        ```

        ## Isolation Levels

        Transaction isolation levels control how transactions interact:

        ### Read Uncommitted
        - Lowest isolation
        - Can see uncommitted changes from other transactions
        - Risk of dirty reads

        ### Read Committed (Default for most databases)
        - Only sees committed changes
        - Prevents dirty reads
        - Risk of non-repeatable reads

        ### Repeatable Read
        - Consistent reads within transaction
        - Prevents non-repeatable reads
        - Risk of phantom reads

        ### Serializable
        - Highest isolation
        - Transactions appear to run sequentially
        - Lowest concurrency

        ```python
        # Setting isolation level (MySQL example)
        cursor.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
        connection.begin()
        # ... operations ...
        connection.commit()
        ```

        ## Auto-Commit Mode

        By default, many database drivers use auto-commit mode:

        ```python
        # Auto-commit mode (each statement is its own transaction)
        cursor.execute("INSERT INTO users ...")  # Immediately committed

        # Disable auto-commit for explicit transactions
        connection.autocommit = False
        cursor.execute("INSERT INTO users ...")  # Not committed yet
        connection.commit()  # Now committed
        ```

        ## Nested Transactions

        Some databases support nested transactions via savepoints:

        ```python
        def outer_operation(cursor, users, orders):
            connection = cursor.connection

            connection.begin()

            user = users.create({"name": "Alice"})

            # Nested "transaction" via savepoint
            cursor.execute("SAVEPOINT nested")
            try:
                orders.create({"user_id": user.id})
                cursor.execute("RELEASE SAVEPOINT nested")
            except Exception:
                cursor.execute("ROLLBACK TO SAVEPOINT nested")

            connection.commit()
        ```

        ## Deadlock Handling

        Deadlocks occur when transactions wait for each other:

        ```python
        import time
        from pymysql.err import OperationalError

        def with_retry(func, max_retries=3, delay=0.1):
            for attempt in range(max_retries):
                try:
                    return func()
                except OperationalError as e:
                    if "Deadlock" in str(e) and attempt < max_retries - 1:
                        time.sleep(delay * (2 ** attempt))  # Exponential backoff
                        continue
                    raise

        def transfer_funds(cursor, from_id, to_id, amount):
            def do_transfer():
                connection = cursor.connection
                connection.begin()
                try:
                    # Always lock in consistent order to prevent deadlocks
                    ids = sorted([from_id, to_id])
                    for id in ids:
                        cursor.execute(
                            "SELECT * FROM accounts WHERE id = %s FOR UPDATE",
                            [id]
                        )
                    # ... perform transfer ...
                    connection.commit()
                except Exception:
                    connection.rollback()
                    raise

            return with_retry(do_transfer)
        ```

        ## Long-Running Transactions

        Avoid long-running transactions:

        ```python
        # ❌ Bad - holds locks for too long
        connection.begin()
        for user in users.where("status=active"):
            # Process each user (might take a long time)
            process_user(user)
            user.save({"processed": True})
        connection.commit()

        # ✅ Better - batch processing with smaller transactions
        batch_size = 100
        offset = 0

        while True:
            connection.begin()
            batch = list(users.where("status=active").where("processed=0").limit(batch_size))
            if not batch:
                connection.rollback()
                break

            for user in batch:
                process_user(user)
                user.save({"processed": True})

            connection.commit()
            offset += batch_size
        ```

        ## Best Practices

        1. **Keep transactions short**: Minimize lock duration
        2. **Handle errors properly**: Always rollback on failure
        3. **Use appropriate isolation**: Balance consistency vs concurrency
        4. **Avoid deadlocks**: Lock resources in consistent order
        5. **Don't hold transactions during I/O**: External calls can be slow
        6. **Use savepoints for partial rollbacks**: When you need granular control
        7. **Monitor transaction duration**: Long transactions indicate problems
        8. **Test failure scenarios**: Ensure rollback works correctly

        ## Common Pitfalls

        ### Forgetting to Commit

        ```python
        # ❌ Changes never persisted
        connection.begin()
        users.create({"name": "Alice"})
        # Forgot connection.commit()!

        # ✅ Always commit
        connection.begin()
        users.create({"name": "Alice"})
        connection.commit()
        ```

        ### Forgetting to Rollback

        ```python
        # ❌ Connection left in bad state
        try:
            connection.begin()
            users.create({"name": "Alice"})
            raise ValueError("Something went wrong")
            connection.commit()
        except Exception:
            pass  # Forgot to rollback!

        # ✅ Always rollback on error
        try:
            connection.begin()
            users.create({"name": "Alice"})
            raise ValueError("Something went wrong")
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        ```

        ### Mixing Auto-Commit and Explicit Transactions

        ```python
        # ❌ Confusing behavior
        connection.autocommit = True
        connection.begin()  # This might not work as expected

        # ✅ Be explicit about mode
        connection.autocommit = False
        connection.begin()
        # ... operations ...
        connection.commit()
        ```
    """),
}
