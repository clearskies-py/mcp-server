"""
V1 codebase analyzer.

Scans and analyzes clearskies v1 projects to understand their structure.
"""

from pathlib import Path
from typing import TYPE_CHECKING

from .parsers import ApplicationParser, HandlerParser, ModelParser

if TYPE_CHECKING:
    from .models import AnalysisReport


class V1CodebaseAnalyzer:
    """Analyzer for clearskies v1 codebases."""

    def __init__(self, project_path: str | Path):
        """
        Initialize the analyzer.

        Args:
            project_path: Path to the v1 project directory
        """
        self.project_path = Path(project_path)
        self.model_parser = ModelParser()
        self.handler_parser = HandlerParser()
        self.application_parser = ApplicationParser()

    def analyze(self) -> "AnalysisReport":
        """
        Perform full codebase analysis.

        Returns:
            Complete analysis report
        """
        from .models import AnalysisReport

        report = AnalysisReport(project_path=self.project_path)

        # Discover all Python files
        python_files = self._discover_python_files()

        # Parse each file
        for file_path in python_files:
            try:
                # Try to parse as model file
                models = self.model_parser.parse_file(file_path)
                report.models.extend(models)

                # Try to parse as handler/application file
                handlers = self.handler_parser.parse_file(file_path)
                report.handlers.extend(handlers)

            except Exception as e:
                report.errors.append(f"Error parsing {file_path}: {e}")

        # Generate warnings
        report.warnings.extend(self._generate_warnings(report))

        return report

    def _discover_python_files(self) -> list[Path]:
        """
        Discover all Python files in the project.

        Returns:
            List of Python file paths
        """
        python_files = []

        for path in self.project_path.rglob("*.py"):
            # Skip common directories
            if any(part in path.parts for part in [".venv", "venv", "__pycache__", ".git", "tests"]):
                continue
            python_files.append(path)

        return python_files

    def _generate_warnings(self, report: "AnalysisReport") -> list[str]:
        """
        Generate warnings based on analysis.

        Args:
            report: Current analysis report

        Returns:
            List of warning messages
        """
        warnings = []

        # Check for models without explicit backend
        models_without_backend = [m for m in report.models if m.backend == "MemoryBackend"]
        if len(models_without_backend) > len(report.models) * 0.5:
            warnings.append(
                f"{len(models_without_backend)} models using default MemoryBackend - may need real backend in v2"
            )

        # Check for handlers without explicit configuration
        handlers_needing_attention = [h for h in report.handlers if not h.config.get("readable_columns")]
        if handlers_needing_attention:
            warnings.append(
                f"{len(handlers_needing_attention)} handlers will need explicit readable_column_names in v2"
            )

        # Check for models with many custom methods
        complex_models = [m for m in report.models if len(m.custom_methods) > 5]
        if complex_models:
            warnings.append(f"{len(complex_models)} models have >5 custom methods - review for proper v2 patterns")

        return warnings

    def analyze_single_file(self, file_path: str | Path) -> dict[str, list | str]:
        """
        Analyze a single Python file.

        Args:
            file_path: Path to the Python file

        Returns:
            Dictionary with parsed models and handlers
        """
        file_path = Path(file_path)
        result: dict[str, list | str] = {"models": [], "handlers": [], "applications": []}

        try:
            result["models"] = self.model_parser.parse_file(file_path)
            result["handlers"] = self.handler_parser.parse_file(file_path)
            result["applications"] = self.application_parser.parse_file(file_path)
        except Exception as e:
            result["error"] = str(e)

        return result

    def get_migration_complexity(self, report: "AnalysisReport") -> dict[str, str | int]:
        """
        Assess the complexity of the migration.

        Args:
            report: Analysis report

        Returns:
            Dict with complexity metrics
        """
        total_models = len(report.models)
        total_handlers = len(report.handlers)
        total_custom_methods = sum(len(m.custom_methods) for m in report.models)
        total_hooks = sum(len(m.hooks) for m in report.models)

        # Calculate complexity score
        complexity_score = total_models * 1 + total_handlers * 2 + total_custom_methods * 0.5 + total_hooks * 0.5

        if complexity_score < 10:
            complexity_level = "simple"
        elif complexity_score < 30:
            complexity_level = "moderate"
        elif complexity_score < 60:
            complexity_level = "complex"
        else:
            complexity_level = "very_complex"

        return {
            "complexity_level": complexity_level,
            "complexity_score": int(complexity_score),
            "total_models": total_models,
            "total_handlers": total_handlers,
            "total_custom_methods": total_custom_methods,
            "total_hooks": total_hooks,
            "estimated_migration_time_hours": max(1, int(complexity_score / 10)),
        }
