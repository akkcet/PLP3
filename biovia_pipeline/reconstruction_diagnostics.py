# reconstruction_diagnostics.py

from dataclasses import dataclass, asdict
from pathlib import Path
import json


# ============================================================
# MODELS
# ============================================================

@dataclass
class ReconstructionDiagnostics:

    application_name: str

    pages: int

    workflows: int

    api_contracts: int

    mapped_components: int

    missing_components: int

    generated_components: int

    validation_passed: bool

    generated_path: str


# ============================================================
# ENGINE
# ============================================================

class ReconstructionDiagnosticsEngine:

    def build(
        self,
        context,
        validation_report=None
    ):

        generated_components = len(

            getattr(
                context.binding_result,
                "missing_components",
                []
            )
        )

        api_contracts = len(

            getattr(
                context,
                "api_contracts",
                []
            )
        )

        validation_passed = True

        if validation_report:

            validation_passed = (
                validation_report.passed
            )

        return ReconstructionDiagnostics(

            application_name=

                getattr(
                    context.protocol_analysis,
                    "protocol_name",
                    "GeneratedApplication"
                ),

            pages=
                len(
                    context.page_graph.pages
                ),

            workflows=1,

            api_contracts=
                api_contracts,

            mapped_components=
                len(
                    context.binding_result
                    .bound_components
                ),

            missing_components=
                len(
                    context.binding_result
                    .missing_components
                ),

            generated_components=
                generated_components,

            validation_passed=
                validation_passed,

            generated_path=
                context.output_dir
        )

    # ========================================================
    # SAVE JSON
    # ========================================================

    def save(
        self,
        diagnostics,
        output_dir
    ):

        output_dir = Path(
            output_dir
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        path = (
            output_dir
            /
            "reconstruction_report.json"
        )

        path.write_text(

            json.dumps(
                asdict(
                    diagnostics
                ),
                indent=4
            ),

            encoding="utf-8"
        )

        return path

    # ========================================================
    # REPORT
    # ========================================================

    def print_report(
        self,
        diagnostics
    ):

        print()

        print("=" * 80)
        print("RECONSTRUCTION DIAGNOSTICS")
        print("=" * 80)

        print()

        print(
            "Application:",
            diagnostics.application_name
        )

        print(
            "Pages:",
            diagnostics.pages
        )

        print(
            "Workflows:",
            diagnostics.workflows
        )

        print(
            "API Contracts:",
            diagnostics.api_contracts
        )

        print(
            "Mapped Components:",
            diagnostics.mapped_components
        )

        print(
            "Missing Components:",
            diagnostics.missing_components
        )

        print(
            "Generated Components:",
            diagnostics.generated_components
        )

        print(
            "Validation Passed:",
            diagnostics.validation_passed
        )

        print(
            "Generated Path:",
            diagnostics.generated_path
        )

        print()