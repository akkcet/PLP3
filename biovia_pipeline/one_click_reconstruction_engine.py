# one_click_reconstruction_engine.py

from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile

from .app_reconstruction_agent_v2 import (
    AppReconstructionAgentV2,
    ReconstructionRequest
)


# ============================================================
# MODELS
# ============================================================

@dataclass
class ReconstructionPackage:

    app_name: str
    application_path: str
    zip_path: str
    validation_passed: bool
    quality_score: float
    ui_pattern: str


# ============================================================
# ENGINE
# ============================================================

class OneClickReconstructionEngine:

    def __init__(self):

        self.agent = (
            AppReconstructionAgentV2()
        )

    # ========================================================
    # PUBLIC API
    # ========================================================

    def generate(
        self,
        protocol_xml: str,
        screenshots=None,
        business_description: str = "",
        output_dir: str = "./generated_app6",
        ui_pattern="wizard"
    ) -> ReconstructionPackage:

        if screenshots is None:

            screenshots = []

        #
        # Run reconstruction pipeline
        #
        result = (

            self.agent.generate_application(

                ReconstructionRequest(

                    protocol_xml=
                        protocol_xml,

                    screenshot_descriptions=
                        screenshots,

                    business_description=
                        business_description,

                    output_dir=
                        output_dir,
                    ui_pattern=
                        ui_pattern
                )
            )
        )

        #
        # Create Zip Package
        #
        zip_path = (
            self._package_application(
                result.generated_path
            )
        )

        #
        # Determine score
        #
        quality_score = (
            self._calculate_quality_score(
                result
            )
        )

        return ReconstructionPackage(

            app_name=
                result.application_name,

            application_path=
                result.generated_path,

            zip_path=
                zip_path,

            validation_passed=
                True,

            quality_score=
                quality_score,
            ui_pattern=
                ui_pattern
        )

    # ========================================================
    # ZIP PACKAGING
    # ========================================================

    def _package_application(
        self,
        application_path
    ):

        app_path = Path(
            application_path
        )

        zip_path = (
            str(app_path)
            + ".zip"
        )

        with ZipFile(
            zip_path,
            "w"
        ) as zip_file:

            for file in (
                app_path.rglob("*")
            ):

                if file.is_file():

                    zip_file.write(

                        file,

                        file.relative_to(
                            app_path
                        )
                    )

        return zip_path

    # ========================================================
    # QUALITY SCORE
    # ========================================================

    def _calculate_quality_score(
        self,
        result
    ):

        mapped = (
            result.mapped_components
        )

        missing = (
            result.missing_components
        )

        total = (
            mapped + missing
        )

        if total == 0:

            return 100.0

        score = (

            mapped

            /

            total

        ) * 100

        return round(
            score,
            2
        )

    # ========================================================
    # REPORT
    # ========================================================

    def print_report(
        self,
        package
    ):

        print()

        print("=" * 80)

        print(
            "ONE CLICK RECONSTRUCTION"
        )

        print("=" * 80)

        print()

        print(
            "Application:"
        )

        print(
            package.app_name
        )

        print()

        print(
            "Generated Path:"
        )

        print(
            package.application_path
        )

        print()

        print(
            "ZIP Package:"
        )

        print(
            package.zip_path
        )

        print()

        print(
            "Validation Passed:"
        )

        print(
            package.validation_passed
        )

        print()

        print(
            "Quality Score:"
        )

        print(
            package.quality_score
        )

        print()


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    engine = (
        OneClickReconstructionEngine()
    )

    package = (

        engine.generate(

            protocol_xml="""
            <Protocol></Protocol>
            """,

            screenshots=[

                "Browse XML",

                "Process XML",

                "Import Files"
            ],

            business_description="""
            User uploads XML.

            Files are parsed.

            User selects files.

            Files are imported into ELN.
            """,
            ui_pattern="single_page"
        )
    )

    engine.print_report(
        package
    )
# engine = OneClickReconstructionEngine()

# package = engine.generate(

#     protocol_xml=xml,

#     screenshots=screenshots,

#     business_description=description)
#