"""
Module documentation resources for clearskies ecosystem.

This module provides resource functions that return documentation
for various clearskies extension modules.
"""

from ..tools.modules import explain_module, get_module_info, list_modules


def modules_overview() -> str:
    """Overview of all clearskies extension modules in the ecosystem."""
    return list_modules()


def module_aws() -> str:
    """Documentation for the clearskies-aws module."""
    return get_module_info("clearskies-aws") + "\n\n---\n\n" + explain_module("clearskies-aws")


def module_graphql() -> str:
    """Documentation for the clearskies-graphql module."""
    return get_module_info("clearskies-graphql") + "\n\n---\n\n" + explain_module("clearskies-graphql")


def module_gitlab() -> str:
    """Documentation for the clearskies-gitlab module."""
    return get_module_info("clearskies-gitlab") + "\n\n---\n\n" + explain_module("clearskies-gitlab")


def module_cortex() -> str:
    """Documentation for the clearskies-cortex module."""
    return get_module_info("clearskies-cortex") + "\n\n---\n\n" + explain_module("clearskies-cortex")


def module_snyk() -> str:
    """Documentation for the clearskies-snyk module."""
    return get_module_info("clearskies-snyk") + "\n\n---\n\n" + explain_module("clearskies-snyk")


def module_akeyless() -> str:
    """Documentation for the clearskies-akeyless-custom-producer module."""
    return (
        get_module_info("clearskies-akeyless-custom-producer")
        + "\n\n---\n\n"
        + explain_module("clearskies-akeyless-custom-producer")
    )
