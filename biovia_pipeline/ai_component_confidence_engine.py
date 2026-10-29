from dataclasses import dataclass


# ============================================================
# MODELS
# ============================================================

@dataclass
class ComponentConfidence:

    component_name: str

    confidence_score: float

    factors: dict


# ============================================================
# ENGINE
# ============================================================

class AIComponentConfidenceEngine:

    def calculate(
        self,
        component_name: str,
        similarity_score: float = 0.0,
        tests_passed: bool = False,
        refinement_count: int = 0,
        has_pilotscript: bool = False,
        repository_component: bool = False
    ) -> ComponentConfidence:

        score = 0.0

        factors = {}

        #
        # Existing repository component
        #
        if repository_component:

            score += 50

            factors[
                "repository_component"
            ] = 50

        #
        # Similarity match
        #
        similarity_points = (
            similarity_score * 30
        )

        score += similarity_points

        factors[
            "similarity"
        ] = round(
            similarity_points,
            2
        )

        #
        # Test execution
        #
        if tests_passed:

            score += 15

            factors[
                "tests"
            ] = 15

        #
        # PilotScript source available
        #
        if has_pilotscript:

            score += 10

            factors[
                "pilotscript"
            ] = 10

        #
        # Penalize excessive refinements
        #
        penalty = (
            refinement_count * 2
        )

        score -= penalty

        factors[
            "refinement_penalty"
        ] = -penalty

        score = max(
            0,
            min(
                score,
                100
            )
        )

        return ComponentConfidence(

            component_name=
                component_name,

            confidence_score=
                round(score, 2),

            factors=factors
        )
    def confidence_level(
        self,
        score
    ):

        if score >= 90:
            return "VERY HIGH"

        if score >= 75:
            return "HIGH"

        if score >= 50:
            return "MEDIUM"

        return "LOW"
    def requires_review(
        self,
        confidence
    ):

        return (
            confidence.confidence_score
            < 70
        )
    def print_report(
        self,
        confidence
    ):

        print()

        print("=" * 80)

        print(
            confidence.component_name
        )

        print("=" * 80)

        print()

        print(
            "Confidence Score:",
            confidence.confidence_score
        )

        print()

        for key, value in (
            confidence.factors.items()
        ):

            print(
                f"{key}: {value}"
            )