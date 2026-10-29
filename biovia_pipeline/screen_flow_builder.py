##screen_flow_builder.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ============================================================
# PAGE GRAPH MODELS
# ============================================================

@dataclass
class PageNode:
    """
    Represents a generated page/screen in the reconstructed app.
    """

    page_id: str
    page_name: str
    page_type: str

    controls: List[str] = field(default_factory=list)

    incoming_pages: List[str] = field(default_factory=list)
    outgoing_pages: List[str] = field(default_factory=list)


@dataclass
class NavigationEdge:
    """
    Represents navigation between pages.
    """

    source_page: str
    destination_page: str
    action: str


@dataclass
class ScreenFlowGraph:
    """
    Final output used by React generator.
    """

    pages: List[PageNode]
    navigation: List[NavigationEdge]
    entry_page: str


# ============================================================
# BUILDER
# ============================================================

class ScreenFlowBuilder:

    def build(
        self,
        protocol_analysis,
        ui_analysis
    ) -> ScreenFlowGraph:
        """
        Build page graph from:
            - Protocol XML analysis
            - Screenshot analysis
        """
        if ui_analysis is None:

            return self._build_from_protocol_only(
            protocol_analysis
            )
        pages: List[PageNode] = []
        navigation: List[NavigationEdge] = []

        #
        # Detect workflow from screenshots
        #
        workflow_steps = self._infer_workflow_steps(
            ui_analysis
        )

        #
        # Create pages
        #
        previous_page = None

        for idx, step in enumerate(workflow_steps):

            page = PageNode(
                page_id=f"page_{idx+1}",
                page_name=step["name"],
                page_type=step["type"],
                controls=step["controls"]
            )

            pages.append(page)

            if previous_page:

                navigation.append(
                    NavigationEdge(
                        source_page=previous_page.page_id,
                        destination_page=page.page_id,
                        action="next"
                    )
                )

                previous_page.outgoing_pages.append(
                    page.page_id
                )

                page.incoming_pages.append(
                    previous_page.page_id
                )

            previous_page = page

        entry_page = (
            pages[0].page_id
            if pages
            else "page_1"
        )

        return ScreenFlowGraph(
            pages=pages,
            navigation=navigation,
            entry_page=entry_page
        )

    # ========================================================
    # WORKFLOW EXTRACTION
    # ========================================================

    def _infer_workflow_steps(
        self,
        ui_analysis
    ):

        steps = []

        all_controls = []

        for screen in ui_analysis.screens:

            for widget in screen.widgets:

                all_controls.append(
                    widget.widget_type
                )

        #
        # Upload XML
        #
        if "FileUpload" in all_controls:

            steps.append({
                "name":
                    "Upload XML",

                "type":
                    "upload",

                "controls": [
                    "FileUpload",
                    "PrimaryButton"
                ]
            })

        #
        # Parse XML
        #
        steps.append({
            "name":
                "Review XML Data",

            "type":
                "data_review",

            "controls": [
                "DataGrid",
                "PrimaryButton"
            ]
        })

        #
        # Select Files
        #
        steps.append({
            "name":
                "Select Files",

            "type":
                "selection",

            "controls": [
                "DataGrid",
                "MultiSelect",
                "PrimaryButton"
            ]
        })

        #
        # Import To ELN
        #
        steps.append({
            "name":
                "Import Files",

            "type":
                "import",

            "controls": [
                "ProgressBar",
                "StatusPanel"
            ]
        })

        #
        # Summary
        #
        steps.append({
            "name":
                "Completed",

            "type":
                "summary",

            "controls": [
                "ImportSummary",
                "SuccessBanner"
            ]
        })

        return steps


    def _build_from_protocol_only(
    self,
    protocol_analysis
):

        pages = []
        navigation = []

        previous_page = None

        workflow_steps = [

            {
                "name": "Upload XML",
                "type": "upload",
                "controls": [
                    "FileUpload",
                    "PrimaryButton"
                ]
            },

            {
                "name": "Review XML Data",
                "type": "review",
                "controls": [
                    "DataGrid",
                    "PrimaryButton"
                ]
            },

            {
                "name": "Import Files",
                "type": "import",
                "controls": [
                    "ProgressBar",
                    "StatusPanel"
                ]
            },

            {
                "name": "Completed",
                "type": "summary",
                "controls": [
                    "ImportSummary"
                ]
            }
        ]

        for idx, step in enumerate(
            workflow_steps
        ):

            page = PageNode(

                page_id=f"page_{idx+1}",

                page_name=step["name"],

                page_type=step["type"],

                controls=step["controls"]
            )

            pages.append(page)

            if previous_page:

                navigation.append(

                    NavigationEdge(

                        source_page=
                            previous_page.page_id,

                        destination_page=
                            page.page_id,

                        action="next"
                    )
                )

            previous_page = page

        return ScreenFlowGraph(

            pages=pages,

            navigation=navigation,

            entry_page=
                pages[0].page_id
                if pages
                else "page_1"
        )

    # ========================================================
    # DEBUG UTILITIES
    # ========================================================

    def print_graph(
        self,
        graph: ScreenFlowGraph
    ):

        print("\n===== APP FLOW =====\n")

        for page in graph.pages:

            print(
                f"{page.page_id}"
                f" -> "
                f"{page.page_name}"
            )

            print("Controls:")

            for c in page.controls:

                print(
                    f"   - {c}"
                )

            print()

        print(
            "\nNavigation:\n"
        )

        for edge in graph.navigation:

            print(
                f"{edge.source_page}"
                f" -> "
                f"{edge.destination_page}"
            )