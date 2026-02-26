"""
Known clearskies extension modules registry.

This module contains a minimal registry of known clearskies extension modules.
The registry only contains static metadata that rarely changes (package names,
import names, descriptions). Component information is discovered dynamically.
"""

KNOWN_MODULES: dict[str, dict] = {
    "clearskies-aws": {
        "package": "clear-skies-aws",
        "import": "clearskies_aws",
        "description": "AWS bindings for clearskies – Lambda contexts, DynamoDB/SQS backends, Parameter Store/Secrets Manager integration, SES/SNS/SQS actions, and IAM DB auth.",
        "pypi_url": "https://pypi.org/project/clear-skies-aws/",
        "optional_dep_name": "aws",
    },
    # Note: clearskies-graphql is not yet published to PyPI
    # "clearskies-graphql": {
    #     "package": "clear-skies-graphql",
    #     "import": "clearskies_graphql",
    #     "description": "GraphQL backend for clearskies – dynamically constructs GraphQL queries from model definitions with automatic case conversion, cursor/offset pagination, and relationship support.",
    #     "pypi_url": "https://pypi.org/project/clear-skies-graphql/",
    #     "optional_dep_name": "graphql",
    # },
    "clearskies-gitlab": {
        "package": "clear-skies-gitlab",
        "import": "clearskies_gitlab",
        "description": "GitLab integration module for clearskies – pre-built models for both GitLab REST and GraphQL APIs with ready-to-use backends.",
        "pypi_url": "https://pypi.org/project/clear-skies-gitlab/",
        "optional_dep_name": "gitlab",
    },
    "clearskies-cortex": {
        "package": "clear-skies-cortex",
        "import": "clearskies_cortex",
        "description": "Cortex service catalog integration for clearskies – pre-built models for the Cortex API to manage catalog entities, teams, scorecards, and more.",
        "pypi_url": "https://pypi.org/project/clear-skies-cortex/",
        "optional_dep_name": "cortex",
    },
    "clearskies-snyk": {
        "package": "clear-skies-snyk",
        "import": "clearskies_snyk",
        "description": "Snyk security platform integration for clearskies – comprehensive models for the Snyk REST API and legacy v1 API covering organizations, projects, groups, issues, policies, and more.",
        "pypi_url": "https://pypi.org/project/clear-skies-snyk/",
        "optional_dep_name": "snyk",
    },
    "clearskies-akeyless-custom-producer": {
        "package": "clear-skies-akeyless-custom-producer",
        "import": "clearskies_akeyless_custom_producer",
        "description": "Clearskies module for building Akeyless custom dynamic secret producers and rotators.",
        "pypi_url": "https://pypi.org/project/clear-skies-akeyless-custom-producer/",
        "optional_dep_name": "akeyless",
    },
}


# Static examples for modules (used as fallback when module is not installed)
# These are kept minimal and only provide basic usage guidance
MODULE_EXAMPLES: dict[str, str] = {
    "clearskies-aws": """\
# clearskies-aws Usage Guide

## Installation
```bash
pip install clear-skies-aws
# Or with clearskies-mcp:
pip install clearskies-mcp[aws]
```

## Lambda behind ALB

```python
import clearskies
import clearskies_aws

class User(clearskies.Model):
    id_column_name = "id"
    backend = clearskies.backends.MemoryBackend()
    id = clearskies.columns.Uuid()
    name = clearskies.columns.String()

execute = clearskies_aws.contexts.LambdaAlb(
    clearskies.endpoints.RestfulApi(
        url="users",
        model_class=User,
        readable_column_names=["id", "name"],
        writeable_column_names=["name"],
        default_sort_column_name="name",
    ),
    classes=[User],
)

def lambda_handler(event, context):
    return execute(event, context)
```

## DynamoDB Backend

```python
import clearskies
import clearskies_aws

class Product(clearskies.Model):
    id_column_name = "id"
    backend = clearskies_aws.backends.DynamoDBBackend()

    id = clearskies.columns.Uuid()
    name = clearskies.columns.String()
    price = clearskies.columns.Float()
```

## Parameter Store Secrets

```python
import clearskies_aws

def my_handler(secrets):
    api_key = secrets.get('/path/to/api-key')
    return {"status": "ok"}

execute = clearskies_aws.contexts.LambdaAlb(my_handler)

def lambda_handler(event, context):
    return execute(event, context)
```
""",
    "clearskies-gitlab": """\
# clearskies-gitlab Usage Guide

## Installation
```bash
pip install clear-skies-gitlab
# Or with clearskies-mcp:
pip install clearskies-mcp[gitlab]
```

## Environment Setup
Set the following environment variables:
- `GITLAB_AUTH_TOKEN` – Your GitLab personal access token or API token
- `GITLAB_HOST` – GitLab host (default: gitlab.com)

## Using REST Models

```python
import clearskies
from clearskies_gitlab.rest.models import GitlabRestProject, GitlabRestGroup

def list_projects(gitlab_rest_project: GitlabRestProject):
    for project in gitlab_rest_project.where("membership=true"):
        print(f"{project.name}: {project.web_url}")

cli = clearskies.contexts.Cli(
    clearskies.endpoints.Callable(list_projects, model_class=GitlabRestProject),
    classes=[GitlabRestProject],
)
```
""",
    "clearskies-cortex": """\
# clearskies-cortex Usage Guide

## Installation
```bash
pip install clear-skies-cortex
# Or with clearskies-mcp:
pip install clearskies-mcp[cortex]
```

## Environment Setup
Set the following environment variables:
- `CORTEX_AUTH_TOKEN` – Your Cortex API token
- `CORTEX_URL` – Cortex API base URL

## Listing Catalog Entities

```python
import clearskies
from clearskies_cortex.models import CortexCatalogEntity, CortexCatalogEntityService

def list_services(cortex_catalog_entity_service: CortexCatalogEntityService):
    for service in cortex_catalog_entity_service:
        print(f"{service.tag}: {service.title}")

cli = clearskies.contexts.Cli(
    clearskies.endpoints.Callable(list_services),
    classes=[CortexCatalogEntityService],
)
```
""",
    "clearskies-snyk": """\
# clearskies-snyk Usage Guide

## Installation
```bash
pip install clearskies-snyk
# Or with clearskies-mcp:
pip install clearskies-mcp[snyk]
```

## Environment Setup
```bash
# Option 1: Direct API key
export SNYK_AUTH_KEY=your-snyk-api-key

# Option 2: Secret manager path (recommended for production)
export SNYK_AUTH_SECRET_PATH=/path/to/secret
```

## Listing Organizations

```python
import clearskies
from clearskies_snyk.models import SnykOrg, SnykProject

def list_orgs(snyk_org: SnykOrg):
    for org in snyk_org:
        print(f"Org: {org.name} ({org.slug})")

cli = clearskies.contexts.Cli(
    clearskies.endpoints.Callable(list_orgs),
    classes=[SnykOrg],
)
```
""",
    "clearskies-akeyless-custom-producer": """\
# clearskies-akeyless-custom-producer Usage Guide

## Installation
```bash
pip install clear-skies-akeyless-custom-producer
# Or with clearskies-mcp:
pip install clearskies-mcp[akeyless]
```

## NoInput Endpoint (Producer without user input)

```python
import clearskies
from clearskies_akeyless_custom_producer.endpoints import NoInput

def create_credentials():
    return {
        "username": "dynamic-user",
        "password": "generated-password",
    }

wsgi = clearskies.contexts.WsgiRef(
    NoInput(
        create=create_credentials,
    )
)
wsgi()
```

## Available Endpoints
- **NoInput** – For producers that don't need user input
- **WithInput** – For producers that accept user-provided parameters
""",
}


def get_module_names() -> list[str]:
    """Get list of all known module names."""
    return list(KNOWN_MODULES.keys())


def get_module_info(module_name: str) -> dict | None:
    """Get static info for a module.

    Args:
        module_name: The module name (e.g., 'clearskies-aws')

    Returns:
        Module info dict or None if unknown
    """
    return KNOWN_MODULES.get(module_name)


def get_module_example(module_name: str) -> str | None:
    """Get example code for a module.

    Args:
        module_name: The module name

    Returns:
        Example code string or None if not available
    """
    return MODULE_EXAMPLES.get(module_name)


def get_install_command(module_name: str) -> str:
    """Get pip install command for a module.

    Args:
        module_name: The module name

    Returns:
        pip install command string
    """
    info = KNOWN_MODULES.get(module_name)
    if not info:
        return f"# Unknown module: {module_name}"

    return f"pip install {info['package']}"


def get_optional_install_command(module_name: str) -> str:
    """Get pip install command using optional dependency.

    Args:
        module_name: The module name

    Returns:
        pip install command string with optional dependency
    """
    info = KNOWN_MODULES.get(module_name)
    if not info:
        return f"# Unknown module: {module_name}"

    opt_name = info.get("optional_dep_name", module_name.split("-")[-1])
    return f"pip install clearskies-mcp[{opt_name}]"
