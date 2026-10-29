# backend_workflow_generator.py

from pathlib import Path


class BackendWorkflowGenerator:

    # =====================================================
    # IMPORT REGISTRY
    # =====================================================

    FUNCTION_IMPORTS = {

        "notebook_connection":
            "from biovia_pipeline.notebook_connection import notebook_connection",

        "experiment_query":
            "from biovia_pipeline.experiment_query import experiment_query",

        "custom_filter":
            "from biovia_pipeline.custom_filter import custom_filter",

        "custom_manipulator":
            "from biovia_pipeline.custom_manipulator import custom_manipulator",

        "add_pdf_section":
            "from biovia_pipeline.add_pdf_section import add_pdf_section",

        "add_excel_section":
            "from biovia_pipeline.add_excel_section import add_excel_section",

        "add_word_section":
            "from biovia_pipeline.add_word_section import add_word_section",

        "add_image_section":
            "from biovia_pipeline.add_image_section import add_image_section",

        "add_powerpoint_section":
            "from biovia_pipeline.add_powerpoint_section import add_powerpoint_section",

        "extract_sections":
            "from biovia_pipeline.extract_sections import extract_sections",
    }

    # =====================================================
    # MAIN GENERATOR
    # =====================================================

    def generate(
        self,
        workflow_graph,
        output_dir: str
    ):

        root = Path(output_dir)

        root.mkdir(
            parents=True,
            exist_ok=True
        )

        content = self._build_workflow_file(
            workflow_graph
        )

        workflow_name = (
            workflow_graph
            .workflow_name
            .replace(" ", "_")
            .lower()
        )

        (
            root
            /
            f"{workflow_name}.py"
        ).write_text(
            content,
            encoding="utf-8"
        )

    # =====================================================
    # FILE GENERATION
    # =====================================================

    def _build_workflow_file(
        self,
        graph
    ):

        imports = self._generate_imports(
            graph
        )

        execute_body = self._generate_steps(
            graph
        )

        class_name = (
            graph.workflow_name
                 .replace(" ", "")
        )

        return f'''
{imports}


class {class_name}:

    def __init__(self):

        self.context = {{}}

    def execute(self):

{execute_body}

        return self.context


if __name__ == "__main__":

    workflow = {class_name}()

    result = workflow.execute()

    print(result)
'''
    # =====================================================
    # IMPORTS
    # =====================================================

    def _generate_imports(
        self,
        graph
    ):

        imports = set()

        for node in graph.nodes:

            function_name = (
                node.python_function
            )

            if function_name in self.FUNCTION_IMPORTS:

                imports.add(

                    self.FUNCTION_IMPORTS[
                        function_name
                    ]
                )

        imports.add("import json")

        return "\n".join(
            sorted(imports)
        )

    # =====================================================
    # STEP GENERATION
    # =====================================================

    def _generate_steps(
        self,
        graph
    ):

        steps = []

        for node in graph.nodes:

            steps.extend(

                self._generate_node(
                    node
                )

            )

        return "\n".join(steps)

    # =====================================================
    # NODE GENERATION
    # =====================================================

    def _generate_node(
        self,
        node
    ):

        fn = (
            node.python_function
        )

        steps = []

        steps.append(
            f"        # {node.component_name}"
        )

        if fn == "notebook_connection":

            steps.extend([

"""
        self.context["connection"] = notebook_connection(
            server_url="https://notebook.unilever.com",
            authentication_method=
                "Use Username and Password Parameters",
            username="username",
            password="password"
        )
"""
            ])

        elif fn == "experiment_query":

            steps.extend([

"""
        self.context["experiment"] = experiment_query(
            connection=
                self.context.get(
                    "connection"
                ),
            filter_by=
                "Experiment Number",
            filter_type=
                "Equals",
            filter_value=
                "EXP-TEST-001"
        )
"""
            ])

        elif fn == "custom_filter":

            steps.extend([

"""
        self.context["filter_result"] = custom_filter(
            self.context
        )
"""
            ])

        elif fn == "custom_manipulator":

            steps.extend([

"""
        self.context["manipulated"] = custom_manipulator(
            self.context
        )
"""
            ])

        elif fn == "extract_sections":

            steps.extend([

"""
        self.context["sections"] = extract_sections(
            self.context
        )
"""
            ])

        elif fn == "add_pdf_section":

            steps.extend([

"""
        add_pdf_section(
            self.context
        )
"""
            ])

        elif fn == "add_excel_section":

            steps.extend([

"""
        add_excel_section(
            self.context
        )
"""
            ])

        elif fn == "add_word_section":

            steps.extend([

"""
        add_word_section(
            self.context
        )
"""
            ])

        elif fn == "add_image_section":

            steps.extend([

"""
        add_image_section(
            self.context
        )
"""
            ])

        elif fn == "add_powerpoint_section":

            steps.extend([

"""
        add_powerpoint_section(
            self.context
        )
"""
            ])

        else:

            steps.extend([

f"""
        # TODO:
        # Implement {node.component_name}
"""
            ])

        steps.append("")

        return steps