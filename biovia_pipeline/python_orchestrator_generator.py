# python_orchestrator_generator.py

from pathlib import Path


class PythonOrchestratorGenerator:

    COMPONENT_IMPORTS = {

        "Notebook Connection":
"""
from biovia_pipeline.notebook_connection import notebook_connection
""",

        "Experiment Query":
"""
from biovia_pipeline.experiment_query import experiment_query
""",

        "Add PDF Section":
"""
from biovia_pipeline.add_pdf_section import add_pdf_section
""",

        "Add Excel Section":
"""
from biovia_pipeline.add_excel_section import add_excel_section
""",

        "Custom Filter":
"""
from biovia_pipeline.custom_filter import custom_filter
""",

        "Custom Manipulator":
"""
from biovia_pipeline.custom_manipulator import custom_manipulator
""",
    }

    def build_workflow(
        self,
        workflow
    ):

        imports = []

        steps = []

        for comp in workflow.components:

            for key, value in (
                self.COMPONENT_IMPORTS
                .items()
            ):

                if key.lower() in comp.lower():

                    imports.append(
                        value
                    )

                    func = (
                        key.lower()
                           .replace(" ", "_")
                    )

                    steps.append(
                        f"        # {key}"
                    )

        imports_text = "\n".join(
            set(imports)
        )

        steps_text = "\n".join(
            steps
        )

        return f"""
{imports_text}


class {workflow.workflow_name}:

    def execute(self):

{steps_text}

        print(
            "Workflow executed"
        )
"""

    def generate(
        self,
        blueprint,
        output_dir
    ):

        output = Path(output_dir)

        output.mkdir(
            parents=True,
            exist_ok=True
        )

        for workflow in (
            blueprint.workflows
        ):

            code = (
                self.build_workflow(
                    workflow
                )
            )

            file_name = (
                workflow.workflow_name
                .lower()
            )

            (
                output /
                f"{file_name}.py"
            ).write_text(code)