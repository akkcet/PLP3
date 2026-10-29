# component_similarity_engine.py

from dataclasses import dataclass
from difflib import SequenceMatcher

from .component_metadata_registry import (
    ComponentMetadata
)
# ============================================================
# MODELS
# ============================================================

@dataclass
class SimilarComponent:

    name: str

    module_name: str

    similarity_score: float

    category: str


# ============================================================
# ENGINE
# ============================================================

class ComponentSimilarityEngine:

    def find_best_match(
        self,
        component_name,
        metadata_registry
    ):

        best_match = None

        best_score = 0

        for component in (
            metadata_registry
            .components
            .values()
        ):

            if not isinstance(
                component,
                ComponentMetadata
            ):
                continue

            score = (
                self._similarity(

                    component_name,

                    component.name
                )
            )

            if score > best_score:

                best_score = score

                best_match = component

        if not best_match:

            return None

        return SimilarComponent(

            name=
                best_match.component_name,

            module_name=
                best_match.module_name,

            similarity_score=
                best_score,

            category=
                best_match.category
        )

    # ========================================================
    # STRING SIMILARITY
    # ========================================================

    def _similarity(
        self,
        source,
        target
    ):

        return round(

            SequenceMatcher(

                None,

                source.lower(),

                target.lower()

            ).ratio(),

            2
        )

    # ========================================================
    # TOP N MATCHES
    # ========================================================

    def top_matches(
        self,
        component_name,
        metadata_registry,
        top_n=5
    ):

        results = []

        for component in (
            metadata_registry
            .components
            .values()
        ):

            if not isinstance(
                component,
                ComponentMetadata
            ):
                continue

            score = (
                self._similarity(

                    component_name,

                    component.name
                )
            )

            results.append(

                SimilarComponent(

                    name=
                        component.name,

                    module_name=
                        component.module_name,

                    similarity_score=
                        score,

                    category=
                        component.category
                )
            )

        results.sort(

            key=lambda x:
                x.similarity_score,

            reverse=True
        )

        return results[:top_n]

    # ========================================================
    # REPORT
    # ========================================================

    def print_matches(
        self,
        matches
    ):

        print()

        print("=" * 80)

        print(
            "SIMILAR COMPONENTS"
        )

        print("=" * 80)

        print()

        for match in matches:

            print(
                f"{match.name}"
            )

            print(
                f"Module: "
                f"{match.module_name}"
            )

            print(
                f"Category: "
                f"{match.category}"
            )

            print(
                f"Similarity: "
                f"{match.similarity_score}"
            )

            print()