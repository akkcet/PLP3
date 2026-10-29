# component_parameter_to_workflow_mapper.py

from dataclasses import dataclass, field
from typing import List


@dataclass
class WorkflowParameterBinding:

    source_component: str

    source_output: str

    target_component: str

    target_parameter: str

    confidence: float = 1.0


@dataclass
class WorkflowBindingMap:

    bindings: List[
        WorkflowParameterBinding
    ] = field(
        default_factory=list
    )


class ComponentParameterToWorkflowMapper:

    def build(
        self,
        workflow
    ) -> WorkflowBindingMap:

        binding_map = (
            WorkflowBindingMap()
        )

        #
        # Register outputs
        #
        state_producers = {}

        for component in (
            workflow.components
        ):

            for output in (
                component.outputs
            ):

                state_producers[
                    output
                ] = (
                    component.component_name
                )

        #
        # Build dependencies
        #
        for component in (
            workflow.components
        ):

            for required_input in (
                component.inputs
            ):

                if (
                    required_input
                    not in state_producers
                ):

                    continue

                binding_map.bindings.append(

                    WorkflowParameterBinding(

                        source_component=
                            state_producers[
                                required_input
                            ],

                        source_output=
                            required_input,

                        target_component=
                            component.component_name,

                        target_parameter=
                            required_input,

                        confidence=1.0
                    )
                )

        return binding_map