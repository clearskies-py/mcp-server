"""
Dynamic module discovery for clearskies extension modules.

This module provides utilities for dynamically discovering and introspecting
clearskies extension modules, checking their installation status, and
extracting component information.
"""

import importlib
import importlib.metadata
import inspect
import json
from dataclasses import dataclass, field
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Component categories to discover (matching introspection.py categories)
# ---------------------------------------------------------------------------
COMPONENT_CATEGORIES = [
    "columns",
    "endpoints",
    "backends",
    "contexts",
    "authentication",
    "validators",
    "exceptions",
    "di",
    "di_inject",
    "cursors",
    "input_outputs",
    "configs",
    "clients",
    "secrets",
    "security_headers",
    "query",
    "query_results",
    "functional",
    "models",
    "actions",
    # Extension-specific categories
    "rest_models",
    "graphql_models",
    "defaults",
    "classes",
]


@dataclass
class ComponentInfo:
    """Information about a single component (class or function)."""

    name: str
    description: str
    type_: Optional[type] = None
    parameters: list[dict] = field(default_factory=list)
    is_class: bool = True

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "is_class": self.is_class,
        }


@dataclass
class ModuleInfo:
    """Complete information about a clearskies extension module."""

    package_name: str
    import_name: str
    description: str
    pypi_url: str = ""
    is_installed: bool = False
    version: Optional[str] = None
    components: dict[str, list[ComponentInfo]] = field(default_factory=dict)
    metadata: Optional[dict] = None
    error: Optional[str] = None

    @classmethod
    def discover(cls, package_name: str, import_name: str, description: str, pypi_url: str = "") -> "ModuleInfo":
        """Discover module information dynamically.

        Args:
            package_name: The pip package name (e.g., 'clear-skies-aws')
            import_name: The Python import name (e.g., 'clearskies_aws')
            description: Short description of the module
            pypi_url: URL to PyPI page

        Returns:
            ModuleInfo instance with discovered information
        """
        info = cls(
            package_name=package_name,
            import_name=import_name,
            description=description,
            pypi_url=pypi_url,
        )

        try:
            # Check if package is installed
            info.version = importlib.metadata.version(package_name)
            info.is_installed = True

            # Import the module
            module = importlib.import_module(import_name)

            # Check for MCP metadata
            info.metadata = getattr(module, "__mcp_metadata__", None)

            # Discover components
            info.components = cls._discover_all_components(module, import_name)

        except importlib.metadata.PackageNotFoundError:
            info.is_installed = False
            info.error = f"Package '{package_name}' is not installed"

        except ImportError as e:
            info.is_installed = False
            info.error = f"Could not import '{import_name}': {e}"

        except Exception as e:
            info.error = f"Error discovering module: {e}"

        return info

    @classmethod
    def _discover_all_components(cls, module, import_name: str) -> dict[str, list[ComponentInfo]]:
        """Discover all component categories from a module.

        Args:
            module: The imported module object
            import_name: The import name for error messages

        Returns:
            Dictionary mapping category names to lists of ComponentInfo
        """
        components = {}

        for category in COMPONENT_CATEGORIES:
            # Try direct attribute on module
            if hasattr(module, category):
                submodule = getattr(module, category)
                discovered = cls._discover_category(submodule, f"{import_name}.{category}")
                if discovered:
                    components[category] = discovered

            # Try importing as submodule
            else:
                try:
                    submodule = importlib.import_module(f"{import_name}.{category}")
                    discovered = cls._discover_category(submodule, f"{import_name}.{category}")
                    if discovered:
                        components[category] = discovered
                except ImportError:
                    pass

        # Also check for nested submodules (e.g., clearskies_gitlab.rest.models)
        components.update(cls._discover_nested_components(module, import_name))

        return components

    @classmethod
    def _discover_nested_components(cls, module, import_name: str) -> dict[str, list[ComponentInfo]]:
        """Discover components in nested submodules.

        Some modules have nested structures like:
        - clearskies_gitlab.rest.models
        - clearskies_gitlab.graphql.models

        Args:
            module: The imported module object
            import_name: The import name

        Returns:
            Dictionary mapping category names to lists of ComponentInfo
        """
        components = {}

        # Common nested patterns
        nested_patterns = [
            ("rest", "models", "rest_models"),
            ("rest", "backends", "rest_backends"),
            ("graphql", "models", "graphql_models"),
            ("graphql", "backends", "graphql_backends"),
            ("v1", "models", "v1_models"),
            ("v1", "backends", "v1_backends"),
        ]

        for parent, child, category_name in nested_patterns:
            try:
                submodule = importlib.import_module(f"{import_name}.{parent}.{child}")
                discovered = cls._discover_category(submodule, f"{import_name}.{parent}.{child}")
                if discovered:
                    components[category_name] = discovered
            except ImportError:
                pass

        return components

    @classmethod
    def _discover_category(cls, module, module_name: str) -> list[ComponentInfo]:
        """Discover all classes/functions in a module category.

        Args:
            module: The module to introspect
            module_name: Name of the module (for error messages)

        Returns:
            List of ComponentInfo objects
        """
        components = []

        try:
            # Get names to iterate over
            if hasattr(module, "__all__"):
                names = module.__all__
            else:
                names = [n for n in dir(module) if not n.startswith("_")]

            for name in names:
                try:
                    obj = getattr(module, name, None)
                    if obj is None:
                        continue

                    if inspect.isclass(obj):
                        components.append(
                            ComponentInfo(
                                name=name,
                                description=cls._get_first_line_doc(obj),
                                type_=obj,
                                parameters=cls._get_init_params(obj),
                                is_class=True,
                            )
                        )
                    elif callable(obj) and not name.startswith("_"):
                        components.append(
                            ComponentInfo(
                                name=name,
                                description=cls._get_first_line_doc(obj),
                                type_=None,
                                parameters=cls._get_callable_params(obj),
                                is_class=False,
                            )
                        )

                except (AttributeError, TypeError):
                    continue

        except Exception as e:
            print(f"Warning: Could not introspect {module_name}: {e}")

        return components

    @staticmethod
    def _get_first_line_doc(obj) -> str:
        """Get the first line of a docstring."""
        doc = inspect.getdoc(obj) or ""
        return doc.split("\n")[0].strip()

    @staticmethod
    def _get_init_params(cls: type) -> list[dict]:
        """Get __init__ parameters for a class."""
        try:
            sig = inspect.signature(cls.__init__)  # type: ignore[misc]
        except (ValueError, TypeError):
            return []

        params = []
        for name, param in sig.parameters.items():
            if name == "self":
                continue

            info = {"name": name, "kind": str(param.kind.name)}

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

    @staticmethod
    def _get_callable_params(func) -> list[dict]:
        """Get parameters for a callable."""
        try:
            sig = inspect.signature(func)
        except (ValueError, TypeError):
            return []

        params = []
        for name, param in sig.parameters.items():
            info = {"name": name, "kind": str(param.kind.name)}

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

    def get_component_count(self) -> int:
        """Get total number of discovered components."""
        return sum(len(comps) for comps in self.components.values())

    def get_component_summary(self) -> dict[str, int]:
        """Get count of components per category."""
        return {cat: len(comps) for cat, comps in self.components.items()}

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "package_name": self.package_name,
            "import_name": self.import_name,
            "description": self.description,
            "pypi_url": self.pypi_url,
            "is_installed": self.is_installed,
            "version": self.version,
            "components": {cat: [c.to_dict() for c in comps] for cat, comps in self.components.items()},
            "metadata": self.metadata,
            "error": self.error,
        }


class ModuleDiscovery:
    """Manager for discovering clearskies extension modules."""

    def __init__(self, known_modules: dict[str, dict]):
        """Initialize with known modules registry.

        Args:
            known_modules: Dictionary mapping module names to their info
        """
        self.known_modules = known_modules
        self._cache: dict[str, ModuleInfo] = {}

    def discover_module(self, module_name: str, force_refresh: bool = False) -> Optional[ModuleInfo]:
        """Discover a specific module.

        Args:
            module_name: The module name (e.g., 'clearskies-aws')
            force_refresh: If True, bypass cache

        Returns:
            ModuleInfo or None if module is unknown
        """
        if module_name not in self.known_modules:
            return None

        if not force_refresh and module_name in self._cache:
            return self._cache[module_name]

        info = self.known_modules[module_name]
        module_info = ModuleInfo.discover(
            package_name=info["package"],
            import_name=info["import"],
            description=info["description"],
            pypi_url=info.get("pypi_url", ""),
        )

        self._cache[module_name] = module_info
        return module_info

    def discover_all(self, force_refresh: bool = False) -> dict[str, ModuleInfo]:
        """Discover all known modules.

        Args:
            force_refresh: If True, bypass cache

        Returns:
            Dictionary mapping module names to ModuleInfo
        """
        results: dict[str, ModuleInfo] = {}
        for module_name in self.known_modules:
            module_info = self.discover_module(module_name, force_refresh)
            if module_info is not None:
                results[module_name] = module_info
        return results

    def get_installed_modules(self) -> dict[str, ModuleInfo]:
        """Get only installed modules.

        Returns:
            Dictionary of installed modules
        """
        all_modules = self.discover_all()
        return {name: info for name, info in all_modules.items() if info.is_installed}

    def get_not_installed_modules(self) -> dict[str, ModuleInfo]:
        """Get modules that are not installed.

        Returns:
            Dictionary of not-installed modules
        """
        all_modules = self.discover_all()
        return {name: info for name, info in all_modules.items() if not info.is_installed}

    def suggest_modules_for_component(self, component_type: str) -> list[str]:
        """Suggest modules that provide a specific component type.

        Args:
            component_type: The component category (e.g., 'backends', 'contexts')

        Returns:
            List of module names that provide this component type
        """
        suggestions = []
        for name, info in self.known_modules.items():
            module_info = self.discover_module(name)
            if module_info and component_type in module_info.components:
                suggestions.append(name)
        return suggestions

    def clear_cache(self):
        """Clear the discovery cache."""
        self._cache.clear()


def format_module_list(modules: dict[str, ModuleInfo]) -> str:
    """Format a dictionary of modules as markdown.

    Args:
        modules: Dictionary mapping module names to ModuleInfo

    Returns:
        Markdown-formatted string
    """
    lines = []

    for name, info in sorted(modules.items()):
        if info.is_installed:
            status = f"✅ v{info.version}"
            component_summary = []
            for cat, comps in sorted(info.components.items()):
                if comps:
                    cat_title = cat.replace("_", " ").title()
                    component_summary.append(f"  - {len(comps)} {cat_title}")
            summary_text = "\n".join(component_summary) if component_summary else "  (no components discovered)"
        else:
            status = "❌ Not Installed"
            summary_text = f"  Install: `pip install {info.package_name}`"

        lines.append(f"### {name} {status}")
        lines.append(f"**Package:** `{info.package_name}`  ")
        lines.append(f"**Import:** `{info.import_name}`  ")
        lines.append(f"{info.description}\n")
        lines.append(summary_text)
        lines.append("")

    return "\n".join(lines)


def format_module_detail(info: ModuleInfo) -> str:
    """Format detailed module information as markdown.

    Args:
        info: ModuleInfo object

    Returns:
        Markdown-formatted string
    """
    parts = [f"# {info.import_name.replace('_', '-')}"]

    if info.is_installed:
        parts.append(f"\n**Status:** ✅ Installed (v{info.version})")
    else:
        parts.append(f"\n**Status:** ❌ Not Installed")

    parts.append(f"**Package:** `pip install {info.package_name}`  ")
    parts.append(f"**Import:** `import {info.import_name}`")

    if info.pypi_url:
        parts.append(f"**PyPI:** [{info.package_name}]({info.pypi_url})")

    parts.append(f"\n{info.description}")

    if info.error:
        parts.append(f"\n⚠️ **Error:** {info.error}")

    if not info.is_installed:
        parts.append("\n## Installation")
        parts.append("```bash")
        parts.append(f"pip install {info.package_name}")
        parts.append("```")
        return "\n".join(parts)

    # Show components
    if info.components:
        parts.append(f"\n## Components ({info.get_component_count()} total)\n")

        for category, components in sorted(info.components.items()):
            if not components:
                continue

            cat_title = category.replace("_", " ").title()
            parts.append(f"### {cat_title} ({len(components)})\n")

            for comp in sorted(components, key=lambda c: c.name):
                desc = f" – {comp.description}" if comp.description else ""
                parts.append(f"- **{comp.name}**{desc}")

            parts.append("")
    else:
        parts.append("\n*No components discovered. The module may use a non-standard structure.*")

    return "\n".join(parts)
