# application_runtime_builder.py

from pathlib import Path


class ApplicationRuntimeBuilder:

    def __init__(self):

        self.generated_files = []

    # =====================================================
    # MAIN BUILD
    # =====================================================

    def build(
        self,
        reconstruction_context,
        frontend_generator,
        backend_generator,
        scaffolder,
        component_library_generator
    ):

        blueprint = (
            reconstruction_context
            .application_blueprint
        )

        output_root = Path(

            reconstruction_context
            .output_dir

        )

        output_root.mkdir(
            parents=True,
            exist_ok=True
        )

        #
        # Project Scaffold
        #
        scaffolder.generate(
            blueprint,
            str(output_root)
        )

        #
        # Component Library
        #
        component_library_generator.generate(

            str(
                output_root
                /
                "frontend"
                /
                "src"
                /
                "components"
            )
        )

        #
        # React Application
        #
        # print()
        # print("RUNNING DETERMINISTIC REACT GENERATOR")
        # print()
        # frontend_generator.generate(

        #     blueprint,

        #     str(
        #         output_root
        #         /
        #         "frontend"
        #     )
        # )

        #
        # Backend Application
        #
        # backend_generator.generate(

        #     reconstruction_context
        #     .stateful_workflow,

        #     reconstruction_context
        #     .binding_result,

        #     reconstruction_context
        #     .backend_parameters,

        #     reconstruction_context
        #     .workflow_bindings,

        #     str(
        #         output_root
        #         /
        #         "backend"
        #         /
        #         "workflows"
        #     )
        # )

        #
        # Runtime files
        #
        # self._generate_backend_app(
        #     output_root
        # )

        # self._generate_frontend_app(
        #     output_root
        # )

        return True

    # =====================================================
    # BACKEND APP
    # =====================================================

    def _generate_backend_app(
        self,
        root
    ):

        content = '''
from fastapi import FastAPI

app = FastAPI()


@app.get("/health")
def health():

    return {
        "status": "ok"
    }
'''

        path = (
            root
            /
            "backend"
            /
            "app.py"
        )

        path.write_text(
            content,
            encoding="utf-8"
        )

    # =====================================================
    # FRONTEND APP
    # =====================================================

    def _generate_frontend_app(
        self,
        root
    ):

        content = '''
import React from "react";

import AppRoutes
from "./routes/AppRoutes";

export default function App() {

    return (

        <AppRoutes />

    );
}
'''

        path = (
            root
            /
            "frontend"
            /
            "src"
            /
            "App.tsx"
        )

        path.write_text(
            content,
            encoding="utf-8"
        )

    # =====================================================
    # REPORT
    # =====================================================

    def build_report(
        self,
        context
    ):

        return {

            "application":
                context
                .application_blueprint
                .app_name,

            "pages":
                len(
                    context
                    .application_blueprint
                    .pages
                ),

            "components":

                len(
                    context
                    .binding_result
                    .bound_components
                ),

            "missing":

                len(
                    context
                    .binding_result
                    .missing_components
                ),

            "workflow":

                context
                .stateful_workflow
                .workflow_name
        }