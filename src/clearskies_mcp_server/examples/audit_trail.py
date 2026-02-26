"""
Example of audit trail tracking in clearskies.

This module demonstrates how to use the Audit column to track
changes to records over time.
"""

import textwrap


def example_audit_trail() -> str:
    """Complete example of audit trail tracking with the Audit column."""
    return textwrap.dedent('''\
        # clearskies Audit Trail Example

        This example demonstrates how to track changes to records using the
        clearskies Audit column for compliance, debugging, and history tracking.

        ## Complete Example

        ```python
        """
        Audit trail example with clearskies Audit column.

        This script demonstrates:
        - Setting up audit tracking on specific columns
        - Accessing audit history
        - Querying audit records
        - Building audit reports
        """
        import clearskies
        from clearskies import columns
        from clearskies.validators import Required
        from datetime import datetime


        # =============================================================================
        # MODEL DEFINITIONS
        # =============================================================================

        class Document(clearskies.Model):
            """
            Document model with audit trail tracking.

            Tracks changes to title, content, and status fields.
            """
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            title = columns.String(max_length=255, validators=[Required()])
            content = columns.String()
            status = columns.Select(
                ["draft", "review", "approved", "published", "archived"],
                default="draft",
            )
            author_id = columns.String()  # Reference to user
            created_at = columns.Created()
            updated_at = columns.Updated()

            # Audit trail - tracks changes to specified columns
            audit = columns.Audit(
                audit_columns=["title", "content", "status"],
            )


        class Contract(clearskies.Model):
            """
            Contract model with comprehensive audit tracking.

            For compliance, tracks all significant field changes.
            """
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            contract_number = columns.String(max_length=50, validators=[Required()])
            client_name = columns.String(max_length=255, validators=[Required()])
            amount = columns.Float()
            status = columns.Select(
                ["draft", "pending_approval", "approved", "signed", "expired", "terminated"],
                default="draft",
            )
            effective_date = columns.Date()
            expiration_date = columns.Date()
            terms = columns.String()
            created_at = columns.Created()
            updated_at = columns.Updated()

            # Track changes to all business-critical fields
            audit = columns.Audit(
                audit_columns=[
                    "client_name",
                    "amount",
                    "status",
                    "effective_date",
                    "expiration_date",
                    "terms",
                ],
            )


        # =============================================================================
        # USAGE EXAMPLES
        # =============================================================================

        def main():
            documents = Document()

            # Create a document
            doc = documents.create({
                "title": "Project Proposal",
                "content": "Initial draft of the project proposal.",
                "author_id": "user-123",
            })
            print(f"Created document: {doc.id}")

            # Make some changes
            doc.save({"title": "Project Proposal v2"})
            doc.save({"content": "Updated content with more details."})
            doc.save({"status": "review"})
            doc.save({"status": "approved"})

            # =================================================================
            # ACCESSING AUDIT HISTORY
            # =================================================================

            print("\\n=== Audit History ===")
            for audit_record in doc.audit:
                print(f"  Changed: {audit_record.column_name}")
                print(f"    From: {audit_record.old_value}")
                print(f"    To: {audit_record.new_value}")
                print(f"    At: {audit_record.created_at}")
                print()

            # =================================================================
            # BUILDING AUDIT REPORTS
            # =================================================================

            print("\\n=== Status Change History ===")
            status_changes = [a for a in doc.audit if a.column_name == "status"]
            for change in status_changes:
                print(f"  {change.old_value} -> {change.new_value} at {change.created_at}")

            print("\\n=== Title Revision History ===")
            title_changes = [a for a in doc.audit if a.column_name == "title"]
            for i, change in enumerate(title_changes, 1):
                print(f"  v{i}: {change.new_value}")


        def compliance_report(contract):
            """Generate a compliance report for a contract."""
            print(f"\\n=== Compliance Report for Contract {contract.contract_number} ===")
            print(f"Current Status: {contract.status}")
            print(f"Client: {contract.client_name}")
            print(f"Amount: ${contract.amount:,.2f}")

            print("\\nChange History:")
            for audit_record in contract.audit:
                print(f"  [{audit_record.created_at}] {audit_record.column_name}:")
                print(f"    Changed from \'{audit_record.old_value}\' to \'{audit_record.new_value}\'")

            # Count changes by field
            print("\\nChange Summary:")
            field_counts = {}
            for audit_record in contract.audit:
                field_counts[audit_record.column_name] = field_counts.get(audit_record.column_name, 0) + 1
            for field, count in sorted(field_counts.items()):
                print(f"  {field}: {count} change(s)")


        if __name__ == "__main__":
            main()
        ```

        ## REST API with Audit Trail

        ```python
        """
        REST API that exposes audit history.
        """
        import clearskies

        # Custom endpoint to get audit history
        def get_document_audit(document_id: str, documents: Document):
            """Get audit history for a specific document."""
            doc = documents.find(f"id={document_id}")
            if not doc.exists:
                return {"error": "Document not found"}, 404

            audit_history = []
            for audit_record in doc.audit:
                audit_history.append({
                    "column": audit_record.column_name,
                    "old_value": audit_record.old_value,
                    "new_value": audit_record.new_value,
                    "changed_at": str(audit_record.created_at),
                })

            return {
                "document_id": document_id,
                "audit_history": audit_history,
            }

        # Endpoint group with CRUD and audit endpoint
        endpoints = clearskies.endpoints.EndpointGroup(
            endpoints=[
                clearskies.endpoints.RestfulApi(
                    url="documents",
                    model_class=Document,
                    readable_column_names=["id", "title", "content", "status", "created_at", "updated_at"],
                    writeable_column_names=["title", "content", "status"],
                    default_sort_column_name="created_at",
                ),
                clearskies.endpoints.Callable(
                    url="documents/:document_id/audit",
                    handler=get_document_audit,
                ),
            ],
        )

        wsgi = clearskies.contexts.WsgiRef(endpoints)

        if __name__ == "__main__":
            wsgi()
        ```

        ## API Usage

        ### Get Document Audit History

        ```bash
        curl http://localhost:9090/documents/doc-uuid-here/audit
        ```

        Response:
        ```json
        {
          "document_id": "doc-uuid-here",
          "audit_history": [
            {
              "column": "title",
              "old_value": "Project Proposal",
              "new_value": "Project Proposal v2",
              "changed_at": "2024-01-15 10:30:00"
            },
            {
              "column": "status",
              "old_value": "draft",
              "new_value": "review",
              "changed_at": "2024-01-15 11:00:00"
            }
          ]
        }
        ```

        ## Best Practices

        1. **Audit only important columns** - Don\'t audit auto-updated timestamps
        2. **Consider storage implications** - Audit tables can grow large
        3. **Index audit tables** - For efficient querying by record ID and date
        4. **Implement retention policies** - Archive or delete old audit records
        5. **Include user context** - Track who made changes (via authorization_data)
        6. **Use for compliance** - Financial, healthcare, legal requirements

        ## Adding User Context to Audit

        ```python
        class Document(clearskies.Model):
            # ... columns ...

            # Track who made changes
            last_modified_by = columns.CreatedByAuthorizationData(
                authorization_data_key="user_id",
            )

            audit = columns.Audit(
                audit_columns=["title", "content", "status", "last_modified_by"],
            )
        ```
    ''')
