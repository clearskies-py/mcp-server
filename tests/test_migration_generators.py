"""The v1->v2 endpoint generator must emit code that constructs on the installed clearskies."""

from pathlib import Path

import clearskies

from clearskies_mcp_server.migration.generators import EndpointGenerator
from clearskies_mcp_server.migration.models import ColumnDefinition, HandlerDefinition, ModelDefinition


class User(clearskies.Model):
    id_column_name = "id"
    backend = clearskies.backends.MemoryBackend()
    id = clearskies.columns.Uuid()
    name = clearskies.columns.String()
    email = clearskies.columns.Email()


MODEL = ModelDefinition(
    name="User",
    file_path=Path("models.py"),
    columns=[ColumnDefinition("id", "UUID"), ColumnDefinition("name", "String"), ColumnDefinition("email", "Email")],
)


def build(config: dict) -> object:
    code = EndpointGenerator().generate(
        HandlerDefinition(name="users", handler_class="RestfulAPI", config=config, model_class="User"), MODEL
    )
    namespace = {"User": User}
    exec(compile(code, "migrated", "exec"), namespace)
    return namespace["endpoint"]


def test_restful_api_gets_required_v2_arguments():
    assert isinstance(build({"base_url": "users"}), clearskies.endpoints.RestfulApi)


def test_explicit_v1_columns_override_inferred_ones_without_duplicates():
    endpoint = build({"base_url": "users", "readable_columns": ["id", "name"], "searchable_columns": ["name"]})
    assert endpoint.readable_column_names == ["id", "name"]
    assert endpoint.searchable_column_names == ["name"]
