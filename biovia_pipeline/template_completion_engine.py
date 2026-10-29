class TemplateCompletionEngine:

    def complete(
        self,
        workflow,
        template_match
    ):

        for missing in (
            template_match
            .missing_components
        ):

            print(
                f"Template suggests: "
                f"{missing}"
            )

        return (
            template_match
            .missing_components
        )