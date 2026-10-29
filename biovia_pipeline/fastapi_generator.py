# fastapi_generator.py

from pathlib import Path


class FastAPIGenerator:

    def generate(
        self,
        api_contracts,
        output_dir
    ):

        root = Path(output_dir)

        root.mkdir(
            parents=True,
            exist_ok=True
        )

        content = self._build_app(
            api_contracts
        )

        (
            root /
            "generated_api.py"
        ).write_text(
            content,
            encoding="utf-8"
        )

    def _build_app(
        self,
        api_contracts
    ):

        imports = [
            "from fastapi import FastAPI"
        ]

        routes = []

        for contract in api_contracts.contracts:

            routes.append(
                self._generate_route(
                    contract
                )
            )

        routes_text = "\n\n".join(
            routes
        )

        imports_text = "\n".join(
            imports
        )

        return f"""
{imports_text}

app = FastAPI()

{routes_text}
"""

    def _generate_route(
        self,
        contract
    ):

        return f"""
@app.post(
    "{contract.route}"
)
def {contract.endpoint_name}():

    return {{

        "success": True,

        "component":
            "{contract.backend_function}",

        "message":
            "Auto-generated endpoint"
    }}
"""