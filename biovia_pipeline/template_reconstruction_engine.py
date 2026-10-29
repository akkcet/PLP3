# template_reconstruction_engine.py

from dataclasses import dataclass, field
from typing import List


@dataclass
class TemplateMatch:

    template_name: str

    confidence: float

    missing_components: List[str]
    template: object


@dataclass
class ReconstructedWorkflow:

    workflow_name: str

    matched_template: str

    confidence: float

    components: List[str]
class TemplateReconstructionEngine:

    def reconstruct(
        self,
        workflow,
        template_catalog
    ):

        matches = self._find_matches(
            workflow,
            template_catalog
        )

        if not matches:

            return ReconstructedWorkflow(

                workflow_name=
                    workflow.workflow_name,

                matched_template=
                    "None",

                confidence=0,

                components=[

                    x.component_name

                    for x in
                    workflow.components
                ]
            )

        best_match = matches[0]

        return ReconstructedWorkflow(

            workflow_name=
                workflow.workflow_name,

            matched_template=
                best_match.template_name,

            confidence=
                best_match.confidence,

            components=
                best_match.template.components
        )
    def _find_matches(
        self,
        workflow,
        template_catalog
    ):

        workflow_components = {

            x.function_name

            for x in
            workflow.components
        }

        candidates = []

        for template in (
            template_catalog.templates
        ):

            template_components = (
                set(
                    template.components
                )
            )

            overlap = len(

                workflow_components
                .intersection(
                    template_components
                )
            )

            score = (

                overlap

                /

                max(
                    len(
                        template_components
                    ),
                    1
                )
            )

            if score > 0:

                candidates.append(

                    TemplateMatch(

                        template_name=
                            template.template_name,

                        confidence=
                            round(
                                score,
                                2
                            ),

                        missing_components=list(

                            template_components
                            -
                            workflow_components
                        ),
                        template=template
                    )
                )

        candidates.sort(

            key=lambda x:
                x.confidence,

            reverse=True
        )

        return candidates
    def print_reconstruction(
        self,
        reconstruction
    ):

        print()

        print("=" * 80)

        print(
            "TEMPLATE RECONSTRUCTION"
        )

        print("=" * 80)

        print()

        print(
            "Workflow:"
        )

        print(
            reconstruction.workflow_name
        )

        print()

        print(
            "Template:"
        )

        print(
            reconstruction.matched_template
        )

        print()

        print(
            "Confidence:"
        )

        print(
            reconstruction.confidence
        )

        print()

        print(
            "Components:"
        )

        for component in (
            reconstruction.components
        ):

            print(
                f" - {component}"
            )