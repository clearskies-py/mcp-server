"""
MCP tools for v1 to v2 migration.

These tools expose migration functionality through the MCP server.
"""

from pathlib import Path
from typing import Any

from ..migration import V1CodebaseAnalyzer, V1ToV2Mapper, V2CodeGenerator


def analyze_v1_project(project_path: str) -> dict[str, Any]:
    """
    Analyze a ClearSkies v1 project and generate migration report.

    Args:
        project_path: Path to the v1 project directory

    Returns:
        Dictionary containing:
        - models: List of discovered models
        - handlers: List of discovered handlers
        - errors: List of parsing errors
        - warnings: List of migration warnings
        - complexity: Migration complexity assessment
    """
    analyzer = V1CodebaseAnalyzer(project_path)
    report = analyzer.analyze()
    complexity = analyzer.get_migration_complexity(report)

    result = report.to_dict()
    result["complexity"] = complexity

    return result


def generate_v2_migration(
    project_path: str,
    output_path: str,
    dry_run: bool = True,
) -> dict[str, Any]:
    """
    Generate v2 code from a v1 project.

    This tool analyzes a v1 codebase and generates v2-compatible code.
    Use dry_run=True to preview changes without writing files.

    Args:
        project_path: Path to the v1 project directory
        output_path: Path where v2 code should be generated
        dry_run: If True, don't write files (default: True)

    Returns:
        Dictionary containing:
        - files: List of files to create/modify
        - breaking_changes: List of breaking changes
        - warnings: List of warnings
        - manual_steps: List of manual steps required
    """
    # Analyze v1 project
    analyzer = V1CodebaseAnalyzer(project_path)
    report = analyzer.analyze()

    # Generate v2 code
    generator = V2CodeGenerator()
    plan = generator.generate_all(report, Path(output_path))

    # Apply if not dry run
    if not dry_run:
        plan.apply(Path(output_path), dry_run=False)

    return plan.to_dict()


def map_v1_to_v2(v1_code_snippet: str, context: str = "general") -> dict[str, Any]:
    """
    Map a v1 code snippet to its v2 equivalent.

    Useful for understanding how specific v1 patterns translate to v2.

    Args:
        v1_code_snippet: The v1 code to convert
        context: Context hint ('model', 'handler', 'di', 'general')

    Returns:
        Dictionary containing:
        - v2_code: Converted v2 code
        - breaking_changes: List of breaking changes
        - notes: Migration notes
    """
    mapper = V1ToV2Mapper()
    result = mapper.map_snippet(v1_code_snippet, context)

    return {
        "v2_code": result.example_v2 or result.v2_class or "(unable to convert)",
        "breaking_changes": result.breaking_changes,
        "notes": result.migration_notes,
    }


def explain_v1_v2_difference(concept: str) -> str:
    """
    Explain how a specific concept changed between v1 and v2.

    Args:
        concept: The concept to explain. Options:
            - 'model': Model definition changes
            - 'handler': Handler → Endpoint changes
            - 'di': Dependency injection changes
            - 'columns': Column definition changes
            - 'application': Application → Context changes
            - 'backend': Backend configuration changes
            - 'type_hints': Type hint requirements

    Returns:
        Detailed explanation of the changes
    """
    from ..migration.mapper import PATTERN_EXAMPLES

    explanations = {
        "model": """# Model Definition Changes (v1 → v2)

**v1 Pattern:**
- Models use `columns_configuration()` method
- Columns defined in OrderedDict
- Import from `clearskies.column_types`

**v2 Pattern:**
- Columns are class attributes
- Direct instantiation with `columns.Type()`
- Backend specified as class attribute
- Import from `clearskies.columns`

**Example:**

v1:
```python
from clearskies import Model
from collections import OrderedDict

class User(Model):
    def columns_configuration(self):
        return OrderedDict([
            ('id', {'class': clearskies.column_types.UUID}),
            ('name', {'class': clearskies.column_types.String}),
        ])
```

v2:
```python
import clearskies
from clearskies import columns

class User(clearskies.Model):
    backend = clearskies.backends.MemoryBackend()

    id = columns.Uuid()
    name = columns.String()
```

**Breaking Changes:**
- `columns_configuration()` method removed
- Must specify backend on model
- Column type names changed (UUID → Uuid)
""",
        "handler": """# Handler → Endpoint Changes (v1 → v2)

**v1 Pattern:**
- Import from `clearskies.handlers`
- Class name: `RestfulAPI` (uppercase API)
- Configuration via `handler_config` dict
- Wrapped in `Application` class

**v2 Pattern:**
- Import from `clearskies.endpoints`
- Class name: `RestfulApi` (lowercase i)
- Configuration via kwargs
- Wrapped in context (WsgiRef, Cli, etc.)
- Explicit column configuration required

**Example:**

v1:
```python
from clearskies import Application
from clearskies.handlers import RestfulAPI

app = Application(
    handler_class=RestfulAPI,
    handler_config={'model_class': User, 'base_url': 'users'},
)
```

v2:
```python
import clearskies

endpoint = clearskies.endpoints.RestfulApi(
    url="users",
    model_class=User,
    readable_column_names=["id", "name", "email"],
    writeable_column_names=["name", "email"],
)

wsgi = clearskies.contexts.WsgiRef(endpoint)
```

**Breaking Changes:**
- `handlers` → `endpoints` (renamed package)
- `RestfulAPI` → `RestfulApi` (lowercase 'i')
- `handler_config` dict → kwargs
- Must specify readable/writeable columns explicitly
""",
        "di": """# Dependency Injection Changes (v1 → v2)

**v1 Pattern:**
- Constructor-based injection
- Manual DI container management
- `self._di.build(ClassName)`

**v2 Pattern:**
- Property-based injection
- Declarative with `inject.*` helpers
- Models inherit from `InjectableProperties`
- Automatic resolution

**Example:**

v1:
```python
class MyHandler:
    def __init__(self, di):
        self._di = di

    def handle(self, input_output):
        service = self._di.build(MyService)
        service.do_something()
```

v2:
```python
from clearskies.di import inject

class MyModel(clearskies.Model):
    my_service = inject.ByClass(MyService)
    utcnow = inject.Utcnow()

    def do_something(self):
        self.my_service.do_something()
```

**Breaking Changes:**
- No more constructor injection
- Use property decorators instead
- New helpers: `inject.ByClass()`, `inject.Utcnow()`, `inject.Environment()`
""",
        "columns": """# Column Definition Changes (v1 → v2)

**Key Changes:**
- Import changed: `column_types` → `columns`
- Type name changes: `UUID` → `Uuid`, `JSON` → `Json`
- Definition style: OrderedDict → class attributes
- Must instantiate with `()`

**Type Name Mappings:**
- UUID → Uuid
- JSON → Json
- All others remain similar (String, Integer, Email, etc.)

**Breaking Changes:**
- Old OrderedDict style no longer supported
- Column instances required (must call with parentheses)
- Some type names changed casing
""",
        "application": """# Application → Context Changes (v1 → v2)

**v1 Pattern:**
- Single `Application` class for all contexts
- Implicit context detection

**v2 Pattern:**
- Explicit context selection
- Different contexts: `WsgiRef`, `Cli`, `Lambda`, etc.
- DI configuration moved to context

**Example:**

v1:
```python
app = Application(
    handler_class=RestfulAPI,
    handler_config={...},
    bindings={'db': connection},
)
```

v2:
```python
wsgi = clearskies.contexts.WsgiRef(
    endpoint,
    bindings={"database": connection},
    classes=[MyService],
)
```

**Breaking Changes:**
- `Application` class removed
- Must choose explicit context
- `binding_classes`/`binding_modules` → `classes=`/`modules=`
""",
        "backend": """# Backend Configuration Changes (v1 → v2)

**v1 Pattern:**
- Backend passed to models constructor
- Created separately and passed around

**v2 Pattern:**
- Backend as class attribute on model
- Specified directly in model definition

**Example:**

v1:
```python
backend = clearskies.backends.MemoryBackend()
models = Models(backend, columns)
```

v2:
```python
class User(clearskies.Model):
    backend = clearskies.backends.MemoryBackend()
    # ... columns ...
```

**Breaking Changes:**
- Backend must be class attribute
- Specified on each model class
""",
        "type_hints": """# Type Hints (v1 → v2)

**v1:** Type hints were optional

**v2:** Type hints are required (Python 3.13+)

**Best Practices:**
- Use `TYPE_CHECKING` for circular imports
- Annotate all method signatures
- Include return types

**Example:**
```python
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from clearskies.input_outputs.input_output import InputOutput

def handle(self, input_output: InputOutput) -> dict[str, Any]:
    return {"status": "ok"}
```
""",
    }

    explanation = explanations.get(concept)
    if not explanation:
        # Return list of available concepts
        return f"""Unknown concept: '{concept}'

Available concepts:
- model: Model definition changes
- handler: Handler → Endpoint changes
- di: Dependency injection changes
- columns: Column definition changes
- application: Application → Context changes
- backend: Backend configuration changes
- type_hints: Type hint requirements

Use explain_v1_v2_difference with one of these concepts."""

    # Add pattern examples if available
    if concept in PATTERN_EXAMPLES:
        example = PATTERN_EXAMPLES[concept]
        explanation += (
            f"\n\n**Complete Example:**\n\nv1:\n```python\n{example['v1']}\n```\n\nv2:\n```python\n{example['v2']}\n```"
        )

    return explanation


def get_migration_checklist() -> dict[str, list[str]]:
    """
    Get a comprehensive checklist for v1 to v2 migration.

    Returns:
        Dictionary with migration phases and tasks
    """
    return {
        "preparation": [
            "Backup your v1 codebase",
            "Create a new branch for v2 migration",
            "Review v1 to v2 breaking changes documentation",
            "Set up v2 Python environment (Python 3.13+)",
            "Install clearskies v2 package",
        ],
        "analysis": [
            "Run analyze_v1_project on your codebase",
            "Review discovered models and handlers",
            "Note any custom business logic",
            "Identify third-party dependencies",
            "Assess migration complexity",
        ],
        "model_migration": [
            "Convert columns_configuration() to class attributes",
            "Update column type imports (column_types → columns)",
            "Fix column type names (UUID → Uuid, JSON → Json)",
            "Add backend attribute to each model",
            "Migrate model hooks if present",
            "Add type hints to all methods",
        ],
        "endpoint_migration": [
            "Rename handlers → endpoints",
            "Update RestfulAPI → RestfulApi",
            "Convert handler_config dict to kwargs",
            "Add readable_column_names configuration",
            "Add writeable_column_names configuration",
            "Configure sortable and searchable columns",
        ],
        "context_setup": [
            "Replace Application with appropriate context",
            "Choose context: WsgiRef, Cli, Lambda, etc.",
            "Update DI bindings configuration",
            "Convert binding_classes/binding_modules to classes=/modules=",
        ],
        "di_migration": [
            "Convert constructor injection to property injection",
            "Add inject.ByClass() for service dependencies",
            "Use inject.Utcnow() for datetime",
            "Use inject.Environment() for env variables",
            "Ensure models inherit from InjectableProperties",
        ],
        "testing": [
            "Run generated code through linter",
            "Fix any syntax errors",
            "Run unit tests",
            "Test all endpoints",
            "Verify database operations",
            "Check authentication flows",
        ],
        "polish": [
            "Add docstrings to all classes and methods",
            "Ensure consistent type hints",
            "Review and update comments",
            "Format code with black/ruff",
            "Update README and documentation",
        ],
        "deployment": [
            "Test in staging environment",
            "Update deployment scripts",
            "Update CI/CD pipelines",
            "Monitor for runtime errors",
            "Have rollback plan ready",
        ],
    }
