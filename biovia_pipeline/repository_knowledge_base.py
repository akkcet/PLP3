# repository_knowledge_base.py

from dataclasses import dataclass, field
from typing import List, Optional


# ============================================================
# MODELS
# ============================================================

@dataclass
class KnowledgeComponent:

    component_name: str

    import_statement: str

    function_name: str

    category: str

    parameters: List[str]

    purpose: str

    usage_example: str


@dataclass
class RepositoryKnowledgeBase:

    components: List[
        KnowledgeComponent
    ] = field(
        default_factory=list
    )

    def find_component(
        self,
        component_name
    ):

        for component in self.components:

            if (
                component.component_name
                .lower()
                ==
                component_name.lower()
            ):

                return component

        return None
    