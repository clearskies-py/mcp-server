"""
Introspection helpers for clearskies types.

This module provides utilities for introspecting clearskies column types,
endpoint types, backend types, context types, and many more module categories.
"""

import inspect
import json
from typing import Any, Mapping

import clearskies
import clearskies.authentication
import clearskies.backends
import clearskies.columns
import clearskies.contexts
import clearskies.endpoints

# Optional imports - some modules may not exist in all clearskies versions
try:
    import clearskies.validators

    _HAS_VALIDATORS = True
except ImportError:
    _HAS_VALIDATORS = False

try:
    import clearskies.exceptions

    _HAS_EXCEPTIONS = True
except ImportError:
    _HAS_EXCEPTIONS = False

try:
    import clearskies.di

    _HAS_DI = True
except ImportError:
    _HAS_DI = False

try:
    import clearskies.cursors

    _HAS_CURSORS = True
except ImportError:
    _HAS_CURSORS = False

try:
    import clearskies.input_outputs

    _HAS_INPUT_OUTPUTS = True
except ImportError:
    _HAS_INPUT_OUTPUTS = False

try:
    import clearskies.configs

    _HAS_CONFIGS = True
except ImportError:
    _HAS_CONFIGS = False

try:
    import clearskies.clients

    _HAS_CLIENTS = True
except ImportError:
    _HAS_CLIENTS = False

try:
    import clearskies.secrets

    _HAS_SECRETS = True
except ImportError:
    _HAS_SECRETS = False

try:
    import clearskies.security_headers

    _HAS_SECURITY_HEADERS = True
except ImportError:
    _HAS_SECURITY_HEADERS = False

try:
    import clearskies.functional

    _HAS_FUNCTIONAL = True
except ImportError:
    _HAS_FUNCTIONAL = False

try:
    import clearskies.query

    _HAS_QUERY = True
except ImportError:
    _HAS_QUERY = False

try:
    import clearskies.query.result

    _HAS_QUERY_RESULTS = True
except ImportError:
    _HAS_QUERY_RESULTS = False


# ---------------------------------------------------------------------------
# Safe introspection helper
# ---------------------------------------------------------------------------
def safe_introspect_module(module, module_name: str, filter_func=None) -> dict[str, type]:
    """Safely introspect a module, handling missing __all__.

    Args:
        module: The module to introspect
        module_name: Name of the module (for error messages)
        filter_func: Optional function to filter classes (receives class, returns bool)

    Returns:
        Dictionary mapping class names to class objects
    """
    try:
        if hasattr(module, "__all__"):
            names = module.__all__
        else:
            # Fallback to dir(), filter out private
            names = [n for n in dir(module) if not n.startswith("_")]

        result = {}
        for name in names:
            try:
                obj = getattr(module, name)
                if inspect.isclass(obj):
                    if filter_func is None or filter_func(obj):
                        result[name] = obj
            except (AttributeError, TypeError):
                # Skip problematic items
                continue

        return result

    except Exception as e:
        print(f"Warning: Could not introspect {module_name}: {e}")
        return {}


def safe_introspect_module_all(module, module_name: str) -> dict[str, Any]:
    """Safely introspect a module for all items (not just classes).

    Args:
        module: The module to introspect
        module_name: Name of the module (for error messages)

    Returns:
        Dictionary mapping names to objects
    """
    try:
        if hasattr(module, "__all__"):
            names = module.__all__
        else:
            names = [n for n in dir(module) if not n.startswith("_")]

        result = {}
        for name in names:
            try:
                obj = getattr(module, name)
                if not name.startswith("_"):
                    result[name] = obj
            except (AttributeError, TypeError):
                continue

        return result

    except Exception as e:
        print(f"Warning: Could not introspect {module_name}: {e}")
        return {}


# ---------------------------------------------------------------------------
# Type registries - Core (always available)
# ---------------------------------------------------------------------------
COLUMN_TYPES: dict[str, type] = {
    name: getattr(clearskies.columns, name)
    for name in clearskies.columns.__all__
    if inspect.isclass(getattr(clearskies.columns, name, None))
}

ENDPOINT_TYPES: dict[str, type] = {
    name: getattr(clearskies.endpoints, name)
    for name in clearskies.endpoints.__all__
    if inspect.isclass(getattr(clearskies.endpoints, name, None))
}

BACKEND_TYPES: dict[str, type] = {
    name: getattr(clearskies.backends, name)
    for name in clearskies.backends.__all__
    if inspect.isclass(getattr(clearskies.backends, name, None))
}

CONTEXT_TYPES: dict[str, type] = {
    name: getattr(clearskies.contexts, name)
    for name in clearskies.contexts.__all__
    if inspect.isclass(getattr(clearskies.contexts, name, None))
}

# ---------------------------------------------------------------------------
# Type registries - Authentication
# ---------------------------------------------------------------------------
AUTHENTICATION_TYPES: dict[str, type] = safe_introspect_module(clearskies.authentication, "clearskies.authentication")

# ---------------------------------------------------------------------------
# Type registries - Validators (if available)
# ---------------------------------------------------------------------------
VALIDATOR_TYPES: dict[str, type]
if _HAS_VALIDATORS:
    VALIDATOR_TYPES = safe_introspect_module(clearskies.validators, "clearskies.validators")
else:
    VALIDATOR_TYPES = {}

# ---------------------------------------------------------------------------
# Type registries - Exceptions (if available)
# ---------------------------------------------------------------------------
EXCEPTION_TYPES: dict[str, type]
if _HAS_EXCEPTIONS:
    EXCEPTION_TYPES = safe_introspect_module(
        clearskies.exceptions, "clearskies.exceptions", filter_func=lambda cls: issubclass(cls, BaseException)
    )
else:
    EXCEPTION_TYPES = {}

# ---------------------------------------------------------------------------
# Type registries - DI Inject helpers (if available)
# ---------------------------------------------------------------------------
DI_INJECT_TYPES: dict[str, type]
if _HAS_DI:
    try:
        import clearskies.di.inject

        DI_INJECT_TYPES = safe_introspect_module(clearskies.di.inject, "clearskies.di.inject")
    except (ImportError, AttributeError):
        DI_INJECT_TYPES = {}
else:
    DI_INJECT_TYPES = {}

# ---------------------------------------------------------------------------
# Type registries - Cursors (if available)
# ---------------------------------------------------------------------------
CURSOR_TYPES: dict[str, type]
if _HAS_CURSORS:
    CURSOR_TYPES = safe_introspect_module(clearskies.cursors, "clearskies.cursors")
else:
    CURSOR_TYPES = {}

# ---------------------------------------------------------------------------
# Type registries - Input/Outputs (if available)
# ---------------------------------------------------------------------------
INPUT_OUTPUT_TYPES: dict[str, type]
if _HAS_INPUT_OUTPUTS:
    INPUT_OUTPUT_TYPES = safe_introspect_module(clearskies.input_outputs, "clearskies.input_outputs")
else:
    INPUT_OUTPUT_TYPES = {}

# ---------------------------------------------------------------------------
# Type registries - Configs (if available)
# ---------------------------------------------------------------------------
CONFIG_TYPES: dict[str, type]
if _HAS_CONFIGS:
    CONFIG_TYPES = safe_introspect_module(clearskies.configs, "clearskies.configs")
else:
    CONFIG_TYPES = {}

# ---------------------------------------------------------------------------
# Type registries - Clients (if available)
# ---------------------------------------------------------------------------
CLIENT_TYPES: dict[str, type]
if _HAS_CLIENTS:
    CLIENT_TYPES = safe_introspect_module(clearskies.clients, "clearskies.clients")
else:
    CLIENT_TYPES = {}

# ---------------------------------------------------------------------------
# Type registries - Secrets (if available)
# ---------------------------------------------------------------------------
SECRET_TYPES: dict[str, type]
if _HAS_SECRETS:
    SECRET_TYPES = safe_introspect_module(clearskies.secrets, "clearskies.secrets")
else:
    SECRET_TYPES = {}

# ---------------------------------------------------------------------------
# Type registries - Security Headers (if available)
# ---------------------------------------------------------------------------
SECURITY_HEADER_TYPES: dict[str, type]
if _HAS_SECURITY_HEADERS:
    SECURITY_HEADER_TYPES = safe_introspect_module(clearskies.security_headers, "clearskies.security_headers")
else:
    SECURITY_HEADER_TYPES = {}

# ---------------------------------------------------------------------------
# Type registries - Query (if available)
# ---------------------------------------------------------------------------
QUERY_TYPES: dict[str, type]
if _HAS_QUERY:
    QUERY_TYPES = safe_introspect_module(clearskies.query, "clearskies.query")
else:
    QUERY_TYPES = {}

# ---------------------------------------------------------------------------
# Type registries - Query Results (if available)
# ---------------------------------------------------------------------------
QUERY_RESULT_TYPES: dict[str, type]
if _HAS_QUERY_RESULTS:
    QUERY_RESULT_TYPES = safe_introspect_module(clearskies.query.result, "clearskies.query.result")
else:
    QUERY_RESULT_TYPES = {}

# ---------------------------------------------------------------------------
# Type registries - Functional utilities (if available)
# Functional utilities might not all be classes
# ---------------------------------------------------------------------------
FUNCTIONAL_ITEMS: dict[str, Any]
if _HAS_FUNCTIONAL:
    FUNCTIONAL_ITEMS = safe_introspect_module_all(clearskies.functional, "clearskies.functional")
else:
    FUNCTIONAL_ITEMS = {}


# ---------------------------------------------------------------------------
# Registry lookup helpers
# ---------------------------------------------------------------------------
ALL_TYPE_REGISTRIES = {
    "columns": COLUMN_TYPES,
    "endpoints": ENDPOINT_TYPES,
    "backends": BACKEND_TYPES,
    "contexts": CONTEXT_TYPES,
    "authentication": AUTHENTICATION_TYPES,
    "validators": VALIDATOR_TYPES,
    "exceptions": EXCEPTION_TYPES,
    "di_inject": DI_INJECT_TYPES,
    "cursors": CURSOR_TYPES,
    "input_outputs": INPUT_OUTPUT_TYPES,
    "configs": CONFIG_TYPES,
    "clients": CLIENT_TYPES,
    "secrets": SECRET_TYPES,
    "security_headers": SECURITY_HEADER_TYPES,
    "query": QUERY_TYPES,
    "query_results": QUERY_RESULT_TYPES,
    "functional": FUNCTIONAL_ITEMS,
}


def get_type_registry(category: str) -> dict:
    """Get the type registry for a specific category.

    Args:
        category: The category name (e.g., 'columns', 'authentication', 'validators')

    Returns:
        Dictionary mapping type names to type objects
    """
    return ALL_TYPE_REGISTRIES.get(category, {})


def get_all_categories() -> list[str]:
    """Get list of all type categories.

    Returns:
        List of category names
    """
    return list(ALL_TYPE_REGISTRIES.keys())


def get_available_categories() -> list[str]:
    """Get list of categories that have at least one type.

    Returns:
        List of category names with available types
    """
    return [cat for cat, types in ALL_TYPE_REGISTRIES.items() if types]


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------
def get_docstring(cls: type) -> str:
    """Return the docstring of a class, cleaned up for display."""
    doc = inspect.getdoc(cls) or ""
    return doc.strip()


def get_init_params(cls: type) -> list[dict]:
    """Return a list of __init__ parameter info dicts for a class."""
    try:
        sig = inspect.signature(cls.__init__)  # type: ignore[misc]
    except (ValueError, TypeError):
        return []
    params = []
    for name, param in sig.parameters.items():
        if name == "self":
            continue
        info: dict = {"name": name, "kind": str(param.kind.name)}
        if param.default is not inspect.Parameter.empty:
            try:
                json.dumps(param.default)
                info["default"] = param.default
            except (TypeError, ValueError):
                info["default"] = repr(param.default)
        if param.annotation is not inspect.Parameter.empty:
            info["type"] = str(param.annotation)
        params.append(info)
    return params


def get_class_info(cls: type, category_name: str = "Type") -> str:
    """Get formatted documentation for a class.

    Args:
        cls: The class to document
        category_name: The category name for the header (e.g., "Column", "Validator")

    Returns:
        Markdown-formatted documentation string
    """
    doc = get_docstring(cls)
    params = get_init_params(cls)

    parts = [f"# {category_name}: {cls.__name__}\n"]

    if doc:
        parts.append(doc)

    # Show class hierarchy for exceptions
    if issubclass(cls, BaseException):
        mro = cls.__mro__[1:]  # Skip the class itself
        if mro:
            parts.append("\n## Exception Hierarchy\n")
            hierarchy = " → ".join([c.__name__ for c in mro if c != object])
            parts.append(f"{cls.__name__} → {hierarchy}")

    if params:
        parts.append("\n## Constructor Parameters\n")
        for p in params:
            default = f" = {p['default']}" if "default" in p else ""
            type_hint = f": {p['type']}" if "type" in p else ""
            parts.append(f"- `{p['name']}{type_hint}{default}`")

    return "\n".join(parts)


def list_types_formatted(type_registry: Mapping[str, type]) -> str:
    """Format a type registry as a markdown list.

    Args:
        type_registry: Dictionary mapping type names to type objects

    Returns:
        Markdown-formatted list of types with descriptions
    """
    lines = []
    for name, cls in sorted(type_registry.items()):
        doc = get_docstring(cls)
        first_line = doc.split("\n")[0] if doc else "(no description)"
        lines.append(f"- **{name}**: {first_line}")
    return "\n".join(lines) if lines else "(no types available)"
