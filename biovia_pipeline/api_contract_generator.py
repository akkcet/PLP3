# api_contract_generator.py

from dataclasses import dataclass


@dataclass
class APIContract:

    endpoint_name: str

    route: str

    function_name: str


class APIContractGenerator:

    def generate(
        self,
        workflow
    ):

        contracts = []

        for component in (
            workflow.components
        ):

            contracts.append(

                APIContract(

                    endpoint_name=
                        component
                        .component_name,

                    route=
                        "/api/" +
                        component
                        .component_name
                        .lower()
                        .replace(
                            " ",
                            "-"
                        ),

                    function_name=
                        component
                        .function_name
                )
            )

        return contracts