# component_parameter_to_backend_mapper.py

from dataclasses import dataclass, field
from typing import Dict


# ============================================================
# MODELS
# ============================================================

@dataclass
class BackendParameterSet:

    component_name: str

    function_name: str

    parameters: Dict = field(
        default_factory=dict
    )


# ============================================================
# PARAMETER TRANSLATION
# ============================================================

PARAMETER_TRANSLATIONS = {

    #
    # Notebook Connection
    #

    "Notebook URL":
        "server_url",

    "Server URL":
        "server_url",

    "Authentication Method":
        "authentication_method",

    "Username":
        "username",

    "Password":
        "password",

    "Session Token":
        "session_token",

    #
    # Experiment Query
    #

    "Filter By":
        "filter_by",

    "Filter Type":
        "filter_type",

    "Filter Value":
        "filter_value",

    "Maximum":
        "maximum",

    #
    # Section Components
    #

    "Section Title":
        "section_title",

    "File Location":
        "file_location",

    "Preview Pages":
        "preview_pages",

    #
    # Azure
    #

    "Azure Location":
        "storage_path",

    "Share Name":
        "share_name",

    #
    # XML
    #

    "XML Path":
        "xml_path",
}


# ============================================================
# MAPPER
# ============================================================

class ComponentParameterToBackendMapper:

    def map_component(
        self,
        component_binding,
        parameter_result
    ) -> BackendParameterSet:

        component_name = (
            component_binding.component_name
        )

        repository = (
            component_binding.repository_component
        )

        component_parameters = (
            parameter_result
            .resolved_components
            .get(component_name)
        )

        backend_params = {}

        if component_parameters:

            for param_name, param in (
                component_parameters
                .parameters.items()
            ):

                mapped_name = (
                    PARAMETER_TRANSLATIONS.get(
                        param_name
                    )
                )

                if mapped_name:

                    backend_params[
                        mapped_name
                    ] = param.parameter_value

        return BackendParameterSet(

            component_name=
                component_name,

            function_name=
                repository.python_function,

            parameters=
                backend_params
        )

    # ========================================================
    # BATCH
    # ========================================================

    def map_all(
        self,
        binding_result,
        parameter_result
    ):

        results = []

        for component in (
            binding_result.bound_components
        ):

            results.append(

                self.map_component(
                    component,
                    parameter_result
                )

            )

        return results

    # ========================================================
    # DEBUG
    # ========================================================

    def print_report(
        self,
        mapped_components
    ):

        print()

        print("=" * 80)

        print(
            "BACKEND PARAMETER REPORT"
        )

        print("=" * 80)

        print()

        for comp in mapped_components:

            print(
                comp.component_name
            )

            print(
                f"Function: "
                f"{comp.function_name}"
            )

            print()

            for key, value in (
                comp.parameters.items()
            ):

                print(
                    f"{key} = {value}"
                )

            print()