"""
Mixin detection and generation for v2 migration.

Detects which mixins (Configurable, InjectableProperties, Loggable) a v1 class needs in v2.
"""

import ast
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence


class MixinDetector:
    """Detect which mixins a v1 class needs in v2."""

    def detect_required_mixins(self, class_node: ast.ClassDef) -> list[str]:
        """
        Analyze v1 class to determine required v2 mixins.

        Args:
            class_node: AST node of the class to analyze

        Returns:
            List of mixin names needed
        """
        mixins = []

        # Check for Configurable mixin (has __init__ with parameters)
        if self._has_init_params(class_node):
            mixins.append("configurable.Configurable")

        # Check for InjectableProperties mixin (uses DI)
        if self._has_di_usage(class_node):
            mixins.append("InjectableProperties")

        # Check for Loggable mixin (uses logging)
        if self._has_logging(class_node):
            mixins.append("loggable.Loggable")

        return mixins

    def _has_init_params(self, class_node: ast.ClassDef) -> bool:
        """
        Check if class has __init__ with parameters beyond self.

        Args:
            class_node: AST node of the class

        Returns:
            True if __init__ has parameters
        """
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                # Has params beyond self (and possibly di)
                param_count = len(item.args.args)
                # Subtract self
                param_count -= 1
                # Subtract di if present (that's handled by InjectableProperties)
                if self._has_di_param(item):
                    param_count -= 1
                return param_count > 0
        return False

    def _has_di_usage(self, class_node: ast.ClassDef) -> bool:
        """
        Check if class uses DI (has __init__(self, di) pattern or uses self.di).

        Args:
            class_node: AST node of the class

        Returns:
            True if class uses DI
        """
        # Check for di parameter in __init__
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                if self._has_di_param(item):
                    return True

        # Check for self.di or self._di usage in methods
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                for node in ast.walk(item):
                    if isinstance(node, ast.Attribute):
                        if isinstance(node.value, ast.Name) and node.value.id == "self":
                            if node.attr in ["di", "_di"]:
                                return True

        return False

    def _has_di_param(self, func_def: ast.FunctionDef) -> bool:
        """
        Check if function has a 'di' parameter.

        Args:
            func_def: AST node of the function

        Returns:
            True if function has di parameter
        """
        for arg in func_def.args.args:
            if arg.arg == "di":
                return True
        return False

    def _has_logging(self, class_node: ast.ClassDef) -> bool:
        """
        Check if class uses logging.

        Args:
            class_node: AST node of the class

        Returns:
            True if class uses logging
        """
        for node in ast.walk(class_node):
            # Check for .logger attribute access
            if isinstance(node, ast.Attribute) and node.attr == "logger":
                return True
            # Check for logging module usage
            if isinstance(node, ast.Name) and "logging" in node.id.lower():
                return True
            # Check for self.log(...) calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ["debug", "info", "warning", "error", "critical"]:
                        if isinstance(node.func.value, ast.Attribute):
                            if node.func.value.attr == "logger":
                                return True
        return False

    def extract_init_params(self, class_node: ast.ClassDef) -> list[tuple[str, str | None, Any]]:
        """
        Extract __init__ parameters for Configurable mixin detection.

        Args:
            class_node: AST node of the class

        Returns:
            List of (param_name, type_hint, default_value) tuples
        """
        for item in class_node.body:
            if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                return self._extract_function_params(item)
        return []

    def _extract_function_params(self, func_def: ast.FunctionDef) -> list[tuple[str, str | None, Any]]:
        """
        Extract parameters from a function definition.

        Args:
            func_def: AST node of the function

        Returns:
            List of (param_name, type_hint, default_value) tuples
        """
        params = []
        args = func_def.args

        # Calculate defaults mapping
        defaults_start = len(args.args) - len(args.defaults)

        for idx, arg in enumerate(args.args):
            if arg.arg in ["self", "di"]:
                continue

            # Extract type hint
            type_hint = None
            if arg.annotation:
                type_hint = ast.unparse(arg.annotation)

            # Extract default value
            default = None
            if idx >= defaults_start:
                default_node = args.defaults[idx - defaults_start]
                default = self._extract_value(default_node)

            params.append((arg.arg, type_hint, default))

        return params

    def _extract_value(self, node: ast.AST) -> Any:
        """Extract value from AST node."""
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.List):
            return [self._extract_value(elt) for elt in node.elts]
        if isinstance(node, ast.Dict):
            return {
                self._extract_value(k): self._extract_value(v) for k, v in zip(node.keys, node.values) if k is not None
            }
        if isinstance(node, ast.Name):
            if node.id == "True":
                return True
            if node.id == "False":
                return False
            if node.id == "None":
                return None
            return node.id
        return None


class MixinGenerator:
    """Generate mixin-based class definitions."""

    # Mixin order matters: Configurable, InjectableProperties, Loggable, BaseClass
    MIXIN_ORDER = [
        "configurable.Configurable",
        "InjectableProperties",
        "loggable.Loggable",
    ]

    def generate_class_with_mixins(
        self,
        class_name: str,
        mixins: list[str],
        base_class: str = "clearskies.Model",
    ) -> str:
        """
        Generate class definition with proper mixin inheritance.

        Args:
            class_name: Name of the class
            mixins: List of mixin names to include
            base_class: Base class name

        Returns:
            Class definition string
        """
        # Order mixins according to MIXIN_ORDER
        ordered_mixins = []
        for mixin in self.MIXIN_ORDER:
            if mixin in mixins:
                ordered_mixins.append(mixin)

        # Add base class at the end
        inheritance = ordered_mixins + [base_class]

        return f"class {class_name}({', '.join(inheritance)}):"

    def generate_required_imports(self, mixins: list[str]) -> list[str]:
        """
        Generate import statements for mixins.

        Args:
            mixins: List of mixin names

        Returns:
            List of import strings
        """
        imports = []

        if "configurable.Configurable" in mixins:
            imports.append("from clearskies import configs, configurable")
            imports.append("from clearskies.decorators import parameters_to_properties")

        if "InjectableProperties" in mixins:
            imports.append("from clearskies.di import inject, InjectableProperties")

        if "loggable.Loggable" in mixins:
            imports.append("from clearskies import loggable")

        return imports

    def should_use_mixin(self, mixin_name: str, class_features: dict[str, bool]) -> bool:
        """
        Determine if a mixin should be used based on class features.

        Args:
            mixin_name: Name of the mixin to check
            class_features: Dictionary of detected features

        Returns:
            True if mixin should be used
        """
        if mixin_name == "configurable.Configurable":
            return class_features.get("has_init_params", False)

        if mixin_name == "InjectableProperties":
            return class_features.get("uses_di", False)

        if mixin_name == "loggable.Loggable":
            return class_features.get("uses_logging", False)

        return False
