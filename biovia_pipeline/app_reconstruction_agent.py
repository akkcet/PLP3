# app_reconstruction_agent.py

from dataclasses import dataclass, field
from typing import List, Dict

from .component_resolver import resolve_backend_component
from .ui_component_resolver import resolve_ui_component


@dataclass
class UIControl:
    name: str
    component_type: str
    props: Dict = field(default_factory=dict)


@dataclass
class PageBlueprint:
    name: str
    controls: List[UIControl] = field(default_factory=list)


@dataclass
class WorkflowBlueprint:
    name: str
    backend_components: List[str] = field(default_factory=list)


@dataclass
class ApplicationBlueprint:
    pages: List[PageBlueprint]
    workflows: List[WorkflowBlueprint]
    missing_components: List[str]


class ApplicationReconstructionAgent:

    def reconstruct(self, protocol_analysis) -> ApplicationBlueprint:

        page = PageBlueprint(name="MainPage")

        backend_components = []
        missing = []

        for node in protocol_analysis.nodes:

            if node.role.value == "GREEN_UI_GENERATOR":

                ui_component = resolve_ui_component(
                    node.visual_name
                )

                if ui_component:

                    page.controls.append(
                        UIControl(
                            name=node.visual_name,
                            component_type=ui_component
                        )
                    )

                else:
                    missing.append(node.visual_name)

            else:

                backend_component = resolve_backend_component(
                    node.visual_name
                )

                if backend_component:
                    backend_components.append(
                        backend_component
                    )
                else:
                    missing.append(node.visual_name)

        workflow = WorkflowBlueprint(
            name="MainWorkflow",
            backend_components=backend_components
        )

        return ApplicationBlueprint(
            pages=[page],
            workflows=[workflow],
            missing_components=missing
        )