"""
MCP resources for v1 to v2 migration.

Educational resources about migrating from clearskies v1 to v2.
"""


def migration_guide() -> str:
    """Complete migration guide."""
    return """# ClearSkies v1 to v2 Migration Guide

## Overview

This guide will help you migrate your clearskies v1 applications to v2. The migration involves several key changes to how models, handlers (now endpoints), and applications are structured.

## Quick Start

1. **Analyze your v1 codebase:**
   ```python
   # Use the MCP tool
   analyze_v1_project(project_path="/path/to/v1/project")
   ```

2. **Generate v2 code:**
   ```python
   # Use the MCP tool
   generate_v2_migration(
       project_path="/path/to/v1/project",
       output_path="/path/to/v2/project",
       dry_run=True  # Preview first!
   )
   ```

3. **Review and adjust** the generated code

4. **Test thoroughly** before deploying

## Major Changes

### 1. Model Definitions

**v1:** OrderedDict with `columns_configuration()` method
**v2:** Class attributes with `columns` module

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

    id = columns.Uuid()  # Note: lowercase 'u'
    name = columns.String()
```

**Key Changes:**
- Remove `columns_configuration()` method
- Define columns as class attributes
- Import from `clearskies.columns`
- Add `backend` class attribute
- Column type name changes: `UUID` → `Uuid`, `JSON` → `Json`

### 2. Handlers → Endpoints

**v1:** `handlers` package
**v2:** `endpoints` package

v1:
```python
from clearskies import Application
from clearskies.handlers import RestfulAPI

app = Application(
    handler_class=RestfulAPI,
    handler_config={
        'model_class': User,
        'base_url': 'users',
    },
)
```

v2:
```python
import clearskies

endpoint = clearskies.endpoints.RestfulApi(  # lowercase 'i'
    url="users",
    model_class=User,
    readable_column_names=["id", "name", "email"],
    writeable_column_names=["name", "email"],
)
```

**Key Changes:**
- `handlers` → `endpoints` (package renamed)
- `RestfulAPI` → `RestfulApi` (lowercase 'i')
- `handler_config` dict → direct kwargs
- Explicit `readable_column_names` and `writeable_column_names` required

### 3. Application → Context

**v1:** Single `Application` class
**v2:** Explicit context wrappers

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

**Available Contexts:**
- `WsgiRef` - Development WSGI server
- `Wsgi` - Production WSGI
- `Cli` - Command-line applications
- `Lambda` - AWS Lambda
- And more...

**Key Changes:**
- Choose explicit context type
- `binding_classes` → `classes=`
- `binding_modules` → `modules=`

### 4. Dependency Injection

**v1:** Constructor injection
**v2:** Property injection

v1:
```python
class MyHandler:
    def __init__(self, di):
        self._di = di

    def handle(self, input_output):
        service = self._di.build(MyService)
```

v2:
```python
from clearskies.di import inject

class MyModel(clearskies.Model):
    my_service = inject.ByClass(MyService)
    utcnow = inject.Utcnow()

    def my_method(self):
        self.my_service.do_something()
```

**Key Changes:**
- Use `inject.*` helpers
- Property-based instead of constructor-based
- Models inherit from `InjectableProperties`

### 5. Type Hints

v2 requires Python 3.13+ and comprehensive type hints:

```python
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from clearskies.input_outputs.input_output import InputOutput

def handle(self, input_output: InputOutput) -> dict[str, Any]:
    return {"status": "ok"}
```

## Migration Checklist

Use `get_migration_checklist()` tool for complete checklist.

## Common Pitfalls

1. **Forgetting to add backend attribute** to models
2. **Using old column type names** (UUID vs Uuid)
3. **Missing readable/writeable column configuration** on endpoints
4. **Not updating import statements** (column_types vs columns)
5. **Forgetting type hints** on method signatures

## Getting Help

- Use `explain_v1_v2_difference(concept)` for specific topics
- Use `map_v1_to_v2(code_snippet)` to convert code snippets
- Review the pattern examples in the migration resources

## Next Steps

1. Start with a small pilot project or module
2. Migrate models first, then endpoints
3. Set up the context wrapper
4. Update DI patterns
5. Add comprehensive type hints
6. Test thoroughly
7. Deploy incrementally

Good luck with your migration!
"""


def breaking_changes() -> str:
    """Complete list of breaking changes."""
    return """# ClearSkies v1 to v2 Breaking Changes

## Model Definitions

### ❌ Removed: `columns_configuration()` method
**Impact:** HIGH
**Migration:** Convert OrderedDict to class attributes

**v1:**
```python
def columns_configuration(self):
    return OrderedDict([('name', {'class': String})])
```

**v2:**
```python
name = columns.String()
```

### ❌ Removed: Implicit backend
**Impact:** HIGH
**Migration:** Add `backend` class attribute

**v2:**
```python
class User(clearskies.Model):
    backend = clearskies.backends.MemoryBackend()
```

### ⚠️ Changed: Column type names
**Impact:** MEDIUM
**Migration:** Update casing

- `UUID` → `Uuid`
- `JSON` → `Json`

### ⚠️ Changed: Column imports
**Impact:** HIGH
**Migration:** Update import path

- `from clearskies import column_types` → `from clearskies import columns`

## Handlers → Endpoints

### ❌ Renamed: `handlers` package
**Impact:** HIGH
**Migration:** Update all imports

**v1:** `from clearskies.handlers import ...`
**v2:** `from clearskies.endpoints import ...`

### ⚠️ Renamed: `RestfulAPI`
**Impact:** HIGH
**Migration:** Change class name

**v1:** `RestfulAPI`
**v2:** `RestfulApi` (lowercase 'i')

### ❌ Removed: `handler_config` dict
**Impact:** HIGH
**Migration:** Convert to kwargs

**v1:**
```python
handler_config={'model_class': User, 'base_url': 'users'}
```

**v2:**
```python
model_class=User, url="users"
```

### ✅ Required: Explicit column configuration
**Impact:** HIGH
**Migration:** Add readable/writeable column lists

**v2:**
```python
readable_column_names=["id", "name"],
writeable_column_names=["name"],
```

## Application → Context

### ❌ Removed: `Application` class
**Impact:** HIGH
**Migration:** Use explicit context

**v1:** `Application(...)`
**v2:** `clearskies.contexts.WsgiRef(...)` (or Cli, Lambda, etc.)

### ⚠️ Renamed: DI Configuration
**Impact:** MEDIUM
**Migration:** Update parameter names

- `binding_classes` → `classes=`
- `binding_modules` → `modules=`

## Dependency Injection

### ❌ Removed: Constructor-based DI
**Impact:** HIGH
**Migration:** Use property injection

**v1:**
```python
def __init__(self, di):
    self._di = di
```

**v2:**
```python
my_service = inject.ByClass(MyService)
```

### ✅ Added: `inject.*` helpers
**Impact:** MEDIUM
**Migration:** Use new helpers

New helpers:
- `inject.ByClass(ClassName)`
- `inject.Utcnow()`
- `inject.Environment(key)`
- `inject.Requests()`

## Type Hints

### ✅ Required: Comprehensive type hints
**Impact:** HIGH
**Migration:** Add type annotations to all methods

**v2:**
```python
def my_method(self, param: str) -> dict[str, Any]:
    ...
```

### ✅ Required: Python 3.13+
**Impact:** HIGH
**Migration:** Upgrade Python version

## Backend Configuration

### ⚠️ Changed: Backend specification
**Impact:** MEDIUM
**Migration:** Move backend to model class

**v1:** Backend passed to constructor
**v2:** Backend as class attribute

## Import Organization

### ⚠️ Changed: Import style
**Impact:** MEDIUM
**Migration:** Use consistent imports

**v2 Best Practice:**
```python
import clearskies
from clearskies import columns
from clearskies.di import inject
```

## Configuration Patterns

### ⚠️ Changed: Base classes and mixins
**Impact:** MEDIUM
**Migration:** Use new mixins

New mixins in v2:
- `Configurable` - For declarative configuration
- `InjectableProperties` - For DI support
- `Loggable` - For automatic logging
- `@parameters_to_properties` decorator

## Query Patterns

### ⚠️ Changed: Query customization
**Impact:** LOW
**Migration:** Use `get_final_query()`

**v2:**
```python
def get_final_query(self) -> Query:
    return self.get_query().add_where(Condition("status='active'"))
```

## Summary

**Total Breaking Changes:** 15+
**High Impact:** 11
**Medium Impact:** 4

**Recommendation:** Plan for significant refactoring time. Start with a pilot project to understand the migration process before tackling larger codebases.

**Estimated Migration Time:**
- Small project (1-5 models): 2-4 hours
- Medium project (5-20 models): 1-2 days
- Large project (20+ models): 3-5 days
"""


def migration_patterns() -> str:
    """Get common v1 patterns and v2 equivalents."""
    return """# ClearSkies v1 to v2 Pattern Mappings

## Complete Pattern Examples

### 1. Simple Model

**v1:**
```python
from clearskies import Model
from collections import OrderedDict
import clearskies.column_types as ct

class User(Model):
    id_column_name = "id"

    def columns_configuration(self):
        return OrderedDict([
            ('id', {'class': ct.UUID}),
            ('name', {'class': ct.String}),
            ('email', {'class': ct.Email}),
            ('created', {'class': ct.Created}),
        ])
```

**v2:**
```python
import clearskies
from clearskies import columns

class User(clearskies.Model):
    id_column_name = "id"
    backend = clearskies.backends.MemoryBackend()

    id = columns.Uuid()
    name = columns.String()
    email = columns.Email()
    created = columns.Created()
```

### 2. Model with Relationships

**v1:**
```python
def columns_configuration(self):
    return OrderedDict([
        ('id', {'class': ct.UUID}),
        ('user_id', {'class': ct.BelongsTo, 'parent_class': User}),
        ('posts', {'class': ct.HasMany, 'child_class': Post}),
    ])
```

**v2:**
```python
id = columns.Uuid()
user_id = columns.BelongsTo(parent_class=User)
posts = columns.HasMany(child_class=Post)
```

### 3. Model with Hooks

**v1:**
```python
class User(Model):
    def columns_configuration(self):
        return OrderedDict([...])

    def pre_save(self, data, id=None):
        data['name'] = data['name'].strip()
        return data

    def post_save(self, data, id):
        # Send notification
        pass
```

**v2:**
```python
class User(clearskies.Model):
    # ... columns ...

    def pre_save(self, **kwargs) -> dict[str, Any]:
        data = kwargs.get('data', {})
        data['name'] = data['name'].strip()
        return data

    def post_save(self, **kwargs) -> None:
        # Send notification
        pass
```

### 4. RestfulAPI Handler

**v1:**
```python
from clearskies import Application
from clearskies.handlers import RestfulAPI

app = Application(
    handler_class=RestfulAPI,
    handler_config={
        'model_class': User,
        'base_url': 'users',
        'readable_columns': ['id', 'name', 'email'],
        'writeable_columns': ['name', 'email'],
    },
    bindings={'database': db_connection},
)
```

**v2:**
```python
import clearskies

endpoint = clearskies.endpoints.RestfulApi(
    url="users",
    model_class=User,
    readable_column_names=["id", "name", "email"],
    writeable_column_names=["name", "email"],
    sortable_column_names=["name", "created_at"],
    searchable_column_names=["name", "email"],
)

wsgi = clearskies.contexts.WsgiRef(
    endpoint,
    bindings={"database": db_connection},
)
```

### 5. Custom Handler/Endpoint

**v1:**
```python
from clearskies.handlers import Callable

class MyHandler:
    def __init__(self, di):
        self._di = di

    def handle(self, input_output):
        user = self._di.build(User)
        return {'users': user.all()}

app = Application(
    handler_class=Callable,
    handler_config={'callable': MyHandler},
)
```

**v2:**
```python
from typing import TYPE_CHECKING, Any
from clearskies.di import inject

if TYPE_CHECKING:
    from clearskies.input_outputs.input_output import InputOutput

class MyCallable:
    users = inject.ByClass(User)

    def __call__(self, input_output: InputOutput) -> dict[str, Any]:
        return {"users": self.users.all()}

endpoint = clearskies.endpoints.Callable(
    callable=MyCallable,
)
```

### 6. Authentication

**v1:**
```python
from clearskies.authentication import SecretBearer

app = Application(
    handler_class=RestfulAPI,
    handler_config={
        'model_class': User,
        'authentication': SecretBearer(secret='my-secret'),
    },
)
```

**v2:**
```python
endpoint = clearskies.endpoints.RestfulApi(
    model_class=User,
    authentication=clearskies.authentication.SecretBearer(
        environment_key="API_SECRET"
    ),
)
```

### 7. CLI Application

**v1:**
```python
from clearskies import Application
from clearskies.handlers import Callable

app = Application(
    handler_class=Callable,
    handler_config={'callable': my_function},
    environment='cli',
)
```

**v2:**
```python
cli = clearskies.contexts.Cli(
    clearskies.endpoints.Callable(callable=my_function),
)
```

### 8. Dependency Injection

**v1:**
```python
class MyService:
    def __init__(self, di):
        self._di = di

    def send_email(self, user_id):
        user = self._di.build(User, user_id)
        # ...

app = Application(
    handler_config={...},
    bindings={'email_service': MyEmailService()},
    binding_classes=[MyService],
)
```

**v2:**
```python
from clearskies.di import inject

class MyService(clearskies.di.InjectableProperties):
    users = inject.ByClass(User)
    email_service = inject.ByClass(MyEmailService)

    def send_email(self, user_id: str) -> None:
        user = self.users.find(user_id)
        # ...

wsgi = clearskies.contexts.WsgiRef(
    endpoint,
    bindings={"email_service": MyEmailService()},
    classes=[MyService],
)
```

### 9. Multiple Endpoints (Routing)

**v1:**
```python
from clearskies.handlers import SimpleRouting

app = Application(
    handler_class=SimpleRouting,
    handler_config={
        'routes': [
            {'path': '/users', 'handler': RestfulAPI, 'handler_config': {...}},
            {'path': '/posts', 'handler': RestfulAPI, 'handler_config': {...}},
        ],
    },
)
```

**v2:**
```python
routing = clearskies.endpoints.SimpleRouting(
    routes=[
        {"path": "/users", "endpoint": users_endpoint},
        {"path": "/posts", "endpoint": posts_endpoint},
    ],
)

# Or use EndpointGroup
from clearskies.endpoints import EndpointGroup

group = EndpointGroup(
    url="/api",
    endpoints=[
        clearskies.endpoints.RestfulApi(url="users", model_class=User),
        clearskies.endpoints.RestfulApi(url="posts", model_class=Post),
    ],
)
```

### 10. Custom Validation

**v1:**
```python
def columns_configuration(self):
    return OrderedDict([
        ('email', {
            'class': ct.Email,
            'required': True,
            'is_unique': True,
        }),
    ])
```

**v2:**
```python
from clearskies.validators import Required, Unique

email = columns.Email(
    validators=[Required(), Unique()],
)
```

## Quick Reference

| v1 Concept | v2 Equivalent |
|------------|---------------|
| `clearskies.handlers` | `clearskies.endpoints` |
| `clearskies.column_types` | `clearskies.columns` |
| `Application` | `contexts.WsgiRef` / `contexts.Cli` |
| `RestfulAPI` | `RestfulApi` |
| `handler_class` | Direct endpoint instantiation |
| `handler_config` | Endpoint kwargs |
| `binding_classes` | `classes=` |
| `binding_modules` | `modules=` |
| `UUID` | `Uuid` |
| `JSON` | `Json` |
| Constructor DI | Property DI with `inject.*` |
| `columns_configuration()` | Class attributes |

## Next Steps

1. Use `map_v1_to_v2()` to convert your specific code
2. Use `generate_v2_migration()` to auto-generate v2 code
3. Test incrementally
4. Review the complete migration guide
"""
