# pilotscript_reconstruction_engine.py

from dataclasses import dataclass, field
from typing import List, Dict, Optional

from biovia_pipeline.pilotscript_parser import (
    PilotScriptParser
)


# ============================================================
# MODELS
# ============================================================

@dataclass
class PilotScriptComponent:

    component_name: str

    component_type: str

    expression: str

    source_xml_id: Optional[str] = None


@dataclass
class ReconstructedPython:

    component_name: str

    component_type: str

    original_expression: str

    generated_code: str

    success: bool

    error: Optional[str] = None


@dataclass
class ReconstructionResult:

    reconstructed: List[
        ReconstructedPython
    ] = field(
        default_factory=list
    )

    failed: List[
        ReconstructedPython
    ] = field(
        default_factory=list
    )


# ============================================================
# ENGINE
# ============================================================

class PilotScriptReconstructionEngine:

    def reconstruct(
        self,
        component: PilotScriptComponent
    ) -> ReconstructedPython:

        try:

            parser = PilotScriptParser(
                component.expression
            )

            generated_code = (
                parser.transpile_to_python()
            )

            return ReconstructedPython(

                component_name=
                    component.component_name,

                component_type=
                    component.component_type,

                original_expression=
                    component.expression,

                generated_code=
                    generated_code,

                success=True
            )

        except Exception as ex:

            return ReconstructedPython(

                component_name=
                    component.component_name,

                component_type=
                    component.component_type,

                original_expression=
                    component.expression,

                generated_code="",

                success=False,

                error=str(ex)
            )

    # ========================================================
    # BATCH RECONSTRUCTION
    # ========================================================

    def reconstruct_all(
        self,
        components: List[PilotScriptComponent]
    ) -> ReconstructionResult:

        result = ReconstructionResult()

        for component in components:

            reconstructed = (
                self.reconstruct(
                    component
                )
            )

            if reconstructed.success:

                result.reconstructed.append(
                    reconstructed
                )

            else:

                result.failed.append(
                    reconstructed
                )

        return result

    # ========================================================
    # XML EXTRACTION
    # ========================================================

    def extract_from_protocol(
        self,
        protocol_analysis
    ) -> List[PilotScriptComponent]:

        components = []

        for node in protocol_analysis.nodes:

            parameters = getattr(
                node,
                "parameters",
                {}
            )

            expression = None

            #
            # Common PLP parameter names
            #
            expression_keys = [

                "Expression",

                "PilotScript",

                "Filter Expression",

                "Custom Expression",

                "Script",

                "Condition"
            ]

            for key in expression_keys:

                if key in parameters:

                    expression = (
                        parameters[key]
                    )

                    break

            if not expression:
                continue

            components.append(

                PilotScriptComponent(

                    component_name=
                        node.visual_name,

                    component_type=
                        node.visual_name,

                    expression=
                        str(expression),

                    source_xml_id=
                        getattr(
                            node,
                            "component_id",
                            None
                        )
                )
            )

        return components

    # ========================================================
    # WORKFLOW CODE OUTPUT
    # ========================================================

    def generate_python_module(
        self,
        reconstructed_components
    ):

        sections = []

        sections.append(
            "# Auto Generated PilotScript Reconstructions"
        )

        sections.append("")

        for component in reconstructed_components:

            sections.append(
                f"# Component: "
                f"{component.component_name}"
            )

            sections.append("")

            sections.append(
                component.generated_code
            )

            sections.append("")
            sections.append(
                "#" * 60
            )
            sections.append("")

        return "\n".join(
            sections
        )

    # ========================================================
    # REPORTING
    # ========================================================

    def print_report(
        self,
        result: ReconstructionResult
    ):

        print()

        print("=" * 80)

        print(
            "PILOTSCRIPT RECONSTRUCTION REPORT"
        )

        print("=" * 80)

        print()

        print(
            f"Successful : "
            f"{len(result.reconstructed)}"
        )

        print(
            f"Failed     : "
            f"{len(result.failed)}"
        )

        print()

        if result.failed:

            print(
                "FAILED COMPONENTS"
            )

            print("-" * 80)

            for component in result.failed:

                print()

                print(
                    component.component_name
                )

                print(
                    component.error
                )

    # ========================================================
    # PYTHON SNIPPET
    # ========================================================

    def to_workflow_snippet(
        self,
        reconstructed: ReconstructedPython
    ):

        return f"""
# {reconstructed.componentode}
"""