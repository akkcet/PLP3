# react_app_generator_v5.py

from pathlib import Path

from biovia_pipeline.layout_enhancer import (
    LayoutEnhancer
)


class ReactAppGeneratorV5:

    def __init__(self):

        self.layout_enhancer = (
            LayoutEnhancer()
        )

    def generate(

        self,

        wizard_blueprint,

        screenshot_labels,

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

        (
            root /
            "src/components"
        ).mkdir(

            parents=True,

            exist_ok=True
        )

        self._generate_stepper(
            wizard_blueprint,
            root
        )

        self._generate_pages(
            wizard_blueprint,
            screenshot_labels,
            root
        )

    # ------------------------------------------------

    def _generate_stepper(
        self,
        wizard,
        root
    ):

        step_names = []

        for step in wizard.steps:

            step_names.append(
                f'"{step.page_title}"'
            )

        content = f"""
import React from "react";

const steps = [
    {",".join(step_names)}
];

export default function WizardStepper() {{

    return (

        <div
            className="
                flex
                gap-4
                mb-8
            "
        >

            {{

                steps.map(

                    (step,index)=>(

                        <div
                            key={{index}}
                            className="
                                px-4
                                py-2
                                rounded
                                bg-slate-200
                            "
                        >

                            {{step}}

                        </div>

                    )

                )

            }}

        </div>
    );
}}
"""

        (
            root
            / "src/components/WizardStepper.tsx"
        ).write_text(
            content,
            encoding="utf-8"
        )

    # ------------------------------------------------

    def _generate_pages(
        self,
        wizard,
        screenshot_labels,
        root
    ):

        for step in wizard.steps:

            enhanced = (

                self.layout_enhancer
                .enrich_controls(

                    step.controls,

                    screenshot_labels
                )
            )

            controls = []

            for control in enhanced:

                controls.append(

                    self._render_control(
                        control
                    )
                )

            controls_markup = (
                "\n".join(controls)
            )

            page_name = (

                step.page_name
                .replace(" ", "")
            )

            content = f"""
import React from "react";

import WizardStepper
from "../components/WizardStepper";

export default function
{page_name}() {{

    return (

        <div
            className="
                p-8
                max-w-6xl
                mx-auto
            "
        >

            <WizardStepper />

            <h1
              className="
                text-3xl
                font-bold
                mb-6
              "
            >

               {step.page_title}

            </h1>

            {controls_markup}

        </div>
    );
}}
"""

            (
                root
                / "src/pages"
                / f"{page_name}.tsx"
            ).write_text(
                content,
                encoding="utf-8"
            )

    # ------------------------------------------------

    def _render_control(
        self,
        control
    ):

        if (
            control.control_type
            == "FileUpload"
        ):

            return f"""
<div className="mb-6">

    <label
        className="
            block
            font-medium
            mb-2
        "
    >
        {control.label}
    </label>

    <input
        type="file"
    />

</div>
"""

        if (
            control.control_type
            == "PrimaryButton"
        ):

            return f"""
<button
 className="
    px-4
    py-2
    bg-blue-600
    text-white
    rounded
 "
>

 {control.label}

</button>
"""

        if (
            control.control_type
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

    <h3
      className="font-semibold"
    >
       {control.label}
    </h3>

    <div>
      Grid Placeholder
    </div>

</div>
"""

        if (
            control.control_type
            == "ProgressBar"
        ):

            return """
<div>

    Progress Bar

</div>
"""

        if (
            control.control_type
            == "ImportSummary"
        ):

            return """
<div>

    Import Complete

</div>
"""

        return f"""
<div>

 {control.label}

</div>
"""
