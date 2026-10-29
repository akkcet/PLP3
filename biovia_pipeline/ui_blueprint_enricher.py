# ui_blueprint_enricher.py

from copy import deepcopy


class UIBlueprintEnricher:

    def enrich(
        self,
        blueprint,
        screenshot_labels
    ):

        enriched = deepcopy(
            blueprint
        )

        button_labels = []

        upload_labels = []

        input_labels = []

        for screen in screenshot_labels:

            for lbl in screen.labels:

                if lbl.label_type == "button":

                    button_labels.append(
                        lbl.text
                    )

                elif lbl.label_type == "input":

                    input_labels.append(
                        lbl.text
                    )

                elif "browse" in lbl.text.lower():

                    upload_labels.append(
                        lbl.text
                    )

        button_index = 0
        input_index = 0
        upload_index = 0

        for page in enriched.pages:

            for component in page.components:

                #
                # Buttons
                #
                if (
                    component.component_type
                    == "PrimaryButton"
                ):

                    if button_index < len(
                        button_labels
                    ):

                        component.label = (
                            button_labels[
                                button_index
                            ]
                        )

                        button_index += 1

                #
                # Upload controls
                #
                elif (
                    component.component_type
                    == "FileUpload"
                ):

                    if upload_index < len(
                        upload_labels
                    ):

                        component.label = (
                            upload_labels[
                                upload_index
                            ]
                        )

                        upload_index += 1

                #
                # Inputs
                #
                elif (
                    component.component_type
                    == "TextInput"
                ):

                    if input_index < len(
                        input_labels
                    ):

                        component.label = (
                            input_labels[
                                input_index
                            ]
                        )

                        input_index += 1

        return enriched