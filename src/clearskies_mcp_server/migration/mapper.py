"""
Mapping database for v1 to v2 migrations.

This module contains comprehensive mappings of v1 concepts to their v2 equivalents.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import MappingResult


class V1ToV2Mapper:
    """Maps v1 clearskies concepts to v2 equivalents."""

    # Class name mappings
    CLASS_MAPPINGS = {
        # Handlers → Endpoints
        "clearskies.handlers.RestfulAPI": "clearskies.endpoints.RestfulApi",
        "clearskies.handlers.SimpleRouting": "clearskies.endpoints.SimpleRouting",
        "clearskies.handlers.Callable": "clearskies.endpoints.Callable",
        # Application → Contexts
        "clearskies.Application": "clearskies.contexts.Wsgi",
        # Column types
        "clearskies.column_types.UUID": "clearskies.columns.Uuid",
        "clearskies.column_types.String": "clearskies.columns.String",
        "clearskies.column_types.Integer": "clearskies.columns.Integer",
        "clearskies.column_types.Float": "clearskies.columns.Float",
        "clearskies.column_types.Boolean": "clearskies.columns.Boolean",
        "clearskies.column_types.DateTime": "clearskies.columns.DateTime",
        "clearskies.column_types.Created": "clearskies.columns.Created",
        "clearskies.column_types.Updated": "clearskies.columns.Updated",
        "clearskies.column_types.Email": "clearskies.columns.Email",
        "clearskies.column_types.JSON": "clearskies.columns.Json",
        "clearskies.column_types.BelongsTo": "clearskies.columns.BelongsTo",
        "clearskies.column_types.HasMany": "clearskies.columns.HasMany",
        "clearskies.column_types.ManyToMany": "clearskies.columns.ManyToMany",
    }

    # Import path mappings
    IMPORT_MAPPINGS = {
        "from clearskies.handlers import": "from clearskies.endpoints import",
        "from clearskies import Application": "from clearskies.contexts import Wsgi",
        "from clearskies import column_types": "from clearskies import columns",
        "clearskies.column_types": "clearskies.columns",
    }

    # Configuration key mappings (handler_config → endpoint kwargs)
    CONFIG_MAPPINGS = {
        "model_class": "model_class",
        "base_url": "url",
        "readable_columns": "readable_column_names",
        "writeable_columns": "writeable_column_names",
        "searchable_columns": "searchable_column_names",
        "sortable_columns": "sortable_column_names",
        "default_sort_column": "default_sort_column_name",
    }

    # Backend mappings
    BACKEND_MAPPINGS = {
        "clearskies.backends.MemoryBackend": "clearskies.backends.MemoryBackend",
        "clearskies.backends.CursorBackend": "clearskies.backends.CursorBackend",
        "clearskies.backends.ApiBackend": "clearskies.backends.ApiBackend",
    }

    # Breaking changes documentation
    BREAKING_CHANGES = {
        "columns_configuration": [
            "columns_configuration() method removed",
            "Columns must be defined as class attributes",
            "Import from clearskies.columns instead of clearskies.column_types",
            "Column classes must be instantiated with ()",
        ],
        "Application": [
            "Application class removed",
            "Use explicit context wrappers (WsgiRef, Cli, etc.)",
            "handler_config dict replaced with kwargs",
            "binding_classes/binding_modules replaced with classes=/modules=",
        ],
        "handlers": [
            "handlers renamed to endpoints",
            "RestfulAPI renamed to RestfulApi (lowercase 'i')",
            "handler_config dict replaced with kwargs",
            "More explicit configuration required (readable/writeable columns)",
        ],
        "di": [
            "Constructor-based DI replaced with property injection",
            "Use inject.ByClass() for dependencies",
            "Models inherit from InjectableProperties mixin",
            "Additional helpers: inject.Utcnow(), inject.Environment()",
        ],
        "backend": [
            "Backend passed to model constructor → backend as class attribute",
            "Backend must be specified on model class",
        ],
        "type_hints": [
            "Type hints required (Python 3.13+)",
            "Use TYPE_CHECKING for circular import avoidance",
            "All methods should have type annotations",
        ],
    }

    def map_class(self, v1_class: str) -> "MappingResult":
        """Map a v1 class to its v2 equivalent."""
        from .models import MappingResult

        v2_class = self.CLASS_MAPPINGS.get(v1_class)
        breaking_changes = []
        migration_notes = []

        if "handlers" in v1_class:
            breaking_changes.extend(self.BREAKING_CHANGES["handlers"])
            migration_notes.append("Update all handler references to use endpoints")
        elif "Application" in v1_class:
            breaking_changes.extend(self.BREAKING_CHANGES["Application"])
            migration_notes.append("Choose appropriate context: WsgiRef, Cli, Lambda, etc.")
        elif "column_types" in v1_class:
            breaking_changes.append("Import from clearskies.columns instead of column_types")
            breaking_changes.append("Note: UUID → Uuid (lowercase 'u'), JSON → Json")

        return MappingResult(
            v2_class=v2_class,
            breaking_changes=breaking_changes,
            migration_notes=migration_notes,
        )

    def map_import(self, v1_import: str) -> str:
        """Map a v1 import statement to v2 equivalent."""
        for v1_pattern, v2_pattern in self.IMPORT_MAPPINGS.items():
            if v1_pattern in v1_import:
                return v1_import.replace(v1_pattern, v2_pattern)
        return v1_import

    def map_config_key(self, v1_key: str) -> str:
        """Map a v1 config key to v2 equivalent."""
        return self.CONFIG_MAPPINGS.get(v1_key, v1_key)

    def map_column_type(self, v1_column: str) -> str:
        """Map a v1 column type to v2 equivalent."""
        # Handle short names
        if not v1_column.startswith("clearskies"):
            v1_column = f"clearskies.column_types.{v1_column}"

        v2_column = self.CLASS_MAPPINGS.get(v1_column)
        if v2_column:
            # Return just the class name
            return v2_column.split(".")[-1]
        return v1_column.split(".")[-1]

    def get_breaking_changes_for_concept(self, concept: str) -> list[str]:
        """Get breaking changes for a specific concept."""
        return self.BREAKING_CHANGES.get(concept, [])

    def map_snippet(self, v1_code: str, context: str) -> "MappingResult":
        """Map a v1 code snippet to v2 equivalent."""
        from .models import MappingResult

        v2_code = v1_code

        # Apply import mappings
        for v1_pattern, v2_pattern in self.IMPORT_MAPPINGS.items():
            v2_code = v2_code.replace(v1_pattern, v2_pattern)

        # Apply class name mappings
        for v1_class, v2_class in self.CLASS_MAPPINGS.items():
            # Replace fully qualified names
            v2_code = v2_code.replace(v1_class, v2_class)
            # Replace short names (e.g., RestfulAPI → RestfulApi)
            v1_short = v1_class.split(".")[-1]
            v2_short = v2_class.split(".")[-1]
            v2_code = v2_code.replace(v1_short, v2_short)

        breaking_changes = []
        notes = []

        if "columns_configuration" in v1_code:
            breaking_changes.extend(self.BREAKING_CHANGES["columns_configuration"])
            notes.append("Convert columns_configuration() to class attributes")
        if "Application(" in v1_code:
            breaking_changes.extend(self.BREAKING_CHANGES["Application"])
            notes.append("Convert Application to appropriate context wrapper")
        if "handler_class" in v1_code or "handler_config" in v1_code:
            breaking_changes.extend(self.BREAKING_CHANGES["handlers"])
            notes.append("Convert handler_config dict to endpoint kwargs")

        return MappingResult(
            v2_class=None,
            breaking_changes=breaking_changes,
            migration_notes=notes,
            example_v1=v1_code,
            example_v2=v2_code,
        )


# Pattern examples for common migrations
PATTERN_EXAMPLES = {
    "model_definition": {
        "v1": """from clearskies import Model
from collections import OrderedDict

class User(Model):
    id_column_name = "id"

    def columns_configuration(self):
        return OrderedDict([
            ('id', {'class': clearskies.column_types.UUID}),
            ('name', {'class': clearskies.column_types.String}),
            ('email', {'class': clearskies.column_types.Email}),
        ])""",
        "v2": """import clearskies
from clearskies import columns

class User(clearskies.Model):
    id_column_name = "id"
    backend = clearskies.backends.MemoryBackend()

    id = columns.Uuid()
    name = columns.String()
    email = columns.Email()""",
    },
    "handler_definition": {
        "v1": """from clearskies import Application
from clearskies.handlers import RestfulAPI

app = Application(
    handler_class=RestfulAPI,
    handler_config={
        'model_class': User,
        'base_url': 'users',
    },
)""",
        "v2": """import clearskies

endpoint = clearskies.endpoints.RestfulApi(
    url="users",
    model_class=User,
    readable_column_names=["id", "name", "email"],
    writeable_column_names=["name", "email"],
)

wsgi = clearskies.contexts.WsgiRef(endpoint)""",
    },
    "di_injection": {
        "v1": """class MyHandler:
    def __init__(self, di):
        self._di = di

    def handle(self, input_output):
        service = self._di.build(MyService)
        service.do_something()""",
        "v2": """from clearskies.di import inject

class MyModel(clearskies.Model):
    my_service = inject.ByClass(MyService)

    def do_something(self):
        self.my_service.do_something()""",
    },
}
