# react_generator.py

from pathlib import Path


class ReactGenerator:

    CONTROL_MAPPING = {

        "FileUpload":
"""
<FileUpload />
""",

        "PrimaryButton":
"""
<PrimaryButton>
   Submit
</PrimaryButton>
""",

        "TextLabel":
"""
<TextLabel />
""",

        "DataGrid":
"""
<DataGrid />
""",

        "FormGroup":
"""
<FormGroup />
""",

        "Row":
"""
<Row />
""",

        "Column":
"""
<Column />
"""
    }
    def render_component_with_bindings(
        self,
        component,
        ui_binding_result
    ):

        props = []

        #
        # Existing props
        #
        if hasattr(
            component,
            "props"
        ):

            for key, value in (
                component.props.items()
            ):

                if isinstance(
                    value,
                    bool
                ):

                    props.append(
                        f'{key}={{{str(value).lower()}}}'
                    )

                else:

                    props.append(
                        f'{key}="{value}"'
                    )

        #
        # UI state bindings
        #
        for state in (
            ui_binding_result.states
        ):

            if (

                "FileUpload"
                in component.component_type

                and

                state.state_name
                ==
                "selectedFile"

            ):

                props.append(
                    "onChange={setSelectedFile}"
                )

        #
        # Action bindings
        #
        if (
            component.component_type
            ==
            "PrimaryButton"
        ):

            if (
                ui_binding_result.actions
            ):

                action = (
                    ui_binding_result.actions[0]
                )

                props.append(
                    f"onClick={{{action.action_name}}}"
                )

        props_string = " ".join(
            props
        )

        if (
            component.component_type
            ==
            "PrimaryButton"
        ):

            return f"""
    <PrimaryButton {props_string}>
        {component.label}
    </PrimaryButton>
    """

        return f"""
    <{component.component_type}
        {props_string}
    />
    """
    def generate_page(self, page, ui_binding_result):

        controls = []

        for c in page.controls:

            jsx = self.render_component_with_bindings(c,ui_binding_result)            
            controls.append(jsx)


        jsx_body = "\n".join(controls)

        return f"""
import React from "react";

export default function {page.name}() {{

  return (

    <div className="p-6">

      {jsx_body}

    </div>

  );
}}
"""
    def render_component(
        self,
        component
    ):

        props = []

        if hasattr(
            component,
            "props"
        ):

            for key, value in (
                component.props.items()
            ):

                if isinstance(
                    value,
                    bool
                ):

                    props.append(
                        f'{key}={{{str(value).lower()}}}'
                    )

                else:

                    props.append(
                        f'{key}="{value}"'
                    )

        props_str = " ".join(
            props
        )

        if (
            component.component_type
            ==
            "PrimaryButton"
        ):

            button_text = (

                component.label

                or

                component.props.get(
                    "text",
                    "Submit"
                )
            )

            return f"""
    <PrimaryButton {props_str}>
        {button_text}
    </PrimaryButton>
    """

        return f"""
    <{component.component_type}
        {props_str}
    />
    """

    def write_application(
        self,
        blueprint,
        output_dir: str
    ):

        output = Path(output_dir)

        output.mkdir(
            parents=True,
            exist_ok=True
        )

        pages_dir = output / "pages"

        pages_dir.mkdir(exist_ok=True)

        for page in blueprint.pages:

            content = self.generate_page(
                page
            )

            file_path = (
                pages_dir /
                f"{page.name}.tsx"
            )

            file_path.write_text(
                content,
                encoding="utf-8"
            )