"""
Lifecycle concept explanations for clearskies framework.

This module contains explanations for save lifecycle and state machine concepts.
"""

import textwrap

LIFECYCLE_CONCEPTS = {
    "save_lifecycle": textwrap.dedent("""\
        # clearskies Save Lifecycle

        The save process in clearskies follows a strict lifecycle with hooks at each step:

        1. **pre_save** (columns, then model) – Modify data before persistence. Must be stateless.
           Return: `dict[str, Any]` with additional/modified data.
        2. **to_backend** (columns, then model) – Convert data for the backend (e.g. datetime → string).
        3. **Backend create/update** – Data is persisted.
        4. **post_save** (columns, then model) – Called after backend update. Id is available. Model NOT yet updated.
        5. **Model data updated** – The model instance reflects the new data.
        6. **save_finished** (columns, then model) – Called after model is fully updated. Use `was_changed()` and `previous_value()`.

        ## Hook Summary

        | Hook            | Stateful | Return Value   | Id Present | Backend Updated | Model Updated |
        |-----------------|----------|----------------|------------|-----------------|---------------|
        | pre_save        | No       | dict[str, Any] | No         | No              | No            |
        | post_save       | Yes      | None           | Yes        | Yes             | No            |
        | save_finished   | Yes      | None           | Yes        | Yes             | Yes           |

        ## Example

        ```python
        class User(clearskies.Model):
            def pre_save(self, data):
                if self.is_changing("name", data):
                    data["name_slug"] = data["name"].lower().replace(" ", "-")
                return data

            def post_save(self, data, id):
                if self.is_changing("email", data):
                    send_verification_email(data["email"])

            def save_finished(self):
                if self.was_changed("status"):
                    log(f"Status changed from {self.previous_value('status')} to {self.status}")
        ```
    """),
    "state_machine": textwrap.dedent("""\
        # clearskies State Machine Approach

        clearskies encourages organizing business logic as a state machine using the column
        lifecycle hooks (on_change_pre_save, on_change_post_save, on_change_save_finished).

        Columns can declare actions that fire when their value changes:

        ```python
        status = columns.Select(
            ["pending", "approved", "rejected"],
            on_change_pre_save={
                "approved": lambda data, model: {"approved_at": datetime.utcnow()},
            },
            on_change_post_save={
                "approved": lambda data, model, id: send_approval_notification(id),
            },
        )
        ```

        This approach keeps business logic organized around state transitions rather than
        scattered across controllers and services.
    """),
}
