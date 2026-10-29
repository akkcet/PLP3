# reconstruction_knowledge_graph.py

from dataclasses import dataclass, field
from typing import Dict, List


# ============================================================
# NODES
# ============================================================

@dataclass
class KnowledgeNode:

    node_id: str

    node_type: str

    name: str

    attributes: Dict = field(
        default_factory=dict
    )


@dataclass
class KnowledgeEdge:

    source_id: str

    target_id: str

    relation: str


@dataclass
class KnowledgeGraph:

    nodes: Dict[
        str,
        KnowledgeNode
    ] = field(
        default_factory=dict
    )

    edges: List[
        KnowledgeEdge
    ] = field(
        default_factory=list
    )

class ReconstructionKnowledgeGraph:

    def __init__(self):

        self.graph = (
            KnowledgeGraph()
        )

    # ========================================================
    # ADD NODE
    # ========================================================

    def add_node(
        self,
        node
    ):

        self.graph.nodes[
            node.node_id
        ] = node

    # ========================================================
    # ADD EDGE
    # ========================================================

    def add_edge(
        self,
        edge
    ):

        self.graph.edges.append(
            edge
        )
    def from_protocol(
        self,
        protocol_analysis
    ):

        for node in (
            protocol_analysis.nodes
        ):

            self.add_node(

                KnowledgeNode(

                    node_id=
                        f"component_{node.local_id}",

                    node_type=
                        "component",

                    name=
                        node.visual_name,

                    attributes={

                        "role":
                            str(node.role),

                        "status":
                            str(node.status)
                    }
                )
            )
    def from_business_workflow(
        self,
        workflow
    ):

        for step in (
            workflow.workflow_steps
        ):

            self.add_node(

                KnowledgeNode(

                    node_id=
                        f"step_{step.step_number}",

                    node_type=
                        "workflow_step",

                    name=
                        step.step_name,

                    attributes={

                        "action":
                            step.action_type
                    }
                )
            )

        for i in range(
            len(workflow.workflow_steps)
            - 1
        ):

            self.add_edge(

                KnowledgeEdge(

                    source_id=
                        f"step_{i+1}",

                    target_id=
                        f"step_{i+2}",

                    relation=
                        "next"
                )
            )
    def from_templates(
        self,
        template_catalog
    ):

        for template in (
            template_catalog.templates
        ):

            self.add_node(

                KnowledgeNode(

                    node_id=
                        template.template_name,

                    node_type=
                        "template",

                    name=
                        template.template_name,

                    attributes={

                        "category":
                            template.category,

                        "confidence":
                            template.confidence
                    }
                )
            )
    def from_stateful_workflow(
        self,
        workflow
    ):

        for component in (
            workflow.components
        ):

            self.add_node(

                KnowledgeNode(

                    node_id=
                        component.function_name,

                    node_type=
                        "backend_function",

                    name=
                        component.function_name,

                    attributes={

                        "inputs":
                            component.inputs,

                        "outputs":
                            component.outputs
                    }
                )
            )
    def find_components(
        self,
        category
    ):

        return [

            node

            for node in

            self.graph.nodes.values()

            if node.node_type
            ==
            category
        ]
    def summary(
        self
    ):

        return {

            "nodes":
                len(
                    self.graph.nodes
                ),

            "edges":
                len(
                    self.graph.edges
                )
        }
import json
from pathlib import Path


class KnowledgeGraphExporter:

    def save(
        self,
        graph,
        output_path
    ):

        output = {

            "nodes": [

                vars(x)

                for x in

                graph.nodes.values()
            ],

            "edges": [

                vars(x)

                for x in

                graph.edges
            ]
        }

        Path(
            output_path
        ).write_text(

            json.dumps(
                output,
                indent=4
            ),

            encoding="utf-8"
        )