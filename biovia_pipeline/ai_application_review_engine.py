# ai_application_review_engine.py

from dataclasses import dataclass, field
from typing import List


# ============================================================
# MODELS
# ============================================================

@dataclass
class ArchitectureFinding:

    category: str

    severity: str

    recommendation: str

    confidence: float


@dataclass
class ApplicationReview:

    findings: List[
        ArchitectureFinding
    ] = field(
        default_factory=list
    )

    score: float = 0.0

class AIApplicationReviewEngine:

    def review(
        self,
        context
    ) -> ApplicationReview:

        findings = []

        #
        # Missing components
        #
        if (
            context.binding_result
            .missing_components
        ):

            findings.append(

                ArchitectureFinding(

                    category=
                        "Components",

                    severity=
                        "HIGH",

                    recommendation=
                        f"{len(context.binding_result.missing_components)} "
                        f"components still require implementation.",

                    confidence=0.95
                )
            )

        #
        # Page count
        #
        if (
            len(
                context.page_graph.pages
            ) < 2
        ):

            findings.append(

                ArchitectureFinding(

                    category=
                        "UI",

                    severity=
                        "HIGH",

                    recommendation=
                        "Workflow may require additional pages.",

                    confidence=0.85
                )
            )

        #
        # API Contracts
        #
        if (
            len(
                context.api_contracts
            ) == 0
        ):

            findings.append(

                ArchitectureFinding(

                    category=
                        "Backend",

                    severity=
                        "CRITICAL",

                    recommendation=
                        "No API contracts generated.",

                    confidence=1.0
                )
            )

        #
        # Business workflow
        #
        if (
            not context.business_workflow
            or
            not context.business_workflow.workflow_steps
        ):

            findings.append(

                ArchitectureFinding(

                    category=
                        "Workflow",

                    severity=
                        "HIGH",

                    recommendation=
                        "Workflow steps not identified.",

                    confidence=0.90
                )
            )

        score = (
            self._calculate_score(
                findings
            )
        )

        return ApplicationReview(

            findings=findings,

            score=score
        )
    def _calculate_score(
        self,
        findings
    ):

        score = 100

        for finding in findings:

            if (
                finding.severity
                == "CRITICAL"
            ):
                score -= 40

            elif (
                finding.severity
                == "HIGH"
            ):
                score -= 20

            elif (
                finding.severity
                == "MEDIUM"
            ):
                score -= 10

            else:
                score -= 5

        return max(
            score,
            0
        )
    def print_review(
        self,
        review
    ):

        print()

        print("=" * 80)

        print(
            "AI APPLICATION REVIEW"
        )

        print("=" * 80)

        print()

        print(
            f"Quality Score: "
            f"{review.score}"
        )

        print()

        for finding in (
            review.findings
        ):

            print(
                f"[{finding.severity}] "
                f"{finding.category}"
            )

            print(
                finding.recommendation
            )

            print(
                f"Confidence: "
                f"{finding.confidence}"
            )

            print()