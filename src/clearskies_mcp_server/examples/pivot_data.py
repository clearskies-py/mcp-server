"""
Example of many-to-many relationships with pivot data in clearskies.

This module demonstrates how to use ManyToManyIdsWithData and ManyToManyPivots
columns for relationships that need additional data on the relationship itself.
"""

import textwrap


def example_pivot_data() -> str:
    """Complete example of many-to-many relationships with pivot data."""
    return textwrap.dedent('''\
        # clearskies Many-to-Many with Pivot Data Example

        This example demonstrates how to model many-to-many relationships that need
        additional data on the relationship itself (e.g., quantity, role, permissions).

        ## Complete Example: E-commerce Order System

        ```python
        """
        Many-to-many with pivot data example.

        This script demonstrates:
        - ManyToManyIdsWithData for IDs with pivot data
        - ManyToManyPivots for accessing pivot records
        - Creating and updating relationships with data
        - Querying through pivot tables
        """
        import clearskies
        from clearskies import columns
        from clearskies.validators import Required


        # =============================================================================
        # MODEL DEFINITIONS
        # =============================================================================

        class Product(clearskies.Model):
            """Product model for the catalog."""
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            name = columns.String(validators=[Required()])
            sku = columns.String(validators=[Required()])
            price = columns.Float(validators=[Required()])
            stock_quantity = columns.Integer(default=0)
            created_at = columns.Created()


        class OrderProduct(clearskies.Model):
            """
            Pivot model for the order-product relationship.

            Defined before Order so Order can reference it.  order_id is a plain
            string because Order doesn't exist yet at this point.
            """
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            order_id = columns.String()
            product_id = columns.BelongsToId(Product)
            quantity = columns.Integer(default=1)
            unit_price = columns.Float()
            discount = columns.Float(default=0.0)

            # Load the related product
            product = columns.BelongsToModel("product_id")

            def line_total(self):
                """Calculate line item total."""
                return (self.unit_price * self.quantity) - self.discount


        class Order(clearskies.Model):
            """Order model with many-to-many relationship to products."""
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            order_number = columns.String(validators=[Required()])
            customer_name = columns.String(validators=[Required()])
            customer_email = columns.Email()
            status = columns.Select(
                ["pending", "confirmed", "shipped", "delivered", "cancelled"],
                default="pending",
            )
            created_at = columns.Created()
            updated_at = columns.Updated()

            # Many-to-many with pivot data (quantity, unit_price at time of order).
            # Reading it returns the product ids; writing it takes one dict per pivot record.
            product_ids_with_data = columns.ManyToManyIdsWithData(
                related_model_class=Product,
                pivot_model_class=OrderProduct,
                readable_pivot_column_names=["id", "product_id", "quantity", "unit_price", "discount"],
            )

            # Access to pivot records directly
            order_items = columns.ManyToManyPivots("product_ids_with_data")

            def calculate_total(self):
                """Calculate order total from line items."""
                return sum(item.line_total() for item in self.order_items)


        # =============================================================================
        # USAGE EXAMPLES
        # =============================================================================

        def main(products: Product, orders: Order, order_products: OrderProduct):
            # Create some products
            laptop = products.create({
                "name": "Gaming Laptop",
                "sku": "LAPTOP-001",
                "price": 1299.99,
                "stock_quantity": 50,
            })

            mouse = products.create({
                "name": "Wireless Mouse",
                "sku": "MOUSE-001",
                "price": 49.99,
                "stock_quantity": 200,
            })

            keyboard = products.create({
                "name": "Mechanical Keyboard",
                "sku": "KB-001",
                "price": 149.99,
                "stock_quantity": 100,
            })

            # =================================================================
            # CREATING ORDER WITH PIVOT DATA
            # =================================================================

            # Each dict identifies the product by the pivot's related id column (product_id)
            order = orders.create({
                "order_number": "ORD-2024-001",
                "customer_name": "Example User",
                "customer_email": "user@example.com",
                "product_ids_with_data": [
                    {
                        "product_id": laptop.id,
                        "quantity": 1,
                        "unit_price": laptop.price,
                        "discount": 100.00,  # $100 off laptop
                    },
                    {
                        "product_id": mouse.id,
                        "quantity": 2,
                        "unit_price": mouse.price,
                        "discount": 0,
                    },
                    {
                        "product_id": keyboard.id,
                        "quantity": 1,
                        "unit_price": keyboard.price,
                        "discount": 0,
                    },
                ],
            })

            print(f"Created order: {order.order_number}")
            print(f"Order total: ${order.calculate_total():,.2f}")

            # =================================================================
            # READING PIVOT DATA
            # =================================================================

            print("\\n=== Order Line Items ===")
            for item in order.order_items:
                print(f"  {item.product.name}")
                print(
                    f"    Qty: {item.quantity} x ${item.unit_price:.2f} "
                    f"- ${item.discount:.2f} discount = ${item.line_total():.2f}"
                )

            # =================================================================
            # UPDATING PIVOT DATA
            # =================================================================

            # Add another product to the order
            headphones = products.create({
                "name": "Wireless Headphones",
                "sku": "HP-001",
                "price": 199.99,
                "stock_quantity": 75,
            })

            # Items left out are removed, so resend the current items plus the new one
            current_items = [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "discount": item.discount,
                }
                for item in order.order_items
            ]
            current_items.append({
                "product_id": headphones.id,
                "quantity": 1,
                "unit_price": headphones.price,
                "discount": 20.00,
            })

            order.save({"product_ids_with_data": current_items})
            print(f"\\nUpdated order total: ${order.calculate_total():,.2f}")

            # =================================================================
            # QUERYING THROUGH PIVOT DATA
            # =================================================================

            print("\\n=== Orders containing Laptops ===")
            # Find all orders that contain a specific product
            for op in order_products.where(f"product_id={laptop.id}"):
                laptop_order = orders.find(f"id={op.order_id}")
                print(f"  Order: {laptop_order.order_number}, Qty: {op.quantity}")


        cli = clearskies.contexts.Cli(main, classes=[Product, Order, OrderProduct])

        if __name__ == "__main__":
            cli()
        ```

        ## REST API for Orders with Line Items

        ```python
        """
        REST API for orders with pivot data.
        """
        import clearskies

        wsgi = clearskies.contexts.WsgiRef(
            clearskies.endpoints.RestfulApi(
                url="orders",
                model_class=Order,
                readable_column_names=[
                    "id",
                    "order_number",
                    "customer_name",
                    "customer_email",
                    "status",
                    "order_items",
                    "created_at",
                ],
                writeable_column_names=[
                    "order_number",
                    "customer_name",
                    "customer_email",
                    "status",
                    "product_ids_with_data",
                ],
                searchable_column_names=["order_number", "customer_name"],
                sortable_column_names=["created_at", "order_number"],
                default_sort_column_name="created_at",
            ),
            classes=[Product, Order, OrderProduct],
        )

        if __name__ == "__main__":
            wsgi()
        ```

        ## API Usage

        ### Create Order with Line Items

        ```bash
        curl -X POST http://localhost:9090/orders \\
          -H "Content-Type: application/json" \\
          -d \'{
            "order_number": "ORD-2024-002",
            "customer_name": "Example User",
            "customer_email": "user@example.com",
            "product_ids_with_data": [
              {"product_id": "product-uuid-1", "quantity": 2, "unit_price": 49.99, "discount": 0},
              {"product_id": "product-uuid-2", "quantity": 1, "unit_price": 199.99, "discount": 10}
            ]
          }\'
        ```

        ### Update Order Line Items

        ```bash
        curl -X PUT http://localhost:9090/orders/order-uuid \\
          -H "Content-Type: application/json" \\
          -d \'{
            "product_ids_with_data": [
              {"product_id": "product-uuid-1", "quantity": 3, "unit_price": 49.99, "discount": 5},
              {"product_id": "product-uuid-2", "quantity": 1, "unit_price": 199.99, "discount": 10}
            ]
          }\'
        ```

        ## User Roles Example

        Another common use case: users with roles that have permissions.

        ```python
        class Role(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            name = columns.String(validators=[Required()])
            permissions = columns.Json()  # List of permission strings


        class UserRole(clearskies.Model):
            """Pivot model holding the extra relationship data."""
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            user_id = columns.String()
            role_id = columns.String()
            assigned_at = columns.Date()
            assigned_by = columns.String()
            expires_at = columns.Date()


        class User(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            email = columns.Email(validators=[Required()])
            name = columns.String()

            # Roles with additional data (assigned_at, assigned_by, expires_at)
            role_ids_with_data = columns.ManyToManyIdsWithData(
                related_model_class=Role,
                pivot_model_class=UserRole,
            )
            user_roles = columns.ManyToManyPivots("role_ids_with_data")


        # Assign role with metadata
        user.save({
            "role_ids_with_data": [
                {
                    "role_id": admin_role.id,
                    "assigned_at": "2024-01-15",
                    "assigned_by": "system",
                    "expires_at": None,  # Never expires
                },
                {
                    "role_id": editor_role.id,
                    "assigned_at": "2024-01-15",
                    "assigned_by": "admin-user-id",
                    "expires_at": "2024-12-31",  # Temporary role
                },
            ],
        })
        ```

        ## Best Practices

        1. **Define explicit pivot models** - For complex pivot data and querying
        2. **Index foreign keys** - In the pivot table for performance
        3. **Validate pivot data** - Ensure required fields are present
        4. **Consider data integrity** - What happens when related records are deleted?
        5. **Use transactions** - For atomic updates to pivot data
    ''')
