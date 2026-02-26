"""
Concept explanations for clearskies framework.

This package contains detailed explanations of clearskies framework concepts
used by the explain_concept tool. Concepts are organized by category.
"""

from .advanced import ADVANCED_CONCEPTS
from .authentication import AUTH_CONCEPTS
from .backends import BACKEND_CONCEPTS
from .base_classes import BASE_CLASS_CONCEPTS
from .core import CORE_CONCEPTS
from .data import DATA_CONCEPTS
from .devex import DEVEX_CONCEPTS
from .di import DI_CONCEPTS
from .features import FEATURES_CONCEPTS
from .internals import INTERNALS_CONCEPTS
from .lifecycle import LIFECYCLE_CONCEPTS
from .observability import OBSERVABILITY_CONCEPTS
from .programming import PROGRAMMING_CONCEPTS
from .reference import REFERENCE_CONCEPTS

# Combine all concept dictionaries into one
CONCEPT_EXPLANATIONS = {
    **CORE_CONCEPTS,
    **DI_CONCEPTS,
    **AUTH_CONCEPTS,
    **LIFECYCLE_CONCEPTS,
    **PROGRAMMING_CONCEPTS,
    **DATA_CONCEPTS,
    **FEATURES_CONCEPTS,
    **OBSERVABILITY_CONCEPTS,
    **ADVANCED_CONCEPTS,
    **BACKEND_CONCEPTS,
    **INTERNALS_CONCEPTS,
    **DEVEX_CONCEPTS,
    **REFERENCE_CONCEPTS,
    **BASE_CLASS_CONCEPTS,
}

__all__ = ["CONCEPT_EXPLANATIONS"]
