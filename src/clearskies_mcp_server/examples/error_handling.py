"""Error handling example for clearskies."""

import textwrap


def example_error_handling() -> str:
    """Complete example of error handling in clearskies."""
    return textwrap.dedent("""\
        # Example: Error Handling Patterns

        This example demonstrates comprehensive error handling in clearskies applications.

        ## Complete Application with Error Handling

        ```python
        import clearskies
        from clearskies import columns
        from clearskies.validators import Required, Unique, Validator
        import logging

        logger = logging.getLogger(__name__)

        # Custom validator with specific error message
        class PositiveNumber(Validator):
            def __init__(self, message=None):
                self.message = message

            def validate(self, value, column, model):
                if value is not None and value <= 0:
                    return self.message or f"{column.name} must be a positive number"
                return None

        class MinLength(Validator):
            def __init__(self, min_length: int):
                self.min_length = min_length

            def validate(self, value, column, model):
                if value and len(value) < self.min_length:
                    return f"Must be at least {self.min_length} characters"
                return None

        class Product(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            name = columns.String(validators=[Required(), MinLength(3)])
            sku = columns.String(validators=[Required(), Unique()])
            price = columns.Float(validators=[Required(), PositiveNumber("Price must be greater than zero")])
            stock = columns.Integer(validators=[PositiveNumber()])
            category = columns.Select(["electronics", "clothing", "food", "other"])
            created_at = columns.Created()
            updated_at = columns.Updated()

        # Custom error for business logic
        class InsufficientStockError(Exception):
            def __init__(self, product_id: str, requested: int, available: int):
                self.product_id = product_id
                self.requested = requested
                self.available = available
                super().__init__(f"Insufficient stock for product {product_id}")

        class ExternalServiceError(Exception):
            pass

        def process_order(
            products: Product,
            request_data: dict,
            input_output,
        ):
            try:
                product_id = request_data.get("product_id")
                quantity = request_data.get("quantity", 0)

                # Input validation
                errors = {}
                if not product_id:
                    errors["product_id"] = "Product ID is required"
                if not quantity or quantity <= 0:
                    errors["quantity"] = "Quantity must be a positive number"

                if errors:
                    return input_output.respond_json(
                        {
                            "status": "input_errors",
                            "error": "",
                            "data": [],
                            "pagination": {},
                            "input_errors": errors,
                        },
                        400,
                    )

                # Find product
                product = products.find(f"id={product_id}")
                if not product.exists:
                    return input_output.respond_json(
                        {
                            "status": "client_error",
                            "error": f"Product {product_id} not found",
                            "data": [],
                            "pagination": {},
                            "input_errors": {},
                        },
                        404,
                    )

                # Check stock
                if product.stock < quantity:
                    raise InsufficientStockError(product_id, quantity, product.stock)

                # Process order (simulated)
                new_stock = product.stock - quantity
                product.save({"stock": new_stock})

                return {
                    "status": "success",
                    "data": {
                        "order_id": "ord_" + product_id[:8],
                        "product_id": product_id,
                        "quantity": quantity,
                        "total": product.price * quantity,
                        "remaining_stock": new_stock,
                    },
                }

            except InsufficientStockError as e:
                logger.warning(f"Insufficient stock: {e}")
                return input_output.respond_json(
                    {
                        "status": "client_error",
                        "error": f"Insufficient stock. Requested: {e.requested}, Available: {e.available}",
                        "data": [],
                        "pagination": {},
                        "input_errors": {},
                    },
                    409,  # Conflict
                )

            except ExternalServiceError as e:
                logger.error(f"External service error: {e}")
                return input_output.respond_json(
                    {
                        "status": "failure",
                        "error": "Payment service temporarily unavailable. Please try again.",
                        "data": [],
                        "pagination": {},
                        "input_errors": {},
                    },
                    503,  # Service Unavailable
                )

            except Exception as e:
                logger.exception(f"Unexpected error processing order: {e}")
                return input_output.respond_json(
                    {
                        "status": "failure",
                        "error": "An unexpected error occurred. Please try again later.",
                        "data": [],
                        "pagination": {},
                        "input_errors": {},
                    },
                    500,
                )

        wsgi = clearskies.contexts.WsgiRef(
            clearskies.EndpointGroup(
                endpoints=[
                    clearskies.endpoints.RestfulApi(
                        url="products",
                        model_class=Product,
                        readable_column_names=["id", "name", "sku", "price", "stock", "category", "created_at"],
                        writeable_column_names=["name", "sku", "price", "stock", "category"],
                        sortable_column_names=["name", "price", "stock", "created_at"],
                        searchable_column_names=["name", "sku", "category"],
                        default_sort_column_name="name",
                    ),
                    clearskies.endpoints.Callable(
                        process_order,
                        url="orders",
                        request_methods=["POST"],
                        model_class=Product,
                    ),
                ],
            ),
            classes=[Product],
        )

        if __name__ == "__main__":
            wsgi()
        ```

        ## Usage Examples

        ### Successful Operations

        ```bash
        # Create a product
        $ curl 'http://localhost:8080/products' \\
            -d '{"name": "Widget", "sku": "WDG-001", "price": 29.99, "stock": 100, "category": "electronics"}' | jq
        {
            "status": "success",
            "data": {
                "id": "abc123...",
                "name": "Widget",
                "sku": "WDG-001",
                "price": 29.99,
                "stock": 100,
                "category": "electronics"
            }
        }

        # Place an order
        $ curl 'http://localhost:8080/orders' \\
            -d '{"product_id": "abc123...", "quantity": 5}' | jq
        {
            "status": "success",
            "data": {
                "order_id": "ord_abc123",
                "product_id": "abc123...",
                "quantity": 5,
                "total": 149.95,
                "remaining_stock": 95
            }
        }
        ```

        ### Validation Errors

        ```bash
        # Missing required fields
        $ curl 'http://localhost:8080/products' \\
            -d '{"name": "AB"}' | jq
        {
            "status": "input_errors",
            "error": "",
            "data": [],
            "pagination": {},
            "input_errors": {
                "name": "Must be at least 3 characters",
                "sku": "Sku is required",
                "price": "Price is required"
            }
        }

        # Invalid price
        $ curl 'http://localhost:8080/products' \\
            -d '{"name": "Widget", "sku": "WDG-002", "price": -10}' | jq
        {
            "status": "input_errors",
            "error": "",
            "data": [],
            "pagination": {},
            "input_errors": {
                "price": "Price must be greater than zero"
            }
        }

        # Duplicate SKU
        $ curl 'http://localhost:8080/products' \\
            -d '{"name": "Another Widget", "sku": "WDG-001", "price": 19.99}' | jq
        {
            "status": "input_errors",
            "error": "",
            "data": [],
            "pagination": {},
            "input_errors": {
                "sku": "Sku must be unique"
            }
        }
        ```

        ### Business Logic Errors

        ```bash
        # Product not found
        $ curl 'http://localhost:8080/orders' \\
            -d '{"product_id": "nonexistent", "quantity": 5}' | jq
        {
            "status": "client_error",
            "error": "Product nonexistent not found",
            "data": [],
            "pagination": {},
            "input_errors": {}
        }

        # Insufficient stock
        $ curl 'http://localhost:8080/orders' \\
            -d '{"product_id": "abc123...", "quantity": 1000}' | jq
        {
            "status": "client_error",
            "error": "Insufficient stock. Requested: 1000, Available: 95",
            "data": [],
            "pagination": {},
            "input_errors": {}
        }
        ```

        ### Server Errors

        ```bash
        # External service failure (returns 503)
        # (This would happen if the payment service was down)
        {
            "status": "failure",
            "error": "Payment service temporarily unavailable. Please try again.",
            "data": [],
            "pagination": {},
            "input_errors": {}
        }

        # Unexpected error (returns 500)
        {
            "status": "failure",
            "error": "An unexpected error occurred. Please try again later.",
            "data": [],
            "pagination": {},
            "input_errors": {}
        }
        ```
    """)
