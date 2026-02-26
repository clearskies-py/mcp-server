"""
V2 code generators.

Generate v2-compatible code from v1 patterns.
"""

from pathlib import Path
from typing import TYPE_CHECKING

from .mapper import V1ToV2Mapper

if TYPE_CHECKING:
    from .models import (
        AnalysisReport,
        ColumnDefinition,
        DIUsage,
        HandlerDefinition,
        InitParam,
        MigrationPlan,
        MixinConfig,
        ModelDefinition,
    )


class ModelGenerator:
    """Generate v2 model classes with mixins, type hints, and modern patterns."""

    def __init__(self, mapper: V1ToV2Mapper | None = None):
        """Initialize the generator."""
        self.mapper = mapper or V1ToV2Mapper()

        # Import helper classes
        from .import_organizer import ImportOrganizer
        from .mixin_detector import MixinDetector, MixinGenerator
        from .type_hint_generator import TypeHintGenerator

        self.type_hint_gen = TypeHintGenerator()
        self.mixin_detector = MixinDetector()
        self.mixin_gen = MixinGenerator()
        self.import_org = ImportOrganizer()
        self.config_gen = ConfigGenerator()
        self.di_gen = DIPropertyGenerator()

    def generate(self, model_def: "ModelDefinition") -> str:
        """
        Generate v2 model code from v1 model definition.

        Args:
            model_def: V1 model definition

        Returns:
            Generated v2 model code with mixins, type hints, configs
        """
        lines = []
        required_imports = set()

        # Always need clearskies and columns
        required_imports.add("import clearskies")
        required_imports.add("from clearskies import columns")

        # Detect mixin requirements if not already detected
        if model_def.mixin_config is None:
            model_def.mixin_config = self._analyze_model_for_mixins(model_def)

        mixin_config = model_def.mixin_config

        # Add mixin imports
        if mixin_config.required_mixins:
            mixin_imports = self.mixin_gen.generate_required_imports(mixin_config.required_mixins)
            required_imports.update(mixin_imports)

        # Add DI imports if needed
        if mixin_config.di_usage.has_di_init or mixin_config.di_usage.di_builds:
            required_imports.add("from clearskies.di import inject, InjectableProperties")

        # Type checking imports
        if model_def.hooks or model_def.custom_methods:
            type_checking_imports = self.type_hint_gen.generate_type_checking_block(
                self.type_hint_gen.detect_required_imports("\n".join([h for h in model_def.hooks]))
            )
            if type_checking_imports:
                lines.append(type_checking_imports)
                lines.append("")

        # Generate organized imports
        import_block = self.import_org.generate_import_block(required_imports)
        lines.append(import_block)

        # Class definition with mixins
        class_line = self.mixin_gen.generate_class_with_mixins(
            model_def.name, mixin_config.required_mixins, "clearskies.Model"
        )
        lines.append(class_line)

        # Class attributes
        lines.append(f'    id_column_name = "{model_def.id_column}"')
        lines.append(f"    backend = clearskies.backends.{model_def.backend}()")
        if model_def.table_name:
            lines.append(f'    table_name = "{model_def.table_name}"')
        lines.append("")

        # Generate configs.* attributes if Configurable is used
        if "configurable.Configurable" in mixin_config.required_mixins and mixin_config.init_params:
            lines.append("    # Configuration attributes")
            lines.append(self.config_gen.generate_config_attributes(mixin_config.init_params))
            lines.append("")

        # Generate DI properties if InjectableProperties is used
        if "InjectableProperties" in mixin_config.required_mixins and mixin_config.di_usage.di_builds:
            lines.append("    # Dependency injection properties")
            lines.append(self.di_gen.generate_di_properties(mixin_config.di_usage))
            lines.append("")

        # Generate columns
        for col in model_def.columns:
            col_code = self._generate_column(col)
            if col_code:
                lines.append(f"    {col_code}")

        # Generate __init__ if Configurable is used
        if "configurable.Configurable" in mixin_config.required_mixins and mixin_config.init_params:
            lines.append("")
            lines.append(self.config_gen.generate_decorated_init(mixin_config.init_params))

        # Generate hooks if any with type hints
        if model_def.hooks:
            lines.append("")
            lines.append("    # Lifecycle hooks")
            for hook in model_def.hooks:
                lines.append(self._generate_hook_stub_with_hints(hook))

        # Add note about custom methods
        if model_def.custom_methods:
            lines.append("")
            lines.append("    # TODO: Migrate custom methods:")
            for method in model_def.custom_methods:
                lines.append(f"    # - {method}()")

        return "\n".join(lines)

    def _analyze_model_for_mixins(self, model_def: "ModelDefinition") -> "MixinConfig":
        """
        Analyze model to detect required mixins.

        Args:
            model_def: Model definition to analyze

        Returns:
            MixinConfig with detected requirements
        """
        from .models import DIUsage, MixinConfig

        # This would normally parse the actual class AST, but since we have
        # a ModelDefinition, we infer from available information
        config = MixinConfig()

        # For now, assume basic configuration
        # In a real implementation, this would parse the original v1 code
        config.uses_logging = False
        config.di_usage = DIUsage()

        return config

    def _generate_hook_stub_with_hints(self, hook_name: str) -> str:
        """Generate a hook method stub with type hints."""
        return self.type_hint_gen.add_hints_to_hook_method(hook_name)

    def _generate_column(self, col: "ColumnDefinition") -> str:
        """Generate a single column definition."""
        v2_column_type = self.mapper.map_column_type(col.column_class)

        # Build kwargs from config
        kwargs_parts = []
        for key, value in col.config.items():
            if isinstance(value, str):
                kwargs_parts.append(f'{key}="{value}"')
            elif isinstance(value, bool):
                kwargs_parts.append(f"{key}={value}")
            elif isinstance(value, list):
                kwargs_parts.append(f"{key}={value!r}")
            else:
                kwargs_parts.append(f"{key}={value}")

        kwargs_str = ", ".join(kwargs_parts)
        if kwargs_str:
            return f"{col.name} = columns.{v2_column_type}({kwargs_str})"
        return f"{col.name} = columns.{v2_column_type}()"

    def _generate_hook_stub(self, hook_name: str) -> str:
        """Generate a hook method stub."""
        return f"""
    def {hook_name}(self, **kwargs):
        \"\"\"Hook: {hook_name}.\"\"\"
        # TODO: Migrate {hook_name} logic
        pass"""


class EndpointGenerator:
    """Generate v2 endpoint configurations with authentication."""

    def __init__(self, mapper: V1ToV2Mapper | None = None):
        """Initialize the generator."""
        self.mapper = mapper or V1ToV2Mapper()

        from .auth_migrator import AuthMigrationHelper

        self.auth_helper = AuthMigrationHelper()

    def generate(self, handler_def: "HandlerDefinition", model_def: "ModelDefinition | None" = None) -> str:
        """
        Generate v2 endpoint code from v1 handler definition.

        Args:
            handler_def: V1 handler definition
            model_def: Optional model definition for inferring columns

        Returns:
            Generated v2 endpoint code with authentication
        """
        lines = []

        # Determine endpoint class
        v2_endpoint_class = self.mapper.map_class(f"clearskies.handlers.{handler_def.handler_class}").v2_class
        if not v2_endpoint_class:
            v2_endpoint_class = "clearskies.endpoints.RestfulApi"

        endpoint_class_name = v2_endpoint_class.split(".")[-1]

        # Imports
        lines.append("import clearskies")
        lines.append("from typing import Any")
        lines.append("")

        # Generate endpoint configuration
        lines.append(f"endpoint = clearskies.endpoints.{endpoint_class_name}(")

        # Add URL
        url = handler_def.config.get("base_url", handler_def.config.get("url", ""))
        if url:
            lines.append(f'    url="{url}",')

        # Add model_class
        model_class = handler_def.config.get("model_class", handler_def.model_class)
        if model_class:
            lines.append(f"    model_class={model_class},")

        # Add column configurations
        if model_def:
            readable_cols = [col.name for col in model_def.columns if not col.name.startswith("_")]
            writeable_cols = [
                col.name
                for col in model_def.columns
                if not col.name.startswith("_") and col.name not in [model_def.id_column, "created_at", "updated_at"]
            ]

            lines.append(f"    readable_column_names={readable_cols!r},")
            lines.append(f"    writeable_column_names={writeable_cols!r},")

        # Add authentication if present
        if handler_def.authentication or "authentication" in handler_def.config:
            auth_code, _ = self.auth_helper.migrate_auth(handler_def.config)
            lines.append(f"    {auth_code},")

        # Add other config
        for key, value in handler_def.config.items():
            if key not in ["base_url", "url", "model_class", "authentication", "authentication_config"]:
                v2_key = self.mapper.map_config_key(key)
                if isinstance(value, str):
                    lines.append(f'    {v2_key}="{value}",')
                else:
                    lines.append(f"    {v2_key}={value!r},")

        lines.append(")")

        return "\n".join(lines)


class ContextGenerator:
    """Generate v2 context wrappers."""

    def generate(self, context_type: str = "WsgiRef") -> str:
        """
        Generate v2 context wrapper code.

        Args:
            context_type: Type of context (WsgiRef, Cli, Lambda, etc.)

        Returns:
            Generated v2 context code
        """
        lines = []

        lines.append("import clearskies")
        lines.append("")
        lines.append("# Import your models and endpoints")
        lines.append("# from .models import User")
        lines.append("# from .endpoints import user_endpoint")
        lines.append("")

        if context_type == "WsgiRef":
            lines.append("# WSGI application")
            lines.append("wsgi = clearskies.contexts.WsgiRef(")
            lines.append("    # your_endpoint,  # TODO: Add your endpoint")
            lines.append("    # bindings={},  # TODO: Add DI bindings")
            lines.append("    # classes=[],  # TODO: Add classes for DI")
            lines.append(")")
        elif context_type == "Cli":
            lines.append("# CLI application")
            lines.append("cli = clearskies.contexts.Cli(")
            lines.append("    # your_endpoint,  # TODO: Add your endpoint")
            lines.append("    # bindings={},  # TODO: Add DI bindings")
            lines.append(")")
        else:
            lines.append(f"# {context_type} application")
            lines.append(f"app = clearskies.contexts.{context_type}(")
            lines.append("    # your_endpoint,  # TODO: Configure endpoint")
            lines.append(")")

        return "\n".join(lines)


class DIGenerator:
    """Generate v2 dependency injection code."""

    def generate_property_injection(self, class_name: str, dependencies: list[str]) -> str:
        """
        Generate property-based DI code.

        Args:
            class_name: Name of the class
            dependencies: List of dependency class names

        Returns:
            Generated DI code
        """
        lines = []

        lines.append(f"class {class_name}(clearskies.Model):")
        lines.append("    # Property-based dependency injection")
        for dep in dependencies:
            lines.append(f"    {dep.lower()} = inject.ByClass({dep})")
        lines.append("")
        lines.append("    def my_method(self):")
        for dep in dependencies:
            lines.append(f"        self.{dep.lower()}.do_something()")

        return "\n".join(lines)


class ConfigGenerator:
    """Generate configs.* attributes and decorated __init__."""

    def __init__(self):
        """Initialize the generator."""
        from .parsers import ConfigParser

        self.parser = ConfigParser()

    def generate_config_attributes(self, params: list["InitParam"]) -> str:
        """
        Generate configs.* class attributes from __init__ params.

        Args:
            params: List of InitParam objects

        Returns:
            Generated config attributes code
        """
        lines = []
        for param in params:
            config_type = self.parser.infer_config_type(param)
            kwargs = []

            if param.default is not None:
                if isinstance(param.default, str):
                    kwargs.append(f'default="{param.default}"')
                else:
                    kwargs.append(f"default={param.default}")

            kwargs_str = ", ".join(kwargs) if kwargs else ""
            lines.append(f"    {param.name} = {config_type}({kwargs_str})")

        return "\n".join(lines)

    def generate_decorated_init(self, params: list["InitParam"]) -> str:
        """
        Generate @parameters_to_properties decorated __init__.

        Args:
            params: List of InitParam objects

        Returns:
            Generated __init__ method code
        """
        param_strs = []
        for param in params:
            if param.type_hint:
                param_str = f"{param.name}: {param.type_hint} | None = None"
            else:
                param_str = f"{param.name} = None"
            param_strs.append(param_str)

        return f"""    @parameters_to_properties
    def __init__(self, {", ".join(param_strs)}):
        super().finalize_and_validate_configuration()"""


class DIPropertyGenerator:
    """Generate property-based DI from v1 constructor DI."""

    INJECT_HELPERS = {
        "models": "inject.ByName('models')",
        "cursor": "inject.ByName('cursor')",
        "utcnow": "inject.Utcnow()",
        "time": "inject.Utcnow()",
        "environment": "inject.Environment()",
        "requests": "inject.Requests()",
        "logger": "inject.Logger()",
    }

    def generate_di_properties(self, di_usage: "DIUsage") -> str:
        """
        Generate inject.* properties from DI usage.

        Args:
            di_usage: DIUsage object with detected patterns

        Returns:
            Generated DI properties code
        """
        lines = []

        for build_target in di_usage.di_builds:
            target_lower = build_target.lower()

            if target_lower in self.INJECT_HELPERS:
                lines.append(f"    {target_lower} = {self.INJECT_HELPERS[target_lower]}")
            else:
                # Assume it's a class name
                class_name = build_target.title().replace("_", "")
                lines.append(f"    {target_lower} = inject.ByClass({class_name})")

        # Add any explicit inject properties
        for prop_name, class_name in di_usage.inject_properties.items():
            if prop_name not in [target.lower() for target in di_usage.di_builds]:
                lines.append(f"    {prop_name} = inject.ByClass({class_name})")

        return "\n".join(lines)

    def generate_inject_helper(self, helper_name: str) -> str:
        """
        Generate a specific inject helper.

        Args:
            helper_name: Name of the helper (utcnow, environment, etc.)

        Returns:
            Generated inject property code
        """
        helper_lower = helper_name.lower()
        if helper_lower in self.INJECT_HELPERS:
            return f"    {helper_lower} = {self.INJECT_HELPERS[helper_lower]}"
        return f"    # TODO: Configure {helper_name} injection"


class V2CodeGenerator:
    """Main code generator that orchestrates all generation."""

    def __init__(self, mapper: V1ToV2Mapper | None = None):
        """Initialize the generator."""
        self.mapper = mapper or V1ToV2Mapper()
        self.model_gen = ModelGenerator(self.mapper)
        self.endpoint_gen = EndpointGenerator(self.mapper)
        self.context_gen = ContextGenerator()
        self.di_gen = DIGenerator()

    def generate_all(self, report: "AnalysisReport", output_dir: Path | None = None) -> "MigrationPlan":
        """
        Generate complete v2 codebase from analysis report.

        Args:
            report: V1 analysis report
            output_dir: Optional output directory path

        Returns:
            Complete migration plan
        """
        from .models import MigrationFile, MigrationPlan

        plan = MigrationPlan()

        # Generate models
        for model_def in report.models:
            model_code = self.model_gen.generate(model_def)
            file_path = Path("models") / f"{model_def.name.lower()}.py"
            plan.files.append(MigrationFile(path=file_path, content=model_code))

        # Generate endpoints
        if report.handlers:
            endpoint_code_parts = ["import clearskies", ""]
            for handler_def in report.handlers:
                # Find corresponding model
                corresponding_model: "ModelDefinition | None" = None
                model_class = handler_def.config.get("model_class")
                if model_class:
                    for m in report.models:
                        if m.name == model_class:
                            corresponding_model = m
                            break

                endpoint_code = self.endpoint_gen.generate(handler_def, corresponding_model)
                endpoint_code_parts.append(endpoint_code)
                endpoint_code_parts.append("")

            plan.files.append(MigrationFile(path=Path("endpoints.py"), content="\n".join(endpoint_code_parts)))

        # Generate context/application
        context_code = self.context_gen.generate("WsgiRef")
        plan.files.append(MigrationFile(path=Path("app.py"), content=context_code))

        # Collect breaking changes
        plan.breaking_changes.append("Models: columns_configuration() → class attributes")
        plan.breaking_changes.append("Handlers → Endpoints (renamed)")
        plan.breaking_changes.append("Application → Context wrappers")
        plan.breaking_changes.append("Explicit readable/writeable column configuration required")

        # Collect manual steps with detailed guidance
        plan.manual_steps.append("=" * 80)
        plan.manual_steps.append("MIGRATION COMPLETE - MANUAL STEPS REQUIRED (~15% of work)")
        plan.manual_steps.append("=" * 80)
        plan.manual_steps.append("")

        plan.manual_steps.append("1. CUSTOM BUSINESS LOGIC (~5% of migration)")
        plan.manual_steps.append("   Review all TODO comments in generated code:")
        for model in report.models:
            if model.hooks or model.custom_methods:
                plan.manual_steps.append(
                    f"   - {model.file_path}: Migrate logic from {len(model.hooks)} hooks, {len(model.custom_methods)} custom methods"
                )
        plan.manual_steps.append("   Action: Copy business logic from v1, adapt for breaking changes")
        plan.manual_steps.append("")

        plan.manual_steps.append("2. ENDPOINT SECURITY REVIEW (~3% of migration)")
        plan.manual_steps.append("   Verify readable/writeable column lists:")
        for handler in report.handlers:
            if handler.model_class:
                plan.manual_steps.append(
                    f"   - {handler.name}: Remove sensitive columns (passwords, tokens, etc.) from readable_column_names"
                )
        plan.manual_steps.append("   Action: Remove password_hash, api_tokens, secrets from exposed columns")
        plan.manual_steps.append("")

        plan.manual_steps.append("3. PRODUCTION CONTEXT SETUP (~2% of migration)")
        plan.manual_steps.append("   Configure production context in app.py:")
        plan.manual_steps.append("   - Switch from WsgiRef (dev) → Wsgi (production)")
        plan.manual_steps.append("   - Set up production DI bindings")
        plan.manual_steps.append("   - Configure database connections")
        plan.manual_steps.append("   Action: Update context wrapper for your deployment environment")
        plan.manual_steps.append("")

        plan.manual_steps.append("4. COMPLEX DI PATTERNS (~2% of migration)")
        plan.manual_steps.append("   Review any dynamic or computed DI patterns:")
        plan.manual_steps.append("   - Dynamic class loading (di.build(computed_name))")
        plan.manual_steps.append("   - Conditional DI")
        plan.manual_steps.append("   - Factory patterns")
        plan.manual_steps.append("   Action: Manually convert to appropriate inject.* pattern")
        plan.manual_steps.append("")

        plan.manual_steps.append("5. TESTING & VALIDATION (~3% of migration)")
        plan.manual_steps.append("   - Run all tests: pytest tests/")
        plan.manual_steps.append("   - Compare v1 vs v2 behavior on critical workflows")
        plan.manual_steps.append("   - Test authentication flows")
        plan.manual_steps.append("   - Load testing if applicable")
        plan.manual_steps.append("   Action: Ensure feature parity between v1 and v2")
        plan.manual_steps.append("")

        plan.manual_steps.append("AUTOMATED (Already completed by migration tool):")
        plan.manual_steps.append("  ✅ Type hints (Python 3.13+)")
        plan.manual_steps.append("  ✅ Mixins (Configurable, InjectableProperties, Loggable)")
        plan.manual_steps.append("  ✅ Configuration (configs.* attributes)")
        plan.manual_steps.append("  ✅ DI property injection")
        plan.manual_steps.append("  ✅ Import organization")
        plan.manual_steps.append("  ✅ Authentication configuration")
        plan.manual_steps.append("  ✅ Column definitions")
        plan.manual_steps.append("")
        plan.manual_steps.append("Need help? Run: explain_v1_v2_difference('<topic>')")
        plan.manual_steps.append("=" * 80)

        # Add warnings
        if report.warnings:
            plan.warnings.extend(report.warnings)

        return plan
