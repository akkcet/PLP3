# react_generator_v2.py

from pathlib import Path


class ReactGeneratorV2:

    CONTROL_MAP = {

        "FileUpload":
"""
<FileUpload />
""",

        "PrimaryButton":
"""
<Button>
    Continue
</Button>
""",

        "DataGrid":
"""
<DataGrid />
""",

        "MultiSelect":
"""
<MultiSelect />
""",

        "ProgressBar":
"""
<ProgressBar />
""",
    }

    def generate_page(
        self,
        page
    ):

        controls = []

        for control in page.controls:

            controls.append(

                self.CONTROL_MAP.get(
                    control,
                    f"<div>{control}</div>"
                )
            )

        page_body = "\n".join(
            controls
        )

        return f"""
import React from "react";

export default function {page.page_name.replace(' ', '')}() {{

    return (

        <div className="p-6 space-y-4">

            <h1>
                {page.page_name}
            </h1>

            {page_body}

        </div>

    );
}}
"""

    def generate_routes(
        self,
        blueprint
    ):

        imports = []
        routes = []

        for page in blueprint.pages:

            page_name = (
                page.page_name
                .replace(" ", "")
            )

            imports.append(
f'import {page_name} from "../pages/{page_name}";'
            )

            routes.append(
f'<Route path="{page.route}" element={{<{page_name} />}} />'
            )

        return f"""
import {{
    Routes,
    Route
}} from "react-router-dom";

{' '.join(imports)}

export default function AppRoutes() {{

    return (

        <Routes>

            {' '.join(routes)}

        </Routes>
    );
}}
"""

    def generate(
        self,
        blueprint,
        output_dir
    ):

        root = Path(output_dir)

        pages = root / "pages"

        pages.mkdir(
            parents=True,
            exist_ok=True
        )

        for page in blueprint.pages:

            tsx = self.generate_page(
                page
            )

            file_name = (
                page.page_name
                .replace(" ", "")
            )

            (pages /
             f"{file_name}.tsx"
             ).write_text(tsx)

        routes_dir = (
            root / "routes"
        )

        routes_dir.mkdir(
            exist_ok=True
        )

        (
            routes_dir /
            "AppRoutes.tsx"
        ).write_text(
            self.generate_routes(
                blueprint
            )
        )