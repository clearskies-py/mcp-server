"""
Code generation tools for clearskies MCP server.

This module contains tools for generating clearskies models, endpoints, and contexts.
"""

import textwrap

from ..introspection import COLUMN_TYPES, CONTEXT_TYPES, ENDPOINT_TYPES


def generate_model(
    name: str,
    columns: list[dict],
    backend_type: str = "MemoryBackend",
    backend_options: dict | None = None,
    id_column_name: str = "id",
    hooks: list[str] | None = None,
) -> str:
    """Generate a clearskies Model class definition.

    Args:
        name: The model class name in PascalCase (e.g. "User", "OrderProduct").
        columns: List of column definitions. Each dict has:
            - name (str): Column name
            - type (str): Column type (e.g. "String", "Integer", "Uuid", "BelongsToId")
            - options (dict, optional): Keyword arguments for the column constructor
        backend_type: Backend class name (default: "MemoryBackend").
        backend_options: Keyword arguments for the backend constructor.
        id_column_name: The name of the id column (default: "id").
        hooks: Optional list of hook methods to include stubs for (e.g. ["pre_save", "post_save", "save_finished"]).
    """
    backend_options = backend_options or {}
    hooks = hooks or []

    # Track imports
    imports = {"import clearskies", "from clearskies import columns"}
    validator_imports: set[str] = set()
    relationship_model_imports: set[str] = set()

    # Build column lines
    column_lines = []
    for col in columns:
        col_name = col["name"]
        col_type = col["type"]
        col_opts = col.get("options", {})

        if col_type not in COLUMN_TYPES:
            return f"Error: Unknown column type '{col_type}'. Available: {', '.join(sorted(COLUMN_TYPES))}"

        # Handle validators in options
        if "validators" in col_opts:
            validators = col_opts["validators"]
            validator_strs = []
            for v in validators:
                if isinstance(v, str):
                    validator_imports.add(v)
                    validator_strs.append(f"{v}()")
                elif isinstance(v, dict):
                    v_name = v["name"]
                    v_args = v.get("args", {})
                    validator_imports.add(v_name)
                    args_str = ", ".join(f"{k}={repr(val)}" for k, val in v_args.items())
                    validator_strs.append(f"{v_name}({args_str})")
            col_opts["validators"] = f"[{', '.join(validator_strs)}]"

        # Handle model references in relationship columns
        if col_type in ("BelongsToId", "HasMany", "ManyToManyIds", "ManyToManyModels") and "model_class" in col_opts:
            relationship_model_imports.add(col_opts["model_class"])

        # Build options string
        opt_parts = []
        for k, v in col_opts.items():
            if k == "validators":
                opt_parts.append(f"validators={v}")
            elif isinstance(v, str) and not v.startswith("["):
                # Check if it looks like a class reference
                if k in ("model_class", "parent_model_class"):
                    opt_parts.append(f"{k}={v}")
                else:
                    opt_parts.append(f"{k}={repr(v)}")
            else:
                opt_parts.append(f"{k}={v}")
        opts_str = "(" + ", ".join(opt_parts) + ")" if opt_parts else "()"
        column_lines.append(f"    {col_name} = columns.{col_type}{opts_str}")

    # Build backend string
    backend_opt_parts = []
    for k, v in backend_options.items():
        if isinstance(v, str) and (k.endswith("_class") or k == "authentication"):
            backend_opt_parts.append(f"{k}={v}")
        else:
            backend_opt_parts.append(f"{k}={repr(v)}")
    backend_opts_str = "(" + ", ".join(backend_opt_parts) + ")" if backend_opt_parts else "()"

    # Build imports
    if validator_imports:
        imports.add(f"from clearskies.validators import {', '.join(sorted(validator_imports))}")

    # Build hook stubs
    hook_stubs = []
    hook_templates = {
        "pre_save": textwrap.dedent("""\
            def pre_save(self, data: dict[str, Any]) -> dict[str, Any]:
                # Modify data before it's persisted to the backend.
                # Return a dict of additional/modified data.
                return data
        """),
        "post_save": textwrap.dedent("""\
            def post_save(self, data: dict[str, Any], id: str | int) -> None:
                # Called after the backend has been updated but before the model is updated.
                # The record id is available here.
                pass
        """),
        "save_finished": textwrap.dedent("""\
            def save_finished(self) -> None:
                # Called after the model is fully updated.
                # Use self.was_changed() and self.previous_value() here.
                pass
        """),
        "pre_delete": textwrap.dedent("""\
            def pre_delete(self) -> None:
                # Called before a record is deleted from the backend.
                pass
        """),
        "post_delete": textwrap.dedent("""\
            def post_delete(self) -> None:
                # Called after a record is deleted from the backend.
                pass
        """),
        "where_for_request": textwrap.dedent("""\
            def where_for_request(
                self,
                model,
                input_output,
                routing_data: dict[str, str],
                authorization_data: dict[str, Any],
                overrides: dict[str, clearskies.Column] = {},
            ):
                # Automatically apply filtering for list/search endpoints.
                return model
        """),
    }

    for hook in hooks:
        if hook in hook_templates:
            # Indent the hook template
            indented = "\n".join("    " + line if line.strip() else "" for line in hook_templates[hook].split("\n"))
            hook_stubs.append(indented)

    if hooks:
        imports.add("from typing import Any")

    # Assemble
    parts = ["\n".join(sorted(imports)), ""]
    for model_ref in sorted(relationship_model_imports):
        parts.append(f"# from your_models import {model_ref}")
    if relationship_model_imports:
        parts.append("")

    parts.append(f"\nclass {name}(clearskies.Model):")
    parts.append(f'    id_column_name = "{id_column_name}"')
    parts.append(f"    backend = clearskies.backends.{backend_type}{backend_opts_str}")
    parts.append("")
    parts.extend(column_lines)

    if hook_stubs:
        parts.append("")
        parts.extend(hook_stubs)

    return "\n".join(parts)


def generate_endpoint(
    endpoint_type: str,
    model_name: str,
    url: str = "",
    readable_column_names: list[str] | None = None,
    writeable_column_names: list[str] | None = None,
    sortable_column_names: list[str] | None = None,
    searchable_column_names: list[str] | None = None,
    default_sort_column_name: str = "",
    authentication: str = "",
    extra_options: dict | None = None,
) -> str:
    """Generate a clearskies endpoint configuration.

    Args:
        endpoint_type: Type of endpoint (e.g. "RestfulApi", "List", "Create", "Get", "Update", "Delete", "Callable").
        model_name: The model class name to use with this endpoint.
        url: The URL path for the endpoint (optional).
        readable_column_names: List of column names that are returned in the response.
        writeable_column_names: List of column names the client can set.
        sortable_column_names: List of column names the client can sort by.
        searchable_column_names: List of column names the client can search by.
        default_sort_column_name: The default column to sort by.
        authentication: Authentication configuration (e.g. 'clearskies.authentication.SecretBearer(environment_key="MY_SECRET")').
        extra_options: Additional keyword arguments for the endpoint constructor.
    """
    extra_options = extra_options or {}

    if endpoint_type not in ENDPOINT_TYPES:
        available = ", ".join(sorted(ENDPOINT_TYPES))
        return f"Error: Unknown endpoint type '{endpoint_type}'. Available: {available}"

    parts = []
    parts.append(f"clearskies.endpoints.{endpoint_type}(")

    opts = []
    if url:
        opts.append(f'    url="{url}",')
    opts.append(f"    model_class={model_name},")

    if readable_column_names:
        opts.append(f"    readable_column_names={repr(readable_column_names)},")
    if writeable_column_names:
        opts.append(f"    writeable_column_names={repr(writeable_column_names)},")
    if sortable_column_names:
        opts.append(f"    sortable_column_names={repr(sortable_column_names)},")
    if searchable_column_names:
        opts.append(f"    searchable_column_names={repr(searchable_column_names)},")
    if default_sort_column_name:
        opts.append(f'    default_sort_column_name="{default_sort_column_name}",')
    if authentication:
        opts.append(f"    authentication={authentication},")

    for k, v in extra_options.items():
        if isinstance(v, str):
            opts.append(f"    {k}={v},")
        else:
            opts.append(f"    {k}={repr(v)},")

    parts.extend(opts)
    parts.append(")")

    return "\n".join(parts)


def generate_context(
    context_type: str,
    endpoint_code: str,
    classes: list[str] | None = None,
    modules: list[str] | None = None,
    bindings: dict | None = None,
) -> str:
    """Generate a clearskies context configuration that wraps an endpoint.

    Args:
        context_type: The context type (e.g. "Cli", "WsgiRef", "Wsgi").
        endpoint_code: The endpoint expression to wrap (e.g. output from generate_endpoint).
        classes: List of model class names to register with DI.
        modules: List of module names to register with DI.
        bindings: Dictionary of name → value DI bindings.
    """
    if context_type not in CONTEXT_TYPES:
        available = ", ".join(sorted(CONTEXT_TYPES))
        return f"Error: Unknown context type '{context_type}'. Available: {available}"

    parts = [f"clearskies.contexts.{context_type}("]

    # Indent the endpoint code
    endpoint_lines = endpoint_code.strip().split("\n")
    parts.append(f"    {endpoint_lines[0]}")
    for line in endpoint_lines[1:]:
        parts.append(f"        {line}")
    parts[-1] += ","

    if classes:
        parts.append(f"    classes=[{', '.join(classes)}],")
    if modules:
        parts.append(f"    modules=[{', '.join(modules)}],")
    if bindings:
        binding_parts = []
        for k, v in bindings.items():
            if isinstance(v, str):
                binding_parts.append(f'        "{k}": {v},')
            else:
                binding_parts.append(f'        "{k}": {repr(v)},')
        parts.append("    bindings={")
        parts.extend(binding_parts)
        parts.append("    },")

    parts.append(")")
    return "\n".join(parts)


def generate_endpoint_group(
    url: str = "",
    endpoints: list[dict] | None = None,
    authentication: str = "",
) -> str:
    """Generate a clearskies EndpointGroup configuration.

    Args:
        url: The URL prefix for all endpoints in the group.
        endpoints: List of endpoint configurations. Each dict has:
            - type (str): Endpoint type (e.g. "RestfulApi", "Callable", "List")
            - model_name (str): Model class name (for model-based endpoints)
            - url (str): URL path for this endpoint
            - readable_column_names (list[str], optional): Readable columns
            - writeable_column_names (list[str], optional): Writeable columns
            - sortable_column_names (list[str], optional): Sortable columns
            - searchable_column_names (list[str], optional): Searchable columns
            - default_sort_column_name (str, optional): Default sort column
            - request_methods (list[str], optional): Allowed HTTP methods (for Callable)
            - extra_options (dict, optional): Additional endpoint options
        authentication: Authentication configuration for all endpoints in the group
            (e.g. 'clearskies.authentication.SecretBearer(environment_key="MY_SECRET")').
    """
    endpoints = endpoints or []

    parts = ["clearskies.EndpointGroup("]

    if url:
        parts.append(f'    url="{url}",')

    if authentication:
        parts.append(f"    authentication={authentication},")

    if endpoints:
        parts.append("    endpoints=[")

        for ep in endpoints:
            ep_type = ep.get("type", "Callable")
            ep_url = ep.get("url", "")
            model_name = ep.get("model_name", "")

            if ep_type not in ENDPOINT_TYPES:
                return f"Error: Unknown endpoint type '{ep_type}'. Available: {', '.join(sorted(ENDPOINT_TYPES))}"

            ep_parts = [f"        clearskies.endpoints.{ep_type}("]

            if ep_url:
                ep_parts.append(f'            url="{ep_url}",')
            if model_name:
                ep_parts.append(f"            model_class={model_name},")

            # Handle common endpoint options
            if ep.get("readable_column_names"):
                ep_parts.append(f"            readable_column_names={repr(ep['readable_column_names'])},")
            if ep.get("writeable_column_names"):
                ep_parts.append(f"            writeable_column_names={repr(ep['writeable_column_names'])},")
            if ep.get("sortable_column_names"):
                ep_parts.append(f"            sortable_column_names={repr(ep['sortable_column_names'])},")
            if ep.get("searchable_column_names"):
                ep_parts.append(f"            searchable_column_names={repr(ep['searchable_column_names'])},")
            if ep.get("default_sort_column_name"):
                ep_parts.append(f'            default_sort_column_name="{ep["default_sort_column_name"]}",')
            if ep.get("request_methods"):
                ep_parts.append(f"            request_methods={repr(ep['request_methods'])},")

            # Handle extra options
            for k, v in ep.get("extra_options", {}).items():
                if isinstance(v, str):
                    ep_parts.append(f"            {k}={v},")
                else:
                    ep_parts.append(f"            {k}={repr(v)},")

            ep_parts.append("        ),")
            parts.extend(ep_parts)

        parts.append("    ],")

    parts.append(")")
    return "\n".join(parts)
