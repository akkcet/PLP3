# react_app_generator_v4.py

from pathlib import Path


class ReactAppGeneratorV4:

    def generate(
        self,
        schema,
        output_dir
    ):

        root = Path(output_dir)

        (
            root /
            "src/pages"
        ).mkdir(
            parents=True,
            exist_ok=True
        )

        for page in schema.pages:

            self._generate_page(
                page,
                root
            )

    def _generate_page(
        self,
        page,
        root
    ):

        controls = []

        #for control in page.components:
        for control in page.controls:
            controls.append(

                self._render_control(
                    control
                )
            )

        controls_text = "\n".join(
            controls
        )

        page_name = (
            page.page_name
            .replace(" ", "")
        )

        content = f"""
import React from "react";

export default function {page_name}() {{

    return (

        <div
            className="
                p-6
                space-y-4
            "
        >

            <h1
                className="
                    text-2xl
                    font-bold
                "
            >
                {page.page_name}
            </h1>

            {controls_text}

        </div>
    );
}}
"""

        (
            root /
            "src/pages" /
            f"{page_name}.tsx"
        ).write_text(
            content,
            encoding="utf-8"
        )

    def _render_control(
        self,
        control
    ):
        if isinstance(control, str):

            return f"""
            <div>
             
            {control}
             
            </div>
            """
        label = (
            control.label
            #or control.component_type
            or control
        )

        if (
            #control.component_type
            control
            == "FileUpload"
        ):

            return f"""
<div>

<label
 className="block mb-2"
>
 {label}
</label>

<input
 type="file"
/>

</div>
"""

        elif (
            #control.component_type
            control
            == "PrimaryButton"
        ):

            return f"""
<button
 className="
  bg-blue-600
  text-white
  px-4
  py-2
  rounded
 "
>
 {label}
</button>
"""

        elif (
            #control.component_type
            control
            == "TextInput"
        ):

            return f"""
<div>

<label
 className="block mb-2"
>
 {label}
</label>

<input
 type="text"
 className="
  border
  p-2
  w-full
 "
/>

</div>
"""

        elif (
            #control.component_type
            control
            == "DataGrid"
        ):

            return f"""
<div
 className="
  border
  rounded
  p-4
 "
>

<h3>
 {label}
</h3>

<div>
 Data Grid Placeholder
</div>

</div>
"""

        return f"""
<div>

 {label}

</div>
"""