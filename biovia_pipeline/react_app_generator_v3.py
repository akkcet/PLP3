# react_app_generator_v3.py

from pathlib import Path


class ReactAppGeneratorV3:

    def generate(
        self,
        blueprint,
        output_dir: str
    ):

        root = Path(output_dir)

        self._create_structure(root)

        self._generate_app(root)

        self._generate_layout(root)

        self._generate_routes(
            blueprint,
            root
        )

        self._generate_types(root)

        self._generate_services(
            blueprint,
            root
        )

        self._generate_pages(
            blueprint,
            root
        )

    # ====================================================
    # FOLDER STRUCTURE
    # ====================================================

    def _create_structure(
        self,
        root: Path
    ):

        folders = [

            "src",

            "src/pages",

            "src/components",

            "src/layouts",

            "src/routes",

            "src/services",

            "src/types",

            "src/hooks",
        ]

        for folder in folders:

            (
                root /
                folder
            ).mkdir(
                parents=True,
                exist_ok=True
            )

    # ====================================================
    # APP.TSX
    # ====================================================

    def _generate_app(
        self,
        root: Path
    ):

        content = """
import React from "react";

import {
    BrowserRouter
} from "react-router-dom";

import AppRoutes from "./routes/AppRoutes";

export default function App() {

    return (

        <BrowserRouter>

            <AppRoutes />

        </BrowserRouter>
    );
}
"""

        (
            root /
            "src/App.tsx"
        ).write_text(
            content,
            encoding="utf-8"
        )

    # ====================================================
    # APP LAYOUT
    # ====================================================

    def _generate_layout(
        self,
        root: Path
    ):

        content = """
import React from "react";

interface AppLayoutProps {

    title: string;

    children: React.ReactNode;
}

export default function AppLayout(
    props: AppLayoutProps
) {

    return (

        <div className="min-h-screen bg-slate-50">

            <header
                className="
                    bg-slate-900
                    text-white
                    px-6
                    py-4
                "
            >

                <h1
                    className="
                        text-xl
                        font-bold
                    "
                >
                    {props.title}
                </h1>

            </header>

            <main
                className="p-6"
            >
                {props.children}
            </main>

        </div>
    );
}
"""

        (
            root /
            "src/layouts/AppLayout.tsx"
        ).write_text(
            content,
            encoding="utf-8"
        )

    # ====================================================
    # ROUTES
    # ====================================================

    def _generate_routes(
        self,
        blueprint,
        root: Path
    ):

        imports = []

        routes = []

        for page in blueprint.pages:

            component_name = (
                page.page_name
                    .replace(
                        " ",
                        ""
                    )
            )

            imports.append(
                f'import {component_name} from "../pages/{component_name}";'
            )

            routes.append(
                f'<Route path="{page.route}" element={{<{component_name} />}} />'
            )

        imports_text = "\n".join(
            imports
        )

        routes_text = "\n".join(
            routes
        )

        content = f"""
import React from "react";

import {{
    Routes,
    Route
}} from "react-router-dom";

{imports_text}

export default function AppRoutes() {{

    return (

        <Routes>

            {routes_text}

        </Routes>
    );
}}
"""

        (
            root /
            "src/routes/AppRoutes.tsx"
        ).write_text(
            content,
            encoding="utf-8"
        )

    # ====================================================
    # TYPES
    # ====================================================

    def _generate_types(
        self,
        root: Path
    ):

        content = """
export interface ApiResponse<T> {

    success: boolean;

    data: T;

    error?: string;
}

export interface WorkflowResult {

    status: string;

    message: string;
}

export interface ImportFile {

    fileName: string;

    fileLocation: string;

    sectionTitle: string;
}
"""

        (
            root /
            "src/types/CommonTypes.ts"
        ).write_text(
            content,
            encoding="utf-8"
        )

    # ====================================================
    # API SERVICES
    # ====================================================

    def _generate_services(
        self,
        blueprint,
        root: Path
    ):

        functions = []

        for endpoint in blueprint.api_endpoints:

            func_name = (
                endpoint.name
                    .replace(
                        " ",
                        ""
                    )
            )

            functions.append(
f"""
export async function {func_name}(
    payload: any
) {{

    const response =
        await fetch(
            "{endpoint.route}",
            {{
                method: "POST",

                headers: {{
                    "Content-Type":
                        "application/json"
                }},

                body: JSON.stringify(
                    payload
                )
            }}
        );

    return response.json();
}}
"""
            )

        content = (
            "\n".join(functions)
        )

        (
            root /
            "src/services/api.ts"
        ).write_text(
            content,
            encoding="utf-8"
        )

    # ====================================================
    # PAGE GENERATION
    # ====================================================

    def _generate_pages(
        self,
        blueprint,
        root: Path
    ):

        for page in blueprint.pages:

            content = self._generate_page(
                page
            )

            page_name = (
                page.page_name
                    .replace(
                        " ",
                        ""
                    )
            )

            (
                root /
                "src/pages" /
                f"{page_name}.tsx"
            ).write_text(
                content,
                encoding="utf-8"
            )

    # ====================================================
    # SINGLE PAGE
    # ====================================================

    def _generate_page(
        self,
        page
    ):

        controls = []

        for control in page.controls:

            controls.append(
                self._map_control(
                    control
                )
            )

        controls_markup = "\n".join(
            controls
        )

        component_name = (
            page.page_name
                .replace(
                    " ",
                    ""
                )
        )

        return f"""
import React from "react";

import AppLayout
from "../layouts/AppLayout";

export default function {component_name}() {{

    return (

        <AppLayout
            title="{page.page_name}"
        >

            {controls_markup}

        </AppLayout>
    );
}}
"""


    ##Generate API Actions
    def _generate_actions(
        self,
        ui_bindings
    ):

        lines = []

        for action in (
            ui_bindings.actions
        ):

            lines.append(
    f"""
    async function
    {action.action_name}() {{

        const result =
            await fetch(
                "{action.api_endpoint}",
                {{
                    method: "POST"
                }}
            );

        return result.json();
    }}
    """
            )

        return "\n".join(
            lines
        )
    ##generate state
    def _generate_state(
        self,
        ui_bindings
    ):

        lines = []

        for state in (
            ui_bindings.states
        ):

            setter = (

                "set"

                +

                state.state_name[0]
                    .upper()

                +

                state.state_name[1:]
            )

            default_value = "null"

            if (
                state.state_type
                ==
                "string"
            ):

                default_value = '""'

            elif (
                state.state_type
                ==
                "any[]"
            ):

                default_value = "[]"

            lines.append(
    f"""
    const [
        {state.state_name},
        {setter}
    ] = useState(
        {default_value}
    );
    """
            )

        return "\n".join(
            lines
        )
    # ====================================================
    # CONTROL MAPPING
    # ====================================================

    def _map_control(
        self,
        control
    ):

        mapping = {

            "FileUpload":
"""
<div>

    <label
        className="
            block
            mb-2
            font-medium
        "
    >
        Upload File
    </label>

    <input
        type="file"
    />

</div>
""",

            "PrimaryButton":
"""
<button
    className="
        bg-blue-600
        text-white
        px-4
        py-2
        rounded
    "
>
    Continue
</button>
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
    Data Grid Placeholder
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

    Progress Bar

</div>
""",

            "ImportSummary":
"""
<div>

    Import Summary

</div>
""",

            "StatusPanel":
"""
<div>

    Status Panel

</div>
"""
        }

        return mapping.get(
            control,
            f"<div>{control}</div>"
        )