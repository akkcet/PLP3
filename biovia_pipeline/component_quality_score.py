# component_quality_score.py

class ComponentQualityScore:

    def calculate(
        self,
        runner_result
    ):

        if runner_result["passed"]:

            return 100.0

        return 0.0