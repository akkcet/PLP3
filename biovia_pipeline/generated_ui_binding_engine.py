# generated_ui_binding_engine.py

from dataclasses import dataclass, field
from typing import Dict, List


# ============================================================
# MODELS
# ============================================================

@dataclass
class UIStateBinding:

    component_name: str

    state_name: str

    state_type: str


@dataclass
class UIActionBinding:

    component_name: str

    action_name: str

    api_endpoint: str


@dataclass
class UIBindingResult:

    states: List[UIStateBinding] = field(
        default_factory=list
    )

    actions: List[UIActionBinding] = field(
        default_factory=list
    )


# ============================================================
# ENGINE
# ============================================================

class GeneratedUIBindingEngine:

    def build(
        self,
        application_blueprint,
        api_contracts
    ) -> UIBindingResult:

        result = UIBindingResult()

        #
        # Create state bindings
        #
        for page in application_blueprint.pages:

            for control in page.controls:

                control_name = str(control)

                #
                # File Upload
                #
                if (
                    "FileUpload"
                    in control_name
                ):

                    result.states.append(

                        UIStateBinding(

                            component_name=
                                control_name,

                            state_name=
                                "selectedFile",

                            state_type=
                                "File | null"
                        )
                    )

                #
                # TextInput
                #
                elif (
                    "TextInput"
                    in control_name
                ):

                    result.states.append(

                        UIStateBinding(

                            component_name=
                                control_name,

                            state_name=
                                "inputValue",

                            state_type=
                                "string"
                        )
                    )

                #
                # DataGrid
                #
                elif (
                    "DataGrid"
                    in control_name
                ):

                    result.states.append(

                        UIStateBinding(

                            component_name=
                                control_name,

                            state_name=
                                "gridData",

                            state_type=
                                "any[]"
                        )
                    )

        #
        # Create action bindings
        #
        for api in api_contracts:

            result.actions.append(

                UIActionBinding(

                    component_name=
                        api.endpoint_name,

                    action_name=
                        api.endpoint_name,

                    api_endpoint=
                        api.route
                )
            )

        return result

    # ========================================================
    # DEBUG
    # ========================================================

    def print_bindings(
        self,
        result
    ):

        print()

        print("=" * 80)
        print("UI STATE BINDINGS")
        print("=" * 80)
        print()

        for state in result.states:

            print(
                state.component_name,
                "->",
                state.state_name
            )

        print()

        print("=" * 80)
        print("UI ACTIONS")
        print("=" * 80)
        print()

        for action in result.actions:

            print(
                action.action_name,
                "->",
                action.api_endpoint
            )