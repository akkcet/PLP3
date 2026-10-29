# workflow_api_binding_builder.py

from dataclasses import dataclass, field
from typing import List


@dataclass
class PageActionBinding:

    page_name: str

    action_name: str

    api_route: str

    backend_function: str


@dataclass
class WorkflowApiBindings:

    bindings: List[
        PageActionBinding
    ] = field(
        default_factory=list
    )


class WorkflowApiBindingBuilder:
    def print_report(
        self,
        bindings
    ):

        print()

        print("=" * 80)

        print(
            "WORKFLOW API BINDINGS"
        )

        print("=" * 80)

        print()

        for binding in (
            bindings.bindings
        ):

            print(
                f"{binding.page_name}"
            )

            print(
                f"Action : "
                f"{binding.action_name}"
            )

            print(
                f"Route  : "
                f"{binding.api_route}"
            )

            print(
                f"Function : "
                f"{binding.backend_function}"
            )

            print()    
    
    def _find_contract(
        self,
        contracts,
        action_name
    ):

        normalized = (
            action_name
            .lower()
        )

        for key, value in (
            contracts.items()
        ):

            if normalized in key:

                return value

        return None
    def _determine_action(
        self,
        page_type
    ):

        mapping = {

            "UPLOAD":
                "ProcessXml",

            "PROCESS":
                "ProcessXml",

            "SELECTION":
                "ImportFiles",

            "IMPORT":
                "ImportFiles",

            "DOWNLOAD":
                "DownloadFiles",

            "REVIEW":
                "Review",

            "COMPLETE":
                "Complete"
        }

        return mapping.get(
            page_type,
            page_type
        )    

    def build(
        self,
        page_graph,
        api_contracts,
        workflow
    ):

        result = WorkflowApiBindings()

        contract_lookup = {

            contract.endpoint_name.lower():
                contract

            for contract in api_contracts
        }

        for page in page_graph.pages:

            page_name = (
                page.page_name
            )

            page_type = (
                page.page_type
            )

            action_name = (
                self._determine_action(
                    page_type
                )
            )

            contract = (
                self._find_contract(
                    contract_lookup,
                    action_name
                )
            )

            if contract:

                result.bindings.append(

                    PageActionBinding(

                        page_name=
                            page_name,

                        action_name=
                            action_name,

                        api_route=
                            contract.route,

                        backend_function=
                            contract.function_name
                    )
                )

        return result