"""
Data models for the migration system.

These models represent the structure of v1 code and migration results.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence


@dataclass
class InitParam:
    """Parameter from __init__ method."""

    name: str
    default: Any | None = None
    type_hint: str | None = None


@dataclass
class DIUsage:
    """Detected DI usage patterns in a class."""

    has_di_init: bool = False
    di_builds: list[str] = field(default_factory=list)
    inject_properties: dict[str, str] = field(default_factory=dict)  # property_name -> class_name


@dataclass
class AuthConfig:
    """Authentication configuration."""

    auth_type: str = ""
    environment_key: str = ""
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class MixinConfig:
    """Mixin configuration for a class."""

    required_mixins: list[str] = field(default_factory=list)
    init_params: list[InitParam] = field(default_factory=list)
    di_usage: DIUsage = field(default_factory=DIUsage)
    uses_logging: bool = False


@dataclass
class ColumnDefinition:
    """Definition of a model column."""

    name: str
    column_class: str
    config: dict[str, Any] = field(default_factory=dict)
    is_relationship: bool = False
    relationship_type: str | None = None  # 'belongs_to', 'has_many', 'many_to_many'


@dataclass
class ModelDefinition:
    """Definition of a v1 model."""

    name: str
    file_path: Path
    id_column: str = "id"
    table_name: str | None = None
    columns: list[ColumnDefinition] = field(default_factory=list)
    backend: str = "MemoryBackend"
    hooks: list[str] = field(default_factory=list)
    relationships: list[ColumnDefinition] = field(default_factory=list)
    custom_methods: list[str] = field(default_factory=list)
    base_classes: list[str] = field(default_factory=list)
    mixin_config: MixinConfig | None = None  # Detected mixin requirements


@dataclass
class HandlerDefinition:
    """Definition of a v1 handler."""

    name: str
    handler_class: str
    config: dict[str, Any] = field(default_factory=dict)
    model_class: str | None = None
    base_url: str | None = None
    authentication: str | None = None
    decorators: list[str] = field(default_factory=list)


@dataclass
class ApplicationDefinition:
    """Definition of a v1 application."""

    file_path: Path
    handler_config: HandlerDefinition | None = None
    bindings: dict[str, Any] = field(default_factory=dict)
    binding_classes: list[str] = field(default_factory=list)
    binding_modules: list[str] = field(default_factory=list)
    context_type: str = "wsgi"  # wsgi, cli, etc.


@dataclass
class DIBinding:
    """Dependency injection binding."""

    name: str
    value: Any
    binding_type: str  # 'instance', 'class', 'module'


@dataclass
class AnalysisReport:
    """Complete analysis report of a v1 codebase."""

    project_path: Path
    models: list[ModelDefinition] = field(default_factory=list)
    handlers: list[HandlerDefinition] = field(default_factory=list)
    applications: list[ApplicationDefinition] = field(default_factory=list)
    di_bindings: list[DIBinding] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "project_path": str(self.project_path),
            "models": [
                {
                    "name": m.name,
                    "file_path": str(m.file_path),
                    "id_column": m.id_column,
                    "columns": [
                        {"name": c.name, "column_class": c.column_class, "config": c.config} for c in m.columns
                    ],
                    "backend": m.backend,
                    "hooks": m.hooks,
                }
                for m in self.models
            ],
            "handlers": [
                {
                    "name": h.name,
                    "handler_class": h.handler_class,
                    "config": h.config,
                    "model_class": h.model_class,
                }
                for h in self.handlers
            ],
            "applications": [
                {"file_path": str(a.file_path), "context_type": a.context_type} for a in self.applications
            ],
            "errors": self.errors,
            "warnings": self.warnings,
        }


@dataclass
class MappingResult:
    """Result of mapping a v1 concept to v2."""

    v2_class: str | None
    breaking_changes: list[str] = field(default_factory=list)
    migration_notes: list[str] = field(default_factory=list)
    example_v1: str = ""
    example_v2: str = ""


@dataclass
class MigrationFile:
    """A file to be created/modified during migration."""

    path: Path
    content: str
    operation: str = "create"  # 'create', 'update'
    original_content: str | None = None


@dataclass
class MigrationPlan:
    """Complete migration plan with all files to be generated."""

    files: list[MigrationFile] = field(default_factory=list)
    breaking_changes: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    manual_steps: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "files": [{"path": str(f.path), "operation": f.operation, "content": f.content} for f in self.files],
            "breaking_changes": self.breaking_changes,
            "warnings": self.warnings,
            "manual_steps": self.manual_steps,
        }

    def apply(self, output_path: Path, dry_run: bool = False) -> None:
        """Apply the migration plan to the filesystem."""
        for migration_file in self.files:
            target_path = output_path / migration_file.path
            if dry_run:
                print(f"Would {migration_file.operation}: {target_path}")
                continue

            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(migration_file.content)


@dataclass
class ValidationIssue:
    """Validation issue found in migrated code."""

    severity: str  # 'error', 'warning'
    message: str
    file_path: Path | None = None
    line_number: int | None = None


@dataclass
class ValidationReport:
    """Report of migration validation."""

    issues: list[ValidationIssue] = field(default_factory=list)
    is_valid: bool = True

    def add_error(self, message: str, file_path: Path | None = None, line_number: int | None = None) -> None:
        """Add an error to the report."""
        self.issues.append(ValidationIssue("error", message, file_path, line_number))
        self.is_valid = False

    def add_warning(self, message: str, file_path: Path | None = None, line_number: int | None = None) -> None:
        """Add a warning to the report."""
        self.issues.append(ValidationIssue("warning", message, file_path, line_number))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "is_valid": self.is_valid,
            "issues": [
                {
                    "severity": i.severity,
                    "message": i.message,
                    "file_path": str(i.file_path) if i.file_path else None,
                    "line_number": i.line_number,
                }
                for i in self.issues
            ],
        }
