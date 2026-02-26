"""
Import organization and rewriting for v2.

Handles conversion of v1 imports to v2 equivalents and organizes import statements.
"""

import ast
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import ast as ast_types
    from collections.abc import Sequence


class ImportOrganizer:
    """Organize and rewrite imports for v2."""

    # Mapping of v1 module paths to v2 equivalents
    MODULE_MAPPINGS = {
        "clearskies.handlers": "clearskies.endpoints",
        "clearskies.column_types": "clearskies.columns",
        "clearskies.input_requirements": "clearskies.validators",
        "clearskies.authentication.authentication": "clearskies.authentication",
        "clearskies.binding_specs": "clearskies.di.inject",
    }

    # Import aliases that should be updated
    CLASS_MAPPINGS = {
        "Handlers": "Endpoints",
        "column_types": "columns",
        "input_requirements": "validators",
    }

    def rewrite_imports(self, source_code: str) -> str:
        """
        Rewrite all imports from v1 to v2.

        Args:
            source_code: Source code with v1 imports

        Returns:
            Source code with v2 imports
        """
        try:
            tree = ast.parse(source_code)
            self._rewrite_import_nodes(tree)
            return ast.unparse(tree)
        except SyntaxError:
            # Fallback to regex-based replacement
            return self._rewrite_imports_regex(source_code)

    def _rewrite_import_nodes(self, tree: ast.Module) -> None:
        """Rewrite import nodes in AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module in self.MODULE_MAPPINGS:
                    node.module = self.MODULE_MAPPINGS[node.module]
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in self.MODULE_MAPPINGS:
                        alias.name = self.MODULE_MAPPINGS[alias.name]

    def _rewrite_imports_regex(self, source_code: str) -> str:
        """Rewrite imports using regex patterns."""
        code = source_code

        # Rewrite module imports
        for old, new in self.MODULE_MAPPINGS.items():
            code = re.sub(rf"\bfrom {re.escape(old)} import\b", f"from {new} import", code)
            code = re.sub(rf"\bimport {re.escape(old)}\b", f"import {new}", code)

        return code

    def generate_import_block(self, required_imports: set[str]) -> str:
        """
        Generate organized import block.

        Args:
            required_imports: Set of import statements needed

        Returns:
            Organized import block
        """
        # Group imports by category
        stdlib = []
        third_party = []
        clearskies_imports = []

        for imp in sorted(required_imports):
            if imp.startswith("from typing") or imp.startswith("import typing"):
                stdlib.append(imp)
            elif imp.startswith("import clearskies") or imp.startswith("from clearskies"):
                clearskies_imports.append(imp)
            else:
                third_party.append(imp)

        # Build import block
        lines = []

        if stdlib:
            lines.extend(stdlib)
            lines.append("")

        if third_party:
            lines.extend(third_party)
            lines.append("")

        if clearskies_imports:
            lines.extend(clearskies_imports)
            lines.append("")

        return "\n".join(lines)

    def detect_required_imports(self, generated_code: str) -> set[str]:
        """
        Detect which imports are needed for generated code.

        Args:
            generated_code: Generated code to analyze

        Returns:
            Set of required import statements
        """
        required = set()

        # Check for clearskies usage
        if "clearskies.Model" in generated_code or re.search(r"\bclearskies\.\w+", generated_code):
            required.add("import clearskies")

        # Check for columns usage
        if "columns." in generated_code:
            required.add("from clearskies import columns")

        # Check for validators usage
        if "validators." in generated_code:
            required.add("from clearskies import validators")

        # Check for inject usage
        if "inject." in generated_code or "InjectableProperties" in generated_code:
            required.add("from clearskies.di import inject, InjectableProperties")

        # Check for configs usage
        if "configs." in generated_code:
            required.add("from clearskies import configs, configurable")

        # Check for decorators
        if "@parameters_to_properties" in generated_code:
            required.add("from clearskies.decorators import parameters_to_properties")

        # Check for loggable
        if "loggable.Loggable" in generated_code or "Loggable" in generated_code:
            required.add("from clearskies import loggable")

        # Check for type hints
        if ": Any" in generated_code or "-> Any" in generated_code:
            required.add("from typing import Any")

        if "TYPE_CHECKING" in generated_code:
            required.add("from typing import TYPE_CHECKING")

        return required

    def organize_imports(self, import_statements: list[str]) -> list[str]:
        """
        Organize import statements according to PEP 8.

        Args:
            import_statements: List of import statements

        Returns:
            Organized list of import statements
        """
        # Group imports
        stdlib = []
        third_party = []
        local = []

        for stmt in import_statements:
            if any(
                stmt.startswith(f"import {m}") or stmt.startswith(f"from {m}")
                for m in ["typing", "ast", "re", "pathlib", "collections", "dataclasses"]
            ):
                stdlib.append(stmt)
            elif "clearskies" in stmt:
                local.append(stmt)
            else:
                third_party.append(stmt)

        # Sort each group
        stdlib.sort()
        third_party.sort()
        local.sort()

        # Combine with blank lines between groups
        result = []
        if stdlib:
            result.extend(stdlib)
        if third_party:
            if result:
                result.append("")
            result.extend(third_party)
        if local:
            if result:
                result.append("")
            result.extend(local)

        return result

    def cleanup_unused_imports(self, source_code: str) -> str:
        """
        Remove unused import statements.

        Args:
            source_code: Source code to clean up

        Returns:
            Source code with unused imports removed
        """
        try:
            tree = ast.parse(source_code)

            # Collect all used names
            used_names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    used_names.add(node.id)
                elif isinstance(node, ast.Attribute):
                    # Get the root name
                    root: ast.expr = node
                    while isinstance(root, ast.Attribute):
                        root = root.value
                    if isinstance(root, ast.Name):
                        used_names.add(root.id)

            # Filter imports
            filtered_body: list[ast.stmt] = []
            for node in tree.body:
                if isinstance(node, ast.Import):
                    # Keep if any alias is used
                    keep = any((alias.asname or alias.name.split(".")[0]) in used_names for alias in node.names)
                    if keep:
                        filtered_body.append(node)
                elif isinstance(node, ast.ImportFrom):
                    # Keep if any imported name is used
                    keep = any((alias.asname or alias.name) in used_names for alias in node.names)
                    if keep:
                        filtered_body.append(node)
                else:
                    filtered_body.append(node)

            tree.body = filtered_body
            return ast.unparse(tree)

        except SyntaxError:
            # If parsing fails, return original code
            return source_code

    def merge_duplicate_imports(self, source_code: str) -> str:
        """
        Merge duplicate import statements.

        Args:
            source_code: Source code with possibly duplicate imports

        Returns:
            Source code with merged imports
        """
        try:
            tree = ast.parse(source_code)

            # Group ImportFrom statements by module
            import_groups: dict[str, set[str]] = {}

            new_body = []
            for node in tree.body:
                if isinstance(node, ast.ImportFrom) and node.module:
                    if node.module not in import_groups:
                        import_groups[node.module] = set()
                    for alias in node.names:
                        import_groups[node.module].add(alias.name)
                else:
                    new_body.append(node)

            # Create merged ImportFrom statements
            for module, names in sorted(import_groups.items()):
                import_node = ast.ImportFrom(
                    module=module,
                    names=[ast.alias(name=name, asname=None) for name in sorted(names)],
                    level=0,
                )
                new_body.insert(0, import_node)

            tree.body = new_body
            return ast.unparse(tree)

        except SyntaxError:
            return source_code
