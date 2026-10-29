# generation_context_engine.py

class GenerationContextEngine:

    def __init__(self):

        self.summaries = []

    def add_summary(
        self,
        artifact_name,
        summary
    ):

        self.summaries.append(

            {
                "artifact":
                    artifact_name,

                "summary":
                    summary
            }
        )

    def build_prompt_context(
        self
    ):

        sections = []

        for item in self.summaries:

            sections.append(

f"""
==================================================
{item["artifact"].upper()} SUMMARY
==================================================

{item["summary"]}

"""
            )

        return "\n".join(
            sections
        )