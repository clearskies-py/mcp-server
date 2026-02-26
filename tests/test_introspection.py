"""Tests for introspection module."""

from __future__ import annotations

import inspect
import unittest
from typing import Any
from unittest.mock import MagicMock, Mock, patch

from clearskies_mcp_server import introspection


class TestSafeIntrospectModule(unittest.TestCase):
    """Test safe_introspect_module function."""

    def test_introspect_with_all_attribute(self) -> None:
        """Test introspection when module has __all__."""
        mock_module = MagicMock()
        mock_module.__all__ = ["TestClass", "AnotherClass"]

        class TestClass:
            pass

        class AnotherClass:
            pass

        mock_module.TestClass = TestClass
        mock_module.AnotherClass = AnotherClass

        result = introspection.safe_introspect_module(mock_module, "test_module")

        assert "TestClass" in result
        assert "AnotherClass" in result
        assert result["TestClass"] is TestClass
        assert result["AnotherClass"] is AnotherClass

    def test_introspect_without_all_attribute(self) -> None:
        """Test introspection when module lacks __all__."""
        mock_module = MagicMock()
        del mock_module.__all__

        class PublicClass:
            pass

        mock_module.PublicClass = PublicClass
        mock_module._private_class = Mock()

        with patch("builtins.dir", return_value=["PublicClass", "_private_class"]):
            result = introspection.safe_introspect_module(mock_module, "test_module")

        assert "PublicClass" in result
        assert "_private_class" not in result

    def test_introspect_with_filter_func(self) -> None:
        """Test introspection with a filter function."""
        mock_module = MagicMock()
        mock_module.__all__ = ["BaseClass", "DerivedClass"]

        class BaseClass:
            pass

        class DerivedClass(BaseClass):
            pass

        mock_module.BaseClass = BaseClass
        mock_module.DerivedClass = DerivedClass

        # Only accept derived classes
        result = introspection.safe_introspect_module(
            mock_module, "test_module", filter_func=lambda cls: issubclass(cls, BaseClass) and cls != BaseClass
        )

        assert "DerivedClass" in result
        assert "BaseClass" not in result

    def test_introspect_handles_attribute_error(self) -> None:
        """Test that AttributeError is handled gracefully."""
        mock_module = MagicMock()
        mock_module.__all__ = ["MissingClass", "ValidClass"]

        class ValidClass:
            pass

        mock_module.ValidClass = ValidClass

        # Configure getattr to raise AttributeError for MissingClass
        def mock_getattr(name):
            if name == "MissingClass":
                raise AttributeError("MissingClass not found")
            return getattr(mock_module, name)

        with patch.object(mock_module, "__getattribute__", side_effect=mock_getattr):
            result = introspection.safe_introspect_module(mock_module, "test_module")

        # Should only contain ValidClass, MissingClass should be skipped
        assert "ValidClass" in result
        assert "MissingClass" not in result

    def test_introspect_handles_exception(self) -> None:
        """Test that general exceptions are handled gracefully."""
        mock_module = MagicMock()
        mock_module.__all__ = Mock(side_effect=RuntimeError("Test error"))

        result = introspection.safe_introspect_module(mock_module, "test_module")

        assert result == {}


class TestSafeIntrospectModuleAll(unittest.TestCase):
    """Test safe_introspect_module_all function."""

    def test_introspect_all_items(self) -> None:
        """Test introspection of all items, not just classes."""
        mock_module = MagicMock()
        mock_module.__all__ = ["test_class", "test_function", "test_constant"]

        class TestClass:
            pass

        def test_function():
            pass

        mock_module.test_class = TestClass
        mock_module.test_function = test_function
        mock_module.test_constant = 42

        result = introspection.safe_introspect_module_all(mock_module, "test_module")

        assert "test_class" in result
        assert "test_function" in result
        assert "test_constant" in result
        assert result["test_constant"] == 42

    def test_introspect_all_filters_private(self) -> None:
        """Test that private items are filtered out."""
        mock_module = MagicMock()
        mock_module.__all__ = ["public_item", "_private_item"]
        mock_module.public_item = "public"
        mock_module._private_item = "private"

        result = introspection.safe_introspect_module_all(mock_module, "test_module")

        assert "public_item" in result
        assert "_private_item" not in result


class TestGetDocstring(unittest.TestCase):
    """Test get_docstring function."""

    def test_get_docstring_with_doc(self) -> None:
        """Test getting docstring from a class with documentation."""

        class TestClass:
            """This is a test class.

            With multiple lines.
            """

            pass

        doc = introspection.get_docstring(TestClass)
        assert "This is a test class" in doc
        assert "With multiple lines" in doc

    def test_get_docstring_without_doc(self) -> None:
        """Test getting docstring from a class without documentation."""

        class TestClass:
            pass

        doc = introspection.get_docstring(TestClass)
        assert doc == ""


class TestGetInitParams(unittest.TestCase):
    """Test get_init_params function."""

    def test_get_init_params_basic(self) -> None:
        """Test getting init parameters from a simple class."""

        class TestClass:
            def __init__(self, name: str, age: int = 0):
                pass

        params = introspection.get_init_params(TestClass)

        assert len(params) == 2
        assert params[0]["name"] == "name"
        assert "str" in params[0]["type"]
        assert "default" not in params[0]

        assert params[1]["name"] == "age"
        assert "int" in params[1]["type"]
        assert params[1]["default"] == 0

    def test_get_init_params_no_params(self) -> None:
        """Test getting init parameters from a class with no params."""

        class TestClass:
            def __init__(self):
                pass

        params = introspection.get_init_params(TestClass)
        assert len(params) == 0

    def test_get_init_params_complex_default(self) -> None:
        """Test getting init parameters with non-JSON-serializable defaults."""

        class TestClass:
            def __init__(self, callback=lambda x: x):
                pass

        params = introspection.get_init_params(TestClass)

        assert len(params) == 1
        assert params[0]["name"] == "callback"
        assert "default" in params[0]
        # Non-serializable defaults should be repr'd
        assert "lambda" in str(params[0]["default"])

    def test_get_init_params_handles_no_signature(self) -> None:
        """Test handling classes without inspectable __init__."""

        class TestClass:
            pass

        # Mock to raise ValueError when inspecting
        with patch("inspect.signature", side_effect=ValueError):
            params = introspection.get_init_params(TestClass)
            assert params == []


class TestGetClassInfo(unittest.TestCase):
    """Test get_class_info function."""

    def test_get_class_info_basic(self) -> None:
        """Test getting class info for a basic class."""

        class TestClass:
            """Test documentation."""

            def __init__(self, value: int):
                pass

        info = introspection.get_class_info(TestClass, "Column")

        assert "# Column: TestClass" in info
        assert "Test documentation" in info
        assert "Constructor Parameters" in info
        assert "value" in info

    def test_get_class_info_exception(self) -> None:
        """Test getting class info for an exception class."""

        class CustomError(ValueError):
            """Custom error."""

            pass

        info = introspection.get_class_info(CustomError, "Exception")

        assert "# Exception: CustomError" in info
        assert "Custom error" in info
        assert "Exception Hierarchy" in info
        assert "ValueError" in info

    def test_get_class_info_no_params(self) -> None:
        """Test getting class info for a class with explicit empty init."""

        class TestClass:
            """Test class."""

            def __init__(self):
                pass

        info = introspection.get_class_info(TestClass)

        assert "# Type: TestClass" in info
        assert "Test class" in info
        # Class with empty __init__ should not show parameters
        assert "Constructor Parameters" not in info


class TestListTypesFormatted(unittest.TestCase):
    """Test list_types_formatted function."""

    def test_list_types_formatted_basic(self) -> None:
        """Test formatting a type registry."""

        class TypeA:
            """Type A description.

            More details.
            """

            pass

        class TypeB:
            """Type B description."""

            pass

        registry = {"TypeA": TypeA, "TypeB": TypeB}

        result = introspection.list_types_formatted(registry)

        assert "**TypeA**: Type A description." in result
        assert "**TypeB**: Type B description." in result

    def test_list_types_formatted_empty(self) -> None:
        """Test formatting an empty registry."""
        result = introspection.list_types_formatted({})
        assert result == "(no types available)"

    def test_list_types_formatted_no_docstring(self) -> None:
        """Test formatting types without docstrings."""

        class UndocumentedType:
            pass

        registry = {"UndocumentedType": UndocumentedType}

        result = introspection.list_types_formatted(registry)

        assert "**UndocumentedType**: (no description)" in result

    def test_list_types_formatted_sorted(self) -> None:
        """Test that types are sorted alphabetically."""

        class Zebra:
            """Z."""

            pass

        class Apple:
            """A."""

            pass

        class Middle:
            """M."""

            pass

        registry = {"Zebra": Zebra, "Apple": Apple, "Middle": Middle}

        result = introspection.list_types_formatted(registry)
        lines = result.split("\n")

        # Should be sorted: Apple, Middle, Zebra
        assert "Apple" in lines[0]
        assert "Middle" in lines[1]
        assert "Zebra" in lines[2]


class TestRegistryHelpers(unittest.TestCase):
    """Test registry helper functions."""

    def test_get_type_registry(self) -> None:
        """Test get_type_registry function."""
        columns = introspection.get_type_registry("columns")
        assert isinstance(columns, dict)

        # Should return empty dict for unknown category
        unknown = introspection.get_type_registry("unknown_category")
        assert unknown == {}

    def test_get_all_categories(self) -> None:
        """Test get_all_categories function."""
        categories = introspection.get_all_categories()
        assert isinstance(categories, list)
        assert "columns" in categories
        assert "endpoints" in categories
        assert "backends" in categories
        assert "contexts" in categories

    def test_get_available_categories(self) -> None:
        """Test get_available_categories function."""
        categories = introspection.get_available_categories()
        assert isinstance(categories, list)

        # All categories should have at least one type
        for category in categories:
            registry = introspection.get_type_registry(category)
            assert len(registry) > 0


class TestTypeRegistries(unittest.TestCase):
    """Test that type registries are properly populated."""

    def test_column_types_populated(self) -> None:
        """Test that COLUMN_TYPES is populated."""
        assert len(introspection.COLUMN_TYPES) > 0
        assert "String" in introspection.COLUMN_TYPES

    def test_endpoint_types_populated(self) -> None:
        """Test that ENDPOINT_TYPES is populated."""
        assert len(introspection.ENDPOINT_TYPES) > 0

    def test_backend_types_populated(self) -> None:
        """Test that BACKEND_TYPES is populated."""
        assert len(introspection.BACKEND_TYPES) > 0

    def test_context_types_populated(self) -> None:
        """Test that CONTEXT_TYPES is populated."""
        assert len(introspection.CONTEXT_TYPES) > 0

    def test_authentication_types_populated(self) -> None:
        """Test that AUTHENTICATION_TYPES is populated."""
        assert len(introspection.AUTHENTICATION_TYPES) > 0

    def test_all_type_registries_keys(self) -> None:
        """Test that ALL_TYPE_REGISTRIES has expected keys."""
        expected_keys = {
            "columns",
            "endpoints",
            "backends",
            "contexts",
            "authentication",
            "validators",
            "exceptions",
            "di_inject",
            "cursors",
            "input_outputs",
            "configs",
            "clients",
            "secrets",
            "security_headers",
            "query",
            "query_results",
            "functional",
        }

        assert set(introspection.ALL_TYPE_REGISTRIES.keys()) == expected_keys


if __name__ == "__main__":
    unittest.main()
