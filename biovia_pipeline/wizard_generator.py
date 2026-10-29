# wizard_generator.py

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


# ============================================================
# MODELS
# ============================================================

@dataclass
class WizardPage:

    page_name: str

    page_title: str

    controls: List[str] = field(
        default_factory=list
    )


@dataclass
class WizardBlueprint:

    wizard_name: str

    steps: List[WizardPage]

    route: str = "/"


# ============================================================
# GENERATOR
# ============================================================

class WizardGenerator:

    CONTROL_MAP = {

        "UPLOAD": [
            "FileUpload",
            "PrimaryButton"
        ],

        "PROCESS": [
            "StatusPanel",
            "PrimaryButton"
        ],

        "SELECTION": [
            "DataGrid",
            "MultiSelect",
            "PrimaryButton"
        ],

        "IMPORT": [
            "ProgressBar",
            "StatusPanel"
        ],

        "COMPLETE": [
            "ImportSummary"
        ]
    }

    # ========================================================
    # BUILD BLUEPRINT
    # ========================================================

    def build_blueprint(
        self,
        workflow_definition
    ) -> WizardBlueprint:

        pages = []

        for step in workflow_definition.steps:

            page = WizardPage(

                page_name=
                    self._page_name(
                        step.name
                    ),

                page_title=
                    step.name,

                controls=
                    self.CONTROL_MAP.get(
                        step.action_type,
                        []
                    )
            )

            pages.append(page)

        return WizardBlueprint(

            wizard_name=
                workflow_definition.workflow_name,

            steps=pages,

            route="/"
        )

    # ========================================================
    # GENERATE APPLICATION
    # ========================================================

    def generate(
        self,
        wizard: WizardBlueprint,
        output_dir: str
    ):

        root = Path(output_dir)

        (root / "components").mkdir(
            parents=True,
            exist_ok=True
        )

        (root / "pages").mkdir(
            parents=True,
            exist_ok=True
        )

        self._generate_wizard(
            wizard,
            root
        )

        self._generate_steps(
            wizard,
            root
        )

    # ========================================================
    # MAIN WIZARD TSX
    # ========================================================

    def _generate_wizard(
        self,
        wizard,
        root
    ):

        imports = []

        route_map = []

        for page in wizard.steps:

            imports.append(
                f'import {page.page_name} '
                f'from "../pages/{page.page_name}";'
            )

        for idx, page in enumerate(
            wizard.steps
        ):

            route_map.append(
                f"""
                {idx}: (
                    <{page.page_name}
                        onNext={{next}}
                        onBack={{back}}
                    />
                )
                """
            )

        imports_text = "\n".join(
            imports
        )

        route_text = ",".join(
            route_map
        )

        content = f"""
import React, {{
    useState
}} from "react";

{imports_text}

export default function Wizard() {{

    const [
        currentStep,
        setCurrentStep
    ] = useState(0);

    const next = () => {{

        setCurrentStep(
            currentStep + 1
        );
    }};

    const back = () => {{

        setCurrentStep(
            currentStep - 1
        );
    }};

    const pages = {{

        {route_text}

    }};

    return (

        <div>

            {{pages[currentStep]}}

        </div>
    );
}}
"""

        (
            root /
            "components" /
            "Wizard.tsx"
        ).write_text(
            content,
            encoding="utf-8"
        )

    # ========================================================
    # GENERATE STEP PAGES
    # ========================================================

    def _generate_steps(
        self,
        wizard,
        root
    ):

        for page in wizard.steps:

            controls = []

            for control in page.controls:

                controls.append(
                    self._render_control(
                        control
                    )
                )

            controls_markup = (
                "\n".join(
                    controls
                )
            )

            content = f"""
import React from "react";

interface Props {{

    onNext: () => void;

    onBack: () => void;
}}

export default function
{page.page_name}(props: Props) {{

    return (

        <div
            className="
                max-w-6xl
                mx-auto
                p-8
                space-y-6
            "
        >

            <h1
                className="
                    text-2xl
                    font-bold
                "
            >
                {page.page_title}
            </h1>

            {controls_markup}

            <div
                className="
                    flex
                    justify-between
                "
            >

                <button
                    onClick={{props.onBack}}
                >
                    Back
                </button>

                <button
                    onClick={{props.onNext}}
                >
                    Next
                </button>

            </div>

        </div>
    );
}}
"""

            (
                root /
                "pages" /
                f"{page.page_name}.tsx"
            ).write_text(
                content,
                encoding="utf-8"
            )

    # ========================================================
    # CONTROL RENDERING
    # ========================================================

    def _render_control(
        self,
        control
    ):

        mapping = {

            "FileUpload":
"""
<div>

    <label>
        Upload File
    </label>

    <input
        type="file"
    />

</div>
""",

            "DataGrid":
"""
<div
 className="
   border
   rounded
   p-4
 "
>

  Data Grid

</div>
""",

            "MultiSelect":
"""
<select
 multiple
 className="
    border
    p-2
    w-full
 "
>
   <option>
      Placeholder
   </option>
</select>
""",

            "ProgressBar":
"""
<div>

    ProgressBar

</div>
""",

            "ImportSummary":
"""
<div>

    Import Complete

</div>
""",

            "StatusPanel":
"""
<div>

    Status Panel

</div>
""",

            "PrimaryButton":
"""
<button
 className="
    bg-blue-500
    text-white
    px-4
    py-2
 "
>
    Execute
</button>
"""
        }

        return mapping.get(
            control,
            f"<div>{control}</div>"
        )

    # ========================================================
    # HELPERS
    # ========================================================

    def _page_name(
        self,
        value: str
    ):

        parts = (
            value
            .replace("-", " ")
            .split()
        )

        return "".join(
            x.capitalize()
            for x in parts
        )