# component_parameter_resolver.py

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ============================================================
# MODELS
# ============================================================

@dataclass
class ComponentParameter:

    parameter_name: str

    parameter_value: str

    source: str = "xml"


@dataclass
class ResolvedComponent:

    component_name: str

    parameters: Dict[
        str,
        ComponentParameter
    ] = field(
        default_factory=dict
    )


@dataclass
class ParameterResolutionResult:

    resolved_components: Dict[
        str,
        ResolvedComponent
    ]


# ============================================================
# RESOLVER
# ============================================================

class ComponentParameterResolver:

    def resolve(
        self,
        protocol_analysis
    ) -> ParameterResolutionResult:

        resolved = {}

        for node in protocol_analysis.nodes:

            component = ResolvedComponent(

                component_name=
                    node.visual_name
            )

            #
            # Existing parser normally stores
            # parameters in node.parameters
            #
            params = getattr(
                node,
                "parameters",
                {}
            )

            for name, value in (
                params.items()
            ):

                component.parameters[
                    name
                ] = ComponentParameter(

                    parameter_name=name,

                    parameter_value=
                        str(value)
                )

            resolved[
                node.visual_name
            ] = component

        return ParameterResolutionResult(
            resolved_components=
                resolved
        )

    # ========================================================
    # LOOKUPS
    # ========================================================

    def get_component_parameters(
        self,
        result:
        ParameterResolutionResult,

        component_name: str
    ) -> Dict:

        component = (
            result
            .resolved_components
            .get(component_name)
        )

        if not component:
            return {}

        output = {}

        for key, value in (
            component.parameters.items()
        ):

            output[key] = (
                value.parameter_value
            )

        return output

    # ========================================================
    # DEBUG
    # ========================================================

    def print_report(
        self,
        result:
        ParameterResolutionResult
    ):

        print()

        print("=" * 80)

        print(
            "PARAMETER REPORT"
        )

        print("=" * 80)

        print()

        for component in (
            result
            .resolved_components
            .values()
        ):

            print(
                component.component_name
            )

            print(
                "-" * 40
            )

            for parameter in (
                component.parameters.values()
            ):

                print(
                    f"{parameter.parameter_name}"
                    f" = "
                    f"{parameter.parameter_value}"
                )

            print()