# wizard_reconstruction_engine.py

from dataclasses import dataclass, field
from typing import List


@dataclass
class WizardStep:

    step_id: str

    step_name: str

    page_title: str

    controls: List[str] = field(
        default_factory=list
    )


@dataclass
class WizardBlueprint:

    workflow_name: str

    steps: List[WizardStep]

    start_step: str


class WizardReconstructionEngine:

    CONTROL_MAPPING = {

        "UPLOAD": [
            "FileUpload",
            "PrimaryButton"
        ],

        "PROCESS": [
            "StatusPanel",
            "PrimaryButton"
        ],

        "SELECTION": [
            "DataGrid",
            "PrimaryButton"
        ],

        "IMPORT": [
            "ProgressBar",
            "StatusPanel"
        ],

        "REVIEW": [
            "DataGrid",
            "PrimaryButton"
        ],

        "COMPLETE": [
            "ImportSummary"
        ]
    }

    def build(
        self,
        workflow_definition
    ) -> WizardBlueprint:

        steps = []

        for index, workflow_step in enumerate(
            workflow_definition.steps,
            start=1
        ):

            controls = self.CONTROL_MAPPING.get(
                workflow_step.action_type,
                []
            )

            steps.append(

                WizardStep(

                    step_id=f"step_{index}",

                    step_name=
                        workflow_step.name,

                    page_title=
                        workflow_step.name,

                    controls=
                        controls
                )
            )

        return WizardBlueprint(

            workflow_name=
                workflow_definition.workflow_name,

            steps=steps,

            start_step=
                steps[0].step_id
                if steps
                else ""
        )

    def print_wizard(
        self,
        wizard: WizardBlueprint
    ):

        print()
        print("=" * 80)
        print(wizard.workflow_name)
        print("=" * 80)

        for step in wizard.steps:

            print()

            print(
                f"{step.step_id}"
            )

            print(
                f"Title: {step.page_title}"
            )

            print(
                f"Controls: {step.controls}"
            )