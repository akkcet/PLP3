# workflow_orchestrator_builder.py

from dataclasses import dataclass, field
from typing import List, Dict, Optional


# ============================================================
# MODELS
# ============================================================

@dataclass
class ExecutionNode:

    node_id: str

    component_name: str

    python_function: str

    component_category: str

    input_vars: List[str] = field(
        default_factory=list
    )

    output_vars: List[str] = field(
        default_factory=list
    )


@dataclass
class ExecutionEdge:

    source_node: str

    target_node: str

    condition: Optional[str] = None


@dataclass
class WorkflowGraph:

    workflow_name: str

    nodes: List[ExecutionNode]

    edges: List[ExecutionEdge]

    entry_node: Optional[str]

    exit_node: Optional[str]


# ============================================================
# BUILDER
# ============================================================

class WorkflowOrchestratorBuilder:

    def build(
        self,
        workflow_definition,
        component_bindings
    ) -> WorkflowGraph:

        nodes = []

        edges = []

        previous_node = None

        bound_lookup = {}

        #
        # Create lookup table
        #
        for component in (
            component_bindings.bound_components
        ):

            bound_lookup[
                component.component_name.lower()
            ] = component

        #
        # Build workflow
        #
        for idx, step in enumerate(
            workflow_definition.steps
        ):

            matching_component = (
                self._find_matching_component(
                    step.name,
                    bound_lookup
                )
            )

            if matching_component:

                node = ExecutionNode(

                    node_id=
                        f"node_{idx+1}",

                    component_name=
                        matching_component.component_name,

                    python_function=
                        matching_component
                        .repository_component
                        .python_function,

                    component_category=
                        matching_component
                        .repository_component
                        .category
                )

            else:

                node = ExecutionNode(

                    node_id=
                        f"node_{idx+1}",

                    component_name=
                        step.name,

                    python_function=
                        self._default_function_name(
                            step.name
                        ),

                    component_category=
                        "generated"
                )

            nodes.append(node)

            #
            # Create edge
            #
            if previous_node:

                edges.append(

                    ExecutionEdge(

                        source_node=
                            previous_node.node_id,

                        target_node=
                            node.node_id
                    )
                )

            previous_node = node

        return WorkflowGraph(

            workflow_name=
                workflow_definition.workflow_name,

            nodes=nodes,

            edges=edges,

            entry_node=
                nodes[0].node_id
                if nodes else None,

            exit_node=
                nodes[-1].node_id
                if nodes else None
        )

    # ========================================================
    # COMPONENT MATCHING
    # ========================================================

    def _find_matching_component(
        self,
        step_name,
        bindings
    ):

        normalized = (
            step_name
            .lower()
            .strip()
        )

        for key, value in bindings.items():

            if normalized in key:
                return value

            if key in normalized:
                return value

        return None

    # ========================================================
    # FALLBACK
    # ========================================================

    def _default_function_name(
        self,
        value
    ):

        return (
            value
            .replace(" ", "_")
            .replace("-", "_")
            .lower()
        )

    # ========================================================
    # VISUALIZATION
    # ========================================================

    def print_graph(
        self,
        graph: WorkflowGraph
    ):

        print()

        print("=" * 80)

        print(
            graph.workflow_name
        )

        print("=" * 80)

        print()

        print(
            f"Entry Node: "
            f"{graph.entry_node}"
        )

        print(
            f"Exit Node: "
            f"{graph.exit_node}"
        )

        print()

        print("Nodes")

        print("-" * 80)

        for node in graph.nodes:

            print(
                f"{node.node_id}"
            )

            print(
                f"Component: "
                f"{node.component_name}"
            )

            print(
                f"Function: "
                f"{node.python_function}"
            )

            print(
                f"Category: "
                f"{node.component_category}"
            )

            print()

        print()

        print("Edges")

        print("-" * 80)

        for edge in graph.edges:

            print(
                f"{edge.source_node}"
                f" -> "
                f"{edge.target_node}"
            )

        print()