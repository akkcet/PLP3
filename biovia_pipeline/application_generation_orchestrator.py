# application_generation_orchestrator.py

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


# ============================================================
# PIPELINE
# ============================================================

from biovia_pipeline.protocol_to_blueprint_pipeline import (
    ProtocolToBlueprintPipeline
)

from biovia_pipeline.application_generator import (
    ApplicationGenerator
)

from biovia_pipeline.wizard_reconstruction_engine import (
    WizardReconstructionEngine
)

from biovia_pipeline.screenshot_ocr_engine import (
    ScreenshotOCREngine
)

from biovia_pipeline.screenshot_label_extractor import (
    ScreenshotLabelExtractor
)

from biovia_pipeline.react_app_generator_v5 import (
    ReactAppGeneratorV5
)

from biovia_pipeline.fastapi_application_generator import (
    FastAPIApplicationGenerator
)


# ============================================================
# RESULT
# ============================================================

@dataclass
class GeneratedApplication:

    application_name: str

    output_path: str

    frontend_path: str

    backend_path: str

    screenshots_processed: int

    components_mapped: int

    components_missing: int


# ============================================================
# ORCHESTRATOR
# ============================================================

class ApplicationGenerationOrchestrator:

    def __init__(self):

        self.pipeline = (
            ProtocolToBlueprintPipeline()
        )

        self.application_generator = (
            ApplicationGenerator()
        )

        self.wizard_engine = (
            WizardReconstructionEngine()
        )

        self.ocr_engine = (
            ScreenshotOCREngine()
        )

        self.label_extractor = (
            ScreenshotLabelExtractor()
        )

        self.react_generator = (
            ReactAppGeneratorV5()
        )

        self.fastapi_generator = (
            FastAPIApplicationGenerator()
        )

    # ========================================================
    # MAIN ENTRY
    # ========================================================

    def generate_application(

        self,

        protocol_analysis,

        screenshots: Optional[
            List[str]
        ] = None,

        output_root: str =
            "generated_apps"

    ) -> GeneratedApplication:

        screenshots = (
            screenshots or []
        )

        #
        # STEP 1
        # OCR + LABEL EXTRACTION
        #
        screenshot_labels = (
            self._process_screenshots(
                screenshots
            )
        )

        #
        # STEP 2
        # BUILD PIPELINE RESULT
        #
        pipeline_result = (

            self.pipeline.run(

                protocol_analysis=
                    protocol_analysis,

                screenshot_labels=
                    self._flatten_labels(
                        screenshot_labels
                    )
            )
        )

        #
        # STEP 3
        # GENERATE APP STRUCTURE
        #
        app_root = (

            self.application_generator.generate(

                pipeline_result,

                output_root

            )

        )

        #
        # STEP 4
        # BUILD WIZARD
        #
        wizard = (

            self.wizard_engine.build(

                pipeline_result
                .workflow_definition

            )

        )

        #
        # STEP 5
        # ENHANCED REACT
        #
        frontend_dir = (

            Path(app_root)

            / "frontend"

        )

        self.react_generator.generate(

            wizard,

            screenshot_labels,

            frontend_dir

        )

        #
        # STEP 6
        # FASTAPI APP
        #
        backend_dir = (

            Path(app_root)

            / "backend"

        )

        # self.fastapi_generator.generate(

        #     pipeline_result
        #     .workflow_graph,

        #     backend_dir

        # )

        return GeneratedApplication(

            application_name=

                pipeline_result
                .application_blueprint
                .app_name,

            output_path=
                str(app_root),

            frontend_path=
                str(frontend_dir),

            backend_path=
                str(backend_dir),

            screenshots_processed=
                len(screenshots),

            components_mapped=

                len(

                    pipeline_result
                    .binding_result
                    .bound_components

                ),

            components_missing=

                len(

                    pipeline_result
                    .binding_result
                    .missing_components

                )
        )

    # ========================================================
    # SCREENSHOT PROCESSING
    # ========================================================

    def _process_screenshots(
        self,
        screenshots
    ):

        output = []

        for screenshot in screenshots:

            ocr_result = (

                self.ocr_engine.extract_text(
                    screenshot
                )

            )

            lines = [

                item.text

                for item in
                ocr_result.lines
            ]

            labels = (

                self.label_extractor.extract(

                    Path(
                        screenshot
                    ).name,

                    lines

                )

            )

            output.append(
                labels
            )

        return output

    # ========================================================
    # LABEL FLATTENER
    # ========================================================

    def _flatten_labels(
        self,
        screenshot_labels
    ):

        labels = []

        for screen in screenshot_labels:

            for label in screen.labels:

                labels.append(
                    label.text
                )

        return labels

    # ========================================================
    # REPORT
    # ========================================================

    def print_report(
        self,
        generated_app:
        GeneratedApplication
    ):

        print()

        print("=" * 80)

        print(
            "APPLICATION GENERATION REPORT"
        )

        print("=" * 80)

        print()

        print(
            f"Application: "
            f"{generated_app.application_name}"
        )

        print(
            f"Location: "
            f"{generated_app.output_path}"
        )

        print()

        print(
            f"Frontend: "
            f"{generated_app.frontend_path}"
        )

        print(
            f"Backend: "
            f"{generated_app.backend_path}"
        )

        print()

        print(
            f"Screenshots: "
            f"{generated_app.screenshots_processed}"
        )

        print(
            f"Mapped Components: "
            f"{generated_app.components_mapped}"
        )

        print(
            f"Missing Components: "
            f"{generated_app.components_missing}"
        )

        print()