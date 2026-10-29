# protocol_to_blueprint_pipeline.py

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from biovia_pipeline.component_metadata_registry import (
    ComponentMetadataRegistry
)

from biovia_pipeline.component_parameter_resolver import (
    ComponentParameterResolver
)

from biovia_pipeline.repository_component_binding_engine import (
    RepositoryComponentBindingEngine
)

from biovia_pipeline.workflow_component_type_detector import (
    WorkflowComponentTypeDetector
)

from biovia_pipeline.workflow_label_extractor import (
    WorkflowLabelExtractor
)

from biovia_pipeline.workflow_state_mapper import (
    WorkflowStateMapper
)

from biovia_pipeline.application_blueprint_builder import (
    ApplicationBlueprintBuilder
)

from biovia_pipeline.screen_flow_builder import (
    ScreenFlowBuilder
)


# ============================================================
# RESULT
# ============================================================

@dataclass
class PipelineResult:

    protocol_analysis: object

    metadata_registry: object

    parameter_result: object

    binding_result: object

    workflow_definition: object

    workflow_graph: object

    stateful_workflow: object

    application_blueprint: object


# ============================================================
# PIPELINE
# ============================================================

class ProtocolToBlueprintPipeline:

    def __init__(self):

        self.registry = (
            ComponentMetadataRegistry()
        )

        self.parameter_resolver = (
            ComponentParameterResolver()
        )

        self.binding_engine = (
            RepositoryComponentBindingEngine()
        )

        self.component_detector = (
            WorkflowComponentTypeDetector()
        )

        self.workflow_extractor = (
            WorkflowLabelExtractor()
        )

        self.state_mapper = (
            WorkflowStateMapper()
        )

        self.blueprint_builder = (
            ApplicationBlueprintBuilder()
        )

        self.screen_flow_builder = (
            ScreenFlowBuilder()
        )

    # ========================================================
    # MAIN ENTRY
    # ========================================================

    def run(

        self,

        protocol_analysis,

        screenshot_labels: Optional[
            List[str]
        ] = None,

        screen_analysis=None

    ) -> PipelineResult:

        #
        # Step 1
        # Load repository metadata
        #
        self.registry.load_repository()

        #
        # Step 2
        # Resolve parameters
        #
        parameter_result = (

            self.parameter_resolver.resolve(
                protocol_analysis
            )

        )

        #
        # Step 3
        # Bind components
        #
        binding_result = (

            self.binding_engine.bind(
                protocol_analysis
            )

        )

        #
        # Step 4
        # Discover workflow
        #
        workflow_definition = (

            self.workflow_extractor.extract(

                screenshot_labels
                or []

            )

        )

        #
        # Step 5
        # Screen Flow
        #
        workflow_graph = (

            self.screen_flow_builder.build(

                protocol_analysis,

                screen_analysis

            )

        )

        #
        # Step 6
        # State Mapping
        #
        # stateful_workflow = (

        #     self.state_mapper.build(
        #         workflow_graph
        #     )

        # )
        stateful_workflow = None

        #
        # Step 7
        # Application Blueprint
        #
        application_blueprint = (

            self.blueprint_builder.build(

                protocol_analysis,

                workflow_graph

            )

        )

        return PipelineResult(

            protocol_analysis=
                protocol_analysis,

            metadata_registry=
                self.registry,

            parameter_result=
                parameter_result,

            binding_result=
                binding_result,

            workflow_definition=
                workflow_definition,

            workflow_graph=
                workflow_graph,

            stateful_workflow=
                stateful_workflow,

            application_blueprint=
                application_blueprint
        )

    # ========================================================
    # REPORT
    # ========================================================

    def print_report(
        self,
        result: PipelineResult
    ):

        print()

        print("=" * 80)
        print("PROTOCOL RECONSTRUCTION PIPELINE")
        print("=" * 80)

        print()

        print(
            f"Repository Components: "
            f"{len(result.metadata_registry.components)}"
        )

        print(
            f"Bound Components: "
            f"{len(result.binding_result.bound_components)}"
        )

        print(
            f"Missing Components: "
            f"{len(result.binding_result.missing_components)}"
        )

        print()

        print(
            f"Screens: "
            f"{len(result.application_blueprint.pages)}"
        )

        print()

        print(
            f"Workflows: "
            f"{len(result.application_blueprint.workflows)}"
        )

        print()

    # ========================================================
    # DEBUG
    # ========================================================

    def print_component_summary(
        self,
        protocol_analysis
    ):

        print()

        print("=" * 80)
        print("COMPONENT CLASSIFICATION")
        print("=" * 80)

        print()

        names = [

            node.visual_name

            for node in protocol_analysis.nodes
        ]

        self.component_detector.print_report(
            names
        )