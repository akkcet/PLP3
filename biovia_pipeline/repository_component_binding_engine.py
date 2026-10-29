# repository_component_binding_engine.py

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ============================================================
# MODELS
# ============================================================

@dataclass
class RepositoryComponent:

    plp_name: str

    python_module: str

    python_function: str

    import_statement: str

    category: str


@dataclass
class BoundComponent:

    component_name: str

    repository_component: RepositoryComponent

    confidence: float


@dataclass
class BindingResult:

    bound_components: List[BoundComponent]

    missing_components: List[str]


# ============================================================
# COMPONENT REGISTRY
# ============================================================

COMPONENT_REPOSITORY = {

    "notebook connection":
        RepositoryComponent(
            plp_name="Notebook Connection",
            python_module=
                "biovia_pipeline.notebook_connection",
            python_function=
                "notebook_connection",
            import_statement=
                "from biovia_pipeline.notebook_connection import notebook_connection",
            category="connection"
        ),

    "experiment query":
        RepositoryComponent(
            plp_name="Experiment Query",
            python_module=
                "biovia_pipeline.experiment_query",
            python_function=
                "experiment_query",
            import_statement=
                "from biovia_pipeline.experiment_query import experiment_query",
            category="query"
        ),

    "custom filter":
        RepositoryComponent(
            plp_name="Custom Filter",
            python_module=
                "biovia_pipeline.custom_filter",
            python_function=
                "custom_filter",
            import_statement=
                "from biovia_pipeline.custom_filter import custom_filter",
            category="filter"
        ),

    "custom manipulator":
        RepositoryComponent(
            plp_name="Custom Manipulator",
            python_module=
                "biovia_pipeline.custom_manipulator",
            python_function=
                "custom_manipulator",
            import_statement=
                "from biovia_pipeline.custom_manipulator import custom_manipulator",
            category="transformer"
        ),

    "add pdf section":
        RepositoryComponent(
            plp_name="Add PDF Section",
            python_module=
                "biovia_pipeline.add_pdf_section",
            python_function=
                "add_pdf_section",
            import_statement=
                "from biovia_pipeline.add_pdf_section import add_pdf_section",
            category="eln"
        ),

    "add excel section":
        RepositoryComponent(
            plp_name="Add Excel Section",
            python_module=
                "biovia_pipeline.add_excel_section",
            python_function=
                "add_excel_section",
            import_statement=
                "from biovia_pipeline.add_excel_section import add_excel_section",
            category="eln"
        ),

    "add word section":
        RepositoryComponent(
            plp_name="Add Word Section",
            python_module=
                "biovia_pipeline.add_word_section",
            python_function=
                "add_word_section",
            import_statement=
                "from biovia_pipeline.add_word_section import add_word_section",
            category="eln"
        ),

    "add image section":
        RepositoryComponent(
            plp_name="Add Image Section",
            python_module=
                "biovia_pipeline.add_image_section",
            python_function=
                "add_image_section",
            import_statement=
                "from biovia_pipeline.add_image_section import add_image_section",
            category="eln"
        ),

    "add powerpoint section":
        RepositoryComponent(
            plp_name="Add PowerPoint Section",
            python_module=
                "biovia_pipeline.add_powerpoint_section",
            python_function=
                "add_powerpoint_section",
            import_statement=
                "from biovia_pipeline.add_powerpoint_section import add_powerpoint_section",
            category="eln"
        ),

    "extract sections":
        RepositoryComponent(
            plp_name="Extract Sections",
            python_module=
                "biovia_pipeline.extract_sections",
            python_function=
                "extract_sections",
            import_statement=
                "from biovia_pipeline.extract_sections import extract_sections",
            category="eln"
        )
}


# ============================================================
# BINDING ENGINE
# ============================================================

class RepositoryComponentBindingEngine:

    def bind(
        self,
        protocol_analysis
    ) -> BindingResult:

        bound = []

        missing = []

        for node in protocol_analysis.nodes:

            repository_component = (
                self._find_match(
                    node.visual_name
                )
            )

            if repository_component:

                bound.append(

                    BoundComponent(

                        component_name=
                            node.visual_name,

                        repository_component=
                            repository_component,

                        confidence=1.0
                    )
                )

            else:

                missing.append(
                    node.visual_name
                )

        return BindingResult(

            bound_components=
                bound,

            missing_components=
                missing
        )

    # ========================================================
    # MATCHING
    # ========================================================

    def _find_match(
        self,
        component_name: str
    ):

        normalized = (
            component_name
            .strip()
            .lower()
        )

        #
        # Exact Match
        #
        if normalized in COMPONENT_REPOSITORY:

            return COMPONENT_REPOSITORY[
                normalized
            ]

        #
        # Partial Match
        #
        for key in COMPONENT_REPOSITORY:

            if key in normalized:

                return COMPONENT_REPOSITORY[
                    key
                ]

        return None

    # ========================================================
    # HELPERS
    # ========================================================

    def get_imports(
        self,
        binding_result: BindingResult
    ):

        imports = set()

        for component in (
            binding_result.bound_components
        ):

            imports.add(

                component
                    .repository_component
                    .import_statement
            )

        return sorted(imports)

    def get_workflow_calls(
        self,
        binding_result: BindingResult
    ):

        calls = []

        for component in (
            binding_result.bound_components
        ):

            calls.append(

                f"{component.repository_component.python_function}()"
            )

        return calls

    # ========================================================
    # DEBUG
    # ========================================================

    def print_binding_report(
        self,
        result: BindingResult
    ):

        print()

        print("=" * 70)

        print(
            "COMPONENT BINDING REPORT"
        )

        print("=" * 70)

        print()

        print(
            f"Mapped: "
            f"{len(result.bound_components)}"
        )

        print(
            f"Missing: "
            f"{len(result.missing_components)}"
        )

        print()

        for bound in (
            result.bound_components
        ):

            print(
                f"{bound.component_name}"
                f" -> "
                f"{bound.repository_component.python_module}"
            )

        if result.missing_components:

            print()

            print("Missing:")

            for comp in (
                result.missing_components
            ):

                print(
                    f"  - {comp}"
                )