# generated_component_enricher.py

class GeneratedComponentEnricher:

    def enrich(
        self,
        generated_component,
        similar_component
    ):

        if not similar_component:

            return generated_component

        enriched = (
            generated_component
        )

        banner = f'''
# =====================================================
# Similar Existing Component
# =====================================================

# Name:
# {similar_component.name}

# Similarity:
# {similar_component.similarity_score}

# Category:
# {similar_component.category}

'''

        enriched.generated_code = (

            banner

            +

            enriched.generated_code
        )

        return enriched