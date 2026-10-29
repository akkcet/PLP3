# business_blueprint_enricher.py

class BusinessBlueprintEnricher:

    def enrich(
        self,
        blueprint,
        business_workflow
    ):

        workflow_steps = {

            step.step_name.lower()

            for step in
            business_workflow.workflow_steps
        }

        #
        # Example:
        # Add page labels
        #
        for page in blueprint.pages:

            page_name = (
                page.page_name
                .lower()
            )

            if "upload" in page_name:

                page.page_description = (
                    "Upload XML file"
                )

            elif "import" in page_name:

                page.page_description = (
                    "Import files into ELN"
                )

        #
        # Attach business goal
        #
        blueprint.business_goal = (
            business_workflow.business_goal
        )

        blueprint.workflow_name = (
            business_workflow.workflow_name
        )

        return blueprint
