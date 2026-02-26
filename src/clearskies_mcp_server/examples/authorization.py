"""Authorization example for clearskies."""

import textwrap


def example_authorization() -> str:
    """Complete example of authorization patterns in clearskies."""
    return textwrap.dedent("""\
        # Example: Authorization Patterns

        This example demonstrates various authorization patterns in clearskies.

        ## Multi-Tenant Application

        ```python
        import clearskies
        from clearskies import columns
        from clearskies.validators import Required

        class TenantResource(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            tenant_id = columns.String(validators=[Required()])
            name = columns.String(validators=[Required()])
            data = columns.Json()
            created_at = columns.Created()

            def where_for_request(
                self,
                model,
                input_output,
                routing_data,
                authorization_data,
                overrides={},
            ):
                # Get tenant_id from JWT claims
                tenant_id = authorization_data.get("tenant_id")

                if not tenant_id:
                    # No tenant context - return empty results
                    return model.where("1=0")

                # Filter to only show tenant's resources
                return model.where(f"tenant_id={tenant_id}")

        wsgi = clearskies.contexts.WsgiRef(
            clearskies.endpoints.RestfulApi(
                url="resources",
                model_class=TenantResource,
                authentication=clearskies.authentication.Jwks(
                    jwks_url="https://auth.example.com/.well-known/jwks.json",
                    claims_to_authorization_data={
                        "tenant_id": "https://example.com/tenant_id",
                    },
                ),
                readable_column_names=["id", "name", "data", "created_at"],
                writeable_column_names=["name", "data"],
                default_sort_column_name="name",
            ),
            classes=[TenantResource],
        )

        if __name__ == "__main__":
            wsgi()
        ```

        ## Role-Based Access Control (RBAC)

        ```python
        import clearskies
        from clearskies import columns
        from clearskies.validators import Required

        class Document(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            title = columns.String(validators=[Required()])
            content = columns.String()
            classification = columns.Select(["public", "internal", "confidential", "secret"])
            created_at = columns.Created()

            def where_for_request(
                self,
                model,
                input_output,
                routing_data,
                authorization_data,
                overrides={},
            ):
                user_role = authorization_data.get("role", "guest")
                clearance_levels = {
                    "guest": ["public"],
                    "employee": ["public", "internal"],
                    "manager": ["public", "internal", "confidential"],
                    "admin": ["public", "internal", "confidential", "secret"],
                }

                allowed = clearance_levels.get(user_role, ["public"])
                return model.where(f"classification in {','.join(allowed)}")

        # Create endpoint with different permissions for read vs write
        def create_document(
            documents: Document,
            request_data: dict,
            authorization_data: dict,
        ):
            user_role = authorization_data.get("role", "guest")

            # Only managers and admins can create documents
            if user_role not in ["manager", "admin"]:
                return {"error": "Insufficient permissions"}, 403

            # Admins can create any classification, managers up to confidential
            classification = request_data.get("classification", "internal")
            if user_role == "manager" and classification == "secret":
                return {"error": "Managers cannot create secret documents"}, 403

            doc = documents.create(request_data)
            return {"id": doc.id, "title": doc.title, "classification": doc.classification}

        wsgi = clearskies.contexts.WsgiRef(
            clearskies.EndpointGroup(
                endpoints=[
                    clearskies.endpoints.RestfulApi(
                        url="documents",
                        model_class=Document,
                        authentication=clearskies.authentication.Jwks(
                            jwks_url="https://auth.example.com/.well-known/jwks.json",
                            claims_to_authorization_data={"role": "role"},
                        ),
                        readable_column_names=["id", "title", "content", "classification", "created_at"],
                        writeable_column_names=[],  # Read-only via REST
                        default_sort_column_name="title",
                    ),
                    clearskies.endpoints.Callable(
                        create_document,
                        url="documents/create",
                        request_methods=["POST"],
                        model_class=Document,
                        authentication=clearskies.authentication.Jwks(
                            jwks_url="https://auth.example.com/.well-known/jwks.json",
                            claims_to_authorization_data={"role": "role"},
                        ),
                    ),
                ],
            ),
            classes=[Document],
        )

        if __name__ == "__main__":
            wsgi()
        ```

        ## Resource Ownership

        ```python
        import clearskies
        from clearskies import columns
        from clearskies.validators import Required

        class UserProfile(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            user_id = columns.String(validators=[Required()])  # Owner
            display_name = columns.String()
            bio = columns.String()
            is_public = columns.Boolean()
            created_at = columns.Created()
            updated_at = columns.Updated()

            def where_for_request(
                self,
                model,
                input_output,
                routing_data,
                authorization_data,
                overrides={},
            ):
                user_id = authorization_data.get("sub")

                # Users can see:
                # 1. Their own profile
                # 2. Public profiles
                if user_id:
                    return model.where(f"user_id={user_id}").union(
                        model.where("is_public=1")
                    )
                else:
                    # Unauthenticated users only see public profiles
                    return model.where("is_public=1")

        def update_profile(
            user_profiles: UserProfile,
            routing_data: dict,
            request_data: dict,
            authorization_data: dict,
            input_output,
        ):
            profile_id = routing_data.get("id")
            user_id = authorization_data.get("sub")

            profile = user_profiles.find(f"id={profile_id}")
            if not profile.exists:
                return input_output.respond_json(
                    {"status": "client_error", "error": "Profile not found"},
                    404,
                )

            # Only owner can update their profile
            if profile.user_id != user_id:
                return input_output.respond_json(
                    {"status": "client_error", "error": "Access denied"},
                    403,
                )

            profile.save(request_data)
            return {
                "status": "success",
                "data": {
                    "id": profile.id,
                    "display_name": profile.display_name,
                    "bio": profile.bio,
                    "is_public": profile.is_public,
                },
            }

        wsgi = clearskies.contexts.WsgiRef(
            clearskies.EndpointGroup(
                endpoints=[
                    clearskies.endpoints.List(
                        url="profiles",
                        model_class=UserProfile,
                        authentication=clearskies.authentication.Jwks(
                            jwks_url="https://auth.example.com/.well-known/jwks.json",
                            claims_to_authorization_data={"sub": "sub"},
                        ),
                        readable_column_names=["id", "display_name", "bio", "is_public"],
                        default_sort_column_name="display_name",
                    ),
                    clearskies.endpoints.Callable(
                        update_profile,
                        url="profiles/:id",
                        request_methods=["PUT"],
                        model_class=UserProfile,
                        authentication=clearskies.authentication.Jwks(
                            jwks_url="https://auth.example.com/.well-known/jwks.json",
                            claims_to_authorization_data={"sub": "sub"},
                        ),
                    ),
                ],
            ),
            classes=[UserProfile],
        )

        if __name__ == "__main__":
            wsgi()
        ```

        ## Usage Examples

        ```bash
        # List documents (filtered by role)
        curl 'http://localhost:8080/documents' \\
            -H 'Authorization: Bearer <jwt-token>'

        # Create document (requires manager/admin role)
        curl 'http://localhost:8080/documents/create' \\
            -H 'Authorization: Bearer <jwt-token>' \\
            -d '{"title": "New Doc", "content": "...", "classification": "internal"}'

        # Update own profile
        curl -X PUT 'http://localhost:8080/profiles/<profile-id>' \\
            -H 'Authorization: Bearer <jwt-token>' \\
            -d '{"display_name": "New Name", "bio": "Updated bio"}'
        ```
    """)
