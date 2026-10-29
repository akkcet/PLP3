# component_pattern_mining_engine.py

from dataclasses import dataclass, field
from typing import List, Dict


# ============================================================
# MODELS
# ============================================================

@dataclass
class WorkflowPattern:

    pattern_name: str

    components: List[str]

    frequency: int

    category: str


@dataclass
class PatternCatalog:

    patterns: List[
        WorkflowPattern
    ] = field(
        default_factory=list
    )
class ComponentPatternMiningEngine:

    def mine(
        self,
        workflows
    ) -> PatternCatalog:

        frequencies = {}

        for workflow in workflows:

            names = [

                x.function_name

                for x in
                workflow.components
            ]

            #
            # Window size = 2
            #
            for index in range(
                len(names) - 1
            ):

                pair = (

                    names[index],

                    names[index + 1]
                )

                frequencies[
                    pair
                ] = (

                    frequencies.get(
                        pair,
                        0
                    )

                    + 1
                )

        catalog = (
            PatternCatalog()
        )

        for pair, count in (
            frequencies.items()
        ):

            catalog.patterns.append(

                WorkflowPattern(

                    pattern_name=
                        self._name(
                            pair
                        ),

                    components=
                        list(pair),

                    frequency=
                        count,

                    category=
                        self._category(
                            pair
                        )
                )
            )

        return catalog
    def _name(
        self,
        pair
    ):

        return (

            pair[0]

            +

            "_to_"

            +

            pair[1]

        )
    def _category(
        self,
        pair
    ):

        pair_text = (
            " ".join(pair)
            .lower()
        )

        if (

            "notebook"

            in pair_text

            or

            "experiment"

            in pair_text

        ):

            return "ELN"

        if (

            "section"

            in pair_text

        ):

            return "IMPORT"

        return "GENERAL"
    def print_catalog(
        self,
        catalog
    ):

        print()

        print("=" * 80)

        print(
            "PATTERN CATALOG"
        )

        print("=" * 80)

        print()

        for pattern in (
            catalog.patterns
        ):

            print(
                pattern.pattern_name
            )

            print(
                f"Category: "
                f"{pattern.category}"
            )

            print(
                f"Frequency: "
                f"{pattern.frequency}"
            )

            print(
                f"Components: "
                f"{pattern.components}"
            )

            print()