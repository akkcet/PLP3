# application_decision_engine.py

class ApplicationDecisionEngine:

    def determine_ui_role(
        self,
        component_name,
        business_workflow
    ):

        name = (
            component_name
            .lower()
        )

        workflow_text = (

            " ".join(

                x.step_name
                for x in
                business_workflow.workflow_steps

            ).lower()
        )

        if (

            "file chooser" in name

            and

            "upload" in workflow_text

        ):

            return "FileUpload"

        if (

            "submit button" in name

            and

            "import" in workflow_text

        ):

            return "PrimaryButton"

        return None