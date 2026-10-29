# fastapi_application_generator.py

import json

from pathlib import Path

from biovia_pipeline.api_contract_generator import (
    APIContractGenerator
)

from biovia_pipeline.fastapi_generator import (
    FastAPIGenerator
)


class FastAPIApplicationGenerator:

    def __init__(self):

        self.contract_generator = (
            APIContractGenerator()
        )

        self.fastapi_generator = (
            FastAPIGenerator()
        )

    # ========================================================
    # ENTRYPOINT
    # ========================================================

    def generate(
        self,
        workflow_graph,
        output_dir
    ):

        root = Path(output_dir)

        self._create_structure(
            root
        )

        api_contracts = (
            self.contract_generator.generate(
                workflow_graph
            )
        )

        self._generate_main(
            root
        )

        self._generate_router(
            api_contracts,
            root
        )

        self._generate_models(
            api_contracts,
            root
        )

        self._generate_requirements(
            root
        )

        self._generate_metadata(
            workflow_graph,
            root
        )

    # ========================================================
    # STRUCTURE
    # ========================================================

    def _create_structure(
        self,
        root
    ):

        folders = [

            "routers",

            "models",

            "services",

            "workflows"
        ]

        for folder in folders:

            (
                root / folder
            ).mkdir(
                parents=True,
                exist_ok=True
            )

    # ========================================================
    # MAIN.PY
    # ========================================================

    def _generate_main(
        self,
        root
    ):

        content = """
from fastapi import FastAPI

from routers.generated_router import router


app = FastAPI(
    title="Generated PLP Application",
    version="1.0.0"
)

app.include_router(router)


@app.get("/")
async def root():

    return {
        "status": "running"
    }
"""

        (
            root / "main.py"
        ).write_text(
            content,
            encoding="utf-8"
        )

    # ========================================================
    # ROUTER
    # ========================================================

    def _generate_router(
        self,
        api_contracts,
        root
    ):

        routes = []

        imports = [

            "from fastapi import APIRouter",

            "from models.requests import *",

            "from models.responses import *"
        ]

        for contract in api_contracts.contracts:

            endpoint = self._create_route(
                contract
            )

            routes.append(
                endpoint
            )

        router_code = f"""
{'\\n'.join(imports)}

router = APIRouter()


{'\\n\\n'.join(routes)}
"""

        (
            root
            / "routers"
            / "generated_router.py"
        ).write_text(
            router_code,
            encoding="utf-8"
        )

    # ========================================================
    # SINGLE ROUTE
    # ========================================================

    def _create_route(
        self,
        contract
    ):

        endpoint_name = (
            contract.endpoint_name
            .replace(" ", "")
        )

        return f"""
@router.post(
    "{contract.route}"
)
async def {endpoint_name}(

    request: {contract.request_model}

):

    #
    # TODO:
    # invoke generated workflow
    #

    return {{

        "success": True,

        "component":
            "{contract.backend_function}",

        "request":
            request.model_dump()
    }}
"""
    # ========================================================
    # REQUEST / RESPONSE MODELS
    # ========================================================

    def _generate_models(
        self,
        api_contracts,
        root
    ):

        request_models = []

        response_models = []

        request_models.append(
            "from pydantic import BaseModel\n"
        )

        response_models.append(
            "from pydantic import BaseModel\n"
        )

        for contract in (
            api_contracts.contracts
        ):

            request_models.append(
                f"""
class {contract.request_model}(BaseModel):

    payload: dict = {{}}
"""
            )

            response_models.append(
                f"""
class {contract.response_model}(BaseModel):

    success: bool

    message: str
"""
            )

        (
            root
            / "models"
            / "requests.py"
        ).write_text(

            "\n".join(
                request_models
            ),

            encoding="utf-8"
        )

        (
            root
            / "models"
            / "responses.py"
        ).write_text(

            "\n".join(
                response_models
            ),

            encoding="utf-8"
        )

    # ========================================================
    # REQUIREMENTS
    # ========================================================

    def _generate_requirements(
        self,
        root
    ):

        requirements = """
fastapi
uvicorn
pydantic
requests
python-multipart
"""

        (
            root
            / "requirements.txt"
        ).write_text(
            requirements.strip(),
            encoding="utf-8"
        )

    # ========================================================
    # METADATA
    # ========================================================

    def _generate_metadata(
        self,
        workflow_graph,
        root
    ):

        metadata = {

            "workflow_name":
                workflow_graph.workflow_name,

            "components":

                [

                    node.component_name

                    for node in
                    workflow_graph.nodes
                ]
        }

        (
            root
            / "application_metadata.json"
        ).write_text(

            json.dumps(
                metadata,
                indent=4
            ),

            encoding="utf-8"
        )