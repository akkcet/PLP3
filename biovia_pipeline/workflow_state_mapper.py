# workflow_state_mapper.py

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class ComponentExecution:

    component_name: str

    function_name: str

    inputs: List[str] = field(
        default_factory=list
    )

    outputs: List[str] = field(
        default_factory=list
    )


@dataclass
class StatefulWorkflow:

    workflow_name: str

    components: List[
        ComponentExecution
    ]


STATE_RULES = {

    "notebook_connection": {

        "inputs": [],

        "outputs": [
            "connection"
        ]
    },

    "experiment_query": {

        "inputs": [
            "connection"
        ],

        "outputs": [
            "experiment"
        ]
    },

    "extract_sections": {

        "inputs": [
            "experiment"
        ],

        "outputs": [
            "sections"
        ]
    },

    "add_pdf_section": {

        "inputs": [
            "connection",
            "experiment",
            "sections"
        ],

        "outputs": [
            "pdf_result"
        ]
    }
}


class WorkflowStateMapper:

    def build(
        self,
        binding_result
    ):

        components = []

        for bound in (
            binding_result
            .bound_components
        ):

            function_name = (
                bound
                .repository_component
                .python_function
            )

            rules = (
                STATE_RULES.get(
                    function_name,
                    {}
                )
            )

            components.append(

                ComponentExecution(

                    component_name=
                        bound.component_name,

                    function_name=
                        function_name,

                    inputs=
                        rules.get(
                            "inputs",
                            []
                        ),

                    outputs=
                        rules.get(
                            "outputs",
                            []
                        )
                )
            )

        return StatefulWorkflow(

            workflow_name=
                "GeneratedWorkflow",

            components=
                components
        )