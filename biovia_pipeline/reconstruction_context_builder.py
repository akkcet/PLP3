# reconstruction_context_builder.py

from dataclasses import dataclass
from typing import Optional


@dataclass
class ReconstructionContext:

    #
    # Inputs
    #

    protocol_analysis: object

    screenshot_analysis: object

    business_workflow: object

    #
    # Repository Mapping
    #

    binding_result: object

    stateful_workflow: object

    #
    # Blueprint
    #

    application_blueprint: object


class ReconstructionContextBuilder:

    def build(
        self,
        protocol_analysis,
        screenshot_analysis,
        business_workflow,
        binding_result,
        stateful_workflow,
        application_blueprint
    ):

        return ReconstructionContext(

            protocol_analysis=
                protocol_analysis,

            screenshot_analysis=
                screenshot_analysis,

            business_workflow=
                business_workflow,

            binding_result=
                binding_result,

            stateful_workflow=
                stateful_workflow,

            application_blueprint=
                application_blueprint
        )