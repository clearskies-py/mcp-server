"""
Module ecosystem tools for clearskies MCP server.

This module contains tools for documenting clearskies extension modules
using dynamic discovery to introspect installed modules.
"""

import textwrap
from typing import Optional

from ..known_modules import (
    KNOWN_MODULES,
    MODULE_EXAMPLES,
    get_install_command,
    get_module_example,
    get_optional_install_command,
)
from ..module_discovery import (
    ModuleDiscovery,
    ModuleInfo,
    format_module_detail,
    format_module_list,
)

# Global module discovery instance
_discovery: Optional[ModuleDiscovery] = None


def _get_discovery() -> ModuleDiscovery:
    """Get or create the module discovery instance."""
    global _discovery
    if _discovery is None:
        _discovery = ModuleDiscovery(KNOWN_MODULES)
    return _discovery


def list_modules() -> str:
    """List all available clearskies extension modules with a summary of what each provides.

    Shows installation status, version (if installed), and component counts
    for each known clearskies extension module.
    """
    discovery = _get_discovery()
    modules = discovery.discover_all()

    lines = ["# Clearskies Extension Modules\n"]

    # Separate installed and not installed
    installed = {k: v for k, v in modules.items() if v.is_installed}
    not_installed = {k: v for k, v in modules.items() if not v.is_installed}

    if installed:
        lines.append("## Installed Modules\n")
        lines.append(format_module_list(installed))

    if not_installed:
        lines.append("\n## Available Modules (Not Installed)\n")
        lines.append(format_module_list(not_installed))
        lines.append("\n### Installation")
        lines.append("```bash")
        lines.append("# Install individual modules:")
        for name in sorted(not_installed.keys()):
            info = KNOWN_MODULES[name]
            opt_name = info.get("optional_dep_name", name.split("-")[-1])
            lines.append(f"pip install clearskies-mcp[{opt_name}]")
        lines.append("")
        lines.append("# Or install all modules:")
        lines.append("pip install clearskies-mcp[all]")
        lines.append("```")

    return "\n".join(lines)


def get_module_info(module_name: str) -> str:
    """Get detailed documentation for a specific clearskies extension module.

    Shows installation status, version, and all discovered components
    with their descriptions and parameters.

    Args:
        module_name: The module name (e.g. "clearskies-aws", "clearskies-graphql", "clearskies-snyk").
    """
    if module_name not in KNOWN_MODULES:
        available = ", ".join(sorted(KNOWN_MODULES.keys()))
        return f"Unknown module '{module_name}'. Available modules: {available}"

    discovery = _get_discovery()
    module_info = discovery.discover_module(module_name)

    if module_info is None:
        return f"Could not discover module '{module_name}'"

    return format_module_detail(module_info)


def explain_module(module_name: str) -> str:
    """Get usage examples and integration guidance for a specific clearskies extension module.

    Args:
        module_name: The module name (e.g. "clearskies-aws", "clearskies-graphql", "clearskies-snyk",
                     "clearskies-gitlab", "clearskies-cortex", "clearskies-akeyless-custom-producer").
    """
    if module_name not in KNOWN_MODULES:
        available = ", ".join(sorted(KNOWN_MODULES.keys()))
        return f"Unknown module '{module_name}'. Available modules: {available}"

    # Try to get example from static examples
    example = get_module_example(module_name)

    if example:
        return example

    # Fallback: generate basic example from module info
    discovery = _get_discovery()
    module_info = discovery.discover_module(module_name)

    if module_info is None:
        return f"No examples available for '{module_name}'"

    return _generate_basic_example(module_info)


def get_module_components(module_name: str, category: Optional[str] = None) -> str:
    """Get detailed component information for a module.

    Lists all components in a module, optionally filtered by category,
    with their descriptions and constructor parameters.

    Args:
        module_name: The module name (e.g. "clearskies-aws")
        category: Optional category filter (e.g. "backends", "contexts", "models")
    """
    if module_name not in KNOWN_MODULES:
        available = ", ".join(sorted(KNOWN_MODULES.keys()))
        return f"Unknown module '{module_name}'. Available modules: {available}"

    discovery = _get_discovery()
    module_info = discovery.discover_module(module_name)

    if module_info is None:
        return f"Could not discover module '{module_name}'"

    if not module_info.is_installed:
        return (
            f"Module '{module_name}' is not installed.\n\n"
            f"Install with: `{get_install_command(module_name)}`\n"
            f"Or: `{get_optional_install_command(module_name)}`"
        )

    parts = [f"# {module_name} Components\n"]

    if category:
        # Filter to specific category
        if category not in module_info.components:
            available_cats = ", ".join(sorted(module_info.components.keys()))
            return f"Category '{category}' not found in {module_name}.\nAvailable categories: {available_cats}"

        components = module_info.components[category]
        cat_title = category.replace("_", " ").title()
        parts.append(f"## {cat_title} ({len(components)})\n")

        for comp in sorted(components, key=lambda c: c.name):
            parts.append(f"### {comp.name}\n")
            if comp.description:
                parts.append(f"{comp.description}\n")

            if comp.parameters:
                parts.append("**Parameters:**")
                for param in comp.parameters:
                    default = f" = {param.get('default', '')}" if "default" in param else ""
                    type_hint = f": {param.get('type', '')}" if "type" in param else ""
                    parts.append(f"- `{param['name']}{type_hint}{default}`")
            parts.append("")
    else:
        # Show all categories
        for cat, components in sorted(module_info.components.items()):
            if not components:
                continue

            cat_title = cat.replace("_", " ").title()
            parts.append(f"## {cat_title} ({len(components)})\n")

            for comp in sorted(components, key=lambda c: c.name):
                desc = f" – {comp.description}" if comp.description else ""
                parts.append(f"- **{comp.name}**{desc}")

            parts.append("")

    return "\n".join(parts)


def suggest_modules(component_type: str) -> str:
    """Suggest modules that provide a specific component type.

    Args:
        component_type: The component category (e.g. "backends", "contexts", "models")
    """
    discovery = _get_discovery()
    suggestions = discovery.suggest_modules_for_component(component_type)

    if not suggestions:
        return f"No modules found that provide '{component_type}' components."

    parts = [f"# Modules providing {component_type}\n"]

    for module_name in sorted(suggestions):
        module_info = discovery.discover_module(module_name)
        if module_info is None:
            continue

        status = f"✅ v{module_info.version}" if module_info.is_installed else "❌ Not Installed"
        parts.append(f"### {module_name} {status}")
        parts.append(f"{module_info.description}\n")

        if component_type in module_info.components:
            components = module_info.components[component_type]
            for comp in components[:5]:  # Show first 5
                parts.append(f"- {comp.name}")
            if len(components) > 5:
                parts.append(f"- ... and {len(components) - 5} more")

        if not module_info.is_installed:
            parts.append(f"\nInstall: `{get_optional_install_command(module_name)}`")

        parts.append("")

    return "\n".join(parts)


def check_module_compatibility(module_name: str) -> str:
    """Check if a module is installed and compatible.

    Args:
        module_name: The module name to check
    """
    if module_name not in KNOWN_MODULES:
        available = ", ".join(sorted(KNOWN_MODULES.keys()))
        return f"Unknown module '{module_name}'. Available modules: {available}"

    discovery = _get_discovery()
    module_info = discovery.discover_module(module_name)

    if module_info is None:
        return f"Could not check module '{module_name}'"

    parts = [f"# {module_name} Compatibility Check\n"]

    if module_info.is_installed:
        parts.append(f"✅ **Installed:** v{module_info.version}")
        parts.append(f"**Package:** `{module_info.package_name}`")
        parts.append(f"**Import:** `import {module_info.import_name}`\n")

        # Show component summary
        summary = module_info.get_component_summary()
        if summary:
            parts.append("## Discovered Components\n")
            for cat, count in sorted(summary.items()):
                cat_title = cat.replace("_", " ").title()
                parts.append(f"- {cat_title}: {count}")

        if module_info.error:
            parts.append(f"\n⚠️ **Warning:** {module_info.error}")
    else:
        parts.append("❌ **Not Installed**\n")
        parts.append("## Installation\n")
        parts.append("```bash")
        parts.append(get_install_command(module_name))
        parts.append("# Or:")
        parts.append(get_optional_install_command(module_name))
        parts.append("```")

        if module_info.error:
            parts.append(f"\n**Error:** {module_info.error}")

    return "\n".join(parts)


def refresh_module_cache() -> str:
    """Refresh the module discovery cache.

    Forces re-discovery of all modules, useful after installing new modules.
    """
    discovery = _get_discovery()
    discovery.clear_cache()
    modules = discovery.discover_all(force_refresh=True)

    installed_count = sum(1 for m in modules.values() if m.is_installed)
    total_count = len(modules)

    parts = ["# Module Cache Refreshed\n"]
    parts.append(f"Discovered {installed_count}/{total_count} installed modules.\n")

    for name, info in sorted(modules.items()):
        if info.is_installed:
            comp_count = info.get_component_count()
            parts.append(f"- ✅ {name} v{info.version} ({comp_count} components)")
        else:
            parts.append(f"- ❌ {name} (not installed)")

    return "\n".join(parts)


def _generate_basic_example(module_info: ModuleInfo) -> str:
    """Generate a basic example for a module without static examples.

    Args:
        module_info: The ModuleInfo object

    Returns:
        Basic example code string
    """
    parts = [f"# {module_info.import_name.replace('_', '-')} Usage\n"]

    parts.append("## Installation\n")
    parts.append("```bash")
    parts.append(f"pip install {module_info.package_name}")
    parts.append("```\n")

    if not module_info.is_installed:
        parts.append("*Module is not installed. Install it to see detailed examples.*")
        return "\n".join(parts)

    parts.append("## Basic Import\n")
    parts.append("```python")
    parts.append(f"import {module_info.import_name}")
    parts.append("```\n")

    # Show available components
    if module_info.components:
        parts.append("## Available Components\n")
        for cat, components in sorted(module_info.components.items()):
            if components:
                cat_title = cat.replace("_", " ").title()
                parts.append(f"### {cat_title}")
                for comp in components[:5]:
                    parts.append(f"- `{module_info.import_name}.{cat}.{comp.name}`")
                if len(components) > 5:
                    parts.append(f"- ... and {len(components) - 5} more")
                parts.append("")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Legacy compatibility - keep old static registry available for fallback
# ---------------------------------------------------------------------------

# Re-export for backward compatibility
MODULE_REGISTRY = KNOWN_MODULES
