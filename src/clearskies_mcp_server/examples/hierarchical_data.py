"""
Example of hierarchical data (CategoryTree) in clearskies.

This module demonstrates how to model and work with tree-structured data
using clearskies CategoryTree columns.
"""

import textwrap


def example_hierarchical_data() -> str:
    """Complete example of hierarchical data with CategoryTree columns."""
    return textwrap.dedent('''\
        # clearskies Hierarchical Data Example

        This example demonstrates how to model tree-structured data (categories,
        organizational hierarchies, nested comments) using clearskies CategoryTree columns.

        ## Complete Example

        ```python
        """
        Hierarchical data example with clearskies CategoryTree columns.

        This script demonstrates:
        - Self-referencing relationships with BelongsToSelf
        - CategoryTreeAncestors for parent chain
        - CategoryTreeChildren for immediate children
        - CategoryTreeDescendants for all descendants
        - Tree traversal and manipulation
        """
        import clearskies
        from clearskies import columns
        from clearskies.validators import Required


        # =============================================================================
        # MODEL DEFINITION
        # =============================================================================

        class Category(clearskies.Model):
            """
            Category model with hierarchical structure.

            Supports unlimited nesting depth with efficient tree traversal.
            """
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            name = columns.String(max_length=255, validators=[Required()])
            description = columns.String()
            slug = columns.String(max_length=255)

            # Self-referencing foreign key for parent
            parent_id = columns.BelongsToSelf()

            # Tree navigation columns
            parent = columns.BelongsToModel(
                parent_model_class="Category",
                parent_id_column_name="parent_id",
            )
            ancestors = columns.CategoryTreeAncestors(
                parent_id_column_name="parent_id",
            )
            children = columns.CategoryTreeChildren(
                parent_id_column_name="parent_id",
            )
            descendants = columns.CategoryTreeDescendants(
                parent_id_column_name="parent_id",
            )

            # Auto-generate slug from name
            def pre_save(self, data):
                if "name" in data and not data.get("slug"):
                    data["slug"] = data["name"].lower().replace(" ", "-")
                return data


        # =============================================================================
        # USAGE EXAMPLES
        # =============================================================================

        def main():
            # Get a model instance for querying
            categories = Category()

            # Create root categories
            electronics = categories.create({
                "name": "Electronics",
                "description": "Electronic devices and accessories",
            })

            clothing = categories.create({
                "name": "Clothing",
                "description": "Apparel and fashion items",
            })

            # Create subcategories under Electronics
            computers = categories.create({
                "name": "Computers",
                "description": "Desktop and laptop computers",
                "parent_id": electronics.id,
            })

            phones = categories.create({
                "name": "Phones",
                "description": "Mobile phones and smartphones",
                "parent_id": electronics.id,
            })

            # Create deeper nesting
            laptops = categories.create({
                "name": "Laptops",
                "description": "Portable computers",
                "parent_id": computers.id,
            })

            desktops = categories.create({
                "name": "Desktops",
                "description": "Desktop computers",
                "parent_id": computers.id,
            })

            gaming_laptops = categories.create({
                "name": "Gaming Laptops",
                "description": "High-performance gaming laptops",
                "parent_id": laptops.id,
            })

            # =================================================================
            # TREE TRAVERSAL EXAMPLES
            # =================================================================

            print("=== Tree Structure ===")
            print_tree(electronics)

            print("\\n=== Ancestors of Gaming Laptops ===")
            # Get all ancestors (parent chain to root)
            for ancestor in gaming_laptops.ancestors:
                print(f"  - {ancestor.name}")
            # Output:
            #   - Laptops
            #   - Computers
            #   - Electronics

            print("\\n=== Children of Electronics ===")
            # Get immediate children only
            for child in electronics.children:
                print(f"  - {child.name}")
            # Output:
            #   - Computers
            #   - Phones

            print("\\n=== All Descendants of Electronics ===")
            # Get all descendants (children, grandchildren, etc.)
            for descendant in electronics.descendants:
                print(f"  - {descendant.name}")
            # Output:
            #   - Computers
            #   - Phones
            #   - Laptops
            #   - Desktops
            #   - Gaming Laptops

            print("\\n=== Breadcrumb Navigation ===")
            # Build breadcrumb path
            breadcrumbs = build_breadcrumbs(gaming_laptops)
            print(" > ".join(breadcrumbs))
            # Output: Electronics > Computers > Laptops > Gaming Laptops

            print("\\n=== Root Categories ===")
            # Find all root categories (no parent)
            roots = categories.where("parent_id is null")
            for root in roots:
                print(f"  - {root.name}")


        def print_tree(category, indent=0):
            """Recursively print category tree."""
            prefix = "  " * indent
            print(f"{prefix}- {category.name}")
            for child in category.children:
                print_tree(child, indent + 1)


        def build_breadcrumbs(category):
            """Build breadcrumb path from root to category."""
            # Ancestors are returned from immediate parent to root
            # Reverse to get root-to-current order
            path = [ancestor.name for ancestor in reversed(list(category.ancestors))]
            path.append(category.name)
            return path


        if __name__ == "__main__":
            main()
        ```

        ## REST API for Categories

        ```python
        """
        REST API endpoint for hierarchical categories.
        """
        import clearskies

        # Reuse the Category model from above

        wsgi = clearskies.contexts.WsgiRef(
            clearskies.endpoints.RestfulApi(
                url="categories",
                model_class=Category,
                readable_column_names=[
                    "id",
                    "name",
                    "description",
                    "slug",
                    "parent_id",
                ],
                writeable_column_names=[
                    "name",
                    "description",
                    "parent_id",
                ],
                searchable_column_names=["name", "description"],
                sortable_column_names=["name"],
                default_sort_column_name="name",
            )
        )

        if __name__ == "__main__":
            wsgi()
        ```

        ## API Usage Examples

        ### Create Root Category

        ```bash
        curl -X POST http://localhost:9090/categories \\
          -H "Content-Type: application/json" \\
          -d \'{"name": "Electronics", "description": "Electronic devices"}\'
        ```

        ### Create Subcategory

        ```bash
        curl -X POST http://localhost:9090/categories \\
          -H "Content-Type: application/json" \\
          -d \'{"name": "Computers", "parent_id": "electronics-uuid-here"}\'
        ```

        ### Get Category with Tree Info

        ```bash
        curl http://localhost:9090/categories/category-uuid-here
        ```

        ### List Root Categories

        ```bash
        curl "http://localhost:9090/categories?parent_id=null"
        ```

        ## Best Practices

        1. **Index the parent_id column** - Essential for tree traversal performance
        2. **Limit tree depth** - Very deep trees can impact performance
        3. **Cache tree structures** - For frequently accessed hierarchies
        4. **Use materialized paths** - For very large trees (custom implementation)
        5. **Validate circular references** - Prevent parent pointing to descendant

        ## Preventing Circular References

        ```python
        class Category(clearskies.Model):
            # ... columns ...

            def pre_save(self, data):
                if "parent_id" in data and data["parent_id"]:
                    # Check if new parent is a descendant
                    if self.id:  # Only for updates
                        descendant_ids = [d.id for d in self.descendants]
                        if data["parent_id"] in descendant_ids:
                            raise ValueError("Cannot set parent to a descendant")
                return data
        ```
    ''')
