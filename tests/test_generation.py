"""Generated code from the scaffolding/generation tools must run on the installed clearskies."""

import re

import pytest

from clearskies_mcp_server.introspection import ENDPOINT_TYPES
from clearskies_mcp_server.tools import generation, scaffolding

COLUMNS = [
    {"name": "name", "type": "String"},
    {"name": "email", "type": "Email"},
    {"name": "age", "type": "Integer"},
]


def run_generated(code: str) -> dict:
    blocks = re.findall(r"```python\n(.*?)```", code, re.S)
    namespace: dict = {"__name__": "generated"}
    exec(compile("\n\n".join(blocks) if blocks else code, "generated", "exec"), namespace)
    return namespace


def test_scaffold_restful_api_builds_and_serves():
    import clearskies

    namespace = run_generated(scaffolding.scaffold_restful_api("User", COLUMNS))
    context = clearskies.contexts.Context(namespace["app"].application, classes=[namespace["User"]])
    status, body, _ = context(request_method="POST", url="users", body={"name": "alice", "email": "a@example.com"})
    assert status == 200, body
    status, body, _ = context(url="users")
    assert status == 200, body
    assert [row["name"] for row in body["data"]] == ["alice"]


def test_scaffold_project_with_two_models_builds():
    run_generated(
        scaffolding.scaffold_project(
            "demo",
            [
                {"name": "User", "columns": COLUMNS},
                {"name": "Team", "columns": [{"name": "title", "type": "String"}]},
            ],
        )
    )


def test_generate_model_declares_its_id_column():
    code = generation.generate_model("User", [{"name": "name", "type": "String"}])
    assert "    id = columns.Uuid()" in code
    run_generated(code)


@pytest.mark.parametrize("kwargs", [{}, {"readable_column_names": ["id", "name"], "writeable_column_names": ["name"]}])
def test_generate_endpoint_reports_missing_required_args(kwargs):
    code = generation.generate_endpoint("RestfulApi", "User", url="users", **kwargs)
    assert code.startswith("Error: RestfulApi requires")
    assert "searchable_column_names" in code


def test_generate_endpoint_complete_restful_api_constructs():
    model = generation.generate_model("User", [{"name": "name", "type": "String"}])
    endpoint = generation.generate_endpoint(
        "RestfulApi",
        "User",
        url="users",
        readable_column_names=["id", "name"],
        writeable_column_names=["name"],
        sortable_column_names=["name"],
        searchable_column_names=["name"],
        default_sort_column_name="name",
    )
    assert not endpoint.startswith("Error")
    run_generated(f"{model}\n\nendpoint = {endpoint}")


def test_every_endpoint_type_accepts_its_required_args_via_extra_options():
    # sanity check that the required-arg check doesn't reject types whose requirements come from extra_options
    for name in ENDPOINT_TYPES:
        assert not generation.generate_endpoint(
            name, "User", extra_options={"to_call": "lambda: {}"} if name == "Callable" else None
        ).startswith(f"Error: Unknown endpoint type")
