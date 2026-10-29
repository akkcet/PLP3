class MissingComponentContextBuilder:

    def build(
        self,
        context,
        component_name
    ):

        lines = []

        lines.append(
            f"Application:"
        )

        lines.append(
            context.application_blueprint
            .app_name
        )

        lines.append("")

        lines.append(
            "Business Workflow:"
        )

        lines.append(

            context.business_workflow
            .workflow_name
        )

        lines.append("")

        lines.append(
            "Known Components:"
        )

        for bound in (

            context.binding_result
            .bound_components

        ):

            lines.append(
                bound.component_name
            )

        return "\n".join(
            lines
        )
