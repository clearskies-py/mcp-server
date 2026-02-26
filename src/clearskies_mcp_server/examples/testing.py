"""Testing example for clearskies."""

import textwrap


def example_testing() -> str:
    """Complete example of testing clearskies applications."""
    return textwrap.dedent("""\
        # Example: Testing clearskies Applications

        This example demonstrates comprehensive testing patterns for clearskies applications.

        ## Project Structure

        ```
        my_project/
        ├── models/
        │   └── user.py
        ├── tests/
        │   ├── test_models.py
        │   ├── test_endpoints.py
        │   └── test_hooks.py
        └── app.py
        ```

        ## models/user.py

        ```python
        import clearskies
        from clearskies import columns
        from clearskies.validators import Required, Unique

        class User(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            name = columns.String(validators=[Required()])
            email = columns.Email(validators=[Required(), Unique()])
            age = columns.Integer()
            status = columns.Select(["active", "inactive", "pending"])
            created_at = columns.Created()
            updated_at = columns.Updated()

            def pre_save(self, data):
                # Auto-set status for new users
                if not self.exists and "status" not in data:
                    data["status"] = "pending"
                return data

            def post_save(self, data, id):
                # Track status changes
                if self.is_changing("status", data):
                    print(f"User {id} status changed to {data.get('status')}")
        ```

        ## tests/test_models.py

        ```python
        import pytest
        from models.user import User

        class TestUserModel:
            def setup_method(self):
                # Fresh model instance for each test
                self.users = User()

            def test_create_user(self):
                user = self.users.create({
                    "name": "Alice",
                    "email": "alice@example.com",
                    "age": 30
                })

                assert user.name == "Alice"
                assert user.email == "alice@example.com"
                assert user.age == 30
                assert user.id is not None
                assert user.status == "pending"  # Auto-set by pre_save

            def test_update_user(self):
                user = self.users.create({
                    "name": "Bob",
                    "email": "bob@example.com"
                })
                original_id = user.id

                user.save({"name": "Robert", "status": "active"})

                assert user.name == "Robert"
                assert user.status == "active"
                assert user.id == original_id

            def test_query_users(self):
                self.users.create({"name": "Alice", "email": "alice@example.com", "age": 25})
                self.users.create({"name": "Bob", "email": "bob@example.com", "age": 30})
                self.users.create({"name": "Charlie", "email": "charlie@example.com", "age": 35})

                # Query with conditions
                results = list(self.users.where("age>=30"))
                assert len(results) == 2

                # Find single record
                alice = self.users.find("name=Alice")
                assert alice.email == "alice@example.com"

            def test_unique_email_validation(self):
                self.users.create({"name": "First", "email": "unique@example.com"})

                with pytest.raises(Exception) as exc_info:
                    self.users.create({"name": "Second", "email": "unique@example.com"})

                assert "unique" in str(exc_info.value).lower() or "email" in str(exc_info.value).lower()

            def test_required_field_validation(self):
                with pytest.raises(Exception):
                    self.users.create({"email": "test@example.com"})  # Missing name

            def test_delete_user(self):
                user = self.users.create({"name": "ToDelete", "email": "delete@example.com"})
                user_id = user.id

                user.delete()

                deleted = self.users.find(f"id={user_id}")
                assert deleted.exists is False
        ```

        ## tests/test_endpoints.py

        ```python
        import pytest
        import clearskies
        from models.user import User

        class TestUserEndpoints:
            def setup_method(self):
                self.endpoint = clearskies.endpoints.RestfulApi(
                    url="users",
                    model_class=User,
                    readable_column_names=["id", "name", "email", "age", "status", "created_at"],
                    writeable_column_names=["name", "email", "age", "status"],
                    sortable_column_names=["name", "age", "created_at"],
                    searchable_column_names=["name", "email"],
                    default_sort_column_name="name",
                )
                self.cli = clearskies.contexts.Cli(self.endpoint, classes=[User])

            def test_create_via_api(self):
                result = self.cli.execute_test(
                    method="POST",
                    path="/users",
                    body={"name": "Jane", "email": "jane@example.com", "age": 28},
                )

                assert result["status"] == "success"
                assert result["data"]["name"] == "Jane"
                assert result["data"]["email"] == "jane@example.com"
                assert "id" in result["data"]

            def test_list_users(self):
                # Create some users first
                self.cli.execute_test(
                    method="POST",
                    path="/users",
                    body={"name": "Alice", "email": "alice@example.com"},
                )
                self.cli.execute_test(
                    method="POST",
                    path="/users",
                    body={"name": "Bob", "email": "bob@example.com"},
                )

                result = self.cli.execute_test(
                    method="GET",
                    path="/users",
                )

                assert result["status"] == "success"
                assert len(result["data"]) == 2

            def test_search_users(self):
                self.cli.execute_test(
                    method="POST",
                    path="/users",
                    body={"name": "Alice Smith", "email": "alice@example.com"},
                )
                self.cli.execute_test(
                    method="POST",
                    path="/users",
                    body={"name": "Bob Jones", "email": "bob@example.com"},
                )

                result = self.cli.execute_test(
                    method="GET",
                    path="/users?name=Alice",
                )

                assert result["status"] == "success"
                assert len(result["data"]) == 1
                assert result["data"][0]["name"] == "Alice Smith"

            def test_validation_errors(self):
                result = self.cli.execute_test(
                    method="POST",
                    path="/users",
                    body={"email": "invalid"},  # Missing name, invalid email
                )

                assert result["status"] == "input_errors"
                assert "name" in result["input_errors"]
        ```

        ## tests/test_hooks.py

        ```python
        import pytest
        from unittest.mock import Mock, patch
        import clearskies
        from clearskies import columns

        class Order(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            status = columns.String()
            total = columns.Float()

            _notification_service = None

            def post_save(self, data, id):
                if self._notification_service and self.is_changing("status", data):
                    self._notification_service.notify(
                        f"Order {id} status changed to {data.get('status')}"
                    )

        class TestHooks:
            def test_notification_sent_on_status_change(self):
                mock_notifier = Mock()
                Order._notification_service = mock_notifier

                orders = Order()
                order = orders.create({"status": "pending", "total": 100.0})

                # First save triggers notification
                mock_notifier.notify.assert_called_once()

                # Update status
                mock_notifier.reset_mock()
                order.save({"status": "completed"})

                mock_notifier.notify.assert_called_once()
                assert "completed" in mock_notifier.notify.call_args[0][0]

                Order._notification_service = None

            def test_no_notification_when_status_unchanged(self):
                mock_notifier = Mock()
                Order._notification_service = mock_notifier

                orders = Order()
                order = orders.create({"status": "pending", "total": 100.0})
                mock_notifier.reset_mock()

                # Update total only, not status
                order.save({"total": 150.0})

                mock_notifier.notify.assert_not_called()

                Order._notification_service = None
        ```

        ## Running Tests

        ```bash
        # Run all tests
        pytest tests/

        # Run with verbose output
        pytest tests/ -v

        # Run specific test file
        pytest tests/test_models.py

        # Run specific test
        pytest tests/test_models.py::TestUserModel::test_create_user
        ```
    """)
