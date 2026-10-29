# pipeline_validation_engine.py

from dataclasses import dataclass, field
from typing import List


# ============================================================
# MODELS
# ============================================================

@dataclass
class ValidationCheck:

    name: str

    passed: bool

    details: str


@dataclass
class ValidationReport:

    checks: List[
        ValidationCheck
    ] = field(
        default_factory=list
    )

    @property
    def passed(self):

        return all(
            x.passed
            for x in self.checks
        )

class PipelineValidationEngine:

    def validate(
        self,
        protocol_analysis,
        binding_result,
        parameter_result,
        backend_parameters,
        workflow_bindings,
        stateful_workflow,
        page_graph,
        blueprint,
        api_contracts
    ):

        report = ValidationReport()

        report.checks.append(

            ValidationCheck(

                name="Protocol Analysis",

                passed=
                    protocol_analysis
                    is not None,

                details=
                    "Protocol analysis created."
            )
        )

        report.checks.append(

            ValidationCheck(

                name="Component Bindings",

                passed=
                    binding_result
                    is not None,

                details=
                    f"Mapped Components: "
                    f"{len(binding_result.bound_components)}"
            )
        )

        report.checks.append(

            ValidationCheck(

                name="Parameter Resolution",

                passed=
                    parameter_result
                    is not None,

                details=
                    "Parameter resolution completed."
            )
        )

        report.checks.append(

            ValidationCheck(

                name="Backend Parameters",

                passed=
                    backend_parameters
                    is not None,

                details=
                    f"{len(backend_parameters)} backend parameter sets."
            )
        )

        report.checks.append(

            ValidationCheck(

                name="Workflow Bindings",

                passed=
                    workflow_bindings
                    is not None,

                details=
                    "Workflow bindings generated."
            )
        )

        report.checks.append(

            ValidationCheck(

                name="Stateful Workflow",

                passed=
                    stateful_workflow
                    is not None,

                details=
                    "Workflow state graph available."
            )
        )

        report.checks.append(

            ValidationCheck(

                name="Page Graph",

                passed=
                    page_graph
                    is not None,

                details=
                    f"{len(page_graph.pages)} pages."
            )
        )

        report.checks.append(

            ValidationCheck(

                name="Blueprint",

                passed=
                    blueprint
                    is not None,

                details=
                    "Application blueprint generated."
            )
        )

        report.checks.append(

            ValidationCheck(

                name="API Contracts",

                passed=
                    api_contracts
                    is not None,

                details=
                    f"{len(api_contracts)} endpoints."
            )
        )

        return report
    def ensure_valid(
        self,
        report
    ):

        failures = [

            x

            for x in report.checks

            if not x.passed
        ]

        if failures:

            error_text = "\n".join(

                f"{x.name}: {x.details}"

                for x in failures
            )

            raise RuntimeError(

                "Pipeline Validation Failed\n\n"

                + error_text
            )
    def print_report(
        self,
        report
    ):

        print()

        print("=" * 80)

        print(
            "PIPELINE VALIDATION"
        )

        print("=" * 80)

        print()

        for check in (
            report.checks
        ):

            status = (

                "PASS"

                if check.passed

                else

                "FAIL"
            )

            print(

                f"[{status}] "

                f"{check.name}"

            )

            print(
                f"  {check.details}"
            )

            print()

        print(
            f"OVERALL: "
            f"{'PASS' if report.passed else 'FAIL'}"
        )