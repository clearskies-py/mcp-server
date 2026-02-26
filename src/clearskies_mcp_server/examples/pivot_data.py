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
            name = columns.String(max_length=255, validators=[Required()])
            sku = columns.String(max_length=50, validators=[Required()])
            price = columns.Float(validators=[Required()])
            stock_quantity = columns.Integer(default=0)
            created_at = columns.Created()


        class Order(clearskies.Model):
            """Order model with many-to-many relationship to products."""
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            order_number = columns.String(max_length=50, validators=[Required()])
            customer_name = columns.String(max_length=255, validators=[Required()])
            customer_email = columns.Email(max_length=255)
            status = columns.Select(
                ["pending", "confirmed", "shipped", "delivered", "cancelled"],
                default="pending",
            )
            created_at = columns.Created()
            updated_at = columns.Updated()

            # Many-to-many with pivot data (quantity, unit_price at time of order)
            product_ids_with_data = columns.ManyToManyIdsWithData(
                related_model_class=Product,
                pivot_table="order_products",
                pivot_data_columns=["quantity", "unit_price", "discount"],
            )

            # Access to pivot records directly
            order_items = columns.ManyToManyPivots(
                pivot_model_class="OrderProduct",
            )

            def calculate_total(self):
                """Calculate order total from line items."""
                total = 0
                for item in self.product_ids_with_data:
                    quantity = item.get("quantity", 1)
                    unit_price = item.get("unit_price", 0)
                    discount = item.get("discount", 0)
                    total += (unit_price * quantity) - discount
                return total


        class OrderProduct(clearskies.Model):
            """Pivot model for order-product relationship."""
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            order_id = columns.BelongsToId(parent_model_class=Order)
            product_id = columns.BelongsToId(parent_model_class=Product)
            quantity = columns.Integer(default=1, validators=[Required()])
            unit_price = columns.Float(validators=[Required()])
            discount = columns.Float(default=0)

            # Load related models
            order = columns.BelongsToModel(
                parent_model_class=Order,
                parent_id_column_name="order_id",
            )
            product = columns.BelongsToModel(
                parent_model_class=Product,
                parent_id_column_name="product_id",
            )

            def line_total(self):
                """Calculate line item total."""
                return (self.unit_price * self.quantity) - self.discount


        # =============================================================================
        # USAGE EXAMPLES
        # =============================================================================

        def main():
            products = Product()
            orders = Order()

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

            order = orders.create({
                "order_number": "ORD-2024-001",
                "customer_name": "John Doe",
                "customer_email": "john@example.com",
                "product_ids_with_data": [
                    {
                        "id": laptop.id,
                        "quantity": 1,
                        "unit_price": laptop.price,
                        "discount": 100.00,  # $100 off laptop
                    },
                    {
                        "id": mouse.id,
                        "quantity": 2,
                        "unit_price": mouse.price,
                        "discount": 0,
                    },
                    {
                        "id": keyboard.id,
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
            for item in order.product_ids_with_data:
                product = products.find(f"id={item[\'id\']}")
                qty = item["quantity"]
                price = item["unit_price"]
                discount = item["discount"]
                line_total = (price * qty) - discount
                print(f"  {product.name}")
                print(f"    Qty: {qty} x ${price:.2f} - ${discount:.2f} discount = ${line_total:.2f}")

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

            # Get current items and add new one
            current_items = list(order.product_ids_with_data)
            current_items.append({
                "id": headphones.id,
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
            order_products = OrderProduct()
            laptop_orders = order_products.where(f"product_id={laptop.id}")
            for op in laptop_orders:
                print(f"  Order: {op.order.order_number}, Qty: {op.quantity}")


        if __name__ == "__main__":
            main()
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
                    "product_ids_with_data",
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
            )
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
            "customer_name": "Jane Smith",
            "customer_email": "jane@example.com",
            "product_ids_with_data": [
              {"id": "product-uuid-1", "quantity": 2, "unit_price": 49.99, "discount": 0},
              {"id": "product-uuid-2", "quantity": 1, "unit_price": 199.99, "discount": 10}
            ]
          }\'
        ```

        ### Update Order Line Items

        ```bash
        curl -X PUT http://localhost:9090/orders/order-uuid \\
          -H "Content-Type: application/json" \\
          -d \'{
            "product_ids_with_data": [
              {"id": "product-uuid-1", "quantity": 3, "unit_price": 49.99, "discount": 5},
              {"id": "product-uuid-2", "quantity": 1, "unit_price": 199.99, "discount": 10}
            ]
          }\'
        ```

        ## User Roles Example

        Another common use case: users with roles that have permissions.

        ```python
        class User(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            email = columns.Email(validators=[Required()])
            name = columns.String(max_length=255)

            # Roles with additional data (assigned_at, assigned_by, expires_at)
            role_ids_with_data = columns.ManyToManyIdsWithData(
                related_model_class="Role",
                pivot_table="user_roles",
                pivot_data_columns=["assigned_at", "assigned_by", "expires_at"],
            )


        class Role(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            name = columns.String(max_length=100, validators=[Required()])
            permissions = columns.Json()  # List of permission strings


        # Assign role with metadata
        user.save({
            "role_ids_with_data": [
                {
                    "id": admin_role.id,
                    "assigned_at": "2024-01-15",
                    "assigned_by": "system",
                    "expires_at": None,  # Never expires
                },
                {
                    "id": editor_role.id,
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
