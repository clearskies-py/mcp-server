"""
Advanced concept explanations for clearskies framework.

This module contains explanations for async patterns, advanced state machines,
and secrets backend usage.
"""

import textwrap

ADVANCED_CONCEPTS = {
    "async": textwrap.dedent("""\
        # Async Support in clearskies

        clearskies is primarily designed for synchronous operation, which aligns with
        its declarative programming model and WSGI-based contexts. However, there are
        patterns for integrating async code when needed.

        ## Current State

        As of the current version, clearskies:
        - Uses synchronous backends (CursorBackend, MemoryBackend, ApiBackend)
        - Provides synchronous contexts (Wsgi, WsgiRef, Cli)
        - Executes model operations synchronously

        This design choice simplifies the programming model and works well for most
        use cases where database operations are the primary bottleneck.

        ## When You Need Async

        Consider async patterns when:
        - Making multiple independent external API calls
        - Handling WebSocket connections
        - Processing real-time data streams
        - Building high-concurrency applications

        ## Integrating Async Code

        ### Using asyncio.run() in Callable Endpoints

        ```python
        import asyncio
        import aiohttp
        import clearskies

        async def fetch_multiple_apis(urls: list[str]) -> list[dict]:
            async with aiohttp.ClientSession() as session:
                tasks = [fetch_url(session, url) for url in urls]
                return await asyncio.gather(*tasks)

        async def fetch_url(session, url: str) -> dict:
            async with session.get(url) as response:
                return await response.json()

        def aggregate_data(urls: list[str]):
            # Run async code from sync context
            results = asyncio.run(fetch_multiple_apis(urls))
            return {"results": results}

        cli = clearskies.contexts.Cli(
            clearskies.endpoints.Callable(
                callable=aggregate_data,
                input_requirements={"urls": list},
            )
        )
        ```

        ### Using ThreadPoolExecutor for Parallel I/O

        ```python
        from concurrent.futures import ThreadPoolExecutor, as_completed
        import clearskies
        import requests

        def fetch_url(url: str) -> dict:
            response = requests.get(url)
            return response.json()

        def parallel_fetch(urls: list[str], max_workers: int = 10):
            results = []
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                future_to_url = {executor.submit(fetch_url, url): url for url in urls}
                for future in as_completed(future_to_url):
                    url = future_to_url[future]
                    try:
                        results.append({"url": url, "data": future.result()})
                    except Exception as e:
                        results.append({"url": url, "error": str(e)})
            return results

        def aggregate_endpoint(urls: list[str]):
            return {"results": parallel_fetch(urls)}
        ```

        ### Async Background Tasks

        For fire-and-forget operations:

        ```python
        import asyncio
        import threading
        import clearskies

        # Background event loop
        _loop = None
        _thread = None

        def get_event_loop():
            global _loop, _thread
            if _loop is None:
                _loop = asyncio.new_event_loop()
                _thread = threading.Thread(target=_loop.run_forever, daemon=True)
                _thread.start()
            return _loop

        def run_async_background(coro):
            loop = get_event_loop()
            asyncio.run_coroutine_threadsafe(coro, loop)

        async def send_notification_async(user_id: str, message: str):
            # Async notification logic
            await some_async_api.send(user_id, message)

        class User(clearskies.Model):
            def save_finished(self):
                if self.was_changed("status"):
                    # Fire and forget async notification
                    run_async_background(
                        send_notification_async(self.id, f"Status changed to {self.status}")
                    )
        ```

        ## ASGI Considerations

        If you need full async support, consider:

        1. **Using an ASGI framework** – FastAPI, Starlette, etc.
        2. **clearskies for business logic** – Use clearskies models with async wrappers
        3. **Async database drivers** – asyncpg, aiomysql, etc.

        ### Example: clearskies Models with FastAPI

        ```python
        from fastapi import FastAPI
        import clearskies
        from clearskies import columns

        app = FastAPI()

        class User(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()
            id = columns.Uuid()
            name = columns.String()
            email = columns.Email()

        @app.get("/users")
        async def list_users():
            # clearskies operations are sync, but FastAPI handles the async context
            users = User()
            return [{"id": u.id, "name": u.name} for u in users.limit(100)]

        @app.post("/users")
        async def create_user(name: str, email: str):
            users = User()
            user = users.create({"name": name, "email": email})
            return {"id": user.id, "name": user.name, "email": user.email}
        ```

        ## Best Practices

        1. **Keep it simple** – Use sync code unless you have a specific need for async
        2. **Isolate async code** – Wrap async operations in sync functions
        3. **Use thread pools** – For parallel I/O without full async
        4. **Consider message queues** – For background processing (Celery, RQ)
        5. **Profile first** – Ensure async actually improves performance
        6. **Handle errors** – Async errors can be harder to debug

        ## When to Use What

        | Scenario | Recommendation |
        |----------|----------------|
        | Standard CRUD API | Sync clearskies (default) |
        | Multiple API calls | ThreadPoolExecutor or asyncio.run() |
        | Background tasks | Message queue (Celery, RQ) |
        | WebSockets | ASGI framework + clearskies models |
        | High concurrency | ASGI framework + clearskies models |
        | Real-time streaming | ASGI framework |
    """),
    "state_machine_advanced": textwrap.dedent("""\
        # Advanced State Machine Patterns in clearskies

        clearskies encourages organizing business logic as state machines using column
        lifecycle hooks. This guide covers advanced patterns for complex state management.

        ## Basic State Machine Review

        ```python
        import clearskies
        from clearskies import columns
        from datetime import datetime

        class Order(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            customer_id = columns.String()
            total = columns.Float()

            status = columns.Select(
                ["pending", "confirmed", "shipped", "delivered", "cancelled"],
                on_change_pre_save={
                    "confirmed": lambda data, model: {"confirmed_at": datetime.utcnow()},
                    "shipped": lambda data, model: {"shipped_at": datetime.utcnow()},
                    "delivered": lambda data, model: {"delivered_at": datetime.utcnow()},
                },
                on_change_post_save={
                    "confirmed": lambda data, model, id: send_confirmation_email(id),
                    "shipped": lambda data, model, id: send_shipping_notification(id),
                },
            )

            confirmed_at = columns.Datetime()
            shipped_at = columns.Datetime()
            delivered_at = columns.Datetime()
        ```

        ## State Transition Validation

        Enforce valid state transitions:

        ```python
        import clearskies
        from clearskies import columns

        VALID_TRANSITIONS = {
            None: ["pending"],  # Initial state
            "pending": ["confirmed", "cancelled"],
            "confirmed": ["shipped", "cancelled"],
            "shipped": ["delivered"],
            "delivered": [],  # Terminal state
            "cancelled": [],  # Terminal state
        }

        class Order(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            status = columns.Select(["pending", "confirmed", "shipped", "delivered", "cancelled"])

            def pre_save(self, data):
                if "status" in data:
                    current_status = self.status if self.exists else None
                    new_status = data["status"]

                    if new_status not in VALID_TRANSITIONS.get(current_status, []):
                        raise ValueError(
                            f"Invalid transition from '{current_status}' to '{new_status}'"
                        )
                return data
        ```

        ## State-Dependent Behavior

        Different behavior based on current state:

        ```python
        import clearskies
        from clearskies import columns

        class Order(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            status = columns.Select(["draft", "submitted", "approved", "rejected"])
            amount = columns.Float()

            def pre_save(self, data):
                # Only allow amount changes in draft status
                if "amount" in data and self.exists and self.status != "draft":
                    raise ValueError("Cannot modify amount after submission")

                # Auto-approve small orders
                if data.get("status") == "submitted" and data.get("amount", self.amount) < 100:
                    data["status"] = "approved"
                    data["auto_approved"] = True

                return data

            def can_edit(self) -> bool:
                return self.status == "draft"

            def can_submit(self) -> bool:
                return self.status == "draft" and self.amount > 0

            def can_approve(self) -> bool:
                return self.status == "submitted"
        ```

        ## Multiple State Machines

        Handle multiple independent states:

        ```python
        import clearskies
        from clearskies import columns

        class Order(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()

            # Order lifecycle state
            order_status = columns.Select(
                ["pending", "confirmed", "shipped", "delivered"],
                on_change_post_save={
                    "shipped": lambda data, model, id: update_inventory(id),
                },
            )

            # Payment state (independent)
            payment_status = columns.Select(
                ["unpaid", "pending", "paid", "refunded"],
                on_change_post_save={
                    "paid": lambda data, model, id: record_payment(id),
                    "refunded": lambda data, model, id: process_refund(id),
                },
            )

            # Fulfillment state (independent)
            fulfillment_status = columns.Select(
                ["unfulfilled", "partial", "fulfilled", "returned"],
            )

            def can_ship(self) -> bool:
                # Can only ship if confirmed and paid
                return (
                    self.order_status == "confirmed" and
                    self.payment_status == "paid"
                )
        ```

        ## State History Tracking

        Track state changes over time:

        ```python
        import clearskies
        from clearskies import columns
        from datetime import datetime
        import json

        class Order(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            status = columns.Select(["pending", "confirmed", "shipped", "delivered"])
            status_history = columns.Json(default=[])

            def pre_save(self, data):
                if "status" in data and (not self.exists or data["status"] != self.status):
                    history = self.status_history.copy() if self.exists else []
                    history.append({
                        "from": self.status if self.exists else None,
                        "to": data["status"],
                        "timestamp": datetime.utcnow().isoformat(),
                        "changed_by": data.get("_changed_by", "system"),
                    })
                    data["status_history"] = history
                return data

            def get_status_duration(self, status: str) -> float:
                \"\"\"Get time spent in a specific status (in seconds).\"\"\"
                total = 0
                for i, entry in enumerate(self.status_history):
                    if entry["to"] == status:
                        start = datetime.fromisoformat(entry["timestamp"])
                        # Find when we left this status
                        if i + 1 < len(self.status_history):
                            end = datetime.fromisoformat(self.status_history[i + 1]["timestamp"])
                        else:
                            end = datetime.utcnow()
                        total += (end - start).total_seconds()
                return total
        ```

        ## Event-Driven State Changes

        Trigger state changes from external events:

        ```python
        import clearskies
        from clearskies import columns

        class Order(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            status = columns.Select(["pending", "paid", "shipped", "delivered"])
            payment_id = columns.String()
            tracking_number = columns.String()

            def on_payment_received(self, payment_id: str):
                \"\"\"Called when payment webhook is received.\"\"\"
                if self.status != "pending":
                    raise ValueError(f"Cannot process payment in status {self.status}")

                self.save({
                    "status": "paid",
                    "payment_id": payment_id,
                })

            def on_shipment_created(self, tracking_number: str):
                \"\"\"Called when shipment webhook is received.\"\"\"
                if self.status != "paid":
                    raise ValueError(f"Cannot ship order in status {self.status}")

                self.save({
                    "status": "shipped",
                    "tracking_number": tracking_number,
                })

            def on_delivery_confirmed(self):
                \"\"\"Called when delivery webhook is received.\"\"\"
                if self.status != "shipped":
                    raise ValueError(f"Cannot confirm delivery in status {self.status}")

                self.save({"status": "delivered"})
        ```

        ## Workflow Orchestration

        Complex multi-step workflows:

        ```python
        import clearskies
        from clearskies import columns
        from datetime import datetime

        class Workflow(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.CursorBackend()

            id = columns.Uuid()
            workflow_type = columns.String()
            current_step = columns.Integer(default=0)
            steps = columns.Json(default=[])
            status = columns.Select(["pending", "running", "completed", "failed"])

            def advance(self):
                \"\"\"Move to the next step in the workflow.\"\"\"
                if self.current_step >= len(self.steps):
                    self.save({"status": "completed"})
                    return

                step = self.steps[self.current_step]
                try:
                    # Execute the step
                    execute_step(step)
                    self.save({
                        "current_step": self.current_step + 1,
                        "status": "running" if self.current_step + 1 < len(self.steps) else "completed",
                    })
                except Exception as e:
                    self.save({
                        "status": "failed",
                        "error": str(e),
                    })

            def retry(self):
                \"\"\"Retry the current step.\"\"\"
                if self.status != "failed":
                    raise ValueError("Can only retry failed workflows")
                self.save({"status": "running"})
                self.advance()
        ```

        ## Best Practices

        1. **Define valid transitions explicitly** – Don't allow arbitrary state changes
        2. **Use hooks for side effects** – Keep state logic in the model
        3. **Track state history** – For debugging and auditing
        4. **Separate independent states** – Don't combine unrelated state machines
        5. **Test state transitions** – Unit test all valid and invalid transitions
        6. **Document state diagrams** – Make state machines visible to the team
    """),
    "secrets_backend": textwrap.dedent("""\
        # Secrets Backend in clearskies

        The SecretsBackend allows you to store model data in a secrets manager instead of
        a traditional database. This is useful for storing sensitive configuration data
        that needs to be managed as structured records.

        ## Overview

        SecretsBackend:
        - Stores each record as a separate secret
        - Supports CRUD operations like other backends
        - Integrates with AWS Secrets Manager, Akeyless, etc.
        - Useful for managing API keys, credentials, configuration

        ## Basic Usage

        ```python
        import clearskies
        from clearskies import columns

        class ApiCredential(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.SecretsBackend(
                secret_prefix="api-credentials/",
            )

            id = columns.String()
            name = columns.String()
            api_key = columns.String()
            api_secret = columns.String()
            environment = columns.Select(["development", "staging", "production"])
            created_at = columns.Created()
            updated_at = columns.Updated()
        ```

        ## AWS Secrets Manager Integration

        Using clearskies-aws:

        ```python
        import clearskies
        import clearskies_aws
        from clearskies import columns

        class DatabaseCredential(clearskies.Model):
            id_column_name = "id"
            backend = clearskies_aws.backends.SecretsManagerBackend(
                secret_prefix="database-credentials/",
                region="us-east-1",
            )

            id = columns.String()
            name = columns.String()
            host = columns.String()
            port = columns.Integer()
            username = columns.String()
            password = columns.String()
            database = columns.String()
        ```

        ## Akeyless Integration

        Using clearskies-akeyless:

        ```python
        import clearskies
        import clearskies_akeyless_custom_producer
        from clearskies import columns

        class ServiceCredential(clearskies.Model):
            id_column_name = "id"
            backend = clearskies_akeyless_custom_producer.backends.AkeylessBackend(
                secret_path="/credentials/services/",
            )

            id = columns.String()
            service_name = columns.String()
            client_id = columns.String()
            client_secret = columns.String()
        ```

        ## Use Cases

        ### Managing API Keys

        ```python
        class ExternalApiKey(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.SecretsBackend(
                secret_prefix="external-apis/",
            )

            id = columns.String()
            provider = columns.String()  # e.g., "stripe", "twilio"
            environment = columns.Select(["sandbox", "production"])
            api_key = columns.String()
            webhook_secret = columns.String()
            created_at = columns.Created()

        # Create a new API key record
        api_keys = ExternalApiKey()
        api_keys.create({
            "id": "stripe-prod",
            "provider": "stripe",
            "environment": "production",
            "api_key": "sk_live_...",
            "webhook_secret": "whsec_...",
        })

        # Retrieve API key
        stripe_key = api_keys.find("id=stripe-prod")
        print(stripe_key.api_key)
        ```

        ### Managing Database Credentials

        ```python
        class DatabaseConfig(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.SecretsBackend(
                secret_prefix="databases/",
            )

            id = columns.String()
            name = columns.String()
            engine = columns.Select(["mysql", "postgresql", "mongodb"])
            host = columns.String()
            port = columns.Integer()
            username = columns.String()
            password = columns.String()
            database = columns.String()
            ssl_enabled = columns.Boolean(default=True)

            def get_connection_string(self) -> str:
                if self.engine == "mysql":
                    return f"mysql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
                elif self.engine == "postgresql":
                    return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
                else:
                    raise ValueError(f"Unsupported engine: {self.engine}")
        ```

        ### Rotating Credentials

        ```python
        class RotatableCredential(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.SecretsBackend(
                secret_prefix="rotating-credentials/",
            )

            id = columns.String()
            current_key = columns.String()
            previous_key = columns.String()
            rotated_at = columns.Datetime()

            def rotate(self, new_key: str):
                \"\"\"Rotate to a new key while keeping the previous one.\"\"\"
                self.save({
                    "previous_key": self.current_key,
                    "current_key": new_key,
                    "rotated_at": datetime.utcnow(),
                })

            def validate_key(self, key: str) -> bool:
                \"\"\"Check if a key is valid (current or previous).\"\"\"
                return key in [self.current_key, self.previous_key]
        ```

        ## KMS Encryption

        For additional security, enable KMS encryption:

        ```python
        import clearskies_aws

        class EncryptedCredential(clearskies.Model):
            id_column_name = "id"
            backend = clearskies_aws.backends.SecretsManagerBackend(
                secret_prefix="encrypted-credentials/",
                kms_key_id="arn:aws:kms:us-east-1:123456789:key/12345678-1234-1234-1234-123456789012",
            )

            id = columns.String()
            data = columns.Json()
        ```

        ## Best Practices

        1. **Use meaningful prefixes** – Organize secrets by type/environment
        2. **Implement rotation** – Regularly rotate sensitive credentials
        3. **Limit access** – Use IAM policies to restrict who can read secrets
        4. **Audit access** – Enable logging for secret access
        5. **Don't store in code** – Never hardcode secrets
        6. **Use separate secrets per environment** – Don't share between dev/prod
        7. **Encrypt at rest** – Use KMS encryption for sensitive data
        8. **Version secrets** – Track changes to credentials

        ## Limitations

        - Query performance is slower than databases
        - Limited query capabilities (no complex WHERE clauses)
        - Cost considerations for high-volume access
        - Rate limits on secrets manager APIs
        - Not suitable for high-frequency read/write operations
    """),
}
