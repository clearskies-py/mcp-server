"""
Scaffolding tools for clearskies MCP server.

This module contains tools for scaffolding complete clearskies projects.
"""

from .generation import generate_context, generate_endpoint, generate_model


def scaffold_project(
    project_name: str,
    models: list[dict],
    context_type: str = "WsgiRef",
    endpoint_type: str = "RestfulApi",
) -> str:
    """Generate a complete clearskies project with models and endpoints.

    Returns the full file content for a working clearskies application.

    Args:
        project_name: The name of the project/application.
        models: List of model definitions. Each dict has:
            - name (str): Model class name in PascalCase
            - columns (list[dict]): Column definitions (same format as generate_model)
            - backend_type (str, optional): Backend type (default: "MemoryBackend")
            - id_column_name (str, optional): Id column name (default: "id")
            - url (str, optional): URL path for the REST API
            - readable_column_names (list[str], optional): Readable columns
            - writeable_column_names (list[str], optional): Writeable columns
            - sortable_column_names (list[str], optional): Sortable columns
            - searchable_column_names (list[str], optional): Searchable columns
            - default_sort_column_name (str, optional): Default sort column
        context_type: The context type to use (default: "WsgiRef").
        endpoint_type: Endpoint type to use (default: "RestfulApi").
    """
    # Collect all imports
    imports = {"import clearskies", "from clearskies import columns"}
    validator_names: set[str] = set()
    all_model_names: list[str] = []

    # Generate models
    model_blocks = []
    endpoint_blocks = []

    for model_def in models:
        m_name = model_def["name"]
        all_model_names.append(m_name)
        m_columns = model_def.get("columns", [])
        m_backend = model_def.get("backend_type", "MemoryBackend")
        m_id_col = model_def.get("id_column_name", "id")

        # Collect validators
        for col in m_columns:
            for v in col.get("options", {}).get("validators", []):
                if isinstance(v, str):
                    validator_names.add(v)
                elif isinstance(v, dict):
                    validator_names.add(v["name"])

        # Generate model code
        model_code = generate_model(
            name=m_name,
            columns=m_columns,
            backend_type=m_backend,
            id_column_name=m_id_col,
        )
        # Strip the import lines from individual model generations
        model_lines = []
        for line in model_code.split("\n"):
            if line.startswith("import ") or line.startswith("from "):
                continue
            model_lines.append(line)
        model_blocks.append("\n".join(model_lines).strip())

        # Generate endpoint
        url = model_def.get("url", m_name.lower() + "s")

        # Default readable columns to all column names
        readable = model_def.get("readable_column_names")
        if not readable:
            readable = [c["name"] for c in m_columns]

        writeable = model_def.get("writeable_column_names")
        if not writeable:
            writeable = [
                c["name"]
                for c in m_columns
                if c["type"]
                not in (
                    "Uuid",
                    "Created",
                    "Updated",
                    "Audit",
                    "CreatedByIp",
                    "CreatedByHeader",
                    "CreatedByAuthorizationData",
                    "CreatedByRoutingData",
                    "CreatedByUserAgent",
                )
            ]

        sortable = model_def.get("sortable_column_names", readable)
        searchable = model_def.get("searchable_column_names", readable)
        default_sort = model_def.get("default_sort_column_name", m_columns[0]["name"] if m_columns else "id")

        endpoint_code = generate_endpoint(
            endpoint_type=endpoint_type,
            model_name=m_name,
            url=url,
            readable_column_names=readable,
            writeable_column_names=writeable,
            sortable_column_names=sortable,
            searchable_column_names=searchable,
            default_sort_column_name=default_sort,
        )
        endpoint_blocks.append(endpoint_code)

    if validator_names:
        imports.add(f"from clearskies.validators import {', '.join(sorted(validator_names))}")

    # Build the file
    parts = [f'"""clearskies application: {project_name}"""', ""]
    parts.append("\n".join(sorted(imports)))
    parts.append("")

    # Add models
    for block in model_blocks:
        parts.append("")
        parts.append(block)

    parts.append("")
    parts.append("")
    parts.append("# " + "=" * 70)
    parts.append("# Application")
    parts.append("# " + "=" * 70)
    parts.append("")

    if len(endpoint_blocks) == 1:
        # Single endpoint
        endpoint_expr = endpoint_blocks[0]
    else:
        # Multiple endpoints → use EndpointGroup
        group_parts = ["clearskies.EndpointGroup("]
        group_parts.append("    endpoints=[")
        for ep in endpoint_blocks:
            ep_lines = ep.strip().split("\n")
            group_parts.append(f"        {ep_lines[0]}")
            for line in ep_lines[1:]:
                group_parts.append(f"            {line}")
            group_parts[-1] += ","
        group_parts.append("    ],")
        group_parts.append(")")
        endpoint_expr = "\n".join(group_parts)

    context_code = generate_context(
        context_type=context_type,
        endpoint_code=endpoint_expr,
        classes=all_model_names,
    )

    parts.append(f"app = {context_code}")
    parts.append("")
    parts.append("")
    parts.append('if __name__ == "__main__":')
    parts.append("    app()")
    parts.append("")

    return "\n".join(parts)


def scaffold_restful_api(
    model_name: str,
    columns: list[dict],
    url: str = "",
    backend_type: str = "MemoryBackend",
    backend_options: dict | None = None,
    authentication: str = "",
    context_type: str = "WsgiRef",
) -> str:
    """Generate a complete, runnable clearskies REST API application for a single model.

    This is a convenience tool that generates a model, a RestfulApi endpoint, and a context
    in a single file ready to run.

    Args:
        model_name: Model class name in PascalCase (e.g. "User").
        columns: List of column definitions. Each dict has:
            - name (str): Column name
            - type (str): Column type
            - options (dict, optional): Column constructor options
        url: URL path (default: auto-generated from model name).
        backend_type: Backend type (default: "MemoryBackend").
        backend_options: Backend constructor options.
        authentication: Authentication expression.
        context_type: Context type (default: "WsgiRef").
    """
    # Auto-generate URL from model name
    if not url:
        # Simple pluralization
        snake = ""
        for i, c in enumerate(model_name):
            if c.isupper() and i > 0:
                snake += "_"
            snake += c.lower()
        url = snake + "s"

    readable = [c["name"] for c in columns]
    writeable = [
        c["name"]
        for c in columns
        if c["type"]
        not in (
            "Uuid",
            "Created",
            "Updated",
            "Audit",
            "CreatedByIp",
            "CreatedByHeader",
            "CreatedByAuthorizationData",
            "CreatedByRoutingData",
            "CreatedByUserAgent",
        )
    ]

    return scaffold_project(
        project_name=f"{model_name} API",
        models=[
            {
                "name": model_name,
                "columns": columns,
                "backend_type": backend_type,
                "url": url,
                "readable_column_names": readable,
                "writeable_column_names": writeable,
                "sortable_column_names": readable,
                "searchable_column_names": readable,
                "default_sort_column_name": columns[0]["name"] if columns else "id",
            }
        ],
        context_type=context_type,
        endpoint_type="RestfulApi",
    )


def generate_model_with_relationships(
    models: list[dict],
) -> str:
    """Generate multiple related clearskies Model classes with their relationships properly configured.

    Use this when you need to create models with BelongsTo, HasMany, or ManyToMany relationships.

    Args:
        models: List of model definitions. Each dict has:
            - name (str): Model class name
            - columns (list[dict]): Column definitions
            - backend_type (str, optional): Backend type
            - id_column_name (str, optional): Id column name
    """
    parts = [
        "import clearskies",
        "from clearskies import columns",
        "",
    ]

    for model_def in models:
        model_code = generate_model(
            name=model_def["name"],
            columns=model_def.get("columns", []),
            backend_type=model_def.get("backend_type", "MemoryBackend"),
            id_column_name=model_def.get("id_column_name", "id"),
        )
        # Strip redundant import lines
        for line in model_code.split("\n"):
            if line.startswith("import ") or line.startswith("from "):
                continue
            parts.append(line)
        parts.append("")

    return "\n".join(parts)
