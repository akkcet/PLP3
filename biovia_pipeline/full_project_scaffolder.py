# full_project_scaffolder.py

from pathlib import Path
import json


class FullProjectScaffolder:

    def generate(
        self,
        blueprint,
        output_dir: str
    ):

        root = Path(output_dir)

        frontend = root / "frontend"
        backend = root / "backend"

        self._build_frontend(frontend)
        self._build_backend(backend)

        self._build_readme(
            root,
            blueprint
        )

        self._build_metadata(
            root,
            blueprint
        )

    # =========================================================
    # FRONTEND
    # =========================================================

    def _build_frontend(
        self,
        frontend_root: Path
    ):

        frontend_root.mkdir(
            parents=True,
            exist_ok=True
        )

        self._create_src_tree(
            frontend_root
        )

        self._generate_package_json(
            frontend_root
        )

        self._generate_vite_config(
            frontend_root
        )

        self._generate_tsconfig(
            frontend_root
        )

        self._generate_tsconfig_node(
            frontend_root
        )

        self._generate_index_html(
            frontend_root
        )

        self._generate_main_tsx(
            frontend_root
        )

        self._generate_app_tsx(
            frontend_root
        )

    # =========================================================
    # BACKEND
    # =========================================================

    def _build_backend(
        self,
        backend_root: Path
    ):

        backend_root.mkdir(
            parents=True,
            exist_ok=True
        )

        (backend_root / "routers").mkdir(
            exist_ok=True
        )

        (backend_root / "services").mkdir(
            exist_ok=True
        )

        (backend_root / "workflows").mkdir(
            exist_ok=True
        )

        (backend_root / "models").mkdir(
            exist_ok=True
        )

        self._generate_requirements(
            backend_root
        )

        self._generate_backend_main(
            backend_root
        )

    # =========================================================
    # DIRECTORY STRUCTURE
    # =========================================================

    def _create_src_tree(
        self,
        frontend_root: Path
    ):

        folders = [

            "src",

            "src/pages",

            "src/components",

            "src/layouts",

            "src/routes",

            "src/types",

            "src/services",

            "src/hooks",

            "src/assets"
        ]

        for folder in folders:

            (
                frontend_root /
                folder
            ).mkdir(
                parents=True,
                exist_ok=True
            )

    # =========================================================
    # PACKAGE.JSON
    # =========================================================

    def _generate_package_json(
        self,
        frontend_root: Path
    ):

        package_json = {

            "name":
                "generated-plp-app",

            "private":
                True,

            "version":
                "1.0.0",

            "type":
                "module",

            "scripts": {

                "dev":
                    "vite",

                "build":
                    "tsc && vite build",

                "preview":
                    "vite preview"
            },

            "dependencies": {

                "react":
                    "^19.0.0",

                "react-dom":
                    "^19.0.0",

                "react-router-dom":
                    "^7.0.0",

                "axios":
                    "^1.8.0"
            },

            "devDependencies": {

                "@types/react":
                    "^19.0.10",

                "@types/react-dom":
                    "^19.0.4",

                "@vitejs/plugin-react":
                    "^4.3.0",

                "typescript":
                    "^5.8.0",

                "vite":
                    "^6.0.0"
            }
        }

        (
            frontend_root /
            "package.json"
        ).write_text(

            json.dumps(
                package_json,
                indent=4
            ),

            encoding="utf-8"
        )

    # =========================================================
    # VITE CONFIG
    # =========================================================

    def _generate_vite_config(
        self,
        frontend_root: Path
    ):

        content = """
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({

    plugins: [

        react()
    ],

    server: {

        port: 5173
    }
});
"""

        (
            frontend_root /
            "vite.config.ts"
        ).write_text(
            content,
            encoding="utf-8"
        )

    # =========================================================
    # TSCONFIG
    # =========================================================

    def _generate_tsconfig(
        self,
        frontend_root: Path
    ):

        content = {
            "compilerOptions": {

                "target": "ES2022",

                "useDefineForClassFields": True,

                "lib": [
                    "DOM",
                    "DOM.Iterable",
                    "ES2022"
                ],

                "allowJs": False,

                "skipLibCheck": True,

                "esModuleInterop": True,

                "allowSyntheticDefaultImports":
                    True,

                "strict": True,

                "forceConsistentCasingInFileNames":
                    True,

                "module": "ESNext",

                "moduleResolution":
                    "Node",

                "resolveJsonModule":
                    True,

                "isolatedModules":
                    True,

                "noEmit": True,

                "jsx": "react-jsx"
            },

            "include": [

                "src"
            ]
        }

        (
            frontend_root /
            "tsconfig.json"
        ).write_text(

            json.dumps(
                content,
                indent=4
            ),

            encoding="utf-8"
        )

    # =========================================================
    # TSCONFIG NODE
    # =========================================================

    def _generate_tsconfig_node(
        self,
        frontend_root: Path
    ):

        content = {

            "compilerOptions": {

                "composite": True,

                "module": "ESNext",

                "moduleResolution":
                    "Node"
            },

            "include": [

                "vite.config.ts"
            ]
        }

        (
            frontend_root /
            "tsconfig.node.json"
        ).write_text(

            json.dumps(
                content,
                indent=4
            ),

            encoding="utf-8"
        )

    # =========================================================
    # INDEX.HTML
    # =========================================================

#     def _generate_index_html(
#         self,
#         frontend_root: Path
#     ):

#         content = """
# <!DOCTYPE html>

# <html lang="en">

# <head>

#     <meta charset="UTF-8" />

#     <meta
#         name="viewport"
#         content="width=device-width, initial-scale=1.0"
#     />

#     <title>
#         Generated PLP Application
#     </title>

# </head>

# <body>

#     <div id="root"></div>

#     /src/main.tsxscript>

# </body>

# </html>
# """

#         (
#             frontend_root /
#             "index.html"
#         ).write_text(
#             content,
#             encoding="utf-8"
#         )
    def _generate_index_html(
        self,
        frontend_root: Path
    ):

        content = """
    <!DOCTYPE html>
    <html lang="en">

    <head>

        <meta charset="UTF-8" />

        <meta
            name="viewport"
            content="width=device-width, initial-scale=1.0"
        />

        <title>
            Generated PLP Application
        </title>

    </head>

    <body>

        <div id="root"></div>

        <script
            type="module"
            src="/src/main.tsx"
        ></script>

    </body>

    </html>
    """

        (
            frontend_root /
            "index.html"
        ).write_text(
            content,
            encoding="utf-8"
        )
    # =========================================================
    # MAIN TSX
    # =========================================================

#     def _generate_main_tsx(
#         self,
#         frontend_root: Path
#     ):

#         content = """
# import React from "react";
# import ReactDOM from "react-dom/client";

# import App from "./App";

# ReactDOM.createRoot(
#     document.getElementById("root")!
# ).render(

#     <React.StrictMode>

#         <App />

#     </React.StrictMode>
# );
# """

#         (
#             frontend_root /
#             "src/main.tsx"
#         ).write_text(
#             content,
#             encoding="utf-8"
#         )
    def _generate_main_tsx(
        self,
        frontend_root: Path
    ):

        content = """
    import React from "react";
    import ReactDOM from "react-dom/client";

    import App from "./App";

    ReactDOM.createRoot(
        document.getElementById("root")!
    ).render(

        <React.StrictMode>

            <App />

        </React.StrictMode>
    );
    """

        (
            frontend_root /
            "src/main.tsx"
        ).write_text(
            content,
            encoding="utf-8"
        )
    # =========================================================
    # APP TSX
    # =========================================================

#     def _generate_app_tsx(
#         self,
#         frontend_root: Path
#     ):

#         content = """
# import React from "react";

# export default function App() {

#     return (

#         <div>

#             Generated Application

#         </div>
#     );
# }
# """

#         (
#             frontend_root /
#             "src/App.tsx"
#         ).write_text(
#             content,
#             encoding="utf-8"
#         )
    def _generate_app_tsx(
        self,
        frontend_root: Path
    ):

        content = """
    import React from "react";

    import AppRoutes from "./routes/AppRoutes";

    export default function App() {

        return (

            <AppRoutes />

        );
    }
    """

        (
            frontend_root /
            "src/App.tsx"
        ).write_text(
            content,
            encoding="utf-8"
        )
    # =========================================================
    # REQUIREMENTS.TXT
    # =========================================================

    def _generate_requirements(
        self,
        backend_root: Path
    ):

        content = """
fastapi
uvicorn
pydantic
requests
python-multipart
"""

        (
            backend_root /
            "requirements.txt"
        ).write_text(
            content.strip(),
            encoding="utf-8"
        )

    # =========================================================
    # FASTAPI MAIN
    # =========================================================

    def _generate_backend_main(
        self,
        backend_root: Path
    ):

        content = """
from fastapi import FastAPI

app = FastAPI()


@app.get("/")

def root():

    return {

        "status": "running"
    }
"""

        (
            backend_root /
            "main.py"
        ).write_text(
            content,
            encoding="utf-8"
        )

        # =========================================================
    # README
    # =========================================================

    def _build_readme(
        self,
        root: Path,
        blueprint
    ):

        content = f"""
        # {blueprint.app_name}

        Generated by PLP Reconstruction Agent

        ## Frontend

        ```bash
        cd frontend
        npm install
        npm run dev
        cd backend
        pip install -r requirements.txt
        uvicorn main:app --reload
        ```
        Generated Statistics

        Pages: {len(blueprint.pages)}

        Workflows: {len(blueprint.workflows)}

        API Endpoints: {len(blueprint.api_endpoints)}

        Reusable Components: {len(blueprint.reusable_components)}

        Missing Components: {len(blueprint.missing_components)} """
        (
            root /
            "README.md"
        ).write_text(
            content,
            encoding="utf-8"
        )
    def _build_metadata(
        self,
        root: Path,
        blueprint
    ):

        metadata = {

            "app_name":
                blueprint.app_name,

            "pages":
                len(
                    blueprint.pages
                ),

            "workflows":
                len(
                    blueprint.workflows
                ),

            "api_endpoints":
                len(
                    blueprint.api_endpoints
                ),

            "reusable_components":
                len(
                    blueprint.reusable_components
                ),

            "missing_components":
                len(
                    blueprint.missing_components
                )
        }

        (
            root /
            "metadata.json"
        ).write_text(

            json.dumps(
                metadata,
                indent=4
            ),

            encoding="utf-8"
        )