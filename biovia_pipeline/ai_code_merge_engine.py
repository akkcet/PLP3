# ai_code_merge_engine.py

from dataclasses import dataclass
from typing import List


@dataclass
class MergeDecision:

    category: str

    original_value: str

    ai_value: str

    selected_value: str

    reason: str


@dataclass
class MergeResult:

    enhanced_blueprint: object

    decisions: List[MergeDecision]
class AICodeMergeEngine:

    def merge(
        self,
        blueprint,
        ai_enhancement
    ):

        decisions = []

        enhanced_blueprint = blueprint

        page_lookup = {

            page.page_name: page

            for page in enhanced_blueprint.pages
        }

        for enhanced_page in (
            ai_enhancement.enhanced_pages
        ):

            if (
                enhanced_page.page_name
                not in page_lookup
            ):

                continue

            page = (
                page_lookup[
                    enhanced_page.page_name
                ]
            )

            decisions.append(

                MergeDecision(

                    category="Page Title",

                    original_value=
                        page.page_name,

                    ai_value=
                        enhanced_page.page_title,

                    selected_value=
                        enhanced_page.page_title,

                    reason=
                        "AI generated title is more descriptive."
                )
            )

            #
            # Replace title
            #
            page.page_name = (
                enhanced_page.page_title
            )

        return MergeResult(

            enhanced_blueprint=
                enhanced_blueprint,

            decisions=
                decisions
        )
    def print_report(
        self,
        merge_result
    ):

        print()

        print("=" * 80)

        print("AI MERGE REPORT")

        print("=" * 80)

        print()

        for decision in (
            merge_result.decisions
        ):

            print(
                decision.category
            )

            print(
                f"Original: "
                f"{decision.original_value}"
            )

            print(
                f"AI: "
                f"{decision.ai_value}"
            )

            print(
                f"Selected: "
                f"{decision.selected_value}"
            )

            print(
                f"Reason: "
                f"{decision.reason}"
            )

            print()