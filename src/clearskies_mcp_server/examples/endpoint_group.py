"""Endpoint group example for clearskies."""

import textwrap


def example_endpoint_group() -> str:
    """Complete example of clearskies endpoint groups."""
    return textwrap.dedent("""\
        # Example: Endpoint Groups

        This example demonstrates how to organize multiple endpoints using EndpointGroup.

        ## Complete Multi-Endpoint API

        ```python
        import clearskies
        from clearskies import columns
        from clearskies.validators import Required

        # Models
        class User(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            name = columns.String(validators=[Required()])
            email = columns.Email(validators=[Required()])
            role = columns.Select(["user", "admin", "moderator"])
            created_at = columns.Created()

        class Post(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()

            id = columns.Uuid()
            title = columns.String(validators=[Required()])
            content = columns.String()
            author_id = columns.String()
            status = columns.Select(["draft", "published", "archived"])
            created_at = columns.Created()
            updated_at = columns.Updated()

        # Custom handlers
        def get_stats(users: User, posts: Post):
            return {
                "total_users": len(list(users)),
                "total_posts": len(list(posts)),
                "published_posts": len(list(posts.where("status=published"))),
            }

        def publish_post(posts: Post, routing_data: dict, input_output):
            post = posts.find(f"id={routing_data['id']}")
            if not post.exists:
                return input_output.respond_json(
                    {"status": "client_error", "error": "Post not found", "data": [], "pagination": {}, "input_errors": {}},
                    404,
                )
            post.save({"status": "published"})
            return {"id": post.id, "status": post.status}

        # Application with endpoint groups
        wsgi = clearskies.contexts.WsgiRef(
            clearskies.EndpointGroup(
                url="/api/v1",
                endpoints=[
                    # Users API
                    clearskies.endpoints.RestfulApi(
                        url="users",
                        model_class=User,
                        readable_column_names=["id", "name", "email", "role", "created_at"],
                        writeable_column_names=["name", "email", "role"],
                        sortable_column_names=["name", "created_at"],
                        searchable_column_names=["name", "email"],
                        default_sort_column_name="name",
                    ),
                    # Posts API
                    clearskies.endpoints.RestfulApi(
                        url="posts",
                        model_class=Post,
                        readable_column_names=["id", "title", "content", "author_id", "status", "created_at", "updated_at"],
                        writeable_column_names=["title", "content", "author_id", "status"],
                        sortable_column_names=["title", "created_at", "updated_at"],
                        searchable_column_names=["title", "content"],
                        default_sort_column_name="created_at",
                    ),
                    # Custom endpoints
                    clearskies.endpoints.Callable(
                        get_stats,
                        url="stats",
                        model_class=User,
                    ),
                    clearskies.endpoints.Callable(
                        publish_post,
                        url="posts/:id/publish",
                        request_methods=["POST"],
                        model_class=Post,
                    ),
                ],
            ),
            classes=[User, Post],
        )

        if __name__ == "__main__":
            wsgi()
        ```

        ## Usage

        ```bash
        # Create a user
        $ curl 'http://localhost:8080/api/v1/users' \\
            -d '{"name": "Alice", "email": "alice@example.com", "role": "admin"}' | jq
        {
            "status": "success",
            "data": {
                "id": "abc123...",
                "name": "Alice",
                "email": "alice@example.com",
                "role": "admin",
                "created_at": "2024-01-15T10:30:00Z"
            }
        }

        # Create a post
        $ curl 'http://localhost:8080/api/v1/posts' \\
            -d '{"title": "Hello World", "content": "My first post", "author_id": "abc123...", "status": "draft"}' | jq
        {
            "status": "success",
            "data": {
                "id": "post123...",
                "title": "Hello World",
                "content": "My first post",
                "author_id": "abc123...",
                "status": "draft"
            }
        }

        # Get stats
        $ curl 'http://localhost:8080/api/v1/stats' | jq
        {
            "status": "success",
            "data": {
                "total_users": 1,
                "total_posts": 1,
                "published_posts": 0
            }
        }

        # Publish a post
        $ curl 'http://localhost:8080/api/v1/posts/post123.../publish' -X POST | jq
        {
            "status": "success",
            "data": {
                "id": "post123...",
                "status": "published"
            }
        }

        # List users with search
        $ curl 'http://localhost:8080/api/v1/users?name=Alice' | jq

        # List posts sorted by date
        $ curl 'http://localhost:8080/api/v1/posts?sort=created_at&direction=desc' | jq
        ```

        ## With Authentication

        ```python
        import os
        import clearskies
        from clearskies import columns

        os.environ["API_SECRET"] = "my-secret-token"

        class SecureData(clearskies.Model):
            id_column_name = "id"
            backend = clearskies.backends.MemoryBackend()
            id = columns.Uuid()
            data = columns.String()

        wsgi = clearskies.contexts.WsgiRef(
            clearskies.EndpointGroup(
                url="/api/secure",
                authentication=clearskies.authentication.SecretBearer(
                    environment_key="API_SECRET"
                ),
                endpoints=[
                    clearskies.endpoints.RestfulApi(
                        url="data",
                        model_class=SecureData,
                        readable_column_names=["id", "data"],
                        writeable_column_names=["data"],
                        default_sort_column_name="id",
                    ),
                ],
            ),
            classes=[SecureData],
        )

        if __name__ == "__main__":
            wsgi()
        ```

        Usage with authentication:

        ```bash
        # Without auth - fails
        $ curl 'http://localhost:8080/api/secure/data'
        {"status": "client_error", "error": "Unauthorized"}

        # With auth - works
        $ curl 'http://localhost:8080/api/secure/data' \\
            -H 'Authorization: Bearer my-secret-token' | jq
        {"status": "success", "data": []}
        ```
    """)
