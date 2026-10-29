class PatternSimilarityEngine:

    def find_matches(
        self,
        workflow,
        catalog
    ):

        matches = []

        names = {

            x.function_name

            for x in
            workflow.components
        }

        for pattern in (
            catalog.patterns
        ):

            overlap = len(

                names.intersection(

                    pattern.components
                )
            )

            if overlap > 0:

                matches.append(

                    (
                        pattern,
                        overlap
                    )
                )

        return sorted(

            matches,

            key=lambda x:
                x[1],

            reverse=True
        )