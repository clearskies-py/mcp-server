# ClearSkies v1 to v2 Migration Assistant

This module provides comprehensive tools and automations to migrate clearskies v1 projects to v2.

## Overview

The migration assistant includes:

1. **V1 Codebase Analyzer** - Scans and analyzes v1 projects
2 **Pattern Parsers** - Extracts v1 patterns (models, handlers, DI, columns)
3. **V1→V2 Mapper** - Maps v1 concepts to v2 equivalents
4. **V2 Code Generators** - Generates v2-compatible code
5. **Migration Validator** - Validates generated code
6. **MCP Tools** - Exposed as MCP server tools
7 **MCP Resources** - Educational documentation

## MCP Tools

### `analyze_v1_project(project_path: str)`

Analyzes a v1 codebase and generates a detailed report.

**Returns:**
- Discovered models, handlers, applications
- Errors and warnings
- Complexity assessment

**Example:**
```python
result = analyze_v1_project("/path/to/v1/project")
print(result["complexity"])  # {'complexity_level': 'moderate', 'estimated_migration_time_hours': 4}
```

### `generate_v2_migration(project_path: str, output_path: str, dry_run: bool = True)`

Generates v2 code from v1 project.

**Arguments:**
- `project_path`: Path to v1 project
- `output_path`: Where to write v2 code
- `dry_run`: If True, don't write files (preview only)

**Returns:**
- List of files to create/modify
- Breaking changes
- Manual steps required

**Example:**
```python
# Preview migration
result = generate_v2_migration(
    "/path/to/v1/project",
    "/path/to/v2/project",
    dry_run=True
)

# Apply migration
result = generate_v2_migration(
    "/path/to/v1/project",
    "/path/to/v2/project",
    dry_run=False
)
```

### `map_v1_to_v2(v1_code_snippet: str, context: str = "general")`

Converts a v1 code snippet to v2 equivalent.

**Arguments:**
- `v1_code_snippet`: V1 code to convert
- `context`: Hint about code type ('model', 'handler', 'di', 'general')

**Returns:**
- Converted v2 code
- Breaking changes
- Migration notes

**Example:**
```python
v1_code = """
from clearskies import Model
class User(Model):
    def columns_configuration(self):
        return OrderedDict([('name', {'class': String})])
"""

result = map_v1_to_v2(v1_code, context='model')
print(result["v2_code"])
```

### `explain_v1_v2_difference(concept: str)`

Explains how a specific concept changed between v1 and v2.

**Available concepts:**
- `model`: Model definition changes
- `handler`: Handler → Endpoint changes
- `di`: Dependency injection changes
- `columns`: Column definition changes
- `application`: Application → Context changes
- `backend`: Backend configuration changes
- `type_hints`: Type hint requirements

**Example:**
```python
explanation = explain_v1_v2_difference('model')
print(explanation)  # Detailed explanation with examples
```

### `get_migration_checklist()`

Returns a comprehensive migration checklist with all phases and tasks.

**Returns:**
Dictionary with phases: preparation, analysis, model_migration, endpoint_migration, context_setup, di_migration, testing, polish, deployment

## MCP Resources

### `clearskies://migration/guide`

Complete migration guide with step-by-step instructions.

### `clearskies://migration/breaking-changes`

Comprehensive list of all breaking changes with impact assessment.

### `clearskies://migration/patterns`

Common v1 patterns and their v2 equivalents with complete examples.

## Module Structure

```
migration/
├── __init__.py               # Public API
├── models.py                 # Data models for migration (+ InitParam, DIUsage, AuthConfig, MixinConfig)
├── mapper.py                 # V1 → V2 mapping database
├── parsers.py                # Pattern parsers (Model, Handler, DI, Column, Config, Context)
├── analyzer.py               # Codebase analyzer
├── generators.py             # V2 code generators (with Mixin, Config, DI, Auth)
├── validator.py              # Migration validator
├── type_hint_generator.py    # NEW: Type hint generation
├── mixin_detector.py         # NEW: Mixin detection and generation
├── import_organizer.py       # NEW: Import rewriting and organization
├── auth_migrator.py          # NEW: Authentication migration
└── README.md                 # This file
```

## Usage Example

### As Python Module

```python
from clearskies_mcp_server.migration import (
    V1CodebaseAnalyzer,
    V2CodeGenerator,
    V1ToV2Mapper,
)

# Analyze v1 project
analyzer = V1CodebaseAnalyzer("/path/to/v1/project")
report = analyzer.analyze()

print(f"Found {len(report.models)} models")
print(f"Found {len(report.handlers)} handlers")

# Generate v2 code
generator = V2CodeGenerator()
plan = generator.generate_all(report)

# Review plan
for file in plan.files:
    print(f"{file.operation}: {file.path}")

# Apply migration
plan.apply(Path("/path/to/v2/project"), dry_run=False)
```

### Via MCP Tools

```python
# Through MCP server
import mcp_client

# Analyze
result = mcp_client.call_tool("analyze_v1_project", {
    "project_path": "/path/to/v1/project"
})

# Generate migration
migration = mcp_client.call_tool("generate_v2_migration", {
    "project_path": "/path/to/v1/project",
    "output_path": "/path/to/v2/project",
    "dry_run": True
})
```

## Key Features

### Comprehensive Analysis
- Discovers all models, handlers, and applications
- Identifies custom hooks and methods
- Detects relationships between models
- **Analyzes mixin requirements** (Configurable, InjectableProperties, Loggable)
- **Detects DI usage patterns** (constructor injection, property injection)
- **Identifies configuration parameters**
- Assesses migration complexity

### Intelligent Code Generation
- Converts `columns_configuration()` to class attributes
- **Generates Python 3.13+ type hints** automatically
- **Applies mixins** with proper inheritance ordering
- **Creates configs.* attributes** from `__init__` parameters
- **Generates property-based DI** from constructor DI
- **Organizes imports** (PEP 8, deduplicated, categorized)
- **Generates authentication configurations** (SecretBearer, JWKS, etc.)
- Updates import statements (handlers → endpoints, etc.)
- Generates v2 endpoint configurations
- Creates context wrappers with smart type detection
- Preserves custom logic with typed TODOs

### Validation
- Syntax checking
- Import validation
- Structure validation
- Completeness checking
- Best practices compliance
- Mixin compatibility checking
- Type hint validation

### Educational Resources
- Complete migration guide
- Breaking changes documentation
- Pattern examples with before/after code
- Interactive explanations
- Coverage metrics and progress tracking

## Migration Process

1. **Preparation**
   - Backup v1 codebase
   - Create migration branch
   - Set up v2 environment

2. **Analysis**
   ```python
   report = analyze_v1_project("/path/to/v1/project")
   ```

3. **Generation**
   ```python
   migration = generate_v2_migration(
       "/path/to/v1/project",
       "/path/to/v2/project",
       dry_run=True  # Preview first!
   )
   ```

4. **Review**
   - Check generated code
   - Review breaking changes
   - Note manual steps

5. **Apply**
   ```python
   # When ready
   migration = generate_v2_migration(
       "/path/to/v1/project",
       "/path/to/v2/project",
       dry_run=False  # Actually migrate
   )
   ```

6. **Manual Adjustments**
   - Complete TODO items
   - Add type hints
   - Configure readable/writeable columns
   - Test thoroughly

## Breaking Changes Handled

The migration assistant handles these breaking changes automatically:

### Fully Automated ✅
- ✅ `columns_configuration()` → class attributes
- ✅ `column_types` → `columns` imports
- ✅ `UUID` → `Uuid`, `JSON` → `Json`
- ✅ `handlers` → `endpoints` imports
- ✅ `RestfulAPI` → `RestfulApi`
- ✅ `handler_config` dict → kwargs
- ✅ **Type hints** - Automatically generated (Python 3.13+)
- ✅ **Mixins** - Auto-detected (Configurable, InjectableProperties, Loggable)
- ✅ **Configuration** - `__init__` params → `configs.*` attributes with `@parameters_to_properties`
- ✅ **DI Property Injection** - Constructor DI → property-based injection
- ✅ **Import Organization** - Full rewriting, cleanup, PEP 8 compliance
- ✅ **Authentication** - SecretBearer, JWKS, JWT, OAuth2 generation

### Partially Automated ⚠️
- ⚠️ `Application` → context wrapper (smart inference, review recommended)
- ⚠️ Complex DI patterns (advanced patterns may need adjustment)

## New Features (v2024.2)

The migration tool now provides **modern Python pattern generation**:

### Type Hint Generation
Automatically adds Python 3.13+ type hints to:
- Method parameters
- Return types
- Hook methods
- Type_CHECKING blocks for circular imports

### Mixin Detection & Generation
Automatically detects and applies:
- `Configurable` mixin (for classes with configuration)
- `InjectableProperties` mixin (for DI usage)
- `Loggable` mixin (for logging)

With proper inheritance ordering and required imports.

### Configuration Management
Converts v1 constructor parameters to v2 declarative configuration:
- `__init__` parameters → `configs.*` attributes
- Infers config types (String, Integer, Boolean, Dict, List)
- Generates `@parameters_to_properties` decorated `__init__`

### Enhanced DI
Transforms constructor-based DI to property-based injection:
- Detects `self.di.build()` patterns
- Generates `inject.ByClass()`, `inject.ByName()` properties
- Built-in  helpers: `inject.Utcnow()`, `inject.Environment()`, `inject.Requests()`, etc.

### Import Management
- Module path rewriting (handlers → endpoints)
- PEP 8 organization (stdlib, third-party, local)
- Duplicate merging
- Unused import cleanup

### Authentication Migration
Generates full authentication configurations:
- SecretBearer, SecretBasic, JWKS, JWT, OAuth2, Public
- Environment key configuration
- Decorator-based auth detection

## Limitations

- Custom business logic requires manual review
- Some advanced DI patterns may need adjustment
- Readable/writeable column lists should be reviewed
- Third-party extensions may not have v2 equivalents
- Query patterns (get_final_query, Condition) not yet automated (P3)

## Testing

The migration system includes comprehensive tests:

```bash
pytest tests/test_migration.py -v
```

## Contributing

To add new migration patterns:

1. Update [`mapper.py`](mapper.py:1) with new mappings
2. Enhance parsers in [`parsers.py`](parsers.py:1)
3. Update generators in [`generators.py`](generators.py:1)
4. Add tests
5. Update documentation

## Support

For migration assistance:
- Use `explain_v1_v2_difference(concept)` for specific topics
- Consult `clearskies://migration/guide` resource
- Review `clearskies://migration/patterns` for examples
- Check the migration checklist with `get_migration_checklist()`

## Future Enhancements

- Automated test generation
- Performance comparison
- Gradual migration support
- Rollback mechanisms
- IDE integration
- Community pattern sharing
