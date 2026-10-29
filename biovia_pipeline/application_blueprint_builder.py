# application_blueprint_builder.py

from dataclasses import dataclass, field
from typing import List


@dataclass
class APIEndpoint:

    name: str
    route: str
    backend_component: str


@dataclass
class FrontendPage:

    page_name: str
    route: str

    controls: List[str] = field(default_factory=list)


@dataclass
class BackendWorkflow:

    workflow_name: str

    components: List[str] = field(
        default_factory=list
    )


@dataclass
class ApplicationBlueprint:

    app_name: str

    pages: List[FrontendPage]

    workflows: List[BackendWorkflow]

    api_endpoints: List[APIEndpoint]

    reusable_components: List[str]

    missing_components: List[str]


class ApplicationBlueprintBuilder:

    def build(
        self,
        protocol_analysis,
        screen_flow_graph
    ) -> ApplicationBlueprint:

        pages = []
        workflows = []
        endpoints = []

        reusable_components = []
        missing_components = []

        #
        # Build Pages
        #
        for page in screen_flow_graph.pages:

            pages.append(

                FrontendPage(
                    page_name=page.page_name,
                    route=f"/{page.page_id}",
                    controls=page.controls
                )
            )

        #
        # Build Workflows
        #
        blue_nodes = [

            n.visual_name

            for n in protocol_analysis.nodes

            if "BLUE" in str(n.role)
        ]

        workflows.append(

            BackendWorkflow(
                workflow_name="MainWorkflow",
                components=blue_nodes
            )
        )

        #
        # Build Endpoints
        #
        for comp in blue_nodes:

            route = (
                "/" +
                comp.lower()
                .replace(" ", "-")
            )

            endpoints.append(

                APIEndpoint(
                    name=comp,
                    route=route,
                    backend_component=comp
                )
            )

            reusable_components.append(
                comp
            )

        return ApplicationBlueprint(

            app_name=protocol_analysis.protocol_name,

            pages=pages,

            workflows=workflows,

            api_endpoints=endpoints,

            reusable_components=
                reusable_components,

            missing_components=
                missing_components,
        )