# component_metadata_registry.py

import importlib
import pkgutil

from dataclasses import dataclass
from typing import Dict, List, Optional


# ============================================================
# MODELS
# ============================================================

@dataclass
class ComponentMetadata:

    name: str

    module_name: str

    category: str

    inputs: List[str]

    outputs: List[str]

    parameters: List[str]

    ui_component: bool = False

    import_path: Optional[str] = None


# ============================================================
# REGISTRY
# ============================================================

class ComponentMetadataRegistry:

    def __init__(self):

        self.components: Dict[
            str,
            ComponentMetadata
        ] = {}

    # ========================================================
    # LOAD ALL COMPONENTS
    # ========================================================

    def load_repository(
        self,
        package_name="biovia_pipeline.components"
    ):

        package = importlib.import_module(
            package_name
        )
        print()
        print("=" * 80)
        print("PACKAGE:", package_name)
        print("=" * 80)
        for module_info in (
            pkgutil.iter_modules(
                package.__path__
            )
        ):

            module_name = (
                module_info.name
            )
            print(
                "DISCOVERED MODULE:",
                module_name
            )
            full_name = (
                f"{package_name}."
                f"{module_name}"
            )

            try:

                module = (
                    importlib.import_module(
                        full_name
                    )
                )

                metadata = getattr(
                    module,
                    "COMPONENT_METADATA",
                    None
                )
                if metadata:

                    print(
                        "FOUND METADATA:",
                        metadata
                    )

                else:

                    print(
                        "NO METADATA:",
                        module_name
                    )

                if not metadata:
                    continue

                component = ComponentMetadata(

                    name=
                        metadata.get(
                            "name",
                            module_name
                        ),

                    module_name=
                        module_name,

                    category=
                        metadata.get(
                            "category",
                            "UNKNOWN"
                        ),

                    inputs=
                        metadata.get(
                            "inputs",
                            []
                        ),

                    outputs=
                        metadata.get(
                            "outputs",
                            []
                        ),

                    parameters=
                        metadata.get(
                            "parameters",
                            []
                        ),

                    ui_component=
                        metadata.get(
                            "ui_component",
                            False
                        ),

                    import_path=
                        full_name
                )

                self.components[
                    component.name.lower()
                ] = component

            except Exception as ex:

                print(
                    f"Failed loading "
                    f"{full_name}: "
                    f"{ex}"
                )

    # ========================================================
    # LOOKUPS
    # ========================================================

    def get(
        self,
        component_name: str
    ):

        return self.components.get(
            component_name.lower()
        )

    def exists(
        self,
        component_name: str
    ):

        return (
            component_name
            in self.components
        )

    def all_components(
        self
    ):

        return list(
            self.components.values()
        )

    # ========================================================
    # FILTERING
    # ========================================================

    def by_category(
        self,
        category: str
    ):

        return [

            c

            for c in (
                self.components.values()
            )

            if c.category == category
        ]
    def register_generated(
        self,
        generated_component
    ):

        metadata = ComponentMetadata(

            name=
                generated_component.component_name,

            module_name=
                (
                    "generated_components."
                    +
                    generated_component
                    .component_name
                    .replace(" ", "_")
                    .replace("-", "_")
                    .lower()
                ),

            category=
                "ai_generated",

            inputs=[],

            outputs=[],

            parameters=[],

            ui_component=False,

            import_path=None
        )

        self.register(
            metadata
        )

        return metadata
    # ========================================================
    # REGISTER
    # ========================================================

    def register(
        self,
        metadata
    ):

        #
        # Generated component object
        #
        if isinstance(
            metadata,
            ComponentMetadata
        ):

            self.components[
                metadata.name.lower()
            ] = metadata

            return True

        #
        # Dictionary metadata
        #
        if isinstance(
            metadata,
            dict
        ):

            component_name = (
                metadata.get(
                    "component_name"
                )
                or
                metadata.get(
                    "name"
                )
            )

            if component_name:

                self.components[
                    component_name.lower()
                ] = metadata

                return True

        return False
    
    # ========================================================
    # REPORT
    # ========================================================

    def print_report(
        self
    ):

        print()

        print("=" * 80)

        print(
            "COMPONENT METADATA REGISTRY"
        )

        print("=" * 80)

        print()

        for component in (
            self.components.values()
        ):

            print(
                component.name
            )

            print(
                f"  Module : "
                f"{component.module_name}"
            )

            print(
                f"  Category : "
                f"{component.category}"
            )

            print(
                f"  Inputs : "
                f"{component.inputs}"
            )

            print(
                f"  Outputs : "
                f"{component.outputs}"
            )

            print()