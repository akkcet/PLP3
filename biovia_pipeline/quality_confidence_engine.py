# quality_confidence_engine.py

class QualityConfidenceEngine:

    def calculate(
        self,
        history
    ):

        if not history:

            return 0

        passed = len(

            [
                x

                for x in history

                if x["passed"]
            ]
        )

        return round(

            (
                passed
                /
                len(history)
            )
            * 100,

            2
        )