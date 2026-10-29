# component_parameter_to_ui_mapper.py

from dataclasses import dataclass, field
from typing import Dict, List


# ============================================================
# MODELS
# ============================================================

@dataclass
class UIComponentDefinition:

    component_type: str

    label: str = ""

    props: Dict = field(
        default_factory=dict
    )


@dataclass
class UIPageDefinition:

    page_name: str

    components: List[
        UIComponentDefinition
    ] = field(
        default_factory=list
    )


# ============================================================
# PARAMETER MAPPING
# ============================================================

PARAMETER_MAP = {

    #
    # Generic
    #

    "Label":
        "label",

    "Title":
        "title",

    "Placeholder":
        "placeholder",

    "Required":
        "required",

    #
    # File Upload
    #

    "Accept":
        "accept",

    "File Types":
        "accept",

    #
    # Grid
    #

    "Columns":
        "columns",

    #
    # Buttons
    #

    "Button Text":
        "text",

    "Text":
        "text",

    #
    # Form
    #

    "Default Value":
        "defaultValue"
}


# ============================================================
# MAPPER
# ============================================================

class ComponentParameterToUIMapper:

    def map_component(
        self,
        node
    ):

        component_type = (
            self._determine_component(
                node.visual_name
            )
        )

        ui_component = (
            UIComponentDefinition(
                component_type=
                    component_type
            )
        )

        parameters = getattr(
            node,
            "parameters",
            {}
        )

        for name, value in (
            parameters.items()
        ):

            mapped_name = (
                PARAMETER_MAP.get(
                    name
                )
            )

            if mapped_name:

                ui_component.props[
                    mapped_name
                ] = value

        label = (

            ui_component.props.get(
                "label"
            )

            or

            ui_component.props.get(
                "title"
            )

            or

            node.visual_name
        )

        ui_component.label = (
            label
        )

        return ui_component

    # ========================================================
    # COMPONENT TYPE
    # ========================================================

    def _determine_component(
        self,
        name
    ):

        value = (
            name.lower()
        )

        if (

            "file chooser"
            in value

        ):

            return "FileUpload"

        if (

            "submit button"
            in value

        ):

            return "PrimaryButton"

        if (

            "list box"
            in value

        ):

            return "DataGrid"

        if (

            "input form"
            in value

        ):

            return "Form"

        return "GenericComponent"

    # ========================================================
    # PAGE GENERATION
    # ========================================================

    def map_page(
        self,
        page_name,
        nodes
    ):

        page = UIPageDefinition(

            page_name=
                page_name
        )

        for node in nodes:

            page.components.append(

                self.map_component(
                    node
                )

            )

        return page

    # ========================================================
    # DEBUG
    # ========================================================

    def print_page(
        self,
        page
    ):

        print()

        print(
            "=" * 70
        )

        print(
            page.page_name
        )

        print(
            "=" * 70
        )

        print()

        for component in (
            page.components
        ):

            print(
                component.component_type
            )

            print(
                component.label
            )

            print(
                component.props
            )

            print()