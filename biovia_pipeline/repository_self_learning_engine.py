# repository_self_learning_engine.py

from pathlib import Path
import importlib.util
import json

from .component_metadata_registry import (
    ComponentMetadata
)
class RepositorySelfLearningEngine:

    def __init__(self):

        self.learned_components = {}

    # =====================================================
    # REGISTER GENERATED COMPONENT
    # =====================================================

    def register_generated_component(
        self,
        generated_component,
        metadata_registry
    ):

        # metadata = ComponentMetadata(

        #     name=
        #         generated_component.component_name,

        #     module_name=
        #         (
        #             "generated_components."
        #             +
        #             generated_component.component_name
        #                 .replace(" ", "_")
        #                 .replace("-", "_")
        #                 .lower()
        #         ),

        #     category=
        #         "ai_generated",

        #     inputs=[],

        #     outputs=[],

        #     aliases=[
        #         generated_component.component_name
        #     ]
        # )
        metadata = ComponentMetadata(

            name=
                generated_component.component_name,

            module_name=
                (
                    "generated_components."
                    +
                    generated_component.component_name
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
        # metadata_registry.register(
        #     metadata
        # )
        metadata_registry.register_generated(
            generated_component
        )
        self.learned_components[
            generated_component.component_name
        ] = metadata

        return True

    # =====================================================
    # DISCOVER GENERATED COMPONENTS
    # =====================================================

    def discover_generated_components(
        self,
        generated_folder
    ):

        generated_folder = Path(
            generated_folder
        )

        discovered = []

        if not generated_folder.exists():

            return discovered

        for file in generated_folder.glob(
            "*.py"
        ):

            metadata = (
                self._read_metadata(
                    file
                )
            )

            if metadata:

                discovered.append(
                    metadata
                )

        return discovered

    # =====================================================
    # LOAD COMPONENT METADATA
    # =====================================================

    def _read_metadata(
        self,
        file_path
    ):

        try:

            spec = (
                importlib.util
                .spec_from_file_location(
                    file_path.stem,
                    str(file_path)
                )
            )

            module = (
                importlib.util
                .module_from_spec(
                    spec
                )
            )

            spec.loader.exec_module(
                module
            )

            metadata = getattr(
                module,
                "COMPONENT_METADATA",
                None
            )

            return metadata

        except Exception as ex:

            print(
                f"Failed loading "
                f"{file_path}: {ex}"
            )

            return None

    # =====================================================
    # UPDATE REGISTRY FILE
    # =====================================================

    def update_registry_file(
        self,
        registry_path,
        component_metadata
    ):

        registry_path = Path(
            registry_path
        )

        if registry_path.exists():

            data = json.loads(

                registry_path.read_text(
                    encoding="utf-8"
                )

            )

        else:

            data = {}

        name = component_metadata.get(
            "component_name"
        )

        data[name] = component_metadata

        registry_path.write_text(

            json.dumps(
                data,
                indent=4
            ),

            encoding="utf-8"
        )

    # =====================================================
    # AUTO DISCOVERY
    # =====================================================

    def learn_from_generated_folder(
        self,
        generated_folder,
        registry_path
    ):

        discovered = (
            self.discover_generated_components(
                generated_folder
            )
        )

        for metadata in discovered:

            self.update_registry_file(

                registry_path,

                metadata
            )

        return len(discovered)

    # =====================================================
    # REPORT
    # =====================================================

    def print_report(
        self
    ):

        print()

        print("=" * 80)

        print(
            "SELF LEARNING REPORT"
        )

        print("=" * 80)

        print()

        print(
            f"Learned Components: "
            f"{len(self.learned_components)}"
        )

        print()

        for component in (
            self.learned_components
        ):

            print(
                component
            )