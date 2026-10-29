# component_refinement_loop.py
from .component_refinement_engine import (
    RefinementRequest
)
class ComponentRefinementLoop:

    def run(
        self,
        generated_component,
        test_generator,
        test_runner,
        refinement_engine,

        max_iterations=3
    ):

        current_component = (
            generated_component
        )

        history = []

        for iteration in range(
            max_iterations
        ):

            test = (
                test_generator.generate(
                    current_component
                )
            )

            test_path = (
                test_generator.save(
                    test,
                    "generated_tests"
                )
            )

            result = (
                test_runner.run(
                    test_path
                )
            )

            history.append(
                result
            )

            if result["passed"]:

                return {

                    "success": True,

                    "component":
                        current_component,

                    "history":
                        history
                }

            refinement = (
                refinement_engine.refine(

                    RefinementRequest(

                        component_name=
                            current_component
                            .component_name,

                        generated_code=
                            current_component
                            .generated_code,

                        test_result=
                            result
                    )
                )
            )

            current_component.generated_code = (

                refinement.refined_code
            )

        return {

            "success": False,

            "component":
                current_component,

            "history":
                history
        }