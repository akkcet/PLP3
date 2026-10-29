# ai_auto_fix_engine.py

from dataclasses import dataclass
from typing import List


@dataclass
class AutoFix:

    category: str

    action: str

    confidence: float


@dataclass
class AutoFixResult:

    fixes: List[AutoFix]

    modified_blueprint: object
class AIAutoFixEngine:

    def apply(
        self,
        review,
        blueprint
    ):

        fixes = []

        updated_blueprint = blueprint

        for finding in review.findings:

            #
            # Missing Components
            #
            if (

                finding.category
                == "Components"

            ):

                fixes.append(

                    AutoFix(

                        category=
                            "Components",

                        action=
                            "Generate missing components",

                        confidence=0.95
                    )
                )

            #
            # Missing Validation
            #
            elif (

                finding.category
                == "Workflow"

            ):

                fixes.append(

                    AutoFix(

                        category=
                            "Workflow",

                        action=
                            "Insert validation step",

                        confidence=0.85
                    )
                )

        return AutoFixResult(

            fixes=
                fixes,

            modified_blueprint=
                updated_blueprint
        )
    def add_validation_step(
        self,
        blueprint
    ):

        page_names = [

            x.page_name

            for x in
            blueprint.pages
        ]

        if (
            "Validation"
            not in page_names
        ):

            blueprint.pages.insert(

                1,

                type(
                    blueprint.pages[0]
                )(

                    page_name=
                        "Validation",

                    route=
                        "/validation",

                    controls=[
                        "StatusPanel",
                        "PrimaryButton"
                    ]
                )
            )

        return blueprint
    def fix_missing_components(
        self,
        blueprint,
        missing_components
    ):

        if not missing_components:

            return blueprint

        #
        # Mark for AI generation
        #
        blueprint.missing_components = [

            x

            for x in missing_components
        ]

        return blueprint
    def print_result(
        self,
        result
    ):

        print()

        print("=" * 80)

        print(
            "AUTO FIX REPORT"
        )

        print("=" * 80)

        print()

        for fix in result.fixes:

            print(
                fix.category
            )

            print(
                fix.action
            )

            print(
                fix.confidence
            )

            print()