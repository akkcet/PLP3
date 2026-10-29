# component_refinement_engine.py

from dataclasses import dataclass


# ============================================================
# MODELS
# ============================================================

@dataclass
class RefinementRequest:

    component_name: str

    generated_code: str

    test_result: dict


@dataclass
class RefinementResult:

    component_name: str

    original_code: str

    refined_code: str

    refinement_reason: str


# ============================================================
# ENGINE
# ============================================================

class ComponentRefinementEngine:

    def refine(
        self,
        request: RefinementRequest
    ) -> RefinementResult:

        if request.test_result["passed"]:

            return RefinementResult(

                component_name=
                    request.component_name,

                original_code=
                    request.generated_code,

                refined_code=
                    request.generated_code,

                refinement_reason=
                    "No refinement needed."
            )

        refined_code = (
            self._apply_refinement(
                request.generated_code,
                request.test_result
            )
        )

        return RefinementResult(

            component_name=
                request.component_name,

            original_code=
                request.generated_code,

            refined_code=
                refined_code,

            refinement_reason=
                self._extract_reason(
                    request.test_result
                )
        )

    # ========================================================
    # REFINEMENT
    # ========================================================

    def _apply_refinement(
        self,
        code,
        test_result
    ):

        improved = code

        #
        # Empty return handling
        #
        if (
            "None"
            in test_result["stderr"]
        ):

            improved = improved.replace(
                "return None",
                "return {}"
            )

        #
        # Missing result variable
        #
        if (
            "result"
            in test_result["stderr"]
        ):

            improved += """

# Added fallback
result = {}

"""

        return improved

    # ========================================================
    # REASON
    # ========================================================

    def _extract_reason(
        self,
        result
    ):

        stderr = (
            result.get(
                "stderr",
                ""
            )
        )

        if stderr:

            return stderr

        return "Unknown test failure."

    # ========================================================
    # REPORT
    # ========================================================

    def print_report(
        self,
        refinement
    ):

        print()

        print("=" * 80)

        print(
            refinement.component_name
        )

        print("=" * 80)

        print()

        print(
            "Reason:"
        )

        print(
            refinement.refinement_reason
        )

        print()

        print(
            "Refined Code:"
        )

        print(
            refinement.refined_code
        )