# business_flow_interpreter.py

from dataclasses import dataclass, field
from typing import List


# ============================================================
# MODELS
# ============================================================

@dataclass
class BusinessActor:

    name: str

    role: str


@dataclass
class BusinessStep:

    step_number: int

    step_name: str

    action_type: str

    confidence: float = 1.0


@dataclass
class BusinessWorkflow:

    workflow_name: str

    business_goal: str

    actors: List[BusinessActor]

    workflow_steps: List[BusinessStep]

    inputs: List[str]

    outputs: List[str]


# ============================================================
# INTERPRETER
# ============================================================

class BusinessFlowInterpreter:

    def interpret(
        self,
        description: str
    ) -> BusinessWorkflow:

        text = (
            description
            .strip()
            .lower()
        )

        actors = self._extract_actors(
            text
        )

        steps = self._extract_steps(
            text
        )

        inputs = self._detect_inputs(
            text
        )

        outputs = self._detect_outputs(
            text
        )

        workflow_name = (
            self._infer_workflow_name(
                text
            )
        )

        business_goal = (
            self._infer_business_goal(
                text
            )
        )

        return BusinessWorkflow(

            workflow_name=
                workflow_name,

            business_goal=
                business_goal,

            actors=
                actors,

            workflow_steps=
                steps,

            inputs=
                inputs,

            outputs=
                outputs
        )

    # ========================================================
    # ACTORS
    # ========================================================

    def _extract_actors(
        self,
        text: str
    ):

        actors = []

        if (
            "user"
            in text
        ):

            actors.append(

                BusinessActor(
                    name="User",
                    role="Operator"
                )
            )

        if (
            "scientist"
            in text
        ):

            actors.append(

                BusinessActor(
                    name="Scientist",
                    role="Business User"
                )
            )

        if (
            "eln"
            in text
            or
            "notebook"
            in text
        ):

            actors.append(

                BusinessActor(
                    name="Notebook",
                    role="External System"
                )
            )

        if (
            "azure"
            in text
        ):

            actors.append(

                BusinessActor(
                    name="Azure File Share",
                    role="Storage"
                )
            )

        return actors

    # ========================================================
    # STEPS
    # ========================================================

    def _extract_steps(
        self,
        text: str
    ):

        steps = []

        current_step = 1

        if (
            "upload"
            in text
        ):

            steps.append(

                BusinessStep(
                    step_number=
                        current_step,

                    step_name=
                        "Upload XML",

                    action_type=
                        "UPLOAD"
                )
            )

            current_step += 1

        if (
            "parse"
            in text
            or
            "process xml"
            in text
        ):

            steps.append(

                BusinessStep(
                    step_number=
                        current_step,

                    step_name=
                        "Parse XML",

                    action_type=
                        "PROCESS"
                )
            )

            current_step += 1

        if (
            "select"
            in text
        ):

            steps.append(

                BusinessStep(
                    step_number=
                        current_step,

                    step_name=
                        "Select Files",

                    action_type=
                        "SELECTION"
                )
            )

            current_step += 1

        if (
            "download"
            in text
        ):

            steps.append(

                BusinessStep(
                    step_number=
                        current_step,

                    step_name=
                        "Download Files",

                    action_type=
                        "DOWNLOAD"
                )
            )

            current_step += 1

        if (
            "attach"
            in text
            or
            "import"
            in text
        ):

            steps.append(

                BusinessStep(
                    step_number=
                        current_step,

                    step_name=
                        "Attach To ELN",

                    action_type=
                        "IMPORT"
                )
            )

            current_step += 1

        if (
            "delete"
            in text
            or
            "cleanup"
            in text
        ):

            steps.append(

                BusinessStep(
                    step_number=
                        current_step,

                    step_name=
                        "Cleanup Temporary Files",

                    action_type=
                        "CLEANUP"
                )
            )

        return steps

    # ========================================================
    # INPUTS
    # ========================================================

    def _detect_inputs(
        self,
        text: str
    ):

        inputs = []

        if (
            "xml"
            in text
        ):

            inputs.append(
                "xml_file"
            )

        if (
            "experiment"
            in text
        ):

            inputs.append(
                "experiment_number"
            )

        if (
            "file"
            in text
        ):

            inputs.append(
                "selected_files"
            )

        return inputs

    # ========================================================
    # OUTPUTS
    # ========================================================

    def _detect_outputs(
        self,
        text: str
    ):

        outputs = []

        if (
            "eln"
            in text
            or
            "notebook"
            in text
        ):

            outputs.append(
                "notebook_sections"
            )

        if (
            "attached"
            in text
        ):

            outputs.append(
                "attachments"
            )

        return outputs

    # ========================================================
    # WORKFLOW NAME
    # ========================================================

    def _infer_workflow_name(
        self,
        text: str
    ):

        if (
            "xml"
            in text
            and
            "eln"
            in text
        ):

            return (
                "XML To ELN Import Workflow"
            )

        if (
            "notebook"
            in text
        ):

            return (
                "Notebook Import Workflow"
            )

        return (
            "Generated Workflow"
        )

    # ========================================================
    # BUSINESS GOAL
    # ========================================================

    def _infer_business_goal(
        self,
        text: str
    ):

        if (
            "import"
            in text
            and
            "eln"
            in text
        ):

            return (
                "Import external files "
                "into ELN experiments"
            )

        return (
            "Generated business process"
        )

    # ========================================================
    # DEBUG
    # ========================================================

    def print_workflow(
        self,
        workflow: BusinessWorkflow
    ):

        print()

        print("=" * 80)

        print(
            workflow.workflow_name
        )

        print("=" * 80)

        print()

        print(
            "Business Goal:"
        )

        print(
            workflow.business_goal
        )

        print()

        print(
            "Actors:"
        )

        for actor in workflow.actors:

            print(
                f"- {actor.name} "
                f"({actor.role})"
            )

        print()

        print(
            "Workflow Steps:"
        )

        for step in (
            workflow.workflow_steps
        ):

            print(

                f"{step.step_number}. "

                f"{step.step_name}"

                f" ({step.action_type})"
            )

        print()

        print(
            "Inputs:"
        )

        print(
            workflow.inputs
        )

        print()

        print(
            "Outputs:"
        )

        print(
            workflow.outputs
        )

        print()


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    text = '''

    User uploads XML.

    XML is parsed.

    Files are selected.

    Files are downloaded
    from Azure File Share.

    Files are attached
    to ELN experiment.

    Temporary files
    are deleted.
    '''

    interpreter = (
        BusinessFlowInterpreter()
    )

    workflow = (
        interpreter.interpret(
            text
        )
    )

    interpreter.print_workflow(
        workflow
    )