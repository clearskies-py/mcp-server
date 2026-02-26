"""
Migration validator.

Validates generated v2 code for correctness and completeness.
"""

import ast
import re
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import MigrationPlan, ValidationReport


class MigrationValidator:
    """Validator for migration quality and correctness."""

    def validate(self, plan: "MigrationPlan") -> "ValidationReport":
        """
        Validate a migration plan.

        Args:
            plan: Migration plan to validate

        Returns:
            Validation report with issues and warnings
        """
        from .models import ValidationReport

        report = ValidationReport()

        for migration_file in plan.files:
            # Validate syntax
            if not self._validate_python_syntax(migration_file.content):
                report.add_error(
                    f"Invalid Python syntax in generated file",
                    migration_file.path,
                )

            # Validate imports
            import_issues = self._validate_imports(migration_file.content)
            for issue in import_issues:
                report.add_warning(issue, migration_file.path)

            #  Validate structure
            if "models" in str(migration_file.path):
                model_issues = self._validate_model_structure(migration_file.content)
                for issue in model_issues:
                    report.add_warning(issue, migration_file.path)

            if "endpoint" in str(migration_file.path):
                endpoint_issues = self._validate_endpoint_structure(migration_file.content)
                for issue in endpoint_issues:
                    report.add_warning(issue, migration_file.path)

        return report

    def _validate_python_syntax(self, code: str) -> bool:
        """Check if code has valid Python syntax."""
        try:
            ast.parse(code)
            return True
        except SyntaxError:
            return False

    def _validate_imports(self, code: str) -> list[str]:
        """Validate that imports are correct."""
        issues = []

        # Check for v1 imports that shouldn't be there
        v1_patterns = [
            r"from clearskies\.handlers import",
            r"from clearskies import Application",
            r"from clearskies import column_types",
            r"import clearskies\.column_types",
        ]

        for pattern in v1_patterns:
            if re.search(pattern, code):
                issues.append(f"Found v1 import pattern: {pattern}")

        # Check for required v2 imports
        if "class " in code and "clearskies.Model" in code:
            if "from clearskies import columns" not in code:
                issues.append("Missing 'from clearskies import columns' for model")

        return issues

    def _validate_model_structure(self, code: str) -> list[str]:
        """Validate model structure."""
        issues = []

        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check for Model base class
                    has_model_base = any(
                        (isinstance(base, ast.Attribute) and base.attr == "Model")
                        or (isinstance(base, ast.Name) and base.id == "Model")
                        for base in node.bases
                    )

                    if has_model_base:
                        # Check for backend attribute
                        has_backend = any(
                            isinstance(item, ast.Assign)
                            and any(isinstance(target, ast.Name) and target.id == "backend" for target in item.targets)
                            for item in node.body
                        )

                        if not has_backend:
                            issues.append(f"Model {node.name} missing backend attribute")

                        # Check for columns_configuration (shouldn't exist in v2)
                        has_old_config = any(
                            isinstance(item, ast.FunctionDef) and item.name == "columns_configuration"
                            for item in node.body
                        )

                        if has_old_config:
                            issues.append(
                                f"Model {node.name} still has columns_configuration() - should use class attributes"
                            )

        except SyntaxError:
            issues.append("Could not parse model code")

        return issues

    def _validate_endpoint_structure(self, code: str) -> list[str]:
        """Validate endpoint structure."""
        issues = []

        # Check for old Application usage
        if "Application(" in code:
            issues.append("Found Application() call - should use context wrapper")

        # Check for handler_config dict
        if "handler_config" in code:
            issues.append("Found handler_config dict - should use kwargs")

        # Check for readable/writeable column configuration
        if "RestfulApi(" in code:
            if "readable_column_names" not in code:
                issues.append("RestfulApi missing readable_column_names configuration")
            if "writeable_column_names" not in code:
                issues.append("RestfulApi missing writeable_column_names configuration")

        return issues

    def validate_completeness(self, v2_code: str, v1_code: str) -> list[str]:
        """
        Check if all v1 features are present in v2 code.

        Args:
            v2_code: Generated v2 code
            v1_code: Original v1 code

        Returns:
            List of missing features
        """
        missing = []

        # Extract v1 model columns
        v1_columns = self._extract_v1_columns(v1_code)
        v2_columns = self._extract_v2_columns(v2_code)

        for col_name in v1_columns:
            if col_name not in v2_columns:
                missing.append(f"Column '{col_name}' from v1 not found in v2")

        # Check for hooks
        v1_hooks = self._extract_hooks(v1_code)
        v2_hooks = self._extract_hooks(v2_code)

        for hook in v1_hooks:
            if hook not in v2_hooks:
                missing.append(f"Hook '{hook}' from v1 not found in v2")

        return missing

    def _extract_v1_columns(self, code: str) -> list[str]:
        """Extract column names from v1 code."""
        columns = []

        # Look for OrderedDict pattern
        pattern = r"\('(\w+)',\s*\{"
        matches = re.finditer(pattern, code)
        for match in matches:
            columns.append(match.group(1))

        return columns

    def _extract_v2_columns(self, code: str) -> list[str]:
        """Extract column names from v2 code."""
        columns = []

        # Look for column assignments: name = columns.Type()
        pattern = r"(\w+)\s*=\s*columns\.\w+\("
        matches = re.finditer(pattern, code)
        for match in matches:
            columns.append(match.group(1))

        return columns

    def _extract_hooks(self, code: str) -> list[str]:
        """Extract hook method names from code."""
        hooks = []
        hook_names = ["pre_save", "post_save", "save_finished", "pre_delete", "post_delete"]

        for hook in hook_names:
            if f"def {hook}" in code:
                hooks.append(hook)

        return hooks

    def check_best_practices(self, code: str) -> list[str]:
        """
        Check if code follows v2 best practices.

        Args:
            code: Generated code to check

        Returns:
            List of best practice violations
        """
        violations = []

        # Check for type hints
        if "def " in code and "->" not in code:
            violations.append("Methods missing return type hints")

        # Check for docstrings
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if not ast.get_docstring(node):
                        violations.append(f"{node.name} missing docstring")
        except SyntaxError:
            pass

        # Check for proper imports
        if "clearskies" in code:
            if "import clearskies" not in code:
                violations.append("Should use 'import clearskies' at top of file")

        return violations
