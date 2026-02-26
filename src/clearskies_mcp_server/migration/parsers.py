"""
Pattern parsers for analyzing v1 code structures.

These parsers extract structured information from v1 clearsk ies code.
"""

import ast
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .models import ColumnDefinition, DIUsage, HandlerDefinition, InitParam, ModelDefinition


class ModelParser:
    """Parse v1 model definitions."""

    def parse_file(self, file_path: Path) -> list["ModelDefinition"]:
        """Parse model definitions from a Python file."""
        from .models import ModelDefinition

        try:
            content = file_path.read_text()
            tree = ast.parse(content)
            models = []

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it's a Model subclass
                    if self._is_model_class(node):
                        model_def = self._parse_model_class(node, file_path)
                        if model_def:
                            models.append(model_def)

            return models
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return []

    def _is_model_class(self, node: ast.ClassDef) -> bool:
        """Check if a class definition is a Model subclass."""
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id == "Model":
                return True
            if isinstance(base, ast.Attribute) and base.attr == "Model":
                return True
        return False

    def _parse_model_class(self, node: ast.ClassDef, file_path: Path) -> "ModelDefinition | None":
        """Parse a model class definition."""
        from .mixin_detector import MixinDetector
        from .models import DIUsage, InitParam, MixinConfig, ModelDefinition
        from .parsers import ConfigParser, DIPatternDetector

        model_def = ModelDefinition(
            name=node.name,
            file_path=file_path,
        )

        # Initialize mixin detection
        mixin_detector = MixinDetector()
        di_detector = DIPatternDetector()
        config_parser = ConfigParser()

        # Detect mixins
        required_mixins = mixin_detector.detect_required_mixins(node)
        init_params = mixin_detector.extract_init_params(node)
        di_usage = di_detector.detect_di_usage(node)
        uses_logging = mixin_detector._has_logging(node)

        # Store mixin configuration
        model_def.mixin_config = MixinConfig(
            required_mixins=required_mixins,
            init_params=[
                InitParam(name=name, type_hint=type_hint, default=default) for name, type_hint, default in init_params
            ],
            di_usage=di_usage,
            uses_logging=uses_logging,
        )

        # Extract class attributes
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        if target.id == "id_column_name":
                            if isinstance(item.value, ast.Constant):
                                model_def.id_column = item.value.value
                        elif target.id == "table_name":
                            if isinstance(item.value, ast.Constant):
                                model_def.table_name = item.value.value

            # Look for columns_configuration method
            elif isinstance(item, ast.FunctionDef) and item.name == "columns_configuration":
                model_def.columns = self._parse_columns_configuration(item)

            # Look for hooks
            elif isinstance(item, ast.FunctionDef):
                if item.name in ["pre_save", "post_save", "save_finished", "pre_delete", "post_delete"]:
                    model_def.hooks.append(item.name)
                elif not item.name.startswith("_") and item.name not in [
                    "columns_configuration",
                    "all_columns",
                ]:
                    model_def.custom_methods.append(item.name)

        return model_def

    def _parse_columns_configuration(self, func_def: ast.FunctionDef) -> list["ColumnDefinition"]:
        """Parse columns_configuration method to extract column definitions."""
        from .models import ColumnDefinition

        columns = []

        for stmt in func_def.body:
            if isinstance(stmt, ast.Return) and stmt.value:
                # Look for OrderedDict([...])
                if isinstance(stmt.value, ast.Call):
                    if hasattr(stmt.value.func, "id") and stmt.value.func.id == "OrderedDict":
                        if stmt.value.args and isinstance(stmt.value.args[0], ast.List):
                            for elt in stmt.value.args[0].elts:
                                if isinstance(elt, ast.Tuple) and len(elt.elts) == 2:
                                    col_def = self._parse_column_tuple(elt)
                                    if col_def:
                                        columns.append(col_def)

        return columns

    def _parse_column_tuple(self, tuple_node: ast.Tuple) -> "ColumnDefinition | None":
        """Parse a single column tuple from OrderedDict."""
        from .models import ColumnDefinition

        if len(tuple_node.elts) != 2:
            return None

        # Column name
        name_node = tuple_node.elts[0]
        if not isinstance(name_node, ast.Constant):
            return None
        col_name = name_node.value

        # Column config dict
        config_node = tuple_node.elts[1]
        if not isinstance(config_node, ast.Dict):
            return None

        config = {}
        column_class = "String"

        for key_node, value_node in zip(config_node.keys, config_node.values):
            if isinstance(key_node, ast.Constant):
                key = key_node.value

                if key == "class":
                    # Extract column class
                    if isinstance(value_node, ast.Attribute):
                        column_class = value_node.attr
                    elif isinstance(value_node, ast.Name):
                        column_class = value_node.id
                else:
                    # Store other config
                    config[key] = self._extract_value(value_node)

        return ColumnDefinition(name=col_name, column_class=column_class, config=config)

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
            return node.id
        return None


class HandlerParser:
    """Parse v1 handler definitions."""

    def parse_file(self, file_path: Path) -> list["HandlerDefinition"]:
        """Parse handler definitions from a Python file."""
        from .models import HandlerDefinition

        try:
            content = file_path.read_text()
            tree = ast.parse(content)
            handlers = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    handler_def = self._parse_application_call(node)
                    if handler_def:
                        handlers.append(handler_def)

            return handlers
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return []

    def _parse_application_call(self, node: ast.Call) -> "HandlerDefinition | None":
        """Parse an Application() call."""
        from .models import HandlerDefinition

        # Check if this is an Application call
        if isinstance(node.func, ast.Name) and node.func.id == "Application":
            handler_def = HandlerDefinition(name="unnamed_handler", handler_class="")

            for kw in node.keywords:
                if kw.arg == "handler_class":
                    if isinstance(kw.value, ast.Name):
                        handler_def.handler_class = kw.value.id
                    elif isinstance(kw.value, ast.Attribute):
                        handler_def.handler_class = kw.value.attr

                elif kw.arg == "handler_config":
                    if isinstance(kw.value, ast.Dict):
                        handler_def.config = self._parse_dict(kw.value)

            return handler_def

        return None

    def _parse_dict(self, node: ast.Dict) -> dict[str, Any]:
        """Parse a dictionary AST node."""
        result = {}
        for key_node, value_node in zip(node.keys, node.values):
            if isinstance(key_node, ast.Constant):
                key = key_node.value
                value = self._extract_value(value_node)
                result[key] = value
        return result

    def _extract_value(self, node: ast.AST) -> Any:
        """Extract value from AST node."""
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return f"{self._extract_value(node.value)}.{node.attr}"
        if isinstance(node, ast.List):
            return [self._extract_value(elt) for elt in node.elts]
        if isinstance(node, ast.Dict):
            return {
                self._extract_value(k): self._extract_value(v) for k, v in zip(node.keys, node.values) if k is not None
            }
        return None


class ColumnParser:
    """Parse column definitions from OrderedDict structures."""

    def parse_ordered_dict(self, ordered_dict_code: str) -> list["ColumnDefinition"]:
        """Parse column definitions from OrderedDict code string."""
        from .models import ColumnDefinition

        columns = []

        # Extract column definitions using regex
        # Pattern: ('column_name', {'class': column_types.ColumnClass, ...})
        pattern = r"\('(\w+)',\s*\{([^}]+)\}\)"
        matches = re.finditer(pattern, ordered_dict_code)

        for match in matches:
            col_name = match.group(1)
            col_config = match.group(2)

            # Extract column class
            class_match = re.search(r"'class':\s*\w+\.(\w+)", col_config)
            column_class = class_match.group(1) if class_match else "String"

            columns.append(ColumnDefinition(name=col_name, column_class=column_class))

        return columns


class DIParser:
    """Parse dependency injection configurations."""

    def parse_bindings(self, application_code: str) -> dict[str, Any]:
        """Parse bindings from Application initialization."""
        bindings = {}

        # Extract bindings dict
        bindings_match = re.search(r"bindings\s*=\s*\{([^}]+)\}", application_code)
        if bindings_match:
            bindings_str = bindings_match.group(1)
            # Simple parsing - could be enhanced with AST
            for line in bindings_str.split(","):
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip().strip("'\"")
                    value = value.strip()
                    bindings[key] = value

        return bindings


class ApplicationParser:
    """Parse Application configurations."""

    def parse_file(self, file_path: Path) -> list[dict[str, Any]]:
        """Parse Application definitions from a Python file."""
        try:
            content = file_path.read_text()
            tree = ast.parse(content)
            applications = []

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id == "Application":
                        app_config = self._parse_application_call(node)
                        if app_config:
                            applications.append(app_config)

            return applications
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return []

    def _parse_application_call(self, node: ast.Call) -> dict[str, Any] | None:
        """Parse an Application() call."""
        config = {}

        for kw in node.keywords:
            if kw.arg in ["handler_class", "handler_config", "bindings", "binding_classes", "binding_modules"]:
                config[kw.arg] = self._extract_value(kw.value)

        return config if config else None

    def _extract_value(self, node: ast.AST) -> Any:
        """Extract value from AST node."""
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Attribute):
            return f"{self._extract_value(node.value)}.{node.attr}"
        if isinstance(node, ast.List):
            return [self._extract_value(elt) for elt in node.elts]
        if isinstance(node, ast.Dict):
            result = {}
            for k, v in zip(node.keys, node.values):
                if k is not None:
                    key = self._extract_value(k)
                    value = self._extract_value(v)
                    result[key] = value
            return result
        return None


class ConfigParser:
    """Parse __init__ parameters and convert to configs.* attributes."""

    def extract_init_params(self, func_def: ast.FunctionDef) -> list["InitParam"]:
        """
        Extract parameters from __init__ method.

        Args:
            func_def: AST node of the __init__ function

        Returns:
            List of InitParam objects
        """
        from .models import InitParam

        params = []
        args = func_def.args

        # Calculate defaults mapping
        defaults_start = len(args.args) - len(args.defaults)

        for idx, arg in enumerate(args.args):
            if arg.arg in ["self", "di"]:
                continue

            # Extract default value
            default = None
            if idx >= defaults_start:
                default_node = args.defaults[idx - defaults_start]
                default = self._extract_value(default_node)

            # Extract type hint
            type_hint = None
            if arg.annotation:
                type_hint = ast.unparse(arg.annotation)

            params.append(InitParam(name=arg.arg, default=default, type_hint=type_hint))

        return params

    def infer_config_type(self, param: "InitParam") -> str:
        """
        Infer configs.* type from parameter.

        Args:
            param: InitParam to analyze

        Returns:
            Config type string (e.g., 'configs.String')
        """
        # Infer from type hint first
        if param.type_hint:
            type_hint = param.type_hint.lower()
            if "str" in type_hint:
                return "configs.String"
            if "int" in type_hint:
                return "configs.Integer"
            if "bool" in type_hint:
                return "configs.Boolean"
            if "dict" in type_hint:
                return "configs.StringDict"
            if "list" in type_hint:
                return "configs.List"

        # Infer from default value
        if isinstance(param.default, str):
            return "configs.String"
        if isinstance(param.default, int) and not isinstance(param.default, bool):
            return "configs.Integer"
        if isinstance(param.default, bool):
            return "configs.Boolean"
        if isinstance(param.default, dict):
            return "configs.StringDict"
        if isinstance(param.default, list):
            return "configs.List"

        # Default fallback
        return "configs.String"

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


class DIPatternDetector:
    """Detect v1 DI patterns that need migration."""

    def detect_di_usage(self, class_node: ast.ClassDef) -> "DIUsage":
        """
        Detect how a class uses DI in v1.

        Args:
            class_node: AST node of the class

        Returns:
            DIUsage object with detected patterns
        """
        from .models import DIUsage

        usage = DIUsage()

        for item in class_node.body:
            if isinstance(item, ast.FunctionDef):
                if item.name == "__init__":
                    usage.has_di_init = self._has_di_param(item)

                # Detect self._di.build() and di.build() calls
                for node in ast.walk(item):
                    if isinstance(node, ast.Call):
                        if self._is_di_build_call(node):
                            target = self._extract_di_build_target(node)
                            if target:
                                usage.di_builds.append(target)

        return usage

    def _has_di_param(self, func_def: ast.FunctionDef) -> bool:
        """Check if function has a 'di' parameter."""
        for arg in func_def.args.args:
            if arg.arg == "di":
                return True
        return False

    def _is_di_build_call(self, node: ast.Call) -> bool:
        """
        Check if node is a self._di.build() or di.build() call.

        Args:
            node: AST call node

        Returns:
            True if it's a DI build call
        """
        if isinstance(node.func, ast.Attribute):
            if node.func.attr == "build":
                if isinstance(node.func.value, ast.Attribute):
                    # self._di.build() or self.di.build()
                    return node.func.value.attr in ["_di", "di"]
                elif isinstance(node.func.value, ast.Name):
                    # di.build()
                    return node.func.value.id == "di"
        return False

    def _extract_di_build_target(self, node: ast.Call) -> str | None:
        """
        Extract the target class/service name from di.build() call.

        Args:
            node: AST call node

        Returns:
            Target name or None
        """
        if node.args:
            first_arg = node.args[0]
            if isinstance(first_arg, ast.Constant):
                return first_arg.value
            if isinstance(first_arg, ast.Name):
                return first_arg.id
        return None


class ContextDetector:
    """Detect appropriate v2 context from v1 usage."""

    def infer_context_type(self, file_path: Path, app_node: ast.Call | None = None) -> str:
        """
        Infer v2 context type from v1 Application call and file path.

        Args:
            file_path: Path to the application file
            app_node: Optional AST node of Application call

        Returns:
            Context type string (WsgiRef, Cli, Lambda, etc.)
        """
        # Check file name patterns
        file_name_lower = file_path.name.lower()

        if "lambda" in file_name_lower:
            return "Lambda"
        if "cli" in file_name_lower or "command" in file_name_lower or "console" in file_name_lower:
            return "Cli"
        if "wsgi" in file_name_lower and "ref" not in file_name_lower:
            return "Wsgi"

        # Check for WSGI patterns in the code
        if app_node and self._has_wsgi_pattern(app_node):
            return "Wsgi"

        # Check for CLI patterns
        if app_node and self._has_cli_pattern(app_node):
            return "Cli"

        # Default to WsgiRef for development
        return "WsgiRef"

    def _has_wsgi_pattern(self, app_node: ast.Call) -> bool:
        """
        Check if Application is used in WSGI context.

        Args:
            app_node: AST node of Application call

        Returns:
            True if WSGI patterns detected
        """
        # Look for .wsgi property access
        # Check if the Application is assigned to a variable named 'application' or 'wsgi'
        return False  # TODO: Enhance detection

    def _has_cli_pattern(self, app_node: ast.Call) -> bool:
        """
        Check if Application is used in CLI context.

        Args:
            app_node: AST node of Application call

        Returns:
            True if CLI patterns detected
        """
        # Look for CLI handler configurations
        for kw in app_node.keywords:
            if kw.arg == "handler_class":
                if isinstance(kw.value, ast.Attribute):
                    if "cli" in kw.value.attr.lower():
                        return True
        return False
