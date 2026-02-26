"""
Type hint generation for migrated code.

Adds Python 3.13+ type hints to generated v2 code.
"""

import ast
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


class TypeHintGenerator:
    """Add type hints to migrated code."""

    # Common type hint mappings
    TYPE_HINTS = {
        "input_output": "InputOutput",
        "model": "Model",
        "data": "dict[str, Any]",
        "id": "str | int",
        "kwargs": "Any",
        "cursor": "Cursor",
        "di": "DI",
        "models": "Models",
        "utcnow": "callable",
        "environment": "Environment",
        "logger": "Logger",
        "config": "dict[str, Any]",
        "self": None,  # Never type hint self
    }

    # Return type hints for common methods
    RETURN_TYPES = {
        "pre_save": "None",
        "post_save": "None",
        "save_finished": "None",
        "pre_delete": "None",
        "post_delete": "None",
        "__init__": "None",
        "configure": "None",
        "validate": "bool",
        "to_dict": "dict[str, Any]",
        "get_id": "str | int",
    }

    def add_type_hints_to_model(self, model_code: str) -> str:
        """
        Add type hints to model methods.

        Args:
            model_code: Source code of a model class

        Returns:
            Model code with type hints added
        """
        try:
            tree = ast.parse(model_code)

            # Find class definitions
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Add type hints to methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            self._add_type_hints_to_function(item)

            # Convert back to source code
            return ast.unparse(tree)
        except SyntaxError:
            # If parsing fails, return original code
            return model_code

    def _add_type_hints_to_function(self, func_def: ast.FunctionDef) -> None:
        """Add type hints to a function definition."""
        # Add parameter type hints
        for arg in func_def.args.args:
            if arg.arg != "self" and arg.annotation is None:
                type_hint = self.infer_parameter_type(arg.arg, func_def.name)
                if type_hint:
                    arg.annotation = ast.Name(id=type_hint, ctx=ast.Load())

        # Add return type hint
        if func_def.returns is None:
            return_type = self.infer_return_type(func_def.name)
            if return_type:
                func_def.returns = ast.Name(id=return_type, ctx=ast.Load())

    def infer_parameter_type(self, param_name: str, context: str) -> str | None:
        """
        Infer type hint from parameter name and context.

        Args:
            param_name: Name of the parameter
            context: Function/method name context

        Returns:
            Type hint string or None
        """
        # Check exact matches first
        if param_name in self.TYPE_HINTS:
            return self.TYPE_HINTS[param_name]

        # Check patterns
        if param_name.endswith("_id"):
            return "str | int"
        if param_name.endswith("_at"):
            return "datetime"
        if param_name.endswith("_list"):
            return "list[Any]"
        if param_name.endswith("_dict"):
            return "dict[str, Any]"
        if param_name.startswith("is_") or param_name.startswith("has_"):
            return "bool"
        if param_name.endswith("_count"):
            return "int"

        # Default to Any for unknown parameters
        return "Any"

    def infer_return_type(self, method_name: str) -> str | None:
        """
        Infer return type from method name.

        Args:
            method_name: Name of the method

        Returns:
            Return type hint string or None
        """
        # Check exact matches
        if method_name in self.RETURN_TYPES:
            return self.RETURN_TYPES[method_name]

        # Check patterns
        if method_name.startswith("get_"):
            return "Any"
        if method_name.startswith("find_"):
            return "Model | None"
        if method_name.startswith("list_"):
            return "list[Model]"
        if method_name.startswith("is_") or method_name.startswith("has_"):
            return "bool"
        if method_name.startswith("count_"):
            return "int"
        if method_name.startswith("save") or method_name.startswith("update") or method_name.startswith("delete"):
            return "None"

        return None

    def generate_type_checking_block(self, imports: list[str]) -> str:
        """
        Generate TYPE_CHECKING block for circular import avoidance.

        Args:
            imports: List of types to import conditionally

        Returns:
            TYPE_CHECKING block as string
        """
        if not imports:
            return ""

        lines = [
            "from typing import TYPE_CHECKING, Any",
            "",
            "if TYPE_CHECKING:",
        ]

        for import_str in imports:
            lines.append(f"    {import_str}")

        return "\n".join(lines)

    def detect_required_imports(self, code: str) -> list[str]:
        """
        Detect which type imports are needed for code.

        Args:
            code: Source code to analyze

        Returns:
            List of import statements needed
        """
        required = []

        # Check for type hint usage
        if "InputOutput" in code:
            required.append("from clearskies.input_outputs.input_output import InputOutput")
        if re.search(r":\s*Model", code) or re.search(r"->\s*Model", code):
            required.append("from clearskies.model import Model")
        if "Cursor" in code:
            required.append("from clearskies.backends.cursor import Cursor")
        if "DI" in code and "from clearskies" not in code:
            required.append("from clearskies.di.di import DI")
        if "Models" in code:
            required.append("from clearskies.models import Models")
        if "Environment" in code:
            required.append("from clearskies.environment import Environment")
        if "Logger" in code:
            required.append("from logging import Logger")

        return required

    def add_hints_to_hook_method(self, hook_name: str, parameters: list[str] | None = None) -> str:
        """
        Generate a hook method with proper type hints.

        Args:
            hook_name: Name of the hook (pre_save, post_save, etc.)
            parameters: Optional list of parameter names

        Returns:
            Fully typed hook method stub
        """
        params = parameters or []

        # Build parameter list with type hints
        param_strs = ["self"]
        for param in params:
            type_hint = self.infer_parameter_type(param, hook_name)
            if type_hint:
                param_strs.append(f"{param}: {type_hint}")
            else:
                param_strs.append(param)

        param_strs.append("**kwargs: Any")

        return_type = self.RETURN_TYPES.get(hook_name, "None")

        return f"""    def {hook_name}({", ".join(param_strs)}) -> {return_type}:
        \"\"\"Hook: {hook_name}.\"\"\"
        # TODO: Migrate {hook_name} logic
        pass"""

    def add_hints_to_method(
        self, method_name: str, parameters: list[tuple[str, str | None]] | None = None, return_type: str | None = None
    ) -> str:
        """
        Generate a method signature with type hints.

        Args:
            method_name: Name of the method
            parameters: List of (name, type_hint) tuples
            return_type: Return type hint (inferred if None)

        Returns:
            Method signature with type hints
        """
        params = parameters or []

        # Build parameter list
        param_strs = ["self"]
        for param_name, param_type in params:
            if param_type:
                param_strs.append(f"{param_name}: {param_type}")
            else:
                inferred_type = self.infer_parameter_type(param_name, method_name)
                if inferred_type:
                    param_strs.append(f"{param_name}: {inferred_type}")
                else:
                    param_strs.append(param_name)

        # Determine return type
        if return_type is None:
            return_type = self.infer_return_type(method_name) or "None"

        return f"def {method_name}({', '.join(param_strs)}) -> {return_type}:"
