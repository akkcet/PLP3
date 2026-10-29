class GenerationSummaryBuilder:

    def build_ui_summary(
        self,
        generated_page
    ):

        return {

            "summary":
                (
                    "Single page XML "
                    "import workflow."
                ),

            "decisions": [

                "Uses MainPage.tsx",

                "Uses React state",

                "Requires parse_xml API",

                "Requires "
                "import_selected_files API"
            ]
        }
