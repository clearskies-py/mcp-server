"""
Advanced state machine example for clearskies framework.

This module contains a complete example demonstrating advanced state machine
patterns including transition validation, state history, and multiple state machines.
"""


def example_state_machine_advanced() -> str:
    """Complete example of advanced state machine patterns in clearskies."""
    return '''\
# Advanced State Machine Patterns Example

This example demonstrates advanced state machine patterns in clearskies including
state transition validation, state history tracking, and multiple independent state machines.

## Complete Order Management System

```python
import clearskies
from clearskies import columns
from datetime import datetime
import json

# =============================================================================
# STATE TRANSITION DEFINITIONS
# =============================================================================

# Valid order status transitions
ORDER_TRANSITIONS = {
    None: ["pending"],  # Initial state
    "pending": ["confirmed", "cancelled"],
    "confirmed": ["processing", "cancelled"],
    "processing": ["shipped", "cancelled"],
    "shipped": ["delivered", "returned"],
    "delivered": [],  # Terminal state
    "cancelled": [],  # Terminal state
    "returned": ["refunded"],
    "refunded": [],  # Terminal state
}

# Valid payment status transitions
PAYMENT_TRANSITIONS = {
    None: ["pending"],
    "pending": ["authorized", "failed"],
    "authorized": ["captured", "voided"],
    "captured": ["refunded", "partially_refunded"],
    "partially_refunded": ["refunded"],
    "refunded": [],
    "voided": [],
    "failed": ["pending"],  # Can retry
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def send_notification(order_id: str, event: str, data: dict = None):
    """Send notification for order events."""
    print(f"Notification: Order {order_id} - {event}")
    # In production: send email, push notification, webhook, etc.


def update_inventory(order_id: str, action: str):
    """Update inventory based on order action."""
    print(f"Inventory: Order {order_id} - {action}")
    # In production: update inventory system


def process_payment(order_id: str, amount: float, action: str):
    """Process payment action."""
    print(f"Payment: Order {order_id} - {action} ${amount}")
    # In production: call payment gateway


# =============================================================================
# ORDER MODEL WITH ADVANCED STATE MACHINE
# =============================================================================

class Order(clearskies.Model):
    id_column_name = "id"
    backend = clearskies.backends.MemoryBackend()

    # Basic fields
    id = columns.Uuid()
    customer_id = columns.String()
    customer_email = columns.Email()
    total_amount = columns.Float()
    created_at = columns.Created()
    updated_at = columns.Updated()

    # Order status with lifecycle hooks
    order_status = columns.Select(
        ["pending", "confirmed", "processing", "shipped", "delivered", "cancelled", "returned", "refunded"],
        on_change_pre_save={
            "confirmed": lambda data, model: {
                "confirmed_at": datetime.utcnow(),
            },
            "processing": lambda data, model: {
                "processing_started_at": datetime.utcnow(),
            },
            "shipped": lambda data, model: {
                "shipped_at": datetime.utcnow(),
            },
            "delivered": lambda data, model: {
                "delivered_at": datetime.utcnow(),
            },
            "cancelled": lambda data, model: {
                "cancelled_at": datetime.utcnow(),
            },
        },
        on_change_post_save={
            "confirmed": lambda data, model, id: send_notification(id, "order_confirmed"),
            "shipped": lambda data, model, id: send_notification(id, "order_shipped"),
            "delivered": lambda data, model, id: send_notification(id, "order_delivered"),
            "cancelled": lambda data, model, id: send_notification(id, "order_cancelled"),
        },
    )

    # Payment status (independent state machine)
    payment_status = columns.Select(
        ["pending", "authorized", "captured", "refunded", "partially_refunded", "voided", "failed"],
        on_change_post_save={
            "captured": lambda data, model, id: update_inventory(id, "reserve"),
            "refunded": lambda data, model, id: update_inventory(id, "release"),
        },
    )

    # Timestamps for each state
    confirmed_at = columns.Datetime()
    processing_started_at = columns.Datetime()
    shipped_at = columns.Datetime()
    delivered_at = columns.Datetime()
    cancelled_at = columns.Datetime()

    # State history tracking
    status_history = columns.Json(default=[])

    # Shipping info
    tracking_number = columns.String()
    carrier = columns.String()

    # Cancellation/return info
    cancellation_reason = columns.String()
    return_reason = columns.String()

    def pre_save(self, data):
        """Validate state transitions and track history."""
        # Validate order status transition
        if "order_status" in data:
            current = self.order_status if self.exists else None
            new = data["order_status"]
            if new not in ORDER_TRANSITIONS.get(current, []):
                raise ValueError(
                    f"Invalid order status transition: '{current}' -> '{new}'. "
                    f"Valid transitions: {ORDER_TRANSITIONS.get(current, [])}"
                )

        # Validate payment status transition
        if "payment_status" in data:
            current = self.payment_status if self.exists else None
            new = data["payment_status"]
            if new not in PAYMENT_TRANSITIONS.get(current, []):
                raise ValueError(
                    f"Invalid payment status transition: '{current}' -> '{new}'. "
                    f"Valid transitions: {PAYMENT_TRANSITIONS.get(current, [])}"
                )

        # Track status history
        history = self.status_history.copy() if self.exists else []

        if "order_status" in data and (not self.exists or data["order_status"] != self.order_status):
            history.append({
                "type": "order_status",
                "from": self.order_status if self.exists else None,
                "to": data["order_status"],
                "timestamp": datetime.utcnow().isoformat(),
            })

        if "payment_status" in data and (not self.exists or data["payment_status"] != self.payment_status):
            history.append({
                "type": "payment_status",
                "from": self.payment_status if self.exists else None,
                "to": data["payment_status"],
                "timestamp": datetime.utcnow().isoformat(),
            })

        if history != (self.status_history if self.exists else []):
            data["status_history"] = history

        return data

    # =============================================================================
    # STATE QUERY METHODS
    # =============================================================================

    def can_confirm(self) -> bool:
        """Check if order can be confirmed."""
        return (
            self.order_status == "pending" and
            self.payment_status in ["authorized", "captured"]
        )

    def can_ship(self) -> bool:
        """Check if order can be shipped."""
        return (
            self.order_status == "processing" and
            self.payment_status == "captured"
        )

    def can_cancel(self) -> bool:
        """Check if order can be cancelled."""
        return self.order_status in ["pending", "confirmed", "processing"]

    def can_return(self) -> bool:
        """Check if order can be returned."""
        return self.order_status == "delivered"

    def can_refund(self) -> bool:
        """Check if order can be refunded."""
        return (
            self.order_status in ["cancelled", "returned"] and
            self.payment_status == "captured"
        )

    # =============================================================================
    # STATE TRANSITION METHODS
    # =============================================================================

    def confirm(self):
        """Confirm the order."""
        if not self.can_confirm():
            raise ValueError(f"Cannot confirm order in status {self.order_status}/{self.payment_status}")
        self.save({"order_status": "confirmed"})

    def start_processing(self):
        """Start processing the order."""
        if self.order_status != "confirmed":
            raise ValueError(f"Cannot start processing order in status {self.order_status}")
        self.save({"order_status": "processing"})

    def ship(self, tracking_number: str, carrier: str):
        """Ship the order."""
        if not self.can_ship():
            raise ValueError(f"Cannot ship order in status {self.order_status}/{self.payment_status}")
        self.save({
            "order_status": "shipped",
            "tracking_number": tracking_number,
            "carrier": carrier,
        })

    def mark_delivered(self):
        """Mark order as delivered."""
        if self.order_status != "shipped":
            raise ValueError(f"Cannot mark delivered order in status {self.order_status}")
        self.save({"order_status": "delivered"})

    def cancel(self, reason: str):
        """Cancel the order."""
        if not self.can_cancel():
            raise ValueError(f"Cannot cancel order in status {self.order_status}")
        self.save({
            "order_status": "cancelled",
            "cancellation_reason": reason,
        })
        # Void or refund payment if needed
        if self.payment_status == "authorized":
            self.void_payment()
        elif self.payment_status == "captured":
            self.refund_payment()

    def initiate_return(self, reason: str):
        """Initiate a return."""
        if not self.can_return():
            raise ValueError(f"Cannot return order in status {self.order_status}")
        self.save({
            "order_status": "returned",
            "return_reason": reason,
        })

    # =============================================================================
    # PAYMENT METHODS
    # =============================================================================

    def authorize_payment(self):
        """Authorize payment for the order."""
        if self.payment_status != "pending":
            raise ValueError(f"Cannot authorize payment in status {self.payment_status}")
        process_payment(self.id, self.total_amount, "authorize")
        self.save({"payment_status": "authorized"})

    def capture_payment(self):
        """Capture authorized payment."""
        if self.payment_status != "authorized":
            raise ValueError(f"Cannot capture payment in status {self.payment_status}")
        process_payment(self.id, self.total_amount, "capture")
        self.save({"payment_status": "captured"})

    def void_payment(self):
        """Void authorized payment."""
        if self.payment_status != "authorized":
            raise ValueError(f"Cannot void payment in status {self.payment_status}")
        process_payment(self.id, self.total_amount, "void")
        self.save({"payment_status": "voided"})

    def refund_payment(self, amount: float = None):
        """Refund captured payment."""
        if self.payment_status not in ["captured", "partially_refunded"]:
            raise ValueError(f"Cannot refund payment in status {self.payment_status}")
        amount = amount or self.total_amount
        process_payment(self.id, amount, "refund")
        if amount >= self.total_amount:
            self.save({"payment_status": "refunded"})
        else:
            self.save({"payment_status": "partially_refunded"})

    # =============================================================================
    # ANALYTICS METHODS
    # =============================================================================

    def get_time_in_status(self, status: str) -> float:
        """Get total time spent in a specific status (in seconds)."""
        total = 0
        for i, entry in enumerate(self.status_history):
            if entry["type"] == "order_status" and entry["to"] == status:
                start = datetime.fromisoformat(entry["timestamp"])
                # Find when we left this status
                end = None
                for j in range(i + 1, len(self.status_history)):
                    if self.status_history[j]["type"] == "order_status":
                        end = datetime.fromisoformat(self.status_history[j]["timestamp"])
                        break
                if end is None:
                    end = datetime.utcnow()
                total += (end - start).total_seconds()
        return total

    def get_processing_time(self) -> float:
        """Get total processing time from confirmed to shipped."""
        if not self.confirmed_at or not self.shipped_at:
            return 0
        return (self.shipped_at - self.confirmed_at).total_seconds()


# =============================================================================
# USAGE EXAMPLE
# =============================================================================

if __name__ == "__main__":
    # Create an order
    orders = Order()
    order = orders.create({
        "customer_id": "cust-123",
        "customer_email": "customer@example.com",
        "total_amount": 99.99,
        "order_status": "pending",
        "payment_status": "pending",
    })
    print(f"Created order: {order.id}")

    # Process payment
    order.authorize_payment()
    print(f"Payment authorized: {order.payment_status}")

    order.capture_payment()
    print(f"Payment captured: {order.payment_status}")

    # Confirm and process order
    order.confirm()
    print(f"Order confirmed: {order.order_status}")

    order.start_processing()
    print(f"Processing started: {order.order_status}")

    # Ship order
    order.ship("1Z999AA10123456784", "UPS")
    print(f"Order shipped: {order.order_status}, tracking: {order.tracking_number}")

    # Mark delivered
    order.mark_delivered()
    print(f"Order delivered: {order.order_status}")

    # Print status history
    print("\\nStatus History:")
    for entry in order.status_history:
        print(f"  {entry['type']}: {entry['from']} -> {entry['to']} at {entry['timestamp']}")

    # Try invalid transition (should raise error)
    try:
        order.cancel("Changed my mind")
    except ValueError as e:
        print(f"\\nExpected error: {e}")
```

## Key Patterns Demonstrated

1. **State Transition Validation** - Only allow valid transitions between states
2. **Multiple State Machines** - Independent order and payment status tracking
3. **State History** - Track all state changes with timestamps
4. **Lifecycle Hooks** - Automatic timestamps and notifications on state changes
5. **Business Logic Methods** - Encapsulate state transitions in methods
6. **Query Methods** - Check if transitions are allowed before attempting
7. **Analytics** - Calculate time spent in each status
'''
