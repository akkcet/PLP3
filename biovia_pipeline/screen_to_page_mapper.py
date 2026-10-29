# screen_to_page_mapper.py

from dataclasses import dataclass, field
from typing import List, Optional


# ============================================================
# MODELS
# ============================================================

@dataclass
class PageDefinition:

    page_name: str

    route: str

    page_type: str

    title: str

    controls: List[str] = field(
        default_factory=list
    )

    description: str = ""

    parent_page: Optional[str] = None


@dataclass
class NavigationLink:

    source_page: str

    target_page: str

    action: str


@dataclass
class ApplicationPageGraph:

    pages: List[PageDefinition]

    navigation: List[NavigationLink]

    entry_page: str


# ============================================================
# PAGE MAPPER
# ============================================================

class ScreenToPageMapper:

    def build(
        self,
        business_workflow,
        screen_flow_graph,
        ui_pattern="wizard"
    ) -> ApplicationPageGraph:
        if ui_pattern == "single_page":

            return self._build_single_page_graph(
                business_workflow
            )
        pages = []

        navigation = []

        previous_page = None

        for index, step in enumerate(
            business_workflow.workflow_steps,
            start=1
        ):

            page = PageDefinition(

                page_name=
                    self._page_name(
                        step.step_name
                    ),

                route=
                    self._route(
                        step.step_name
                    ),

                page_type=
                    step.action_type,

                title=
                    step.step_name,

                controls=
                    self._default_controls(
                        step.action_type
                    ),

                description=
                    self._description(
                        step.action_type
                    )
            )

            pages.append(
                page
            )

            if previous_page:

                navigation.append(

                    NavigationLink(

                        source_page=
                            previous_page.page_name,

                        target_page=
                            page.page_name,

                        action="next"
                    )
                )

            previous_page = page

        return ApplicationPageGraph(

            pages=pages,

            navigation=navigation,

            entry_page=
                pages[0].page_name
                if pages
                else "Home"
        )

    # ========================================================
    # ROUTES
    # ========================================================

    def _route(
        self,
        name
    ):

        return (

            "/"

            +

            name
            .lower()
            .replace(" ", "-")
        )

    # ========================================================
    # PAGE NAME
    # ========================================================

    def _page_name(
        self,
        value
    ):

        return (

            value
            .replace("-", " ")
            .title()
            .replace(" ", "")
        )

    # ========================================================
    # DEFAULT CONTROLS
    # ========================================================

    def _default_controls(
        self,
        action_type
    ):

        mapping = {

            "UPLOAD": [

                "FileUpload",

                "PrimaryButton"
            ],

            "PROCESS": [

                "StatusPanel",

                "PrimaryButton"
            ],

            "SELECTION": [

                "DataGrid",

                "MultiSelect",

                "PrimaryButton"
            ],

            "DOWNLOAD": [

                "ProgressBar",

                "StatusPanel"
            ],

            "IMPORT": [

                "ProgressBar",

                "StatusPanel"
            ],

            "REVIEW": [

                "DataGrid",

                "PrimaryButton"
            ],

            "COMPLETE": [

                "ImportSummary"
            ],

            "CLEANUP": [

                "StatusPanel"
            ]
        }

        return mapping.get(
            action_type,
            []
        )

    # ========================================================
    # DESCRIPTIONS
    # ========================================================

    def _description(
        self,
        action_type
    ):

        descriptions = {

            "UPLOAD":
                "Upload source XML files.",

            "PROCESS":
                "Parse and validate XML.",

            "SELECTION":
                "Select files to import.",

            "DOWNLOAD":
                "Download files from source system.",

            "IMPORT":
                "Attach selected files to ELN.",

            "COMPLETE":
                "Display import summary.",

            "REVIEW":
                "Review extracted content.",

            "CLEANUP":
                "Remove temporary files."
        }

        return descriptions.get(
            action_type,
            ""
        )
    def _build_single_page_graph(
        self,
        business_workflow
    ):

        page = PageDefinition(

            page_name=
                "MainPage",

            route=
                "/",

            page_type=
                "STATEFUL",

            title=
                business_workflow.workflow_name,

            controls=[

                "FileUpload",

                "DataGrid",

                "MultiSelect",

                "PrimaryButton",

                "StatusPanel"
            ],

            description=
                business_workflow.business_goal
        )

        return ApplicationPageGraph(

            pages=[page],

            navigation=[],

            entry_page="MainPage"
        )
    # ========================================================
    # DEBUG
    # ========================================================

    def print_page_graph(
        self,
        graph
    ):

        print()

        print("=" * 80)
        print("APPLICATION PAGE GRAPH")
        print("=" * 80)

        print()

        print(
            f"Entry Page : "
            f"{graph.entry_page}"
        )

        print()

        print("Pages")

        print("-" * 80)

        for page in graph.pages:

            print()

            print(
                f"Name  : {page.page_name}"
            )

            print(
                f"Route : {page.route}"
            )

            print(
                f"Type  : {page.page_type}"
            )

            print(
                f"Title : {page.title}"
            )

            print(
                f"Controls : "
                f"{page.controls}"
            )

        print()

        print("Navigation")

        print("-" * 80)

        for nav in graph.navigation:

            print(

                f"{nav.source_page}"

                f" --> "

                f"{nav.target_page}"

            )