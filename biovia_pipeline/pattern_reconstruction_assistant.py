from .pattern_similarity_engine import (
    PatternSimilarityEngine
)
class PatternReconstructionAssistant:

    def suggest(
        self,
        workflow,
        catalog
    ):

        similarity = (
            PatternSimilarityEngine()
        )

        return similarity.find_matches(

            workflow,

            catalog
        )