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
                to_call=aggregate_data,
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
                    current_status = self.status if self else None
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
                if "amount" in data and self and self.status != "draft":
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
                if "status" in data and (not self or data["status"] != self.status):
                    history = self.status_history.copy() if self else []
                    history.append({
                        "from": self.status if self else None,
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
        # Secrets in clearskies

        clearskies 2.x does not store models in a secrets manager (`SecretsBackend` is not
        exported from `clearskies.backends` and should not be used). Instead, secrets are a
        dependency named `secrets`: bind a secret manager once, then read secrets wherever
        they are needed.

        ## Secret Managers

        - `clearskies.secrets.Secrets` – base class and the default `secrets` dependency.
          Every method raises `NotImplementedError`, so you must bind a real manager.
        - `clearskies.secrets.Akeyless` – Akeyless vault (requires the `akeyless` SDK).
        - `clearskies_aws.secrets.SecretsManager` / `clearskies_aws.secrets.ParameterStore` –
          AWS Secrets Manager and SSM Parameter Store (from clearskies-aws).

        ```python
        import clearskies

        app = clearskies.contexts.WsgiRef(
            my_endpoint,
            bindings={
                "secrets": clearskies.secrets.Akeyless(
                    access_id="p-abc123",      # must match ^p-[0-9a-zA-Z]+$
                    access_type="aws_iam",     # "aws_iam", "saml", or "jwt"
                    # jwt_env_key="AKEYLESS_JWT",  # required for access_type="jwt"
                ),
            },
        )
        ```

        ## Reading Secrets

        Callables receive the manager through an argument named `secrets`; classes that
        extend `clearskies.di.InjectableProperties` (models, endpoints, your own services)
        use `inject.Secrets()`:

        ```python
        import clearskies
        from clearskies.di import inject

        def handler(secrets):
            return {"configured": bool(secrets.get("/path/to/api-key"))}

        class ServiceClient(clearskies.di.InjectableProperties):
            secrets = inject.Secrets()

            def api_key(self) -> str:
                return self.secrets.get("/path/to/api-key")
        ```

        `Secrets.get()` signature:

        ```python
        get(path, silent_if_not_found=False, refresh=False, json_path=None, kind=None)
        ```

        - `silent_if_not_found` – return an empty value instead of raising
        - `refresh` – bypass `cache_storage` and fetch from the manager
        - `json_path` – parse the secret as JSON and return a field (dot notation, e.g.
          `"credentials.api_key"`). Renamed from `json_attribute` in 2.1.8.
        - `kind` – `"static_secret"`, `"dynamic_secret"`, or `"rotated_secret"`

        Other methods: `create`, `update`, `upsert`, `delete`, `list_secrets`, `list_sub_folders`.

        ## Akeyless Specifics

        - Kind resolution: explicit `kind=` → `describe_secret` if `auto_guess_type=True` →
          `static_secret`. Passing `kind=` skips the extra `describe_secret` API call.
        - Dynamic/rotated secrets accept `args={...}` for producer arguments.
        - Optional caching: `cache_storage=clearskies.secrets.cache_storage.MemoryCache(default_ttl=300)`
          (or a `SecretCache` subclass; clearskies-aws provides `ParameterStoreCache`).
        - Auth tokens are cached and renewed `token_refresh_buffer` seconds (default 300) before expiry.

        ```python
        password = secrets.get("/path/to/db-credentials", kind="dynamic_secret", json_path="password")
        ```

        ## SecretBearer Authentication

        `clearskies.authentication.SecretBearer` reads its key from the `secrets` dependency when
        `secret_key` is set (or from an environment variable with `environment_key`). Since 2.1.8–2.1.10:

        - `secret_kind` – `"static_secret"`, `"dynamic_secret"`, or `"rotated_secret"` (validated by
          `clearskies.configs.SecretKind`); forwarded as `kind=`
        - `refresh=True` – always forward `refresh=True` to `secrets.get()`
        - `json_path` – extract one field from a JSON secret
        - `headers(retry_auth=True)` – clear the cached key and re-fetch once (e.g. after a 401)

        These options only apply with `secret_key`. `alternate_secret_key` (for rotation) uses
        `refresh` and `json_path` but not `secret_kind`.

        ```python
        authentication = clearskies.authentication.SecretBearer(
            secret_key="/path/to/service-token",
            secret_kind="dynamic_secret",
            json_path="credentials.token",
            refresh=True,
            header_prefix="Bearer ",
        )
        ```

        ## Custom Managers and Testing

        Subclass `clearskies.secrets.Secrets` and bind an instance as `secrets`. If it is used
        with `SecretBearer(secret_key=...)`, its `get()` must accept `refresh`, `json_path`, and
        `kind` keyword arguments, because `SecretBearer` always passes them.

        Note: in clearskies-aws 2.1.2, `SecretsManager.get()` and `ParameterStore.get()` do not
        accept those arguments, so combining them with `SecretBearer(secret_key=...)` raises
        `TypeError`. Call their `get()` directly, or wrap them in a subclass that accepts the extra
        keyword arguments.

        ## Best Practices

        1. **Never hardcode or log secret values**
        2. **Inject `secrets`** instead of creating clients inside your code
        3. **Pass `kind=`/`secret_kind`** for Akeyless dynamic or rotated secrets to avoid extra API calls
        4. **Use `alternate_secret_key`** to rotate inbound API keys without downtime
        5. **Use separate secret paths per environment**
    """),
}
