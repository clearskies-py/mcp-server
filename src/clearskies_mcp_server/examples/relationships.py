"""Model relationships example for clearskies."""

import textwrap


def example_relationships() -> str:
    """Return example of clearskies models with relationships."""
    return textwrap.dedent("""\
        # Example: Model Relationships

        ```python
        import clearskies
        from clearskies import columns
        from clearskies.validators import Required

        class Category(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            name = columns.String(validators=[Required()])

        class Product(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            name = columns.String(validators=[Required()])
            price = columns.Float(validators=[Required()])
            category_id = columns.BelongsToId(Category, readable_parent_columns=["id", "name"])
            category = columns.BelongsToModel("category_id")
            created_at = columns.Created()

        class Order(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            customer_name = columns.String(validators=[Required()])
            product_ids = columns.ManyToManyIds(Product, pivot_table_name="order_products")
            products = columns.ManyToManyModels("product_ids")
            created_at = columns.Created()
        ```

        ## Relationship Types

        - **BelongsToId** – Foreign key to a parent model
        - **BelongsToModel** – Auto-loads the parent model from a foreign key column
        - **HasMany** – One-to-many relationship (defined on the parent)
        - **HasOne** – One-to-one relationship
        - **ManyToManyIds** – Many-to-many via pivot table (stores/returns ids)
        - **ManyToManyModels** – Many-to-many (returns full model instances)
        - **BelongsToSelf** – Self-referencing relationship
        - **HasManySelf** – Self-referencing one-to-many
    """)
