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
        - Setting up audit tracking with an audit model
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

        class AuditRecord(clearskies.Model):
            """
            Audit model shared by all audited models.

            The Audit column requires exactly these column names.
            """
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            class_name = columns.String()
            resource_id = columns.String()
            action = columns.String()  # create, update, or delete
            data = columns.Json()  # changed values ({"from": ..., "to": ...} for updates)
            created_at = columns.Created(date_format="%Y-%m-%d %H:%M:%S.%f")


        class Document(clearskies.Model):
            """
            Document model with audit trail tracking.

            Every create/update/delete is recorded in AuditRecord.
            """
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            title = columns.String(validators=[Required()])
            content = columns.String()
            status = columns.Select(
                ["draft", "review", "approved", "published", "archived"],
                default="draft",
            )
            author_id = columns.String()  # Reference to user
            created_at = columns.Created()
            updated_at = columns.Updated()

            # Audit trail - don't record changes to auto-updated timestamps
            audit = columns.Audit(
                audit_model_class=AuditRecord,
                exclude_columns=["created_at", "updated_at"],
            )


        class Contract(clearskies.Model):
            """
            Contract model with comprehensive audit tracking.

            For compliance, tracks all significant field changes.
            """
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            contract_number = columns.String(validators=[Required()])
            client_name = columns.String(validators=[Required()])
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

            # Record every business-critical change, but hide the terms text in the audit log
            audit = columns.Audit(
                audit_model_class=AuditRecord,
                exclude_columns=["created_at", "updated_at"],
                mask_columns=["terms"],
            )


        # =============================================================================
        # USAGE EXAMPLES
        # =============================================================================

        def main(documents: Document):
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
            for audit_record in doc.audit.sort_by("created_at", "asc"):
                print(f"  Action: {audit_record.action}")
                print(f"    Data: {audit_record.data}")
                print(f"    At: {audit_record.created_at}")
                print()

            # =================================================================
            # BUILDING AUDIT REPORTS
            # =================================================================

            print("\\n=== Status Change History ===")
            for change in doc.audit.where("action=update").sort_by("created_at", "asc"):
                if "status" in change.data.get("to", {}):
                    print(f"  {change.data['from'].get('status')} -> {change.data['to']['status']} at {change.created_at}")


        def compliance_report(contract):
            """Generate a compliance report for a contract."""
            print(f"\\n=== Compliance Report for Contract {contract.contract_number} ===")
            print(f"Current Status: {contract.status}")
            print(f"Client: {contract.client_name}")
            print(f"Amount: ${contract.amount:,.2f}")

            print("\\nChange History:")
            for audit_record in contract.audit.sort_by("created_at", "asc"):
                print(f"  [{audit_record.created_at}] {audit_record.action}: {audit_record.data}")

            # Count changes by field
            print("\\nChange Summary:")
            field_counts = {}
            for audit_record in contract.audit.where("action=update"):
                for field in audit_record.data.get("to", {}):
                    field_counts[field] = field_counts.get(field, 0) + 1
            for field, count in sorted(field_counts.items()):
                print(f"  {field}: {count} change(s)")


        cli = clearskies.contexts.Cli(main, classes=[Document, Contract, AuditRecord])

        if __name__ == "__main__":
            cli()
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
            if not doc:
                raise clearskies.exceptions.NotFound("Document not found")

            audit_history = []
            for audit_record in doc.audit.sort_by("created_at", "asc"):
                audit_history.append({
                    "action": audit_record.action,
                    "data": audit_record.data,
                    "changed_at": str(audit_record.created_at),
                })

            return {
                "document_id": document_id,
                "audit_history": audit_history,
            }

        # Endpoint group with CRUD and audit endpoint
        endpoints = clearskies.EndpointGroup(
            [
                clearskies.endpoints.RestfulApi(
                    url="documents",
                    model_class=Document,
                    readable_column_names=["id", "title", "content", "status", "created_at", "updated_at"],
                    writeable_column_names=["title", "content", "status"],
                    searchable_column_names=["title", "content", "status"],
                    sortable_column_names=["created_at"],
                    default_sort_column_name="created_at",
                ),
                clearskies.endpoints.Callable(
                    get_document_audit,
                    url="documents/:document_id/audit",
                ),
            ],
        )

        wsgi = clearskies.contexts.WsgiRef(endpoints, classes=[Document, AuditRecord])

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
              "action": "update",
              "data": {"from": {"title": "Project Proposal"}, "to": {"title": "Project Proposal v2"}},
              "changed_at": "2024-01-15 10:30:00.000000"
            },
            {
              "action": "update",
              "data": {"from": {"status": "draft"}, "to": {"status": "review"}},
              "changed_at": "2024-01-15 11:00:00.000000"
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

            # Record who created the record (read from the authorization data)
            created_by = columns.CreatedByAuthorizationData("user_id")

            audit = columns.Audit(
                audit_model_class=AuditRecord,
                exclude_columns=["created_at", "updated_at"],
            )
        ```
    ''')
