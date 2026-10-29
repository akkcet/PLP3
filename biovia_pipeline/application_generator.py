# application_generator.py

import json

from pathlib import Path
from datetime import datetime

from biovia_pipeline.react_app_generator_v4 import (
    ReactAppGeneratorV4
)

from biovia_pipeline.backend_workflow_generator_v2 import (
    BackendWorkflowGeneratorV2
)

from biovia_pipeline.api_contract_generator import (
    APIContractGenerator
)

from biovia_pipeline.fastapi_generator import (
    FastAPIGenerator
)

from biovia_pipeline.react_service_generator import (
    ReactServiceGenerator
)


class ApplicationGenerator:

    def __init__(self):

        self.react_generator = (
            ReactAppGeneratorV4()
        )

        self.backend_generator = (
            BackendWorkflowGeneratorV2()
        )

        self.api_generator = (
            APIContractGenerator()
        )

        self.fastapi_generator = (
            FastAPIGenerator()
        )

        self.react_service_generator = (
            ReactServiceGenerator()
        )

    # =====================================================
    # ENTRYPOINT
    # =====================================================

    def generate(
        self,
        pipeline_result,
        output_dir="generated_apps"
    ):

        app_name = (
            self._sanitize_name(
                pipeline_result
                .application_blueprint
                .app_name
            )
        )

        app_root = (
            Path(output_dir)
            / app_name
        )

        self._create_structure(
            app_root
        )

        self._generate_metadata(
            pipeline_result,
            app_root
        )

        self._generate_specs(
            pipeline_result,
            app_root
        )

        self._generate_frontend(
            pipeline_result,
            app_root
        )

        self._generate_backend(
            pipeline_result,
            app_root
        )

        return app_root

    # =====================================================
    # STRUCTURE
    # =====================================================

    def _create_structure(
        self,
        app_root
    ):

        folders = [

            "frontend",

            "backend",

            "generated_specs",

            "screenshots",

            "assets"
        ]

        for folder in folders:

            (
                app_root
                / folder
            ).mkdir(

                parents=True,

                exist_ok=True
            )

    # =====================================================
    # METADATA
    # =====================================================

    def _generate_metadata(
        self,
        result,
        app_root
    ):

        metadata = {

            "app_name":
                result.application_blueprint.app_name,

            "generated":
                datetime.utcnow().isoformat(),

            "components":

                len(

                    result.binding_result
                    .bound_components

                ),

            "missing_components":

                len(

                    result.binding_result
                    .missing_components

                ),

            "pages":

                len(

                    result
                    .application_blueprint
                    .pages

                )
        }

        (
            app_root
            / "metadata.json"
        ).write_text(

            json.dumps(

                metadata,

                indent=4

            ),

            encoding="utf-8"
        )

    # =====================================================
    # SPECS
    # =====================================================

    def _generate_specs(
        self,
        result,
        app_root
    ):

        specs_dir = (
            app_root
            / "generated_specs"
        )

        #
        # Blueprint
        #

        blueprint_file = (

            specs_dir
            / "application_blueprint.json"

        )

        blueprint_data = {

            "app_name":

                result.application_blueprint.app_name,

            "pages":

                [

                    page.page_name

                    for page in
                    result.application_blueprint.pages

                ]
        }

        blueprint_file.write_text(

            json.dumps(
                blueprint_data,
                indent=4
            ),

            encoding="utf-8"
        )

        #
        # Workflow
        #

        workflow_file = (

            specs_dir
            / "workflow.json"

        )

        # workflow_data = {

        #     "workflow_name":

        #         result.stateful_workflow.workflow_name,

        #     "components":

        #         [

        #             c.component_name

        #             for c in
        #             result.stateful_workflow.components

        #         ]
        # }
        if result.stateful_workflow:

            workflow_data = {

                "workflow_name":

                    result.stateful_workflow.workflow_name,

                "components":

                    [
                        c.component_name
                        for c in
                        result.stateful_workflow.components
                    ]
            }

        else:

            workflow_data = {

                "workflow_name":
                    "Generated Workflow",

                "components":
                    []
            }
        workflow_file.write_text(

            json.dumps(
                workflow_data,
                indent=4
            ),

            encoding="utf-8"
        )

    # =====================================================
    # FRONTEND
    # =====================================================

    def _generate_frontend(
        self,
        result,
        app_root
    ):

        frontend_dir = (
            app_root
            / "frontend"
        )

        self.react_generator.generate(

            result.application_blueprint,

            frontend_dir
        )

        # api_contracts = (

        #     self.api_generator.generate(

        #         result.workflow_graph

        #     )

        # )
        api_contracts = None

        # self.react_service_generator.generate(

        #     api_contracts,

        #     frontend_dir
        #     / "src/services"
        # )
        if api_contracts:
            
            self.react_service_generator.generate(
            
            api_contracts,
            
            frontend_dir
            / "src/services"
            )
    # =====================================================
    # BACKEND
    # =====================================================

    def _generate_backend(
        self,
        result,
        app_root
    ):

        backend_dir = (
            app_root
            / "backend"
        )

        backend_dir.mkdir(
            exist_ok=True
        )

        #
        # Workflow
        #

        # self.backend_generator.generate(

        #     result.stateful_workflow,

        #     result.binding_result,

        #     backend_dir
        # )
        if result.stateful_workflow:

            self.backend_generator.generate(
                result.stateful_workflow,
                result.binding_result,
                backend_dir
            )

        #
        # API
        #

        # api_contracts = (

        #     self.api_generator.generate(

        #         result.workflow_graph

        #     )

        # )
        api_contracts = None
        # self.fastapi_generator.generate(

        #     api_contracts,

        #     backend_dir
        # )
        if api_contracts:
            
            self.fastapi_generator.generate(
            
            api_contracts,
            
            backend_dir
            )

    # =====================================================
    # HELPERS
    # =====================================================

    def _sanitize_name(
        self,
        value
    ):

        if not value:

            return "GeneratedApplication"

        return (

            value

            .replace(" ", "_")

            .replace("-", "_")

        )